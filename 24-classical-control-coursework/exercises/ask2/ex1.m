% Define the numerator and denominator of the transfer function
numerator = conv([1, 7], 1); % Convolution is not actually needed here since [1, 7] is already the numerator
denominator = conv([1, 0, 0], [1, 10]);

% Create a transfer function model
sys = tf(numerator, denominator);

% Time vector from 0 to 25 seconds
t = 0:0.01:25; 

% Step response for a unit step input u(t) = 1 for t >= 0
u = ones(size(t)); 

% Calculate the step response using lsim, which can also handle custom inputs
[y, t] = lsim(sys, u, t);

% Plot the response
plot(t, y);
xlabel('Time (seconds)');
ylabel('Response');
title('Step Response of the SISO System');
grid on;
