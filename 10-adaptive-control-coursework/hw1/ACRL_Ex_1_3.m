%% HW3_AB_full.m  —  Parts (a)–(d) for Systems (A) and (B)
% (a) equilibria
% (b) linearization + stability type
% (c) ROA via quadratic Lyapunov (largest ellipse with dV<0 on boundary)
% (d) phase portraits, nullclines, equilibria, ROA; plus basins for (A)
%
% Self-contained. Uses 'lyap' if available; otherwise solves 2x2 Lyapunov.

clear; clc; close all;

%% ================== USER SETTINGS ==================
N_STRIPS  = 6;                        % how many strips for System (B)
EPS       = 1e-9;                     % safety margin from tan poles
SEEDS     = linspace(-0.85,0.85,7);   % off-diagonal seeds per strip

winA = [-3 3 -9 9];                   % plot window for (A)
winB = [-1.4 1.4 -1.4 1.4];           % plot window for (B) (stay inside ±1 poles)
NANGLES = 240;                        % samples on ellipse boundary
%% ====================================================

%% ------------------ Systems & Jacobians --------------
% System (A)
fA  = @(x)[ x(1) - x(1)^3 + x(2) ;
            3*x(1) - x(2) ];
JA  = @(x)[ 1 - 3*x(1)^2 , 1 ; 3 , -1 ];

% System (B)
fB  = @(x)[ -0.5*tan(pi*x(1)/2) + x(2) ;
             x(1) - 0.5*tan(pi*x(2)/2) ];
JB  = @(x)[ -(pi/4)*sec(pi*x(1)/2).^2 , 1 ;
             1 , -(pi/4)*sec(pi*x(2)/2).^2 ];
%% ====================================================

%% (a) Equilibria
eqA = [ 0 0 ; 2 6 ; -2 -6 ];                       % exact for (A)
[diagB_pairs, offB] = equilibria_B(N_STRIPS, EPS, SEEDS);   % (r,r) and (a,b)

fprintf('=== (a) Equilibria ===\n');
fprintf('System (A):\n'); disp(eqA);
fprintf('System (B) — diagonal (x1=x2=r):\n'); disp(diagB_pairs);
fprintf('System (B) — off-diagonal (a,b):\n'); disp(offB);

%% (b) Linearization & stability classification
% SAFE concatenation (this fixes your error)
if isempty(offB), offB_safe = zeros(0,2); else, offB_safe = offB; end
eqB_all = [diagB_pairs; offB_safe];

infoA = classify_all(eqA,    JA);
infoB = classify_all(eqB_all, JB);

fprintf('\n=== (b) Linearization & type ===\n');
fprintf('System (A):\n'); print_table(infoA);
fprintf('System (B):\n'); print_table(infoB);

%% (c) ROA via quadratic Lyapunov V = y^T P y
Q = eye(2);

% (A): only stable equilibria (the two nodes)
idxA_stable = find([infoA.is_stable]);
roaA = [];
for k = idxA_stable
    xbar = infoA(k).xbar(:);
    A    = JA(xbar);
    P    = lyap2x2(A, Q);
    rho  = largest_rho(fA, xbar, P, NANGLES);
    roaA = [roaA ; xbar.' rho]; %#ok<AGROW>
end

% (B): for all stable eqs we found
idxB_stable = find([infoB.is_stable]);
roaB = [];
for k = idxB_stable
    xbar = infoB(k).xbar(:);
    A    = JB(xbar);
    P    = lyap2x2(A, Q);
    rho  = largest_rho(fB, xbar, P, NANGLES);
    roaB = [roaB ; xbar.' rho]; %#ok<AGROW>
end

fprintf('\n=== (c) ROA ellipse levels (rho) ===\n');
fprintf('System (A) [x1* x2*  rho]\n'); disp(roaA);
fprintf('System (B) [x1* x2*  rho]\n'); disp(roaB);

%% (d) Phase portraits + nullclines + equilibria + ROA + basins(A)
% ---------- System (A) ----------
figure('Name','System (A)'); hold on; axis equal; box on; axis(winA);
title('(A) phase portrait, nullclines, equilibria, ROA');

[xg,yg] = meshgrid(linspace(winA(1),winA(2),31),linspace(winA(3),winA(4),31));
U = xg - xg.^3 + yg; V = 3*xg - yg;
quiver(xg,yg,U,V,'AutoScale','on','Color',[0.7 0.7 0.7]);

x1 = linspace(winA(1),winA(2),1000);
plot(x1, x1.^3 - x1,'k--','LineWidth',1);   % \dot x1=0
plot(x1, 3*x1,'r--','LineWidth',1);         % \dot x2=0

plot_eqs(eqA, infoA);

for k = 1:size(roaA,1)
    xbar = roaA(k,1:2).'; rho = roaA(k,3);
    P = lyap2x2(JA(xbar), Q);
    draw_ellipse(P, rho, xbar, 'g', 2);
end

draw_basins_A(fA, eqA, winA);
legend({'field','\dot x_1=0','\dot x_2=0','eq: saddle','eq: stable','eq: unstable','ROA'},...
       'Location','northwest');

% ---------- System (B) ----------
figure('Name','System (B)'); hold on; axis equal; box on; axis(winB);
title('(B) phase portrait near origin + ROA ellipses');

[xg,yg] = meshgrid(linspace(winB(1),winB(2),35),linspace(winB(3),winB(4),35));
U = -0.5*tan(pi*xg/2) + yg; V = xg - 0.5*tan(pi*yg/2);
quiver(xg,yg,U,V,'AutoScale','on','Color',[0.7 0.7 0.7]);

xx = linspace(winB(1),winB(2),1200);
plot(xx, 0.5*tan(pi*xx/2),'k--','LineWidth',1); % \dot x1=0
plot(0.5*tan(pi*xx/2), xx,'r--','LineWidth',1); % \dot x2=0

plot_eqs(eqB_all, infoB);

% ROA (green) for stable ones inside window
for k = 1:size(eqB_all,1)
    xbar = eqB_all(k,:).';
    if all(xbar > [winB(1);winB(3)]) && all(xbar < [winB(2);winB(4)])
        A = JB(xbar);
        if all(real(eig(A))<0)
            P = lyap2x2(A, Q);
            rho = largest_rho(fB, xbar, P, NANGLES);
            draw_ellipse(P, rho, xbar, 'g', 2);
        end
    end
end
legend({'field','\dot x_1=0','\dot x_2=0','eq: saddle','eq: stable','eq: unstable','ROA'},...
       'Location','northwest');

%% ======================= HELPERS ===========================
function [diag_pairs, pairs] = equilibria_B(N, eps, SEEDS)
% Return diagonal equilibria as (r,r) PAIRS and off-diagonal (a,b).
    % --- Diagonal: tan(pi r / 2) = 2 r
    h = @(r) tan(pi*r/2) - 2*r;
    rs = [-0.5; 0; 0.5];                      % exact central roots
    for n = -N:N
        if n==0, continue; end
        a = (2*n - 1) + eps; b = (2*n + 1) - eps;   % inside strip
        try
            r = fzero(h, [a b]); rs(end+1,1) = r; %#ok<AGROW>
        catch
        end
    end
    rs = sort(rs);
    diag_pairs = [rs rs];                      % (r,r) pairs

    % --- Off-diagonal: solve G(a)=F(F(a))-a=0, b=F(a), skip b≈a
    F = @(x) 0.5*tan(pi*x/2);
    G = @(a) F(F(a)) - a;

    pairs = zeros(0,2);
    found = [];
    for n = -N:N
        if n==0, continue; end
        seeds = 2*n + SEEDS;
        for s = seeds
            try
                a = fzero(G, s);
                b = F(a);
                if ~isfinite(a) || ~isfinite(b), continue; end
                if abs(a-b) < 1e-8, continue; end
                if isempty(found) || all(abs(a-found) > 1e-6)
                    pairs(end+1,:) = [a b]; %#ok<AGROW>
                    found(end+1) = a; %#ok<AGROW>
                end
            catch
            end
        end
    end
end

function info = classify_all(eq, Jfun)
% For each equilibrium point, compute eigenvalues and type.
    if isempty(eq), info = struct([]); return; end
    info = struct('xbar',[],'eigs',[],'type','','is_stable',false);
    info = repmat(info, size(eq,1), 1);
    for k = 1:size(eq,1)
        xbar = eq(k,:);
        A    = Jfun(xbar.');
        L    = eig(A);
        t    = real(L);
        if any(t>0) && any(t<0)
            type = 'saddle'; stable = false;
        elseif all(t<0)
            type = tern(isreal(L),'stable node','stable focus'); stable = true;
        elseif all(t>0)
            type = tern(isreal(L),'unstable node','unstable focus'); stable = false;
        else
            type = 'center/other'; stable = false;
        end
        info(k).xbar = xbar;
        info(k).eigs = L;
        info(k).type = type;
        info(k).is_stable = stable;
    end
end

function print_table(info)
    if isempty(info), fprintf('  (none in window)\n'); return; end
    for k = 1:numel(info)
        x = info(k).xbar;
        L = info(k).eigs;
        fprintf('  x*=(% .6f,% .6f)  eig=[% .4f%+ .4fi, % .4f%+ .4fi]  -> %s\n',...
            x(1),x(2), real(L(1)), imag(L(1)), real(L(2)), imag(L(2)), info(k).type);
    end
end

function P = lyap2x2(A, Q)
% Solve A'P + P A = -Q. Uses 'lyap' if available; else builds 3x3 system.
    try
        P = lyap(A', Q);
        if all(isfinite(P),"all"), return; end
    catch
    end
    % Build linear system using symmetric basis S1,S2,S3
    S1 = [1 0; 0 0]; S2 = [0 1; 1 0]; S3 = [0 0; 0 1];
    pack = @(M)[M(1,1), M(1,2), M(2,2)];
    E1 = pack(A.'*S1 + S1*A);
    E2 = pack(A.'*S2 + S2*A);
    E3 = pack(A.'*S3 + S3*A);
    M  = [E1; E2; E3];
    b  = -pack(Q);
    x  = M\b;                        % x = [p r s]
    P  = [x(1) x(2); x(2) x(3)];
end

function rho = largest_rho(f, xbar, P, nangles)
% Largest rho with dV<0 on V(y)=rho (checked at 'nangles' points).
    [V,D] = eig(P); R = V*diag(1./sqrt(diag(D))); % P^{-1/2}
    rho_lo = 0; rho_hi = 1;
    while all_negative_on_boundary(f,xbar,P,R,rho_hi,nangles) && rho_hi < 1e4
        rho_lo = rho_hi; rho_hi = 2*rho_hi;
    end
    for it=1:40
        rho_mid = 0.5*(rho_lo+rho_hi);
        if all_negative_on_boundary(f,xbar,P,R,rho_mid,nangles)
            rho_lo = rho_mid;
        else
            rho_hi = rho_mid;
        end
    end
    rho = rho_lo;
end

function ok = all_negative_on_boundary(f,xbar,P,R,rho,nangles)
    if rho == 0, ok = true; return; end
    th = linspace(0,2*pi,nangles+1); th(end) = [];
    ok = true;
    for t = th
        y  = R*(sqrt(rho)*[cos(t); sin(t)]);
        x  = xbar + y;
        dx = f(x);
        dV = 2*y.'*P*dx;            % \dot V
        if ~isfinite(dV) || dV >= 0
            ok = false; return;
        end
    end
end

function draw_ellipse(P, rho, center, col, lw)
    [V,D] = eig(P); R = V*diag(1./sqrt(diag(D)));
    th = linspace(0,2*pi,360);
    circ = [cos(th); sin(th)];
    Y = R*(sqrt(rho)*circ);
    X = Y + center;
    plot(X(1,:), X(2,:), col, 'LineWidth', lw);
end

function plot_eqs(eq, info)
    if isempty(eq), return; end
    for k=1:size(eq,1)
        x = eq(k,:);
        switch info(k).type
            case 'saddle',         mfc = [1 0.95 0];
            case {'stable node','stable focus'}, mfc = [0.1 0.7 0.1];
            case {'unstable node','unstable focus'}, mfc = [0.85 0.1 0.1];
            otherwise,             mfc = [0.5 0.5 0.5];
        end
        plot(x(1),x(2),'ko','MarkerFaceColor',mfc,'MarkerSize',6);
    end
end

function draw_basins_A(fA, eqA, win)
% Coarse basin coloring for (A) by short ODE simulations.
    stabs = eqA(2:3,:);                        % the two stable nodes
    col   = [0.7 0.9 0.7; 0.9 0.7 0.7];        % colors for basins
    NX=35; NY=35;
    xs = linspace(win(1),win(2),NX);
    ys = linspace(win(3),win(4),NY);
    for ix = 1:NX-1
        for iy = 1:NY-1
            x0 = [ (xs(ix)+xs(ix+1))/2 ; (ys(iy)+ys(iy+1))/2 ];
            [~,X] = ode45(@(t,x) fA(x), [0 10], x0);
            xf = X(end,:);
            d = vecnorm(stabs - xf, 2, 2);
            [~,which] = min(d);
            rectangle('Position',[xs(ix),ys(iy), xs(ix+1)-xs(ix), ys(iy+1)-ys(iy)],...
                      'FaceColor',[col(which,:) 0.25], 'EdgeColor','none');
        end
    end
    q = findobj(gca,'Type','Quiver'); if ~isempty(q), uistack(q,'top'); end
end

function s = tern(cond,a,b), if cond, s=a; else, s=b; end
end
