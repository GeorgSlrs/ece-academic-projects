function Machine_Learning_hw3_1_a_corrected()
    % MACHINE_LEARNING_HW3_1_A_CORRECTED
    %
    % 1) Generate N=500 synthetic data: Y=0.8*X + W,   X,W ~ N(0,1).
    % 2) Numerically approximate E[Y|X], E[clamp(Y)|X] with the trapezoid rule
    %    using your special formula:
    %      F_{j,1} = 0.5[H(y1)- H(y0)],
    %      F_{j,n} = 0.5[H(y_n)- H(y_{n-1})],
    %      F_{j,i} = 0.5[H(y_i)- H(y_{i-2})], i=2..n-1
    %    Then V = sum_i(F_i * G(y_i) ).
    %
    % 3) Train 4 neural nets using the EXACT gradient-descent update:
    %    theta <- theta 
    %            - mu * sum_{i=1}^N [ phi'(u_i) + g_i * psi'(u_i) ] * grad_theta[u_i]
    %
    %    - 2 nets for G1(Y)=Y => [A1], [A2]
    %    - 2 nets for G2(Y)=clamp(Y) => [A1], [C1]
    %
    % 4) Plot two final figures for E[Y|X], E[clamp(Y)|X],
    %    plus two extra figures for the cost vs. epochs (convergence curves).

    rng(0);  % For reproducibility

    %% (1) Generate synthetic data
    N = 500;
    X = randn(N,1);        % X ~ N(0,1)
    W = randn(N,1);        % W ~ N(0,1)
    Y = 0.8*X + W;         % Y = 0.8X + W

    % Define target functions
    G1 = Y;                         % Unbounded: G1(Y)=Y
    G2 = min(1, max(-1, Y));       % Bounded: clamp(Y) in [-1,1]

    % Normalize X
    X_mean = mean(X);
    X_std = std(X);
    X_normalized = (X - X_mean) / X_std;

    % Define grid for numerical approximation and evaluation
    x_min = floor(min(X_normalized));
    x_max = ceil(max(X_normalized));
    x_grid = linspace(x_min, x_max, 200)';

    %% (2) Numerical trapezoidal approximation
    [numG1, numG2] = trapezoid_conditional_expectation_corrected(x_grid);

    %% (3) Train 4 neural networks
    hiddenSize = 50;
    nEpochs    = 1500;
    lr         = 1e-2;  % Initial learning rate

    % Train networks for E[Y|X] => [A1], [A2]
    disp('--- Training netG1_A1 ---');
    [netG1_A1, costG1_A1] = trainNN_dataDriven_corrected(X_normalized, G1, ...
                                          hiddenSize, nEpochs, lr, 'A1');
    disp('--- Training netG1_A2 ---');
    [netG1_A2, costG1_A2] = trainNN_dataDriven_corrected(X_normalized, G1, ...
                                          hiddenSize, nEpochs, lr, 'A2');

    % Train networks for E[clamp(Y)|X] => [A1], [C1]
    disp('--- Training netG2_A1 ---');
    [netG2_A1, costG2_A1] = trainNN_dataDriven_corrected(X_normalized, G2, ...
                                          hiddenSize, nEpochs, lr, 'A1');
    disp('--- Training netG2_C1 ---');
    [netG2_C1, costG2_C1] = trainNN_dataDriven_corrected(X_normalized, G2, ...
                                          hiddenSize, nEpochs, lr, 'C1');

    %% (4) Evaluate each network on the grid
    yG1_A1 = evaluateNN_corrected(netG1_A1, x_grid);
    yG1_A2 = evaluateNN_corrected(netG1_A2, x_grid);
    yG2_A1 = evaluateNN_corrected(netG2_A1, x_grid);
    yG2_C1 = evaluateNN_corrected(netG2_C1, x_grid);

    %% (5) Plot E[Y|X]: trapezoidal, [A1], [A2]
    figure('Name','E[Y|X]: Trapezoid vs. [A1] vs. [A2]','NumberTitle','off');
    plot(x_grid, numG1, 'k-', 'LineWidth',2, 'DisplayName','Trapezoid'); hold on;
    plot(x_grid, yG1_A1, 'r--', 'LineWidth',2, 'DisplayName','[A1]');
    plot(x_grid, yG1_A2, 'b-.', 'LineWidth',2, 'DisplayName','[A2]');
    legend('show','Location','Best');
    xlabel('x'); ylabel('E[Y|X]');
    title('E[Y|X]: Trapezoid vs. [A1] vs. [A2]');
    grid on; hold off;

    %% (6) Plot E[clamp(Y)|X]: trapezoidal, [A1], [C1]
    figure('Name','E[clamp(Y)|X]: Trapezoid vs. [A1] vs. [C1]','NumberTitle','off');
    plot(x_grid, numG2, 'k-', 'LineWidth',2, 'DisplayName','Trapezoid'); hold on;
    plot(x_grid, yG2_A1, 'r--', 'LineWidth',2, 'DisplayName','[A1]');
    plot(x_grid, yG2_C1, 'b-.', 'LineWidth',2, 'DisplayName','[C1]');
    legend('show','Location','Best');
    xlabel('x'); ylabel('E[clamp(Y)|X]');
    title('E[clamp(Y)|X]: Trapezoid vs. [A1] vs. [C1]');
    grid on; hold off;

    %% (7) Plot Convergence Curves for G1=Y: [A1], [A2]
    figure('Name','Convergence Curves for G1=Y','NumberTitle','off');
    plot(1:nEpochs, costG1_A1, 'r-', 'LineWidth',1.5, 'DisplayName','[A1]'); hold on;
    plot(1:nEpochs, costG1_A2, 'b-', 'LineWidth',1.5, 'DisplayName','[A2]');
    legend('show','Location','Best');
    xlabel('Epoch'); ylabel('Cost');
    title('Convergence for G1=Y');
    grid on; hold off;

    %% (8) Plot Convergence Curves for G2=clamp(Y): [A1], [C1]
    figure('Name','Convergence Curves for G2=clamp(Y)','NumberTitle','off');
    plot(1:nEpochs, costG2_A1, 'r-', 'LineWidth',1.5, 'DisplayName','[A1]'); hold on;
    plot(1:nEpochs, costG2_C1, 'b-', 'LineWidth',1.5, 'DisplayName','[C1]');
    legend('show','Location','Best');
    xlabel('Epoch'); ylabel('Cost');
    title('Convergence for G2=clamp(Y)');
    grid on; hold off;

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% (A) Numerical trapezoidal approximation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [numG1, numG2] = trapezoid_conditional_expectation_corrected(x_grid)
    % This function computes the numerical trapezoidal approximation
    % for E[G1(Y)|X] and E[G2(Y)|X] over a grid of X values.

    n = 200;  % Number of intervals
    yvals = linspace(-5,5,n+1)';  % y0..y_n

    G1vals = yvals;                    % G1(Y)=Y
    G2vals = min(1, max(-1, yvals));  % G2(Y)=clamp(Y)

    numXg = length(x_grid);
    numG1 = zeros(numXg,1);
    numG2 = zeros(numXg,1);

    for j = 1:numXg
        xval = x_grid(j);

        % Compute CDF values for Y|X=x
        Hvals = normcdf(yvals, 0.8*xval, 1);

        % Compute F using trapezoidal rule
        F = zeros(n,1);
        F(1) = 0.5*(Hvals(2) - Hvals(1));
        for i = 2:(n-1)
            F(i) = 0.5*(Hvals(i+1) - Hvals(i-1));
        end
        F(n) = 0.5*(Hvals(n+1) - Hvals(n));

        % Compute V1 and V2 as weighted sums
        V1 = sum(F .* G1vals(2:end));
        V2 = sum(F .* G2vals(2:end));

        numG1(j) = V1;
        numG2(j) = V2;
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% (B) Train Neural Network using Exact Gradient Descent
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [netParams, costHistory] = trainNN_dataDriven_corrected(X, G, ...
                                   hiddenSize, nEpochs, lr, methodTag)
    % This function trains a neural network to approximate E[G(Y)|X]
    % using the exact gradient descent update.

    N = length(X);
    X = X(:);
    G = G(:);

    % Initialize weights using He Initialization for ReLU
    [W1, b1, W2, b2] = initializeWeights_corrected(hiddenSize);
    
    costHistory = zeros(nEpochs,1);
    
    for epoch = 1:nEpochs
        % 1) Forward pass => u_i
        [uVals, Z1] = forwardPass_relu(X, W1, b1, W2, b2);
        
        % 2) Compute phi, phi', psi, psi'
        [phi, phi_prime, psi, psi_prime] = compute_phi_psi(uVals, methodTag);
        
        % 3) Compute Cost
        cost = mean(phi + G .* psi);
        costHistory(epoch) = cost;
        
        % 4) Compute gradients
        % dL/du = phi'(u) + g * psi'(u)
        dLdu = phi_prime + G .* psi_prime;  % Nx1
        
        % 5) Backpropagation to compute gradients w.r. parameters
        [dW1, db1_, dW2, db2_] = backwardPass_relu(X, Z1, W1, b1, W2, b2, dLdu);
        
        % 6) Update parameters
        W1 = W1 - lr * dW1;
        b1 = b1 - lr * db1_;
        W2 = W2 - lr * dW2;
        b2 = b2 - lr * db2_;
    end

    % Store network parameters
    netParams.W1 = W1;
    netParams.b1 = b1;
    netParams.W2 = W2;
    netParams.b2 = b2;
    netParams.method = methodTag;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% (C) Evaluate Neural Network
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function yhat = evaluateNN_corrected(netParams, x_grid)
    % This function evaluates the trained neural network on a grid of X values.

    [uVals, ~] = forwardPass_relu(x_grid, ...
                                  netParams.W1, netParams.b1, ...
                                  netParams.W2, netParams.b2);
    omega = compute_omega(uVals, netParams.method);
    yhat = omega;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% (D) Forward Pass with ReLU Activation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [uVals, Z1] = forwardPass_relu(X, W1, b1, W2, b2)
    % Perform forward propagation through the network with ReLU activation.

    WX  = W1 * X';             % (hiddenSize x 1) * (1 x N) = hiddenSize x N
    WXb = WX + b1;             % (hiddenSize x N) + (hiddenSize x 1) = hiddenSize x N
    Z1  = max(WXb, 0);         % ReLU activation, hiddenSize x N
    uVals = (W2 * Z1 + b2)';    % (1 x hiddenSize) * (hiddenSize x N) + scalar = 1 x N; transpose to Nx1
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% (E) Backward Pass with ReLU Activation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [dW1, db1, dW2, db2] = backwardPass_relu(X, Z1, W1, b1, W2, b2, dLdu)
    % Perform backward propagation to compute gradients.

    N = length(X);
    
    % dW2 => shape(1 x hiddenSize)
    dW2 = (dLdu' * Z1') / N;  % (1 x N) * (N x hiddenSize) = 1 x hiddenSize
    db2 = mean(dLdu);          % scalar
    
    % Backprop to Z1
    dZ1 = W2' * dLdu';         % (hiddenSize x 1) * (1 x N) = hiddenSize x N
    mask = double(Z1 > 0);     % ReLU derivative, hiddenSize x N
    dWXb = dZ1 .* mask;        % (hiddenSize x N) .* (hiddenSize x N) = hiddenSize x N
    
    % dW1 => shape(hiddenSize x 1)
    dW1 = (dWXb * X) / N;      % (hiddenSize x N) * (N x 1) = hiddenSize x 1
    
    % db1 => shape(hiddenSize x 1)
    db1 = mean(dWXb, 2);       % mean across N, hiddenSize x 1
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% (F) Compute phi, phi', psi, psi'
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [phi, phi_prime, psi, psi_prime] = compute_phi_psi(u, methodTag)
    % Compute phi, phi', psi, psi' based on the method tag.

    switch methodTag
        case 'A1'
            % [A1]: ω(z) = z, ρ(z) = -1, φ(z) = z^2 / 2, ψ(z) = -z
            phi = 0.5 * u.^2;
            phi_prime = u;
            psi = -u;
            psi_prime = -ones(size(u));
            
        case 'A2'
            % [A2]: ω(z) = sinh(z), ρ(z) = -exp(-0.5*abs(z)), 
            % φ(z) = (exp(0.5*abs(z)) -1) + (1/3)*(exp(-1.5*abs(z)) -1),  
            % ψ(z) = 2*sign(z)*(exp(-0.5*abs(z)) -1)
            abs_z = abs(u);
            sign_z = sign(u);
            phi = (exp(0.5 * abs_z) - 1) + (1/3) * (exp(-1.5 * abs_z) - 1);
            phi_prime = 0.5 * sign_z .* exp(0.5 * abs_z) - 0.5 * sign_z .* exp(-1.5 * abs_z);
            psi = 2 * sign_z .* (exp(-0.5 * abs_z) - 1);
            psi_prime = -exp(-0.5 * abs_z);  % As per your definition
            
        case 'C1'
            % [C1]: a = -1, b = 1, ω(z) = (a + b*exp(z)) / (1 + exp(z)),  
            % ρ(z) = -exp(z) / (1 + exp(z)),  
            % φ(z) = ((b - a) / (1 + exp(z))) + b*log(1 + exp(z)),  
            % ψ(z) = -log(1 + exp(z))
            a = -1;
            b = 1;
            ez = exp(u);
            omega = (a + b .* ez) ./ (1 + ez);
            phi = ((b - a) ./ (1 + ez)) + b .* log(1 + ez);
            phi_prime = (- (b - a) .* ez ./ (1 + ez).^2 ) + b .* ( ez ./ (1 + ez) );
            psi = -log(1 + ez);
            psi_prime = -ez ./ (1 + ez);
            
        otherwise
            error('Unknown methodTag');
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% (G) Compute omega based on method tag
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function omega = compute_omega(u, methodTag)
    % Compute the transformation omega based on the method tag.

    switch methodTag
        case 'A1'
            omega = u;
        case 'A2'
            omega = sinh(u);
        case 'C1'
            a = -1;
            b = 1;
            ez = exp(u);
            omega = (a + b .* ez) ./ (1 + ez);
        otherwise
            error('Unknown methodTag');
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% (H) Initialize Weights using He Initialization for ReLU
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [W1, b1, W2, b2] = initializeWeights_corrected(hiddenSize)
    % Initialize weights using He Initialization for ReLU activation.

    inputSize = 1;       % Since X is scalar
    outputSize = 1;      % Single output neuron
    
    W1 = randn(hiddenSize, inputSize) * sqrt(2 / inputSize);
    b1 = zeros(hiddenSize, 1);
    W2 = randn(outputSize, hiddenSize) * sqrt(2 / hiddenSize);
    b2 = 0;
end





