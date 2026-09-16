%% Robust-Control Lab – Estimation, Analysis & Robust H∞ Design
clear; clc; close all
s = tf('s');

%% 0) Measured Bode data (normalized by DC gain = 2.4)
amp_meas = [2 1.6 1.15 1 0.7 0.6 0.5 0.4 0.35 0.3]';
w        = 2*pi*(0:9)';  % rad/s

%% 1) Nominal first-order model  G0(s) = K/(τ s + 1)
K_nom   = 2.4;
tau_nom = 1.53;
G0      = K_nom/(tau_nom*s + 1);

%% 2) Compute relative error l_I(ω) = |G_exp/G0 – 1|
magG0   = squeeze(abs(freqresp(G0,w)));
relErr  = abs((amp_meas*K_nom)./magG0 - 1);

%% 3) Fit multiplicative-uncertainty weight W_I(s)
peakErr = 1.2 * max(relErr);  % +20% margin
WI      = tf(peakErr);

%% 4) Build uncertain plant G_unc = G0*(1 + W_I*Delta)
Delta = ultidyn('Delta',[1 1]);  % ||Delta||_∞ ≤ 1
G_unc = G0*(1 + WI*Delta);

%% 5) Re-use previous performance weights WS, WU
WS = makeweight(10,[1 0.1],0.01);  % performance weight on S
WU = 0.2;                          % weight on control effort

%% 6) H∞ synthesis – same WS & WU, plus WI for uncertainty
[K_new, CL_new, gamma] = mixsyn(G0, WS, WU, WI);
fprintf('mixsyn γ = %.3f (γ<1 ⇒ specs met)\n', gamma);

%% 7a) μ-analysis: check RS & RP via μ-margins
RS = robstab(CL_new);             % robust stability margin (μ_RS)
RP = robgain(CL_new,1);           % robust performance margin (μ_RP)
fprintf('μ_RS lower-bound = %.2f (>1 ok)\n', RS.LowerBound);
fprintf('μ_RP lower-bound = %.2f (>1 ok)\n', RP.LowerBound);

%% 7b) NP/RS/RP inequalities (must stay < 1)
wplot  = logspace(-1,2,500);
S_nom  = squeeze(abs(bode( feedback(1, G0*K_new), wplot )));
T_nom  = squeeze(abs(bode( feedback(G0*K_new,1), wplot )));
WSmag  = squeeze(abs(bode( WS, wplot )));
WImag  = squeeze(abs(bode( WI, wplot )));

NPc = WSmag .* S_nom;           % |WS·S|
RSc = WImag .* T_nom;           % |WI·T|
RPc = NPc + RSc;                % |WS·S| + |WI·T|

%% 8-1) Plot uncertainty envelope vs. nominal
figure;
bodemag( usample(G_unc,40),'b:', G0,'r-',{0.1,100} ); grid on
title('Uncertain Plant Family vs Nominal G_0');
xlabel('ω (rad/s)'); ylabel('Magnitude (dB)');
legend('Random Δ samples','Nominal','Location','SouthWest');

%% 8-2) Plot NP (blue), RS (red), RP (black) vs bound=1
figure;
semilogx(wplot, NPc,'b', wplot, RSc,'r', wplot, RPc,'k','LineWidth',1.2);
yline(1,'k--'); grid on
title('NP, RS, RP Inequality Check (must stay <1)');
xlabel('ω (rad/s)'); ylabel('Magnitude');
legend('|WS·S|','|WI·T|','|WS·S|+|WI·T|','Bound =1','Location','NorthWest');

%% 8-3) Closed-loop magnitude spread
figure;
bodemag( usample(CL_new,40),'b:', feedback(G0*K_new,1),'r-',{0.1,100} );
grid on;
title('Closed-Loop Magnitude – Uncertain Family vs Nominal');
xlabel('ω (rad/s)'); ylabel('Magnitude (dB)');
legend('Family','Nominal','Location','SouthWest');

%% 8-4) Closed-loop Bode (mag & phase)
figure;
bode( usample(CL_new,20),'b:', feedback(G0*K_new,1),'r-',{0.1,100} );
grid on;
title('Closed-Loop Bode – Uncertain Family vs Nominal');
legend('Family','Nominal','Location','Best');

%% 8-5) Step response at worst-case plant
[~, Delta_wc] = wcgain(G_unc);     % worst-case Δ(s)
G_wc = usubs(G_unc, Delta_wc);     % numeric worst-case plant
figure;
step( feedback(G_wc*K_new,1), 5 ); grid on
title('Step Response with Worst-Case Plant');
xlabel('Time (s)'); ylabel('Output');
