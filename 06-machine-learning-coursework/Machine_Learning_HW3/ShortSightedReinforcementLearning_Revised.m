function ShortSightedReinforcementLearning_Corrected_v3()
    % ShortSightedReinforcementLearning_Corrected_v3
    %
    % This script performs short-sighted RL for the MDP with:
    % alpha=1 => S_{t+1}=0.8*S_t+1+N(0,1),
    % alpha=2 => S_{t+1}=-2+N(0,1),
    % reward = min(2,S^2).
    %
    % Steps:
    %   1) Numerical computation of V1(s),V2(s) via trapezoid.
    %   2) Data generation (S_t, R_{t+1}) for alpha=1,2.
    %   3) Train four shallow nets: [A1],[C1] for alpha=1, alpha=2.
    %   4) Compare numerical vs. data-driven results.
    %   5) Plot short-sighted policies: numeric vs. data-driven[A1], [C1].
    %   6) Plot cost (MSE) convergence.

    clc; close all; rng('default'); rng(1);

    %% =========================
    %  1. Numerical Computation
    % =========================
    S_min = -10;
    S_max = 10;
    m = 1001;                      % # of grid points for S
    n = 1001;                      % # of grid points for next-state y
    S_grid = linspace(S_min, S_max, m)';  
    y_grid = linspace(S_min, S_max, n)';  

    % Reward R(y) = min(2, y^2).  Always in [0, 2].
    Rvals = min(2, y_grid.^2);

    % We'll form the transition cdfs for alpha=1, alpha=2
    [Y_grid_mat, X_grid_mat] = meshgrid(y_grid, S_grid);
    mu1_matrix = 0.8 .* X_grid_mat + 1.0;  % alpha=1
    mu2_matrix = -2.0 * ones(m, n);       % alpha=2
    sigma1 = 1.0;  sigma2 = 1.0;

    % Normcdf => H1, H2
    H1 = normcdf(Y_grid_mat, mu1_matrix, sigma1);
    H2 = normcdf(Y_grid_mat, mu2_matrix, sigma2);

    % Trapezoid rule for the integrals => F1, F2
    F1 = zeros(m,n);
    F2 = zeros(m,n);

    F1(:,1) = 0.5 * H1(:,1);
    F1(:,2:n) = 0.5 * ( H1(:,2:n) - H1(:,1:n-1) );
    F2(:,1) = 0.5 * H2(:,1);
    F2(:,2:n) = 0.5 * ( H2(:,2:n) - H2(:,1:n-1) );

    % Vector G via average of R for trapezoid
    G = zeros(n,1);
    G(1) = Rvals(1);
    for k=2:n
        G(k) = 0.5 * ( Rvals(k) + Rvals(k-1) );
    end

    % Now V1, V2
    V1 = F1 * G;   % [m x n]*[n x 1] => [m x 1]
    V2 = F2 * G;   % [m x 1]

    % Numerical optimal policy
    [~, policy_num] = max( [V1, V2], [], 2 );  % 1 if V1>=V2, else 2

    %% =========================
    %  2. Data Generation
    % =========================
    N = 1000;
    St_action1 = [];    % (S_t, R_{t+1})
    St_action2 = [];    % (S_t, R_{t+1})

    for t=1:N
        S_t  = randn();           % current state ~ N(0,1)
        alpha_t = randi([1,2]);   % random action in {1,2}

        if alpha_t == 1
            S_tp1 = 0.8*S_t + 1.0 + randn();   % alpha=1
            R_tp1 = min(2, S_tp1^2);
            St_action1 = [St_action1; S_t, R_tp1];
        else
            S_tp1 = -2.0 + randn();            % alpha=2
            R_tp1 = min(2, S_tp1^2);
            St_action2 = [St_action2; S_t, R_tp1];
        end
    end

    %% ================================================================
    %  3. Train Four Shallow Networks: alpha=1 => [A1] & [C1], alpha=2 => [A1] & [C1]
    %% ================================================================

    % Common network hyperparams
    hidden_size   = 100; 
    learning_rate = 0.01;
    epochs        = 100;  
    batch_size    = 32;

    % Data for alpha=1
    X_train_1 = St_action1(:,1);    % S_t
    Y_train_1 = St_action1(:,2);    % R_{t+1}

    % Data for alpha=2
    X_train_2 = St_action2(:,1); 
    Y_train_2 = St_action2(:,2);

    % Initialize cost histories
    cost_history_1A1 = zeros(epochs,1);  % alpha=1, method=[A1]
    cost_history_1C1 = zeros(epochs,1);  % alpha=1, method=[C1]
    cost_history_2A1 = zeros(epochs,1);  % alpha=2, method=[A1]
    cost_history_2C1 = zeros(epochs,1);  % alpha=2, method=[C1]

    rng(1);  % reproducible init
    % alpha=1, [A1]
    W1_1A1 = 0.01*randn(hidden_size,1);
    b1_1A1 = zeros(hidden_size,1);
    W2_1A1 = 0.01*randn(1,hidden_size);
    b2_1A1 = 0;

    % alpha=1, [C1]
    W1_1C1 = 0.01*randn(hidden_size,1);
    b1_1C1 = zeros(hidden_size,1);
    W2_1C1 = 0.01*randn(1,hidden_size);
    b2_1C1 = 0;

    % alpha=2, [A1]
    W1_2A1 = 0.01*randn(hidden_size,1);
    b1_2A1 = zeros(hidden_size,1);
    W2_2A1 = 0.01*randn(1,hidden_size);
    b2_2A1 = 0;

    % alpha=2, [C1]
    W1_2C1 = 0.01*randn(hidden_size,1);
    b1_2C1 = zeros(hidden_size,1);
    W2_2C1 = 0.01*randn(1,hidden_size);
    b2_2C1 = 0;

    %% === Train alpha=1, [A1] ===
    fprintf('\n--- Training: alpha=1, [A1] ---\n');
    for ep=1:epochs
        perm_ = randperm(length(X_train_1));
        for b_i=1:ceil(length(X_train_1)/batch_size)
            idx_b = perm_((b_i-1)*batch_size+1 : min(b_i*batch_size,length(X_train_1)));
            Xb = X_train_1(idx_b)';  % [1 x batch_size]
            Yb = Y_train_1(idx_b)';  % [1 x batch_size]

            [uVals, Zhid] = forwardPass_A1(Xb, W1_1A1, b1_1A1, W2_1A1, b2_1A1);
            % [A1]: omega(z)=z => dMSE/dz = (z - y).
            diff_ = (uVals - Yb);   % [1 x batch_size]
            
            [dW1, db1, dW2, db2] = backwardPass_A1(Xb, Zhid, W2_1A1, diff_);
            W1_1A1 = W1_1A1 - learning_rate*dW1;
            b1_1A1 = b1_1A1 - learning_rate*db1;
            W2_1A1 = W2_1A1 - learning_rate*dW2;
            b2_1A1 = b2_1A1 - learning_rate*db2;
        end
        [uAll, ~] = forwardPass_A1(X_train_1', W1_1A1, b1_1A1, W2_1A1, b2_1A1);
        cost_history_1A1(ep) = mean( (uAll - Y_train_1').^2 );
        if mod(ep,10)==0
            fprintf('ep=%d, cost=%.4f\n', ep, cost_history_1A1(ep));
        end
    end

    %% === Train alpha=1, [C1] ===
    fprintf('\n--- Training: alpha=1, [C1] ---\n');
    for ep=1:epochs
        perm_ = randperm(length(X_train_1));
        for b_i=1:ceil(length(X_train_1)/batch_size)
            idx_b = perm_((b_i-1)*batch_size+1 : min(b_i*batch_size,length(X_train_1)));
            Xb = X_train_1(idx_b)'; 
            Yb = Y_train_1(idx_b)'; 

            [uVals, Zhid] = forwardPass_C1(Xb, W1_1C1, b1_1C1, W2_1C1, b2_1C1);
            [omega_u, rho_u] = transforms_C1_v3(uVals);  % see updated transforms
            % derivative for MSE => (y - omega_u)* (d/dz(omega_u)) = (Yb - omega_u)* rho_u
            diff_ = (Yb - omega_u).* rho_u;  
            
            [dW1, db1, dW2, db2] = backwardPass_C1(Xb, Zhid, W2_1C1, diff_);
            W1_1C1 = W1_1C1 - learning_rate*dW1;
            b1_1C1 = b1_1C1 - learning_rate*db1;
            W2_1C1 = W2_1C1 - learning_rate*dW2;
            b2_1C1 = b2_1C1 - learning_rate*db2;
        end
        [uAll, ~] = forwardPass_C1(X_train_1', W1_1C1, b1_1C1, W2_1C1, b2_1C1);
        [omegaAll, ~] = transforms_C1_v3(uAll);
        cost_history_1C1(ep) = mean( (omegaAll - Y_train_1').^2 );
    end

    %% === Train alpha=2, [A1] ===
    fprintf('\n--- Training: alpha=2, [A1] ---\n');
    for ep=1:epochs
        perm_ = randperm(length(X_train_2));
        for b_i=1:ceil(length(X_train_2)/batch_size)
            idx_b = perm_((b_i-1)*batch_size+1 : min(b_i*batch_size,length(X_train_2)));
            Xb = X_train_2(idx_b)';  
            Yb = Y_train_2(idx_b)';  

            [uVals, Zhid] = forwardPass_A1(Xb, W1_2A1, b1_2A1, W2_2A1, b2_2A1);
            diff_ = (uVals - Yb); 
            
            [dW1, db1, dW2, db2] = backwardPass_A1(Xb, Zhid, W2_2A1, diff_);
            W1_2A1 = W1_2A1 - learning_rate*dW1;
            b1_2A1 = b1_2A1 - learning_rate*db1;
            W2_2A1 = W2_2A1 - learning_rate*dW2;
            b2_2A1 = b2_2A1 - learning_rate*db2;
        end
        [uAll, ~] = forwardPass_A1(X_train_2', W1_2A1, b1_2A1, W2_2A1, b2_2A1);
        cost_history_2A1(ep) = mean( (uAll - Y_train_2').^2 );
    end

    %% === Train alpha=2, [C1] ===
    fprintf('\n--- Training: alpha=2, [C1] ---\n');
    for ep=1:epochs
        perm_ = randperm(length(X_train_2));
        for b_i=1:ceil(length(X_train_2)/batch_size)
            idx_b = perm_((b_i-1)*batch_size+1 : min(b_i*batch_size,length(X_train_2)));
            Xb = X_train_2(idx_b)'; 
            Yb = Y_train_2(idx_b)'; 

            [uVals, Zhid] = forwardPass_C1(Xb, W1_2C1, b1_2C1, W2_2C1, b2_2C1);
            [omega_u, rho_u] = transforms_C1_v3(uVals);
            diff_ = (Yb - omega_u).* rho_u; 

            [dW1, db1, dW2, db2] = backwardPass_C1(Xb, Zhid, W2_2C1, diff_);
            W1_2C1 = W1_2C1 - learning_rate*dW1;
            b1_2C1 = b1_2C1 - learning_rate*db1;
            W2_2C1 = W2_2C1 - learning_rate*dW2;
            b2_2C1 = b2_2C1 - learning_rate*db2;
        end
        [uAll, ~] = forwardPass_C1(X_train_2', W1_2C1, b1_2C1, W2_2C1, b2_2C1);
        [omegaAll, ~] = transforms_C1_v3(uAll);
        cost_history_2C1(ep) = mean( (omegaAll - Y_train_2').^2 );
    end


    %% ===============================================
    %  4. Evaluate the 4 networks on the S_grid
    %% ===============================================
    % alpha=1
    y_1A1 = evaluateNetwork_A1(W1_1A1, b1_1A1, W2_1A1, b2_1A1, S_grid);
    y_1C1 = evaluateNetwork_C1_v3(W1_1C1, b1_1C1, W2_1C1, b2_1C1, S_grid);

    % alpha=2
    y_2A1 = evaluateNetwork_A1(W1_2A1, b1_2A1, W2_2A1, b2_2A1, S_grid);
    y_2C1 = evaluateNetwork_C1_v3(W1_2C1, b1_2C1, W2_2C1, b2_2C1, S_grid);

    %% ===============================================
    %  5. Form data-driven policies
    %% ===============================================
    policy_dataA1 = zeros(m,1); 
    policy_dataC1 = zeros(m,1);
    for j=1:m
       if y_1A1(j) >= y_2A1(j)
           policy_dataA1(j) = 1;
       else
           policy_dataA1(j) = 2;
       end
       if y_1C1(j) >= y_2C1(j)
           policy_dataC1(j) = 1;
       else
           policy_dataC1(j) = 2;
       end
    end

    %% ===============================================
    %  6. PLOTS & COMPARISONS
    %% ===============================================

    % --- Figure 1: Policy: numerical vs data-driven(A1) vs data-driven(C1) ---
    figure('Name','Policy Comparison','NumberTitle','off');
    hold on; grid on;
    plot(S_grid, policy_num, 'k-','LineWidth',2, 'DisplayName','Numerical');
    plot(S_grid, policy_dataA1,'r--','LineWidth',2,'DisplayName','Data-Driven [A1]');
    plot(S_grid, policy_dataC1,'b:','LineWidth',2,'DisplayName','Data-Driven [C1]');
    xlabel('State S'); ylabel('Action');
    legend('Location','Best');
    title('Optimal Policy Comparison');
    xlim([S_min,S_max]); ylim([0.5,2.5]);
    hold off;

    % --- Figure 2: Convergence (MSE) for the 4 networks ---
    figure('Name','Convergence Curves','NumberTitle','off');
    hold on; grid on;
    plot(1:epochs, cost_history_1A1,'r-','LineWidth',1.5,'DisplayName','alpha=1 [A1]');
    plot(1:epochs, cost_history_1C1,'r--','LineWidth',1.5,'DisplayName','alpha=1 [C1]');
    plot(1:epochs, cost_history_2A1,'b-','LineWidth',1.5,'DisplayName','alpha=2 [A1]');
    plot(1:epochs, cost_history_2C1,'b--','LineWidth',1.5,'DisplayName','alpha=2 [C1]');
    legend('show','Location','Best');
    xlabel('Epoch'); ylabel('Cost (MSE)');
    title('Convergence for All Networks');
    hold off;

    % --- Figure 3: v1(S) from numerical vs. A1 vs. C1 ---
    figure('Name','v1(S) Comparison','NumberTitle','off');
    hold on; grid on;
    plot(S_grid, V1, 'k-', 'LineWidth',2, 'DisplayName','Numerical V1');
    plot(S_grid, y_1A1, 'r--','LineWidth',2,'DisplayName','[A1]');
    plot(S_grid, y_1C1, 'b:','LineWidth',2,'DisplayName','[C1]');
    xlabel('State S'); ylabel('v1(S)');
    legend('Location','Best');
    title('v1(S): Numerical vs. Data-Driven');
    xlim([S_min,S_max]);
    hold off;

    % --- Figure 4: v2(S) from numerical vs. A1 vs. C1 ---
    figure('Name','v2(S) Comparison','NumberTitle','off');
    hold on; grid on;
    plot(S_grid, V2, 'k-', 'LineWidth',2, 'DisplayName','Numerical V2');
    plot(S_grid, y_2A1, 'r--','LineWidth',2,'DisplayName','[A1]');
    plot(S_grid, y_2C1, 'b:','LineWidth',2,'DisplayName','[C1]');
    xlabel('State S'); ylabel('v2(S)');
    legend('Location','Best');
    title('v2(S): Numerical vs. Data-Driven');
    xlim([S_min,S_max]);
    hold off;

    % Print a small check around S=0:
    [~, idx0] = min(abs(S_grid));
    fprintf('\nAt S=0:\n');
    fprintf('  Numerical => V1(0)=%.4f, V2(0)=%.4f, policy=%d\n', ...
        V1(idx0), V2(idx0), policy_num(idx0));
    fprintf('  Data-driven[A1] => v1=%.4f, v2=%.4f, policy=%d\n', ...
        y_1A1(idx0), y_2A1(idx0), policy_dataA1(idx0));
    fprintf('  Data-driven[C1] => v1=%.4f, v2=%.4f, policy=%d\n', ...
        y_1C1(idx0), y_2C1(idx0), policy_dataC1(idx0));
    fprintf('\nDone.\n');
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%              HELPER FUNCTIONS [A1]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [uVals, Z1] = forwardPass_A1(Xbatch, W1, b1, W2, b2)
    % forward pass with identity output (no transform)
    Z1_ = W1*Xbatch + b1;         % [hidden_size x batch_size]
    A1_ = tanh(Z1_);
    uVals = W2*A1_ + b2;          % [1 x batch_size]
    Z1 = A1_;  % store for backprop
end

function [dW1, db1, dW2, db2] = backwardPass_A1(Xbatch, Z1, W2, dLdu)
    mb = size(Xbatch,2);
    dW2 = (dLdu * Z1') / mb;       % [1 x hidden_size]
    db2 = mean(dLdu,2);           % [1 x 1]
    dA1 = W2' * dLdu;             % [hidden_size x batch_size]
    dZ1 = dA1 .* (1 - Z1.^2);     % derivative of tanh
    dW1 = (dZ1 * Xbatch') / mb;   % [hidden_size x 1]
    db1 = mean(dZ1,2);
end

function ypred = evaluateNetwork_A1(W1,b1,W2,b2, Xvals)
    % Evaluate on a vector Xvals
    N_ = length(Xvals);
    ypred = zeros(N_,1);
    for j=1:N_
        xj = Xvals(j);
        Z1_ = W1*xj + b1;  
        A1_ = tanh(Z1_);
        u_  = W2*A1_ + b2; 
        ypred(j) = u_;
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%              HELPER FUNCTIONS [C1] (with [a=0,b=2] logistic form)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [uVals, Z1] = forwardPass_C1(Xbatch, W1, b1, W2, b2)
    Z1_ = W1*Xbatch + b1;
    A1_ = tanh(Z1_);
    uVals = W2*A1_ + b2;  
    Z1 = A1_;
end

function [omega_z, rho_z] = transforms_C1_v3(z)
    % [C1]:  omega(z) = (a/(1+e^z)) + b*e^z/(1+e^z)
    %        with a=0, b=2 => omega(z) = 2* e^z/(1 + e^z)
    %        and  rho(z)  = - e^z/(1 + e^z)
    ez = exp(z);
    omega_z = 2 .* ez ./ (1 + ez);    % range in [0,2]
    rho_z   = - ez ./ (1 + ez);       % negative logistic
end

function [dW1, db1, dW2, db2] = backwardPass_C1(Xbatch, Z1, W2, dLdu)
    mb = size(Xbatch,2);
    dW2 = (dLdu * Z1') / mb;
    db2 = mean(dLdu,2);
    dA1 = W2' * dLdu;
    dZ1 = dA1 .* (1 - Z1.^2);   % derivative of tanh
    dW1 = (dZ1 * Xbatch')/mb;
    db1 = mean(dZ1,2);
end

function ypred = evaluateNetwork_C1_v3(W1,b1,W2,b2, Xvals)
    % Evaluate with logistic transform in [0,2].
    N_ = length(Xvals);
    ypred = zeros(N_,1);
    for j=1:N_
        xj = Xvals(j);
        Z1_ = W1*xj + b1;  
        A1_ = tanh(Z1_);
        u_  = W2*A1_ + b2; 
        [omega_u, ~] = transforms_C1_v3(u_);
        ypred(j) = omega_u;
    end
end



