
% Define system parameters
J = 0.01;  % Moment of inertia
b = 0.1;   % Motor damping coefficient
Kt = 0.01; % Motor torque constant
R = 1;     % Electric resistance
L = 0.5;   % Electric inductance

% Define the transfer function of the motor
P_motor = tf(Kt, [J*L J*R+b*L b*R+Kt^2]);

% PID tuning
% The 'pidtune' function does not directly accept overshoot and settling time
% as input arguments. We start with a standard tuning and then may have to
% manually iterate to meet the requirements exactly.
% Initial PID tuning
[pid_controller, info] = pidtune(P_motor, 'PID');

% Adjust controller parameters to achieve the desired performance
% This might require manual iteration to find parameters that satisfy the criteria
pid_controller.Kp = pid_controller.Kp * 1.5; % Increase proportional gain
pid_controller.Ki = pid_controller.Ki * 1;   % Integral gain
pid_controller.Kd = pid_controller.Kd * 0.5; % Decrease derivative gain

% Define a new transfer function that includes the PID controller
T_closed_loop = feedback(pid_controller*P_motor, 1);

% Simulate step response to a step of magnitude 3 rad/s
final_value = 3;  % Final value for the step input
[y, t] = step(T_closed_loop * final_value, 10);

% Calculate performance criteria
S = stepinfo(T_closed_loop * final_value);

% Check if performance criteria are met
settling_time = S.SettlingTime;
overshoot = S.Overshoot;
steady_state_error = abs(final_value - y(end)) / final_value;

% Print out the performance criteria
fprintf('Settling Time: %.2f s\n', settling_time);
fprintf('Overshoot: %.2f%%\n', overshoot);
fprintf('Steady State Error: %.2f%%\n', steady_state_error * 100);

% Plot the response
figure;
plot(t, y);
title('Step Response with PID Controller');
xlabel('Time (s)');
ylabel('Angular Velocity (rad/s)');
grid on;

% Determine if the design criteria are met
is_criteria_met = settling_time < 2 && overshoot < 5 && steady_state_error < 0.01;

% Display if criteria are met
if is_criteria_met
    disp('The designed PID controller meets all design criteria.');
else
    disp('The designed PID controller does not meet all design criteria.');
end

