%% ACRL HW3 - Stepper motor adaptive augmentation + RBF NN
% FULL SCRIPT (with SLIDE projection operator) + EXTRA ERROR GRAPHS (v4)
%
% This script simulates the stepper motor tracking a 2nd-order reference model
% using Adaptive Augmentation + an RBF NN, and compares 4 controller variants:
%
%   1) sigma-mod         (NO projection)
%   2) e-mod             (NO projection)
%   3) sigma-mod + proj  (projection operator EXACTLY like your slide)
%   4) e-mod + proj      (projection operator EXACTLY like your slide)
%
% v4 CHANGES (requested):
%   - Adds BACK the no-load tracking figure (2x2): theta vs theta_r (best controller)
%   - Adds BACK the no-load summary metrics (1x3): RMS(e_theta), RMS(e_omega), max|v|
%   - Keeps the load-case ||e|| overlay subplot (load-case figure is 5x1)
%   - Adds more comments to make the flow clearer
%
% IMPORTANT NOTE ABOUT PROJECTION:
% Projection only changes the parameter update if the adaptive parameters
% approach the chosen bounds (Dx_max, Dr_max, Th_max). If bounds are too large,
% projection might NEVER activate => curves for "proj" and "no-proj" can overlap.

clear; close all; clc;

%% ===================== 1) Nominal parameters (controller design) ============
% These are the "nominal" parameters used in the controller design:
J0   = 4.5e-5;        % nominal inertia [kg*m^2]
B0   = 8.0e-4;        % nominal viscous friction [N*m*s/rad]
Km0  = 0.19;          % nominal torque constant [N*m/A]
Nm   = 50;            % motor electrical factor in sin(Nm*theta), cos(Nm*theta)

%% ===================== 2) Reference model (given) ===========================
% The reference model defines the desired closed-loop behavior:
%   x_m_dot = A_m x_m + B_m r
Am = [0 1; -24 -10];
Bm = [0; 24];         % input r = theta_c (command angle)

%% ===================== 3) Nominal reduced plant =============================
% We design the controller in "virtual input" form:
%   x = [theta; omega]
%   theta_dot = omega
%   omega_dot = - (B0/J0)*omega + v
% so B = [0;1] in this reduced model
A = [0 1; 0 -B0/J0];
B = [0; 1];

%% ===================== 4) Model-matching baseline gains Fx, Fr ==============
% We choose Fx, Fr so that the nominal closed-loop matches the reference model:
%   A + B Fx^T = Am
%   B Fr       = Bm
Fx = [-24; -10 + (B0/J0)];
Fr = 24;

%% ===================== 5) RBF NN: centers in [-30°, +30°] ====================
% Requirement: basis functions must lie in [-30deg, +30deg]
deg = pi/180;
theta_min = -30*deg;
theta_max =  30*deg;

Nrbf = 15;                                  % number of Gaussian RBFs
c = linspace(theta_min, theta_max, Nrbf).'; % centers equally spaced
dc = c(2) - c(1);                           % center spacing
sigma_rbf = 1.5*dc;                         % width (spread): gives smooth overlap

% Add a constant bias feature to allow representing constant offsets
use_bias = true;
if use_bias
    Nphi = Nrbf + 1;  % last feature = 1
else
    Nphi = Nrbf;
end

%% ===================== 6) Adaptive gains + modification params ==============
% Adaptation gain matrices:
%   Dx_hat (2x1): Gamma_x is 2x2
%   Dr_hat (scalar): Gamma_r is scalar
%   Theta_hat (Nphi x 1): Gamma_th is Nphi x Nphi
Gamma_x  = 25 * eye(2);
Gamma_r  = 25;
Gamma_th = 80 * eye(Nphi);

% sigma/e modification coefficients (leakage)
sigma_x  = 0.8;
sigma_r  = 0.8;
sigma_th = 0.8;

%% ===================== 7) Projection settings (bounds + eps_theta) ==========
% Bounds for adaptive parameters. If too large, projection won't activate.
Dx_max = 200;
Dr_max = 200;
Th_max = 200;

% eps_theta_proj is the "boundary thickness" parameter in the smooth projection.
eps_theta_proj = 0.05;

%% ===================== 8) Lyapunov matrix P =================================
% P solves: Am^T P + P Am = -Q (Lyapunov equation)
Q = eye(2);
P = lyap(Am', Q);

%% ===================== 9) Simulation settings ===============================
t0 = 0; tf = 30;

% Initial conditions
x0  = [0;0];            % plant state [theta; omega]
xm0 = [0;0];            % reference model state
Dx0 = [0;0];            % adaptive Dx
Dr0 = 0;                % adaptive Dr
Th0 = zeros(Nphi,1);    % NN weights

% Pack into ODE initial state:
% z = [x; xm; Dx; Dr; Theta]
z0 = [x0; xm0; Dx0; Dr0; Th0];

ode_opts = odeset('RelTol',1e-6,'AbsTol',1e-8);

%% ===================== 10) Controller variants ==============================
variants = { ...
    struct('tag','sigma'     ,'mod','sigma','proj',false), ...
    struct('tag','e'         ,'mod','e'    ,'proj',false), ...
    struct('tag','sigma_proj','mod','sigma','proj',true ), ...
    struct('tag','e_proj'    ,'mod','e'    ,'proj',true ) ...
};

pretty = { ...
    '\sigma-mod', ...
    'e-mod', ...
    '\sigma-mod + proj', ...
    'e-mod + proj' ...
};

% IMPORTANT: best_tag is only used for the "tracking" plot that shows ONE controller.
% It does NOT create a new controller. It simply selects one of the four tags.
best_tag = 'e_proj';  % = e-modification + projection

%% ===================== 11) Uncertainties + load case ========================
% No-load: uncertainty levels ±5%, ±25%, ±50%, ±75%
unc_levels   = [0.05 0.25 0.50 0.75];

% Load case: the exercise asks for unknown external load, test at ±5% uncertainty
do_load_case = true;

%% ===================== 12) Plot styles ======================================
% We use distinct line styles + markers so curves don't "hide" each other.
sty(1) = struct('LineStyle','-','Marker','o','LineWidth',2.0,'MarkerSize',7);
sty(2) = struct('LineStyle','--','Marker','s','LineWidth',2.0,'MarkerSize',7);
sty(3) = struct('LineStyle','-.','Marker','d','LineWidth',2.0,'MarkerSize',7);
sty(4) = struct('LineStyle',':','Marker','^','LineWidth',2.3,'MarkerSize',7);
marker_every = 50;

%% ===================== 13) Run all simulations ==============================
results = {};
idx = 0;

for v=1:numel(variants)
    % No-load runs for each uncertainty level
    for p_unc = unc_levels
        idx = idx + 1;
        results{idx} = simulate_case(variants{v}, p_unc, false);
        warn_if_diverged(results{idx});
    end

    % Load case runs (only at 5% uncertainty as per exercise part 3)
    if do_load_case
        idx = idx + 1;
        results{idx} = simulate_case(variants{v}, 0.05, true);
        warn_if_diverged(results{idx});
    end
end

%% ===================== 14) INFO: overlap check ==============================
% This helps explain why proj and non-proj curves may be identical:
% projection might not activate if parameters remain within bounds.
for p_unc = unc_levels
    check_overlap_pair(results,'sigma','sigma_proj',p_unc,false,1e-8);
    check_overlap_pair(results,'e','e_proj',p_unc,false,1e-8);
end
if do_load_case
    check_overlap_pair(results,'sigma','sigma_proj',0.05,true,1e-8);
    check_overlap_pair(results,'e','e_proj',0.05,true,1e-8);
end

%% ===================== FIGURE 1: No-load e_theta overlays (2x2) ==============
figure('Name','No-load: e_\theta(t) overlays');
tiledlayout(2,2,'Padding','compact','TileSpacing','compact');

for kU = 1:numel(unc_levels)
    p_unc = unc_levels(kU);
    nexttile; hold on; grid on;

    % Plot projected first, then non-projected, to reduce curve hiding
    plot_order = [3 4 1 2];

    for kk=1:numel(plot_order)
        v = plot_order(kk);
        rr = getRun(results, variants{v}.tag, p_unc, false);

        plot(rr.t, rr.e_theta, ...
            'LineStyle',sty(v).LineStyle, ...
            'Marker',sty(v).Marker, ...
            'LineWidth',sty(v).LineWidth, ...
            'MarkerSize',sty(v).MarkerSize, ...
            'MarkerIndices', 1:marker_every:numel(rr.t), ...
            'DisplayName',pretty{v});
    end

    xlabel('t [s]'); ylabel('e_\theta [rad]');
    title(sprintf('No-load: uncertainty \x00B1%.0f%%', 100*p_unc));
    legend('Location','best');
end

%% ===================== FIGURE 2: No-load e_omega overlays (2x2) ==============
figure('Name','No-load: e_\omega(t) overlays');
tiledlayout(2,2,'Padding','compact','TileSpacing','compact');

for kU = 1:numel(unc_levels)
    p_unc = unc_levels(kU);
    nexttile; hold on; grid on;

    plot_order = [3 4 1 2];

    for kk=1:numel(plot_order)
        v = plot_order(kk);
        rr = getRun(results, variants{v}.tag, p_unc, false);

        plot(rr.t, rr.e_omega, ...
            'LineStyle',sty(v).LineStyle, ...
            'Marker',sty(v).Marker, ...
            'LineWidth',sty(v).LineWidth, ...
            'MarkerSize',sty(v).MarkerSize, ...
            'MarkerIndices', 1:marker_every:numel(rr.t), ...
            'DisplayName',pretty{v});
    end

    xlabel('t [s]'); ylabel('e_\omega [rad/s]');
    title(sprintf('No-load: uncertainty \x00B1%.0f%%', 100*p_unc));
    legend('Location','best');
end

%% ===================== FIGURE 3: No-load ||e|| overlays (2x2) ================
figure('Name','No-load: ||e(t)|| overlays');
tiledlayout(2,2,'Padding','compact','TileSpacing','compact');

for kU = 1:numel(unc_levels)
    p_unc = unc_levels(kU);
    nexttile; hold on; grid on;

    plot_order = [3 4 1 2];

    for kk=1:numel(plot_order)
        v = plot_order(kk);
        rr = getRun(results, variants{v}.tag, p_unc, false);

        plot(rr.t, rr.e_norm, ...
            'LineStyle',sty(v).LineStyle, ...
            'Marker',sty(v).Marker, ...
            'LineWidth',sty(v).LineWidth, ...
            'MarkerSize',sty(v).MarkerSize, ...
            'MarkerIndices', 1:marker_every:numel(rr.t), ...
            'DisplayName',pretty{v});
    end

    xlabel('t [s]'); ylabel('||e||');
    title(sprintf('No-load: uncertainty \x00B1%.0f%%', 100*p_unc));
    legend('Location','best');
end

%% ===================== FIGURE 4 (ADDED BACK): No-load tracking (best) ========
% This is exactly the type of figure you showed:
% One controller (best_tag) and compare theta (plant) vs theta_r (reference model).
figure('Name','No-load: tracking (best controller)');
tiledlayout(2,2,'Padding','compact','TileSpacing','compact');

for kU = 1:numel(unc_levels)
    p_unc = unc_levels(kU);
    nexttile; hold on; grid on;

    rrB = getRun(results, best_tag, p_unc, false);

    plot(rrB.t, rrB.theta,   'LineWidth',2.0, 'DisplayName','\theta (plant)');
    plot(rrB.t, rrB.theta_r, '--','LineWidth',2.0, 'DisplayName','\theta_r (model)');

    xlabel('t [s]'); ylabel('\theta [rad]');
    title(sprintf('No-load: \x00B1%.0f%% tracking (best=%s)', 100*p_unc, best_tag));
    legend('Location','best');
end

%% ===================== FIGURE 5 (ADDED BACK): No-load summary metrics ========
% This is the other figure you showed:
% (1) RMS(e_theta) vs uncertainty
% (2) RMS(e_omega) vs uncertainty
% (3) max|v| vs uncertainty
%
% NOTE: To avoid needing the Signal Processing Toolbox, we compute RMS as:
%   RMS(x) = sqrt(mean(x.^2))
rms_e_theta = nan(numel(variants), numel(unc_levels));
rms_e_omega = nan(numel(variants), numel(unc_levels));
max_v       = nan(numel(variants), numel(unc_levels));

for v=1:numel(variants)
    for kU=1:numel(unc_levels)
        rr = getRun(results, variants{v}.tag, unc_levels(kU), false);

        et = rr.e_theta(isfinite(rr.e_theta));
        ew = rr.e_omega(isfinite(rr.e_omega));
        vv = rr.v(isfinite(rr.v));

        if ~isempty(et), rms_e_theta(v,kU) = sqrt(mean(et.^2)); end
        if ~isempty(ew), rms_e_omega(v,kU) = sqrt(mean(ew.^2)); end
        if ~isempty(vv), max_v(v,kU) = max(abs(vv)); end
    end
end

% Jitter x-axis slightly so overlapping points are visible
xU = 100*unc_levels;
xjit = [-1.2, -0.4, +0.4, +1.2];

figure('Name','No-load: summary metrics');
tiledlayout(1,3,'Padding','compact','TileSpacing','compact');

nexttile; hold on; grid on;
for v=1:numel(variants)
    plot(xU + xjit(v), rms_e_theta(v,:), ...
        'LineStyle',sty(v).LineStyle,'Marker',sty(v).Marker, ...
        'LineWidth',sty(v).LineWidth,'MarkerSize',sty(v).MarkerSize, ...
        'DisplayName',pretty{v});
end
xlabel('uncertainty level [%]'); ylabel('RMS(e_\theta) [rad]');
title('RMS(e_\theta) vs uncertainty');
legend('Location','best');

nexttile; hold on; grid on;
for v=1:numel(variants)
    plot(xU + xjit(v), rms_e_omega(v,:), ...
        'LineStyle',sty(v).LineStyle,'Marker',sty(v).Marker, ...
        'LineWidth',sty(v).LineWidth,'MarkerSize',sty(v).MarkerSize, ...
        'DisplayName',pretty{v});
end
xlabel('uncertainty level [%]'); ylabel('RMS(e_\omega) [rad/s]');
title('RMS(e_\omega) vs uncertainty');
legend('Location','best');

nexttile; hold on; grid on;
for v=1:numel(variants)
    plot(xU + xjit(v), max_v(v,:), ...
        'LineStyle',sty(v).LineStyle,'Marker',sty(v).Marker, ...
        'LineWidth',sty(v).LineWidth,'MarkerSize',sty(v).MarkerSize, ...
        'DisplayName',pretty{v});
end
xlabel('uncertainty level [%]'); ylabel('max |v| [rad/s^2]');
title('max|v| vs uncertainty');
legend('Location','best');

%% ===================== FIGURE 6: Load case (±5%) details (5x1) ===============
% Includes overlays for e_theta, e_omega, ||e||, plus tracking and load torque
if do_load_case
    figure('Name','Load case (±5%) details');
    tiledlayout(5,1,'Padding','compact','TileSpacing','compact');

    plot_order = [3 4 1 2];

    % (1) e_theta overlay
    nexttile; hold on; grid on;
    for kk=1:numel(plot_order)
        v = plot_order(kk);
        rr = getRun(results, variants{v}.tag, 0.05, true);
        plot(rr.t, rr.e_theta, ...
            'LineStyle',sty(v).LineStyle,'Marker',sty(v).Marker, ...
            'LineWidth',sty(v).LineWidth,'MarkerSize',sty(v).MarkerSize, ...
            'MarkerIndices', 1:marker_every:numel(rr.t), ...
            'DisplayName',pretty{v});
    end
    xlabel('t [s]'); ylabel('e_\theta [rad]');
    title('Load case: e_\theta overlay');
    legend('Location','best');

    % (2) e_omega overlay
    nexttile; hold on; grid on;
    for kk=1:numel(plot_order)
        v = plot_order(kk);
        rr = getRun(results, variants{v}.tag, 0.05, true);
        plot(rr.t, rr.e_omega, ...
            'LineStyle',sty(v).LineStyle,'Marker',sty(v).Marker, ...
            'LineWidth',sty(v).LineWidth,'MarkerSize',sty(v).MarkerSize, ...
            'MarkerIndices', 1:marker_every:numel(rr.t), ...
            'DisplayName',pretty{v});
    end
    xlabel('t [s]'); ylabel('e_\omega [rad/s]');
    title('Load case: e_\omega overlay');
    legend('Location','best');

    % (3) ||e|| overlay (requested earlier)
    nexttile; hold on; grid on;
    for kk=1:numel(plot_order)
        v = plot_order(kk);
        rr = getRun(results, variants{v}.tag, 0.05, true);
        plot(rr.t, rr.e_norm, ...
            'LineStyle',sty(v).LineStyle,'Marker',sty(v).Marker, ...
            'LineWidth',sty(v).LineWidth,'MarkerSize',sty(v).MarkerSize, ...
            'MarkerIndices', 1:marker_every:numel(rr.t), ...
            'DisplayName',pretty{v});
    end
    xlabel('t [s]'); ylabel('||e||');
    title('Load case: ||e|| overlay');
    legend('Location','best');

    % (4) tracking for best variant
    nexttile; hold on; grid on;
    rrB = getRun(results, best_tag, 0.05, true);
    plot(rrB.t, rrB.theta,   'LineWidth',2.0, 'DisplayName','\theta (plant)');
    plot(rrB.t, rrB.theta_r, '--','LineWidth',2.0, 'DisplayName','\theta_r (model)');
    xlabel('t [s]'); ylabel('\theta [rad]');
    title(sprintf('Load case: tracking (best=%s)', best_tag));
    legend('Location','best');

    % (5) true load torque vs NN estimate (best variant)
    nexttile; hold on; grid on;
    plot(rrB.t, rrB.TL_true, 'LineWidth',2.0, 'DisplayName','T_L true');
    plot(rrB.t, rrB.TL_hat,  '--','LineWidth',2.0, 'DisplayName','\hat{T}_L (NN)');
    xlabel('t [s]'); ylabel('Torque [N·m]');
    title('Load torque: true vs NN estimate');
    legend('Location','best');
end

%% ============================ LOCAL FUNCTIONS ================================
% Local functions are unchanged in structure; I only add comments where useful.

function warn_if_diverged(res)
    % Warn if the simulation produced NaNs/Infs (numerical instability)
    bad = any(~isfinite(res.theta)) || any(~isfinite(res.omega)) || any(~isfinite(res.v));
    if bad
        fprintf('[WARN] Divergence/NaNs detected: tag=%s, unc=%.0f%%, load=%d\n', ...
            res.tag, 100*res.p_unc, res.include_load);
    end
end

function check_overlap_pair(results, tag1, tag2, p_unc, include_load, tol)
    % Checks if two curves are numerically identical (within tolerance).
    % Useful to diagnose why projection and non-projection sometimes look the same.
    r1 = getRun(results, tag1, p_unc, include_load);
    r2 = getRun(results, tag2, p_unc, include_load);

    n = min(numel(r1.e_theta), numel(r2.e_theta));
    d = max(abs(r1.e_theta(1:n) - r2.e_theta(1:n)));

    if isfinite(d) && d < tol
        fprintf('[INFO] Curves overlap (<=%.1e): %s and %s at unc=%.0f%%, load=%d\n', ...
            tol, tag1, tag2, 100*p_unc, include_load);
    end
end

function rr = getRun(results, tag, p_unc, include_load)
    % Retrieve a simulation run by (controller tag, uncertainty level, load flag)
    for i=1:numel(results)
        r = results{i};
        if strcmp(r.tag, tag) && abs(r.p_unc - p_unc)<1e-12 && r.include_load==include_load
            rr = r;
            return;
        end
    end
    error('Run not found: tag=%s, p=%.2f, load=%d', tag, p_unc, include_load);
end

function res = simulate_case(variant, p_unc, include_load)
    % Runs one simulation for a chosen controller variant, uncertainty level, and load flag.

    % Pull shared constants from base workspace (keeps the script simple)
    J0   = evalin('base','J0');   B0   = evalin('base','B0');   Km0  = evalin('base','Km0');
    Nm   = evalin('base','Nm');   Am   = evalin('base','Am');   Bm   = evalin('base','Bm');
    Fx   = evalin('base','Fx');   Fr   = evalin('base','Fr');   P    = evalin('base','P');
    c    = evalin('base','c');    sigma_rbf = evalin('base','sigma_rbf'); use_bias = evalin('base','use_bias');
    theta_min = evalin('base','theta_min'); theta_max = evalin('base','theta_max');
    Gamma_x = evalin('base','Gamma_x'); Gamma_r = evalin('base','Gamma_r'); Gamma_th = evalin('base','Gamma_th');
    sigma_x = evalin('base','sigma_x'); sigma_r = evalin('base','sigma_r'); sigma_th = evalin('base','sigma_th');
    Dx_max  = evalin('base','Dx_max');  Dr_max  = evalin('base','Dr_max');  Th_max   = evalin('base','Th_max');
    eps_theta_proj = evalin('base','eps_theta_proj');
    z0      = evalin('base','z0');      t0      = evalin('base','t0');      tf       = evalin('base','tf');
    ode_opts = evalin('base','ode_opts');

    % True (uncertain) plant parameters:
    % We interpret ±p_unc as multiplicative deviations.
    J_true  = J0*(1+p_unc);
    B_true  = B0*(1+p_unc);
    Km_true = Km0*(1-p_unc);

    % Pack parameters for the ODE
    p = struct();
    p.J0=J0; p.B0=B0; p.Km0=Km0; p.Nm=Nm;
    p.J=J_true; p.B=B_true; p.Km=Km_true;

    p.Am=Am; p.Bm=Bm;
    p.Fx=Fx; p.Fr=Fr;
    p.P=P;

    p.c=c; p.sigma_rbf=sigma_rbf; p.use_bias=use_bias;
    p.theta_min=theta_min; p.theta_max=theta_max;

    p.Gamma_x=Gamma_x; p.Gamma_r=Gamma_r; p.Gamma_th=Gamma_th;
    p.sigma_x=sigma_x; p.sigma_r=sigma_r; p.sigma_th=sigma_th;

    p.Dx_max=Dx_max; p.Dr_max=Dr_max; p.Th_max=Th_max;
    p.eps_theta_proj = eps_theta_proj;

    p.include_load = include_load;
    p.mod_type = variant.mod;   % 'sigma' or 'e'
    p.use_proj = variant.proj;  % true/false

    % Integrate closed-loop system
    odefun = @(t,z) closed_loop_ode(t,z,p);
    [t,z] = ode45(odefun, [t0 tf], z0, ode_opts);

    % Post-process into useful signals and return
    res = post_process(t,z,p);
    res.tag = variant.tag;
    res.p_unc = p_unc;
    res.include_load = include_load;
end

function dz = closed_loop_ode(t,z,p)
    % z = [x(2); xm(2); Dx(2); Dr(1); Theta(Nphi)]
    x  = z(1:2);
    xm = z(3:4);
    Dx = z(5:6);
    Dr = z(7);
    Th = z(8:end);

    theta = x(1);
    omega = x(2);

    % Reference command r(t): 5° step every 3 seconds, clamp to [-30°, +30°]
    step_rad = 5*pi/180;
    r_raw = step_rad * floor(t/3);
    r = min(max(r_raw, p.theta_min), p.theta_max);

    % Reference model dynamics
    xm_dot = p.Am*xm + p.Bm*r;

    % Tracking error
    e = x - xm;

    % RBF features Phi(theta) evaluated only inside the allowed region
    theta_phi = min(max(theta, p.theta_min), p.theta_max);
    Phi = rbf_features(theta_phi, p.c, p.sigma_rbf, p.use_bias);

    % Adaptation driving signal: psi = e^T P B, with B=[0;1]
    psi = e.' * p.P * [0;1];

    % Effective input gain sign (positive here)
    sgnLambda = +1;

    % ---- Control law: baseline + adaptive augmentation ----
    % Baseline nominal control
    v_nom = p.Fx.'*x + p.Fr*r;

    % Adaptive augmentation (Dx, Dr, and NN term)
    v_aug = Dx.'*x + Dr*r + Th.'*Phi;

    % Total "virtual input" v (approximately desired acceleration)
    v = v_nom + v_aug;

    % Convert virtual input to commanded torque via nominal inertia:
    % tau_cmd = J0*v
    tau_cmd = p.J0 * v;

    % Choose currents using sin/cos identity so torque becomes ~ (Km/Km0)*tau_cmd
    ia = -(tau_cmd/p.Km0) * sin(p.Nm*theta);
    ib =  (tau_cmd/p.Km0) * cos(p.Nm*theta);

    % External load torque (unknown to controller; known only to simulation)
    if p.include_load
        TL = 1e-3*(cos(2*theta)^2)*sin(3*theta);
    else
        TL = 0;
    end

    % True electromagnetic torque
    tau_e = -p.Km*ia*sin(p.Nm*theta) + p.Km*ib*cos(p.Nm*theta);

    % Plant dynamics
    theta_dot = omega;
    omega_dot = (1/p.J) * (tau_e - p.B*omega - TL);
    x_dot = [theta_dot; omega_dot];

    % ---- Raw adaptive laws (sigma or e modification) ----
    switch lower(p.mod_type)
        case 'sigma'
            Dx_dot_raw = -p.Gamma_x  * ( x*psi   + p.sigma_x*Dx ) * sgnLambda;
            Dr_dot_raw = -p.Gamma_r  * ( r*psi   + p.sigma_r*Dr ) * sgnLambda;
            Th_dot_raw = -p.Gamma_th * ( Phi*psi + p.sigma_th*Th ) * sgnLambda;

        case 'e'
            psi_norm = abs(psi);
            Dx_dot_raw = -p.Gamma_x  * ( x*psi   + p.sigma_x*psi_norm*Dx ) * sgnLambda;
            Dr_dot_raw = -p.Gamma_r  * ( r*psi   + p.sigma_r*psi_norm*Dr ) * sgnLambda;
            Th_dot_raw = -p.Gamma_th * ( Phi*psi + p.sigma_th*psi_norm*Th ) * sgnLambda;

        otherwise
            error('Unknown mod_type: %s', p.mod_type);
    end

    % ---- SLIDE projection operator (optional) ----
    if p.use_proj
        Dx_dot = proj_slide(Dx, Dx_dot_raw, p.Dx_max, p.eps_theta_proj);
        Dr_dot = proj_slide(Dr, Dr_dot_raw, p.Dr_max, p.eps_theta_proj);
        Th_dot = proj_slide(Th, Th_dot_raw, p.Th_max, p.eps_theta_proj);
    else
        Dx_dot = Dx_dot_raw;
        Dr_dot = Dr_dot_raw;
        Th_dot = Th_dot_raw;
    end

    % Total ODE
    dz = [x_dot; xm_dot; Dx_dot; Dr_dot; Th_dot];
end

function Phi = rbf_features(theta, c, sigma, use_bias)
    % Gaussian RBF features
    diff = theta - c;
    phi = exp(-(diff.^2)/(2*sigma^2));
    if use_bias
        Phi = [phi; 1];
    else
        Phi = phi;
    end
end

function y_proj = proj_slide(theta, y, theta_max, eps_theta)
    % proj_slide: EXACT projection operator from your slide.
    %
    % f(theta) = (||theta||^2 - theta_max^2) / (eps_theta*theta_max^2)
    % grad f   = 2 theta / (eps_theta*theta_max^2)
    %
    % Proj(theta,y) = y - (gradf gradf^T)/(||gradf||^2) * y * f(theta)
    % if f(theta)>0 AND y^T gradf>0

    theta_vec = theta(:);
    y_vec     = y(:);

    f = ( (theta_vec.'*theta_vec) - theta_max^2 ) / (eps_theta*theta_max^2);
    gradf = (2*theta_vec) / (eps_theta*theta_max^2);

    if (f > 0) && (y_vec.'*gradf > 0) && (gradf.'*gradf > 1e-14)
        y_proj_vec = y_vec - (gradf*(gradf.'))/(gradf.'*gradf) * y_vec * f;
    else
        y_proj_vec = y_vec;
    end

    y_proj = reshape(y_proj_vec, size(theta));
end

function r = post_process(t,z,p)
    % Extract trajectories from the ODE solution and reconstruct useful signals

    x  = z(:,1:2);
    xm = z(:,3:4);
    Dx = z(:,5:6);
    Dr = z(:,7);
    Th = z(:,8:end);

    theta   = x(:,1);
    omega   = x(:,2);
    theta_r = xm(:,1);
    omega_r = xm(:,2);

    % Error components
    e_theta = theta - theta_r;
    e_omega = omega - omega_r;

    % Full error magnitude ||e||
    e_norm = sqrt(e_theta.^2 + e_omega.^2);

    % Reconstruct v(t) and load torque signals
    v       = zeros(size(t));
    TL_true = zeros(size(t));
    TL_hat  = zeros(size(t));

    for k=1:numel(t)
        th = theta(k);
        xk = [th; omega(k)];
        xmk = [theta_r(k); omega_r(k)];
        ek = xk - xmk;

        % r(t) again
        step_rad = 5*pi/180;
        r_raw = step_rad * floor(t(k)/3);
        rcmd = min(max(r_raw, p.theta_min), p.theta_max);

        % Phi(theta)
        th_phi = min(max(th, p.theta_min), p.theta_max);
        Phi = rbf_features(th_phi, p.c, p.sigma_rbf, p.use_bias);

        % Adaptation signal psi (used here only if you want to debug)
        psi = ek.' * p.P * [0;1];

        % Virtual input v
        v_nom = p.Fx.'*xk + p.Fr*rcmd;
        v_aug = Dx(k,:)*xk + Dr(k)*rcmd + Th(k,:)*Phi;
        v(k) = v_nom + v_aug;

        % True load torque
        if p.include_load
            TL_true(k) = 1e-3*(cos(2*th)^2)*sin(3*th);
        else
            TL_true(k) = 0;
        end

        % NN torque-equivalent estimate:
        % NN contributes v_nn = Theta^T Phi; in torque units this corresponds to:
        % tau_hat ~ (Km/Km0) * J0 * v_nn
        v_nn = Th(k,:)*Phi;
        TL_hat(k) = (p.Km/p.Km0) * (p.J0 * v_nn);

        %#ok<NASGU> % keep psi for optional debugging
    end

    r = struct();
    r.t = t;

    r.theta   = theta;
    r.omega   = omega;
    r.theta_r = theta_r;
    r.omega_r = omega_r;

    r.e_theta = e_theta;
    r.e_omega = e_omega;
    r.e_norm  = e_norm;

    r.v       = v;

    r.TL_true = TL_true;
    r.TL_hat  = TL_hat;

    % Store adaptive parameters too (useful for checking projection activation)
    r.Dx_hat = Dx;
    r.Dr_hat = Dr;
    r.Th_hat = Th;
end



