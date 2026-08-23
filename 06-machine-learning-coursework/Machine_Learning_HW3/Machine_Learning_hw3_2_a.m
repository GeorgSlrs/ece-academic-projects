
function ComputeOptimalFunctionsAndGenerateData()
    % ComputeOptimalFunctionsAndGenerateData
    %
    % This script performs the following tasks:
    % 1. Computes the expected value functions V1(S) and V2(S) for each state S
    %    using the trapezoidal rule for numerical integration.
    % 2. Determines the optimal policy by selecting the action that maximizes the
    %    expected reward for each state.
    % 3. Generates two datasets of (St, St+1) pairs based on randomly chosen actions.
    % 4. Visualizes the value functions and the optimal policy with plots centered at (0,0).

    %% =========================
    % 1. Numerical Computation
    % ==========================

    % Parameters
    S_min = -10;
    S_max = 10;
    m = 1001;                        % Number of current state grid points
    n = 1001;                        % Number of next state grid points
    S_grid = linspace(S_min, S_max, m)'; % Current state grid [m x 1]
    y_grid = linspace(S_min, S_max, n)'; % Next state grid [n x 1]
    Delta_y = (S_max - S_min) / (n - 1); % Step size in y

    % Reward Function: R(y) = min{2, y^2}
    R = min(2, y_grid.^2);           % Reward vector [n x 1]

    % Initialize Matrices F1 and F2 for actions alpha = 1 and alpha = 2
    F1 = zeros(m, n);                % For action alpha = 1
    F2 = zeros(m, n);                % For action alpha = 2

    % Create grids for current and next states using meshgrid
    [Y_grid_mat, X_grid_mat] = meshgrid(y_grid, S_grid); % Y_grid_mat: [m x n], X_grid_mat: [m x n]

    % Compute means for each action
    mu1_matrix = 0.8 * X_grid_mat + 1.0;        % Mean for alpha = 1 [m x n]
    mu2_matrix = -2.0 * ones(m, n);              % Mean for alpha = 2 [m x n]
    sigma1 = 1.0;                                % Standard deviation for alpha = 1
    sigma2 = 1.0;                                % Standard deviation for alpha = 2

    % Compute CDFs using normcdf for all combinations of S_j and y_i
    H1 = normcdf(Y_grid_mat, mu1_matrix, sigma1); % [m x n] CDF for alpha = 1
    H2 = normcdf(Y_grid_mat, mu2_matrix, sigma2); % [m x n] CDF for alpha = 2

    % Construct Matrix F for Each Action Using the Trapezoidal Weights
    % F_{ji} = 0.5 * (H(y_i | S_j) - H(y_{i-1} | S_j))
    % For i = 1, assume H(y0 | S_j) = 0

    % For alpha = 1
    F1(:,1) = 0.5 * H1(:,1);                          % First column
    F1(:,2:n) = 0.5 * (H1(:,2:n) - H1(:,1:n-1));      % Remaining columns

    % For alpha = 2
    F2(:,1) = 0.5 * H2(:,1);                          % First column
    F2(:,2:n) = 0.5 * (H2(:,2:n) - H2(:,1:n-1));      % Remaining columns

    % Construct Vector G Using the Average of R(y_i) and R(y_{i-1}) for Trapezoidal Rule
    G = zeros(n,1);
    G(1) = R(1);                                      % G_1 = R(y_1)
    G(2:n) = (R(1:n-1) + R(2:n)) / 2;                % G_i = (R(y_{i-1}) + R(y_i)) / 2 for i=2,...,n

    % Compute V1(S_j) and V2(S_j) Using F and G
    V1 = F1 * G;                                      % Expected reward for alpha = 1 [m x 1]
    V2 = F2 * G;                                      % Expected reward for alpha = 2 [m x 1]

    % Determine Optimal Policy
    [V_optimal, policy] = max([V1, V2], [], 2);       % [m x 1], [m x1]
    % policy(j) = 1 if V1(j) > V2(j), else 2

    % ==============================
    % 2. Data Generation
    % ==============================

    % Number of transitions
    N = 1000;

    % Initialize arrays to store (St, St+1) pairs
    St_action1 = zeros(0,2);                        % Pairs where alpha_t = 1
    St_action2 = zeros(0,2);                        % Pairs where alpha_t = 2

    % Initialize S1 ~ N(0,1)
    S_current = randn(N,1);                          % Generates N samples from N(0,1)
    % Note: To generate a single sequence of 1001 states, adjust accordingly.

    % For this implementation, assuming N=1000 independent transitions:
    % Each transition starts with S_t ~ N(0,1), choose alpha_t, generate S_{t+1}

    % Alternatively, to generate a single sequence of 1001 states with 1000 transitions:
    % Uncomment the following block and comment the above.

    %{
    S_sequence = zeros(N+1,1);
    S_sequence(1) = randn();                       % S1 ~ N(0,1)
    for t = 1:N
        alpha_t = randi([1,2]);                     % Randomly choose alpha_t = 1 or 2
        if alpha_t == 1
            S_sequence(t+1) = 0.8 * S_sequence(t) + 1.0 + randn(); % St+1 for alpha=1
            St_action1 = [St_action1; S_sequence(t), S_sequence(t+1)];
        else
            S_sequence(t+1) = -2.0 + randn();        % St+1 for alpha=2
            St_action2 = [St_action2; S_sequence(t), S_sequence(t+1)];
        end
    end
    %}

    % To generate N=1000 independent transitions:
    for t = 1:N
        % Initialize S_t ~ N(0,1)
        St = randn();
        
        % Randomly choose alpha_t = 1 or 2 with equal probability
        alpha_t = randi([1,2]);
        
        % Generate S_{t+1} based on alpha_t
        if alpha_t == 1
            St_plus1 = 0.8 * St + 1.0 + randn();  % alpha = 1
            St_action1 = [St_action1; St, St_plus1];
        else
            St_plus1 = -2.0 + randn();            % alpha = 2
            St_action2 = [St_action2; St, St_plus1];
        end
    end

    % ==============================
    % 3. Visualization
    % ==============================

    % Plot Value Functions V1(S) and V2(S)
    figure('Name', 'Value Functions', 'NumberTitle', 'off');
    plot(S_grid, V1, 'r-', 'LineWidth', 2); hold on;
    plot(S_grid, V2, 'b--', 'LineWidth', 2);
    xlabel('State S');
    ylabel('V_{\alpha}(S)');
    title('Value Functions V1(S) and V2(S)');
    legend('V1(S) - Action 1', 'V2(S) - Action 2', 'Location', 'Best');
    grid on;
    axis tight;
    % Center the graph at (0,0) by adjusting axis limits
    xlim([S_min, S_max]);
    ylim([min([V1; V2]) - 0.1*abs(min([V1; V2])), max([V1; V2]) + 0.1*abs(max([V1; V2]))]);
    hold off;

    % Plot Optimal Policy
    figure('Name', 'Optimal Policy', 'NumberTitle', 'off');
    stairs(S_grid, policy, 'LineWidth', 2);
    xlabel('State S');
    ylabel('Optimal Action \alpha^*(S)');
    title('Optimal Policy \alpha^*(S)');
    yticks([1,2]);
    yticklabels({'Action 1', 'Action 2'});
    grid on;
    axis tight;
    % Center the graph at (0,0) by adjusting axis limits
    xlim([S_min, S_max]);
    ylim([0.5, 2.5]); % To accommodate ytick labels
    hold off;

    % ==============================
    % 4. Sample Outputs
    % ==============================

    % Display sample outputs at S = 0
    [~, idx_zero] = min(abs(S_grid - 0));            % Find index closest to S=0
    V1_at_zero = V1(idx_zero);
    V2_at_zero = V2(idx_zero);
    optimal_action_at_zero = policy(idx_zero);

    fprintf('Sample Outputs at S = 0:\n');
    fprintf('V1(S=0): %.4f (Action 1)\n', V1_at_zero);
    fprintf('V2(S=0): %.4f (Action 2)\n', V2_at_zero);
    if optimal_action_at_zero == 1
        fprintf('Optimal Action at S=0: Action 1\n');
    else
        fprintf('Optimal Action at S=0: Action 2\n');
    end

    % ==============================
    % 5. Data Summary
    % ==============================

    % Display the number of samples in each dataset
    num_action1 = size(St_action1,1);
    num_action2 = size(St_action2,1);
    fprintf('\nData Generation Summary:\n');
    fprintf('Number of (St, St+1) pairs with Action 1: %d\n', num_action1);
    fprintf('Number of (St, St+1) pairs with Action 2: %d\n', num_action2);

    % Optionally, save the datasets to workspace or files
    % Uncomment the following lines to save the datasets as variables in the workspace
    % assignin('base', 'Data_Action1', St_action1);
    % assignin('base', 'Data_Action2', St_action2);

    % Or save to .mat files
    % save('Data_Action1.mat', 'St_action1');
    % save('Data_Action2.mat', 'St_action2');
end

