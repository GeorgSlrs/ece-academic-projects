% Define the transfer functions
s = tf('s');
G = 10 / (s + 1);
Gc = 9 / (s + 1);

% Get the open-loop transfer function
L = G * Gc;

% Calculate the phase and gain margins
[~, ~, ~, phase_margin] = margin(L);

% Calculate the closed-loop transfer function for unity feedback
T = feedback(L, 1);

% Get the step response data
[y, t] = step(T);

% Calculate the percentage overshoot
Mp = (max(y) - 1) * 100;

% Display the results
fprintf('The phase margin is approximately %.2f degrees\n', phase_margin);
fprintf('The percentage overshoot of the closed-loop system is %.2f%%\n', Mp);
