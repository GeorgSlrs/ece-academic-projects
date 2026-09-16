"""
run_all.py
==========
Main entry point for the Rotary Flexible Joint (RFJ) project.

IMPORTANT CHANGE:
- GUI opens BY DEFAULT.
- Use --nogui for CLI / single-run mode.

UPDATED CLI SUPPORT:
- The controlled output is now phi (the link/joint angle), not theta.
- Added selective alpha/twist-related tuning options.
- Kept backward-compatible defaults wherever possible.
"""

from __future__ import annotations
import argparse

from rfj_params import default_params
from simulate import simulate_L2
from metrics import print_metrics
from animate_3d import animate_3d


def main():
    ap = argparse.ArgumentParser()

    # ------------------------------------------------------------
    # GUI behavior
    # ------------------------------------------------------------
    ap.add_argument("--gui", action="store_true",
                    help="Launch GUI explicitly (not necessary anymore, GUI is default)")
    ap.add_argument("--nogui", action="store_true",
                    help="Disable GUI and run single simulation in CLI mode")

    # ------------------------------------------------------------
    # Controller mode
    # ------------------------------------------------------------
    ap.add_argument("--mode",
                    choices=["pid", "smc", "mit", "lqr", "lqg", "hinf", "mrac"],
                    default="pid")

    # ------------------------------------------------------------
    # Simulation / reference settings
    # ------------------------------------------------------------
    ap.add_argument("--T", type=float, default=5.0)
    ap.add_argument("--ref", choices=["step", "sine", "zero"], default="step")
    ap.add_argument("--stepTime", type=float, default=0.1)
    ap.add_argument("--stepAmp", type=float, default=0.5,
                    help="Amplitude of the phi_ref command [rad]")

    # ------------------------------------------------------------
    # Disturbance / uncertainty
    # ------------------------------------------------------------
    ap.add_argument("--dist", choices=["none", "sine", "pulse"], default="none")
    ap.add_argument("--tauL", type=float, default=0.0)
    ap.add_argument("--deltaKs", type=float, default=0.0)
    ap.add_argument("--deltaCs", type=float, default=0.0)

    # ------------------------------------------------------------
    # Noise
    # ------------------------------------------------------------
    ap.add_argument("--measSigma", type=float, default=0.0)
    ap.add_argument("--vSigma", type=float, default=0.0)
    ap.add_argument("--dropout", type=float, default=0.0)
    ap.add_argument("--delay", type=int, default=0)

    # ------------------------------------------------------------
    # PID settings
    # ------------------------------------------------------------
    ap.add_argument("--Kp", type=float, default=2.0)
    ap.add_argument("--Ki", type=float, default=5.0)
    ap.add_argument("--Kd", type=float, default=0.0)
    ap.add_argument("--Kalpha", type=float, default=0.0,
                    help="Optional anti-twist gain; main tracking is phi_ref - phi")

    # ------------------------------------------------------------
    # SMC settings
    # ------------------------------------------------------------
    ap.add_argument("--smcLam", type=float, default=5.0)
    ap.add_argument("--smcK", type=float, default=0.3)
    ap.add_argument("--smcPhi", type=float, default=0.05)
    ap.add_argument("--smcLamAlpha", type=float, default=0.0)
    ap.add_argument("--smcLamDalpha", type=float, default=0.0)

    # ------------------------------------------------------------
    # MIT settings
    # ------------------------------------------------------------
    ap.add_argument("--mitGamma", type=float, default=0.5)
    ap.add_argument("--mitWn", type=float, default=6.0)
    ap.add_argument("--mitZeta", type=float, default=0.9)
    ap.add_argument("--mitKr", type=float, default=1.0)

    # ------------------------------------------------------------
    # LQR / LQG settings
    # ------------------------------------------------------------
    ap.add_argument("--lqrQth", type=float, default=10.0)
    ap.add_argument("--lqrQph", type=float, default=80.0)
    ap.add_argument("--lqrQdth", type=float, default=1.0)
    ap.add_argument("--lqrQdph", type=float, default=2.0)
    ap.add_argument("--lqrQi", type=float, default=0.1)
    ap.add_argument("--lqrQalpha", type=float, default=5.0)
    ap.add_argument("--lqrQdalpha", type=float, default=0.5)
    ap.add_argument("--lqrRv", type=float, default=1.0)

    ap.add_argument("--lqgQproc", type=float, default=1e-5)
    ap.add_argument("--lqgRmeas", type=float, default=1e-4)

    # ------------------------------------------------------------
    # H∞ settings
    # ------------------------------------------------------------
    ap.add_argument("--wb", type=float, default=8.0)
    ap.add_argument("--Ms", type=float, default=2.0)
    ap.add_argument("--As", type=float, default=0.01)
    ap.add_argument("--Wu", type=float, default=0.2)
    ap.add_argument("--wt", type=float, default=25.0)
    ap.add_argument("--Mt", type=float, default=2.0)
    ap.add_argument("--At", type=float, default=0.02)
    ap.add_argument("--hinfOutput", choices=["phi", "theta", "alpha"], default="phi")

    # ------------------------------------------------------------
    # MRAC settings
    # ------------------------------------------------------------
    ap.add_argument("--mracWn", type=float, default=6.0)
    ap.add_argument("--mracZeta", type=float, default=0.9)
    ap.add_argument("--mracGamma", type=float, default=5.0)
    ap.add_argument("--mracSigma", type=float, default=0.05)

    # ------------------------------------------------------------
    # Analysis / animation
    # ------------------------------------------------------------
    ap.add_argument("--analysis", action="store_true")
    ap.add_argument("--savePlots", action="store_true")
    ap.add_argument("--noAnim", action="store_true")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--save3d", action="store_true")

    args = ap.parse_args()

    # ============================================================
    # GUI mode (DEFAULT)
    # ============================================================
    if not args.nogui:
        from rfj_gui import run_gui
        run_gui()
        return

    # ============================================================
    # Non-GUI / CLI mode
    # ============================================================
    p = default_params()
    p.deltaKs = args.deltaKs
    p.deltaCs = args.deltaCs
    p.tauL_max = args.tauL

    controller_cfg = {}

    if args.mode == "pid":
        controller_cfg["pid"] = {
            "Kp": args.Kp,
            "Ki": args.Ki,
            "Kd": args.Kd,
            "Kalpha": args.Kalpha,
        }

    if args.mode == "smc":
        controller_cfg["smc"] = {
            "lam": args.smcLam,
            "k": args.smcK,
            "phi": args.smcPhi,
            "lam_alpha": args.smcLamAlpha,
            "lam_dalpha": args.smcLamDalpha,
        }

    if args.mode == "mit":
        controller_cfg["mit"] = {
            "Kp": args.Kp,
            "Ki": args.Ki,
            "Kd": args.Kd,
            "Kr": args.mitKr,
            "Kalpha": args.Kalpha,
            "gamma": args.mitGamma,
            "wn": args.mitWn,
            "zeta": args.mitZeta,
        }

    if args.mode in ("lqr", "lqg"):
        controller_cfg["lqr"] = {
            "q_theta": args.lqrQth,
            "q_phi": args.lqrQph,
            "q_dtheta": args.lqrQdth,
            "q_dphi": args.lqrQdph,
            "q_i": args.lqrQi,
            "q_alpha": args.lqrQalpha,
            "q_dalpha": args.lqrQdalpha,
            "r_v": args.lqrRv,
        }

    if args.mode == "lqg":
        controller_cfg["lqg"] = {
            "q_proc": args.lqgQproc,
            "r_meas": args.lqgRmeas,
        }

    if args.mode == "hinf":
        controller_cfg["hinf"] = {
            "wb": args.wb,
            "Ms": args.Ms,
            "As": args.As,
            "Wu": args.Wu,
            "wt": args.wt,
            "Mt": args.Mt,
            "At": args.At,
            "output": args.hinfOutput,
        }

    if args.mode == "mrac":
        controller_cfg["mrac"] = {
            "wn": args.mracWn,
            "zeta": args.mracZeta,
            "gamma_scale": args.mracGamma,
            "sigma": args.mracSigma,
        }

    sim = simulate_L2(
        p_nom=p,
        controller_mode=args.mode,
        T=args.T,
        ref_type=args.ref,
        disturb_kind=args.dist,
        controller_cfg=controller_cfg,
        ref_cfg={
            "step_time": args.stepTime,
            "step_amp": args.stepAmp,
        },
        noise_cfg={
            "seed": 0,
            "meas_sigma": args.measSigma,
            "dropout_prob": args.dropout,
            "v_cmd_sigma": args.vSigma,
            "cmd_delay_steps": args.delay,
        },
    )

    print(p.summary())
    print_metrics(sim)

    if args.analysis:
        from analysis_run import run_analysis
        run_analysis(sim, save=args.savePlots, outdir="analysis_out", block=True)

    if not args.noAnim:
        animate_3d(sim, speed=args.speed, save=args.save3d, filename="RFJ_3D.mp4", show=True)


if __name__ == "__main__":
    main()
