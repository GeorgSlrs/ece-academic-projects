%% ============================================================
%  Exercise 2 – Simulation & Plots (fixed streamslice)
%  System:
%    x1_dot = -x1
%    x2_dot = (x1*x2 - 1)*x2^3 + (x1*x2 - 1 + x1^2)*x2
%  Shows:
%   (a) Unique equilibrium (0,0)
%   (b) Local AS near 0 (portrait)
%   (c) Γ = {x : x1*x2 >= 2} positively invariant (V,h plots)
%   (d) Not globally asymptotically stable
%  ------------------------------------------------------------
clear; clc; close all

% ---------- Global style ----------
set(groot,'defaultAxesFontSize',12);
set(groot,'defaultLineLineWidth',1.6);

% ---------- Dynamics ----------
f = @(t,x) [ ...
    -x(1); ...
    (x(1)*x(2)-1)*x(2)^3 + (x(1)*x(2)-1 + x(1)^2)*x(2) ...
];

% Helpers
h_fun = @(x1,x2) x1.*x2;          % h = x1*x2
V_fun = @(x1,x2) 2 - x1.*x2;      % V = 2 - h
Vdot_grid = @(x1,x2) -(x1.*x2) .* ( ((x1.*x2)-1).*(x2.^2 + 1) + x1.^2 - 1 );

% ---------- (a) Unique equilibrium ----------
x_star = [0;0];  %#ok<NASGU>

% ---------- (b) Linearization at 0 ----------
A0 = [-1 0; 0 -1];       % eigenvalues -1,-1 (local AS)
eigsA0 = eig(A0);        %#ok<NASGU>

% ---------- Seeds & ODE options ----------
x0_near   = [0.3; 0.3];  % near origin (should go to 0)
x0_gamma  = [2.0; 1.0];  % on Γ boundary (h=2) – grows fast
T_near    = [0 4.0];
T_gamma   = [0 0.6];     % short horizon for Γ (fast growth)
optsBlow  = odeset('RelTol',1e-9,'AbsTol',1e-11, ...
                   'Events', @(t,x) blowEvent(t,x,100));

% Simulate representative runs
[tN, xN] = ode45(f, T_near,  x0_near,  optsBlow);
[tG, xG] = ode45(f, T_gamma, x0_gamma, optsBlow);

% ---------- Γ-batch simulations (for invariance plots) ----------
X0G = [ 2.0  1.6  -2.2  -1.4;    % x1(0)
        1.0  1.5  -1.0  -1.5 ];  % x2(0)   (all satisfy x1*x2 >= 2)
TspanG   = [0 1.0];
RcapG    = 50;
optsGam  = odeset('RelTol',1e-9,'AbsTol',1e-11, ...
                  'Events', @(t,x) gammaAndBlowEvent(t,x,RcapG));
Ts = cell(1,size(X0G,2));  Xs = Ts;  Iexit = Ts;
for k = 1:size(X0G,2)
    [Ts{k}, Xs{k}, te, ~, ie] = ode45(f, TspanG, X0G(:,k), optsGam); %#ok<ASGLU>
    Iexit{k} = ie;
end

% ---------- Diagnostics for Γ (optional print) ----------
[xg,yg]  = meshgrid(linspace(-3,3,121),linspace(-3,3,121));
maskG    = (xg.*yg >= 2);
Vd_vals  = Vdot_grid(xg,yg);
fprintf('Max Vdot over sampled Γ: %.3e  (expected ≤ 0)\n', max(Vd_vals(maskG)));

%% ===================== FIGURE 1 (Phase portrait) ======================
figure('Color','w'); ax = axes; hold(ax,'on'); box(ax,'on'); axis(ax,'equal');
title(ax,'(a)(b) Phase portrait (true magnitude) + Γ + nullclines');
xlabel(ax,'x_1'); ylabel(ax,'x_2');

% Vector field (true magnitudes)
dx1 = -xg;
dx2 = (xg.*yg - 1).*yg.^3 + (xg.*yg - 1 + xg.^2).*yg;
spd = hypot(dx1,dx2);
spd_clip = min(spd,50);
imagesc(ax, xg(1,:), yg(:,1), log10(1+spd_clip)); set(ax,'YDir','normal');
colormap(ax, parula); cb = colorbar(ax); cb.Label.String='log_{10}(1+|f|)';
uistack(ax.Children(1),'bottom');

% ---- Streamlines (2-D syntax with density; no start arrays)
% This avoids the 3-D "volume data" error.
hstr = streamslice(xg, yg, dx1, dx2, 1.5);
set(hstr,'Color',[0.15 0.15 0.15]);  % darker gray
set(hstr, 'Parent', ax);             % ensure lines are in this axes

% ---- Nullclines
plot(ax, [0 0], [-3 3], 'k-', 'LineWidth',1.2, 'DisplayName','\dot x_1=0');
contour(ax, xg, yg, dx2, [0 0], 'm-', 'LineWidth',1.2, 'DisplayName','\dot x_2=0');

% ---- Γ boundary: x1*x2=2
xx1 = linspace(0.25,3,600);  plot(ax, xx1, 2./xx1, 'r--', 'LineWidth',1.4, 'DisplayName','\Gamma: x_1x_2=2');
xx2 = linspace(-3,-0.25,600); plot(ax, xx2, 2./xx2, 'r--', 'LineWidth',1.4,'HandleVisibility','off');

% ---- Overlay representative trajectories + arrows along them
plot(ax, xN(:,1), xN(:,2), 'b-', 'LineWidth',1.8, 'DisplayName','near origin');
plot(ax, xG(:,1), xG(:,2), 'c-', 'LineWidth',1.8, 'DisplayName','on \Gamma');
add_arrows_along(ax, xN(:,1), xN(:,2), 10, 0.8, 'b');
add_arrows_along(ax, xG(:,1), xG(:,2),  7, 0.8, 'c');

% ---- Mark equilibrium
plot(ax, 0, 0, 'ko', 'MarkerFaceColor','k', 'DisplayName','equilibrium');

xlim(ax,[-3 3]); ylim(ax,[-3 3]);
leg = legend(ax,'Location','best'); set(leg,'Box','off');

%% ===================== FIGURE 2 (Invariance & time) ====================
figure('Color','w'); tl = tiledlayout(2,2,'TileSpacing','compact','Padding','compact');

% (c1) V(t)=2-h(t) for Γ starts  (nonincreasing)
ax1 = nexttile; hold(ax1,'on'); grid(ax1,'on');
for k = 1:numel(Ts)
    tt = Ts{k}; xx = Xs{k};
    plot(ax1, tt, V_fun(xx(:,1),xx(:,2)), 'LineWidth',1.4);
end
yline(ax1, 0,'r--','LineWidth',1.0,'DisplayName','V=0 (h=2)');
xlabel(ax1,'t'); ylabel(ax1,'V(t)=2-x_1x_2'); title(ax1,'(c) V(t) on Γ (nonincreasing)');

% (c2) h(t)=x1x2 for Γ starts  (stays ≥ 2)
ax2 = nexttile; hold(ax2,'on'); grid(ax2,'on');
for k = 1:numel(Ts)
    tt = Ts{k}; xx = Xs{k};
    plot(ax2, tt, h_fun(xx(:,1),xx(:,2)), 'LineWidth',1.4);
end
yline(ax2, 2,'r--','LineWidth',1.0,'DisplayName','h=2');
xlabel(ax2,'t'); ylabel(ax2,'h(t)=x_1x_2'); title(ax2,'(c) h(t) on Γ (stays ≥ 2)');

% Simple time-plots x1(t), x2(t) (near vs Γ)
ax3 = nexttile; hold(ax3,'on'); grid(ax3,'on');
plot(ax3, tN, xN(:,1), 'b-', 'LineWidth',1.6, 'DisplayName','x_1 (near)');
plot(ax3, tN, xN(:,2), 'r-', 'LineWidth',1.6, 'DisplayName','x_2 (near)');
xlabel(ax3,'t'); ylabel(ax3,'state'); title(ax3,'(b) Near-origin: x_1(t), x_2(t)');
leg3 = legend(ax3,'Location','best'); set(leg3,'Box','off');

ax4 = nexttile; hold(ax4,'on'); grid(ax4,'on');
plot(ax4, tG, xG(:,1), 'b-', 'LineWidth',1.6, 'DisplayName','x_1 (\Gamma)');
plot(ax4, tG, xG(:,2), 'r-', 'LineWidth',1.6, 'DisplayName','x_2 (\Gamma)');
xlabel(ax4,'t'); ylabel(ax4,'state'); title(ax4,'(d) On \Gamma: x_1(t), x_2(t)');
leg4 = legend(ax4,'Location','best'); set(leg4,'Box','off');

% (d) Not GAS is evident: near-origin run decays; Γ run grows.

%% ========================= Event helpers ==============================
function [value,isterminal,direction] = gammaAndBlowEvent(~,x,Rmax)
    % 1) Leave Γ?   value(1) = x1*x2 - 2; trigger only if crossing downward
    % 2) Too large? value(2) = Rmax - ||x||_inf; trigger if exceeding cap
    value      = [x(1)*x(2) - 2;  Rmax - norm(x,Inf)];
    isterminal = [1; 1];
    direction  = [-1; -1];
end

function [value,isterminal,direction] = blowEvent(~,x,Rmax)
    value      = Rmax - norm(x,Inf);
    isterminal = 1;
    direction  = -1;
end

%% --------------- Arrow helper for trajectories ------------------------
function add_arrows_along(ax, x, y, n_arrows, scale, colorSpec)
    if numel(x) < 2, return; end
    idx = round(linspace(1, numel(x)-1, n_arrows));
    for k = idx
        dx = x(k+1) - x(k); dy = y(k+1) - y(k);
        if ~isfinite(dx) || ~isfinite(dy), continue; end
        quiver(ax, x(k), y(k), scale*dx, scale*dy, 0, ...
               'MaxHeadSize', 1.2, 'Color', colorSpec, 'LineWidth',1.0);
    end
end

