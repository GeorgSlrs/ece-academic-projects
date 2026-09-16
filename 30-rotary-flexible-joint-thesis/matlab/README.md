# MATLAB / Simulink RFJ prototype

These scripts preserve an earlier thesis implementation with motor-angle (`theta`) tracking. They are separate from the current Python implementation, which tracks the link angle (`phi`).

- `build_lvl0.m`: mechanics-only state-space plant with torque input, PID and twist feedback.
- `build_lvl1.m`: motor electrical state and average H-bridge, duty/voltage command paths and optional back-EMF feed-forward.
- `build_lvl2.m`: sampled controller, quantized sensor path and continuous plant, using PID, sliding-mode or adaptive backstepping in `rfj_controller_core.m`.
- `flex_joint_params.m`: physical parameters and state-space matrices.
- `build_all.m`: model building, simulation and animation orchestration.
- `build_3d.m` / `rfj_quick_anim.m`: Simscape Multibody visualization and a 2D fallback.
- `analysis_*.m`, `rfj_metrics.m`, `run_all_analysis.m`: frequency-domain, state-space, discrete-time and performance analysis.

MATLAB and Simulink are required. Frequency-domain/state-space analysis uses Control System Toolbox; the 3D path uses Simscape Multibody. No toolbox dependencies are bundled.

The source entry points are `build_all` and `run_all_analysis`, but this historical snapshot was not executed during archiving. A static review found that `build_lvl2.m` expects `C_out_e`, `dth_q` and `dph_q`, whereas `flex_joint_params.m` exports `Ce`, `dtheta_q` and `dphi_q`. These inconsistencies require review before rebuilding the L2 model. Generated `.slx`/`.slxc` files and `slprj` caches are omitted.
