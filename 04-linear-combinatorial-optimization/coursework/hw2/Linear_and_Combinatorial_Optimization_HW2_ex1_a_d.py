# ╔════════════════════════════════════════════════════════════════════════════╗
# ║   EXERCISE 1  ·  Primal ⇄ Dual Solution, Full CS Check, Verbose Comments   ║
# ╚════════════════════════════════════════════════════════════════════════════╝
"""
Run with:

    pip install numpy pymprog
    python ex1_verbose_cs.py
"""

import numpy as np
from pymprog import begin, end, var, maximize, solve

tol = 1e-9   # numerical zero tolerance everywhere in the script

# ───────────────────────────────────────────────────────────────────────────────
# 1. BUILD & SOLVE  PRIMAL  (everything in equality-form)
# ───────────────────────────────────────────────────────────────────────────────
begin('primal')

# (a) Declare primal decision variables
x1 = var('x1', bounds=(None,None))          # free variable  (can be ±)
x2,x3,x4,x5 = var('x2, x3, x4, x5')         # non-negative
x6,x7,x8    = var('x6, x7, x8')             # slack / surplus variables

# (b) Objective  max 3x1 + 11x2 + 9x3 − x4 − 29x5
maximize(3*x1 + 11*x2 + 9*x3 - x4 - 29*x5)

# (c) Constraints  (add x6 / x7 / x8 to turn ≤ and ≥ into equalities)
#     Row 1 : ≤ 4   ⇒ +x6
x2 + x3 + x4 - 2*x5 + x6            == 4
#     Row 2 : ≥ 0   ⇒ +x7
- x1 + x2 - x3 - 2*x4 - x5 + x7     == 0
#     Row 3 : ≤ 1   ⇒ +x8
x1 + x2 + x3 - 3*x5 + x8            == 1

solve()      # simplex (GLPK) ─ finds optimal corner in ≤1 ms

# ───────────────────────────────────────────────────────────────────────────────
# 2. COLLECT MATRICES  (needed for tableau & CS equations)
# ───────────────────────────────────────────────────────────────────────────────
A = np.array([[ 0, 1, 1, 1,-2, 1,0,0],
              [-1, 1,-1,-2,-1, 0,1,0],
              [ 1, 1, 1, 0,-3, 0,0,1]], float)
b = np.array([4,0,1], float)
c = np.array([3,11,9,-1,-29,0,0,0], float)
primal   = [x1,x2,x3,x4,x5,x6,x7,x8]
names    = [v.name for v in primal]

# Identify basic columns (vars with non-zero optimum value)
bas_idx = [i for i,v in enumerate(primal) if abs(v.primal)>tol]
while len(bas_idx) < 3: bas_idx.append(next(i for i in range(8) if i not in bas_idx))
NB_idx  = [i for i in range(8) if i not in bas_idx]

B, Binv = A[:,bas_idx], np.linalg.inv(A[:,bas_idx])
x_B     = Binv @ b                      # basic values  (for info)

# ───────────────────────────────────────────────────────────────────────────────
# 3.  PRINT  PRIMAL OPTIMUM  AND B, B⁻¹, B⁻¹b
# ───────────────────────────────────────────────────────────────────────────────
print("\n╔══════════════════════  PART (a) : PRIMAL  ═════════════════════╗")

print("# Basic variables (their columns form B):",
      [names[i] for i in bas_idx])
print("# Non-basic variables:",
      [names[i] for i in NB_idx], "\n")

print("# All primal variable values (basic + non-basic):")
for v in primal: print(f"  {v.name} = {v.primal}")

Z_opt = sum(ci*vi.primal for ci,vi in zip(c,primal))
print(f"\nOptimal objective Z* = {Z_opt}\n")

# Row gaps  (slack / surplus)  – needed for CS
gap1 = 4 -(x2.primal + x3.primal + x4.primal - 2*x5.primal)
gap2 = (-x1.primal + x2.primal - x3.primal - 2*x4.primal - x5.primal)
gap3 = 1 -(x1.primal + x2.primal + x3.primal - 3*x5.primal)
print(f"# Constraint gaps  (0 means “binding”):  g1={gap1}, g2={gap2}, g3={gap3}\n")

print("# Basis matrix  B :\n", B)
print("\n# Inverse B⁻¹ :\n", Binv)
print("\n# Product B⁻¹ b  (= values of the 3 basic vars):\n", x_B)
print("╚═════════════════════════════════════════════════════════════════\n")

# ───────────────────────────────────────────────────────────────────────────────
# 4.  BUILD & SOLVE  MINIMAL DUAL
#     · FREE column x1  → pure equality (no slack)
#     · x2…x5 ≥0        → ≥ inequalities  (subtract slacks u2…u5)
# ───────────────────────────────────────────────────────────────────────────────
end(); begin('dual')

y1 = var('y1', bounds=(0,None))     # dual var for row1  (≤)
y2 = var('y2', bounds=(None,0))     # dual var for row2  (≥)
y3 = var('y3', bounds=(0,None))     # dual var for row3  (≤)
u2,u3,u4,u5 = var('u2, u3, u4, u5') # slacks for ≥ dual rows

# dual objective = 4·y1 + 1·y3
maximize   # <-- PyMprog default is minimization; flip sign
(-4*y1 - y3)

# dual rows ← Aᵀ·y  – u  = c    (signs per column type)
(-1)*y2 + 1*y3              ==  3            # x1 is free
( 1)*y1 +(-1)*y2 + 1*y3 - u2 >= 11           # x2 ≥0
( 1)*y1 +( 1)*y2 + 1*y3 - u3 >=  9           # x3 ≥0
( 1)*y1 +( 2)*y2        - u4 >= -1           # x4 ≥0
(-2)*y1 + 1*y2 +(-3)*y3 - u5 >= -29          # x5 ≥0

solve()

dual = [y1,y2,y3,u2,u3,u4,u5]

print("╔══════════════════════  PART (d) : DUAL  ═══════════════════════╗")
print("# Dual variable values (y’s then slacks u₂…u₅):")
for v in dual: print(f"  {v.name} = {v.primal}")
print()

# ───────────────────────────────────────────────────────────────────────────────
# 5.  COMPLEMENTARY-SLACKNESS  (statements & numerical check)
#     THEORY :
#       • For each original decision var x_j ≥0  ⇒  x_j* · u_j* = 0
#       • For each original row i                ⇒  y_i* · gap_i = 0
#   We evaluate & print every product; all must be numerically 0.
# ───────────────────────────────────────────────────────────────────────────────
print("# Complementary-slackness products (each must be 0):")

# a) products x_j · u_j   for j = 2..5   (x1 free → no u1)
for lab,xv,uv in [("x2·u2",x2,u2),("x3·u3",x3,u3),
                  ("x4·u4",x4,u4),("x5·u5",x5,u5)]:
    print(f"  {lab:<5} = {xv.primal:.3g} × {uv.primal:.3g} = {xv.primal*uv.primal:.1e}")

# b) products y_i · gap_i  for i = 1..3
for lab,yv,g in [("y1·gap1",y1,gap1),("y2·gap2",y2,gap2),("y3·gap3",y3,gap3)]:
    print(f"  {lab:<8} = {yv.primal:.3g} × {g:.3g} = {yv.primal*g:.1e}")

print("╚═════════════════════════════════════════════════════════════════")
end()   # close dual model
