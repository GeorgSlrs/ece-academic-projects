% Define transfer functions for the servo motor and the aircraft
M_s = tf([-10], [1 10]);
G_s = tf([-1 -5], [1 3.5 6]);

% The desired step response has a transfer function C(s) = 2, which we assume
% is a constant gain controller here for simplicity
C_s = 2; 

% Open-loop transfer function
open_loop_tf = series(C_s * M_s, G_s);

% Closed-loop transfer function with unity feedback
closed_loop_tf = feedback(open_loop_tf, 1);

% Time vector for simulation
t = 0:0.01:10; % simulate for 10 seconds

% The desired height function θ_d(t) = at, where a = 0.5/s
a = 0.5;
theta_d = a * t;

% Simulate the response of the system to the desired height function
[theta, t_out] = lsim(closed_loop_tf, theta_d, t);

% Plot the actual height versus time
figure;
plot(t_out, theta);
title('Actual Height vs Time with Initial Controller');
xlabel('Time (s)');
ylabel('Actual Height (θ(t))');
grid on;

% Now, replace the constant gain controller with a PID controller
% Use pidtune to find appropriate PID parameters
% Note: We'll start with some default tuning and then we might need to
% iterate to find parameters that minimize the error
pid_controller = pidtune(series(M_s, G_s), 'PID');

% Update the closed-loop transfer function with the PID controller
closed_loop_pid_tf = feedback(pid_controller * series(M_s, G_s), 1);

% Simulate the response of the system with PID controller
[theta_pid, t_out_pid] = lsim(closed_loop_pid_tf, theta_d, t);

% Plot the actual height versus time with PID controller
figure;
plot(t_out_pid, theta_pid);
title('Actual Height vs Time with PID Controller');
xlabel('Time (s)');
ylabel('Actual Height (θ(t))');
grid on;

% Calculate and display the step response information with PID controller
step_info_pid = stepinfo(closed_loop_pid_tf);
disp(step_info_pid);
