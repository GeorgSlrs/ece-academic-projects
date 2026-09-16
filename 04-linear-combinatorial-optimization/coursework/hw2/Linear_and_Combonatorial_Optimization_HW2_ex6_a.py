# ============================================================
# 0–1 Knapsack via Branch-and-Bound in Python + PuLP
# — Prints the full search tree (with pruning/integrality tags),
#   then the optimal integer solution.
#
# Requirements:
#   pip install pulp
#
# References:
#   – GeeksforGeeks “0/1 Knapsack using Branch and Bound” ...... :contentReference[oaicite:1]{index=1}
#   – PuLP Documentation (variable bounds, solve syntax) ...... :contentReference[oaicite:2]{index=2}
#   – Wikipedia “Knapsack problem” (fractional bound) ......... :contentReference[oaicite:3]{index=3}
#   – StackOverflow “PuLP unbounded LP” ........................ :contentReference[oaicite:4]{index=4}
#   – GeeksforGeeks “Implementing Branch‐and‐Bound” ............ :contentReference[oaicite:5]{index=5}
# ============================================================

import pulp  # PuLP library for LP/MIP modeling :contentReference[oaicite:6]{index=6}

# --------------------------------------------
# 1. Problem Data: volumes, revenues, capacity
# --------------------------------------------
n = 5                               # Total number of packages :contentReference[oaicite:7]{index=7}
volumes = [2, 3, 4, 6, 8]           # Volume of each package: v1..v5 :contentReference[oaicite:8]{index=8}
revenues = [10, 14, 31, 48, 60]      # Revenue of each package: c1..c5 :contentReference[oaicite:9]{index=9}
V_cap = 11                          # Van capacity = 11 units :contentReference[oaicite:10]{index=10}

# -------------------------------------------------
# 2. Global Incumbent (Best Integer Solution So Far)
# -------------------------------------------------
best_val = 0                        # Best integer revenue found so far (initially 0) :contentReference[oaicite:11]{index=11}
best_x = [0] * n                    # Corresponding binary vector (5 zeros) :contentReference[oaicite:12]{index=12}

# ---------------------------------------------------
# 3. BBNode Class: Records Each Node’s Information
# ---------------------------------------------------
class BBNode:
    """
    Represents a node in the Branch-and-Bound tree.
    Fields:
      id         : unique integer identifier
      parent     : reference to parent BBNode (None for root)
      children   : list of child BBNode instances
      fixed      : dict {i: 0 or 1} for variables fixed so far
      level      : depth in the B&B tree (root has level 0)
      bound      : LP relaxation upper bound (float)
      pruned     : True if node is pruned (LP bound ≤ incumbent or infeasible)
      integral   : True if LP solution was integral at this node
      solution   : integer solution [x0..x4] if integral, else None
      branch_var : which variable index we branched on
      branch_val : value (0 or 1) assigned to branch_var
    """
    def __init__(self, nid, parent, fixed, lvl):
        self.id = nid                      # Unique identifier for this node :contentReference[oaicite:13]{index=13}
        self.parent = parent               # Link to parent node (None if root) :contentReference[oaicite:14]{index=14}
        self.children = []                 # List of child BBNode references :contentReference[oaicite:15]{index=15}
        self.fixed = dict(fixed)           # Copy of fixed variable assignments so far :contentReference[oaicite:16]{index=16}
        self.level = lvl                   # Depth in the tree (root=0) :contentReference[oaicite:17]{index=17}
        self.bound = None                  # Will store the LP relaxation bound (float) :contentReference[oaicite:18]{index=18}
        self.pruned = False                # Set to True if node is pruned :contentReference[oaicite:19]{index=19}
        self.integral = False              # Set to True if LP solution is integral :contentReference[oaicite:20]{index=20}
        self.solution = None               # Stores integer solution if integral :contentReference[oaicite:21]{index=21}
        self.branch_var = None             # Variable index used to branch at this node :contentReference[oaicite:22]{index=22}
        self.branch_val = None             # Value (0 or 1) assigned to branch_var :contentReference[oaicite:23]{index=23}

    def add_child(self, child_node):
        """
        Link a child BBNode to this node.
        """
        self.children.append(child_node)   # Append to children list :contentReference[oaicite:24]{index=24}

# --------------------------------------------------------
# 4. LP Relaxation Helper: Solves 0 ≤ x ≤ 1 LP with PuLP
# --------------------------------------------------------
def solve_lp_relax(fixed_vars):
    """
    Solve the LP relaxation for the subproblem defined by `fixed_vars`.
    fixed_vars: dict mapping variable index i → 0 or 1 (forces x[i] = 0 or 1).

    Returns:
      - bound : optimal LP objective value (float), or -inf if infeasible/unbounded
      - x_lp  : list of length n with LP solution values (floats in [0,1])
    """
    # 4.1 Create a PuLP problem in maximization mode
    prob = pulp.LpProblem("knapsack_relax", pulp.LpMaximize)  # :contentReference[oaicite:25]{index=25}

    # 4.2 Define continuous variables x[0]..x[n-1], each 0 ≤ x[i] ≤ 1
    x = [
        pulp.LpVariable(f"x{i}", lowBound=0, upBound=1, cat="Continuous")
        for i in range(n)
    ]  # :contentReference[oaicite:26]{index=26}

    # 4.3 Objective: maximize Σ (revenues[i] * x[i])
    prob += pulp.lpSum(revenues[i] * x[i] for i in range(n))  # :contentReference[oaicite:27]{index=27}

    # 4.4 Capacity constraint: Σ (volumes[i] * x[i]) ≤ V_cap
    prob += pulp.lpSum(volumes[i] * x[i] for i in range(n)) <= V_cap  # :contentReference[oaicite:28]{index=28}

    # 4.5 Note: Each x[i] has upBound=1 from declaration, so 0 ≤ x[i] ≤ 1 holds :contentReference[oaicite:29]{index=29}

    # 4.6 Impose fixed variable assignments (force x[i]=0 or x[i]=1)
    for i, val in fixed_vars.items():
        if val == 0:
            prob += x[i] <= 0  # Forces x[i]=0 since x[i]≥0 anyway :contentReference[oaicite:30]{index=30}
        else:
            prob += x[i] >= 1  # Forces x[i]=1 since x[i]≤1 anyway :contentReference[oaicite:31]{index=31}

    # 4.7 Solve the LP relaxation silently (CBC with no messages)
    prob.solve(pulp.PULP_CBC_CMD(msg=0))  # :contentReference[oaicite:32]{index=32}

    # 4.8 Check solver status: if not Optimal, treat as infeasible/unbounded → bound = -inf
    status = pulp.LpStatus[prob.status]  # :contentReference[oaicite:33]{index=33}
    if status != "Optimal":
        return float("-inf"), [0.0] * n

    # 4.9 Retrieve the LP objective value (upper bound)
    bound = pulp.value(prob.objective)  # :contentReference[oaicite:34]{index=34}

    # 4.10 Retrieve LP solution values for each x[i]
    x_lp = [x[i].varValue for i in range(n)]  # :contentReference[oaicite:35]{index=35}

    return bound, x_lp

# ------------------------------------------------------------------
# 5. MAIN Branch‐and‐Bound Loop (Depth‐First), Building the Tree
# ------------------------------------------------------------------
nodes = []  # List to store all BBNode instances :contentReference[oaicite:36]{index=36}
stack = []  # DFS stack (stores node IDs to explore) :contentReference[oaicite:37]{index=37}
root = BBNode(0, None, {}, 0)  # Root node: ID=0, no parent, no fixed, level=0 :contentReference[oaicite:38]{index=38}
nodes.append(root)
stack.append(0)  # Push root’s ID onto stack :contentReference[oaicite:39]{index=39}
next_id = 1  # Next unique node ID to assign :contentReference[oaicite:40]{index=40}

while stack:
    # 5.1 Pop top node ID (DFS order)
    nid = stack.pop()
    node = nodes[nid]  # Retrieve the BBNode object for this subproblem :contentReference[oaicite:41]{index=41}

    # 5.2 Solve LP relaxation at this node
    lp_val, lp_sol = solve_lp_relax(node.fixed)
    node.bound = lp_val  # Record the LP upper bound for this node :contentReference[oaicite:42]{index=42}

    # 5.3 Pruning check: if LP bound ≤ best_val, prune this node
    if lp_val <= best_val:
        node.pruned = True  # Mark node as pruned (no children will be explored) :contentReference[oaicite:43]{index=43}
        continue  # Skip branching for a pruned node

    # 5.4 Integrality check: if all x_lp[i] ∈ {0,1} within tolerance, node is integral
    is_integral = all(abs(v - round(v)) < 1e-7 for v in lp_sol)
    if is_integral:
        node.integral = True  # Mark as integral leaf :contentReference[oaicite:44]{index=44}
        # Build integer solution by rounding each x_lp[i]
        int_x = [int(round(v)) for v in lp_sol]
        node.solution = int_x
        # Compute integer revenue
        int_val = sum(revenues[i] * int_x[i] for i in range(n))
        # 5.4.1 Update incumbent if integer solution is better
        if int_val > best_val:
            best_val = int_val
            best_x = int_x.copy()
        continue  # No further branching (leaf node)

    # 5.5 Otherwise, LP solution is fractional → branch on first fractional variable
    #      Find index k such that 0 < x_lp[k] < 1
    k = next(i for i, v in enumerate(lp_sol) if 1e-7 < v < 1 - 1e-7)

    # 5.6 Child A: fix x[k] = 0
    fixedA = dict(node.fixed)  # Copy parent’s fixed dict :contentReference[oaicite:45]{index=45}
    fixedA[k] = 0  # Assign x[k]=0 for this child :contentReference[oaicite:46]{index=46}
    childA = BBNode(next_id, node, fixedA, node.level + 1)  # Create child at level+1 :contentReference[oaicite:47]{index=47}
    childA.branch_var = k  # Record that we branched on variable k :contentReference[oaicite:48]{index=48}
    childA.branch_val = 0  # Record that x[k]=0 :contentReference[oaicite:49]{index=49}
    node.add_child(childA)  # Link parent→child :contentReference[oaicite:50]{index=50}
    nodes.append(childA)  # Store child in global list :contentReference[oaicite:51]{index=51}
    stack.append(next_id)  # Schedule this child for exploration (DFS) :contentReference[oaicite:52]{index=52}
    next_id += 1

    # 5.7 Child B: fix x[k] = 1
    fixedB = dict(node.fixed)
    fixedB[k] = 1  # Assign x[k]=1 for this child :contentReference[oaicite:53]{index=53}
    childB = BBNode(next_id, node, fixedB, node.level + 1)
    childB.branch_var = k  # Record branching on k :contentReference[oaicite:54]{index=54}
    childB.branch_val = 1  # Record that x[k]=1 :contentReference[oaicite:55]{index=55}
    node.add_child(childB)
    nodes.append(childB)
    stack.append(next_id)
    next_id += 1

# End of Branch-and-Bound search

# ------------------------------------------------------
# 6. Function to Recursively Print the Entire B&B Tree
# ------------------------------------------------------
def print_tree(node, indent=""):
    """
    Recursively print each node in the Branch-and-Bound tree with indentation.

    For each node, this prints:
      • Node {id} (L{level})  bound={bound:.2f}
      • [PRUNED] tag if node.pruned is True
      • [INTEGRAL val=…] tag if node.integral is True
      • '    branched:  x[{branch_var}] = {branch_val}' if node.branch_var is not None
      • '    fixed:     x[i]=v, x[j]=v, …' if node.fixed is not empty

    Then it recurses on children with an increased indent (4 extra spaces).
    """
    # 6.1 Build status tags
    tags = []
    if node.pruned:
        tags.append("PRUNED")  # :contentReference[oaicite:56]{index=56}
    if node.integral:
        val = sum(revenues[i] * node.solution[i] for i in range(n))
        tags.append(f"INTEGRAL val={val}")  # :contentReference[oaicite:57]{index=57}
    tagstr = f" [{' | '.join(tags)}]" if tags else ""  # :contentReference[oaicite:58]{index=58}

    # 6.2 Print node header with tags
    print(f"{indent}Node {node.id} (L{node.level})  bound={node.bound:.2f}{tagstr}")  # :contentReference[oaicite:59]{index=59}

    # 6.3 If this node was created by branching, show the decision
    if node.branch_var is not None:
        print(f"{indent}    branched:  x[{node.branch_var}] = {node.branch_val}")  # :contentReference[oaicite:60]{index=60}

    # 6.4 Show fixed variables at this node (if any)
    if node.fixed:
        fixed_str = ", ".join(f"x[{i}]={v}" for i, v in sorted(node.fixed.items()))
        print(f"{indent}    fixed:     {fixed_str}")  # :contentReference[oaicite:61]{index=61}

    # 6.5 Recurse on each child with +4 spaces of indentation
    for c in node.children:
        print_tree(c, indent + "    ")  # :contentReference[oaicite:62]{index=62}

# -------------------------------------------------------
# 7. After B&B completes: Print the full tree and optimum
# -------------------------------------------------------
print("\n=== Branch-and-Bound Search Tree ===\n")
print_tree(root)  # Recursively print nodes with indentation :contentReference[oaicite:63]{index=63}

print("\n>>> OPTIMAL integer revenue =", best_val)
print(">>> OPTIMAL x             =", best_x)
# Expected:
#   >>> OPTIMAL integer revenue = 79
#   >>> OPTIMAL x             = [0, 0, 1, 1, 0]
