import numpy as np
import matplotlib.pyplot as plt

# Step 1: Generate 1,000,000 pairs from each distribution
num_samples = 10**6

# For f0(x1, x2) where f0(x) ~ N(0, 1)
x1_f0 = np.random.normal(0, 1, num_samples)
x2_f0 = np.random.normal(0, 1, num_samples)
f0_data = np.vstack((x1_f0, x2_f0)).T

# For f1(x1, x2), generate x1 and x2 independently
x1_f1 = []
x2_f1 = []
for _ in range(num_samples):
    if np.random.uniform(0, 1) > 0.5:
        x1_f1.append(np.random.normal(1, 1))
    else:
        x1_f1.append(np.random.normal(-1, 1))
    
    if np.random.uniform(0, 1) > 0.5:
        x2_f1.append(np.random.normal(1, 1))
    else:
        x2_f1.append(np.random.normal(-1, 1))

x1_f1 = np.array(x1_f1)
x2_f1 = np.array(x2_f1)
f1_data = np.vstack((x1_f1, x2_f1)).T

# Step 2: Apply Bayes' rule to determine the optimal decision

# For data under H0
f0_likelihood_f0 = np.exp(-0.5 * (f0_data ** 2).sum(axis=1))
f1_likelihood_f0 = 0.5 * (
    np.exp(-0.5 * ((f0_data - 1) ** 2).sum(axis=1)) +
    np.exp(-0.5 * ((f0_data + 1) ** 2).sum(axis=1))
)
decisions_f0 = f1_likelihood_f0 > f0_likelihood_f0

# For data under H1
f0_likelihood_f1 = np.exp(-0.5 * (f1_data ** 2).sum(axis=1))
f1_likelihood_f1 = 0.5 * (
    np.exp(-0.5 * ((f1_data - 1) ** 2).sum(axis=1)) +
    np.exp(-0.5 * ((f1_data + 1) ** 2).sum(axis=1))
)
decisions_f1 = f1_likelihood_f1 > f0_likelihood_f1

# Step 3: Compute the percentage of wrong decisions
error_f0 = np.mean(decisions_f0)  # Deciding H1 when H0 is true
error_f1 = np.mean(~decisions_f1)  # Deciding H0 when H1 is true

# Step 4: Calculate the total probability of error
total_error_probability = 0.5 * (error_f0 + error_f1)

# Display the results
print(f"Error probability for H0: {error_f0:.4f}")
print(f"Error probability for H1: {error_f1:.4f}")
print(f"Total probability of error: {total_error_probability:.4f}")

# Step 5: Plot the results
labels = ['H0 Error', 'H1 Error', 'Total Error']
values = [error_f0, error_f1, total_error_probability]

plt.figure(figsize=(10, 6))
plt.bar(labels, values, color=['blue', 'orange', 'green'])
plt.xlabel('Error Type')
plt.ylabel('Probability')
plt.title('Error Probabilities for H0, H1, and Total')
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
