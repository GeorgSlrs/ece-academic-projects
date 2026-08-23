function Machine_Learning_hw3_2_b()
    % Machine_Learning_hw3_2_b
    %
    % Modified so that the training explicitly uses the gradient descent:
    %
    %   theta_t = theta_{t-1} 
    %             - mu * sum_i [ R(Y_i) - omega(u(X_i, theta_{t-1})) ]
    %                       * rho(u(X_i, theta_{t-1}))
    %                       * grad w.r.t. theta of u(X_i, theta_{t-1}).
    %
    rng(0);  % For reproducibility

    %% =========================
    % 1. Numerical Computation
    % ==========================
    
    % Parameters for numerical approximation
    S_min = -10;
    S_max = 10;
    m = 1001;
    n = 1001;
    S_grid = linspace(S_min, S_max, m)'; 
    y_grid = linspace(S_min, S_max, n)'; 
    
    % Reward Function: R(y) = min{2, y^2}
    R = min(2, y_grid.^2);  
    
    % Create meshgrids for (S_j, y_i)
    [Y_grid_mat, X_grid_mat] = meshgrid(y_grid, S_grid); 

    % Means for each action
    mu1_matrix = 0.8 * X_grid_mat + 1.0;  % alpha=1
    mu2_matrix = -2.0 * ones(m, n);       % alpha=2
    sigma1 = 1.0;
    sigma2 = 1.0;

    % Compute CDFs using normcdf => H1, H2
    H1 = normcdf(Y_grid_mat, mu1_matrix, sigma1); 
    H2 = normcdf(Y_grid_mat, mu2_matrix, sigma2); 

    % Compute trapezoidal weights F1, F2
    F1 = zeros(m, n);
    F1(:,1) = 0.5 * H1(:,1);
    for i = 2:n-1
        F1(:,i) = 0.5 * (H1(:,i+1) - H1(:,i-1));
    end
    F1(:,n) = 0.5 * (H1(:,n) - H1(:,n-1));

    F2 = zeros(m, n);
    F2(:,1) = 0.5 * H2(:,1);
    for i = 2:n-1
        F2(:,i) = 0.5 * (H2(:,i+1) - H2(:,i-1));
    end
    F2(:,n) = 0.5 * (H2(:,n) - H2(:,n-1));

    % Construct vector G using average of R(y_i) and R(y_{i-1})
    G = zeros(n,1);
    G(1) = R(1);
    G(2:n) = (R(1:n-1) + R(2:n)) / 2;

    % Compute V1 and V2 as weighted sums
    V1 = F1 * G;  % [m x 1] => E[R | X=S, alpha=1]
    V2 = F2 * G;  % [m x 1] => E[R | X=S, alpha=2]

    % Determine optimal policy (numerical)
    [V_optimal, policy] = max([V1, V2], [], 2);

    %% =========================
    % 2. Data Generation
    % =========================
    N = 10000;  
    St_action1 = zeros(0,2);
    St_action2 = zeros(0,2);

    for t = 1:N
        St = randn();                      % S_t ~ N(0,1)
        alpha_t = randi([1,2]);            % Random action
        if alpha_t == 1
            St_plus1 = 0.8*St + 1.0 + randn();  % alpha=1
            St_action1 = [St_action1; St, St_plus1];
        else
            St_plus1 = -2.0 + randn();           % alpha=2
            St_action2 = [St_action2; St, St_plus1];
        end
    end

    %% =========================
    % 3. Data-Driven Approach
    % =========================
    % Train separate [A1] and [C1] models for V1 and V2

    % Neural Network Parameters
    hidden_size   = 100;
    learning_rate = 0.01;
    epochs        = 100;
    batch_size    = 32;

    % Activation Functions
    hidden_activation = @(x) tanh(x);
    hidden_activation_derivative = @(x) 1 - tanh(x).^2;

    % For [A1]: output is linear => no bounding
    output_activation_A1 = @(x) x;
    output_activation_derivative_A1 = @(x) ones(size(x));

    % For [C1]: output in [0,2] => 2 * sigmoid(x)
    sigmoid = @(x) 1./(1 + exp(-x));
    output_activation_C1 = @(x) 2 * sigmoid(x);
    output_activation_derivative_C1 = @(x) 2 * sigmoid(x).*(1 - sigmoid(x));

    % Initialize neural networks
    [W1_A1_V1, b1_A1_V1, W2_A1_V1, b2_A1_V1] = initializeWeights(hidden_size, 'linear');
    [W1_C1_V1, b1_C1_V1, W2_C1_V1, b2_C1_V1] = initializeWeights(hidden_size, 'bounded');
    [W1_A1_V2, b1_A1_V2, W2_A1_V2, b2_A1_V2] = initializeWeights(hidden_size, 'linear');
    [W1_C1_V2, b1_C1_V2, W2_C1_V2, b2_C1_V2] = initializeWeights(hidden_size, 'bounded');

    % Prepare training data
    X_train_A1_V1 = St_action1(:,1);
    Y_train_A1_V1 = St_action1(:,2);

    X_train_C1_V1 = St_action1(:,1);
    Y_train_C1_V1 = min(2, St_action1(:,2).^2);

    X_train_A1_V2 = St_action2(:,1);
    Y_train_A1_V2 = St_action2(:,2);

    X_train_C1_V2 = St_action2(:,1);
    Y_train_C1_V2 = min(2, St_action2(:,2).^2);

    fprintf('Training Neural Networks...\n');

    % Train [A1]_V1
    fprintf('Training [A1]_V1...\n');
    [W1_A1_V1, b1_A1_V1, W2_A1_V1, b2_A1_V1, cost_A1_V1] = ...
        train_network(X_train_A1_V1, Y_train_A1_V1, ...
                      W1_A1_V1, b1_A1_V1, W2_A1_V1, b2_A1_V1, ...
                      hidden_activation, hidden_activation_derivative, ...
                      output_activation_A1, output_activation_derivative_A1, ...
                      learning_rate, epochs, batch_size, '[A1]');

    % Train [C1]_V1
    fprintf('Training [C1]_V1...\n');
    [W1_C1_V1, b1_C1_V1, W2_C1_V1, b2_C1_V1, cost_C1_V1] = ...
        train_network(X_train_C1_V1, Y_train_C1_V1, ...
                      W1_C1_V1, b1_C1_V1, W2_C1_V1, b2_C1_V1, ...
                      hidden_activation, hidden_activation_derivative, ...
                      output_activation_C1, output_activation_derivative_C1, ...
                      learning_rate, epochs, batch_size, '[C1]');

    % Train [A1]_V2
    fprintf('Training [A1]_V2...\n');
    [W1_A1_V2, b1_A1_V2, W2_A1_V2, b2_A1_V2, cost_A1_V2] = ...
        train_network(X_train_A1_V2, Y_train_A1_V2, ...
                      W1_A1_V2, b1_A1_V2, W2_A1_V2, b2_A1_V2, ...
                      hidden_activation, hidden_activation_derivative, ...
                      output_activation_A1, output_activation_derivative_A1, ...
                      learning_rate, epochs, batch_size, '[A1]');

    % Train [C1]_V2
    fprintf('Training [C1]_V2...\n');
    [W1_C1_V2, b1_C1_V2, W2_C1_V2, b2_C1_V2, cost_C1_V2] = ...
        train_network(X_train_C1_V2, Y_train_C1_V2, ...
                      W1_C1_V2, b1_C1_V2, W2_C1_V2, b2_C1_V2, ...
                      hidden_activation, hidden_activation_derivative, ...
                      output_activation_C1, output_activation_derivative_C1, ...
                      learning_rate, epochs, batch_size, '[C1]');

    %% =========================
    % 4. Evaluation of Networks
    % =========================
    fprintf('Evaluating Neural Networks...\n');
    X_eval = S_grid;

    % Evaluate [A1] for V1, V2
    V1_pred_A1_V1 = evaluate_network(X_eval, W1_A1_V1, b1_A1_V1, W2_A1_V1, b2_A1_V1, ...
                                     hidden_activation, output_activation_A1);
    V1_pred_C1_V1 = evaluate_network(X_eval, W1_C1_V1, b1_C1_V1, W2_C1_V1, b2_C1_V1, ...
                                     hidden_activation, output_activation_C1);

    V2_pred_A1_V2 = evaluate_network(X_eval, W1_A1_V2, b1_A1_V2, W2_A1_V2, b2_A1_V2, ...
                                     hidden_activation, output_activation_A1);
    V2_pred_C1_V2 = evaluate_network(X_eval, W1_C1_V2, b1_C1_V2, W2_C1_V2, b2_C1_V2, ...
                                     hidden_activation, output_activation_C1);

    %% =========================
    % 5. Plotting Results
    % =========================
    figure('Name','V1: Numerical vs. [A1] vs. [C1]');
    plot(S_grid, V1, 'k-', 'LineWidth',2, 'DisplayName','Numerical V1'); hold on;
    plot(S_grid, V1_pred_A1_V1, 'r--', 'LineWidth',2, 'DisplayName','[A1] V1');
    plot(S_grid, V1_pred_C1_V1, 'b-.', 'LineWidth',2, 'DisplayName','[C1] V1');
    xlabel('State S'); ylabel('V1(S)');
    legend('show','Location','Best'); grid on; hold off;

    figure('Name','V2: Numerical vs. [A1] vs. [C1]');
    plot(S_grid, V2, 'k-', 'LineWidth',2, 'DisplayName','Numerical V2'); hold on;
    plot(S_grid, V2_pred_A1_V2, 'r--', 'LineWidth',2, 'DisplayName','[A1] V2');
    plot(S_grid, V2_pred_C1_V2, 'b-.', 'LineWidth',2, 'DisplayName','[C1] V2');
    xlabel('State S'); ylabel('V2(S)');
    legend('show','Location','Best'); grid on; hold off;

    figure('Name','Convergence V1');
    plot(1:epochs, cost_A1_V1, 'r-', 'LineWidth',1.5, 'DisplayName','[A1] V1');
    hold on;
    plot(1:epochs, cost_C1_V1, 'b-.', 'LineWidth',1.5, 'DisplayName','[C1] V1');
    xlabel('Epoch'); ylabel('Cost'); legend('show'); grid on; hold off;

    figure('Name','Convergence V2');
    plot(1:epochs, cost_A1_V2, 'r-', 'LineWidth',1.5, 'DisplayName','[A1] V2');
    hold on;
    plot(1:epochs, cost_C1_V2, 'b-.', 'LineWidth',1.5, 'DisplayName','[C1] V2');
    xlabel('Epoch'); ylabel('Cost'); legend('show'); grid on; hold off;

    %% =========================
    % 6. Derive and Visualize Optimal Policy
    % =========================
    % 1) "Numerical" policy is in 'policy'
    % 2) "Data-driven [A1]" policy
    % 3) "Data-driven [C1]" policy

    % ----- 6.1: Compute data-driven policy using [A1] networks -----
    policy_data_driven_A1 = zeros(m,1);
    for j = 1:m
        if V1_pred_A1_V1(j) >= V2_pred_A1_V2(j)
            policy_data_driven_A1(j) = 1;
        else
            policy_data_driven_A1(j) = 2;
        end
    end

    % ----- 6.2: Compute data-driven policy using [C1] networks -----
    policy_data_driven_C1 = zeros(m,1);
    for j = 1:m
        if V1_pred_C1_V1(j) >= V2_pred_C1_V2(j)
            policy_data_driven_C1(j) = 1;
        else
            policy_data_driven_C1(j) = 2;
        end
    end

    % ----- 6.3: Plot numerical vs. data-driven policies side-by-side -----
    figure('Name','Optimal Policy Comparison');
    plot(S_grid, policy, 'k-', 'LineWidth',2, 'DisplayName','Numerical Policy'); hold on;
    plot(S_grid, policy_data_driven_A1, 'r--', 'LineWidth',2, 'DisplayName','[A1] Policy');
    plot(S_grid, policy_data_driven_C1, 'b-.', 'LineWidth',2, 'DisplayName','[C1] Policy');
    xlabel('State S'); ylabel('Optimal Action \alpha^*(S)');
    legend('show','Location','Best'); grid on; hold off;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Supporting Functions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [W1, b1, W2, b2] = initializeWeights(hidden_size, methodTag)
    input_size = 1;   % scalar input S
    output_size = 1;  % scalar output

    % Simple He-style initialization:
    W1 = randn(hidden_size, input_size) * sqrt(2 / input_size);
    b1 = zeros(hidden_size, 1);
    W2 = randn(output_size, hidden_size) * sqrt(2 / hidden_size);
    b2 = 0;
end


function [W1, b1, W2, b2, cost_history] = train_network(Xtrain, Ytrain, ...
                                                        W1, b1, W2, b2, ...
                                                        hidden_activation, hidden_activation_derivative, ...
                                                        output_activation, output_activation_derivative, ...
                                                        learning_rate, epochs, batch_size, methodTag)
    % Implementation of:
    % theta_t = theta_{t-1} 
    %           - mu * sum( R(Y_i) - omega(u(X_i, theta_{t-1})) ) * rho(u(X_i, theta_{t-1})) * grad_theta[u(X_i)]
    %
    % But in mini-batches. The "cost" here is the MSE-like or average error for monitoring.

    num_samples = length(Xtrain);
    num_batches = ceil(num_samples / batch_size);
    cost_history = zeros(epochs,1);

    for ep = 1:epochs
        % Shuffle indices
        perm = randperm(num_samples);
        X_shuffled = Xtrain(perm);
        Y_shuffled = Ytrain(perm);

        epoch_loss = 0;

        for ibatch = 1:num_batches
            start_idx = (ibatch-1)*batch_size + 1;
            end_idx   = min(ibatch*batch_size, num_samples);

            X_batch = X_shuffled(start_idx:end_idx)';  % [1 x batch_size]
            Y_batch = Y_shuffled(start_idx:end_idx)';  % [1 x batch_size]

            %------------- Forward Pass ----------------
            Z1 = W1 * X_batch + b1;                  % [hidden_size x batch_size]
            A1 = hidden_activation(Z1);              % hidden layer output

            Z2 = W2 * A1 + b2;                       % [1 x batch_size]
            A2 = output_activation(Z2);              % final output = omega(u)

            % For [A1], Y_batch = next-state
            % For [C1], Y_batch = min(2, next-state^2)
            target = Y_batch;  
            err = target - A2;  % [1 x batch_size]

            % dZ2_i = -err_i * rho(u_i)
            dZ2 = -err .* output_activation_derivative(Z2);  % [1 x batch_size]

            %------------- Backprop to Hidden Layer ------------
            dW2 = dZ2 * A1';                          % [1 x hidden_size]
            db2 = sum(dZ2, 2);                       % [1 x 1]

            dA1 = W2' * dZ2;                         % [hidden_size x batch_size]
            dZ1 = dA1 .* hidden_activation_derivative(Z1);  % elementwise

            dW1 = dZ1 * X_batch';                    % [hidden_size x 1]
            db1 = sum(dZ1, 2);                       % [hidden_size x 1]

            %------------- Gradient Descent Update ---------------
            W1 = W1 - (learning_rate / size(X_batch,2)) * dW1;
            b1 = b1 - (learning_rate / size(X_batch,2)) * db1;
            W2 = W2 - (learning_rate / size(X_batch,2)) * dW2;
            b2 = b2 - (learning_rate / size(X_batch,2)) * db2;

            % Accumulate MSE (just for logging)
            batch_loss = mean( err.^2 );
            epoch_loss = epoch_loss + batch_loss;
        end

        % Average loss across mini-batches
        cost_history(ep) = epoch_loss / num_batches;

        % Print progress every 10 epochs
        if mod(ep,10)==0
            fprintf('Epoch %d/%d, Cost: %.4f\n', ep, epochs, cost_history(ep));
        end
    end
end


function output = evaluate_network(Xvals, W1, b1, W2, b2, hidden_activation, output_activation)
    % Evaluate entire dataset Xvals (size [m x 1])
    Z1 = W1 * Xvals' + b1;       % [hidden_size x m]
    A1 = hidden_activation(Z1);
    Z2 = W2 * A1 + b2;           % [1 x m]
    A2 = output_activation(Z2);  % [1 x m]
    output = A2';                % [m x 1]
end
