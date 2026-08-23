% MATLAB Script to Reconstruct and Display 4 Images Using ADAM Optimization
% Processes Each of the 4 Images in data22.mat Separately

%% Step 0: Clear Workspace and Setup
clear;
clc;
close all;

%% Step 1: Load Data
% Define the paths to the data files
dataPath21 = 'C:\Users\georg\Desktop\hw2\data21.mat'; % Neural network parameters
dataPath22 = 'C:\Users\georg\Desktop\hw2\data22.mat'; % Image data

% Load neural network parameters from data21.mat
if exist(dataPath21, 'file') == 2
    load(dataPath21, 'A_1', 'A_2', 'B_1', 'B_2');
else
    error('Data file data21.mat not found at the specified path.');
end

% Load original and noisy images from data22.mat
if exist(dataPath22, 'file') == 2
    load(dataPath22, 'X_i', 'X_n');
else
    error('Data file data22.mat not found at the specified path.');
end

% Verify dimensions
[numPixels, numImages] = size(X_i);
if numPixels ~= 784
    error('Each image should have 784 pixels (28x28). Check X_i in data22.mat.');
end

% For demonstration, process up to 4 images
numDisplayImages = min(4, numImages);

%% Step 2: Set Parameters for ADAM Optimization
% You can change N here as per your requirement (e.g., 500, 400, 350, 300)
N = 340;                      % Number of observed pixels
mu = 1e-3;                    % Learning rate for ADAM (adjusted to standard value)
lambda = 0.9;                 % Decay rate for power estimates (lambda << 1)
c = 1e-8;                     % Small constant to prevent division by zero
max_iters = 1000;             % Maximum number of iterations
tol = 1e-6;                   % Convergence tolerance

%% Step 3: Define Transformation Matrix T
% T is an N x 784 matrix that selects the first N pixels
T = [eye(N), zeros(N, 784 - N)]; % N x 784

%% Step 4: Initialize Composite Image Grid for Visualization
% Define grid parameters
imagesPerRow = numDisplayImages;   % Number of image sets per row
imagesPerColumn = 3;               % Columns: Original, Noisy, Reconstructed
imageSize = 28;                    % Each image is 28x28 pixels
padding = 0;                        % No padding between images

% Calculate the size of the composite image
compositeHeight = numDisplayImages * imageSize + (numDisplayImages - 1) * padding;
compositeWidth = imagesPerColumn * imageSize + (imagesPerColumn - 1) * padding;

% Initialize the composite image matrix
% Each row in the composite image corresponds to one triplet
% Initialize with zeros (black background)
composite_image = zeros(compositeHeight, compositeWidth);

%% Step 5: Reconstruct Images Using ADAM Optimization
% Initialize storage for reconstructed images
reconstructed_X = zeros(784, numDisplayImages);
convergence_history = zeros(max_iters, numDisplayImages); % Optional

for imgIdx = 1:numDisplayImages
    fprintf('Processing Image %d/%d...\n', imgIdx, numDisplayImages);
    
    % Extract the noisy image X_n
    Xn_col = X_n(:, imgIdx); % 784 x 1
    
    % Create the noisy image display by masking out the lost pixels
    noisy_display_col = Xn_col;
    noisy_display_col(N+1:end) = 0; % Set elements N+1 to 784 to zero (black)
    
    % Initialize Z (latent vector)
    % A_1 is 128x10, so Z should be 10x1
    Z = randn(10, 1); % Initialize with random values from N(0,1)
    
    % Initialize Power Estimate P for Z
    P_Z = zeros(size(Z)); % 10 x 1
    
    % Initialize phi(Yt) = 1 for all elements
    phi_Yt = ones(size(Z)); % 10 x 1
    
    % Gradient Descent Loop with ADAM Optimization
    for iter = 1:max_iters
        % Forward pass through the neural network
        W1 = A_1 * Z + B_1;          % Layer 1 pre-activation: 128x1
        Z1 = max(W1, 0);              % ReLU activation: 128x1
        W2 = A_2 * Z1 + B_2;         % Layer 2 pre-activation: 784x1
        X = 1 ./ (1 + exp(W2));      % Sigmoid activation: 1 / (1 + e^{W})
        
        % Compute T * X to isolate the first N pixels
        TX = T * X;                   % N x 1
        
        % Extract the first N pixels from the noisy image
        TXn = Xn_col(1:N);            % N x 1
        
        % Compute residual between observed pixels
        residual = TX - TXn;           % N x 1
        
        % Compute norm squared of residual
        norm_residual_squared = residual' * residual;
        
        % Prevent division by zero by adding a small epsilon
        epsilon_loss = 1e-8;
        norm_residual_squared = norm_residual_squared + epsilon_loss;
        
        % Compute loss function
        J_Z = N * log(norm_residual_squared) + (Z' * Z);
        
        % Store loss for convergence checking (optional)
        convergence_history(iter, imgIdx) = J_Z;
        
        % Convergence check
        if iter > 1 && abs(J_Z - convergence_history(iter - 1, imgIdx)) < tol
            fprintf('Converged at iteration %d with loss %.6f\n', iter, J_Z);
            break;
        end
        
        % Backpropagation to compute gradient of J(Z)
        % Step 1: Compute derivative of loss w.r.t X
        % J(Z) = N * log(||T*X - Xn||^2) + ||Z||^2
        % ∇_X J(Z) = (2 * N * T' * (T*X - Xn)) / ||T*X - Xn||^2
        grad_X = (2 * N * T' * residual) / norm_residual_squared; % 784 x 1
        
        % Step 2: Compute derivative of sigmoid activation
        sigmoid_derivative = X .* (1 - X); % 784 x 1
        
        % Step 3: Compute gradient w.r.t W2
        grad_W2 = grad_X .* sigmoid_derivative; % 784 x 1
        
        % Step 4: Backpropagate to compute gradient w.r.t Z1
        grad_Z1 = A_2' * grad_W2; % 128 x 1
        
        % Step 5: Compute derivative of ReLU activation
        relu_derivative = W1 > 0; % 128 x 1 (logical array)
        
        % Step 6: Compute gradient w.r.t W1
        grad_W1 = grad_Z1 .* relu_derivative; % 128 x 1
        
        % Step 7: Backpropagate to compute gradient w.r.t Z
        grad_Z = A_1' * grad_W1 + 2 * Z; % 10 x 1
        
        % Update Power Estimate P_Z
        P_Z = (1 - lambda) * P_Z + lambda * (grad_Z .* phi_Yt).^2; % Element-wise operations
        
        % Update Z using ADAM-like update rule
        Z = Z - mu * (grad_Z .* phi_Yt) ./ sqrt(c + P_Z); % Element-wise division and square root
        
        % Optional: Display progress every 100 iterations
        if mod(iter, 100) == 0
            fprintf('Image %d, Iteration %d: Loss = %.6f\n', imgIdx, iter, J_Z);
        end
    end
    
    % After convergence, compute the final X using the optimized Z
    W1_final = A_1 * Z + B_1;          % Layer 1 pre-activation: 128x1
    Z1_final = max(W1_final, 0);       % ReLU activation: 128x1
    W2_final = A_2 * Z1_final + B_2;   % Layer 2 pre-activation: 784x1
    X_final = 1 ./ (1 + exp(W2_final)); % Sigmoid activation: 1 / (1 + e^{W})
    
    % Store the reconstructed image
    reconstructed_X(:, imgIdx) = X_final;
    
    %% Step 6: Place Images into the Composite Grid
    % Reshape images into 28x28 matrices
    original_image = reshape(X_i(:, imgIdx), imageSize, imageSize);       % Original Image
    noisy_image = reshape(noisy_display_col, imageSize, imageSize);        % Noisy Image (with lost pixels as black)
    reconstructed_image = reshape(X_final, imageSize, imageSize);         % Reconstructed Image
    
    % Calculate the row position in the composite grid
    currentRow = imgIdx;
    
    % Calculate starting and ending indices for placement in the composite grid
    rowStart = (currentRow - 1) * (imageSize + padding) + 1;
    rowEnd = rowStart + imageSize - 1;
    
    % Calculate column positions for Original, Noisy, Reconstructed
    colStartOriginal = 1;
    colEndOriginal = imageSize;
    
    colStartNoisy = imageSize + padding + 1;
    colEndNoisy = colStartNoisy + imageSize - 1;
    
    colStartReconstructed = 2 * (imageSize + padding) + 1;
    colEndReconstructed = colStartReconstructed + imageSize - 1;
    
    % Place Original Image
    composite_image(rowStart:rowEnd, colStartOriginal:colEndOriginal) = original_image;
    
    % Place Noisy Image
    composite_image(rowStart:rowEnd, colStartNoisy:colEndNoisy) = noisy_image;
    
    % Place Reconstructed Image
    composite_image(rowStart:rowEnd, colStartReconstructed:colEndReconstructed) = reconstructed_image;
end

%% Step 7: Display the Composite Image in Grayscale
figure('Name', 'Composite Visualization', 'NumberTitle', 'off');
imshow(composite_image, []); % Display in grayscale
xlabel(sprintf('Columns: Original | Noisy | Reconstructed for N = %d', N));
title('Image Reconstruction using ADAM Optimization');

%% Step 8: Plot Convergence Curves for All Images in the Same Graph
figure('Name', 'Convergence Curves', 'NumberTitle', 'off');
hold on;
colors = lines(numDisplayImages); % Generate distinct colors for each curve
for imgIdx = 1:numDisplayImages
    plot(convergence_history(1:max_iters, imgIdx), 'Color', colors(imgIdx,:), 'DisplayName', sprintf('Image %d', imgIdx));
end
hold off;
xlabel('Iteration');
ylabel('Loss J(Z)');
title('Convergence Curves for All Images');
legend('show');
grid on;

