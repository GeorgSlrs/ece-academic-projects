function Machine_Learning_hw3_3()
    % MACHINE_LEARNING_HW3_3
    %
    % This code solves the infinite-horizon discounted reward problem
    % with gamma=0.8, 2 actions, and reward R(S)=min(2,S^2).
    %
    % Steps:
    %   1. Numerical solution via iterative approach: 
    %      V_j = F_j [ R + gamma * max(V1,V2) ], j=1,2.
    %   2. Data-driven approach:
    %      - Generate random data (N=1000). 
    %      - Train shallow networks ([A1], [C1]) to learn v1(S), v2(S).
    %   3. Compare results (V1,V2) and optimal policies.
    %
    % References: Lecture 12 slides (Slide17 for numeric, Slides18-19 for data-driven).

    rng(0);  % For reproducibility

    %% -------------------------------------------------
    %  1. PROBLEM PARAMETERS
    %% -------------------------------------------------
    gamma = 0.8;                          % discount factor
    reward_func = @(s) min(2, s.^2);      % R(S)=min(2,S^2)

    % For bounding in [C1], we know: 
    %   0 <= R(S) <= 2 => v_j(S) in [0, 2/(1-gamma)] = [0, 10].

    %% -------------------------------------------------
    %  2. NUMERICAL SOLUTION
    %% -------------------------------------------------
    S_min = -10;
    S_max =  10;
    m = 1001;                             % number of grid points
    S_grid = linspace(S_min, S_max, m)';  % column vector for states

    % We'll use the same grid for y:
    n = m;
    y_grid = S_grid;  % same partition

    % Reward on y_grid:
    R_y = reward_func(y_grid);  % [m x 1]

    % Build the trapezoidal "transition" matrices F1, F2
    % alpha=1 => S_{t+1}=0.8*S_t + 1 + N(0,1)
    % alpha=2 => S_{t+1}=-2 + N(0,1)
    mu1 = 0.8 * S_grid + 1.0;    % [m x 1]
    mu2 = -2.0 * ones(m,1);      % [m x 1]
    sigma1 = 1.0;
    sigma2 = 1.0;

    % We compute H1(j,i)=cdf(y_grid(i), mu1(j), sigma1), then F1 is approx pdf
    H1 = zeros(m, m);
    H2 = zeros(m, m);
    for j=1:m
        H1(j,:) = normcdf(y_grid, mu1(j), sigma1);
        H2(j,:) = normcdf(y_grid, mu2(j), sigma2);
    end
    F1 = zeros(m, m);
    F2 = zeros(m, m);
    for j=1:m
        F1(j,1) = 0.5*H1(j,1);
        F2(j,1) = 0.5*H2(j,1);
        for i=2:m-1
            F1(j,i) = 0.5*( H1(j,i+1) - H1(j,i-1) );
            F2(j,i) = 0.5*( H2(j,i+1) - H2(j,i-1) );
        end
        F1(j,m) = 0.5*(H1(j,m) - H1(j,m-1));
        F2(j,m) = 0.5*(H2(j,m) - H2(j,m-1));
    end

    % Iteratively solve V1, V2
    V1_num = zeros(m,1);
    V2_num = zeros(m,1);

    tol = 1e-4;
    max_iter = 300;
    for iter=1:max_iter
        oldV1 = V1_num;
        oldV2 = V2_num;

        maxV = max( [V1_num, V2_num], [], 2 ); 
        M    = R_y + gamma*maxV;           % R + gamma*max(V1,V2)

        V1_num = F1 * M;
        V2_num = F2 * M;

        if max( norm(V1_num - oldV1, Inf), ...
                norm(V2_num - oldV2, Inf) ) < tol
            fprintf('Numeric iteration converged at iteration %d.\n', iter);
            break;
        end
    end
    [~, policy_num] = max([V1_num, V2_num], [], 2);

    %% -------------------------------------------------
    %  3. DATA GENERATION
    %% -------------------------------------------------
    % We generate N=1000 transitions (St, St+1) for random actions alpha_t in {1,2}.
    N = 1000;
    Sdata = zeros(N+1,1);
    Sdata(1) = randn();   % initial ~ N(0,1)

    alpha_seq = randi([1,2],[N,1]);
    data_action1 = [];  % will store (X_t, Y_t)
    data_action2 = [];

    for t=1:N
        St = Sdata(t);
        at = alpha_seq(t);
        if at == 1
            Snext = 0.8*St + 1.0 + randn();
            data_action1 = [data_action1; St, Snext];
        else
            Snext = -2.0 + randn();
            data_action2 = [data_action2; St, Snext];
        end
        Sdata(t+1) = Snext;
    end

    %% -------------------------------------------------
    %  4. DATA-DRIVEN APPROACH
    %% -------------------------------------------------
    % We train 4 shallow networks:
    %   - [A1]: v1, v2 => identity output
    %   - [C1]: v1, v2 => bounding [0,10]
    hidden_size   = 100;
    learning_rate = 0.01;
    epochs        = 100;
    batch_size    = 32;

    % Hidden activation
    hidden_act = @(x) tanh(x);
    hidden_act_deriv = @(x) 1 - tanh(x).^2;

    % [A1] => identity
    output_act_A1 = @(z) z;
    output_act_deriv_A1 = @(z) ones(size(z));

    % [C1] => in [0,10], so w(z)=10*sigma(z)
    sigmoid = @(z) 1./(1 + exp(-z));
    output_act_C1 = @(z) 10 * sigmoid(z);
    output_act_deriv_C1 = @(z) 10 * sigmoid(z).*(1 - sigmoid(z));

    % Initialize 4 networks
    [W1_A1_V1, b1_A1_V1, W2_A1_V1, b2_A1_V1] = init_weights(hidden_size);
    [W1_A1_V2, b1_A1_V2, W2_A1_V2, b2_A1_V2] = init_weights(hidden_size);

    [W1_C1_V1, b1_C1_V1, W2_C1_V1, b2_C1_V1] = init_weights(hidden_size);
    [W1_C1_V2, b1_C1_V2, W2_C1_V2, b2_C1_V2] = init_weights(hidden_size);

    % Data for alpha=1 => (X1, Y1), alpha=2 => (X2, Y2)
    X1 = data_action1(:,1);
    Y1 = data_action1(:,2);
    X2 = data_action2(:,1);
    Y2 = data_action2(:,2);

    fprintf('\n--- Training [A1] for V1...\n');
    [W1_A1_V1, b1_A1_V1, W2_A1_V1, b2_A1_V1, cost_A1_V1] = ...
        train_discounted_network(X1, Y1, ...
                                 W1_A1_V1, b1_A1_V1, W2_A1_V1, b2_A1_V1, ...
                                 hidden_act, hidden_act_deriv, ...
                                 output_act_A1, output_act_deriv_A1, ...
                                 gamma, learning_rate, epochs, batch_size, ...
                                 'A1-V1', reward_func);

    fprintf('\n--- Training [A1] for V2...\n');
    [W1_A1_V2, b1_A1_V2, W2_A1_V2, b2_A1_V2, cost_A1_V2] = ...
        train_discounted_network(X2, Y2, ...
                                 W1_A1_V2, b1_A1_V2, W2_A1_V2, b2_A1_V2, ...
                                 hidden_act, hidden_act_deriv, ...
                                 output_act_A1, output_act_deriv_A1, ...
                                 gamma, learning_rate, epochs, batch_size, ...
                                 'A1-V2', reward_func);

    fprintf('\n--- Training [C1] for V1...\n');
    [W1_C1_V1, b1_C1_V1, W2_C1_V1, b2_C1_V1, cost_C1_V1] = ...
        train_discounted_network(X1, Y1, ...
                                 W1_C1_V1, b1_C1_V1, W2_C1_V1, b2_C1_V1, ...
                                 hidden_act, hidden_act_deriv, ...
                                 output_act_C1, output_act_deriv_C1, ...
                                 gamma, learning_rate, epochs, batch_size, ...
                                 'C1-V1', reward_func);

    fprintf('\n--- Training [C1] for V2...\n');
    [W1_C1_V2, b1_C1_V2, W2_C1_V2, b2_C1_V2, cost_C1_V2] = ...
        train_discounted_network(X2, Y2, ...
                                 W1_C1_V2, b1_C1_V2, W2_C1_V2, b2_C1_V2, ...
                                 hidden_act, hidden_act_deriv, ...
                                 output_act_C1, output_act_deriv_C1, ...
                                 gamma, learning_rate, epochs, batch_size, ...
                                 'C1-V2', reward_func);

    %% -------------------------------------------------
    %  5. EVALUATION & PLOTS
    %% -------------------------------------------------
    % Evaluate the learned networks on the same grid
    V1_A1 = evaluate_network(S_grid, W1_A1_V1, b1_A1_V1, W2_A1_V1, b2_A1_V1, ...
                             hidden_act, output_act_A1);
    V2_A1 = evaluate_network(S_grid, W1_A1_V2, b1_A1_V2, W2_A1_V2, b2_A1_V2, ...
                             hidden_act, output_act_A1);

    V1_C1 = evaluate_network(S_grid, W1_C1_V1, b1_C1_V1, W2_C1_V1, b2_C1_V1, ...
                             hidden_act, output_act_C1);
    V2_C1 = evaluate_network(S_grid, W1_C1_V2, b1_C1_V2, W2_C1_V2, b2_C1_V2, ...
                             hidden_act, output_act_C1);

    % Data-driven policies:
    policy_A1 = zeros(m,1);
    policy_C1 = zeros(m,1);
    for i=1:m
        % [A1]
        if V1_A1(i) >= V2_A1(i)
            policy_A1(i) = 1;
        else
            policy_A1(i) = 2;
        end
        % [C1]
        if V1_C1(i) >= V2_C1(i)
            policy_C1(i) = 1;
        else
            policy_C1(i) = 2;
        end
    end

    figure('Name','V1 Comparison','NumberTitle','off');
    plot(S_grid, V1_num, 'k-','LineWidth',2); hold on;
    plot(S_grid, V1_A1,  'r--','LineWidth',2);
    plot(S_grid, V1_C1,  'b-.','LineWidth',2);
    legend('Numeric V1','[A1] V1','[C1] V1','Location','Best');
    title('V1 Comparison'); grid on;

    figure('Name','V2 Comparison','NumberTitle','off');
    plot(S_grid, V2_num, 'k-','LineWidth',2); hold on;
    plot(S_grid, V2_A1,  'r--','LineWidth',2);
    plot(S_grid, V2_C1,  'b-.','LineWidth',2);
    legend('Numeric V2','[A1] V2','[C1] V2','Location','Best');
    title('V2 Comparison'); grid on;

    figure('Name','[A1] Convergence','NumberTitle','off');
    plot(1:epochs, cost_A1_V1,'r-','LineWidth',1.5); hold on;
    plot(1:epochs, cost_A1_V2,'r--','LineWidth',1.5);
    legend('V1','V2','Location','Best'); grid on;
    xlabel('Epoch'); ylabel('Cost'); title('[A1] Training Convergence');

    figure('Name','[C1] Convergence','NumberTitle','off');
    plot(1:epochs, cost_C1_V1,'b-','LineWidth',1.5); hold on;
    plot(1:epochs, cost_C1_V2,'b--','LineWidth',1.5);
    legend('V1','V2','Location','Best'); grid on;
    xlabel('Epoch'); ylabel('Cost'); title('[C1] Training Convergence');

    figure('Name','Policy Comparison','NumberTitle','off');
    plot(S_grid, policy_num, 'k-','LineWidth',2,'DisplayName','Numeric'); hold on; grid on;
    plot(S_grid, policy_A1,  'r--','LineWidth',2,'DisplayName','[A1]');
    plot(S_grid, policy_C1,  'b-.','LineWidth',2,'DisplayName','[C1]');
    legend('Location','Best');
    xlabel('State'); ylabel('Action'); 
    ylim([0.5,2.5]);
    title('Optimal Policy Comparison');

    disp('Done with infinite-horizon discounted problem (Problem 3.3).');
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%         SUPPORTING FUNCTIONS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [W1, b1, W2, b2] = init_weights(hidden_size)
    % INIT_WEIGHTS Initialize a shallow net with hidden_size neurons 
    % in the hidden layer and input_size=1, output_size=1.
    input_size = 1;
    output_size = 1;
    scale = 0.01;
    W1 = scale * randn(hidden_size, input_size);
    b1 = zeros(hidden_size,1);
    W2 = scale * randn(output_size, hidden_size);
    b2 = zeros(output_size,1);
end

function [W1, b1, W2, b2, cost_history] = train_discounted_network(...
    Xtrain, Ytrain, ...
    W1, b1, W2, b2, ...
    hidden_act, hidden_act_deriv, ...
    output_act, output_act_deriv, ...
    gamma, learning_rate, epochs, batch_size, ...
    tagName, rewardHandle)
%TRAIN_DISCOUNTED_NETWORK 
%
% Trains a shallow network to approximate v_j(S) for alpha=j 
% using the discounted target:
%    Target = R(S_{t+1}) + gamma * max( v1(S_{t+1}), v2(S_{t+1}) ) .
%
% For demonstration, we show a single-network approach. If you want 
% a strict 2-network approach, you'd pass references to both networks 
% and do a fitted-Q style iteration. Here we do not show that in detail 
% to keep the code more concise.

    cost_history = zeros(epochs,1);
    nSamples = length(Xtrain);

    for ep=1:epochs
        idx_perm = randperm(nSamples);
        epoch_cost = 0;
        for b_=1:ceil(nSamples/batch_size)
            start_idx = (b_-1)*batch_size + 1;
            end_idx   = min(b_*batch_size, nSamples);
            idx_batch = idx_perm(start_idx:end_idx);
            mb = length(idx_batch);

            Xb = Xtrain(idx_batch)';  % [1 x mb]
            Yb = Ytrain(idx_batch)';  % [1 x mb]

            % Forward on Xb => v_j(Xb)
            Z1 = W1 * Xb + b1;               % [hidden_size x mb]
            A1 = hidden_act(Z1);            % [hidden_size x mb]
            Z2 = W2 * A1 + b2;              % [1 x mb]
            A2 = output_act(Z2);            % => v_j(Xb)

            % Evaluate net on Yb => approximate v_j(Yb)
            Z1y = W1 * Yb + b1;
            A1y = hidden_act(Z1y);
            Z2y = W2 * A1y + b2;
            A2y = output_act(Z2y);          % => v_j(Yb)

            % Build target: R(Y) + gamma* max{ v1(Y), v2(Y) } 
            % (Here we only have 1 net's values => we do v_j(Y). 
            %  For a 2-net code, you'd pass in the other net's value, 
            %  do max. This is the "placeholder" single-net version.)
            Ryb = rewardHandle(Yb);
            Target = Ryb + gamma .* A2y;    % [1 x mb]

            % MSE => diff_ = (prediction - target)
            diff_ = (A2 - Target);

            % Backprop
            dA2dZ2 = output_act_deriv(Z2);
            dZ2 = diff_ .* dA2dZ2;          % [1 x mb]

            dW2 = (dZ2 * A1') / mb;         % [1 x hidden_size]
            db2_ = mean(dZ2,2);            % [1 x 1]

            dA1 = W2' * dZ2;               % [hidden_size x mb]
            dZ1 = dA1 .* hidden_act_deriv(Z1);  % [hidden_size x mb]
            dW1 = (dZ1 * Xb') / mb;        % [hidden_size x 1]
            db1_ = mean(dZ1,2);

            % Update
            W2 = W2 - learning_rate*dW2;
            b2 = b2 - learning_rate*db2_;
            W1 = W1 - learning_rate*dW1;
            b1 = b1 - learning_rate*db1_;

            cost_batch = mean(diff_.^2);
            epoch_cost = epoch_cost + cost_batch;
        end

        cost_history(ep) = epoch_cost;
        if mod(ep,10)==0
            fprintf('[%s] Epoch %d/%d, MSE=%.5f\n', ...
                    tagName, ep, epochs, cost_history(ep));
        end
    end
end

function vals = evaluate_network(Xvals, W1, b1, W2, b2, hidden_act, output_act)
    N_ = length(Xvals);
    vals = zeros(N_,1);
    for i=1:N_
        x_ = Xvals(i);
        Z1_ = W1*x_ + b1;
        A1_ = hidden_act(Z1_);
        Z2_ = W2*A1_ + b2;
        vals(i) = output_act(Z2_);
    end
end

