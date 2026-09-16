function demo_fminimax_PI_design
    %% 1. Define the Plant and Weighting Functions
    s = tf('s');
    % Plant: G(s) = 4 / [(s-1)*(0.02*s+1)^2]
    G = 4 / ((s - 1)*(0.02*s + 1)^2);
    
    % Define performance weights:
    % Sensitivity weight Ws: shapes the tracking/disturbance rejection.
    Ws = (s + 0.2)/(0.001*s + 0.2);
    % Control weight Wks: limits the control signal magnitude (static gain).
    Wks = 0.1;
    
    %% 2. Tune PI Controller Using fminimax (Minimax Approach)
    % Define the objective function for fminimax over a frequency grid.
    freqGrid = logspace(-2, 2, 500);
    objHandle = @(x)objPI(x, freqGrid, G, Ws, Wks);
    
    % Initial guess for [Kp, Ki]
    x0 = [1, 1];
    
    % Set options using optimset (older syntax)
    options = optimset('Display', 'iter', 'MaxFunEvals', 1000);
    
    % Run fminimax to tune the PI gains.
    [x_opt, fval] = fminimax(objHandle, x0, [], [], [], [], [], [], [], options);
    Kp = x_opt(1);
    Ki = x_opt(2);
    
    fprintf('\n---------- MINIMAX PI DESIGN ----------\n');
    fprintf('Optimal PI Gains: Kp = %.4f, Ki = %.4f\n', Kp, Ki);
    fprintf('Achieved performance norm (gamma) = %.4f\n', fval);
    
    % PI controller transfer function (built as a tf object)
    K_pi = Kp + Ki/s;
    
    %% 3. Synthesize H∞ Controller Using mixsyn
    [K_hinf, ~, gamma] = mixsyn(G, Ws, Wks, []);
    % Simplify and convert to tf object.
    K_hinf = minreal(tf(K_hinf));
    
    %% 4. Display Transfer Functions in Polynomial Form
    % For the PI controller:
    [num_pi, den_pi] = tfdata(K_pi, 'v');  % Extract numerator and denominator as vectors
    fprintf('\n---------- PI Controller Transfer Function ----------\n');
    fprintf('Numerator coefficients:\n');
    disp(num_pi);
    fprintf('Denominator coefficients:\n');
    disp(den_pi);
    
    % For the H∞ controller:
    [num_hinf, den_hinf] = tfdata(K_hinf, 'v');
    fprintf('\n---------- H∞ Controller Transfer Function ----------\n');
    fprintf('Numerator coefficients:\n');
    disp(num_hinf);
    fprintf('Denominator coefficients:\n');
    disp(den_hinf);
    
    %% 5. Compare Closed-Loop Metrics
    [Ms_pi, Mt_pi, bw_pi, Gm_pi, Pm_pi] = compute_metrics(G, K_pi);
    [Ms_hinf, Mt_hinf, bw_hinf, Gm_hinf, Pm_hinf] = compute_metrics(G, K_hinf);
    
    fprintf('\n---------- Performance Comparison ----------\n');
    fprintf('Metric\t\t\tPI Design\tH∞ Design\n');
    fprintf('Bandwidth (rad/s)\t%.4g\t\t%.4g\n', bw_pi, bw_hinf);
    fprintf('Peak Sensitivity (Ms)\t%.4g\t\t%.4g\n', Ms_pi, Ms_hinf);
    fprintf('Peak Comp. Sens. (Mt)\t%.4g\t\t%.4g\n', Mt_pi, Mt_hinf);
    fprintf('Gain Margin (dB)\t%.4g\t\t%.4g\n', 20*log10(Gm_pi), 20*log10(Gm_hinf));
    fprintf('Phase Margin (deg)\t%.4g\t\t%.4g\n', Pm_pi, Pm_hinf);
    
    %% 6. Plot Closed-Loop Results
    CL_pi = feedback(G*K_pi, 1);
    CL_hinf = feedback(G*K_hinf, 1);
    
    figure;
    step(CL_pi, CL_hinf, 5);
    legend('PI Controller (Minimax)', 'H∞ Controller (mixsyn)');
    title('Closed-Loop Step Response Comparison');
    xlabel('Time (s)');
    ylabel('Output');
    grid on;
    
    figure;
    bode(feedback(1, G*K_pi), feedback(1, G*K_hinf));
    legend('S (Minimax PI)', 'S (H∞)');
    title('Bode Plot of Sensitivity Functions');
    grid on;
    
    % Additionally, plot the controller transfer functions' pole-zero maps.
    figure;
    pzplot(K_pi);
    title('Pole-Zero Plot: PI Controller (Minimax)');
    grid on;
    
    figure;
    pzplot(K_hinf);
    title('Pole-Zero Plot: H∞ Controller (mixsyn)');
    grid on;
end

%% Objective Function for PI Controller Design using fminimax
function F = objPI(x, w, G, Ws, Wks)
    s_val = 1i * w;  % Define s = j*w for the frequency grid
    G_val = squeeze(freqresp(G, w));
    
    % PI controller: K(s) = Kp + Ki/s
    K_val = x(1) + x(2)./s_val;
    
    % Closed-loop sensitivity: S(s) = 1/(1+G(s)*K(s))
    S_val = 1 ./ (1 + G_val .* K_val);
    
    % Evaluate weighting functions.
    Ws_val = squeeze(freqresp(Ws, w));
    Wks_val = Wks * ones(size(w));  % Replicate scalar weight
    
    % Compute the weighted performance measures.
    perf1 = abs(Ws_val .* S_val);
    perf2 = abs(Wks_val .* (K_val .* S_val));
    
    % The objective is the maximum of these two values at each frequency.
    F = max(perf1, perf2);
end

%% Helper Function to Compute Closed-Loop Metrics
function [Ms, Mt, bw, Gm, Pm] = compute_metrics(G, K)
    S = feedback(1, G*K);
    T = feedback(G*K, 1);
    CL = feedback(G*K, 1);
    
    Ms = norm(S, inf);       % Peak sensitivity
    Mt = norm(T, inf);       % Peak complementary sensitivity
    bw = bandwidth(CL);      % Closed-loop bandwidth
    [Gm, Pm] = margin(G*K);  % Gain and phase margins
end
