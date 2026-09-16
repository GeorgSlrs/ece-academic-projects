clc;
clear;
close all;

% Define system parameters
ratiopd = 5;
G = tf([1 ratiopd 0], [1 0 0 0]);

% Define design specifications
Mp = 0.1;
tr = 0.3;
z = -log(Mp) / sqrt(pi^2 + log(Mp)^2);
wn = (2.16 * z + 0.6) / tr;

% Create a figure for root locus plots
figure;
subplot(2, 1, 1);
rlocus(G);
title("Root Locus of G(s)");
sgrid(z, wn);
% Annotating desired parameters on the plot
% Here you manually input the values determined from the root locus
% In practice, use this section to highlight or mark specific points on the plot
annotation('textbox', [0.5, 0.8, 0.1, 0.1], 'String', "K_D/J = 20, K_P/J = 100");

% Calculate feedback system with determined gains
K_D_J = 20; % Example value from root locus analysis
K_P_J = 100; % Example value from root locus analysis
T = feedback(K_D_J*G, 1);

% Plot step response of the closed-loop system
subplot(2, 1, 2);
step(T);
title("Step Response of Closed Loop System");
grid on;

% Display step response information
info = stepinfo(T);
disp(info);
