import os
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# 1. Data Preparation
# ----------------------------

def load_mnist_images(filename):
    with open(filename, 'rb') as f:
        f.read(4)  # Magic number
        num_images = int.from_bytes(f.read(4), 'big')
        num_rows = int.from_bytes(f.read(4), 'big')
        num_cols = int.from_bytes(f.read(4), 'big')
        buffer = f.read(num_images * num_rows * num_cols)
        data = np.frombuffer(buffer, dtype=np.uint8).reshape(num_images, num_rows * num_cols)
        return data / 255.0  # Normalize to [0,1]

def load_mnist_labels(filename):
    with open(filename, 'rb') as f:
        f.read(4)  # Magic number
        num_labels = int.from_bytes(f.read(4), 'big')
        buffer = f.read(num_labels)
        return np.frombuffer(buffer, dtype=np.uint8)

def prepare_data():
    # Set the folder path to your mnist_data directory
    folder = r"C:\Users\georg\Desktop\deep_learning_hw\mnist_data"
    
    # Full paths for each file
    train_images_path = os.path.join(folder, 'train-images.idx3-ubyte')
    train_labels_path = os.path.join(folder, 'train-labels.idx1-ubyte')
    test_images_path = os.path.join(folder, 't10k-images.idx3-ubyte')
    test_labels_path = os.path.join(folder, 't10k-labels.idx1-ubyte')
    
    # Print each path to confirm
    print(f"Train images path: {train_images_path}")
    print(f"Train labels path: {train_labels_path}")
    print(f"Test images path: {test_images_path}")
    print(f"Test labels path: {test_labels_path}")

    # Check if files exist
    assert os.path.exists(train_images_path), f"File not found: {train_images_path}"
    assert os.path.exists(train_labels_path), f"File not found: {train_labels_path}"
    assert os.path.exists(test_images_path), f"File not found: {test_images_path}"
    assert os.path.exists(test_labels_path), f"File not found: {test_labels_path}"

    # Load the data
    train_images = load_mnist_images(train_images_path)
    train_labels = load_mnist_labels(train_labels_path)
    test_images = load_mnist_images(test_images_path)
    test_labels = load_mnist_labels(test_labels_path)
    
    # Filter for digits 0 and 8
    train_filter = np.where((train_labels == 0) | (train_labels == 8))
    test_filter = np.where((test_labels == 0) | (test_labels == 8))
    X_train, y_train = train_images[train_filter], train_labels[train_filter]
    X_test, y_test = test_images[test_filter], test_labels[test_filter]

    # Map labels: 0 stays 0, 8 becomes 1
    y_train = np.where(y_train == 8, 1, 0)
    y_test = np.where(y_test == 8, 1, 0)

    return X_train, y_train, X_test, y_test

# ----------------------------
# 2. Neural Network with Specified Initialization
# ----------------------------

def initialize_parameters(input_size, hidden_size, output_size):
    weights_1 = np.random.normal(0, np.sqrt(1 / (input_size + hidden_size)), (input_size, hidden_size))
    biases_1 = np.zeros((1, hidden_size))
    weights_2 = np.random.normal(0, np.sqrt(1 / (hidden_size + output_size)), (hidden_size, output_size))
    biases_2 = np.zeros((1, output_size))
    return weights_1, biases_1, weights_2, biases_2

def relu(x):
    return np.maximum(0, x)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# ----------------------------
# 3. Forward and Backward Passes with Different Loss Functions
# ----------------------------

def forward_pass(X, weights_1, biases_1, weights_2, biases_2, method='cross_entropy'):
    Z1 = np.dot(X, weights_1) + biases_1
    A1 = relu(Z1)
    Z2 = np.dot(A1, weights_2) + biases_2

    if method == 'cross_entropy':
        A2 = sigmoid(Z2)  # Output as probability
    elif method == 'exponential':
        A2 = Z2  # Output as log-likelihood ratio directly
    else:
        raise ValueError("Invalid method specified.")
    
    return {'X': X, 'Z1': Z1, 'A1': A1, 'Z2': Z2, 'A2': A2}

def compute_loss(A2, Y, method='cross_entropy'):
    m = Y.shape[0]
    if method == 'cross_entropy':
        epsilon = 1e-8
        A2 = np.clip(A2, epsilon, 1 - epsilon)
        loss = - (1 / m) * np.sum(Y * np.log(A2) + (1 - Y) * np.log(1 - A2))
    elif method == 'exponential':
        Y_mapped = 2 * Y - 1
        loss = (1 / m) * np.sum(np.exp(0.5 * Y_mapped * A2) + np.exp(-0.5 * Y_mapped * A2))
    else:
        raise ValueError("Invalid loss method specified.")
    return loss

def backward_pass(cache, Y, weights_2, method='cross_entropy'):
    m = Y.shape[0]
    A2 = cache['A2']
    A1 = cache['A1']
    Z1 = cache['Z1']
    X = cache['X']
    
    if method == 'cross_entropy':
        dZ2 = A2 - Y
    elif method == 'exponential':
        Y_mapped = 2 * Y - 1
        dZ2 = 0.5 * Y_mapped * np.exp(0.5 * Y_mapped * A2) - 0.5 * np.exp(-0.5 * Y_mapped * A2)
    else:
        raise ValueError("Invalid method specified.")
        
    dW2 = np.dot(A1.T, dZ2) / m
    db2 = np.sum(dZ2, axis=0, keepdims=True) / m
    dA1 = np.dot(dZ2, weights_2.T)
    dZ1 = dA1 * (Z1 > 0).astype(float)
    dW1 = np.dot(X.T, dZ1) / m
    db1 = np.sum(dZ1, axis=0, keepdims=True) / m

    return {'dW1': dW1, 'db1': db1, 'dW2': dW2, 'db2': db2}

# ----------------------------
# 4. ADAM Optimizer for Parameter Updates
# ----------------------------

def adam_update(param, grad, P_prev, mu=0.001, lambda_=0.999, c=1e-8):
    P = (1 - lambda_) * P_prev + lambda_ * (grad ** 2)
    param_update = mu * grad / (np.sqrt(c + P))
    param -= param_update
    return param, P

# ----------------------------
# 5. Training Loop with Learning Curve Plotting
# ----------------------------

def train_network_adam(X_train, y_train, num_epochs=1000, learning_rate=0.001, lambda_=0.999, method='cross_entropy'):
    input_size = X_train.shape[1]
    hidden_size = 300
    output_size = 1
    weights_1, biases_1, weights_2, biases_2 = initialize_parameters(input_size, hidden_size, output_size)
    P_w1, P_b1 = np.zeros_like(weights_1), np.zeros_like(biases_1)
    P_w2, P_b2 = np.zeros_like(weights_2), np.zeros_like(biases_2)
    losses = []

    for epoch in range(num_epochs):
        cache = forward_pass(X_train, weights_1, biases_1, weights_2, biases_2, method=method)
        loss = compute_loss(cache['A2'], y_train.reshape(-1, 1), method=method)
        losses.append(loss)
        gradients = backward_pass(cache, y_train.reshape(-1, 1), weights_2, method=method)
        
        weights_1, P_w1 = adam_update(weights_1, gradients['dW1'], P_w1, mu=learning_rate, lambda_=lambda_)
        biases_1, P_b1 = adam_update(biases_1, gradients['db1'], P_b1, mu=learning_rate, lambda_=lambda_)
        weights_2, P_w2 = adam_update(weights_2, gradients['dW2'], P_w2, mu=learning_rate, lambda_=lambda_)
        biases_2, P_b2 = adam_update(biases_2, gradients['db2'], P_b2, mu=learning_rate, lambda_=lambda_)
        
        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Loss: {loss}")
    
    plt.plot(losses, label=f'{method} loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title(f'Learning Curve for {method} Method')
    plt.show()
    return weights_1, biases_1, weights_2, biases_2

# ----------------------------
# 6. Evaluation
# ----------------------------

def evaluate(X, y, weights_1, biases_1, weights_2, biases_2, method='cross_entropy'):
    cache = forward_pass(X, weights_1, biases_1, weights_2, biases_2, method=method)
    predictions = (cache['A2'] > 0.5).astype(int)  # threshold 0.5 for classification
    error_rate = np.mean(predictions != y.reshape(-1, 1))
    return error_rate

# ----------------------------
# Main Script
# ----------------------------
if __name__ == "__main__":
    X_train, y_train, X_test, y_test = prepare_data()
    
    # Train and plot for Cross-Entropy Method
    print("Training with Cross-Entropy Method:")
    w1_ce, b1_ce, w2_ce, b2_ce = train_network_adam(X_train, y_train, method='cross_entropy')
    error_rate_ce = evaluate(X_test, y_test, w1_ce, b1_ce, w2_ce, b2_ce, method='cross_entropy')
    print(f"Cross-Entropy Test Error Rate: {error_rate_ce * 100:.2f}%")
    
    # Train and plot for Exponential Method
    print("\nTraining with Exponential Method:")
    w1_exp, b1_exp, w2_exp, b2_exp = train_network_adam(X_train, y_train, method='exponential')
    error_rate_exp = evaluate(X_test, y_test, w1_exp, b1_exp, w2_exp, b2_exp, method='exponential')
    print(f"Exponential Test Error Rate: {error_rate_exp * 100:.2f}%")
