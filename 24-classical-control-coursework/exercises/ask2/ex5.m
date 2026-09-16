
% Define system parameters
m = 1000; % mass of the car in kg
b = 50; % damping coefficient, Ns/m

% Transfer function of the system
s = tf('s');
G = 1/(m*s + b);

% Initial guess for PID parameters
Kp = 300;
Ki = 20;
Kd = 10;

% Optimization loop - manual adjustments based on observed performance
maxIterations = 100; % Limit on iterations to prevent infinite loops
tolerance = 0.02; % Tolerance for steady-state error (2% of the setpoint)

for i = 1:maxIterations
    % Define PID controller with current parameters
    C = pid(Kp, Ki, Kd);
    
    % Closed-loop system
    T = feedback(C*G, 1);
    
    % Simulate response to a step input of 10 m/s
    [y, t] = step(10*T, 0:0.01:100);
    
    % Calculate performance metrics
    info = stepinfo(T);
    ssErrorPercentage = abs((y(end) - 10) / 10) * 100; % Steady-state error as a percentage of the setpoint
    
    % Display current performance
    fprintf('Iteration: %d, Kp: %.2f, Ki: %.2f, Kd: %.2f\n', i, Kp, Ki, Kd);
    fprintf('Rise Time: %.2f s, Overshoot: %.2f%%, Settling Time: %.2f s, SS Error: %.2f%%\n', ...
        info.RiseTime, info.Overshoot, info.SettlingTime, ssErrorPercentage);
    
    % Check if criteria are met
    if info.RiseTime < 5 && info.Overshoot < 10 && ssErrorPercentage < 2
        disp('Criteria met!');
        break;
    else
        % Adjust PID parameters based on observed performance
        % Note: These adjustments are heuristic-based and may need fine-tuning
        
        % If overshoot is too high, increase Kd
        if info.Overshoot > 10
            Kd = Kd + 10;
        end
        
        % If steady-state error is too high, increase Ki
        if ssErrorPercentage > 2
            Ki = Ki + 5;
        end
        
        % If rise time is too long, increase Kp
        if info.RiseTime > 5
            Kp = Kp + 20;
        end
    end
    
    % Simple break to prevent infinite loop if conditions are not met
    if i == maxIterations
        disp('Max iterations reached without meeting criteria.');
    end
end

% Plot final response
figure;
step(10*T, 0:0.01:100);
title('Final PID Tuned Response');
xlabel('Time (s)');
ylabel('Speed (m/s)');
