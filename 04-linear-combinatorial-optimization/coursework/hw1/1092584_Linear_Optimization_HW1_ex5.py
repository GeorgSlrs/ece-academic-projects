import numpy as np
from itertools import combinations

# -------------------------------
# Part 1: Define the problem data
# -------------------------------

# Variable labels corresponding to the 7 columns:
# x1, x2, x3 are the original decision variables and s1, s2, s3, s4 are the slack variables.
var_labels = ['x1', 'x2', 'x3', 's1', 's2', 's3', 's4']

# Define matrix A (4x7) and vector b.
A = np.array([
    [-1, -1,  0, -1,  0,  0,  0],
    [ 0, -1, -1,  0, -1,  0,  0],
    [-1,  0, -1,  0,  0, -1,  0],
    [20, 10, 15,  0,  0,  0,  1]
], dtype=float)

b = np.array([-10, -15, -12, 300], dtype=float)

# Tolerance for numerical comparisons.
tol = 1e-9

# -------------------------------
# Part 2: Enumerate Basic Solutions
# -------------------------------

# Lists to store solutions and singular bases.
basic_solutions = []   # For bases with invertible B
singular_bases = []    # For combinations where B is singular

# Iterate over all combinations of 4 columns (from the 7 columns) to form potential bases.
for basis in combinations(range(7), 4):
    # Extract the submatrix B corresponding to the chosen columns.
    B = A[:, basis]
    
    # Check if B is nonsingular (i.e. full rank = 4).
    if np.linalg.matrix_rank(B) == 4:
        # Compute the basic variables: x_B = B^-1 * b.
        xB = np.linalg.solve(B, b)
        
        # Form the full solution vector (length 7) with nonbasic variables set to 0.
        full_solution = np.zeros(7)
        for i, idx in enumerate(basis):
            full_solution[idx] = xB[i]
            
        # Check feasibility: all basic variables must be >= 0.
        if np.all(xB >= -tol):
            feasible = True
            # If all basic variables are strictly > 0, then the solution is nondegenerate.
            if np.all(xB > tol):
                degenerate = False
            else:
                degenerate = True
        else:
            feasible = False
            degenerate = None  # Not applicable when not feasible.

        # Store the details for this basic solution.
        basic_solutions.append({
            'basis_indices': basis,                                # 0-indexed column positions.
            'basis_labels': tuple(var_labels[i] for i in basis),     # Corresponding variable labels.
            'x_B': xB,                                             # Computed basic variables (B^-1 * b).
            'full_solution': full_solution,                        # Full solution vector of length 7.
            'feasible': feasible,
            'degenerate': degenerate
        })
    else:
        # Record the basis (combination of columns) for which B is singular (noninvertible).
        singular_bases.append({
            'basis_indices': basis,
            'basis_labels': tuple(var_labels[i] for i in basis)
        })

# -------------------------------
# Part 3: Define the Given Vertices
# -------------------------------
# Vertices given in the problem with (x1, x2, x3) coordinates:
vertices = {
    'A': np.array([3.5, 6.5, 8.5]),
    'B': np.array([5.0, 5.0, 10.0]),
    'C': np.array([6.0, 9.0, 6.0]),
    'D': np.array([0.0, 10.0, 12.0]),
    'E': np.array([0.0, 10.0, 40/3]),  # 40/3 ≈ 13.3333
    'F': np.array([0.0, 12.0, 12.0])
}

# -------------------------------
# Part 4: Display Basic Solutions
# -------------------------------
print("Total number of basic solutions (invertible bases) found:", len(basic_solutions))
print("----------------------------------------------------------")
print("Details of each basic solution:")

for sol in basic_solutions:
    print("Basis indices (0-indexed):", sol['basis_indices'])
    print("Basis labels:", sol['basis_labels'])
    
    # Display the calculation of B^-1 * b (the basic variables) with labels.
    print("Calculation of B^-1 * b (basic variables):")
    for i, label in enumerate(sol['basis_labels']):
        print("  {} = {:.4f}".format(label, sol['x_B'][i]))
        
    # Display the full 7-dimensional solution vector with variable labels.
    print("\nFull solution vector:")
    for i, label in enumerate(var_labels):
        print("  {} = {:.4f}".format(label, sol['full_solution'][i]))
        
    # Check if the solution matches one of the given vertices by comparing x1, x2, x3.
    x_values = sol['full_solution'][:3]  # x1, x2, x3
    matched_vertex = None
    for vertex, coords in vertices.items():
        if np.allclose(x_values, coords, atol=tol):
            matched_vertex = vertex
            break
    if matched_vertex is not None:
        print("This solution corresponds to vertex {}.".format(matched_vertex))
    else:
        print("This solution does not match any of the given vertices.")
    
    # Display feasibility and degeneracy status.
    if sol['feasible']:
        if sol['degenerate']:
            print("Status: Basic Feasible (Degenerate)")
        else:
            print("Status: Basic Feasible (Nondegenerate)")
    else:
        print("Status: Not Feasible")
    print("----------------------------------------------------------")

# -------------------------------
# Part 5: Display Singular Bases
# -------------------------------
print("Total number of singular bases (B not invertible):", len(singular_bases))
print("List of singular bases (column choices):")
for sb in singular_bases:
    print("Basis indices (0-indexed):", sb['basis_indices'], "-> Basis labels:", sb['basis_labels'])
print("----------------------------------------------------------")

# -------------------------------
# Part 6: Evaluate the Objective Function at Each Vertex
# -------------------------------
# The objective function is: Z = 8*x1 + 5*x2 + 4*x3.
print("Objective function values at the given vertices:")
obj_values = {}
for vertex, coords in vertices.items():
    Z = 8 * coords[0] + 5 * coords[1] + 4 * coords[2]
    obj_values[vertex] = Z
    print("Vertex {}: (x1,x2,x3) = {} -> Z = {:.4f}".format(vertex, coords, Z))

# Identify the optimal solution (minimum Z).
optimal_vertex = min(obj_values, key=obj_values.get)
optimal_value = obj_values[optimal_vertex]
print("----------------------------------------------------------")
print("Optimal solution (minimizing Z):")
print("Vertex {} with (x1,x2,x3) = {} and Z = {:.4f}".format(optimal_vertex, vertices[optimal_vertex], optimal_value))
