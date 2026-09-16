
"""
================================================================================
       B R A N C H   &   B O U N D   –  TINY  3‑VAR ILP (PuLP VERSION)
================================================================================
**Purpose:**
This script demonstrates a manual Branch‑and‑Bound (B&B) algorithm to solve the
small integer linear program:

    maximize   z = 34·x₁ + 29·x₂ + 2·x₃
    subject to 7·x₁ + 5·x₂ − x₃ ≤ 16
               −x₁ + 3·x₂ + x₃ ≤ 10
                      −x₂ + 2·x₃ ≤ 3
               x₁, x₂, x₃ ≥ 0 and integer

It uses PuLP (CBC solver) for LP relaxations and hand‑coded recursion for
branching, bounding, and pruning.  Outputs include an ASCII search tree and a
table of all integer solutions found.
================================================================================
"""

# -----------------------------------------------------------------------------
# 0. IMPORTS
# -----------------------------------------------------------------------------
import pulp as pl                    # PuLP modelling library (CBC solver)
from tabulate import tabulate        # tabular display of solutions
import math                          # floor, ceil, infinite values

# -----------------------------------------------------------------------------
# 1. PROBLEM DATA
# -----------------------------------------------------------------------------
# List of objective coefficients [c1, c2, c3] corresponding to x₁,x₂,x₃
OBJ = [34, 29, 2]
# Constraint coefficients and right‑hand sides: (a1, a2, a3, b)
ROWS = [
    ( 7,  5, -1, 16),  # 7*x1 + 5*x2 - x3 ≤ 16
    (-1,  3,  1, 10),  # -x1 + 3*x2 + x3 ≤ 10
    ( 0, -1,  2,  3)   # -x2 + 2*x3 ≤ 3
]
# Total number of decision variables
NUM_VARS = 3

# -----------------------------------------------------------------------------
# 2. LP RELAXATION SOLVER
# -----------------------------------------------------------------------------
def solve_lp(fixed):
    """
    Build and solve the LP relaxation fixing xᵢ variables as specified.

    Args:
        fixed (dict): mapping from variable index (1,2,3) to an integer value
                       to enforce x[i] == fixed[i] at this node.
    Returns:
        status (str): solver status string, e.g. "Optimal" or "Infeasible".
        obj    (float): objective value (−∞ or +∞ signals infeasibility).
        vals   (dict): continuous solution values {i: x_i} if optimal.
    """
    # 2.1 Create an LP maximization problem named "ILP_relax"
    prob = pl.LpProblem(name="ILP_relax", sense=pl.LpMaximize)

    # 2.2 Define continuous decision variables x1,x2,x3 ≥ 0
    # Each x[i] is an LpVariable with lower bound 0
    x = {i: pl.LpVariable(f"x{i}", lowBound=0, cat='Continuous')
         for i in range(1, NUM_VARS+1)}

    # 2.3 Add the objective: maximize Σ_{i=1..3} OBJ[i-1] * x[i]
    prob += pl.lpSum(OBJ[i-1] * x[i] for i in x), "Objective"

    # 2.4 Add the original linear constraints from ROWS
    # Each constraint: a1*x1 + a2*x2 + a3*x3 ≤ b
    for idx, (a1, a2, a3, b) in enumerate(ROWS, start=1):
        prob += (a1*x[1] + a2*x[2] + a3*x[3] <= b), f"Row{idx}"

    # 2.5 Add branch fixings: enforce x[i] == fixed[i]
    for i, val in fixed.items():
        prob += (x[i] == val), f"Fix_x{i}"

    # 2.6 Solve the LP relaxation using CBC (silent mode)
    prob.solve(pl.PULP_CBC_CMD(msg=False))

    # 2.7 Retrieve solver status
    status = pl.LpStatus[prob.status]
    # If not optimal, treat as infeasible in B&B
    if status != "Optimal":
        return status, float('inf'), {}

    # 2.8 Retrieve objective value and variable values
    obj = pl.value(prob.objective)             # objective result
    vals = {i: x[i].value() for i in x}        # dictionary of x1,x2,x3

    # 2.9 Return status, obj bound, and continuous solution
    return status, obj, vals

# -----------------------------------------------------------------------------
# 3. NODE CLASS DEFINITION
# -----------------------------------------------------------------------------
class Node:
    """
    Represents a node in the Branch & Bound tree.
    Each node stores LP relaxation results and branch decisions.
    """
    def __init__(self, fixed):
        # fixed: dictionary of variable fixings at this node
        self.fixed = dict(fixed)              # copy to prevent side‑effects
        # Solve the LP relaxation with these fixings
        self.status, self.obj, self.vals = solve_lp(self.fixed)
        # Children: list of (branch_condition_str, Node) tuples
        self.children = []
        # Flag this node if it yields an integer solution
        self.is_sol = False

    def is_integer(self):
        """Check if LP solution is integer across all variables."""
        # For each x_i, check distance to nearest integer < tolerance
        for i, v in self.vals.items():
            if abs(v - round(v)) > 1e-6:
                return False
        return True

    def branch_var(self):
        """Select the variable index with largest fractional part to branch on."""
        fracs = []  # list of (fractional_part, index)
        for i, v in self.vals.items():
            frac = abs(v - math.floor(v))    # fractional part of v
            # Only consider proper fractions (not near-0 or near-1)
            if frac > 1e-6 and frac < 1 - 1e-6:
                fracs.append((frac, i))
        # If no fractional vars, return None
        if not fracs:
            return None
        # Pick the var with maximal fractional part
        return max(fracs)[1]

# -----------------------------------------------------------------------------
# 4. BRANCH & BOUND SEARCH FUNCTION
# -----------------------------------------------------------------------------
def branch_and_bound():
    """
    Perform depth-first Branch & Bound on the ILP.
    Returns root node and list of integer solutions found.
    """
    solutions = []                 # list to collect integer solutions
    best_obj = -math.inf           # best integer objective found so far
    # Create root node with no fixed variables
    root = Node(fixed={})

    def explore(node):
        """Recursive DFS exploration of B&B tree."""
        nonlocal best_obj
        # 4.1 Prune if LP infeasible or bound ≤ best_obj
        if node.status != "Optimal":
            return
        if node.obj <= best_obj + 1e-9:
            return

        # 4.2 If integer solution, record and prune
        if node.is_integer():
            sol = {i: int(round(v)) for i, v in node.vals.items()}
            node.is_sol = True                    # mark leaf
            solutions.append(sol)                 # store solution
            best_obj = node.obj                   # update incumbent
            return

        # 4.3 Otherwise select variable to branch on
        i = node.branch_var()                    # index 1..3
        # Lower branch value = floor(v)
        lo = math.floor(node.vals[i])
        # Upper branch value = lo + 1
        hi = lo + 1

        # 4.4 Create left child (xᵢ = lo)
        fixed_lo = dict(node.fixed)              # copy current fixings
        fixed_lo[i] = lo                         # add new fixing
        left = Node(fixed_lo)                    # create node and solve LP
        node.children.append((f"x{i} = {lo}", left))
        explore(left)                            # DFS on left branch

        # 4.5 Create right child (xᵢ = hi)
        fixed_hi = dict(node.fixed)              # copy current fixings
        fixed_hi[i] = hi                         # add new fixing
        right = Node(fixed_hi)                   # create node and solve LP
        node.children.append((f"x{i} = {hi}", right))
        explore(right)                           # DFS on right branch

    # Launch DFS from root
    explore(root)
    return root, solutions

# -----------------------------------------------------------------------------
# 5. ASCII TREE PRINTING FUNCTION
# -----------------------------------------------------------------------------
def print_tree(node, prefix="", is_last=True):
    """
    Print the B&B tree in ASCII form with box connectors.
    """
    # Choose connector based on sibling position
    connector = "└── " if is_last else "├── "
    # Start line with prefix and connector
    line = prefix + connector

    # Append node status and bound
    if node.status != "Optimal":
        line += "INFEASIBLE"
    else:
        line += f"z={node.obj:.2f}"                   # LP bound
        # Append fractional solution in brackets
        vals_str = ", ".join(f"x{i}={node.vals[i]:.2f}" for i in sorted(node.vals))
        line += f"  [{vals_str}]"
        # Mark integer solution leaves
        if node.is_sol:
            sol_tup = tuple(int(round(node.vals[i])) for i in sorted(node.vals))
            line += f" ← SOL={sol_tup}"
    print(line)

    # Prepare prefix for children lines
    if is_last:
        child_prefix = prefix + "    "
    else:
        child_prefix = prefix + "│   "

    # Recursively print each child branch
    for idx, (cond, child) in enumerate(node.children):
        # Print branch condition for this child
        branch_conn = "└── " if idx == len(node.children)-1 else "├── "
        print(child_prefix + branch_conn + cond)
        # Recurse into child node
        print_tree(child,
                   prefix=child_prefix + ("    " if idx == len(node.children)-1 else "│   "),
                   is_last=True)

# -----------------------------------------------------------------------------
# 6. PRINT SOLUTIONS TABLE
# -----------------------------------------------------------------------------
def print_solutions(sols):
    """
    Print all integer-feasible solutions in a formatted table.
    """
    table = []
    for sol in sols:
        # Build row: x₁, x₂, x₃, z
        row = [sol[i] for i in sorted(sol)]
        z_val = sum(OBJ[j-1] * sol[j] for j in sorted(sol))  # compute objective
        row.append(z_val)
        table.append(row)
    # Define headers
    headers = ["x1", "x2", "x3", "z"]
    # Print with GitHub-flavored markdown table style
    print(tabulate(table, headers=headers, tablefmt="github", showindex=True))

# -----------------------------------------------------------------------------
# 7. MAIN EXECUTION
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Run Branch & Bound search
    root, sols = branch_and_bound()
    # Print the search tree
    print("\n==== Branch & Bound Search Tree ====")
    print_tree(root)
    # Print the integer solutions found
    print("\n==== Integer Solutions Found ====")
    print_solutions(sols)
