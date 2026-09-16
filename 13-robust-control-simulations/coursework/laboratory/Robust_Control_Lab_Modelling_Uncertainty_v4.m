%% Robust-Control Laboratory — SUPER-ANNOTATED FINAL VERSION
% =========================================================================
% This script now also *prints* the full H∞ controllers (Kmix_gu, Kmix_gd)
% along with all original analyses, Monte-Carlo plots, and performance metrics.
% =========================================================================

%% 1) GLOBAL SETUP ---------------------------------------------------------
clear; clc; close all;                    % Fresh MATLAB workspace
s     = tf('s');                          % Laplace operator (for TF creation) :contentReference[oaicite:6]{index=6}
wPlot = logspace(-1,2,600);               % Frequency grid: 0.1–100 rad/s
fprintf('[1] Environment initialized.\n\n');

%% 2) LOAD & NORMALIZE EXPERIMENTAL DATA ----------------------------------
w_Hz      = (0:9)';                       % Test freqs: 0–9 Hz
w_rad     = 2*pi*w_Hz;                    % → rad/s

amp_u_raw = [2;1.6;1.15;1;0.7;0.6;0.5;0.4;0.35;0.3];
amp_d_raw = [3;3.1;1.4;1.3;1;0.7;0.6;0.5;0.45;0.3];

% **Normalize each by its own max** (not by K_gu/K_gd)
amp_u = amp_u_raw / max(amp_u_raw);
amp_d = amp_d_raw / max(amp_d_raw);
fprintf('[2] Data normalized by each array''s maximum.\n\n');

%% 3) FIRST-ORDER NOMINAL FITS ---------------------------------------------
% These gains and time constants come from magnitude–only least‐squares fits.
K_gu   = 2.4;    tau_gu = 1.53;             % Gu: act→sensor path
Gu     = K_gu / (tau_gu*s + 1);            % Gu(s) = 2.4/(1.53 s + 1)

K_gd   = 1.67;   tau_gd = 1.12;             % Gd: disturbance→sensor path
Gd     = K_gd / (tau_gd*s + 1);            % Gd(s) = 1.67/(1.12 s + 1)

fprintf('[3] Nominal models defined:\n');
fprintf('    Gu(s) = 2.4 / (1.53 s + 1)\n');
fprintf('    Gd(s) = 1.67 / (1.12 s + 1)\n\n');

%% 4) VALIDATION PLOTS -----------------------------------------------------
figure('Name','Gu: Measured vs Nominal');
gu_nom = squeeze(freqresp(Gu,w_rad)) / K_gu;
semilogx(w_rad, amp_u, 'bo-','LineWidth',1.5); hold on; grid on;
semilogx(w_rad, abs(gu_nom), 'r--','LineWidth',2);
xlabel('\omega (rad/s)'); ylabel('Normalized |G_u|');
legend('Measured','Nominal','Location','best');

figure('Name','Gd: Measured vs Nominal');
gd_nom = squeeze(freqresp(Gd,w_rad)) / K_gd;
semilogx(w_rad, amp_d, 'ms-','LineWidth',1.5); hold on; grid on;
semilogx(w_rad, abs(gd_nom), 'k--','LineWidth',2);
xlabel('\omega (rad/s)'); ylabel('Normalized |G_d|');
legend('Measured','Nominal','Location','best');
fprintf('[4] Model-validation plots complete.\n\n');

%% 5) MULTIPLICATIVE MODELING ERRORS --------------------------------------
gu_exp     = amp_u * K_gu;                            
gu_nom_abs = abs(squeeze(freqresp(Gu,w_rad)));
relErr_gu  = abs(gu_exp ./ gu_nom_abs - 1);

gd_exp     = amp_d * K_gd;
gd_nom_abs = abs(squeeze(freqresp(Gd,w_rad)));
relErr_gd  = abs(gd_exp ./ gd_nom_abs - 1);

figure('Name','Modelling Errors');
semilogx(w_rad, relErr_gu,'b-o','LineWidth',1.5,'MarkerFaceColor','b'); hold on;
semilogx(w_rad, relErr_gd,'m-s','LineWidth',1.5,'MarkerFaceColor','m'); grid on;
xlabel('\omega (rad/s)'); ylabel('|G_{exp}/G_{nom}-1|');
legend('Gu','Gd','Location','northwest');
title('Multiplicative modelling errors');
fprintf('[5] Error envelopes plotted.\n\n');

%% 6) UNCERTAINTY WEIGHTS -------------------------------------------------
% Two frequency‐shaped weights to enclose relErr curves:
%   W_gu(s) = (s + 0.02)/(0.05 s + 1)
%   W_gd(s) = (0.5 s^2 + 0.01)/(0.005 s^2 + 0.1 s + 1)
a1=1; b1=0.02; c1=0.05; d1=1;
W_gu = tf([a1, b1],[c1, d1]);              % ultidyn Δ treated with W_gu :contentReference[oaicite:7]{index=7}

a2=0.5; b2=0; c2=0.01; 
d2=0.005; e2=0.1; f2=1;
W_gd = tf([a2, b2, c2],[d2, e2, f2]);

fprintf('[6] Uncertainty weights:\n');
fprintf('    W_gu(s) = (s + 0.02)/(0.05 s + 1)\n');
fprintf('    W_gd(s) = (0.5 s^2 + 0.01)/(0.005 s^2 + 0.1 s + 1)\n\n');

%% 7) BUILD UNCERTAIN PLANTS -----------------------------------------------
Delta_gu = ultidyn('Delta_gu',[1 1]);     % ||Δ_gu||∞ ≤ 1 :contentReference[oaicite:8]{index=8}
Delta_gd = ultidyn('Delta_gd',[1 1]);     % ||Δ_gd||∞ ≤ 1

Gu_unc = Gu * (1 + W_gu*Delta_gu);        % multiplicative uncertainty form :contentReference[oaicite:9]{index=9}
Gd_unc = Gd * (1 + W_gd*Delta_gd);
fprintf('[7] Uncertain models assembled.\n\n');

%% 8) H∞ MIXED-SENSITIVITY WEIGHTS -----------------------------------------
% Specs → tr<0.3s ⇒ ω_b=6, PO<2%⇒M=1.3, ess<1%⇒A=0.01
omega_b=6; M=1.3; A=0.01;
WS = tf([1/M, omega_b],[1, omega_b*A]);   % = (0.769 s + 6)/(s + 0.06) :contentReference[oaicite:10]{index=10}
WU = tf(0.5);                              % constant penalty on control effort

fprintf('[8] H∞ weights defined:\n');
fprintf('    W_S(s) = (0.769 s + 6)/(s + 0.06)\n');
fprintf('    W_U(s) = 0.5\n\n');

%% 9) CLASSICAL CONTROLLERS ------------------------------------------------
Kp    = 10;                               % P gain
Ki    = 10;                               % I gain
ctrlP = Kp;                               % P controller
ctrlPI= Kp + Ki/s;                        % PI controller
fprintf('[9] P and PI controllers defined.\n\n');

%% 10) H∞ CONTROLLER SYNTHESIS & PRINTING ---------------------------------
fprintf('[10] Computing mixed-sensitivity H∞ controllers…\n');
[Kmix_gu,~,gamma_gu] = mixsyn(Gu, WS, [], WU);  % Gu path H∞ design :contentReference[oaicite:11]{index=11}
[Kmix_gd,~,gamma_gd] = mixsyn(Gd, WS, [], WU);  % Gd path H∞ design
fprintf('    Gu γ_opt = %.3g,   Gd γ_opt = %.3g\n', gamma_gu, gamma_gd);

% **Print the full H∞ controller transfer functions**
fprintf('*** H∞ controller for Gu: ***\n'); disp(Kmix_gu);  % display TF form :contentReference[oaicite:12]{index=12}
fprintf('*** H∞ controller for Gd: ***\n'); disp(Kmix_gd);

fprintf('\n');

%% 11) μ-ANALYSIS -----------------------------------------------------------
fprintf('[11] μ-analysis (μ<1 ⇒ PASS):\n');
fprintf('Path | Ctrl | μ_RS   Result | μ_RP   Result\n');
for P = {'Gu','Gd'}
    p = P{1};
    if strcmp(p,'Gu'),  G_nom=Gu; G_unc=Gu_unc; Kmix=Kmix_gu;
    else                G_nom=Gd; G_unc=Gd_unc; Kmix=Kmix_gd; end
    ctrls = {struct('name','P','K',ctrlP), ...
             struct('name','PI','K',ctrlPI), ...
             struct('name','H∞','K',Kmix)};
    for k = 1:3
        C = ctrls{k};
        CL = feedback(G_unc*C.K,1);               % uncertain CL 
        [st,~] = robstab(CL);                     % μ_RS
        [pf,~]= robgain(CL,1);                    % μ_RP
        fprintf('%-3s | %-3s | %6.3f %-5s | %6.3f %-5s\n', ...
            p, C.name, st.LowerBound, ternary(st.LowerBound<1,'PASS','FAIL'), ...
                      pf.LowerBound, ternary(pf.LowerBound<1,'PASS','FAIL'));
    end
end
fprintf('\n');

%% 12) MONTE-CARLO + TIME-DOMAIN METRICS -----------------------------------
n_samps = 50;                              % number of samples :contentReference[oaicite:14]{index=14}
fprintf('[12] Monte-Carlo & performance metrics:\n');
for P = {'Gu','Gd'}
    p = P{1};
    if strcmp(p,'Gu'), G_nom=Gu; G_unc=Gu_unc; Kmix_path=Kmix_gu;
    else                G_nom=Gd; G_unc=Gd_unc; Kmix_path=Kmix_gd; end
    controllers = {struct('name','P','K',ctrlP), ...
                   struct('name','PI','K',ctrlPI), ...
                   struct('name','H∞','K',Kmix_path)};
    for c = 1:3
        C = controllers{c};

        % --- Monte-Carlo Bode overlay ---
        figure('Name',sprintf('%s — %s Monte-Carlo',p,C.name));
        bodemag(usample(feedback(G_unc*C.K,1),n_samps),'b:',wPlot);
        hold on; bodemag(feedback(G_nom*C.K,1),'r-',wPlot);
        title(sprintf('%s-path, %s controller — %d samples',p,C.name,n_samps));
        legend('Samples','Nominal','Location','best'); hold off;

        % --- Time-domain step-response metrics ---
        CL_nom = feedback(G_nom*C.K,1);
        info   = stepinfo(CL_nom,1, ...
                  'RiseTimeLimits',[0.1 0.9], ...
                  'SettlingTimeThreshold',0.02);        % stepinfo 
        tr   = info.RiseTime;                        % 10–90% rise time
        OS   = info.Overshoot;                       % % overshoot
        ts   = info.SettlingTime;                    % settling time
        dcg  = dcgain(CL_nom);                       % DC gain :contentReference[oaicite:16]{index=16}
        ess  = abs(1 - dcg)*100;                     % steady‐state error (%)
        fprintf('%s | %-3s | tr=%.3f s | OS=%.1f%% | ts=%.3f s | ess=%.2f%%\n', ...
                p, C.name, tr, OS, ts, ess);
    end
    fprintf('\n');
end

fprintf('*** All analyses complete. ***\n');

%% Helper function: ternary operator
function out = ternary(cond,a,b)
    if cond, out = a; else out = b; end
end

