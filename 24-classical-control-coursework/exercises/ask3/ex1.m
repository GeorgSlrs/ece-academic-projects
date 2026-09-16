% Define the numerators and denominators of all three transfer functions
num_i = [1];
den_i = [1 4 6 1];
num_ii = [1 1];
den_ii = conv([1 0], [1 4 6]);
num_iii = [1 7];
den_iii = conv(conv([1 0], [1 2]), [1 9]);

% Create transfer function models
sys_i = tf(num_i, den_i);
sys_ii = tf(num_ii, den_ii);
sys_iii = tf(num_iii, den_iii);

% Plot the root locus of each transfer function on the same graph
figure;
hold on; % Hold the plot for multiple root locus plots
rlocus(sys_i, 'r'); % Plot with red color
rlocus(sys_ii, 'g'); % Plot with green color
rlocus(sys_iii, 'b'); % Plot with blue color
hold off; % Release the plot

% Add title and legend
title('Root Locus of Transfer Functions i, ii, and iii');
legend('Transfer Function i', 'Transfer Function ii', 'Transfer Function iii');
