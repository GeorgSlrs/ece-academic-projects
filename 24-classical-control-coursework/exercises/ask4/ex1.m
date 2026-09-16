% Define the transfer function H(s)
H = tf(20, [1 2 30]);

% Task a: Plot the Bode diagram and find the resonance frequency (ωr) and peak magnitude (Mp)
[mag, phase, w] = bode(H); % Get magnitude and phase data
mag = squeeze(mag); % Remove singleton dimensions
phase = squeeze(phase); % Remove singleton dimensions

[Mp, peakIndex] = max(mag); % Find the peak magnitude (Mp) and its index
wr = w(peakIndex); % Resonance frequency is the frequency at the peak magnitude
Mp = 20*log10(Mp); % Convert peak magnitude to dB

% Plot the Bode diagram
figure;
bode(H);
grid on;

% Print the resonance frequency and peak magnitude
fprintf('Resonance frequency (wr): %f rad/sec\n', wr);
fprintf('Peak magnitude (Mp): %f dB\n', Mp);

% Task b: Find the bandwidth (BW)
BW = bandwidth(H); % Find the bandwidth of H

% Print the bandwidth
fprintf('Bandwidth (BW): %f rad/sec\n', BW);

