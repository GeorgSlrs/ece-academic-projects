"""
rfj_gui.py
==========
This file creates the "Control Panel" window (the one with:
- controller selector (radio buttons)
- reference selector (radio buttons)
- many sliders for noise/uncertainty/weights
- buttons: Re-simulate, Start, Stop, Restart, Plots, End

It ALSO creates (and controls) the separate 3D animation window via RFJ3DPlayer,
so the project becomes a two-window app:
  Window A: Control Panel (this file)
  Window B: 3D Player (rfj_player_3d.py)

------------------------------------------------------------
Beginner-friendly overview of how this works
------------------------------------------------------------
1) We create the 3D player object:
       player = RFJ3DPlayer(...)
   This immediately creates its own Matplotlib figure window.

2) We create a second Matplotlib figure window (the control panel):
       fig = plt.figure(...)
   On this window, we add widgets (sliders, radio buttons, buttons).

3) When you click "Re-simulate":
   - We gather the current values from the widgets
   - We call simulate_L2(...) to run a new simulation
   - We tell the 3D player to display the new simulation:
         player.set_sim(sim)

4) Start/Stop/Restart buttons do NOT re-simulate:
   - They only control playback of the already-computed simulation.

5) Plots button now closes the GUI windows and then opens the full analysis set,
   so the total number of visible windows is consistent.

6) Closing either window will close the other and then show the same plots (blocking),
   so you always get the same analysis at the end.

------------------------------------------------------------
UPDATED DESIGN SUPPORT
------------------------------------------------------------
Following the controller redesign:
- phi_ref - phi_hat is now the main tracking objective.
- theta is still shown/measured as the motor-side coordinate.
- alpha = theta_hat - phi_hat is exposed selectively through tuning sliders.
- We do NOT force alpha into every controller in the same way.
- Instead, each controller gets only the alpha-related knobs that make sense for it.

------------------------------------------------------------
Where to run it
------------------------------------------------------------
From terminal in the project folder:
    python run_all.py --gui

(or directly)
    python rfj_gui.py
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from typing import Dict, Any

# Project imports
from rfj_params import default_params
from simulate import simulate_L2
from rfj_player_3d import RFJ3DPlayer


def run_gui():
    # ============================================================
    # 1) Create the 3D Player (Window B)
    # ============================================================
    player = RFJ3DPlayer(speed=1.0, loop=True)

    # ============================================================
    # 2) Create the Control Panel (Window A)
    # ============================================================
    fig = plt.figure(figsize=(18.8, 10.2))
    try:
        fig.canvas.manager.set_window_title("RFJ Control Panel")
    except Exception:
        pass

    # ============================================================
    # Helper functions to keep UI neat & readable
    # ============================================================

    def set_radio_font(radio: RadioButtons):
        for lab in radio.labels:
            lab.set_fontsize(10)

    def add_group_box(x: float, y: float, w: float, h: float, title: str):
        ax = fig.add_axes([x, y, w, h])
        ax.set_facecolor("#f7f7f7")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor("#d0d0d0")
            sp.set_linewidth(1.0)
        ax.text(0.02, 0.965, title, transform=ax.transAxes,
                fontsize=11, weight="bold", va="top")
        return ax

    def add_group_note(group_x: float, group_y: float, group_w: float, group_h: float,
                       text: str):
        fig.text(group_x + 0.03 * group_w,
                 group_y + group_h - 0.13 * group_h,
                 text,
                 fontsize=8.5,
                 color="#555555",
                 va="top",
                 ha="left")

    def add_slider_row(group_x: float, group_y: float, group_w: float, group_h: float,
                       row_index: int, nrows: int,
                       label: str, vmin: float, vmax: float, v0: float,
                       integer: bool = False) -> Slider:
        top_pad = 0.18 * group_h
        bottom_pad = 0.08 * group_h
        usable_h = max(group_h - top_pad - bottom_pad, 0.04)
        row_pitch = usable_h / max(nrows, 1)

        yc = group_y + group_h - top_pad - (row_index + 0.5) * row_pitch

        label_x = group_x + 0.03 * group_w
        slider_x = group_x + 0.42 * group_w
        slider_w = 0.43 * group_w

        ax_h = min(0.020, 0.46 * row_pitch)
        ax = fig.add_axes([slider_x, yc - 0.5 * ax_h, slider_w, ax_h])

        s = Slider(ax, "", float(vmin), float(vmax), valinit=float(v0))
        s.label.set_visible(False)
        s.valtext.set_fontsize(9.5)
        s.valtext.set_position((1.08, 0.5))
        s.valtext.set_ha("left")
        s.valtext.set_va("center")

        fig.text(label_x, yc, label, fontsize=9.5, va="center", ha="left")

        if integer:
            s.valtext.set_text(str(int(round(v0))))

            def _fix(_):
                s.valtext.set_text(str(int(round(s.val))))
            s.on_changed(_fix)
        else:
            def _fmt(_):
                val = float(s.val)
                if abs(val) < 1e-2 and val != 0.0:
                    s.valtext.set_text(f"{val:.1e}")
                elif abs(val) < 0.1:
                    s.valtext.set_text(f"{val:.3f}")
                elif abs(val) < 10:
                    s.valtext.set_text(f"{val:.2f}")
                else:
                    s.valtext.set_text(f"{val:.1f}")

            _fmt(None)
            s.on_changed(_fmt)

        return s

    # ============================================================
    # 3) Header text
    # ============================================================
    fig.text(0.02, 0.978, "RFJ Control Panel", fontsize=18, weight="bold", va="top")
    fig.text(
        0.02, 0.948,
        "Choose controller + reference → adjust grouped settings → Re-simulate.   "
        "H∞ requires: pip install control slycot",
        fontsize=9.5, va="top"
    )

    status = fig.text(0.02, 0.016, "", fontsize=9, color="crimson", va="bottom")

    # ============================================================
    # 4) Radio buttons (controller + reference)
    # ============================================================
    fig.text(0.025, 0.905, "Controller", fontsize=10, weight="bold", va="top")
    ax_mode = fig.add_axes([0.02, 0.79, 0.10, 0.11])
    radio_mode = RadioButtons(
        ax_mode,
        ("pid", "smc", "mit", "lqr", "lqg", "hinf", "mrac"),
        active=0
    )
    set_radio_font(radio_mode)

    fig.text(0.145, 0.905, "Reference", fontsize=10, weight="bold", va="top")
    ax_ref = fig.add_axes([0.14, 0.79, 0.08, 0.11])
    radio_ref = RadioButtons(ax_ref, ("step", "sine", "zero"), active=0)
    set_radio_font(radio_ref)

    # ============================================================
    # 5) Buttons (actions)
    # ============================================================
    ax_resim = fig.add_axes([0.25, 0.855, 0.71, 0.06])
    btn_resim = Button(ax_resim, "Re-simulate", hovercolor="0.90")

    ax_start = fig.add_axes([0.25, 0.79, 0.12, 0.05])
    btn_start = Button(ax_start, "Start", hovercolor="0.90")

    ax_stop = fig.add_axes([0.39, 0.79, 0.12, 0.05])
    btn_stop = Button(ax_stop, "Stop", hovercolor="0.90")

    ax_restart = fig.add_axes([0.53, 0.79, 0.12, 0.05])
    btn_restart = Button(ax_restart, "Restart", hovercolor="0.90")

    ax_plots = fig.add_axes([0.67, 0.79, 0.12, 0.05])
    btn_plots = Button(ax_plots, "Plots", hovercolor="0.90")

    ax_end = fig.add_axes([0.81, 0.79, 0.15, 0.05])
    btn_end = Button(ax_end, "End", hovercolor="0.90")

    # ============================================================
    # 6) Slider layout (grouped by "teams")
    # ============================================================
    gap = 0.015
    col_w = 0.18
    col_x = [0.02, 0.02 + (col_w + gap), 0.02 + 2 * (col_w + gap),
             0.02 + 3 * (col_w + gap), 0.02 + 4 * (col_w + gap)]

    top_y, top_h = 0.40, 0.32
    bot_y, bot_h = 0.05, 0.32

    # ----- Top row groups -----
    add_group_box(col_x[0], top_y, col_w, top_h, "Reference & Playback")
    s_speed = add_slider_row(col_x[0], top_y, col_w, top_h, 0, 3,
                             "Playback speed", 0.2, 6.0, 1.0)
    s_stepT = add_slider_row(col_x[0], top_y, col_w, top_h, 1, 3,
                             "Step time [s]", 0.0, 1.0, 0.1)
    s_stepA = add_slider_row(col_x[0], top_y, col_w, top_h, 2, 3,
                             "Phi step amp [rad]", 0.0, 1.2, 0.5)

    add_group_box(col_x[1], top_y, col_w, top_h, "Plant & Disturbance")
    s_dKs = add_slider_row(col_x[1], top_y, col_w, top_h, 0, 4,
                           "deltaKs", -0.5, 0.5, 0.0)
    s_dCs = add_slider_row(col_x[1], top_y, col_w, top_h, 1, 4,
                           "deltaCs", -0.5, 0.5, 0.0)
    s_tauL = add_slider_row(col_x[1], top_y, col_w, top_h, 2, 4,
                            "tauL max [Nm]", 0.0, 0.10, 0.0)
    s_tauPs = add_slider_row(col_x[1], top_y, col_w, top_h, 3, 4,
                             "tau_proc σ [Nm]", 0.0, 0.05, 0.0)

    add_group_box(col_x[2], top_y, col_w, top_h, "Measurement & Driver Noise")
    s_measS = add_slider_row(col_x[2], top_y, col_w, top_h, 0, 6,
                             "meas σ", 0.0, 0.05, 0.0)
    s_drop = add_slider_row(col_x[2], top_y, col_w, top_h, 1, 6,
                            "dropout", 0.0, 0.50, 0.0)
    s_enc = add_slider_row(col_x[2], top_y, col_w, top_h, 2, 6,
                           "counts/rev", 256, 8192, 4096, integer=True)
    s_vsig = add_slider_row(col_x[2], top_y, col_w, top_h, 3, 6,
                            "V σ [V]", 0.0, 2.0, 0.0)
    s_vbias = add_slider_row(col_x[2], top_y, col_w, top_h, 4, 6,
                             "V bias [V]", -2.0, 2.0, 0.0)
    s_delay = add_slider_row(col_x[2], top_y, col_w, top_h, 5, 6,
                             "delay [samples]", 0, 20, 0, integer=True)

    add_group_box(col_x[3], top_y, col_w, top_h, "PID / MIT Tuning")
    add_group_note(col_x[3], top_y, col_w, top_h,
                   "phi_ref-phi is primary; Kalpha adds optional anti-twist action.")
    s_Kp = add_slider_row(col_x[3], top_y, col_w, top_h, 0, 5,
                          "Kp", 0.0, 20.0, 2.0)
    s_Ki = add_slider_row(col_x[3], top_y, col_w, top_h, 1, 5,
                          "Ki", 0.0, 30.0, 5.0)
    s_Kd = add_slider_row(col_x[3], top_y, col_w, top_h, 2, 5,
                          "Kd", 0.0, 5.0, 0.0)
    s_Kalpha = add_slider_row(col_x[3], top_y, col_w, top_h, 3, 5,
                              "Kalpha", 0.0, 20.0, 0.0)
    s_mit_gamma = add_slider_row(col_x[3], top_y, col_w, top_h, 4, 5,
                                 "MIT gamma", 0.0, 10.0, 0.5)

    add_group_box(col_x[4], top_y, col_w, top_h, "SMC Tuning")
    add_group_note(col_x[4], top_y, col_w, top_h,
                   "lam_alpha and lam_dalpha help suppress flexible-joint oscillations.")
    s_smc_lam = add_slider_row(col_x[4], top_y, col_w, top_h, 0, 5,
                               "lambda", 0.5, 20.0, 5.0)
    s_smc_k = add_slider_row(col_x[4], top_y, col_w, top_h, 1, 5,
                             "k_switch", 0.01, 2.0, 0.3)
    s_smc_phi = add_slider_row(col_x[4], top_y, col_w, top_h, 2, 5,
                               "phi_bl", 0.005, 0.5, 0.05)
    s_smc_lam_alpha = add_slider_row(col_x[4], top_y, col_w, top_h, 3, 5,
                                     "lam_alpha", 0.0, 10.0, 0.0)
    s_smc_lam_dalpha = add_slider_row(col_x[4], top_y, col_w, top_h, 4, 5,
                                      "lam_dalpha", 0.0, 10.0, 0.0)

    # ----- Bottom row groups -----
    lqr_x = col_x[0]
    lqr_w = 2 * col_w + gap
    add_group_box(lqr_x, bot_y, lqr_w, bot_h, "LQR / LQG Weights")
    add_group_note(lqr_x, bot_y, lqr_w, bot_h,
                   "q_phi is the tracked-output weight; q_alpha/q_dalpha penalize twist.")
    s_lqr_qth = add_slider_row(lqr_x, bot_y, lqr_w, bot_h, 0, 8,
                               "q_theta", 0.1, 300.0, 10.0)
    s_lqr_qph = add_slider_row(lqr_x, bot_y, lqr_w, bot_h, 1, 8,
                               "q_phi", 0.1, 300.0, 80.0)
    s_lqr_qdth = add_slider_row(lqr_x, bot_y, lqr_w, bot_h, 2, 8,
                                "q_dtheta", 0.0, 50.0, 1.0)
    s_lqr_qdph = add_slider_row(lqr_x, bot_y, lqr_w, bot_h, 3, 8,
                                "q_dphi", 0.0, 50.0, 2.0)
    s_lqr_qi = add_slider_row(lqr_x, bot_y, lqr_w, bot_h, 4, 8,
                              "q_i", 0.0, 10.0, 0.1)
    s_lqr_qalpha = add_slider_row(lqr_x, bot_y, lqr_w, bot_h, 5, 8,
                                  "q_alpha", 0.0, 100.0, 5.0)
    s_lqr_qdalpha = add_slider_row(lqr_x, bot_y, lqr_w, bot_h, 6, 8,
                                   "q_dalpha", 0.0, 50.0, 0.5)
    s_lqr_rv = add_slider_row(lqr_x, bot_y, lqr_w, bot_h, 7, 8,
                              "r_v", 0.01, 10.0, 1.0)

    add_group_box(col_x[2], bot_y, col_w, bot_h, "LQG Estimator")
    add_group_note(col_x[2], bot_y, col_w, bot_h,
                   "LQG reuses the LQR/LQG weights on the left.")
    s_lqg_qproc = add_slider_row(col_x[2], bot_y, col_w, bot_h, 0, 2,
                                 "q_proc", 1e-7, 1e-2, 1e-5)
    s_lqg_rmeas = add_slider_row(col_x[2], bot_y, col_w, bot_h, 1, 2,
                                 "r_meas", 1e-7, 1e-1, 1e-4)

    add_group_box(col_x[3], bot_y, col_w, bot_h, "Hinf Weights")
    add_group_note(col_x[3], bot_y, col_w, bot_h,
                   "Default output is phi. W3 terms shape T for less oscillatory behavior.")
    s_wb = add_slider_row(col_x[3], bot_y, col_w, bot_h, 0, 7,
                          "wb [rad/s]", 1.0, 30.0, 8.0)
    s_Ms = add_slider_row(col_x[3], bot_y, col_w, bot_h, 1, 7,
                          "Ms", 1.1, 5.0, 2.0)
    s_As = add_slider_row(col_x[3], bot_y, col_w, bot_h, 2, 7,
                          "As", 0.001, 0.2, 0.01)
    s_Wu = add_slider_row(col_x[3], bot_y, col_w, bot_h, 3, 7,
                          "Wu", 0.01, 2.0, 0.2)
    s_wt = add_slider_row(col_x[3], bot_y, col_w, bot_h, 4, 7,
                          "wt [rad/s]", 0.0, 80.0, 25.0)
    s_Mt = add_slider_row(col_x[3], bot_y, col_w, bot_h, 5, 7,
                          "Mt", 1.1, 5.0, 2.0)
    s_At = add_slider_row(col_x[3], bot_y, col_w, bot_h, 6, 7,
                          "At", 0.001, 0.2, 0.02)

    add_group_box(col_x[4], bot_y, col_w, bot_h, "MRAC Tuning")
    add_group_note(col_x[4], bot_y, col_w, bot_h,
                   "MRAC basis now includes alpha and dalpha internally.")
    s_mrac_wn = add_slider_row(col_x[4], bot_y, col_w, bot_h, 0, 4,
                               "wn [rad/s]", 1.0, 20.0, 6.0)
    s_mrac_zeta = add_slider_row(col_x[4], bot_y, col_w, bot_h, 1, 4,
                                 "zeta", 0.2, 1.5, 0.9)
    s_mrac_gamma = add_slider_row(col_x[4], bot_y, col_w, bot_h, 2, 4,
                                  "gamma", 0.1, 30.0, 5.0)
    s_mrac_sigma = add_slider_row(col_x[4], bot_y, col_w, bot_h, 3, 4,
                                  "sigma", 0.0, 0.3, 0.05)

    # ============================================================
    # 7) State container (so callbacks can share state)
    # ============================================================
    state: Dict[str, Any] = {"last_sim": None, "plots_done": False, "closing": False}

    # ============================================================
    # 8) Function that builds a simulation from UI settings
    # ============================================================
    def build_sim():
        # Start from default nominal parameters
        p = default_params()

        # Apply uncertainty sliders
        p.deltaKs = float(s_dKs.val)
        p.deltaCs = float(s_dCs.val)
        p.tauL_max = float(s_tauL.val)

        # Read radio selections
        mode = radio_mode.value_selected
        ref_type = radio_ref.value_selected

        controller_cfg = {}

        # PID config (used if mode="pid")
        controller_cfg["pid"] = {
            "Kp": float(s_Kp.val),
            "Ki": float(s_Ki.val),
            "Kd": float(s_Kd.val),
            "Kalpha": float(s_Kalpha.val),
        }

        # MIT specific config
        controller_cfg["mit"] = {
            "Kp": float(s_Kp.val),
            "Ki": float(s_Ki.val),
            "Kd": float(s_Kd.val),
            "Kalpha": float(s_Kalpha.val),
            "gamma": float(s_mit_gamma.val),
        }

        # SMC specific config
        controller_cfg["smc"] = {
            "lam": float(s_smc_lam.val),
            "k": float(s_smc_k.val),
            "phi": float(s_smc_phi.val),
            "lam_alpha": float(s_smc_lam_alpha.val),
            "lam_dalpha": float(s_smc_lam_dalpha.val),
        }

        # LQR weights (used if mode="lqr" and also reused by LQG)
        controller_cfg["lqr"] = {
            "q_theta": float(s_lqr_qth.val),
            "q_phi": float(s_lqr_qph.val),
            "q_dtheta": float(s_lqr_qdth.val),
            "q_dphi": float(s_lqr_qdph.val),
            "q_i": float(s_lqr_qi.val),
            "q_alpha": float(s_lqr_qalpha.val),
            "q_dalpha": float(s_lqr_qdalpha.val),
            "r_v": float(s_lqr_rv.val),
        }

        # LQG estimator-specific config
        controller_cfg["lqg"] = {
            "q_proc": float(s_lqg_qproc.val),
            "r_meas": float(s_lqg_rmeas.val),
        }

        # H∞ specific config
        if mode == "hinf":
            controller_cfg["hinf"] = {
                "wb": float(s_wb.val),
                "Ms": float(s_Ms.val),
                "As": float(s_As.val),
                "Wu": float(s_Wu.val),
                "wt": float(s_wt.val),
                "Mt": float(s_Mt.val),
                "At": float(s_At.val),
                "output": "phi",
            }

        # MRAC specific config
        if mode == "mrac":
            controller_cfg["mrac"] = {
                "wn": float(s_mrac_wn.val),
                "zeta": float(s_mrac_zeta.val),
                "gamma_scale": float(s_mrac_gamma.val),
                "sigma": float(s_mrac_sigma.val),
            }

        sim = simulate_L2(
            p_nom=p,
            controller_mode=mode,
            T=5.0,
            ref_type=ref_type,
            disturb_kind="sine" if p.tauL_max > 0 else "none",
            controller_cfg=controller_cfg,
            ref_cfg={
                "step_time": float(s_stepT.val),
                "step_amp": float(s_stepA.val),
            },
            noise_cfg={
                "seed": 0,
                "meas_sigma": float(s_measS.val),
                "dropout_prob": float(s_drop.val),
                "enc_counts_per_rev": int(round(s_enc.val)),
                "v_cmd_sigma": float(s_vsig.val),
                "v_cmd_bias": float(s_vbias.val),
                "cmd_delay_steps": int(round(s_delay.val)),
                "tau_process_sigma": float(s_tauPs.val),
            },
        )
        return sim

    # ============================================================
    # 9) Plot function (calls analysis_run.py)
    # ============================================================
    def show_plots(block=True):
        if state["last_sim"] is None:
            status.set_text("No simulation yet. Click Re-simulate first.")
            return
        try:
            from analysis_run import run_analysis
            run_analysis(state["last_sim"], save=False, outdir="analysis_out", block=block)
        except Exception as e:
            status.set_text(f"PLOTS ERROR: {e}")

    # ============================================================
    # 10) Button callbacks
    # ============================================================
    def on_resim(_):
        status.set_text("")
        try:
            sim = build_sim()
            state["last_sim"] = sim
            player.set_sim(sim)
            player.set_speed(float(s_speed.val))
        except Exception as e:
            status.set_text(f"ERROR: {e}")

    def on_start(_):
        player.play()

    def on_stop(_):
        player.pause()

    def on_restart(_):
        player.restart()

    def on_plots(_):
        if state["closing"]:
            return
        state["plots_done"] = True
        state["closing"] = True
        try:
            plt.close(player.fig)
            plt.close(fig)
        except Exception:
            pass
        show_plots(block=True)

    def on_end(_):
        if state["closing"]:
            return
        state["plots_done"] = True
        state["closing"] = True
        try:
            plt.close(player.fig)
            plt.close(fig)
        except Exception:
            pass
        show_plots(block=True)

    btn_resim.on_clicked(on_resim)
    btn_start.on_clicked(on_start)
    btn_stop.on_clicked(on_stop)
    btn_restart.on_clicked(on_restart)
    btn_plots.on_clicked(on_plots)
    btn_end.on_clicked(on_end)

    def on_speed(_):
        player.set_speed(float(s_speed.val))
    s_speed.on_changed(on_speed)

    # ============================================================
    # 11) Close-event behavior
    # ============================================================
    def on_close(_event):
        if state["plots_done"] or state["closing"]:
            return
        state["plots_done"] = True
        state["closing"] = True
        try:
            plt.close(player.fig)
            plt.close(fig)
        except Exception:
            pass
        show_plots(block=True)

    fig.canvas.mpl_connect("close_event", on_close)
    player.fig.canvas.mpl_connect("close_event", on_close)

    # ============================================================
    # 12) Initial simulation at startup (so it moves immediately)
    # ============================================================
    try:
        sim0 = build_sim()
        state["last_sim"] = sim0
        player.set_sim(sim0)
    except Exception as e:
        status.set_text(f"ERROR: {e}")

    player.start()
    player.fig.show()
    fig.show()
    plt.show()


if __name__ == "__main__":
    run_gui()
