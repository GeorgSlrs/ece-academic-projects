% Define the parameters
m = 1000;  % mass of the car in kg
b = 50;    % damping coefficient

% Define the transfer function for the car's dynamics
s = tf('s');
G = 1/(m*s + b);

% Define the desired speed as a function of time
t = 0:0.01:50; % time vector from 0 to 50 seconds with a step of 0.01s
v_desired = 4*cos(0.2*t); % desired velocity

% Since this is a P controller, we need to choose a gain Kp
% The gain Kp needs to be chosen to achieve the settling time criteria
% This typically requires trial and error or analytical methods, but let's assume Kp for now
Kp = 800; % This is an initial guess and would need to be tuned

% Create a P controller
P = Kp;

% The closed-loop transfer function with the P controller
T_cl = feedback(P*G, 1);

% Simulate the response of the closed-loop system to the desired speed
% Assuming the initial condition is 0, we use lsim to simulate the response
[v_actual, t_out] = lsim(T_cl, v_desired, t);

% Plot the actual vs desired speed
figure;
plot(t_out, v_actual, 'b-', t, v_desired, 'r--');
xlabel('Time (seconds)');
ylabel('Speed (m/s)');
title('Cruise Control Response with P Controller');
legend('Actual Speed', 'Desired Speed');
grid on;
% Bode plot of the open-loop system
figure;
bode(G);
grid on;
