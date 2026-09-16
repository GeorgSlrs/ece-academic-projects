import pulp

# ---------------------------------------------------------
# 1. Problem data: coefficients for the dual version
# ---------------------------------------------------------
volumes = [2, 3, 4, 6, 8]    # these are the "a_i" multipliers of y in each dual row
profits = [10, 14, 31, 48, 60]  # these are the "c_i" right-hand sides for each constraint
b_rhs   = 11                 # capacity (primal RHS), used in objective (11·y)
n       = len(volumes)       # number of w_i variables (5)

# ---------------------------------------------------------
# 2. Global incumbent (best integer dual so far)
# ---------------------------------------------------------
best_val = float('inf')      # we are minimizing, so start with +∞
best_sol = None              # will hold the optimal integer-dual vector once found

# ---------------------------------------------------------
# 3. BBNode class: each node in the B&B tree
# ---------------------------------------------------------
class BBNode:
    """
    A node in the Branch-and-Bound tree storing:
      id, depth, parent_id,
      fixed decisions (dict),
      children (list of IDs),
      LP relaxation bound,
      pruned/integral flags,
      integer solution if leaf,
      branchvar (which var we branched on) and branchval.
    """
    def __init__(self, node_id, depth, parent_id, fixed):
        self.id        = node_id
        self.depth     = depth
        self.parent_id = parent_id
        self.fixed     = dict(fixed)  # copy of fixed { index → integer }
        self.children  = []           # list of child IDs
        self.bound     = None         # LP-relaxation objective
        self.pruned    = False
        self.integral  = False
        self.sol       = None         # integer vector if this node is integral
        self.branchvar = None         # index (0 for y, 1..5 for w1..w5)
        self.branchval = None         # value assigned at branching

# ---------------------------------------------------------
# 4. LP relaxation solver for given fixed decisions
# ---------------------------------------------------------
def solve_lp_relax(fixed_dict):
    """
    Build and solve the LP relaxation (continuous) of the dual,
    applying any fixed decisions from `fixed_dict`.

    Returns:
      bound    : LP objective value (float) or +inf if infeasible
      sol_vec  : list [y, w1, ..., w5] of LP values (floats)
      is_int   : True if all variables in sol_vec are (nearly) integer
    """
    # 4.1 Create PuLP problem in minimization mode
    lp = pulp.LpProblem("dual_relax", pulp.LpMinimize)

    # 4.2 Declare continuous variables y ≥ 0, w_i ≥ 0
    y = pulp.LpVariable("y", lowBound=0, cat='Continuous')
    w = [pulp.LpVariable(f"w{i+1}", lowBound=0, cat='Continuous') for i in range(n)]

    # 4.3 Impose any fixed decisions (branching constraints)
    #     We treat index 0 ⇒ y, index 1..5 ⇒ w1..w5
    for idx, val in fixed_dict.items():
        if idx == 0:
            lp += (y == val)
        else:
            lp += (w[idx-1] == val)

    # 4.4 Objective: minimize 11*y + sum(w_i)
    lp += (11 * y + pulp.lpSum(w)), "DualObjective"

    # 4.5 Dual constraints: volumes[i]*y + w[i] ≥ profits[i] for i in 0..4
    for i in range(n):
        lp += (volumes[i] * y + w[i] >= profits[i]), f"dual_constr_{i+1}"

    # 4.6 Solve quietly (CBC, no log messages)
    lp.solve(pulp.PULP_CBC_CMD(msg=0))

    # 4.7 If not optimal, return bound = +∞ so that branch will be pruned
    if pulp.LpStatus[lp.status] != 'Optimal':
        return float('inf'), None, False

    # 4.8 Retrieve solution values
    y_val  = y.varValue
    w_vals = [wi.varValue for wi in w]
    sol_vec = [y_val] + w_vals

    # 4.9 Check integrality (within tolerance)
    is_int = all(abs(v - round(v)) < 1e-7 for v in sol_vec)

    # 4.10 LP objective
    bound = pulp.value(lp.objective)
    return bound, sol_vec, is_int

# ---------------------------------------------------------
# 5. Branch-and-Bound main loop (depth-first search)
# ---------------------------------------------------------
nodes = []
stack = []

# 5.1 Create root node (ID=0, depth=0, no fixed decisions)
root = BBNode(0, depth=0, parent_id=None, fixed={})
nodes.append(root)
stack.append(0)  # push root ID onto DFS stack

next_id = 1      # to assign unique IDs to new nodes

# 5.2 DFS-based Branch-and-Bound
while stack:
    nid  = stack.pop()     # take the last pushed node
    node = nodes[nid]

    # 5.2.1 Solve LP relaxation at this node
    bound, sol_vec, integrality = solve_lp_relax(node.fixed)
    node.bound    = bound
    node.integral = integrality

    # 5.2.2 Prune if LP bound ≥ current best_int_val (since we minimize)
    if bound >= best_val:
        node.pruned = True
        continue

    # 5.2.3 If the LP solution is already integral, update incumbent
    if integrality:
        # Round each value to integer
        node.sol = [int(round(v)) for v in sol_vec]
        best_val = bound
        best_sol = node.sol.copy()
        continue

    # 5.2.4 Otherwise, branch on the first fractional variable
    #       We search sol_vec for the first entry not close to an integer
    for k, v in enumerate(sol_vec):
        if abs(v - round(v)) > 1e-7:
            branch_index = k
            frac_val = v
            break

    # 5.2.5 Child A: fix that variable = floor(frac_val)
    floor_val = int(frac_val // 1)
    fixed_A   = dict(node.fixed)
    fixed_A[branch_index] = floor_val
    childA = BBNode(next_id, node.depth+1, node.id, fixed_A)
    childA.branchvar = branch_index
    childA.branchval = floor_val
    node.children.append(next_id)
    nodes.append(childA)
    stack.append(next_id)
    next_id += 1

    # 5.2.6 Child B: fix that variable = ceil(frac_val)
    ceil_val = floor_val + 1
    fixed_B  = dict(node.fixed)
    fixed_B[branch_index] = ceil_val
    childB = BBNode(next_id, node.depth+1, node.id, fixed_B)
    childB.branchvar = branch_index
    childB.branchval = ceil_val
    node.children.append(next_id)
    nodes.append(childB)
    stack.append(next_id)
    next_id += 1

# ---------------------------------------------------------
# 6. Recursive print of the entire B&B tree
# ---------------------------------------------------------
def print_tree(node_id, indent=""):
    """
    Recursively print each node’s ID, depth, bound, and tags,
    plus the branching decision that created it (if any).
    """
    n = nodes[node_id]

    # Build status tag
    tag = ""
    if n.pruned:
        tag = " [PRUNED]"
    elif n.integral:
        tag = f" [INTEGRAL obj={int(n.bound)}]"

    # Print node header
    print(f"{indent}Node {n.id}  depth={n.depth}  bound={n.bound:.1f}{tag}")

    # If this node was created by branching, show what was fixed
    if n.branchvar is not None:
        varname = "y" if n.branchvar == 0 else f"w{n.branchvar}"
        print(f"{indent}    └─ branched {varname} = {n.branchval}")

    # Recurse on children with extra indentation
    for child_id in n.children:
        print_tree(child_id, indent + "    ")

# 6.1 Call print_tree(0) to display the full tree
print("\n=== Branch-and-Bound Tree (integer dual) ===\n")
print_tree(0)

# ---------------------------------------------------------
# 7. Final integer-dual result
# ---------------------------------------------------------
print("\n>>> BEST integer dual objective =", best_val)
print(">>> BEST (y , w1..w5)           =", best_sol)

# ---------------------------------------------------------
# 8. Complementary-Slackness check against integer-primal
# ---------------------------------------------------------
print("\n=== Complementary-Slackness products (integer vs. integer) ===")

# Known integer-primal optimum from part (a/b):
x_int = [0, 0, 1, 1, 0]    # only items 3 and 4 delivered (value = 79)

# Unpack the best integer-dual solution
y_int, *w_int = best_sol

# 8.1 Row-slack · y
cap_slack = 11 - sum(v*x for v,x in zip(volumes, x_int))
print(f"Row-slack · y = {cap_slack} * {y_int} = {cap_slack*y_int}")

# 8.2 (1-x_i)·w_i for each i=1..5
for i in range(5):
    slack_i = 1 - x_int[i]
    print(f"(1−x_{i+1})·w_{i+1} = {slack_i} * {w_int[i]} = {slack_i * w_int[i]}")

# 8.3 x_i · [volumes[i]·y_int + w_int[i] − profits[i]]
for i in range(5):
    dual_slack = volumes[i] * y_int + w_int[i] - profits[i]
    product    = x_int[i] * dual_slack
    print(f"x_{i+1} * dual-slack_{i+1} = {x_int[i]} * {dual_slack} = {product}")
