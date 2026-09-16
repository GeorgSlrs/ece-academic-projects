
# simulate.py (FULL)
from __future__ import annotations
import numpy as np
from typing import Dict, Any, Optional

from rfj_params import RFJParams
from rfj_dynamics import plant_rhs, rk4_step
from controllers import make_controller, sat_sym
from noise_models import quantize, gauss, random_walk, dropout_hold, DelayLine, deadzone


def reference_signal(t: float, ref_type: str, step_amp: float, step_time: float) -> float:
    """
    Reference generator for the controlled joint/link angle phi.

    The returned value is phi_ref.  Older versions called this theta_ref, but the
    thesis objective is now explicitly link/joint angle tracking.
    """
    if ref_type == "step":
        return float(step_amp) if t >= float(step_time) else 0.0
    if ref_type == "sine":
        return float(step_amp) * np.sin(2*np.pi*1.0*t)
    return 0.0


def disturbance_tauL(t: float, tauL_max: float, kind: str) -> float:
    if tauL_max <= 0:
        return 0.0
    if kind == "sine":
        return float(tauL_max * np.sin(2*np.pi*0.8*t))
    if kind == "pulse":
        return float(tauL_max if (2.0 <= t <= 2.2) else 0.0)
    return 0.0


def simulate_L2(
    p_nom: RFJParams,
    controller_mode: str = "pid",
    T: float = 5.0,
    ref_type: str = "step",
    disturb_kind: str = "none",
    controller_cfg: Optional[Dict[str, Any]] = None,
    ref_cfg: Optional[Dict[str, Any]] = None,
    noise_cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    controller_cfg = controller_cfg or {}
    ref_cfg = ref_cfg or {}
    noise_cfg = noise_cfg or {}

    step_amp = float(ref_cfg.get("step_amp", 0.5))
    step_time = float(ref_cfg.get("step_time", 0.1))

    seed = int(noise_cfg.get("seed", 0))
    rng = np.random.default_rng(seed)

    meas_sigma = float(noise_cfg.get("meas_sigma", 0.0))
    meas_bias_theta = float(noise_cfg.get("meas_bias_theta", 0.0))
    meas_bias_phi = float(noise_cfg.get("meas_bias_phi", 0.0))
    meas_rw_theta = float(noise_cfg.get("meas_rw_theta", 0.0))
    meas_rw_phi = float(noise_cfg.get("meas_rw_phi", 0.0))
    dropout_prob = float(noise_cfg.get("dropout_prob", 0.0))

    enc_counts = int(noise_cfg.get("enc_counts_per_rev", p_nom.counts_per_rev))
    dtheta_q = float(2*np.pi / max(1, enc_counts))
    dphi_q = float(2*np.pi / max(1, enc_counts))

    v_cmd_sigma = float(noise_cfg.get("v_cmd_sigma", 0.0))
    v_cmd_bias = float(noise_cfg.get("v_cmd_bias", 0.0))
    cmd_delay_steps = int(noise_cfg.get("cmd_delay_steps", 0))

    tau_process_sigma = float(noise_cfg.get("tau_process_sigma", 0.0))

    p_true = p_nom.true_params()

    dt = float(p_nom.dt_sim)
    Ts = float(p_nom.Ts_ctrl)
    N = int(np.floor(T / dt)) + 1

    ctrl = make_controller(controller_mode, p_nom=p_nom, cfg=controller_cfg)
    if hasattr(ctrl, "reset"):
        ctrl.reset()

    delay = DelayLine(cmd_delay_steps, init_value=0.0)

    # logs
    t_log = np.zeros(N)
    x_log = np.zeros((N, 5))
    theta_hat_log = np.zeros(N)
    phi_hat_log = np.zeros(N)
    alpha_hat_log = np.zeros(N)

    # Main reference log.  phi_ref is the actual target now.
    phi_ref_log = np.zeros(N)

    # Backward-compatible alias: old analysis notebooks may still look for theta_ref.
    theta_ref_log = np.zeros(N)

    Vcmd_cmd_log = np.zeros(N)
    Vcmd_log = np.zeros(N)
    duty_log = np.zeros(N)

    tauL_log = np.zeros(N)
    dbg_log = []

    x = np.zeros(5)

    theta_hat_hold = 0.0
    phi_hat_hold = 0.0

    b_theta = meas_bias_theta
    b_phi = meas_bias_phi

    next_ctrl_t = 0.0
    Vcmd_applied = 0.0
    Vcmd_cmd = 0.0

    for k in range(N):
        t = k * dt
        theta, phi, dtheta, dphi, i = x

        phi_ref = reference_signal(t, ref_type, step_amp, step_time)

        tauL_det = disturbance_tauL(t, float(p_true.tauL_max), disturb_kind)
        tauL_rand = gauss(rng, tau_process_sigma)
        tauL = tauL_det + tauL_rand

        if t + 1e-12 >= next_ctrl_t:
            b_theta = random_walk(b_theta, rng, meas_rw_theta)
            b_phi = random_walk(b_phi, rng, meas_rw_phi)

            theta_meas = theta + b_theta + gauss(rng, meas_sigma)
            phi_meas = phi + b_phi + gauss(rng, meas_sigma)

            theta_q = quantize(theta_meas, dtheta_q)
            phi_q = quantize(phi_meas, dphi_q)

            theta_hat_hold = dropout_hold(theta_q, theta_hat_hold, rng, dropout_prob)
            phi_hat_hold = dropout_hold(phi_q, phi_hat_hold, rng, dropout_prob)
            alpha_hat_hold = theta_hat_hold - phi_hat_hold

            # Measurements given to controllers.
            meas = {
                "theta_hat": theta_hat_hold,
                "phi_hat": phi_hat_hold,
                "alpha_hat": alpha_hat_hold,
            }

            # Reference bundle.
            # IMPORTANT:
            # - phi_ref is the true/main tracking target.
            # - theta_ref is kept only as a backward-compatible alias.
            # - alpha_ref defaults to 0 because small twist is a natural vibration-suppression target.
            ref = {
                "phi_ref": phi_ref,
                "theta_ref": phi_ref,
                "alpha_ref": 0.0,
            }

            Vcmd_cmd, dbg = ctrl.step(meas, ref, Ts)
            Vcmd_cmd = sat_sym(Vcmd_cmd, p_nom.Vbus)

            V_delayed = delay.push(Vcmd_cmd)
            V_noisy = V_delayed + v_cmd_bias + gauss(rng, v_cmd_sigma)
            V_dz = deadzone(V_noisy, p_nom.v_deadzone)
            Vcmd_applied = sat_sym(V_dz, p_nom.Vbus)

            next_ctrl_t += Ts
            dbg_log.append({"t": t, "mode": controller_mode, **dbg})

        def f_local(xx):
            return plant_rhs(xx, V_cmd=Vcmd_applied, tau_L=tauL, p=p_true)

        x = rk4_step(f_local, x, dt)

        t_log[k] = t
        x_log[k, :] = x
        theta_hat_log[k] = theta_hat_hold
        phi_hat_log[k] = phi_hat_hold
        alpha_hat_log[k] = theta_hat_hold - phi_hat_hold
        phi_ref_log[k] = phi_ref
        theta_ref_log[k] = phi_ref

        Vcmd_cmd_log[k] = Vcmd_cmd
        Vcmd_log[k] = Vcmd_applied
        duty_log[k] = float(np.clip(Vcmd_applied / max(p_nom.Vbus, 1e-9), -1.0, 1.0))
        tauL_log[k] = tauL

    return {
        "p_nom": p_nom,
        "p_true": p_true,
        "controller_mode": controller_mode,
        "ref_type": ref_type,
        "disturb_kind": disturb_kind,
        "ref_cfg": {"step_amp": step_amp, "step_time": step_time},
        "noise_cfg": dict(noise_cfg),
        "controller_cfg": dict(controller_cfg),

        "t": t_log,
        "x": x_log,

        "theta_hat": theta_hat_log,
        "phi_hat": phi_hat_log,
        "alpha_hat": alpha_hat_log,

        "phi_ref": phi_ref_log,
        "theta_ref": theta_ref_log,

        "Vcmd_cmd": Vcmd_cmd_log,
        "Vcmd": Vcmd_log,
        "duty": duty_log,

        "tauL": tauL_log,
        "dbg": dbg_log,
    }
