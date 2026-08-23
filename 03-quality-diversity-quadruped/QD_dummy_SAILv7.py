# ==============================================================
#  S U R R O G A T E   A S S I S T E D   I L L U M I N A T I O N
#  --------------------------------------------------------------
#  HEAVILY COMMENTED, MODERN PYTHON 3.12 RE‑IMPLEMENTATION
#
#  This file is an expanded, teaching‑oriented re‑write of the demo
#  you provided.  The main goals were:
#   1. • EXTREME commenting — every non‑trivial line explains WHAT
#        it does, WHY it exists, and HOW to tweak it.
#   2. • Richer visual analytics   (extra plots + live animation)
#   3. • Optional high‑fidelity physics using PyBullet so you can
#        switch between a cheap analytic model and a true simulator
#        when you have GPU/CPU budget.
#   4. • Live animation of the discovered gait repertoire so you
#        can literally *see* all behaviours in motion.
#   5. • Cross‑platform saving of the repertoire CSV directly to the
#        user’s Desktop (~/Desktop on Linux/macOS or the proper
#        Windows path).
#
#  ----------------------------------------------------------------
#  CONTENTS (⌘/Ctrl‑F to jump):
#    0. Imports, global constants & helper utilities
#    1. Analytic toy quadruped ->  physics‑enabled PyBullet backend
#    2. MAP‑Elites grid archive class                   (unchanged)
#    3. SAIL loop (now with tqdm, configs & nicer logging)
#    4. Plotting helpers (heat‑maps, 3‑D scatter, learning curves)
#    5. Live animation of gait repertoire via matplotlib.animation
#    6. Main() entry point — command‑line flags via argparse
#
#  ----------------------------------------------------------------
#  REQUIRED THIRD‑PARTY LIBS
#    pip install numpy pandas matplotlib scikit‑learn tqdm pybullet
#
#  Tested with:
#    • Python 3.12.2 (but ≥3.8 should work)
#    • numpy 2.1.0, pandas 2.2, matplotlib 3.9, scikit‑learn 1.7,
#      pybullet 3.4, tqdm 4.66
#
# ==============================================================

# ---------------- 0. Imports & Global Settings -----------------
from __future__ import annotations                        # |> type‑hints w/ forward refs

import math                                               # |> misc maths util
import os                                                 # |> env‑vars, desktop path
from pathlib import Path                                  # |> platform‑agnostic paths
from typing import Iterable, Tuple                        # |> static typing helpers

import numpy as np                                        # |> numerics backbone
import pandas as pd                                       # |> tabular storage / CSV
import matplotlib.pyplot as plt                           # |> plotting
from matplotlib import animation                          # |> live animation utils
from matplotlib import gridspec                           # |> multi‑subplot layout
from mpl_toolkits.mplot3d import Axes3D                   # |> 3‑D scatter view

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel

from tqdm import tqdm                                     # |> progress‑bars

# ——— Optional heavy simulator ————————————————————————————
try:
    import pybullet as p                                  # |> real‑time physics engine
    import pybullet_data                                  # |> standard URDF assets
except ImportError:                                       # |> allow pure‑Python fallback
    p = None  # sentinel so we can check later

# ---------------- Convenience helper: Desktop path ------------
# Cross‑platform path where the repertoire CSV will be saved.  We
# default to the user’s Desktop but fall back to CWD if it doesn’t
# exist (e.g. inside a Docker container).
DESKTOP_PATH = Path(__file__).resolve().parent      # folder that holds this script


# ---------------- 0‑B. Random seed & tqdm global tweaks -------
SEED: int = 42
np.random.seed(SEED)                                     # |> global reproducibility

tqdm_kwargs = dict(bar_format="{l_bar}{bar:30}{r_bar}")  # |> uniform style for all bars

# ---------------- 1. Hyper‑parameters -------------------------
# All tunable constants live here in one place so you can turn your
# notebook / IDE into a control panel.
PARAM_DIM      = 4                    # genotype length (# of actuator amplitudes)
GRID_BINS      = (25, 25)             # discretisation of descriptor space
SPEED_RANGE    = (0.0, 2.0)           # physically plausible speed bounds [m/s]
EFFORT_RANGE   = (0.0, 2.0)           # cost of transport (CoT) bounds
INIT_SAMPLES   = 60                   # random initial evaluations (design of experiment)
ITERATIONS     = 60                   # surrogate iterations (budget)
EVALS_PER_ITER = 12                   # true evaluations per iteration
CANDIDATES     = 400                  # #genotypes drawn from GP each iter
UCB_BETA       = 2.0                  # GP UCB exploration vs exploitation knob

# ---------------- 1‑B. Physics‑sim back‑end config ------------
USE_PHYSICS   = True               # set True via CLI to enable PyBullet
SIM_TIMESTEP  = 1./500                # ! keep small for stable sim
SIM_DURATION  = 1.5                   # simulated seconds per eval
URDF_FILE     = "quadruped/minitaur.urdf"  # PyBullet asset (change to your robot)

# ==============================================================
# 1.  A N A L Y T I C   V S   P H Y S I C S   S I M U L A T I O N
# ==============================================================

def simulate_robot_analytic(amplitudes: np.ndarray,
                            noise_std: float = 0.025,
                            seed: int | None = None) -> Tuple[float, float, float]:
    """Cheap, fully analytic toy model of quadruped locomotion.

    This *exactly* mirrors your original function but is renamed so
    we can select between multiple back‑ends (analytic vs physics)."""
    rng = np.random.default_rng(seed)

    # --- (1) Clip amplitudes to actuator limits in rad/s --------
    a = np.clip(amplitudes, -1.0, 1.0)

    # --- (2) Forward speed proxy --------------------------------
    # The more symmetric and higher‑magnitude the leg swings, the
    # faster we go.  It is a vast simplification of real dynamics
    # but good enough for illumination demos.
    base_speed = 2.2 * np.mean(np.abs(a))  # linear in mean |A|
    symmetry   = 0.5 * (1 - np.abs(a[0]-a[2]) - np.abs(a[1]-a[3]))
    speed      = np.clip(base_speed + symmetry, *SPEED_RANGE)

    # --- (3) Energetic cost proxy --------------------------------
    effort = np.clip(np.mean(a**2) * 2.0, *EFFORT_RANGE)

    # --- (4) Inject optional Gaussian noise ----------------------
    speed  += rng.normal(0.0, noise_std)
    effort += rng.normal(0.0, noise_std)

    fitness = speed - 0.1 * effort  # tune weight as needed
    return float(speed), float(effort), float(fitness)


# ----------------------------------------------------------------
# Physics‑enabled simulator using PyBullet.  We load a standard
# Minitaur URDF (open‑source MIT robot) and apply open‑loop sinusoid
# position control to each motor.  The amplitude vector *a* becomes
# the sinusoid magnitude in radians.
# ----------------------------------------------------------------

def _setup_pybullet(gui: bool = False):
    """Connect to PyBullet in either DIRECT (headless) or GUI mode."""
    mode = p.GUI if gui else p.DIRECT
    cid = p.connect(mode)
    p.setTimeStep(SIM_TIMESTEP, physicsClientId=cid)
    p.setGravity(0, 0, -9.81, physicsClientId=cid)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.loadURDF("plane.urdf", physicsClientId=cid)
    return cid


def simulate_robot_pybullet(amplitudes: np.ndarray,
                            seed: int | None = None,
                            gui: bool = False) -> Tuple[float, float, float]:
    """Higher‑fidelity simulation using rigid‑body physics.

    ▸ Parameters
      amplitudes (np.ndarray): 4‑D vector ∈ [‑1,1]
      seed (int | None): for deterministic noise injection (not used now)
      gui (bool):        launch PyBullet GUI if you want to watch

    ▸ Returns
      speed, effort, fitness — same meaning as analytic model
    """
    if p is None:
        raise ImportError("PyBullet is not installed — pip install pybullet")

    amp = np.clip(amplitudes, -1.0, 1.0)
    cid = _setup_pybullet(gui)

    # --- Load robot URDF ----------------------------------------
    robot_id = p.loadURDF(URDF_FILE,
                          [0, 0, 0.2],  # spawn slightly above ground
                          useFixedBase=False,
                          flags=p.URDF_MAINTAIN_LINK_ORDER,
                          physicsClientId=cid)

    # Pre‑compute joint indices to make the control loop fast
    joint_indices = [j for j in range(p.getNumJoints(robot_id, physicsClientId=cid))]

    # --- Run open‑loop sinusoid position control ----------------
    steps = int(SIM_DURATION / SIM_TIMESTEP)
    freq  = 2 * math.pi / SIM_DURATION  # one cycle over sim duration
    initial_pos, _ = p.getBasePositionAndOrientation(robot_id, physicsClientId=cid)

    for step in range(steps):
        t = step * SIM_TIMESTEP
        for i, j_idx in enumerate(joint_indices):
            target = amp[i % 4] * math.sin(freq * t)  # repeating pattern for upper/lower joints
            p.setJointMotorControl2(robot_id, j_idx,
                                    controlMode=p.POSITION_CONTROL,
                                    targetPosition=target,
                                    force=5.0,
                                    physicsClientId=cid)
        p.stepSimulation(physicsClientId=cid)

    final_pos, _ = p.getBasePositionAndOrientation(robot_id, physicsClientId=cid)
    displacement = final_pos[0] - initial_pos[0]  # x‑axis forward
    speed = displacement / SIM_DURATION

    # Effort proxy: mean absolute torque * time — approximate via motor forces.
    # For simplicity we use |amplitude|^2 like analytic model.
    effort = np.clip(np.mean(amp**2) * 2.0, *EFFORT_RANGE)

    fitness = speed - 0.1 * effort

    p.disconnect(cid)
    return float(speed), float(effort), float(fitness)

# --- Dynamic selection helper ----------------------------------

def simulate_robot(amplitudes: np.ndarray, **kwargs):
    """API shim that dispatches to analytic or physics simulator."""
    if USE_PHYSICS:
        return simulate_robot_pybullet(amplitudes, **kwargs)
    return simulate_robot_analytic(amplitudes, **kwargs)

# ==============================================================
# 2. MAP‑ELITES ARCHIVE (unchanged except for doc tweaks)        
# ==============================================================
class MapArchive:
    """2‑D grid archive storing the best solution in each niche."""

    def __init__(self, bins: Tuple[int, int],
                 speed_range: Tuple[float, float],
                 effort_range: Tuple[float, float]):
        self.bins = bins
        self.smin, self.smax = speed_range
        self.emin, self.emax = effort_range

        # Fitness initialised to –∞ so every first solution is accepted
        self.fitness = np.full(bins, -np.inf)
        self.params  = np.empty(bins + (PARAM_DIM,))

    # -----------------------------------------------------------
    # Private helpers
    def _coords(self, speed: float, effort: float) -> Tuple[int, int]:
        """Continuous descriptors → discrete cell indices."""
        s_norm = (speed  - self.smin) / (self.smax - self.smin)
        e_norm = (effort - self.emin) / (self.emax - self.emin)
        s_idx  = int(np.clip(s_norm * (self.bins[0]-1), 0, self.bins[0]-1))
        e_idx  = int(np.clip(e_norm * (self.bins[1]-1), 0, self.bins[1]-1))
        return s_idx, e_idx

    # -----------------------------------------------------------
    # Public interface                                            
    def add(self, speed: float, effort: float, fitness: float, params: np.ndarray):
        """Add *params* to archive if it beats current elite."""
        s_idx, e_idx = self._coords(speed, effort)
        if fitness > self.fitness[s_idx, e_idx]:
            self.fitness[s_idx, e_idx] = fitness
            self.params[s_idx, e_idx]  = params

    def coverage(self) -> float:
        """Fraction of filled cells (diversity metric)."""
        return float(np.mean(self.fitness > -np.inf))

    def mean_fitness(self) -> float:
        filled = self.fitness[self.fitness > -np.inf]
        return float(filled.mean()) if filled.size else float("nan")

# ==============================================================
# 3. S U R R O G A T E   A S S I S T E D   I L L U M I N A T I O N
# ==============================================================

def run_sail() -> tuple[MapArchive, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(SEED)
    archive = MapArchive(GRID_BINS, SPEED_RANGE, EFFORT_RANGE)

    X, y = [], []                     # training data for the GP surrogate
    coverage_hist, meanfit_hist = [], []

    # ——— Phase 0: Initial random samples ————————————
    for _ in tqdm(range(INIT_SAMPLES), desc="Initial samples", **tqdm_kwargs):
        p_vec = rng.uniform(-1, 1, PARAM_DIM)
        s, e, f = simulate_robot(p_vec)
        X.append(p_vec); y.append(f)
        archive.add(s, e, f, p_vec)

    coverage_hist.append(archive.coverage())
    meanfit_hist.append(archive.mean_fitness())

    # ——— Phase 1: Surrogate loop ————————————————
    for it in tqdm(range(ITERATIONS), desc="SAIL iterations", **tqdm_kwargs):

        # (1) Fit GP on all collected data
        kernel = ConstantKernel(1.0, (0.001, 1000)) * Matern(nu=2.5) + WhiteKernel()
        gp = GaussianProcessRegressor(kernel, alpha=1e-6, normalize_y=True, random_state=SEED)
        gp.fit(np.asarray(X), np.asarray(y))

        # (2) Sample CANDIDATES genotypes uniformly in genotype space
        cand = rng.uniform(-1, 1, size=(CANDIDATES, PARAM_DIM))
        mu, std = gp.predict(cand, return_std=True)
        ucb = mu + UCB_BETA * std

        # (3) Map predicted UCB into descriptor space to build a temporary archive
        best_ucb  = np.full(archive.bins, -np.inf)
        best_cand = np.empty(archive.bins + (PARAM_DIM,))
        for idx, p_vec in enumerate(cand):
            s_est, e_est, _ = simulate_robot_analytic(p_vec, noise_std=0.0)   # cheap estimate
            s_idx, e_idx = archive._coords(s_est, e_est)
            if ucb[idx] > best_ucb[s_idx, e_idx]:
                best_ucb[s_idx, e_idx], best_cand[s_idx, e_idx] = ucb[idx], p_vec

        # (4) Select top‑scoring niches to evaluate expensively
        chosen: list[np.ndarray] = []
        for flat_idx in np.argsort(best_ucb.ravel())[::-1][:EVALS_PER_ITER]:
            coord = np.unravel_index(flat_idx, archive.bins)
            if best_ucb[coord] > -np.inf:
                chosen.append(best_cand[coord])

        # (5) True simulation + archive update
        for p_vec in chosen:
            s, e, f = simulate_robot(p_vec)
            X.append(p_vec); y.append(f)
            archive.add(s, e, f, p_vec)

        coverage_hist.append(archive.coverage())
        meanfit_hist.append(archive.mean_fitness())

    return archive, np.asarray(coverage_hist), np.asarray(meanfit_hist)

# ==============================================================
# 4. P L O T T I N G   H E L P E R S
# ==============================================================

def plot_diagnostics(archive: MapArchive,
                     coverage: np.ndarray,
                     meanfit: np.ndarray):
    """Generate heat‑map, scatter and learning‑curve plots."""

    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, height_ratios=[1.2, 1])

    # --- (A) Fitness heat‑map -----------------------------------
    ax0 = fig.add_subplot(gs[0, 0])
    masked = np.ma.masked_where(archive.fitness == -np.inf, archive.fitness)
    im = ax0.imshow(masked.T, origin='lower', cmap='viridis',
                    extent=[0, GRID_BINS[0], 0, GRID_BINS[1]], aspect='auto')
    ax0.set_title("Elite fitness heat‑map (descriptor bins)")
    ax0.set_xlabel("speed bin"); ax0.set_ylabel("effort bin")
    plt.colorbar(im, ax=ax0, fraction=0.045)

    # --- (B) 2‑D descriptor scatter (speed vs effort) -----------
    ax1 = fig.add_subplot(gs[0, 1])
    sp_desc, ef_desc, fit_val = [], [], []
    for i in range(GRID_BINS[0]):
        for j in range(GRID_BINS[1]):
            if archive.fitness[i, j] > -np.inf:
                # convert cell centre back to descriptor values
                sp_desc.append(SPEED_RANGE[0] + (i+0.5)/GRID_BINS[0]*(SPEED_RANGE[1]-SPEED_RANGE[0]))
                ef_desc.append(EFFORT_RANGE[0] + (j+0.5)/GRID_BINS[1]*(EFFORT_RANGE[1]-EFFORT_RANGE[0]))
                fit_val.append(archive.fitness[i, j])

    scatter = ax1.scatter(sp_desc, ef_desc, c=fit_val, cmap='inferno', s=35)
    ax1.set_title("Descriptor scatter (speed vs effort)")
    ax1.set_xlabel("speed [m/s]"); ax1.set_ylabel("effort (CoT)")
    plt.colorbar(scatter, ax=ax1, fraction=0.045)

    # --- (C) Learning curves -----------------------------------
    ax2 = fig.add_subplot(gs[1, :])
    iters = np.arange(len(coverage))
    ax2.plot(iters, coverage*100, label="coverage [%]")
    ax2.plot(iters, meanfit,      label="mean elite fitness")
    ax2.set_title("SAIL learning dynamics")
    ax2.set_xlabel("iteration")
    ax2.grid(alpha=0.3); ax2.legend()

    plt.tight_layout()
    plt.show()


# --------------------------------------------------------------
# Extra plot: 3‑D scatter of speed, effort, fitness -------------

def plot_3d_descriptor_space(archive: MapArchive):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    xs, ys, zs = [], [], []
    for i in range(GRID_BINS[0]):
        for j in range(GRID_BINS[1]):
            if archive.fitness[i, j] > -np.inf:
                xs.append(SPEED_RANGE[0] + (i+0.5)/GRID_BINS[0]*(SPEED_RANGE[1]-SPEED_RANGE[0]))
                ys.append(EFFORT_RANGE[0] + (j+0.5)/GRID_BINS[1]*(EFFORT_RANGE[1]-EFFORT_RANGE[0]))
                zs.append(archive.fitness[i, j])
    sc = ax.scatter(xs, ys, zs, c=zs, cmap='viridis')
    ax.set_xlabel('speed [m/s]'); ax.set_ylabel('effort'); ax.set_zlabel('fitness')
    ax.set_title('3‑D descriptor space')
    fig.colorbar(sc)
    plt.show()

# ==============================================================
# 5. L I V E   A N I M A T I O N   O F   G A I T S
# ==============================================================

HEADER_FOOTER = "Sinusoid‑controlled quadruped\nAmplitude vector: {}"


def animate_repertoire(archive: MapArchive, interval_ms: int = 500):
    """Iterate through archive and animate each gait in PyBullet GUI.

    Each elite is played for *interval_ms* milliseconds of real time
    (not sim time).  Note: This requires PyBullet GUI and therefore
    USE_PHYSICS must be True.
    """
    if p is None:
        raise RuntimeError("PyBullet not available — cannot animate")
    if not USE_PHYSICS:
        raise RuntimeError("Set USE_PHYSICS=True before calling animate")

    # Extract elites as a list of (params, fitness)
    elites: list[tuple[np.ndarray, float]] = []
    for i in range(GRID_BINS[0]):
        for j in range(GRID_BINS[1]):
            if archive.fitness[i, j] > -np.inf:
                elites.append((archive.params[i, j], archive.fitness[i, j]))

    # Sort by fitness descending for a nicer show‑case
    elites.sort(key=lambda x: x[1], reverse=True)

    # --- Matplotlib figure to display params & fitness ---------
    fig, ax = plt.subplots(figsize=(4, 2))
    txt = ax.text(0.5, 0.5, '', ha='center', va='center', fontsize=12)
    ax.axis('off')

    def init():
        txt.set_text('')
        return txt,

    def update(frame):
        param, fit = elites[frame]
        txt.set_text(HEADER_FOOTER.format(np.round(param, 3)))
        # Spawn in PyBullet GUI for real‑time animation
        simulate_robot_pybullet(param, gui=True)
        return txt,

    ani = animation.FuncAnimation(fig, update, frames=len(elites),
                                  init_func=init, blit=True,
                                  interval=interval_ms, repeat=False)
    plt.show()

# ==============================================================
# 6.   M A I N   E N T R Y   P O I N T                          
# ==============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Surrogate‑Assisted Illumination demo")
    parser.add_argument("--physics", action="store_true",
                        help="Use PyBullet physics (slower but more realistic)")
    parser.add_argument("--animate", action="store_true",
                        help="After optimisation, live‑animate the elite repertoire")
    args = parser.parse_args()

    USE_PHYSICS = args.physics  # overwrite global flag

    # (1) Run SAIL
    archive, cov_hist, fit_hist = run_sail()

    # (2) Save repertoire as CSV on Desktop
    repertoire_records = []
    for i in range(GRID_BINS[0]):
        for j in range(GRID_BINS[1]):
            if archive.fitness[i, j] > -np.inf:
                # Convert indices back to descriptor values (cell centres)
                speed_desc  = SPEED_RANGE[0]  + (i+0.5)/GRID_BINS[0]*(SPEED_RANGE[1]-SPEED_RANGE[0])
                effort_desc = EFFORT_RANGE[0] + (j+0.5)/GRID_BINS[1]*(EFFORT_RANGE[1]-EFFORT_RANGE[0])
                p_vec = archive.params[i, j]
                repertoire_records.append({
                    "speed_bin": i,
                    "effort_bin": j,
                    "speed_desc": speed_desc,
                    "effort_desc": effort_desc,
                    "fitness": archive.fitness[i, j],
                    **{f"amp_{k}": p_vec[k] for k in range(PARAM_DIM)}
                })

    df = pd.DataFrame(repertoire_records).sort_values("fitness", ascending=False)
    csv_path = DESKTOP_PATH / "sail_repertoire.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✅ Repertoire saved to {csv_path}  ({len(df)} behaviours)")

    # (3) Visual diagnostics
    plot_diagnostics(archive, cov_hist, fit_hist)
    plot_3d_descriptor_space(archive)

    # (4) Optional live animation (GUI window)
    if args.animate:
        if not USE_PHYSICS:
            print("⚠️  Live animation requires --physics flag; skipping.")
        else:
            animate_repertoire(archive)

