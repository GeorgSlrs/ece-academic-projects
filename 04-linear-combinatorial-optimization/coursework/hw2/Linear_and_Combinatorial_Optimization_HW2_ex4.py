import pulp as pl                             # Import PuLP library for formulating LP problems
from tabulate import tabulate                  # Import tabulate for printing tables neatly
from asciitree import LeftAligned              # Import LeftAligned for printing ASCII trees

# ==================================================================
# 1. Problem Data Setup
# ==================================================================
# Define the list of weekdays in order; used to index coverage constraints
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Define dictionary mapping each weekday to required number of waiters
# This models daily staffing demand
need = {
    "Mon": 8,    # Requirement for Monday
    "Tue": 8,    # Requirement for Tuesday
    "Wed": 8,    # Requirement for Wednesday
    "Thu": 8,    # Requirement for Thursday
    "Fri": 15,   # Requirement for Friday (weekend starts)
    "Sat": 15,   # Requirement for Saturday (peak weekend)
    "Sun": 10    # Requirement for Sunday (wind-down)
}

# ==================================================================
# 2. Shift Definitions (5-on / 2-off cyclic schedule)
# ==================================================================
# List of sets, where each set contains the days worked by that shift index
# Shift 0 works Wed–Sun, off Mon/Tue; Shift 1 works Thu–Mon; etc.
shifts = [
    {"Wed", "Thu", "Fri", "Sat", "Sun"},  # Shift 0: off Mon/Tue
    {"Thu", "Fri", "Sat", "Sun", "Mon"},  # Shift 1: off Tue/Wed
    {"Fri", "Sat", "Sun", "Mon", "Tue"},  # Shift 2: off Wed/Thu
    {"Sat", "Sun", "Mon", "Tue", "Wed"},  # Shift 3: off Thu/Fri
    {"Sun", "Mon", "Tue", "Wed", "Thu"},  # Shift 4: off Fri/Sat
    {"Mon", "Tue", "Wed", "Thu", "Fri"},  # Shift 5: off Sat/Sun
    {"Tue", "Wed", "Thu", "Fri", "Sat"}   # Shift 6: off Sun/Mon
]

# ==================================================================
# 3. LP Relaxation Solver Function
# ==================================================================
def solve_lp(fixed):
    """
    Constructs and solves the LP relaxation with optional fixed variable values.

    Args:
        fixed (dict): mapping shift index -> fixed integer value
    Returns:
        status (str): solver status after solving
        obj (float): objective value (total waiters) from LP
        vals (dict): fractional solution values for each shift index
    """
    # Create a new LP problem instance minimizing total waiters
    prob = pl.LpProblem("Sched", pl.LpMinimize)

    # Create continuous decision variables x[j] >= 0 for j in 0..6
    x = pl.LpVariable.dicts("x", range(7), lowBound=0)

    # Add objective: minimize sum of x[j] over all shifts
    prob += pl.lpSum(x[j] for j in range(7)), "total"

    # Add coverage constraints: for each day d, sum of x[j] for shifts covering d >= need[d]
    for d in days:
        prob += (
            pl.lpSum(x[j] for j, s in enumerate(shifts) if d in s) >= need[d],
            f"cover_{d}"
        )

    # Add branch-and-bound fixings: force x[j] == val for each (j,val) in fixed
    for j, val in fixed.items():
        prob += (x[j] == val, f"fix_{j}")

    # Solve the LP using CBC solver quietly (no msg)
    prob.solve(pl.PULP_CBC_CMD(msg=False))

    # Retrieve solver status as a string (e.g., "Optimal")
    status = pl.LpStatus[prob.status]
    # Retrieve numeric objective value
    obj = pl.value(prob.objective)
    # Retrieve variable values into a dict {j: x_j}
    vals = {j: x[j].value() for j in range(7)}

    # Return status, objective, and variable values
    return status, obj, vals

# ==================================================================
# 4. Node Class for Branch & Bound
# ==================================================================
class Node:
    """
    Represents a node in the Branch & Bound search tree.

    Attributes:
        fixed  (dict): shift indices fixed at this node
        status (str) : LP solver status for this node
        obj    (float): LP objective value
        vals   (dict): LP variable assignments {j: value}
        children (list): list of (branch_condition, child_Node)
        is_sol (bool): flagged True if node corresponds to integer solution
    """
    def __init__(self, fixed):
        # Store a copy of fixed-variable decisions
        self.fixed = fixed.copy()
        # Solve LP relaxation with these fixings
        self.status, self.obj, self.vals = solve_lp(self.fixed)
        # Initialize empty list to hold child branches
        self.children = []
        # Flag to mark if this node yields an integer solution
        self.is_sol = False

    def is_integer(self):
        """
        Check if all variable values are integer (within tolerance).

        Returns:
            True if every vals[j] is within 1e-6 of an integer.
        """
        # Compare each fractional value to nearest integer
        return all(abs(v - round(v)) < 1e-6 for v in self.vals.values())

    def branch_var(self):
        """
        Select the variable with largest fractional part for branching.

        Returns:
            j (int): index of variable to branch on, or None if all integer.
        """
        # Build list of (fractional_part, index) for non-integer vars
        fracs = [((v - int(v)), j)
                 for j, v in self.vals.items()
                 if abs(v - round(v)) > 1e-6]
        # Return index of var with maximum fractional part
        return max(fracs)[1] if fracs else None

# ==================================================================
# 5. Branch & Bound Search Function
# ==================================================================
def branch_and_bound():
    """
    Perform Branch & Bound search:
      - Build full B&B tree with Node instances
      - Collect all integer-feasible solutions

    Returns:
        root      (Node): root of the B&B tree
        solutions (list of dict): all integer solutions found
    """
    # Initialize empty list for integer solutions
    solutions = []
    # Set best objective to infinity for pruning
    best = float('inf')
    # Create root node with no fixed variables
    root = Node({})

    def explore(node):
        # Use nonlocal best to update pruning threshold
        nonlocal best

        # Prune if LP not optimal or objective exceeds current best
        if node.status != "Optimal" or node.obj > best:
            return

        # If LP solution is integer, record it
        if node.is_integer():
            # Convert LP values to integers
            sol = {j: int(round(v)) for j, v in node.vals.items()}
            # Mark this node as solution leaf
            node.is_sol = True
            # Append solution dict to list
            solutions.append(sol)
            # Update best objective for pruning further
            best = min(best, sum(sol.values()))
            return

        # Otherwise, select a variable to branch on
        j = node.branch_var()
        # Compute floor and ceil values for branching decisions
        lo = int(node.vals[j] // 1)
        hi = lo + 1

        # Create left branch: x[j] <= lo
        fixed_lo = node.fixed.copy(); fixed_lo[j] = lo
        left = Node(fixed_lo)                     # Solve LP for left branch
        node.children.append((f"x[{j}] <= {lo}", left))
        explore(left)                             # Recurse into left subtree

        # Create right branch: x[j] >= hi
        fixed_hi = node.fixed.copy(); fixed_hi[j] = hi
        right = Node(fixed_hi)                    # Solve LP for right branch
        node.children.append((f"x[{j}] >= {hi}", right))
        explore(right)                            # Recurse into right subtree

    # Start recursion from root node
    explore(root)
    # Return the complete tree and solutions
    return root, solutions

# ==================================================================
# 6. Pretty-Printing Utilities and Reading Solutions from Tree
# ==================================================================
# These functions help you visualize the B&B search and extract solutions:
#  - print_solutions: tabulates each complete integer solution as a row.
#  - print_tree: renders the full B&B tree in ASCII; each leaf marked with SOL=(x0,...,x6).
#    To read off solutions from the tree:
#      1. Locate each leaf node whose label ends with ", SOL=(...)".
#      2. The SOL tuple gives the full assignment for x0–x6 at that solution.
#      3. The path of branch conditions in brackets ([x[j]<=val], etc.) shows how
#         the algorithm fixed variables to reach that leaf.
#      4. Every leaf with SOL= is one of the integer-feasible solutions (5 in total).

# ------------------------------------------------------------------
def print_solutions(sols):
    """
    Print all integer solutions in a formatted table.

    Each row corresponds to one solution, showing x0–x6 and the total.
    """
    rows = []  # List of rows for tabulate
    for sol in sols:
        # Build a row of shift values + total
        row = [sol[j] for j in range(7)]
        row.append(sum(row))
        rows.append(row)

    headers = [f"x{j}" for j in range(7)] + ["total"]
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid", showindex=1))

# ------------------------------------------------------------------
def print_tree(node, indent=0, branch_label="Root"):
    """
    Print the B&B tree in a clear boxed format, similar to a hand-drawn diagram:
      - Each node is shown as a box with z (objective) on top and x[j] values below.
      - Branch conditions (e.g., x[j] <= lo) are printed as arrows between boxes.
    Args:
      node        : Node object, contains obj, vals, children
      indent      : current indentation level (for recursive calls)
      branch_label: label for this branch (e.g., "Root" or "x[2]<=7")
    """
    # 1. Prepare indentation string
    prefix = "    " * indent
    # 2. Build content lines: first the objective, then each variable
    #    Format objective as z=... and variables as x[j]=value
    header = f"z={node.obj:.2f}"                        # Objective label
    var_lines = [f"x{j}={node.vals[j]:.2f}" for j in sorted(node.vals)]
    content = [header] + var_lines                        # All lines to box
    # 3. Determine box width (longest line plus padding)
    width = max(len(line) for line in content) + 2        # 1 space padding each side
    # 4. Print top border of box
    print(prefix + "+" + "-" * width + "+")
    # 5. Print each line inside box, left-aligned
    for line in content:
        print(prefix + "| " + line.ljust(width-1) + "|")
    # 6. Print bottom border of box
    print(prefix + "+" + "-" * width + "+")
    # 7. If this node is marked as an integer solution, annotate it
    if node.is_sol:
        assign = tuple(int(round(node.vals[j])) for j in sorted(node.vals))
        print(prefix + f"=> SOLUTION: x0–x6 = {assign}")
    # 8. Recurse into children with arrow labels
    for cond, child in node.children:
        # Print the branch condition arrow
        print(prefix + f"   |-- [{cond}]")
        # Recursive call with increased indentation
        print_tree(child, indent+1, cond)
# Note: 'branch_label' is used only for initial call and not printed per-node in this style

# ==================================================================
# 7. Main Execution Block
# ==================================================================
if __name__ == "__main__":
    # Build the B&B tree and collect solutions
    root, sols = branch_and_bound()

    # 7.1 Print the tree in boxed format
    print("==== Tree Diagram ==== ")
    print_tree(root)

    # 7.2 Print all solutions in a table
    print("==== All Solutions ==== ")
    print_solutions(sols)

   