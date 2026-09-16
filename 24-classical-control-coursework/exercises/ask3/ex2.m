% Define the numerator and denominator of the transfer function G(s)
num = [1 -2 2];
den = [1 3 2 0];  % s(s^2 + 3s + 2) is equivalent to s^3 + 3s^2 + 2s

% Create the transfer function model
G = tf(num, den);

% Plot the root locus
figure;
rlocus(G);
title('Root Locus of Transfer Function G(s)');

%%Routh