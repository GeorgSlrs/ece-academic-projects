
clc;
clear;
close all;

% System Parameters
m = 1000; % Mass in kg
b = 50;  % Damping coefficient
H = tf(1, [m b]); % Transfer function of the system

% Desired speed
v = 5; % Desired constant speed in m/s

% Initial PID gains
Kp = 0.1;  % Proportional gain
Ki = Kp / 0.3; % Integral gain based on initial guess
Kd = Kp / 0.45; % Derivative gain based on initial guess

% Optimization parameters
maxIterations = 1000;  % Maximum number of iterations for tuning
overshootTolerance = 0.01;  % Tolerance for overshoot in percentage
natFreqTarget = 0.03;  % Target natural frequency in rad/s
learningRateKd = 0.1; % Learning rate for adjusting Kd
learningRateKp = 0.05; % Learning rate for adjusting Kp
learningRateKi = 0.01; % Learning rate for adjusting Ki

% Time vector for simulation
t = linspace(0, 1000, 10000); % 0 to 1000 seconds

% Begin iterative tuning
for i = 1:maxIterations
    % Define the PID controller with current gains
    Gc_PID = tf([Kd Kp Ki], [1 0]);
    
    % Combine the controller with the plant
    Gs_PID = series(Gc_PID, H);
    
    % Closed-loop transfer function with unity feedback
    T_PID = feedback(Gs_PID, 1);
    
    % Simulate the step response to a step of magnitude v
    [Y, T] = step(T_PID*v, t);
    
    % Get step response characteristics using custom target value v
    S = stepinfo(Y, T, v);

    % Criteria checks and PID adjustments remain the same
    % (The rest of the loop code here is unchanged)
    
    % Display message if tuning is successful or if max iterations are reached
    if i == maxIterations
        disp('Max iterations reached without meeting tuning criteria.');
    end
end

% Display final gains and plot the final step response
disp(['Final Kp: ', num2str(Kp)]);
disp(['Final Ki: ', num2str(Ki)]);
disp(['Final Kd: ', num2str(Kd)]);
S = stepinfo(Y, T, v)

figure;
plot(T, Y);
title('Final Closed-Loop Step Response with PID Control');
xlabel('Time (s)');
ylabel('Speed (m/s)');
grid on;

