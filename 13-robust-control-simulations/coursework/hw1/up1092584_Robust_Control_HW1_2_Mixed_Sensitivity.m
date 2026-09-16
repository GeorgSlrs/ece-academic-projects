clear; clc; close all;

%% (1) Original Plant and Disturbance
s = tf('s');
G  = 6 / ((8*s + 1)*(0.04*s + 1)^2);
Gd = 4.5 / (8*s + 1);

%% (2) Scaling
% y_norm = y/0.1 => y < 0.1 => y_norm < 1
% u_norm = u/3   => u < 3   => u_norm < 1
% => G_norm = 30*G, Gd_norm = 20*Gd
G_norm  = 30*G;
Gd_norm = 20*Gd;

%% (3) Weighting Functions
% W_S(s) = ( (s/2)+20 ) / ( s+0.02 )
% => W_S(0)=20/0.02=1000 => 60 dB at DC
W_S = ( (s/2)+20 ) / ( s + 0.02 );

% W_T(s) = ( s/30 +1 ) / ( 0.05*(s/30)+1 )
% => HF shaping for T
W_T = ( (s/30)+1 ) / ( 0.05*(s/30)+1 );

% W_U = 0.3 => penalize large control effort more strongly
W_U = 0.3;

disp('=== Weighting Functions ===');
disp('W_S(s) = ( (s/2)+20 ) / ( s + 0.02 )');
disp('W_T(s) = ( (s/30)+1 ) / ( 0.05*(s/30)+1 )');
disp('W_U(s) = 0.3');

%% (4) H∞ Synthesis
[K,CL,gamma,info] = mixsyn(G_norm, W_S, W_T, W_U);

disp('=== H∞ Controller K(s) ===');
K_min = minreal(K);
K_tf = tf(K_min)
fprintf('Achieved H∞ norm gamma=%.4f\n', gamma);

%% (5) Compute S, T, Dist->Out
S = feedback(1, G_norm*K);  % S = 1/(1+G_norm*K)
T = 1 - S;                  % T = G_norm*K/(1+G_norm*K)
Gd_cl = Gd_norm * S;        % Closed-loop Disturbance -> y_norm

%% (5.5) H∞ Norm of Closed-Loop Disturbance Transfer Function
Hinf_Gd = norm(Gd_cl, inf);
fprintf('H∞ norm of closed loop disturbance transfer function = %.4f\n', Hinf_Gd);

%% (6) Weighted Bode
figure;
bodemag(W_S*S, W_T*T, W_U*K*S, {1e-2,1e3});
grid on;
legend('|W_S*S|','|W_T*T|','|W_U*K*S|','Location','best');
title('Weighted Sensitivities (Aggressive)');

figure;
subplot(2,1,1);
bodemag(G_norm*K, {1e-2,1e3});
title('Open-Loop: G_{norm}*K');
grid on;
subplot(2,1,2);
bodemag(S, T, {1e-2,1e3});
legend('S','T','Location','best');
title('Sensitivity & Complementary Sensitivity');
grid on;

%% (New Section) Additional Frequency-Domain Plots

% Define a frequency range for analysis
w = logspace(-2, 3, 500);  % Frequency vector from 1e-2 to 1e3 rad/s

% Compute frequency responses for S, T, and G_norm*S
[magS, ~]       = bode(S, w);
[magT, ~]       = bode(T, w);
[magGnormS, ~]  = bode(G_norm*S, w);

% Remove singleton dimensions
magS      = squeeze(magS);
magT      = squeeze(magT);
magGnormS = squeeze(magGnormS);

figure;
semilogx(w, 20*log10(magS), 'b', 'LineWidth',2); hold on;
semilogx(w, 20*log10(magT), 'r', 'LineWidth',2);
semilogx(w, 20*log10(magGnormS), 'g', 'LineWidth',2);
grid on;
xlabel('Frequency (rad/s)');
ylabel('Magnitude (dB)');
legend('|S|','|T|','|G_{norm}S|','Location','best');
title('Magnitude of |S|, |T|, and |G_{norm}S|');

% Loop Gain Function: L = G_norm*K
L = G_norm*K;
[magL, phaseL, wLoop] = bode(L, w);
magL   = squeeze(magL);
phaseL = squeeze(phaseL);

figure;
subplot(2,1,1);
semilogx(wLoop, 20*log10(magL), 'b', 'LineWidth',2);
grid on;
ylabel('Magnitude (dB)');
title('Loop Gain Function: Magnitude');

subplot(2,1,2);
semilogx(wLoop, phaseL, 'r', 'LineWidth',2);
grid on;
xlabel('Frequency (rad/s)');
ylabel('Phase (deg)');
title('Loop Gain Function: Phase');

%% (7) Time-Domain Analysis
tEnd = 5; dt = 0.01; t = 0:dt:tEnd;

% (a) Reference step response of T
[y_ref, t_ref] = step(T, t);

% (b) Disturbance step response of Gd_cl
[y_dist, t_dist] = step(Gd_cl, t);

figure('Name','Time-Domain','NumberTitle','off');
subplot(2,1,1);
plot(t_ref, y_ref, 'b', 'LineWidth',2);
ylabel('y_{norm}');
title('Reference Step (y_{norm})');
grid on;
subplot(2,1,2);
plot(t_dist, y_dist, 'r', 'LineWidth',2);
ylabel('y_{norm}'); xlabel('Time (s)');
title('Disturbance Step (y_{norm})');
grid on;

%% (8) Performance Metrics
% Reference performance metrics
yRef_final = y_ref(end);
[~, idx10] = min(abs(y_ref - 0.1*yRef_final));
[~, idx90] = min(abs(y_ref - 0.9*yRef_final));
riseTime   = t(idx90) - t(idx10);
peakVal    = max(y_ref);
overshoot  = (peakVal - yRef_final) / yRef_final * 100;

fprintf('\n=== Reference Step ===\n');
fprintf('  Final y_norm = %.3f\n', yRef_final);
fprintf('  Rise Time (10-90%%) = %.3f s\n', riseTime);
fprintf('  Overshoot = %.2f %%\n', overshoot);

% Disturbance performance metrics
yDist_final = y_dist(end);
idx15 = find(t >= 1.5, 1, 'first');
yDist_15 = y_dist(idx15);

max_yRef  = max(abs(y_ref));
max_yDist = max(abs(y_dist));

fprintf('\n=== Disturbance Step ===\n');
fprintf('  Final y_norm = %.3f\n', yDist_final);
fprintf('  y_norm at 1.5 s = %.3f\n', yDist_15);
fprintf('  Max|y_norm| (ref) = %.3f, (dist) = %.3f\n', max_yRef, max_yDist);

%% (9) Check Control Effort
Uref_tf = K * S; 
[uref, ~] = step(Uref_tf, t);
uRef_max  = max(abs(uref));

Udist_tf = feedback(-K, G_norm);
[udist, ~] = step(Udist_tf, t);
uDist_max = max(abs(udist));

fprintf('\n=== Control Effort (u_{norm}) ===\n');
fprintf('  Max|u_{norm}| (ref) = %.3f, (dist) = %.3f\n', uRef_max, uDist_max);

%% (10) Spec Check
fprintf('\n=== Spec Check (Approx) ===\n');
fprintf('  Rise Time = %.3f (want < 0.3 s)\n', riseTime);
fprintf('  Overshoot = %.2f%% (want < 2%%)\n', overshoot);
fprintf('  Disturbance final y_{norm} = %.3f (want < 1, i.e., y < 0.1)\n', yDist_final);
fprintf('  Disturbance y_{norm} at 1.5 s = %.3f (want < 0.1, i.e., y < 0.01)\n', yDist_15);
fprintf('  Max|u_{norm}| (ref) = %.3f, (dist) = %.3f (want < 1, i.e., |u| < 3)\n', uRef_max, uDist_max);



