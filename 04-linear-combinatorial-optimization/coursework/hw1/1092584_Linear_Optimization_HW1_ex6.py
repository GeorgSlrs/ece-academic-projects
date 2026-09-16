import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# =============================================================================
# SIMPLEX ALGORITHM IMPLEMENTATION WITH EXTENSIVE COMMENTS AND DETAILED PRINTING
#
# LP PROBLEM:
#   Maximize:   Z = 2x₁ + x₂ + 6x₃ - 4x₄
#   Subject to:
#       x₁ + 2x₂ + 4x₃ - x₄      + s₁ = 6
#       2x₁ + 3x₂ - x₃ + x₄      + s₂ = 12
#       x₁      + x₃ + x₄        + s₃ = 2
#
# VARIABLES:
#   Decision variables: x₁, x₂, x₃, x₄
#   Slack variables:    s₁, s₂, s₃
#
# TABLEAU FORMAT:
#   - Total Rows: 4 (Rows 0-2: Constraint equations; Row 3: Objective function)
#   - Total Columns: 8, arranged as:
#         [ x₁, x₂, x₃, x₄ | s₁, s₂, s₃ | RHS ]
#
# EXPLANATORY COMMENTS:
#
# 1. MINIMUM RATIO TEST:
#    For a chosen incoming variable (with positive coefficient in the objective row),
#    compute for each constraint row (with positive coefficient in that column):
#         ratio = (B⁻¹ * b)_i / (B⁻¹ * N)_{i,α}
#    The smallest ratio indicates the binding constraint; the basic variable in that row is chosen
#    to leave the basis.
#
# 2. GAUSSIAN ELIMINATION (DRIVING):
#    The pivot element (guide element) is at the intersection of the pivot row and column.
#    - Normalize the pivot row by dividing by the pivot element.
#    - Eliminate the pivot column in every other row by subtracting an appropriate multiple
#      of the normalized pivot row.
#
# 3. SELECTING A NEW BASIC VARIABLE:
#    A candidate incoming variable is one with a positive coefficient in the objective row.
#
# 4. STOPPING CRITERIA:
#    - If no positive coefficient exists in the objective row, the solution is optimal.
#    - If for an incoming variable all coefficients in that column are ≤ 0, the LP is unbounded.
#    - If any basic variable value (B⁻¹ * b) is negative, the solution is infeasible.
#
# 5. CHOOSING THE OUTGOING VARIABLE:
#    Determined by the minimum ratio test; if there are ties, branch on all possibilities.
#
# 6. VARIABLE SWAP (EXCHANGE):
#    After pivoting, the incoming variable replaces the outgoing variable in the basis.
#
# 7. GUIDE ELEMENT:
#    The pivot element used during Gaussian elimination.
#
# 8. SIMPLEX ADJACENCY GRAPH (SAG):
#    - Each node represents a distinct tableau state.
#    - Each node is labeled with:
#         B = {…}  (the current basis using 1-based indexing),
#         BFS = (x₁, x₂, x₃, x₄)  (the values of the decision variables),
#         z = actual objective value.
#    - Edges are labeled with pivot decisions (formatted as “+xᵢ / -xⱼ”).
#    - The optimal node is colored differently (lime green).
#
# 9. PRINTING:
#    Every iteration prints the complete tableau, details of the pivot (elimination steps, factors),
#    and the pivot decisions.
#
# =============================================================================

def get_bfs_and_objective(tableau, basis):
    """
    Computes the basic feasible solution (BFS) and the actual objective value.
    
    The tableau is arranged so that the first m-1 rows are constraints and the last row is the objective.
    Since the tableau stores -Z in the objective row, the actual objective value Z is computed as
    - (RHS of the objective row).
    
    Parameters:
      tableau: 2D numpy array representing the current simplex tableau.
      basis:   List of indices corresponding to the basic variables.
    
    Returns:
      bfs: A numpy array with the values for all variables.
      obj_val: The actual objective value Z.
    """
    m, n = tableau.shape
    num_vars = n - 1  # Exclude the RHS column
    bfs = np.zeros(num_vars)
    for i in range(m - 1):
        bfs[basis[i]] = tableau[i, -1]
    # Convert -Z (stored in the tableau) to the actual objective value Z.
    obj_val = -tableau[-1, -1]
    return bfs, obj_val

def create_node_label(basis, bfs, obj_val):
    """
    Creates a label for a node in the SAG.
    
    The label includes:
      - B = {…} : The current basis (with 1-based indexing).
      - BFS = (x₁, x₂, x₃, x₄) : The values of all four decision variables.
      - z = actual objective value.
    
    Returns a formatted string.
    """
    # Convert basis indices to 1-based for clarity.
    basis_str = "{" + ",".join(str(b + 1) for b in basis) + "}"
    # Show values for x₁, x₂, x₃, and x₄ from the BFS.
    bfs_str = "(" + ", ".join(f"{bfs[i]:.2f}" for i in range(4)) + ")"
    label_str = f"B={basis_str}\nBFS={bfs_str}\nz={obj_val:.2f}"
    return label_str

def print_tableau(tableau, basis, node_name):
    """
    Prints the current simplex tableau with a header showing the node name.
    
    The tableau columns are:
      [ x₁, x₂, x₃, x₄, s₁, s₂, s₃, RHS ]
    
    Rows 0 to m-2 correspond to constraints (each with its basic variable), and row m-1 is the objective row.
    """
    m, n = tableau.shape
    num_vars = n - 1  # Exclude RHS

    print(f"\n--- Simplex Tableau at node: {node_name} ---")
    print("-" * 85)
    for i in range(m - 1):
        row_vals = " | ".join(f"{tableau[i, j]:8.3f}" for j in range(num_vars))
        print(f"Constraint {i+1}: {row_vals} || RHS = {tableau[i, -1]:8.3f} | Basic var: x_{basis[i]+1}")
    obj_vals = " | ".join(f"{tableau[m-1, j]:8.3f}" for j in range(num_vars))
    print(f"Objective   : {obj_vals} || Value = {tableau[m-1, -1]:8.3f}")
    print("-" * 85)

def pivot_operation(tableau, pivot_row, pivot_col):
    """
    Performs the pivot operation (Gaussian elimination) on the tableau.
    
    Steps:
      1. Identify the pivot element (guide element) at (pivot_row, pivot_col).
      2. Normalize the pivot row by dividing each element by the pivot element.
      3. For every other row, eliminate the pivot column by subtracting the multiple of
         the normalized pivot row.
    
    Detailed prints describe:
      - The pivot element.
      - The normalization of the pivot row.
      - The elimination factor for each other row and the updated row.
    
    Returns:
      A new tableau after performing the pivot.
    """
    new_tab = np.copy(tableau)
    pivot_elem = new_tab[pivot_row, pivot_col]
    print(f"\n=== Pivot Operation ===")
    print(f"Pivot element (guide) at (row {pivot_row}, col {pivot_col}) = {pivot_elem:.3f}")

    # Normalize the pivot row.
    print(f"Normalizing row {pivot_row} by dividing by {pivot_elem:.3f}.")
    new_tab[pivot_row, :] /= pivot_elem
    print(f"Row {pivot_row} after normalization: {new_tab[pivot_row, :]}")

    # Eliminate the pivot column in all other rows.
    m, _ = new_tab.shape
    for r in range(m):
        if r != pivot_row:
            factor = new_tab[r, pivot_col]
            if abs(factor) > 1e-12:
                print(f"\nEliminating pivot column from row {r} using factor = {factor:.3f}")
                old_row = new_tab[r, :].copy()
                new_tab[r, :] -= factor * new_tab[pivot_row, :]
                print(f"Old row {r}: {old_row}")
                print(f"New row {r}: {new_tab[r, :]}")
    return new_tab

def find_entering_variables(tableau):
    """
    Identifies candidate entering variables.
    
    A variable is eligible to enter if its coefficient in the objective row (ignoring the RHS)
    is positive.
    
    Returns:
      A list of column indices for candidate entering variables.
    """
    obj_row = tableau[-1, :-1]
    candidates = []
    print("\nIdentifying entering variables (positive coefficients in the objective row):")
    for j, coeff in enumerate(obj_row):
        if coeff > 1e-8:
            print(f"  Variable x_{j+1} with coefficient {coeff:.3f} is a candidate.")
            candidates.append(j)
    return candidates

def find_leaving_variables(tableau, pivot_col):
    """
    Applies the MINIMUM RATIO TEST to select candidate leaving variables.
    
    For the chosen pivot column, for each constraint row with a positive coefficient,
    compute:
         ratio = (RHS value) / (coefficient in pivot column)
    The row(s) with the smallest ratio indicate the binding constraint; the basic variable
    in that row is chosen to leave.
    
    Returns:
      A list of row indices for candidate leaving variables.
    """
    m = tableau.shape[0] - 1  # Exclude objective row.
    min_ratio = float('inf')
    candidates = []
    print(f"\nPerforming Minimum Ratio Test for pivot column {pivot_col} (variable x_{pivot_col+1}):")
    for i in range(m):
        coeff = tableau[i, pivot_col]
        if coeff > 1e-8:
            ratio = tableau[i, -1] / coeff
            print(f"  Row {i}: Coefficient = {coeff:.3f}, RHS = {tableau[i, -1]:.3f}, Ratio = {ratio:.3f}")
            if ratio < min_ratio - 1e-12:
                min_ratio = ratio
                candidates = [i]
            elif abs(ratio - min_ratio) < 1e-12:
                candidates.append(i)
    if not candidates:
        print("  No valid leaving variable found (all entries in pivot column ≤ 0) => LP is unbounded.")
    else:
        print(f"  Minimum ratio = {min_ratio:.3f} in row(s): {candidates}")
    return candidates

def tuple_key(bfs, obj_val, tol=1e-5):
    """
    Create a tuple key from the first four decision variables of BFS and the objective value.
    This key is used to identify duplicate optimal solutions.
    """
    return tuple(np.round(bfs[:4], decimals=5)) + (round(obj_val, 5),)

def simplex_recursive(tableau, basis, graph, node_id, path_desc, steps, solutions, max_depth=15):
    """
    Recursively executes the Simplex algorithm, exploring all pivot paths and building the
    Simplex Adjacency Graph (SAG).
    
    Process:
      1. Print the current tableau with node information.
      2. Check feasibility: All constraint rows must have non-negative RHS.
      3. Check optimality: If no candidate entering variable exists, the current solution is optimal.
      4. For each candidate entering variable:
             - Apply the minimum ratio test to determine candidate leaving variable(s).
             - For each candidate leaving variable:
                   a) Print detailed pivot decision (incoming/outgoing, pivot element, ratio).
                   b) Perform the pivot operation (Gaussian elimination) and print elimination steps.
                   c) Swap the basic variable (incoming replaces outgoing).
                   d) Compute the new BFS and actual objective value.
                   e) Create a new node in the SAG with a label showing B, BFS (for x₁, x₂, x₃, x₄), and Z.
                   f) Recurse on the new tableau with updated path.
      5. Stop if the solution is optimal, unbounded, infeasible, or if maximum recursion depth is reached.
    
    Note:
      The objective row stores -Z; thus, the actual objective value is computed as - (RHS of objective).
    
    Parameters:
      tableau: Current simplex tableau (numpy array).
      basis: List of indices representing the current basic variables.
      graph: NetworkX DiGraph used to build the SAG.
      node_id: String identifier for the current node.
      path_desc: Cumulative description of the pivot path taken.
      steps: List recording each iteration step (for debugging).
      solutions: List to store optimal solutions as (BFS, objective, path).
      max_depth: Maximum recursion depth.
    """
    m, n = tableau.shape
    num_constraints = m - 1

    print(f"\n{'=' * 100}\nNode: {node_id}, Path: {path_desc}")
    print_tableau(tableau, basis, node_id)

    # Feasibility check: Each constraint row must have RHS >= 0.
    for i in range(num_constraints):
        if tableau[i, -1] < -1e-8:
            print(f"Infeasible: Row {i} has negative RHS ({tableau[i, -1]:.3f}). Terminating branch.")
            return

    # Optimality check: If no entering variable exists, then the current solution is optimal.
    entering_vars = find_entering_variables(tableau)
    if not entering_vars:
        print("\nNo entering variable found. This solution is optimal!")
        bfs, obj_val = get_bfs_and_objective(tableau, basis)
        print("\n********** OPTIMAL SOLUTION FOUND **********")
        for i, val in enumerate(bfs[:4]):  # Show x1, x2, x3, x4
            print(f"x_{i+1} = {val:.3f}")
        print(f"Objective Value (Z) = {obj_val:.3f}")
        print("**********************************************\n")
        key = tuple_key(bfs, obj_val)
        # Check for duplicate optimal solution to avoid multiple identical optimal nodes.
        if key not in optimal_node_mapping:
            optimal_node_mapping[key] = node_id
            solutions.append((bfs, obj_val, path_desc))
            graph.nodes[node_id]['optimal'] = True  # Mark this node as optimal.
        else:
            existing = optimal_node_mapping[key]
            if not graph.has_edge(node_id, existing):
                graph.add_edge(node_id, existing, label="(merged optimal)")
        return

    # Check recursion depth.
    if max_depth <= 0:
        print("Maximum recursion depth reached. Terminating branch.")
        steps.append((node_id, "Depth limit reached", tableau))
        return

    # Process each candidate entering variable.
    for pivot_col in entering_vars:
        print(f"\n>>> Considering incoming variable x_{pivot_col+1} (Obj coeff = {tableau[-1, pivot_col]:.3f})")
        leaving_candidates = find_leaving_variables(tableau, pivot_col)
        if not leaving_candidates:
            print(f"Unbounded direction for x_{pivot_col+1}. Skipping candidate.")
            continue
        for pivot_row in leaving_candidates:
            outgoing_var = basis[pivot_row]
            pivot_elem = tableau[pivot_row, pivot_col]
            ratio_val = tableau[pivot_row, -1] / pivot_elem
            decision_desc = (f"Pivot Decision: Incoming x_{pivot_col+1}, Outgoing x_{outgoing_var+1}, "
                             f"Pivot = {pivot_elem:.3f}, Ratio = {ratio_val:.3f}")
            print(f"\n{decision_desc}")

            # Create new node identifier.
            new_node_id = f"{node_id}->({pivot_row},{pivot_col})"
            graph.add_node(new_node_id, tableau=tableau, desc=decision_desc)
            edge_label = f"+x{pivot_col+1}/-x{outgoing_var+1}"
            graph.add_edge(node_id, new_node_id, label=edge_label)
            steps.append((new_node_id, decision_desc, tableau))

            # Perform the pivot operation (Gaussian elimination).
            new_tableau = pivot_operation(tableau, pivot_row, pivot_col)

            # Swap the basic variable: incoming variable replaces outgoing in the basis.
            new_basis = basis.copy()
            new_basis[pivot_row] = pivot_col
            print(f"Swapping in basis: x_{pivot_col+1} enters, x_{outgoing_var+1} leaves.")

            # Compute the new BFS and actual objective value.
            bfs, obj_val = get_bfs_and_objective(new_tableau, new_basis)
            label_str = create_node_label(new_basis, bfs, obj_val)
            graph.nodes[new_node_id]['label'] = label_str

            new_path_desc = path_desc + f" -> (+x_{pivot_col+1}, -x_{outgoing_var+1})"
            simplex_recursive(new_tableau, new_basis, graph, new_node_id, new_path_desc, steps, solutions, max_depth - 1)

def plot_sag(graph):
    """
    Plots the Simplex Adjacency Graph (SAG) using a shell_layout for a neat radial appearance.
    
    Appearance Details:
      - Nodes are arranged in concentric circles.
      - Each node displays its label (which includes B, BFS for x₁, x₂, x₃, x₄, and the actual Z).
      - Optimal nodes (where an optimal solution was reached) are colored lime green; others are light blue.
      - Edge labels show pivot decisions in the format "+xᵢ / -xⱼ".
      - Node labels are drawn with elliptical bounding boxes.
    """
    pos = nx.shell_layout(graph, scale=2)
    plt.figure(figsize=(12, 8))

    # Color nodes: optimal nodes in lime green; non-optimal in light blue.
    node_colors = []
    for node in graph.nodes():
        if graph.nodes[node].get('optimal', False):
            node_colors.append('limegreen')
        else:
            node_colors.append('lightblue')

    nx.draw_networkx_nodes(graph, pos, node_size=2000, node_color=node_colors, alpha=0.9)
    nx.draw_networkx_edges(graph, pos, arrows=True, arrowstyle='->', width=2)

    # Retrieve node labels from the 'label' attribute.
    node_labels = nx.get_node_attributes(graph, 'label')
    for n in graph.nodes():
        if n not in node_labels:
            node_labels[n] = n
    nx.draw_networkx_labels(
        graph, pos, labels=node_labels, font_size=10,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.9)
    )

    # Draw edge labels for pivot decisions.
    edge_labels = nx.get_edge_attributes(graph, 'label')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=9)

    plt.title("Simplex Adjacency Graph (SAG)")
    plt.axis("off")
    plt.show()

# Global dictionary to avoid duplicate optimal nodes in the graph.
optimal_node_mapping = {}

def tuple_key(bfs, obj_val, tol=1e-5):
    """
    Create a tuple key from the first four decision variables of BFS and the objective value.
    This key is used to identify duplicate optimal solutions.
    """
    return tuple(np.round(bfs[:4], decimals=5)) + (round(obj_val, 5),)

def simplex_recursive_with_duplicate_check(tableau, basis, graph, node_id, path_desc, steps, solutions, max_depth=15):
    """
    Wrapper for simplex_recursive that could incorporate duplicate optimal solution check.
    Currently, simplex_recursive already uses a global mapping to avoid duplicates.
    """
    simplex_recursive(tableau, basis, graph, node_id, path_desc, steps, solutions, max_depth)

def main():
    """
    Main function to set up the LP, run the Simplex algorithm, build the SAG,
    and display the final optimal solution.
    
    LP DETAILS:
      Maximize:   Z = 2x₁ + x₂ + 6x₃ - 4x₄
      Subject to:
          x₁ + 2x₂ + 4x₃ - x₄      + s₁ = 6
          2x₁ + 3x₂ - x₃ + x₄      + s₂ = 12
          x₁      + x₃ + x₄        + s₃ = 2
      All variables are nonnegative.
    
    TABLEAU:
      - 4 rows (3 constraints + 1 objective).
      - 8 columns: [x₁, x₂, x₃, x₄, s₁, s₂, s₃, RHS].
      - The objective row stores -Z, so the actual objective is - (RHS of objective).
      - Initial basis is the slack variables s₁, s₂, s₃ (columns 4, 5, 6).
    
    FINAL OUTPUT:
      - Detailed printed output for each pivot step.
      - A SAG where each node is labeled with B, BFS (x₁, x₂, x₃, x₄), and actual objective value.
      - Optimal nodes are colored lime green; others are light blue.
      - Duplicate optimal nodes are merged.
      - The final optimal BFS (for x₁, x₂, x₃, x₄) and objective value are printed.
    """
    # Construct the initial tableau.
    tableau = np.array([
        [1,  2,  4, -1,  1,  0,  0,  6],   # Constraint 1: x₁ + 2x₂ + 4x₃ - x₄ + s₁ = 6
        [2,  3, -1,  1,  0,  1,  0, 12],   # Constraint 2: 2x₁ + 3x₂ - x₃ + x₄ + s₂ = 12
        [1,  0,  1,  1,  0,  0,  1,  2],   # Constraint 3: x₁ + x₃ + x₄ + s₃ = 2
        [2,  1,  6, -4,  0,  0,  0,  0]    # Objective row: Maximize Z = 2x₁ + x₂ + 6x₃ - 4x₄ (stored as -Z)
    ], dtype=float)

    # Initial basis: slack variables s₁, s₂, s₃ are basic (columns 4, 5, 6).
    basis = [4, 5, 6]

    # Create the Simplex Adjacency Graph (SAG) as a directed graph.
    graph = nx.DiGraph()
    root_node = "v0"
    graph.add_node(root_node)
    steps = []      # List to record each recursion step.
    solutions = []  # List to store optimal solutions.

    # Compute the BFS and actual objective value at the root.
    bfs, obj_val = get_bfs_and_objective(tableau, basis)
    label_str = create_node_label(basis, bfs, obj_val)
    # Set attributes for the root node.
    nx.set_node_attributes(graph, {root_node: {'label': label_str, 'BFS': bfs, 'objective': obj_val, 'basis': basis}})
    print(f"Root node '{root_node}' created with label:")
    print(label_str)

    # Run the recursive Simplex algorithm.
    simplex_recursive(tableau, basis, graph, root_node, "Start", steps, solutions, max_depth=15)

    # Plot the Simplex Adjacency Graph.
    plot_sag(graph)

    # Print the final optimal solution(s) if found.
    if solutions:
        print("\n========== FINAL OPTIMAL SOLUTION(S) ==========")
        for sol, val, path in solutions:
            print(f"Optimal BFS (x₁, x₂, x₃, x₄): {sol[:4]}")
            print(f"Optimal Objective Value: {val:.3f}")
            print(f"Path taken: {path}\n")
    else:
        print("\nNo optimal solution found (problem may be unbounded or infeasible).")

if __name__ == "__main__":
    main()
