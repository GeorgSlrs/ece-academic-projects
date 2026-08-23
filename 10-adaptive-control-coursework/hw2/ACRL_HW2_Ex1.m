%% MRAC for P(s) = 1/(s(s+a)) using ONLY the normalized MIT rule (slide form)
% Plant:       y¨ + a y˙ = u
% Ref. model:  y_m¨ + 2ζω0 y_m˙ + ω0^2 y_m = ω0^2 r
% Controller:  u = θ1*r - θ2*y - θ3*y˙          (PD + feedforward, linear in θ)
%
% Normalized MIT update (per component i = 1..3):
%   θ̇_i = -γ * e * ψ_i / (α + ψᵀψ)
% with e = y - y_m.
%
% WHAT ARE σ AND ψ_i? NOTES TO SELF
% -------------------
% • σ = [σ1, σ2, σ3]ᵀ are the *driving signals* that tell us how each parameter θ_i
%   enters the control input u. Because u = θ1*r - θ2*y - θ3*y˙,
%   the partial derivatives of u w.r.t. each parameter are:
%       ∂u/∂θ1 =  r     →  σ1 =  r
%       ∂u/∂θ2 = -y     →  σ2 = -y
%       ∂u/∂θ3 = -y˙    →  σ3 = -y˙
%   Intuition: If we “nudge” θ1 a little, u changes like r; if we “nudge” θ2, u
%   changes like -y; if we “nudge” θ3, u changes like -y˙.
%
% • ψ_i are *virtual states* that approximate “how much the plant output y would
%   move if we nudged θ_i a little”. Rather than differentiating the plant
%   equations analytically (messy and non-causal with s-operators), we generate
%   ψ_i by passing σ_i through a *reference-model-shaped* 2nd-order filter:
%
%     ψ_i¨ + 2ζω0 ψ_i˙ + ω0^2 ψ_i = σ_i
%
%   This filter has the same denominator as the reference model. It “tilts” σ_i
%   the same way the model shapes signals, giving a realizable, bounded and
%   well-scaled approximation of ∂y/∂θ_i near the operating condition.
%
% • The regressor vector used in the gradient step is ψ = [ψ1, ψ2, ψ3]ᵀ.
%   The normalization divides by α + ||ψ||² so that when signals are large,
%   the adaptation step is automatically damped; when signals are small,
%   the α term prevents division by ~0.

clear; clc; close all;

%% -------------------------- Display / fonts --------------------------
fsT = 15; fsL = 13; fsTick = 11;
set(groot,'defaultAxesFontSize',fsTick);

%% -------------------------- Plant & model ----------------------------
a    = 1.0;           % unknown to the designer (simulator uses it)
zeta = 0.707;         % model damping
w0   = 2.0;           % model natural frequency (rad/s)

% Ideal matching parameters (if y matched y_m exactly):
%   θ1* = ω0²,  θ2* = ω0²,  θ3* = 2ζω0 - a
th_star = [ w0^2,    w0^2,  2*zeta*w0 - a ];   % [4, 4, 1.828...]

%% -------------------------- Adaptation settings ----------------------
gammas = [0.2, 0.4, 0.8];   % learning rates γ
alpha  = 2.0;               % α > 0 for normalization denominator

%% -------------------------- Reference definition ---------------------
A      = 1.0;                             % sine amplitude
wr_vec = linspace(0.3, 2.0, 12);          % sweep input frequency ω_r (rad/s)

% For each (γ, ω_r) run long enough for transients to die
cycles_settle = 8;                        % discarded cycles
cycles_meas   = 2;                        % used for metrics

%% -------------------------- Buffers for sweep ------------------------
nG = numel(gammas); nW = numel(wr_vec);
Yp_amp  = nan(nG, nW);                    % measured |y_p| amplitude
Ym_amp  = nan(1,  nW);                    % analytical |y_m| amplitude
Erms    = nan(nG, nW);                    % RMS(e) in steady state
Emse    = nan(nG, nW);                    % MSE(e) in steady state
Th_mean = nan(nG, nW, 3);                 % mean θ_i in steady state

%% ======================== Frequency sweep ============================
for iw = 1:nW
    wr = wr_vec(iw);

    % Closed-form |y_m| for r(t)=A sin(ω_r t)
    Ym_amp(1,iw) = A*(w0^2) / sqrt( (w0^2 - wr^2)^2 + (2*zeta*w0*wr)^2 );

    for ig = 1:nG
        gamma = gammas(ig);

        [t, y, ym, e, TH] = simulate_normMIT_sigma(a,zeta,w0,gamma,alpha, ...
                                                   A, wr, cycles_settle, cycles_meas);
        if numel(t) < 10, continue; end

        % ---- metrics over the final 'cycles_meas' periods ----
        Tper = 2*pi/wr;  t1 = t(end) - cycles_meas*Tper;
        idx  = t >= max(t(1), t1);
        if nnz(idx) < 5, continue; end

        seg_y  = y(idx);  seg_e = e(idx);  seg_th = TH(idx,:);

        Yp_amp(ig,iw)    = 0.5*(max(seg_y) - min(seg_y));   % amplitude
        Erms(ig,iw)      = sqrt(mean(seg_e.^2));            % RMS(e)
        Emse(ig,iw)      = mean(seg_e.^2);                  % MSE(e)
        Th_mean(ig,iw,:) = mean(seg_th, 1);                 % mean θ_i
    end
end

%% -------------------------- Plot: |y_p| vs ω_r -----------------------
figure('Color','w','Name','Amplitude vs input frequency');
ax = axes; hold(ax,'on'); grid(ax,'on'); box(ax,'on');
title(ax,'|y_p| (solid, per \gamma) and |y_m| (black dashed) vs input frequency \omega_r', ...
      'FontSize',fsT);
plot(ax, wr_vec, Ym_amp, 'k--', 'LineWidth', 1.8, 'DisplayName','|y_m| (model)');
for ig = 1:nG
    plot(ax, wr_vec, Yp_amp(ig,:), '-', 'LineWidth', 1.8, ...
        'DisplayName', sprintf('\\gamma=%.2g: |y_p|', gammas(ig)));
end
xlabel(ax,'\omega_r (rad/s)','FontSize',fsL); ylabel(ax,'Amplitude','FontSize',fsL);
legend(ax,'Location','best');

%% -------------------------- Plot: RMS(e) & MSE(e) --------------------
figure('Color','w','Name','Error vs input frequency');
ax1 = subplot(2,1,1); hold(ax1,'on'); grid(ax1,'on'); box(ax1,'on');
title(ax1,'RMS(e) vs \omega_r','FontSize',fsT);
for ig = 1:nG
    plot(ax1, wr_vec, Erms(ig,:), 'LineWidth', 1.8, ...
        'DisplayName', sprintf('\\gamma=%.2g', gammas(ig)));
end
xlabel(ax1,'\omega_r (rad/s)','FontSize',fsL); ylabel(ax1,'RMS(e)','FontSize',fsL);
legend(ax1,'Location','best');

ax2 = subplot(2,1,2); hold(ax2,'on'); grid(ax2,'on'); box(ax2,'on');
title(ax2,'MSE(e) vs \omega_r','FontSize',fsT);
for ig = 1:nG
    plot(ax2, wr_vec, Emse(ig,:), 'LineWidth', 1.8, ...
        'DisplayName', sprintf('\\gamma=%.2g', gammas(ig)));
end
xlabel(ax2,'\omega_r (rad/s)','FontSize',fsL); ylabel(ax2,'MSE(e)','FontSize',fsL);
legend(ax2,'Location','best');

%% --------------- Plot: steady-state mean θ_i vs ω_r ------------------
figure('Color','w','Name','Mean parameter values vs frequency');
tl = tiledlayout(3,1,'TileSpacing','compact','Padding','compact');
title(tl,'Mean \theta_i vs \omega_r (steady-state averages)','FontSize',fsT);

ylbl     = {'\overline{\theta}_1','\overline{\theta}_2','\overline{\theta}_3'};
idealLbl = {'\theta_1^*','\theta_2^*','\theta_3^*'};
idealCol = {[0.8500 0.3250 0.0980], [0.4660 0.6740 0.1880], [0.0000 0.4470 0.7410]};

for i = 1:3
    axT = nexttile; hold(axT,'on'); grid(axT,'on'); box(axT,'on');
    for ig = 1:nG
        plot(axT, wr_vec, squeeze(Th_mean(ig,:,i)), 'LineWidth', 1.6, ...
            'DisplayName', sprintf('\\gamma=%.2g', gammas(ig)));
    end
    plot(axT, wr_vec([1 end]), [th_star(i) th_star(i)], '--', ...
        'Color', idealCol{i}, 'LineWidth', 1.4, 'DisplayName', idealLbl{i});
    xlabel(axT,'\omega_r (rad/s)','FontSize',fsL);
    ylabel(axT, ylbl{i},         'FontSize',fsL);
    legend(axT,'Location','best');
end

%% --------- Time overlays at two representative frequencies -----------
wr_show = [0.6, 1.6];
for wr = wr_show
    figure('Color','w','Name',sprintf('Time overlays (wr=%.2f)',wr));
    tl = tiledlayout(2,1,'TileSpacing','compact','Padding','compact');
    title(tl, sprintf('y_p per \\gamma (solid) vs y_m (black dashed);  \\theta_i(t);  \\omega_r=%.2f',wr), ...
          'FontSize', fsT);

    [t_ref, ~, ym_ref] = simulate_normMIT_sigma(a,zeta,w0,gammas(1),alpha, A,wr, cycles_settle,cycles_meas);

    % outputs
    axY = nexttile; hold(axY,'on'); grid(axY,'on'); box(axY,'on');
    plot(axY, t_ref, ym_ref, 'k--', 'LineWidth', 1.3, 'DisplayName','y_m');
    for ig = 1:nG
        [t, y] = simulate_normMIT_sigma(a,zeta,w0,gammas(ig),alpha, A,wr, cycles_settle,cycles_meas);
        plot(axY, t, y, 'LineWidth', 1.3, 'DisplayName', sprintf('\\gamma=%.2g: y_p', gammas(ig)));
    end
    xlabel(axY,'t (s)','FontSize',fsL); ylabel(axY,'output','FontSize',fsL);
    legend(axY,'Location','best');

    % parameters
    axTh = nexttile; hold(axTh,'on'); grid(axTh,'on'); box(axTh,'on');
    for ig = 1:nG
        [t,~,~,~,TH] = simulate_normMIT_sigma(a,zeta,w0,gammas(ig),alpha, A,wr, cycles_settle,cycles_meas);
        plot(axTh, t, TH(:,1), 'LineWidth',1.2, 'DisplayName', sprintf('\\gamma=%.2g: \\theta_1', gammas(ig)));
        plot(axTh, t, TH(:,2), 'LineWidth',1.2, 'DisplayName', sprintf('\\gamma=%.2g: \\theta_2', gammas(ig)));
        plot(axTh, t, TH(:,3), 'LineWidth',1.2, 'DisplayName', sprintf('\\gamma=%.2g: \\theta_3', gammas(ig)));
    end
    plot(axTh, [t(1) t(end)], [th_star(1) th_star(1)], '--', 'Color', idealCol{1}, 'LineWidth',1.3, 'DisplayName', idealLbl{1});
    plot(axTh, [t(1) t(end)], [th_star(2) th_star(2)], '--', 'Color', idealCol{2}, 'LineWidth',1.3, 'DisplayName', idealLbl{2});
    plot(axTh, [t(1) t(end)], [th_star(3) th_star(3)], '--', 'Color', idealCol{3}, 'LineWidth',1.3, 'DisplayName', idealLbl{3});
    xlabel(axTh,'t (s)','FontSize',fsL); ylabel(axTh,'parameters','FontSize',fsL);
    legend(axTh,'Location','eastoutside');
end

%% ====================== Local functions ==============================
function [t, y, ym, e, TH] = simulate_normMIT_sigma(a,zeta,w0,gamma,alpha, A,wr, cycles_settle,cycles_meas)
    % Build horizon and step from ω_r so that we integrate several periods
    Tper = 2*pi/wr;
    Ttot = (cycles_settle + cycles_meas)*Tper;
    dt   = min(2.5e-4, Tper/1600);   % small step for accuracy (RK4)

    N = round(Ttot/dt) + 1;
    t = linspace(0, Ttot, N).';

    % State vector x:
    % 1:y, 2:y˙, 3:y_m, 4:y_m˙,
    % 5:ψ1, 6:ψ2, 7:ψ3, 8:ψ1˙, 9:ψ2˙, 10:ψ3˙,
    % 11:θ1, 12:θ2, 13:θ3
    x = zeros(13,1);

    y  = zeros(N,1);  ym = zeros(N,1);  e = zeros(N,1);  TH = zeros(N,3);

    % Time stepping with classic RK4
    for k = 1:N-1
        y(k)     = x(1);
        ym(k)    = x(3);
        e(k)     = x(1) - x(3);
        TH(k,:)  = x(11:13).';

        x = rk4(@(tt,xx) rhs_normMIT_sigma(tt,xx,a,zeta,w0,gamma,alpha,A,wr), t(k), x, dt);
    end
    % store final point
    y(N)  = x(1); ym(N) = x(3); e(N) = x(1)-x(3); TH(N,:) = x(11:13).';
end

function dx = rhs_normMIT_sigma(t,s,a,zeta,w0,gamma,alpha,A,wr)
    % Unpack states
    y = s(1);    yd = s(2);
    ym = s(3);  ymd = s(4);
    psi1  = s(5);  psi2  = s(6);  psi3  = s(7);
    psid1 = s(8);  psid2 = s(9);  psid3 = s(10);
    th1 = s(11);   th2 = s(12);   th3 = s(13);

    % Reference: single sine r(t) = A sin(ω_r t)
    r = A*sin(wr*t);

    % Control law: PD + reference feedforward (linear in θ)
    u = th1*r - th2*y - th3*yd;

    % Plant & model dynamics
    ydd  = -a*yd + u;
    ymdd = -2*zeta*w0*ymd - (w0^2)*ym + (w0^2)*r;

    % Tracking error
    e = y - ym;

    % ---------- BUILD σ AND ψ (INTUITIVE EXPLANATION HERE) ----------
    % σ tells us "how u would change if θ_i changed a little":
    %   σ1 =  r   (because ∂u/∂θ1 =  r)
    %   σ2 = -y   (because ∂u/∂θ2 = -y)
    %   σ3 = -yd  (because ∂u/∂θ3 = -y˙)
    %
    % ψ_i tells us "how y would respond to that u-change", but through a
    % model-shaped, bounded filter so it is causal and well-scaled.
    % We therefore *filter* each σ_i by the ref-model denominator:
    %   ψ_i¨ + 2ζω0 ψ_i˙ + ω0^2 ψ_i = σ_i
    % (Implement as 2nd-order ODEs.)
    psi1dd = -2*zeta*w0*psid1 - (w0^2)*psi1 + r;   % σ1 =  r
    psi2dd = -2*zeta*w0*psid2 - (w0^2)*psi2 - y;   % σ2 = -y
    psi3dd = -2*zeta*w0*psid3 - (w0^2)*psi3 - yd;  % σ3 = -y˙

    % Normalized MIT rule (componentwise):
    %   θ̇ = -γ * e * ψ / (α + ψᵀψ)
    denom = alpha + (psi1*psi1 + psi2*psi2 + psi3*psi3);
    th1d  = -gamma * e * (psi1 / denom);
    th2d  = -gamma * e * (psi2 / denom);
    th3d  = -gamma * e * (psi3 / denom);

    % Assemble state derivative
    dx = [ yd; ydd; ymd; ymdd; ...
           psid1; psid2; psid3; ...
           psi1dd; psi2dd; psi3dd; ...
           th1d; th2d; th3d ];
end

function xnew = rk4(f,t,x,h)
    % Classic fourth-order Runge–Kutta single step
    k1 = f(t, x);
    k2 = f(t + 0.5*h, x + 0.5*h*k1);
    k3 = f(t + 0.5*h, x + 0.5*h*k2);
    k4 = f(t + h,     x + h*k3);
    xnew = x + (h/6)*(k1 + 2*k2 + 2*k3 + k4);
end

