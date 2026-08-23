%% ACRL_HW2_Ex2_v2_two_param_MRAC.m
% MRAC for a 1st-order reference model using a 2-parameter controller
% Controller: u = th1*r - th2*yp
% Plant (under controller):  yp_dot = b*(th1*r - th2*yp)
% Model:                     ym_dot = -am*ym + bm*r
% Ideal params:              th1* = bm/b,  th2* = am/b
% Adaptation (normalized MIT, optional sigma-leak):
%   s1_dot = b*( r  - th2*s1)    % sensitivity wrt th1
%   s2_dot = b*(-yp - th2*s2)    % sensitivity wrt th2
%   th_i_dot = -(gamma/(alpha + s1^2 + s2^2)) * e * s_i - sigma_leak*th_i
%
% Plots: (1) |yp| vs omega with |ym| dashed, (2) RMS(e) vs omega,
%        (3) mean thetas vs omega with ideal lines, (4) time overlays.

clear; clc; close all;

%% ---------------- User / study parameters ----------------
b  = 4;           % plant gain used by simulator
am = 1; bm = 2;   % reference-model params: M(s)=bm/(s+am)

% ideal parameters for perfect model matching
th1_star = bm/b;  th2_star = am/b;

% sweep settings
A_list = [1.0, 2.0];
gammas = [0.05, 0.20, 1.00];
w_vec  = linspace(0.2, 2.0, 12);
nA = numel(A_list); nG = numel(gammas); nW = numel(w_vec);

% integration / adaptation safety
cycles_settle = 6;               % discard
cycles_meas   = 2;               % measure
theta_sat     = 10;              % soft clamp
sigma_leak    = 0.01;            % optional leakage (0 to disable)
alpha_norm    = 1e-3;            % normalization bias alpha > 0

% storage
Yp_amp = nan(nA,nG,nW);
Ym_amp = nan(nA,nG,nW);
E_rms  = nan(nA,nG,nW);
Th1_avg = nan(nA,nG,nW);
Th2_avg = nan(nA,nG,nW);

%% ========================= Sweep =========================
for ia = 1:nA
    A = A_list(ia);
    for ig = 1:nG
        gamma = gammas(ig);
        for iw = 1:nW
            w = w_vec(iw);
            [t,x] = simulate_case_v2(b,am,bm,gamma,A,w,theta_sat,sigma_leak,alpha_norm,cycles_settle,cycles_meas);
            if numel(t)<5, continue; end

            yp = x(:,1); ym = x(:,2); e = yp-ym; th = x(:,5:6);

            % steady-state window
            Tper = 2*pi/w; t_end = t(end);
            win  = min(cycles_meas*Tper, 0.25*t_end);
            idx  = t >= (t_end - win);
            if nnz(idx)<5, continue; end

            seg_yp = yp(idx); seg_ym = ym(idx); seg_e = e(idx); seg_th = th(idx,:);
            Yp_amp(ia,ig,iw)  = 0.5*(max(seg_yp)-min(seg_yp));
            Ym_amp(ia,ig,iw)  = 0.5*(max(seg_ym)-min(seg_ym));
            E_rms(ia,ig,iw)   = sqrt(mean(seg_e.^2));
            Th1_avg(ia,ig,iw) = mean(seg_th(:,1));
            Th2_avg(ia,ig,iw) = mean(seg_th(:,2));
        end
    end
end

%% -------- Plot: |yp| vs omega with one |ym| dashed --------
for ia = 1:nA
    A = A_list(ia);
    figure('Color','w','Name',sprintf('Amplitude yp, ym vs freq (A=%.2f)',A));
    ax = axes; hold(ax,'on'); grid(ax,'on'); box(ax,'on');
    title(ax, sprintf('|yp| (solid) and |ym| (black dashed) vs omega (A=%.2f)', A));

    % Theoretical model amplitude (same for all gammas)
    Ym_theory = A * bm ./ sqrt(am^2 + w_vec.^2);
    plot(ax, w_vec, Ym_theory, 'k--', 'LineWidth', 1.8, 'DisplayName','|ym| (model)');

    % yp curves per gamma
    for ig = 1:nG
        plot(ax, w_vec, squeeze(Yp_amp(ia,ig,:)), '-', 'LineWidth',1.7, ...
             'DisplayName', sprintf('gamma=%.2g: |yp|', gammas(ig)));
    end
    xlabel(ax,'omega (rad/s)'); ylabel(ax,'Amplitude'); legend(ax,'Location','best');
end

%% -------- Plot: RMS(e) and mean thetas vs freq --------
for ia = 1:nA
    A = A_list(ia);
    figure('Color','w','Name',sprintf('RMS & thetas vs freq (A=%.2f)',A));
    tl = tiledlayout(3,1,'TileSpacing','compact','Padding','compact');
    title(tl, sprintf('Diagnostics vs omega  (A=%.2f)',A));

    ax1 = nexttile; hold(ax1,'on'); grid(ax1,'on'); box(ax1,'on');
    for ig = 1:nG
        plot(ax1, w_vec, squeeze(E_rms(ia,ig,:)), 'LineWidth',1.5, ...
             'DisplayName', sprintf('gamma=%.2g: RMS(e)', gammas(ig)));
    end
    xlabel(ax1,'omega (rad/s)'); ylabel(ax1,'RMS(e)'); legend(ax1,'Location','best');

    ax2 = nexttile; hold(ax2,'on'); grid(ax2,'on'); box(ax2,'on');
    for ig = 1:nG
        plot(ax2, w_vec, squeeze(Th1_avg(ia,ig,:)), 'LineWidth',1.5, ...
             'DisplayName', sprintf('gamma=%.2g: mean(theta1)', gammas(ig)));
    end
    yline(ax2, th1_star, ':', 'theta1*');
    xlabel(ax2,'omega (rad/s)'); ylabel(ax2,'mean(theta1)'); legend(ax2,'Location','best');

    ax3 = nexttile; hold(ax3,'on'); grid(ax3,'on'); box(ax3,'on');
    for ig = 1:nG
        plot(ax3, w_vec, squeeze(Th2_avg(ia,ig,:)), 'LineWidth',1.5, ...
             'DisplayName', sprintf('gamma=%.2g: mean(theta2)', gammas(ig)));
    end
    yline(ax3, th2_star, ':', 'theta2*');
    xlabel(ax3,'omega (rad/s)'); ylabel(ax3,'mean(theta2)'); legend(ax3,'Location','best');
end

%% -------- Time overlays: yp for all gammas + one ym dashed --------
A_demo = A_list(1);  w_show = [0.5, 2.0];
for iw = 1:numel(w_show)
    w = w_show(iw);
    % one model trajectory (independent of gamma)
    [t_ref, x_ref] = simulate_case_v2(b,am,bm,gammas(end),A_demo,w,theta_sat,sigma_leak,alpha_norm,cycles_settle,cycles_meas);

    figure('Color','w','Name',sprintf('Time A=%.2f, w=%.2f',A_demo,w));
    tl = tiledlayout(2,1,'TileSpacing','compact','Padding','compact');
    title(tl, sprintf('A=%.2f, omega=%.2f:  yp (per gamma) & ym (black dashed) ;  theta1, theta2',A_demo,w));

    axY = nexttile; hold(axY,'on'); grid(axY,'on'); box(axY,'on');
    plot(axY, t_ref, x_ref(:,2), 'k--', 'LineWidth', 1.4, 'DisplayName','ym (model)');
    for ig = 1:nG
        [t,x] = simulate_case_v2(b,am,bm,gammas(ig),A_demo,w,theta_sat,sigma_leak,alpha_norm,cycles_settle,cycles_meas);
        plot(axY, t, x(:,1), 'LineWidth', 1.2, 'DisplayName', sprintf('gamma=%.2g: yp', gammas(ig)));
    end
    xlabel(axY,'t (s)'); ylabel(axY,'yp (—), ym (--)'); legend(axY,'Location','best');

    axT = nexttile; hold(axT,'on'); grid(axT,'on'); box(axT,'on');
    for ig = 1:nG
        [t,x] = simulate_case_v2(b,am,bm,gammas(ig),A_demo,w,theta_sat,sigma_leak,alpha_norm,cycles_settle,cycles_meas);
        plot(axT, t, x(:,5), 'LineWidth',1.2, 'DisplayName', sprintf('gamma=%.2g: theta1', gammas(ig)));
        plot(axT, t, x(:,6), '--', 'LineWidth',1.2, 'DisplayName', sprintf('gamma=%.2g: theta2', gammas(ig)));
    end
    yline(axT, th1_star, ':', 'theta1*'); yline(axT, th2_star, ':', 'theta2*');
    xlabel(axT,'t (s)'); ylabel(axT,'theta1 (—), theta2 (--)'); legend(axT,'Location','eastoutside');
end

%% ================= Helpers =================
function [t,x] = simulate_case_v2(b,am,bm,gamma,A,w,theta_sat,sigma_leak,alpha_norm,cycles_settle,cycles_meas)
    % States: [1] yp, [2] ym, [3] s1, [4] s2, [5] th1, [6] th2
    x0 = zeros(6,1);
    T_total = (cycles_settle + cycles_meas) * 2*pi / w;
    tspan   = [0, T_total];
    pars = struct('b',b,'am',am,'bm',bm,'gamma',gamma,'A',A,'w',w, ...
                  'theta_sat',theta_sat,'sigma_leak',sigma_leak,'alpha',alpha_norm);
    opts = odeset('RelTol',1e-6,'AbsTol',1e-8,'MaxStep',(2*pi/w)/80);
    try
        [t,x] = ode45(@(t,x) mrac_ode_v2(t,x,pars), tspan, x0, opts);
    catch
        [t,x] = ode15s(@(t,x) mrac_ode_v2(t,x,pars), tspan, x0, ...
                       odeset('RelTol',1e-6,'AbsTol',1e-8,'MaxStep',(2*pi/w)/120));
    end
end

function dx = mrac_ode_v2(t,x,p)
    yp=x(1); ym=x(2); s1=x(3); s2=x(4); th1=x(5); th2=x(6);
    r = p.A * sin(p.w*t);

    % Controller and closed-loop plant
    u = th1*r - th2*yp;      % 2-parameter controller
    yp_dot = p.b * u;

    % Reference model
    ym_dot = -p.am * ym + p.bm * r;

    % Error
    e = yp - ym;

    % Exact sensitivity dynamics for first-order case
    % (how yp would change if we nudge th1/th2 a bit)
    s1_dot = p.b * ( r   - th2*s1 );
    s2_dot = p.b * ( -yp - th2*s2 );

    % Normalized MIT (with optional sigma-leak)
    denom  = p.alpha + s1*s1 + s2*s2;   % clean normalization
    th1_dot = -(p.gamma/denom)*(e*s1) - p.sigma_leak*th1;
    th2_dot = -(p.gamma/denom)*(e*s2) - p.sigma_leak*th2;

    % Soft saturation (pull back if |theta| > theta_sat)
    if abs(th1) > p.theta_sat, th1_dot = th1_dot - 5*(th1 - sign(th1)*p.theta_sat); end
    if abs(th2) > p.theta_sat, th2_dot = th2_dot - 5*(th2 - sign(th2)*p.theta_sat); end

    dx = [yp_dot; ym_dot; s1_dot; s2_dot; th1_dot; th2_dot];
end

