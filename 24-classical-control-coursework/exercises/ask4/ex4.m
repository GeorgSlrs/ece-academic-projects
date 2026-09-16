% Define the transfer function
s = tf('s');
T = 100 / (s*(s+6));

% Generate the Bode plot with log spacing from 0.1 to 1000 rad/s
omega = logspace(-1, 3, 1000); % 1000 points from 0.1 to 1000 rad/s
[mag,phase,wout] = bode(T,omega);

% Reshape the magnitude array to remove singleton dimensions
mag = reshape(mag, size(wout));

% Find resonance peak Mr and frequency wr
[Mr,wr_index] = max(mag); % Mr is the peak gain in absolute
wr = wout(wr_index); % wr is the frequency at peak gain

% Convert Mr to decibels
Mr_dB = 20*log10(Mr);

% Find the -3dB point for the bandwidth
BW_index = find(mag < Mr/sqrt(2), 1, 'first');
BW = wout(BW_index); % Bandwidth frequency

% Display results
fprintf('Resonance peak (Mr): %f dB\n', Mr_dB);
fprintf('Resonance frequency (wr): %f rad/s\n', wr);
fprintf('Bandwidth (BW): %f rad/s\n', BW);

