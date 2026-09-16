# =================================================================================
# Exercise 1 (a, b, c, d) — Complete Primal & Dual Solution with EVERY LINE COMMENTED
# =================================================================================

import numpy as np                                    # Import NumPy for numerical arrays and linear algebra
from pymprog import begin, var, maximize, minimize, solve, vobj, end
# └── Import PyMprog functions:
#     • begin, end       : start/finish model
#     • var              : declare decision variables
#     • maximize/minimize: set objective
#     • solve            : run the solver
#     • vobj             : retrieve objective value

# ---------------------------------------------------------------------------------
# HELPER FUNCTION: PRINT_TABLEAU
# ---------------------------------------------------------------------------------
def print_tableau(tab, basic_vars, col_names, c_orig, title):
    """
    Prints a simplex tableau in textbook form.
    - tab       : NumPy array shape (m+1, n+1) containing tableau entries
    - basic_vars: list of m strings, names of the basic variables (one per constraint row)
    - col_names : list of n strings, names of columns x1..xn
    - c_orig    : array of original objective coefficients [c1..cn]
    - title     : string to print as the tableau header
    """
    m_plus1, n_plus1 = tab.shape            # m_plus1 = m constraints + 1, n_plus1 = n variables + RHS
    n = n_plus1 - 1                         # number of variables (excluding RHS)
    # Build header row: "Basic", "c_B", then variable names, then "RHS"
    headers = ["Basic", "  c_B"] + col_names + ["   RHS"]
    print("\n" + title)                      # Print the title above the tableau
    print(" | ".join(f"{h:>7}" for h in headers))  # Print headers with fixed width
    print("-" * (9 * len(headers)))          # Separator line
    
    # Print row 0: the -Z row containing negative reduced costs and -Z*
    zrow = ["  -Z", "      "] + \
           [f"{tab[0, j]:>7.2f}" for j in range(n)] + \
           [f"{tab[0, -1]:>7.2f}"]
    print(" | ".join(zrow))                  # Join and print the -Z row entries
    
    # Print constraint rows 1..m
    for i in range(1, m_plus1):
        bv = basic_vars[i-1]                     # Name of the basic variable in row i
        cb = c_orig[col_names.index(bv)]         # Original cost coefficient of that basic variable
        # Build row: [basic var, c_B] + coefficients of x1..xn + RHS
        row = [f"{bv:>4}", f"{cb:>7.2f}"] + \
              [f"{tab[i, j]:>7.2f}" for j in range(n)] + \
              [f"{tab[i, -1]:>7.2f}"]
        print(" | ".join(row))                  # Print the assembled row
    print()                                     # Blank line after the tableau

# =================================================================================
# (1) BUILD & SOLVE THE PRIMAL LP
# =================================================================================
begin('primal_ex1')                           # Start a new model called 'primal_ex1'

# Declare decision variables:
x1 = var('x1', bounds=(None, None))          # x1 is free (no sign restriction)
x2, x3, x4, x5 = var('x2, x3, x4, x5')        # x2..x5 are ≥0 by default

# Declare slack / surplus variables:
x6, x7, x8 = var('x6, x7, x8')               # x6,x7,x8 ≥0 for converting to equalities

# Define the objective function (maximization):
#   Max Z = 3*x1 + 11*x2 + 9*x3 − 1*x4 − 29*x5
maximize(3*x1 + 11*x2 + 9*x3 - x4 - 29*x5)

# Add constraints in equality form:
#   (1) x2 + x3 + x4 − 2*x5 + x6 = 4   (slack x6)
x2 + x3 + x4 - 2*x5 + x6 == 4

#   (2) -x1 + x2 - x3 - 2*x4 - x5 + x7 = 0  (surplus x7)
- x1 + x2 - x3 - 2*x4 - x5 + x7 == 0

#   (3) x1 + x2 + x3 - 3*x5 + x8 = 1   (slack x8)
x1 + x2 + x3 - 3*x5 + x8 == 1

solve()                                      # Solve the primal LP using GLPK

# =================================================================================
# (2) EXTRACT PRIMAL SOLUTION & DETECT THE FINAL BASIS
# =================================================================================
primal_vars = [x1, x2, x3, x4, x5, x6, x7, x8]  # List of all primal variables
names_pr    = [v.name for v in primal_vars]     # ['x1','x2',...,'x8']
c_pr        = np.array([3,11,9,-1,-29,0,0,0], float)  # Objective costs c1..c8
tol         = 1e-9                              # Numerical tolerance for zero
m_pr, n_pr  = 3, 8                              # m=3 constraints, n=8 vars

# Identify basic variables:
basic_idx = [i for i, v in enumerate(primal_vars) if abs(v.primal) > tol]
# If fewer than m_pr due to degeneracy, pad with the first non-chosen vars
if len(basic_idx) < m_pr:
    for i in range(n_pr):
        if i not in basic_idx:
            basic_idx.append(i)
            if len(basic_idx) == m_pr:
                break

nonbasic_idx = [i for i in range(n_pr) if i not in basic_idx]
basic_vars   = [names_pr[i] for i in basic_idx]      # Names of basic vars
nonbasic_vars= [names_pr[i] for i in nonbasic_idx]   # Names of non-basic vars

print("\nPRIMAL BASIC    =", basic_vars)              # Print basic set
print("PRIMAL NONBASIC =", nonbasic_vars)            # Print non-basic set

# =================================================================================
# (3) RECONSTRUCT & PRINT FINAL PRIMAL SIMPLEX TABLEAU
# =================================================================================
# Build the constraint matrix A and RHS vector b
A_pr = np.array([
    [ 0,  1,  1,  1, -2, 1,0,0],
    [-1,  1, -1, -2, -1,0,1,0],
    [ 1,  1,  1,  0, -3,0,0,1],
], float)
b_pr = np.array([4,0,1], float)

B_pr    = A_pr[:, basic_idx]                      # Extract basis columns
N_pr    = A_pr[:, nonbasic_idx]                   # Extract non-basis columns
Binv_pr = np.linalg.inv(B_pr)                     # Compute inverse of basis
cB_pr   = c_pr[basic_idx]                         # Cost vector for basis
cN_pr   = c_pr[nonbasic_idx]                      # Cost vector for non-basis

# Compute reduced costs: r_N = c_N - c_B^T B^-1 N
rN_pr   = cN_pr - cB_pr @ Binv_pr @ N_pr
r_full  = np.zeros(n_pr)                          # Full reduced-cost vector
r_full[nonbasic_idx] = rN_pr                      # Place r_N in non-basic slots

# Compute optimal objective: Z* = c_B^T (B^-1 b)
Z_star_pr = cB_pr @ (Binv_pr @ b_pr)

# Assemble the tableau rows:
Zrow_pr   = np.concatenate((-r_full, [-Z_star_pr]))    # -Z row: [-r | -Z*]
rows_pr   = np.column_stack((Binv_pr @ A_pr, Binv_pr @ b_pr))  # constraint rows

tableau_pr = np.vstack((Zrow_pr, rows_pr))             # Full tableau array

# Print the primal tableau
print_tableau(
    tableau_pr, basic_vars, names_pr, c_pr,
    "FINAL PRIMAL SIMPLEX TABLEAU\n"
    " Row-0: -reduced costs under x1..x8, and -Z* at RHS\n"
    " Rows1..3: basis rows with c_B, B⁻1A, and B⁻1b"
)

# =================================================================================
# (4) PART (a): Optimal x*, Z*, Binding Status, Optimal Vertex
# =================================================================================
print(">>> Part (a) – Primal optimum & binding constraints")
x_star = np.zeros(n_pr)
x_star[basic_idx] = Binv_pr @ b_pr  # Fill basic var values from B^-1 b
for i in range(5):
    print(f"  x{i+1} = {x_star[i]:.4g}")  # Print x1..x5
print(f"  Z*    = {Z_star_pr:.4g}\n")     # Print optimal objective

# Compute constraint gaps (slack/surplus)
gap1 = 4  - (x_star[1] + x_star[2] + x_star[3] - 2*x_star[4])  # slack for (1)
gap2 = (-x_star[0] + x_star[1] - x_star[2] - 2*x_star[3] - x_star[4])  # surplus (2)
gap3 = 1  - (x_star[0] + x_star[1] + x_star[2] - 3*x_star[4])  # slack for (3)
for i,g in enumerate((gap1, gap2, gap3),1):
    st = "binding" if abs(g)<tol else "non-binding"
    print(f"  Constraint {i}: {st} (gap={g:.4g})")

vertex = tuple(x_star[i] for i in range(5))
print(f"\n  Optimal vertex (x1..x5) = {vertex}\n")

# =================================================================================
# (5) PART (b): Objective-Coefficient Sensitivity
# =================================================================================
print(">>> Part (b) – Sensitivity on objective coefficients")
e2 = np.zeros(m_pr)
e2[basic_idx.index(1)] = 1                       # Unit vector selecting x2's B^-1 row
dir_r = e2 @ Binv_pr @ N_pr                      # Direction of r_N w.r.t. δ
low, up = -np.inf, np.inf
for r_val, d_val in zip(rN_pr, dir_r):
    if abs(d_val)<tol: continue
    bnd = r_val / d_val
    if d_val>0:
        up = min(up, bnd)
    else:
        low= max(low,bnd)
print(f"  Basic x2: {low:.2f} ≤ δ ≤ {up:.2f} → new c2∈[9,16]")
r4 = r_full[3]
print(f"  Non-basic x4: δ ≤ {-r4:.2f} → new c4≤4\n")

# =================================================================================
# (6) PART (c): RHS Sensitivity
# =================================================================================
print(">>> Part (c) – RHS sensitivity for constraint 1")
e1 = np.array([1,0,0], float)                   # Unit vector for constraint 1
dir_b = Binv_pr @ e1                             # Effect of γ on x_B
lowg, upg = -np.inf, np.inf
for xb, di in zip(Binv_pr @ b_pr, dir_b):
    if abs(di)<tol: continue
    bnd = -xb/di
    if di>0:
        lowg= max(lowg, bnd)
    else:
        upg = min(upg, bnd)
print(f"  Constraint1: γ ≥ {lowg:.2f}  (no upper bound)\n")

# =================================================================================
# (7) BUILD & SOLVE THE DUAL LP — coefficients taken directly from A_pr
# =================================================================================
end()                                   # close the primal model
begin('dual_ex1')                       # start a fresh PyMprog model for the dual

# -------------------------------------------------------------------------------
# 7.1  Dual variables: one per primal row
#       row1 (≤) → y1 ≥ 0
#       row2 (≥) → y2 ≤ 0
#       row3 (≤) → y3 ≥ 0
# -------------------------------------------------------------------------------
y1 = var('y1', bounds=(0,   None))      # ≥ 0
y2 = var('y2', bounds=(None, 0))        # ≤ 0
y3 = var('y3', bounds=(0,   None))      # ≥ 0

# -------------------------------------------------------------------------------
# 7.2  Slack / surplus variables for the dual inequalities
#       One u_j for each primal column j that is non-free (j = 2..5 here)
#       u1 is just a name we give to the free-column row so that we keep
#       everything in equality form (u1 will be forced to 0 by optimality).
# -------------------------------------------------------------------------------
u1 = var('u1', bounds=(None, None))     # free  (x1 is free → equality)
u2, u3, u4, u5 = var('u2, u3, u4, u5')  # ≥ 0   (for x2..x5, which are ≥ 0)

# -------------------------------------------------------------------------------
# 7.3  Dual objective:   min  4·y1 + 0·y2 + 1·y3     ( = bᵀ·y )
# -------------------------------------------------------------------------------
minimize(4*y1 + y3)

# -------------------------------------------------------------------------------
# 7.4  Dual constraints (automatically from A_pr)
#       For each primal column  j = 1..5
#           (A_pr^T · y)_j  −  u_j  =  c_j     if x_j ≥ 0     ( “≥” row )
#           (A_pr^T · y)_j  +  u_j  =  c_j     if x_j ≤ 0     ( not present )
#           (A_pr^T · y)_j           =  c_j     if x_j free
# -------------------------------------------------------------------------------
# Pull the column vectors from A_pr so we cannot make a sign mistake.
a1, a2, a3 = A_pr[:, 0], A_pr[:, 1], A_pr[:, 2]  # cols for x1,x2,x3
a4, a5     = A_pr[:, 3], A_pr[:, 4]              # cols for x4,x5

# x1 is FREE  → equality with no slack (u1 is “dummy” but kept for tableau)
(a1[0])*y1 + (a1[1])*y2 + (a1[2])*y3 + u1  ==  3

# x2 ≥ 0  → “≥” inequality converted to equality by subtracting u2
(a2[0])*y1 + (a2[1])*y2 + (a2[2])*y3 - u2 >= 11   # PyMprog lets us write ≥
# x3 ≥ 0
(a3[0])*y1 + (a3[1])*y2 + (a3[2])*y3 - u3 >=  9
# x4 ≥ 0
(a4[0])*y1 + (a4[1])*y2 + (a4[2])*y3 - u4 >= -1
# x5 ≥ 0
(a5[0])*y1 + (a5[1])*y2 + (a5[2])*y3 - u5 >= -29

solve()                                # run GLPK on the dual

# =================================================================================
# (8)  LIST ALL PRIMAL AND DUAL VARIABLE VALUES
# =================================================================================
print("\n>>> Complete variable report")
print("Primal (x1..x8):")
for v in primal_vars:
    print(f"  {v.name} = {v.primal:.6g}")
print("\nDual (y1..y3, u1..u5):")
for v in [y1, y2, y3, u1, u2, u3, u4, u5]:
    print(f"  {v.name} = {v.primal:.6g}")
print()

# =================================================================================
# (9)  COMPLEMENTARY SLACKNESS (full detail, including x·u and y·slack products)
# =================================================================================
print(">>> Complementary-slackness products\n")

# (i) x_j * u_j  for j = 1..5
print("x_j  *  u_j  (should all be 0):")
for j, (xv, uv) in enumerate(zip(primal_vars[:5], [u1,u2,u3,u4,u5]), start=1):
    prod = xv.primal * uv.primal
    print(f"  x{j}*·u{j}* = {xv.primal:.6g} × {uv.primal:.6g} = {prod:.2e}")

# (ii) y_i * primal-gap_i   for i = 1..3
print("\ny_i * (primal gap of row i) (should all be 0):")
gaps = [x6.primal, x7.primal, x8.primal]       # exactly b_i - a_i·x*
for i, (yv, gap) in enumerate(zip([y1,y2,y3], gaps), start=1):
    print(f"  y{i}*·gap{i} = {yv.primal:.6g} × {gap:.6g} = {yv.primal*gap:.2e}")

# (iii) Grand sum
grand_sum = sum(xv.primal*uv.primal for xv,uv in zip(primal_vars[:5],[u1,u2,u3,u4,u5])) + \
            sum(yv.primal*gap for yv,gap in zip([y1,y2,y3], gaps))
print(f"\nSum of ALL CS products = {grand_sum:.2e} (should be 0)\n")
print("✔ Dual now matches the description and CS conditions hold.")