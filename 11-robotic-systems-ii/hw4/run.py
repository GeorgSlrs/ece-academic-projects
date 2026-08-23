"""
run.py
======

NO ROS. Pure Python + pyCandle hardware runner (TVLQR tracking).

It:
  - loads precomputed tvlqr_cache.npz (t_nom, X_nom, U_nom, dt_nom, K_list)
  - uses a lightweight projection helper from projection_helper.py
  - connects to motors by ping()
  - uses RAW_TORQUE mode
  - reads (q1,q2) and estimates (dq1,dq2) if needed
  - computes TVLQR tracking torque:
        tau = u_bar[k] - K_k (x - x_bar[k])
  - sends torque commands safely

  - Keep torque limits SMALL at first.
  - Make sure the mechanism is clear / supported.
  
"""

import os
import time
import signal
import pyCandle
import numpy as np
import projection_helper as proj


# ============================================================
# USER SETTINGS (EDIT THESE IF NEEDED)
# ============================================================

# Cache file produced by build_tvlqr_cache.py
TVLQR_CACHE_FILE = "tvlqr_cache.npz"

# Preferred motor IDs in PHYSICAL meaning:
#   PREFERRED_IDS = [SHOULDER_ID, ELBOW_ID]
PREFERRED_IDS = [375, 399]

# If your physical wiring is opposite of your meaning above, flip this:
SWAP_SHOULDER_ELBOW = False

# Torque direction signs (flip if motion is reversed)
SHOULDER_TAU_SIGN = +1.0
ELBOW_TAU_SIGN    = +1.0


# CALIBRATION METHOD:
#   1) Set CALIBRATE_PRINT_RAW=True
#   2) Manually hold the arm in the desired FINAL pose (fully up)
#   3) Run python run.py, read printed q_raw values
#   4) Put those into Q1_OFFSET_RAD and Q2_OFFSET_RAD
# Then in that physical pose the model will see q = [0,0] after offset,
# so we add GOAL_Q1 = pi explicitly below.
.
Q1_SIGN = +1.0
Q2_SIGN = +1.0

# These are in *radians*, same units as getPosition() returns in your setup.
# (After you calibrate, set them to the raw readings in the desired pose.)
Q1_OFFSET_RAD = 0.0
Q2_OFFSET_RAD = 0.0

# Desired final equilibrium in MODEL coordinates
GOAL_Q1 = np.pi
GOAL_Q2 = 0.0

# Print raw encoder angles once at startup (for calibration)
CALIBRATE_PRINT_RAW = False

# ------------------------------------------------------------

# Torque limits (Nm)  (HARDWARE safety)
TORQUE_LIMIT = np.array([0.15, 0.15], dtype=float)

# Torque rate limit (Nm/s) to avoid step jumps
MAX_TAU_RATE = 1.0

# Reset encoder zero at start? ONLY if your arm is physically at the right zero pose.
RESET_ENCODER_ZERO = False

# Control update:
#   - For tracking, best is dt_ctrl = dt_nom (from cache).
USE_DT_CTRL_EQUALS_DT_NOM = True
DT_CTRL_OVERRIDE = 0.01  # used only if USE_DT_CTRL_EQUALS_DT_NOM=False

# Velocity estimation smoothing (finite-difference fallback)
VEL_SMOOTH_ALPHA = 0.30  # 0..1

# Projection tube settings (should match what you tuned in simulation)
WPROJ = np.diag([4.0, 4.0, 0.5, 0.5])
TUBE_RADIUS = 0.6

# If your hardware torques are much smaller than sim torques, you can scale
# the TVLQR+feedforward torque before clipping:
TORQUE_SCALE = 1.0

# Print diagnostics every N seconds
PRINT_EVERY = 1.0

# ------------------------------------------------------------
# IMPORTANT: PROGRESS RULE ROBUSTNESS
# ------------------------------------------------------------
# If projection ever jumps BACK to early knots, the controller will "give up"
# and stabilize the DOWN configuration.
#
# We enforce monotone progress and allow only tiny backtracking.
ALLOW_BACKTRACK = 1  # indices allowed to go backwards (0 or 1 recommended)

# Terminal lock: once we're close to goal, stop projecting and HOLD final knot
LOCK_TO_GOAL_WHEN_CLOSE = True
LOCK_ANGLE_TOL = 0.25   # rad
LOCK_VEL_TOL   = 0.8    # rad/s

# ------------------------------------------------------------

# Small delay after candle.begin() to let background update thread populate md80s.
BEGIN_POPULATE_SLEEP_SEC = 0.20


# ============================================================
# Angle helpers (wrap + unwrap)
# ============================================================

def wrap_pi(a):
    """Wrap angle to (-pi, pi]."""
    a = float(a)
    return (a + np.pi) % (2.0 * np.pi) - np.pi

def unwrap_update(prev_unwrapped, prev_wrapped, new_wrapped):
    """
    Maintain a continuous (unwrapped) angle online.
    Inputs are wrapped angles in (-pi,pi].
    """
    dw = float(new_wrapped - prev_wrapped)
    # pick the equivalent increment with smallest magnitude
    if dw > np.pi:
        dw -= 2.0 * np.pi
    elif dw < -np.pi:
        dw += 2.0 * np.pi
    return float(prev_unwrapped + dw)


# ============================================================
# pyCandle compatibility helpers
# ============================================================

def make_candle_usb():
    """Try USB constructor first; fall back to older signature."""
    try:
        return pyCandle.Candle(pyCandle.CAN_BAUD_1M, True, pyCandle.USB)
    except TypeError:
        return pyCandle.Candle(pyCandle.CAN_BAUD_1M, True)

def candle_ping_ids(candle):
    """ping() signature differs; support both."""
    try:
        return candle.ping(pyCandle.CAN_BAUD_1M)
    except TypeError:
        return candle.ping()

def safe_get_velocity(motor):
    """Try getVelocity() if available; else return None."""
    if hasattr(motor, "getVelocity"):
        try:
            return float(motor.getVelocity())
        except Exception:
            return None
    return None


# ============================================================
# Hardware TVLQR runner
# ============================================================

class RealPendulumTVLQR:
    def __init__(self):
        # ----------------------------
        # (A) Load cache (nominal + K)
        # ----------------------------
        here = os.path.dirname(os.path.abspath(__file__))
        cache_path = os.path.join(here, TVLQR_CACHE_FILE)

        if not os.path.exists(cache_path):
            raise RuntimeError(
                f"[ERROR] Missing cache file:\n  {cache_path}\n\n"
                "You must generate it first by running:\n"
                "  python build_tvlqr_cache.py\n"
            )

        data = np.load(cache_path, allow_pickle=False)

        self.t_nom  = data["t_nom"]
        self.X_nom  = data["X_nom"]
        self.U_nom  = data["U_nom"]
        self.dt_nom = float(np.array(data["dt_nom"]).reshape(()))
        self.K_list = data["K_list"]  # shape: (N-1, 2, 4)

        self.N_nom = int(self.t_nom.shape[0])
        self.T_nom = float(self.t_nom[-1])

        # Decide control period
        if USE_DT_CTRL_EQUALS_DT_NOM:
            self.dt_ctrl = float(self.dt_nom)
        else:
            self.dt_ctrl = float(DT_CTRL_OVERRIDE)

        print(f"[INFO] Loaded cache: {TVLQR_CACHE_FILE}")
        print(f"[INFO] N={len(self.t_nom)}  dt_nom={self.dt_nom:.6f}  dt_ctrl={self.dt_ctrl:.6f}")

        # Projection settings
        self.Wproj = np.array(WPROJ, dtype=float)
        self.tube_radius = float(TUBE_RADIUS)

        # Safety
        self.tau_limit = np.array(TORQUE_LIMIT, dtype=float)
        self.max_tau_rate = float(MAX_TAU_RATE)

        # ----------------------------
        # (B) Connect to hardware + choose motors
        # ----------------------------
        print("[INFO] Connecting to CANdle/USB...")
        self.candle = make_candle_usb()

        ids = candle_ping_ids(self.candle)
        print(f"[INFO] ping() detected motor IDs: {ids}")

        if len(ids) == 0:
            raise RuntimeError("[ERROR] No motors detected. Check power/USB/CAN wiring.")

        # Choose two motors: prefer PREFERRED_IDS
        chosen = []
        for pid in PREFERRED_IDS:
            if pid in ids and pid not in chosen:
                chosen.append(pid)

        # Fill from detected ids if missing
        for mid in ids:
            if len(chosen) >= 2:
                break
            if mid not in chosen:
                chosen.append(mid)

        if len(chosen) < 2:
            raise RuntimeError("[ERROR] Need 2 motors for shoulder+elbow. Only found one.")

        shoulder_id, elbow_id = chosen[0], chosen[1]
        if SWAP_SHOULDER_ELBOW:
            shoulder_id, elbow_id = elbow_id, shoulder_id

        self.shoulder_id = shoulder_id
        self.elbow_id = elbow_id

        print(f"[INFO] Using SHOULDER={self.shoulder_id}  ELBOW={self.elbow_id}")

        # IMPORTANT: add in this exact order so md80s[0]=shoulder, md80s[1]=elbow
        self.candle.addMd80(self.shoulder_id)
        self.candle.addMd80(self.elbow_id)

        if RESET_ENCODER_ZERO:
            print("[WARN] RESET_ENCODER_ZERO=True -> resetting encoders NOW.")
            self.candle.controlMd80SetEncoderZero(self.shoulder_id)
            self.candle.controlMd80SetEncoderZero(self.elbow_id)

        # Set mode + enable
        for mid in [self.shoulder_id, self.elbow_id]:
            self.candle.controlMd80Mode(mid, pyCandle.RAW_TORQUE)
            self.candle.controlMd80Enable(mid, True)

        # Start background update loop
        self.candle.begin()
        time.sleep(BEGIN_POPULATE_SLEEP_SEC)

        # Deterministic mapping
        self.shoulder_motor = self.candle.md80s[0]
        self.elbow_motor    = self.candle.md80s[1]

        # ----------------------------
        # (C) State estimation init
        # ----------------------------
        self.last_time = time.perf_counter()

        # Raw / wrapped / unwrapped angles tracking
        self.q_wrapped_prev = None
        self.q_unwrapped    = None

        self.last_qd = np.zeros(2, dtype=float)

        # Torque history (for rate limit)
        self.tau_last = np.zeros(2, dtype=float)

        # Projection history
        self.k_ref_prev = 0
        self.start_wall = time.perf_counter()

        # Shutdown flag
        self._stop = False

        # Optional calibration print
        if CALIBRATE_PRINT_RAW:
            q1_raw = float(self.shoulder_motor.getPosition())
            q2_raw = float(self.elbow_motor.getPosition())
            print("\n[CALIB] RAW encoder positions (rad):")
            print(f"  q1_raw={q1_raw:.6f}   q2_raw={q2_raw:.6f}")
            print("Put these into Q1_OFFSET_RAD / Q2_OFFSET_RAD while holding the desired pose.\n")

        # Send zero torque initially
        self.send_torque(np.zeros(2, dtype=float))
        print("[INFO] Initialized. Sending 0 torque. Ready to run.")


    def read_positions_model(self):
        """
        Read encoder angles and map them to MODEL angles (q1,q2),
        using offset + sign + wrap + online unwrap.
        """
        q1_raw = float(self.shoulder_motor.getPosition())
        q2_raw = float(self.elbow_motor.getPosition())

        # offset + sign
        q1 = Q1_SIGN * (q1_raw - Q1_OFFSET_RAD)
        q2 = Q2_SIGN * (q2_raw - Q2_OFFSET_RAD)

        # wrap to (-pi,pi]
        q1w = wrap_pi(q1)
        q2w = wrap_pi(q2)

        if self.q_wrapped_prev is None:
            # initialize unwrapped with wrapped
            self.q_wrapped_prev = np.array([q1w, q2w], dtype=float)
            self.q_unwrapped = np.array([q1w, q2w], dtype=float)
            return self.q_unwrapped.copy()

        # online unwrap
        q1u = unwrap_update(self.q_unwrapped[0], self.q_wrapped_prev[0], q1w)
        q2u = unwrap_update(self.q_unwrapped[1], self.q_wrapped_prev[1], q2w)

        self.q_wrapped_prev = np.array([q1w, q2w], dtype=float)
        self.q_unwrapped = np.array([q1u, q2u], dtype=float)

        return self.q_unwrapped.copy()

    def read_velocities(self, q_now, dt):
        v1 = safe_get_velocity(self.shoulder_motor)
        v2 = safe_get_velocity(self.elbow_motor)

        if (v1 is not None) and (v2 is not None):
            # NOTE: if velocity sign is wrong, you can flip here similarly.
            return np.array([float(v1), float(v2)], dtype=float)

        # finite-difference fallback (using UNWRAPPED angles, avoids +-pi jumps)
        if dt <= 1e-6:
            return self.last_qd.copy()

        qd_fd = (q_now - self.q_prev) / dt
        a = float(VEL_SMOOTH_ALPHA)
        qd = a * qd_fd + (1.0 - a) * self.last_qd
        return qd

    def read_state(self):
        t = time.perf_counter()
        dt = t - self.last_time

        q = self.read_positions_model()

        if not hasattr(self, "q_prev"):
            self.q_prev = q.copy()

        qd = self.read_velocities(q, dt)

        self.q_prev = q.copy()
        self.last_qd = qd.copy()
        self.last_time = t

        # x = [q1,q2,dq1,dq2]
        return np.array([q[0], q[1], qd[0], qd[1]], dtype=float), dt

    def rate_limit(self, tau_cmd, tau_prev, dt):
        max_step = self.max_tau_rate * max(dt, 1e-6)
        delta = np.clip(tau_cmd - tau_prev, -max_step, +max_step)
        return tau_prev + delta

    def send_torque(self, tau):
        tau = np.asarray(tau, dtype=float).copy()

        # clip
        tau[0] = float(np.clip(tau[0], -self.tau_limit[0], +self.tau_limit[0]))
        tau[1] = float(np.clip(tau[1], -self.tau_limit[1], +self.tau_limit[1]))

        # sign mapping
        tau_hw = np.array([
            SHOULDER_TAU_SIGN * tau[0],
            ELBOW_TAU_SIGN    * tau[1],
        ], dtype=float)

        # send to hardware
        self.shoulder_motor.setTargetTorque(float(tau_hw[0]))
        self.elbow_motor.setTargetTorque(float(tau_hw[1]))

    def stop(self):
        self._stop = True

    def shutdown_safely(self):
        print("[WARN] Shutdown: sending 0 torque, disabling motors, candle.end()")
        try:
            for _ in range(8):
                self.send_torque(np.zeros(2, dtype=float))
                time.sleep(0.02)
        except Exception:
            pass

        try:
            for mid in [self.shoulder_id, self.elbow_id]:
                self.candle.controlMd80Enable(mid, False)
        except Exception:
            pass

        try:
            self.candle.end()
        except Exception:
            pass

    def choose_kref(self, x_hat):
        """
        Projection + monotone progress protection.
        """
        # projection candidate
        k_cand, dist = proj.pick_progress_farthest_inside_tube(
            x_hat, self.X_nom, self.Wproj, self.tube_radius
        )

        # monotone rule: don't jump backward (or allow only tiny backtrack)
        k_min = max(0, int(self.k_ref_prev) - int(ALLOW_BACKTRACK))
        k_ref = max(k_min, int(k_cand))

        # also cap to valid
        k_ref = int(np.clip(k_ref, 0, self.N_nom - 1))

        return k_ref, float(dist)

    def close_to_goal(self, x):
        q1e = wrap_pi(x[0] - GOAL_Q1)
        q2e = wrap_pi(x[1] - GOAL_Q2)
        qe = np.sqrt(q1e*q1e + q2e*q2e)
        ve = np.sqrt(x[2]*x[2] + x[3]*x[3])
        return (qe <= LOCK_ANGLE_TOL) and (ve <= LOCK_VEL_TOL)

    def run(self):
        print("\n================ RUNNING (NO ROS) ================")
        print("Controls:")
        print("  - Ctrl+C : emergency stop (0 torque + disable)")
        print("==================================================\n")

        next_time = time.perf_counter()
        last_print = time.perf_counter()

        while not self._stop:
            now = time.perf_counter()
            if now < next_time:
                time.sleep(max(0.0, next_time - now))
                continue

            # Read hardware state
            x, _dt_meas = self.read_state()
            x_hat = x  # no extra estimator here

            # Choose reference knot
            k_ref, dist = self.choose_kref(x_hat)

            # Terminal lock: once close, force final knot (prevents falling back to "down")
            if LOCK_TO_GOAL_WHEN_CLOSE and self.close_to_goal(x_hat):
                k_ref = self.N_nom - 1

            # store progress
            self.k_ref_prev = k_ref

            # K_list has length N-1, nominal has length N
            kK = int(np.clip(k_ref, 0, self.K_list.shape[0] - 1))

            x_bar = self.X_nom[k_ref]
            u_bar = self.U_nom[k_ref]
            Kk    = self.K_list[kK]

            # TVLQR tracking torque
            tau_cmd = u_bar - Kk @ (x_hat - x_bar)

            # scale
            tau_cmd = TORQUE_SCALE * np.asarray(tau_cmd, dtype=float)

            # clip to torque limits
            tau_cmd = np.array([
                np.clip(tau_cmd[0], -self.tau_limit[0], +self.tau_limit[0]),
                np.clip(tau_cmd[1], -self.tau_limit[1], +self.tau_limit[1]),
            ], dtype=float)

            # rate limit
            tau_send = self.rate_limit(tau_cmd, self.tau_last, self.dt_ctrl)
            self.tau_last = tau_send.copy()

            # send
            self.send_torque(tau_send)

            # diagnostics
            if (time.perf_counter() - last_print) >= PRINT_EVERY:
                sat1 = abs(tau_send[0]) >= (self.tau_limit[0] - 1e-9)
                sat2 = abs(tau_send[1]) >= (self.tau_limit[1] - 1e-9)
                sat = int(sat1) + int(sat2)

                q1e = wrap_pi(x[0] - GOAL_Q1)
                q2e = wrap_pi(x[1] - GOAL_Q2)

                print(
                    f"q=[{x[0]: .3f}, {x[1]: .3f}]  dq=[{x[2]: .3f}, {x[3]: .3f}]  "
                    f"err_q=[{q1e: .3f},{q2e: .3f}]  "
                    f"k_ref={k_ref:3d}  dist={dist: .3f}  "
                    f"tau=[{tau_send[0]: .3f}, {tau_send[1]: .3f}]  sat={sat}"
                )
                last_print = time.perf_counter()

            next_time += self.dt_ctrl


def main():
    runner = None

    def handle_sigint(sig, frame):
        if runner is not None:
            runner.stop()

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        runner = RealPendulumTVLQR()
        runner.run()
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if runner is not None:
            runner.shutdown_safely()


if __name__ == "__main__":
    main()
