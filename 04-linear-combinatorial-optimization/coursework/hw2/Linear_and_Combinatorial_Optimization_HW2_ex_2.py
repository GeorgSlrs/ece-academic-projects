
# Step-by-step solving of the DUAL (Exercise 2) and recovery of the PRIMAL optimal edge
# entirely with comments explaining each operation.

import numpy as np
from scipy.optimize import linprog
import sympy as sp

def solve_dual_and_recover_primal_scipy():
    """
    1) Solve Dual via SciPy's linprog.
    2) Compute dual slacks to see which constraints bind.
    3) Use complementary slackness to pin down primal zeros and bindings.
    4) Solve the reduced primal system symbolically for the parametric solution.
    5) Impose feasibility to bound the free parameter.
    6) Print the full optimal edge in the primal.
    """

    # --------------------------------------------------------------------------
    # 1) DUAL FORMULATION
    # --------------------------------------------------------------------------
    # Dual maximizes W = -6*y2 + 3*y3.
    # We convert to minimization: min(6*y2 - 3*y3).
    # Variables: [y1, y2+, y2-, y3] with y2 = y2+ - y2-.
    # All these are >= 0.

    # Cost vector for minimization (c·x): 6*y2p - 6*y2n - 3*y3
    c = np.array([0,  6, -6, -3])

    # Equality constraint D3: y1 + 2(y2p - y2n) - 4y3 = 0
    A_eq = np.array([[1, 2, -2, -4]])
    b_eq = np.array([0])

    # Inequalities:
    # D1: 2y1 - y2 - 3y3 <= -1   from 1 + 2y1 - y2 -3y3 <=0
    # D2: -3y1 - y2 +  y3 <=  1   from 1 + 3y1 + y2 - y3 >=0 (flip)
    # D4: -y1  - y2 + 2y3 <=  0   from y1 + y2 -2y3 >=0 (flip)
    A_ub = np.array([
        [ 2, -1,  1, -3],
        [-3, -1,  1,  1],
        [-1, -1,  1,  2]
    ])
    b_ub = np.array([-1, 1, 0])

    # Bounds for y1, y2p, y2n, y3
    bounds = [(0, None)] * 4

    # Solve with HiGHS
    res = linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=bounds, method='highs')

    # Extract dual solution
    y1, y2p, y2n, y3 = res.x
    y2 = y2p - y2n
    W  = -6*y2 + 3*y3

    # --------------------------------------------------------------------------
    # 2) COMPUTE DUAL SLACKS
    # --------------------------------------------------------------------------
    # Slack definitions (should be >=0 if feasible):
    # slack_D1 = 0 - (1+2y1 - y2 -3y3)
    # slack_D2 = (1+3y1 + y2 - y3) - 0
    # slack_D3 = 0 (equality)
    # slack_D4 = (y1 + y2 -2y3) - 0
    s1 = -(1 + 2*y1 - y2 - 3*y3)
    s2 =  (1 + 3*y1 + y2 -  y3)
    s4 =  (y1 +   y2 - 2*y3)

    print("=== Dual solution & slacks ===")
    print(f"y1 = {y1:.4f}, y2 = {y2:.4f}, y3 = {y3:.4f}, W* = {W:.4f}")
    print(f"slack D1 = {s1:.4f}, D2 = {s2:.4f}, D3 = 0.0000, D4 = {s4:.4f}\n")

    # --------------------------------------------------------------------------
    # 3) COMPLEMENTARY-SLACKNESS FOR PRIMAL VARIABLES
    # --------------------------------------------------------------------------
    # Rule: x_j * slack_j = 0 ⇒ if slack_j > 0 ⇒ x_j = 0; if slack_j = 0 ⇒ x_j may be > 0
    print("=== Complementary-slackness decisions ===")
    print(f"slack D1 = {s1:.4f} → x1 free")
    print(f"slack D2 = {s2:.4f} → x2 = 0")
    print(f"slack D3 = 0.0000 → x3 free")
    print(f"slack D4 = {s4:.4f} → x4 free\n")

    # --------------------------------------------------------------------------
    # 4) REDUCED PRIMAL SYSTEM (binding constraints + x2=0)
    # --------------------------------------------------------------------------
    # Binding primal (2): -x1 + x2 + 2x3 + x4 = 6
    # Binding primal (3):  3x1 + x2 + 4x3 + 2x4 = 3
    # And x2 = 0 from slack D2
    # Solve symbolically for x1, x4 in terms of x3=t
    x1, x3, x4 = sp.symbols('x1 x3 x4', real=True)
    eq1 = -x1 + 2*x3 +   x4 - 6
    eq2 =  3*x1 + 4*x3 + 2*x4 - 3
    sol = sp.solve((eq1, eq2), (x1, x4))
    x1_expr = sol[x1]  # -1.8
    x4_expr = sol[x4]  # 4.2 - 2*t

    print("=== Primal complementary solution (parametric) ===")
    print(f"x1 = {x1_expr}    # = -1.8")
    print("x2 = 0")
    print("x3 = t            # free parameter")
    print(f"x4 = {x4_expr}  # = 4.2 - 2*t\n")

    # --------------------------------------------------------------------------
    # 5) FEASIBILITY BOUNDS ON t
    # --------------------------------------------------------------------------
    # x4 >= 0 → 4.2 -2t >= 0 → t <= 2.1
    # primal (1) slack: 2x1+3x2+x3+x4 <=0 → 0.6 - t <= 0 → t >= 0.6
    print("=== Feasibility bounds on t ===")
    print("t <= 2.1  (from x4 >= 0)")
    print("t >= 0.6  (from slack of constraint (1))\n")

    # --------------------------------------------------------------------------
    # 6) FINAL OUTPUT: optimal edge in the primal
    # --------------------------------------------------------------------------
    print("=== Optimal primal edge ===")
    print("x(t) = (-1.8, 0, t, 4.2 - 2*t), for 0.6 <= t <= 2.1")
    print("Endpoints:")
    print("  t = 0.6 → (-1.8, 0, 0.6, 3.0)")
    print("  t = 2.1 → (-1.8, 0, 2.1, 0)")
    print("Primal objective z* = x1 + x2 = -1.8\n")

if __name__ == "__main__":
    solve_dual_and_recover_primal_scipy()
