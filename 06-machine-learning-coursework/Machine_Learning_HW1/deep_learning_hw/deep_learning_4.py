import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Step 1: Generate Data
# ----------------------------

# Number of samples
num_samples = 10**6

# Generate H0 data: N(0,1) for both x1 and x2
f0_data = np.random.normal(0, 1, (num_samples, 2))

# Generate H1 data: mixture of N(1,1) and N(-1,1) for both x1 and x2
mixture_choices = np.random.rand(num_samples, 2) > 0.5  # True for N(1,1), False for N(-1,1)
f1_data = np.where(
    mixture_choices,
    np.random.normal(1, 1, (num_samples, 2)),
    np.random.normal(-1, 1, (num_samples, 2))
)

# ----------------------------
# Step 2: Compute Bayes Optimal Test
# ----------------------------

def compute_log_likelihood_ratios(x):
    """
    Computes the log-likelihood ratio log(r(x1, x2)) where
    r(x1, x2) = (f1(x1)/f0(x1)) * (f1(x2)/f0(x2))
    """
    # Log-likelihoods under f0
    log_f0 = -0.5 * x**2 - np.log(np.sqrt(2 * np.pi))

    # Log-likelihoods under f1 (mixture)
    log_f1_pos = -0.5 * (x - 1)**2 - np.log(np.sqrt(2 * np.pi))
    log_f1_neg = -0.5 * (x + 1)**2 - np.log(np.sqrt(2 * np.pi))

    # Compute log(f1) using log-sum-exp for numerical stability
    max_log = np.maximum(log_f1_pos, log_f1_neg)
    log_f1 = max_log + np.log(0.5 * np.exp(log_f1_pos - max_log) + 0.5 * np.exp(log_f1_neg - max_log))

    # Log-likelihood ratios for each dimension
    log_r = log_f1 - log_f0  # Shape: (num_samples, 2)

    # Total log-likelihood ratio
    total_log_r = np.sum(log_r, axis=1)  # Shape: (num_samples,)
    return total_log_r

# Compute log-likelihood ratios for H0 and H1 data
log_r_f0 = compute_log_likelihood_ratios(f0_data)
log_r_f1 = compute_log_likelihood_ratios(f1_data)

# Decisions based on log-likelihood ratios
decisions_f0 = (log_r_f0 > 0).astype(int)  # H1 if log(r) > 0
decisions_f1 = (log_r_f1 > 0).astype(int)  # H1 if log(r) > 0

# Error probabilities
error_f0 = np.mean(decisions_f0 != 0)  # Error: H0 -> H1
error_f1 = np.mean(decisions_f1 != 1)  # Error: H1 -> H0
total_error_probability = 0.5 * (error_f0 + error_f1)

print(f"Error probability for H0: {error_f0:.4f}")
print(f"Error probability for H1: {error_f1:.4f}")
print(f"Total probability of error (Bayes Optimal): {total_error_probability:.4f}")

# Plot Bayes Optimal Errors
labels_plot = ['H0 Error', 'H1 Error', 'Total Error']
values = [error_f0, error_f1, total_error_probability]

plt.figure(figsize=(8, 6))
plt.bar(labels_plot, values, color=['blue', 'orange', 'green'])
plt.xlabel('Error Type')
plt.ylabel('Probability')
plt.title('Bayes Optimal Error Probabilities')
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# ----------------------------
# Step 3: Prepare Training Data
# ----------------------------

train_samples = 200  # Number of training samples per hypothesis

# Training data for H0: N(0,1)
train_f0_data = np.random.normal(0, 1, (train_samples, 2))

# Training data for H1: mixture of N(1,1) and N(-1,1)
mixture_choices_train = np.random.rand(train_samples, 2) > 0.5
train_f1_data = np.where(
    mixture_choices_train,
    np.random.normal(1, 1, (train_samples, 2)),
    np.random.normal(-1, 1, (train_samples, 2))
)

# Combine training data and labels
train_data = np.vstack((train_f0_data, train_f1_data))  # Shape: (400, 2)
train_labels = np.hstack((np.zeros(train_samples), np.ones(train_samples))).reshape(-1, 1)  # Shape: (400, 1)

# Compute log-likelihood ratios for training data
log_r_train = compute_log_likelihood_ratios(train_data)

# Targets for Cross-Entropy Method: P(H1|x) = r / (1 + r)
ce_targets = (np.exp(log_r_train) / (1 + np.exp(log_r_train))).reshape(-1, 1)  # Shape: (400, 1)

# Targets for Exponential Method: transform labels to -1 or +1
exp_targets = 2 * train_labels - 1  # Transforms labels from {0,1} to {-1,+1}

# ----------------------------
# Step 4: Define Neural Network Components
# ----------------------------

def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return (x > 0).astype(float)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def initialize_parameters(input_size, hidden_size, output_size):
    """
    Initializes weights and biases.
    Weights are drawn from N(0, 1/(n + m)) where n and m are input and output dimensions.
    Biases are initialized to zero.
    """
    weights_1 = np.random.normal(0, np.sqrt(1 / (input_size + hidden_size)), (input_size, hidden_size))
    biases_1 = np.zeros(hidden_size)
    weights_2 = np.random.normal(0, np.sqrt(1 / (hidden_size + output_size)), (hidden_size, output_size))
    biases_2 = np.zeros(output_size)
    return weights_1, biases_1, weights_2, biases_2

def custom_cross_entropy_loss(Y, targets):
    """
    Computes the binary cross-entropy loss.
    Args:
        Y: Predicted probabilities (N, 1).
        targets: True probabilities (N, 1).
    Returns:
        Scalar loss value.
    """
    epsilon = 1e-8  # To prevent log(0)
    return np.mean(-targets * np.log(Y + epsilon) - (1 - targets) * np.log(1 - Y + epsilon))

def custom_exponential_loss(Y, targets):
    """
    Computes the standard exponential loss.
    Args:
        Y: Predicted raw outputs (N, 1).
        targets: Transformed labels (-1 or +1) (N, 1).
    Returns:
        Scalar loss value.
    """
    return np.mean(np.exp(- targets * Y))

def sgd_with_adam_normalization(param, grad, P_prev, mu=0.001, lambda_=0.999, c=1e-8):
    """
    Performs the SGD update with ADAM-like normalization on a parameter.
    Args:
        param: Current parameter value.
        grad: Gradient of the loss w.r.t. the parameter.
        P_prev: Previous power estimate (P[t-1]).
        mu: Learning rate.
        lambda_: Decay rate for the power estimate.
        c: Small constant to prevent division by zero.
    Returns:
        Updated parameter, updated P.
    """
    # Update power estimate
    P = (1 - lambda_) * P_prev + lambda_ * (grad ** 2)

    # Update parameter with normalized gradient
    param_update = mu * grad / (np.sqrt(c + P))
    param -= param_update

    return param, P

def initialize_power_estimates(shape):
    """
    Initializes the power estimates P for a given parameter shape.
    Starts with zeros.
    """
    return np.zeros(shape)

def forward_pass(data, weights_1, biases_1, weights_2, biases_2, activation_output='sigmoid'):
    """
    Performs a forward pass through the network.
    Args:
        data: Input data of shape (N, 2).
        weights_1: Weights of the first layer (2, 20).
        biases_1: Biases of the first layer (20,).
        weights_2: Weights of the second layer (20, 1).
        biases_2: Biases of the second layer (1,).
        activation_output: 'sigmoid' or 'none'.
    Returns:
        Y: Output activations (N, 1).
        Z1: Hidden layer activations (N, 20).
    """
    W1 = np.dot(data, weights_1) + biases_1  # Shape: (N, 20)
    Z1 = relu(W1)  # Shape: (N, 20)
    W2 = np.dot(Z1, weights_2) + biases_2  # Shape: (N, 1)
    if activation_output == 'sigmoid':
        Y = sigmoid(W2)  # Shape: (N, 1)
    elif activation_output == 'none':
        Y = W2  # Shape: (N, 1)
    else:
        raise ValueError("Invalid activation_output")
    return Y, Z1

def compute_gradients_custom(X, Z1, Y, targets, weights_1, biases_1, weights_2, method='cross_entropy'):
    """
    Computes the gradients based on the provided loss functions.
    Args:
        X: Input data (N, 2).
        Z1: Hidden layer activations (N, 20).
        Y: Output activations (N, 1).
        targets: True labels or targets (N, 1).
        weights_1: Weights of the first layer (2, 20).
        biases_1: Biases of the first layer (20,).
        weights_2: Weights of the second layer (20, 1).
        method: 'cross_entropy' or 'exponential'.
    Returns:
        Gradients for weights_2, biases_2, weights_1, biases_1.
    """
    N = X.shape[0]

    if method == 'cross_entropy':
        # For cross-entropy loss with sigmoid activation
        U2 = Y - targets  # Shape: (N, 1)
        f2_prime = Y * (1 - Y)  # Derivative of sigmoid
    elif method == 'exponential':
        # For exponential loss with linear activation
        U2 = - targets * np.exp(- targets * Y)  # Shape: (N, 1)
        f2_prime = np.ones_like(Y)  # Derivative of linear activation is 1
    else:
        raise ValueError("Invalid method")

    V2 = U2 * f2_prime  # Shape: (N, 1)

    # Compute gradients for weights_2 and biases_2
    grad_weights_2 = np.dot(Z1.T, V2) / N  # Shape: (20, 1)
    grad_biases_2 = np.sum(V2, axis=0) / N  # Shape: (1,)

    # Compute V1 = (V2 dot weights_2^T) ⊙ f'_1(W1)
    f1_prime = relu_derivative(np.dot(X, weights_1) + biases_1)  # Shape: (N, 20)
    V1 = np.dot(V2, weights_2.T) * f1_prime  # Shape: (N, 20)

    # Compute gradients for weights_1 and biases_1
    grad_weights_1 = np.dot(X.T, V1) / N  # Shape: (2, 20)
    grad_biases_1 = np.sum(V1, axis=0) / N  # Shape: (20,)

    return grad_weights_2, grad_biases_2, grad_weights_1, grad_biases_1

# ----------------------------
# Step 5: Training Function with SGD and ADAM-like Normalization
# ----------------------------

def train_network_sgd_adam_norm(train_data, targets, method='cross_entropy', num_epochs=500, mu=0.001, lambda_=0.999, c=1e-8, hidden_size=20):
    """
    Trains a neural network using SGD with ADAM-like normalization.
    Args:
        train_data: Training data of shape (400, 2).
        targets: Targets for training of shape (400, 1).
        method: 'cross_entropy' or 'exponential'.
        num_epochs: Number of training epochs.
        mu: Learning rate.
        lambda_: Decay rate for the power estimate.
        c: Small constant to prevent division by zero.
        hidden_size: Number of neurons in the hidden layer.
    Returns:
        Trained weights and biases, and history of loss values.
    """
    input_size = 2
    output_size = 1

    # Initialize parameters
    weights_1, biases_1, weights_2, biases_2 = initialize_parameters(input_size, hidden_size, output_size)

    # Initialize power estimates for each parameter matrix
    P_w1 = initialize_power_estimates(weights_1.shape)
    P_b1 = initialize_power_estimates(biases_1.shape)
    P_w2 = initialize_power_estimates(weights_2.shape)
    P_b2 = initialize_power_estimates(biases_2.shape)

    history = []

    for epoch in range(1, num_epochs + 1):
        # Forward pass
        Y, Z1 = forward_pass(train_data, weights_1, biases_1, weights_2, biases_2,
                             activation_output='sigmoid' if method == 'cross_entropy' else 'none')

        # Compute loss
        if method == 'cross_entropy':
            loss = custom_cross_entropy_loss(Y, targets)
        elif method == 'exponential':
            loss = custom_exponential_loss(Y, targets)
        else:
            raise ValueError("Invalid training method")

        history.append(loss)

        # Compute gradients
        grad_weights_2, grad_biases_2, grad_weights_1, grad_biases_1 = compute_gradients_custom(
            train_data, Z1, Y, targets, weights_1, biases_1, weights_2, method=method)

        # Update weights and biases using SGD with ADAM-like normalization
        weights_2, P_w2 = sgd_with_adam_normalization(weights_2, grad_weights_2, P_w2, mu, lambda_, c)
        biases_2, P_b2 = sgd_with_adam_normalization(biases_2, grad_biases_2, P_b2, mu, lambda_, c)
        weights_1, P_w1 = sgd_with_adam_normalization(weights_1, grad_weights_1, P_w1, mu, lambda_, c)
        biases_1, P_b1 = sgd_with_adam_normalization(biases_1, grad_biases_1, P_b1, mu, lambda_, c)

        # Print smoothed cost every 50 epochs
        if epoch % 50 == 0:
            # Smoothed loss: average of the last 20 epochs
            smoothed_loss = np.mean(history[-20:])
            print(f"Epoch {epoch}, Smoothed Cost ({method.capitalize()} SGD with ADAM-like Norm): {smoothed_loss:.6f}")

    return weights_1, biases_1, weights_2, biases_2, history

# ----------------------------
# Step 6: Train Both Neural Networks
# ----------------------------

# Train Cross-Entropy Network
print("\nTraining Cross-Entropy Network with SGD and ADAM-like Normalization:")
weights_1_ce, biases_1_ce, weights_2_ce, biases_2_ce, history_ce = train_network_sgd_adam_norm(
    train_data, ce_targets, method='cross_entropy', num_epochs=500, mu=0.001, lambda_=0.999, c=1e-8, hidden_size=20)

# Train Exponential Network
print("\nTraining Exponential Network with SGD and ADAM-like Normalization:")
weights_1_exp, biases_1_exp, weights_2_exp, biases_2_exp, history_exp = train_network_sgd_adam_norm(
    train_data, exp_targets, method='exponential', num_epochs=500, mu=0.001, lambda_=0.999, c=1e-8, hidden_size=20)

# ----------------------------
# Step 7: Plot Training Loss
# ----------------------------

plt.figure(figsize=(10, 6))
plt.plot(history_ce, label='Cross-Entropy Loss with SGD + ADAM-like Norm')
plt.plot(history_exp, label='Exponential Loss with SGD + ADAM-like Norm', color='orange')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss over Epochs for Cross-Entropy and Exponential Methods')
plt.legend()
plt.grid(True)
plt.show()

# ----------------------------
# Step 8: Evaluate Neural Networks on Test Data
# ----------------------------

def compute_decisions(Y, method='cross_entropy'):
    """
    Converts network outputs to binary decisions based on the method.
    Args:
        Y: Network outputs.
        method: 'cross_entropy' or 'exponential'.
    Returns:
        Binary decisions: 0 or 1.
    """
    if method == 'cross_entropy':
        # Decide H1 if P(H1|x) > 0.5
        decisions = (Y.flatten() > 0.5).astype(int)
    elif method == 'exponential':
        # Decide H1 if Y > 0 (since targets are -1 or +1)
        decisions = (Y.flatten() > 0).astype(int)
    else:
        raise ValueError("Invalid method for decision computation")
    return decisions

def evaluate_network_in_batches(test_data, weights_1, biases_1, weights_2, biases_2, method='cross_entropy', batch_size=100000):
    """
    Evaluates the network on test data in batches to manage memory usage.
    Args:
        test_data: Test data of shape (2,000,000, 2).
        weights_1: Weights of the first layer.
        biases_1: Biases of the first layer.
        weights_2: Weights of the second layer.
        biases_2: Biases of the second layer.
        method: 'cross_entropy' or 'exponential'.
        batch_size: Number of samples per batch.
    Returns:
        decisions: Binary decisions for all test samples.
    """
    num_test = test_data.shape[0]
    decisions = np.zeros(num_test, dtype=int)

    for start in range(0, num_test, batch_size):
        end = min(start + batch_size, num_test)
        batch = test_data[start:end]
        Y, _ = forward_pass(batch, weights_1, biases_1, weights_2, biases_2,
                            activation_output='sigmoid' if method == 'cross_entropy' else 'none')
        batch_decisions = compute_decisions(Y, method=method)
        decisions[start:end] = batch_decisions

    return decisions

# Prepare Test Data
test_data = np.vstack((f0_data, f1_data))  # Shape: (2,000,000, 2)
test_labels = np.hstack((np.zeros(num_samples), np.ones(num_samples)))  # Shape: (2,000,000,)

# Evaluate Cross-Entropy Network on Test Data
print("\nEvaluating Cross-Entropy Network on Test Data:")
decisions_ce = evaluate_network_in_batches(test_data, weights_1_ce, biases_1_ce, weights_2_ce, biases_2_ce, method='cross_entropy')

# Evaluate Exponential Network on Test Data
print("\nEvaluating Exponential Network on Test Data:")
decisions_exp = evaluate_network_in_batches(test_data, weights_1_exp, biases_1_exp, weights_2_exp, biases_2_exp, method='exponential')

# Compute error probabilities for Cross-Entropy method
error_ce_f0 = np.mean(decisions_ce[test_labels == 0] != 0)
error_ce_f1 = np.mean(decisions_ce[test_labels == 1] != 1)
total_error_ce = 0.5 * (error_ce_f0 + error_ce_f1)

# Compute error probabilities for Exponential method
error_exp_f0 = np.mean(decisions_exp[test_labels == 0] != 0)
error_exp_f1 = np.mean(decisions_exp[test_labels == 1] != 1)
total_error_exp = 0.5 * (error_exp_f0 + error_exp_f1)

# Print probabilities for all methods
print(f"\nBayes Optimal Total Error Probability: {total_error_probability:.6f}")
print(f"Cross-Entropy Method Total Error Probability: {total_error_ce:.6f}")
print(f"Exponential Method Total Error Probability: {total_error_exp:.6f}")

# Plot comparison of error probabilities
labels_compare = ['Bayes Optimal', 'Cross-Entropy', 'Exponential']
values_compare = [total_error_probability, total_error_ce, total_error_exp]

plt.figure(figsize=(8, 6))
plt.bar(labels_compare, values_compare, color=['green', 'blue', 'orange'])
plt.xlabel('Method')
plt.ylabel('Total Error Probability')
plt.title('Comparison of Total Error Probabilities')
plt.ylim(0, max(values_compare) + 0.05)
for i, v in enumerate(values_compare):
    plt.text(i, v + 0.005, f"{v:.6f}", ha='center')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
