%% verify_stability_no_radius_PRETTY.m
% Verifies stability of:
%   x1' =  x2 + c*x1*(x1^2+x2^2)
%   x2' = -x1 + c*x2*(x1^2+x2^2)
% using V(x)=0.5*(x1^2+x2^2). No polar coordinates are used.
% We visualize: phase portrait, V(t), and Vdot(t).
% Now with RADIAL in/out arrows (blue=in, red=out) so "approach vs depart"
% is visually unambiguous. Optionally keep tangent arrows too.

clear; clc; close all;

% --- make all text LaTeX so \dot{} etc. render correctly
set(0,'DefaultTextInterpreter','latex');
set(0,'DefaultAxesTickLabelInterpreter','latex');
set(0,'DefaultLegendInterpreter','latex');

% --- parameters you can play with
cs         = [0, -1, 0.5];       % three regimes: center, attractive, unstable
Tmax       = 20;                  % nominal time horizon
NormLimit  = 5;                   % stop if ||x|| exceeds this (prevents runaway plots)
opts       = odeset('RelTol',1e-10, 'AbsTol',1e-12);
ICs = [ 0.8   0.0;                % initial conditions (rows)
        0.6   0.4;
       -0.7   0.2;
        0.2  -0.9 ];

% --- arrow appearance (choose what to draw)
arrow_mode = 'radial';            % 'radial' | 'tangent' | 'both'
nArrows    = 10;                  % how many per trajectory (for both kinds)
fracLen    = 0.06;                % arrow length as fraction of axis range

% radial colors
col_out = [0.85 0.20 0.20];       % outward (rdot>0)  -> RED
col_in  = [0.20 0.35 0.90];       % inward  (rdot<0)  -> BLUE
col_zer = [0.50 0.50 0.50];       % near-zero radial  -> GRAY

% --- figure and layout
figure('Color','w','Position',[80 80 1300 720]);

for i = 1:numel(cs)
    c = cs(i);

    % ========= Left column: Phase portrait =========
    ax1 = subplot(3,3,3*(i-1)+1); hold(ax1,'on'); axis(ax1,'equal');
    grid(ax1,'on'); box(ax1,'on');
    title(ax1, sprintf('Phase portrait, $c = %g$', c));
    xlabel(ax1,'$x_1$'); ylabel(ax1,'$x_2$');

    % (A) draw a light vector field with quiver
    [Xg,Yg] = meshgrid(linspace(-2,2,21), linspace(-2,2,21));
    Ug = Yg + c.*Xg.*(Xg.^2 + Yg.^2);
    Vg = -Xg + c.*Yg.*(Xg.^2 + Yg.^2);
    quiver(ax1, Xg, Yg, Ug, Vg, ...
        'AutoScale','on','AutoScaleFactor',0.7, 'Color',[.85 .85 .85]);

    % storage for middle/right plots
    Vs = {}; Vdots = {}; Ts = {};

    % (B) simulate each initial condition
    for k = 1:size(ICs,1)
        x0 = ICs(k,:).';

        % event: stop when norm crosses NormLimit (useful for c>0)
        ev = @(t,x) stop_when_big_norm(t,x,NormLimit);
        opts_k = odeset(opts,'Events',ev);

        % RHS must return a 2x1 column for ode45 -> use sys_rhs_ode
        [T,X] = ode45(@(t,x) sys_rhs_ode(t,x,c), [0 Tmax], x0, opts_k);

        % Lyapunov signals along the trajectory (no polar coords)
        Vnum = 0.5*sum(X.^2,2);
        DX   = sys_rhs_mat(X,c);                        % Nx2 \dot x along traj
        Vdot = X(:,1).*DX(:,1) + X(:,2).*DX(:,2);       % x1*dx1 + x2*dx2

        % store for plotting
        Ts{end+1}    = T;
        Vs{end+1}    = Vnum;
        Vdots{end+1} = Vdot;

        % (C) plot trajectory curve
        htraj = plot(ax1, X(:,1), X(:,2), 'LineWidth',1.4, 'DisplayName','trajectory');
        plot(ax1, X(1,1), X(1,2), 'k.','MarkerSize',12); % start marker

        % (D) arrows
        switch lower(arrow_mode)
            case 'tangent'
                add_tangent_arrows_equal_arc(ax1, X, nArrows, fracLen, htraj.Color);
            case 'radial'
                add_radial_inout_arrows(ax1, X, DX, nArrows, fracLen, col_in, col_out, col_zer);
            case 'both'
                add_tangent_arrows_equal_arc(ax1, X, nArrows, fracLen*0.8, [0.2 0.2 0.2]*0.8);
                add_radial_inout_arrows(ax1, X, DX, nArrows, fracLen, col_in, col_out, col_zer);
        end
    end

    % Optional legend for the phase plot (explains radial arrows)
    switch lower(arrow_mode)
        case 'radial'
            h1 = plot(ax1, NaN,NaN,'-','Color',col_in,  'LineWidth',2,'DisplayName','radial inward');
            h2 = plot(ax1, NaN,NaN,'-','Color',col_out, 'LineWidth',2,'DisplayName','radial outward');
            legend(ax1, [h1 h2], {'radial inward','radial outward'}, 'Location','southwest');
        case 'both'
            h1 = plot(ax1, NaN,NaN,'-','Color',col_in,  'LineWidth',2,'DisplayName','radial inward');
            h2 = plot(ax1, NaN,NaN,'-','Color',col_out, 'LineWidth',2,'DisplayName','radial outward');
            h3 = plot(ax1, NaN,NaN,'-','Color',[0.2 0.2 0.2]*0.8,'LineWidth',2,'DisplayName','tangent');
            legend(ax1, [h1 h2 h3], {'radial inward','radial outward','tangent'}, 'Location','southwest');
        otherwise
            % no legend needed for tangent-only
    end

    % ========= Middle column: V(t) =========
    ax2 = subplot(3,3,3*(i-1)+2); hold(ax2,'on'); grid(ax2,'on'); box(ax2,'on');
    title(ax2, '$V(t)=\frac{1}{2}\,\|x(t)\|^2$');
    xlabel(ax2,'$t$'); ylabel(ax2,'$V(t)$');
    for k = 1:numel(Vs)
        plot(ax2, Ts{k}, Vs{k}, 'LineWidth',1.4);
    end
    % quick textual verdict from sign of Vdot
    text(ax2, 0.02,0.92, verdict_from_Vdot(Vdots), ...
        'Units','normalized','FontWeight','bold', ...
        'BackgroundColor','w','EdgeColor',[.8 .8 .8]);

    % ========= Right column: Vdot(t) =========
    ax3 = subplot(3,3,3*(i-1)+3); hold(ax3,'on'); grid(ax3,'on'); box(ax3,'on');
    title(ax3, '$\dot V(t)=x_1\,\dot x_1 + x_2\,\dot x_2$');
    xlabel(ax3,'$t$'); ylabel(ax3,'$\dot V(t)$');
    for k = 1:numel(Vdots)
        plot(ax3, Ts{k}, Vdots{k}, 'LineWidth',1.2);
    end
end

sgtitle('Verification (no polar coords): phase, $V(t)$, and $\dot V(t)$', 'FontWeight','bold');

%% ----------------- helpers -----------------

% ODE RHS for ode45: return 2x1 column vector
function dx = sys_rhs_ode(~,x,c)
    x1 = x(1); x2 = x(2);
    s  = x1^2 + x2^2;
    dx = [  x2 + c*x1*s;
           -x1 + c*x2*s ];
end

% Vectorized RHS on an Nx2 matrix X: return Nx2 (for post-processing)
function DX = sys_rhs_mat(X,c)
    x1 = X(:,1); x2 = X(:,2);
    s  = x1.^2 + x2.^2;
    DX = [ x2 + c.*x1.*s,  -x1 + c.*x2.*s ];
end

% Event: stop integration once ||x|| reaches 'limit' (useful for c>0 blow-up)
function [value, isterminal, direction] = stop_when_big_norm(~,x,limit)
    value      = limit - norm(x);  % cross zero when ||x|| = limit
    isterminal = 1;                % stop the integration
    direction  = -1;               % detect decreasing crossing (value ↓ through 0)
end

% --- Tangent arrows (equal-arc spacing), show direction along the curve.
% nArrows: how many arrows; fracLen: arrow length as fraction of axis range.
function add_tangent_arrows_equal_arc(ax, X, nArrows, fracLen, color)
    if size(X,1) < 2 || nArrows <= 0, return; end
    dX  = diff(X,1,1);                     % (N-1) x 2
    seg = sqrt(sum(dX.^2,2));              % segment lengths
    S   = [0; cumsum(seg)];
    L   = S(end);
    if L <= 0, return; end
    sTargets = linspace(0.1*L, 0.9*L, nArrows);

    xl = xlim(ax); yl = ylim(ax);
    baseLen = fracLen * max(diff(xl), diff(yl));

    hold_state = ishold(ax); hold(ax,'on');
    for sT = sTargets
        j = find(S <= sT, 1, 'last');
        if isempty(j) || j >= numel(S), continue; end
        v = dX(j,:); nv = norm(v);
        if nv < eps, continue; end
        p = X(j,:);
        dir = (v / nv) * baseLen;
        quiver(ax, p(1), p(2), dir(1), dir(2), 0, ...
               'MaxHeadSize', 1.3, 'LineWidth', 1.0, ...
               'Color', color, 'Clipping','off');
    end
    if ~hold_state, hold(ax,'off'); end
end

% --- Radial in/out arrows (blue=in, red=out, gray≈zero).
% nArrows: how many; fracLen: arrow length as fraction of axis range.
function add_radial_inout_arrows(ax, X, DX, nArrows, fracLen, col_in, col_out, col_zer)
    if size(X,1) < 2 || nArrows <= 0, return; end

    % pick evenly spaced indices along the polyline
    idx = round(linspace(2, size(X,1), nArrows));  % avoid the very first point

    % length scale from axis range
    xl = xlim(ax); yl = ylim(ax);
    baseLen = fracLen * max(diff(xl), diff(yl));

    % small threshold to classify near-zero radial component
    tol = 1e-12;

    for j = idx
        p = X(j,:);  r = norm(p);
        if r < 1e-14, continue; end
        er   = p / r;                 % unit radial (outward)
        rdot = dot(DX(j,:), er);      % radial speed

        if abs(rdot) < tol
            % optional: show a small gray tick; comment out to skip
            dir = 0.5 * er * baseLen; col = col_zer;
        elseif rdot > 0
            dir = 1.0 * er * baseLen; col = col_out;  % outward
        else
            dir = -1.0 * er * baseLen; col = col_in;  % inward
        end

        quiver(ax, p(1), p(2), dir(1), dir(2), 0, ...
               'MaxHeadSize', 1.6, 'LineWidth', 1.2, ...
               'Color', col, 'Clipping','off');
    end
end

% Summarize the observed sign of Vdot across simulated trajectories
function txt = verdict_from_Vdot(Vdots)
    tol = 1e-8; hasPos = false; hasNeg = false;
    for k=1:numel(Vdots)
        v = Vdots{k};
        hasPos = hasPos || any(v >  tol);
        hasNeg = hasNeg || any(v < -tol);
    end
    if hasPos && ~hasNeg
        txt = 'Observed: $\dot V>0$ (unstable)';
    elseif hasNeg && ~hasPos
        txt = 'Observed: $\dot V<0$ (attractive)';
    else
        txt = 'Observed: $\dot V\approx 0$ (center)';
    end
end

