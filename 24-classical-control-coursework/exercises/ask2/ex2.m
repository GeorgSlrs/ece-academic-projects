% Time vector from 0 to 30 seconds
t = 0:0.01:30; 

% Define the system parameters for each case
params = [2, 0; 2, 0.1; 1, 0; 1, 0.2];

% Create a figure to hold the subplots
figure;

% Loop through each set of parameters to create and plot the impulse response
for i = 1:4
    % Unpack omega_n and zeta for the current iteration
    omega_n = params(i, 1);
    zeta = params(i, 2);
    
    % Define the numerator and denominator of the transfer function
    numerator = omega_n^2; % For an impulse response, the numerator is omega_n^2
    denominator = [1, 2*zeta*omega_n, omega_n^2];
    
    % Create a transfer function model
    sys = tf(numerator, denominator);
    
    % Create a subplot for the current impulse response
    subplot(2, 2, i);
    impulse(sys, t);
    grid on;
    
    % Title for the subplot indicating the parameters
    title(['Impulse Response with omega_n = ', num2str(omega_n), ' and zeta = ', num2str(zeta)]);
    xlabel('Time (seconds)');
    ylabel('Amplitude');
end

% Adjust layout to prevent subplot titles and labels from overlapping
sgtitle('Impulse Responses for Different Values of zeta and omega_n'); % Super title for all subplots
