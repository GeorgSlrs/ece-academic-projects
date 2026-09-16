% Define the parameters for the mass, damping, and spring constant.
M = 10;  % mass (kg)
b = 0.5;   % damping coefficient (kg/s)
k = 1; % spring constant (N/m)
y0 = 0;  % equilibrium position (m)

% Define the forcing function as a sinusoidal function for this example.
F = @(t) 1; 

% Define the initial conditions.
y_initial = y0;      % initial displacement (m)
v_initial = 0;       % initial velocity (m/s)
initial_conditions = [y_initial, v_initial];

% Define the time span to solve the differential equation.
tspan = [0, 100]; % time from 0 to 100 seconds

% Define the differential equation as a function handle.
odefun = @(t, y) [y(2); (F(t) - b*y(2) - k*(y(1) - y0))/M];

% Solve the differential equation using ode45.
[t, Y] = ode45(odefun, tspan, initial_conditions);

% Plot the results.
plot(t, Y(:,1)); % Plot displacement over time
xlabel('Time (s)');
ylabel('Displacement (m)');
title('Displacement of Mass Over Time');
