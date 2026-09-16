% Define the system matrices
A = [-7 -4; 1 0];
B = [1; 0];
C = [1 4];
D = 1;

% Create the system model
sys = ss(A, B, C, D);

% Generate a range of frequencies from very low (DC) to high
freqs = logspace(-4, 4, 1000); % from 10^-4 to 10^4 rad/s

% Task a - Calculate DC-Gain and high-frequency gain from Bode plot
[mag,~,wout] = bode(sys, freqs);

% Extract the magnitude and convert to absolute (not dB)
mag = squeeze(mag(1,:,:));
abs_mag = 20*log10(mag);

% Find DC Gain (at frequency close to 0)
dc_gain = mag(1);
fprintf('DC Gain from Bode plot: %f\n', dc_gain);

% Find high-frequency gain (gain as frequency approaches a high value)
% Assuming high frequency as the last point of our freq range here for simplicity
high_freq_gain = mag(end);
fprintf('High-frequency Gain from Bode plot: %f\n', high_freq_gain);

% Alternatively, find the high-frequency gain from the Bode plot where the
% magnitude plot becomes flat indicating a steady value. This can be found by
% inspecting the plot or by finding the frequency where the slope of the magnitude
% plot is approximately zero.

% Plot the Bode diagram for visualization
figure;
bode(sys, freqs);
grid on;

% Task b - Plot the step response
figure;
step(sys, 12); % Plot step response for 12 seconds

% Calculate DC-Gain from the step response
dc_gain_step = dcgain(sys);
fprintf('DC Gain from step response: %f\n', dc_gain_step);