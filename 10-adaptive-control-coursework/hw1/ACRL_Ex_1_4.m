%% simulate_GES_system_full.m
% System:  xdot = -a * ( I + S(x) + x x^T ) * x
% Dimension: 2 (so we can visualize). Proof holds for any n.
% This script:
%  (1) Draws phase portrait + many trajectories with arrows
%  (2) Plots V(t)=1/2||x||^2 vs V(0) e^{-2 a t}, and ||x(t)|| vs ||x(0)|| e^{-a t}
%  (3) Verifies dV/dt = x^T xdot = -a (||x||^2 + ||x||^4)
%  (4) Prints small diagnostics to confirm the exponential bound numerically

clear; clc; close all;

%% ------------------- User settings -------------------
a        = 1.0;                % >0
S_mode   = 'state_quad';       % 'zero' | 'const' | 'state_lin' | 'state_quad'
kS       = 2.0;                % parameter for S(x) when relevant
Tfinal   = 8.0;                % simulation horizon
nTraj    = 8;                  % trajectories per circle
radii    = [0.5, 1.0, 1.5];    % initial radii
gridL    = 2.2;                % field window [-gridL,gridL]^2
x0_main  = [ 1.3; -1.1 ];      % "main" IC used for V(t), ||x(t)|| plots
DO_CHECK = true;               % set false to skip numeric checks

%% ------------------- ODE RHS (2D) -------------------
% xdot = f(t,x) = -a * (I + S(x) + x x^T) * x
f = @(t,x) -a * ( (eye(2) + S_of_x(x,S_mode,kS) + (x*x.')) * x );

%% ------------------- Phase portrait vector field -------------------
Nx = 21; Ny = 21;
x1 = linspace(-gridL, gridL, Nx);
x2 = linspace(-gridL, gridL, Ny);
[X1,X2] = meshgrid(x1,x2);
U = zeros(size(X1)); V = zeros(size(X2));
for i = 1:numel(X1)
    x = [X1(i); X2(i)];
    dx = f(0,x);
    U(i) = dx(1); V(i) = dx(2);
end

figure('Color','w'); hold on; axis equal; grid on;
quiver(X1,X2,U,V,'AutoScale','on','AutoScaleFactor',0.6,'Color',[0.75 0.75 0.75]);
title(sprintf('Phase portrait: a=%.2f, S\\_mode=%s',a,S_mode),'Interpreter','tex');
xlabel('x_1'); ylabel('x_2'); xlim([-gridL gridL]); ylim([-gridL gridL]);

% Sample trajectories from circles of initial conditions
colors = lines(numel(radii));
for rr = 1:numel(radii)
    r = radii(rr);
    for m = 1:nTraj
        th = 2*pi*(m-1)/nTraj;
        x0 = r*[cos(th); sin(th)];
        [T,X] = ode45(f, [0 Tfinal], x0);

        plot(X(:,1), X(:,2), 'Color', colors(rr,:), 'LineWidth', 1.4);
        % add small arrows along each trajectory
        arrow_every = max(2, round(numel(T)/12));
        for j = 1:arrow_every:numel(T)-1
            p = X(j,:); q = X(j+1,:) - X(j,:);
            quiver(p(1),p(2),q(1),q(2),0,'MaxHeadSize',0.8,'Color',colors(rr,:));
        end

        % Optional: bound checks for each trajectory
        if DO_CHECK
            Vtraj  = 0.5*sum(X.^2,2);
            Vbnd   = Vtraj(1)*exp(-2*a*T);
            slack  = Vbnd - Vtraj;                 % should be >= 0 (up to small eps)
            Phi    = exp(2*a*T).*Vtraj;            % integrating-factor must be nonincreasing
            if min(slack) < -1e-7 || any(diff(Phi) > 1e-7)
                warning('Bound check tolerance exceeded at x0=[%.3f, %.3f]', x0(1), x0(2));
            end
        end
    end
end
plot(0,0,'ko','MarkerFaceColor','k','MarkerSize',5); % equilibrium

%% ------------------- Main trajectory for scalar plots -------------------
[Tmain,Xmain] = ode45(f,[0 Tfinal], x0_main);

%% ------------------- Figure 1b: V(t) vs exponential bound; ||x(t)|| ----------
Vmain = 0.5*sum(Xmain.^2,2);
Vbnd  = Vmain(1)*exp(-2*a*Tmain);

figure('Color','w');
subplot(2,1,1);
plot(Tmain,Vmain,'LineWidth',1.8); hold on;
plot(Tmain,Vbnd,'--','LineWidth',1.8);
xlabel('t'); ylabel('V(t)=\frac{1}{2}\|x(t)\|^2','Interpreter','tex');
legend('Actual V(t)','V(0) e^{-2 a t}','Location','northeast');
grid on; title('Lyapunov decay and exponential comparison bound');

subplot(2,1,2);
normX = sqrt(sum(Xmain.^2,2));
plot(Tmain, normX, 'LineWidth',1.8); grid on;
xlabel('t'); ylabel('||x(t)||');
title('State norm ||x(t)||');

if DO_CHECK
    slackV = Vbnd - Vmain;                          % >= 0 ideally
    Phi    = exp(2*a*Tmain).*Vmain;                 % nonincreasing
    fprintf('Min slack Vbound - V = %.3e\n', min(slackV));
    fprintf('Max increase in Phi=e^{2at}V: %.3e\n', max([0; diff(Phi)]));
end

%% ------------------- Figure 2: Verify dV/dt = x^T xdot = -a(||x||^2+||x||^4) --
Vdot_num = zeros(size(Tmain));
Vdot_clo = zeros(size(Tmain));
for i = 1:numel(Tmain)
    x  = Xmain(i,:).';
    dx = f(Tmain(i), x);
    Vdot_num(i) = x.'*dx;
    Vdot_clo(i) = -a*(norm(x)^2 + norm(x)^4);
end
figure('Color','w');
plot(Tmain,Vdot_num,'LineWidth',1.8); hold on; grid on;
plot(Tmain,Vdot_clo,'--','LineWidth',1.8);
xlabel('t'); ylabel('\dot V(t)');
legend('x^T \dot x (numerical)','-a(\|x\|^2+\|x\|^4)','Interpreter','tex','Location','best');
title('Verification of \dot V formula');

%% ------------------- Figure 3: ||x(t)|| vs bound and component envelopes -----
boundNorm = norm(x0_main)*exp(-a*Tmain);   % ||x(0)|| e^{-a t}

figure('Color','w');

% Top: norm vs bound
subplot(2,1,1);
plot(Tmain, normX, 'LineWidth', 1.8); hold on; grid on;
plot(Tmain, boundNorm, '--', 'LineWidth', 1.8);
xlabel('t'); ylabel('||x(t)||');
title('State norm and exponential bound');
legend('||x(t)||','||x(0)|| e^{-a t}','Location','northeast');

% Bottom: components with ± envelope (|x_i(t)| <= ||x(0)|| e^{-a t})
subplot(2,1,2); hold on; grid on;
tt  = Tmain(:);
env = boundNorm(:);
% shaded envelope
fill([tt; flipud(tt)], [env; -flipud(env)], [0.88 0.92 1.00], ...
     'EdgeColor','none','FaceAlpha',0.5);
% components
plot(Tmain, Xmain(:,1), 'LineWidth', 1.5);
if size(Xmain,2) >= 2
    plot(Tmain, Xmain(:,2), 'LineWidth', 1.5);
end
yline(0,'k:');
xlabel('t'); ylabel('states');
title('Components inside the exponential envelope');
legend('{\pm}||x(0)|| e^{-a t}','x_1(t)','x_2(t)','Location','northeast');

if DO_CHECK
    slack_norm = boundNorm - normX;                 % >= 0 ideally
    fprintf('Min slack (norm bound): %.3e\n', min(slack_norm));
end

%% ------------------- Helper: S(x) -------------------
function S = S_of_x(x, mode, k)
% Returns a 2x2 skew-symmetric matrix S(x) (S' = -S).
% We use S(x) = [ 0  -sigma(x);  sigma(x)  0 ] with different sigma(x).
    switch mode
        case 'zero'
            sigma = 0;
        case 'const'
            sigma = k;                         % constant rotation
        case 'state_lin'
            sigma = k * (x(1)+x(2));          % linear in state
        case 'state_quad'
            sigma = k * (1 + norm(x)^2);      % grows with radius
        otherwise
            error('Unknown S_mode.');
    end
    S = [0, -sigma; sigma, 0];
end

