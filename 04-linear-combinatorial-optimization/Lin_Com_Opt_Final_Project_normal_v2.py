# =====================================================================
# WORKOUT LP — TWO-PHASE SIMPLEX + TABLEAUX + READABLE SAG + SA (x1..x9 ONLY) + DUAL
# =====================================================================
#   • Builds a 9-variable "hours per month" workout LP (x1..x9 ≥ 0).
#   • Solves with PuLP/CBC quickly (sanity check).
#   • Runs a FROM-SCRATCH TWO-PHASE SIMPLEX (tableau):
#       PHASE I  : add artificials, maximize -sum(artificials) to get a feasible basis.
#       PHASE II : drop artificials, optimize the true objective.
#     Every pivot prints ENTER/LEAVE and a full tableau with '-Z' (reduced costs).
#   • Saves and shows a readable Simplex Adjacency Graph (SAG) to the current folder.
# =====================================================================

import math
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# =====================================================================
# (PERF) Timing & Memory utilities
# =====================================================================
import sys, time, platform
try:
    import psutil  # best effort for current RSS
except Exception:
    psutil = None
try:
    import resource  # best effort for peak RSS (ru_maxrss)
except Exception:
    resource = None

_SCRIPT_T0 = time.perf_counter()

def _bytes_to_mb(x):
    return f"{(x / (1024*1024)):.2f} MB" if isinstance(x, (int, float)) and x is not None else "N/A"

def get_current_rss_bytes():
    """Return current resident set size in bytes, if available."""
    # Prefer psutil if present
    if psutil is not None:
        try:
            return psutil.Process(os.getpid()).memory_info().rss
        except Exception:
            pass
    # Try /proc/self/statm on Linux
    try:
        if sys.platform.startswith("linux"):
            with open("/proc/self/statm", "r") as f:
                parts = f.read().split()
                if len(parts) >= 2:
                    pages = int(parts[1])
                    page_size = os.sysconf("SC_PAGE_SIZE")
                    return pages * page_size
    except Exception:
        pass
    return None  # Unknown

def get_peak_rss_bytes():
    """Return peak RSS in bytes if available (based on ru_maxrss semantics)."""
    if resource is None:
        return None
    try:
        ru = resource.getrusage(resource.RUSAGE_SELF)
        peak = getattr(ru, "ru_maxrss", None)
        if peak is None:
            return None
        # On Linux, ru_maxrss is in kilobytes; on macOS it's in bytes.
        if sys.platform.startswith("darwin"):
            return int(peak)  # bytes
        else:
            return int(peak * 1024)  # KB → bytes
    except Exception:
        return None

def print_perf(tag, t0):
    """Print wall time and memory (current + peak RSS) for a section."""
    dt = time.perf_counter() - t0
    cur = get_current_rss_bytes()
    peak = get_peak_rss_bytes()
    print(f"[PERF] {tag}: {dt:.6f} s | RSS now={_bytes_to_mb(cur)} | Peak RSS={_bytes_to_mb(peak)}")

# -----------------------------
# (0) MODEL DATA
# -----------------------------
# Decision variables (monthly hours; all >= 0)
#   x1: Moderate cardio
#   x2: HIIT (vigorous intervals)
#   x3: Strength upper
#   x4: Strength lower
#   x5: Core & stability
#   x6: Flexibility / stretching
#   x7: Yoga / mobility
#   x8: Plyometrics / agility
#   x9: Active recovery (very light movement)
var_names = ["x1","x2","x3","x4","x5","x6","x7","x8","x9"]

# Objective weights (points per hour). Tweak to taste.
c = np.array([5.0, 8.0, 6.5, 6.5, 4.0, 2.0, 3.0, 5.5, 1.5], dtype=float)

# Minimum explicit Active Recovery to avoid x9 = 0
MIN_ACTIVE_RECOVERY = 8.0  # e.g., ≈ 2 h/week baseline

# Build constraints A x (sense) b
A_list, b_list, sense_list = [], [], []

# C1) total time ≤ 60
A_list.append([1,1,1,1,1,1,1,1,1]);   b_list.append(60.0);  sense_list.append("<=")
# C2) aerobic min ≥ 10.8  (vigorous≈2×; plyo≈1.5×; yoga/active≈0.5×)
A_list.append([1,2,0,0,0,0,0.5,1.5,0.5]);  b_list.append(10);  sense_list.append(">=")
# C3) strength min ≥ 8  (core/HIIT/plyo half-credit toward "strengthiness")
A_list.append([0,0.5,1,1,0.5,0,0,0.5,0]);  b_list.append(8.0);    sense_list.append(">=")
# C4) flexibility + mobility ≥ 6
A_list.append([0,0,0,0,0,1,1,0,0]);        b_list.append(6.0);    sense_list.append(">=")
# C5) HIIT cap ≤ 8
A_list.append([0,1,0,0,0,0,0,0,0]);        b_list.append(8.0);    sense_list.append("<=")
# C6) plyometrics cap ≤ 6
A_list.append([0,0,0,0,0,0,0,1,0]);        b_list.append(6.0);    sense_list.append("<=")
# C7) “heavy” cap ≤ 28 (HIIT + both strength + plyo)
A_list.append([0,1,1,1,0,0,0,1,0]);        b_list.append(28.0);   sense_list.append("<=")
# C8) fatigue balance: (x2+x3+x4+x8) − 4(x6+x7+x9) − 2x5 ≤ 0
A_list.append([0,1,1,1,-2,-4,-4,1,-4]);    b_list.append(0.0);    sense_list.append("<=")
# C9) strength upper ≤ 18
A_list.append([0,0,1,0,0,0,0,0,0]);        b_list.append(18.0);   sense_list.append("<=")
# C10) strength lower ≤ 18
A_list.append([0,0,0,1,0,0,0,0,0]);        b_list.append(18.0);   sense_list.append("<=")
# C11) upper - lower ≤ 4
A_list.append([0,0,1,-1,0,0,0,0,0]);       b_list.append(4.0);    sense_list.append("<=")
# C12) lower - upper ≤ 4
A_list.append([0,0,-1,1,0,0,0,0,0]);       b_list.append(4.0);    sense_list.append("<=")
# C13) yoga supply cap ≤ 12
A_list.append([0,0,0,0,0,0,1,0,0]);        b_list.append(12.0);   sense_list.append("<=")
# C14) core + active ≥ 8
A_list.append([0,0,0,0,1,0,0,0,1]);        b_list.append(8.0);    sense_list.append(">=")
# C14b) explicit Active Recovery ≥ MIN_ACTIVE_RECOVERY
A_list.append([0,0,0,0,0,0,0,0,1]);        b_list.append(MIN_ACTIVE_RECOVERY); sense_list.append(">=")
# C15) cardio near strength:  x1 − 0.8x3 − 0.8x4 ≥ 0
A_list.append([1,0,-0.8,-0.8,0,0,0,0,0]);  b_list.append(0.0);    sense_list.append(">=")

A = np.array(A_list, dtype=float)
b = np.array(b_list, dtype=float)
m, n = A.shape  # m = number of constraints (15), n = number of decision vars (9)

# ------------------------------------------------
# (1) Quick PRIMAL solve with PuLP/CBC (sanity check)
# ------------------------------------------------
t_cbc = time.perf_counter()
try:
    import pulp
    prob = pulp.LpProblem("WorkoutLP", pulp.LpMaximize)
    x = {nm: pulp.LpVariable(nm, lowBound=0) for nm in var_names}
    # Objective
    prob += pulp.lpSum(w*x[nm] for w, nm in zip(c, var_names))
    # Constraints
    for i in range(m):
        expr = pulp.lpSum(A[i,j]*x[var_names[j]] for j in range(n))
        if   sense_list[i] == "<=": prob += expr <= b[i]
        elif sense_list[i] == ">=": prob += expr >= b[i]
        else:                       prob += expr == b[i]
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    print("CBC status:", pulp.LpStatus[prob.status])
    print("Primal Z* (CBC):", pulp.value(prob.objective))
    for nm in var_names: print(f"  {nm} = {x[nm].value():.6g}")
    print_perf("CBC (primal sanity)", t_cbc)
except Exception as e:
    print("PuLP/CBC not available:", e)
    print_perf("CBC attempt (failed)", t_cbc)

# -----------------------------------------------------------
# (2) Two-phase Simplex (tableau) — we want to see all steps
# -----------------------------------------------------------
def make_standard_form(A, b, sense, var_names):
    """
    Convert Ax (sense) b, x>=0 to equality form for a tableau:
      • ensure RHS >= 0 (flip row if needed),
      • add SLACK for ≤, SURPLUS+ARTIFICIAL for ≥, ARTIFICIAL for =,
      • in Phase I, artificials are basic and cost is -1 to drive them to 0.
    Returns:
      A_std, b_std, all_col_names, basis0(list of basic col indices),
      art_cols(indices of artificial columns), c_phase1 (cost for Phase I).
    """
    m, n = A.shape
    A_std = A.copy(); b_std = b.copy(); sense = sense.copy()
    names = var_names.copy()
    basis, art_cols = [], []

    # Make RHS ≥ 0
    for i in range(m):
        if b_std[i] < 0:
            A_std[i,:] *= -1; b_std[i] *= -1
            if sense[i] == "<=": sense[i] = ">="
            elif sense[i] == ">=": sense[i] = "<="

    # Add columns row-by-row according to the sense
    for i in range(m):
        if sense[i] == "<=":
            col = np.zeros((m,1)); col[i,0] =  1.0            # slack
            A_std = np.hstack((A_std, col)); names.append(f"s{i+1}")
            basis.append(A_std.shape[1]-1)                     # slack basic
        elif sense[i] == ">=":
            col = np.zeros((m,1)); col[i,0] = -1.0             # surplus
            A_std = np.hstack((A_std, col)); names.append(f"u{i+1}")
            col = np.zeros((m,1)); col[i,0] =  1.0             # artificial
            A_std = np.hstack((A_std, col)); names.append(f"a{i+1}")
            basis.append(A_std.shape[1]-1); art_cols.append(A_std.shape[1]-1)
        else:  # equality
            col = np.zeros((m,1)); col[i,0] =  1.0             # artificial
            A_std = np.hstack((A_std, col)); names.append(f"a{i+1}")
            basis.append(A_std.shape[1]-1); art_cols.append(A_std.shape[1]-1)

    # Phase-I objective: maximize -(sum artificials)  (i.e., minimize their sum)
    c1 = np.zeros(A_std.shape[1]);  [c1.__setitem__(j, -1.0) for j in art_cols]
    return A_std, b_std, names, basis, art_cols, c1

def build_tableau(A_std, b_std, cost, basis):
    """
    Build the (m+1) x (n+1) tableau with top '-Z' row holding reduced costs.
    Start with row0 = cost and subtract c_B times each basic row to get
    reduced costs (c_j - z_j). RHS of row 0 equals (-Z).
    """
    m, n = A_std.shape
    T = np.zeros((m+1, n+1))
    T[1:, :n] = A_std; T[1:, -1] = b_std
    T[0, :n]  = cost;  T[0,  -1] = 0.0
    cB = T[0, basis]
    for i, bcol in enumerate(basis, start=1):
        T[0, :] -= cB[i-1]*T[i, :]
    return T

def choose_entering(T):
    """Dantzig rule (maximization): choose the column with largest positive reduced cost."""
    reduced = T[0, :-1]
    idx = np.where(reduced > 1e-10)[0]
    return int(idx[np.argmax(reduced[idx])]) if len(idx) else None

def ratio_test(T, j):
    """Minimum ratio among rows with a_ij>0; returns pivot row index. None → unbounded."""
    rows, ratios = [], []
    for i in range(1, T.shape[0]):
        a = T[i, j]
        if a > 1e-12:
            rows.append(i); ratios.append(T[i, -1] / a)
    if not ratios: return None
    return rows[int(np.argmin(ratios))]

def pivot(T, i, j):
    """Gauss–Jordan pivot: normalize pivot row and zero out column j elsewhere."""
    piv = T[i, j]; T[i, :] /= piv
    for r in range(T.shape[0]):
        if r == i: continue
        T[r, :] -= T[r, j]*T[i, :]

def print_tableau(T, basis, names, note=""):
    """
    Pretty print tableau with beginner explanations.
    Top row '-Z' shows reduced costs (c_j - z_j). Positive → entering candidate.
    RHS of '-Z' equals (-Z). At optimum, that equals -Z*. Row labels are BASIC vars.
    """
    df = pd.DataFrame(T, index=["-Z"] + [names[j] for j in basis],
                         columns=names + ["RHS"])
    print("\n" + "="*120)
    print(f"SIMPLEX TABLEAU {note}")
    print("- Row '-Z': reduced costs (c_j - z_j). Positive → ENTER to improve Z (max).")
    print("- RHS in '-Z' equals (-Z). At optimum this equals -Z*. Row labels are BASIC vars.")
    print("="*120)
    print(df.to_string())
    return df

def simplex_loop(T, basis, names, phase_tag="Phase"):
    """
    Run simplex with:
      • prints of enter/leave and the full tableau every iteration,
      • path of BFS snapshots for the SAG.
    Returns final tableau, final basis, and the path.
    """
    path = []
    def read_solution():
        x = np.zeros(T.shape[1]-1)
        for r, bcol in enumerate(basis, start=1): x[bcol] = T[r, -1]
        return x, -T[0, -1]
    # initial
    print_tableau(T, basis, names, note=f"({phase_tag} start: basis {[names[j] for j in basis]})")
    x0, z0 = read_solution(); path.append({"basis":basis.copy(),"x":x0.copy(),"z":z0})
    it = 0
    while True:
        it += 1
        j = choose_entering(T)
        if j is None: break
        i = ratio_test(T, j)
        if i is None: raise RuntimeError(f"Unbounded in {phase_tag}")
        print(f"\nIteration {it} ({phase_tag}): ENTER {names[j]}, LEAVE {names[basis[i-1]]}")
        pivot(T, i, j); basis[i-1] = j
        print_tableau(T, basis, names, note=f"({phase_tag} after pivot {it})")
        x, z = read_solution(); path.append({"basis":basis.copy(),"x":x.copy(),"z":z})
    return T, basis, path

# Phase I
t_phase1 = time.perf_counter()
A_std, b_std, names_all, B0, art_cols, c1 = make_standard_form(A, b, sense_list, var_names)
T1 = build_tableau(A_std, b_std, c1, B0.copy())
T1f, B1f, path1 = simplex_loop(T1, B0.copy(), names_all, "Phase I")
if abs(-T1f[0,-1]) > 1e-8:
    raise RuntimeError("Infeasible: artificials > 0 at Phase-I optimum.")
print_perf("Phase I (two-phase simplex)", t_phase1)

# Phase II: drop artificials; rebuild cost row for the *true* objective c
t_phase2 = time.perf_counter()
keep = np.ones(T1f.shape[1]-1, dtype=bool); [keep.__setitem__(j, False) for j in art_cols]
T2b = np.zeros((T1f.shape[0], keep.sum()+1))
T2b[1:, :-1] = T1f[1:, :-1][:, keep];  T2b[1:, -1] = T1f[1:, -1]
names2 = [names_all[j] for j in range(len(keep)) if keep[j]]

# true objective (only original decision vars carry coefficients)
c2 = np.zeros(len(names2))
for j, nm in enumerate(names2):
    if nm in var_names: c2[j] = c[var_names.index(nm)]

# Map Phase-I basis into reduced columns (replace artificials if they were basic)
B2 = []
for j in B1f:
    if j in art_cols:
        # Find the row where that artificial was basic and pivot any non-artificial in
        row = B1f.index(j) + 1
        cand = np.where(abs(T2b[row, :-1]) > 1e-9)[0]
        enter = int(cand[0])
        piv = T2b[row, enter]
        T2b[row, :] /= piv
        for r in range(T2b.shape[0]):
            if r == row: continue
            T2b[r, :] -= T2b[r, enter]*T2b[row, :]
        B2.append(enter)
    else:
        new_idx = np.where(keep[:j+1])[0].tolist().index(j)
        B2.append(new_idx)

# Build Phase-II reduced-cost row and run simplex
T2 = T2b.copy(); T2[0,:] = 0.0; T2[0,:-1] = c2
cB = T2[0, B2]
for r, bcol in enumerate(B2, start=1): T2[0,:] -= cB[r-1]*T2[r,:]
T2f, Bf, path2 = simplex_loop(T2, B2.copy(), names2, "Phase II")
print_perf("Phase II (two-phase simplex)", t_phase2)

# Read final solution (over current columns)
x_all = np.zeros(T2f.shape[1]-1)
for r, bcol in enumerate(Bf, start=1): x_all[bcol] = T2f[r,-1]
Z_star = -T2f[0,-1]

basis_names    = [names2[j] for j in Bf]
nonbasic_names = [nm for nm in names2 if nm not in basis_names]
print("\n=== FINAL (two-phase tableau) ===")
print("Z* =", Z_star)
print("BASIC:", basis_names)
print("NONBASIC:", nonbasic_names)
print("Decision vars:", {nm: x_all[names2.index(nm)] if nm in names2 else 0.0 for nm in var_names})

# ------------------------------------------------
# Binding / Non-binding report for original constraints (C1..C15)
# ------------------------------------------------
try:
    # Reconstruct decision-vector x_dec in original var order (x1..x9)
    x_dec = np.zeros(n)
    for j, nm in enumerate(var_names):
        x_dec[j] = x_all[names2.index(nm)] if nm in names2 else 0.0

    # Human-readable labels for constraints C1..C15 (matches comment block)
    constraint_labels = [
        "C1: total time ≤ 60",
        "C2: aerobic min ≥ 10",
        "C3: strength min ≥ 8",
        "C4: flexibility+mobility ≥ 6",
        "C5: HIIT cap ≤ 8",
        "C6: plyometrics cap ≤ 6",
        "C7: heavy cap ≤ 28",
        "C8: fatigue balance ≤ 0",
        "C9: strength upper ≤ 18",
        "C10: strength lower ≤ 18",
        "C11: upper - lower ≤ 4",
        "C12: lower - upper ≤ 4",
        "C13: yoga supply cap ≤ 12",
        "C14: core + active ≥ 8",
        f"C14b: active recovery ≥ {MIN_ACTIVE_RECOVERY:g}",
        "C15: cardio near strength ≥ 0",
    ]

    tol = 1e-8
    rows = []
    for i in range(m):
        lhs = float(A[i,:] @ x_dec)
        rhs = float(b[i])
        sense = sense_list[i]
        if sense == "<=":
            slack = rhs - lhs
        elif sense == ">=":
            slack = lhs - rhs
        else:  # equality (not used here, but safe)
            slack = abs(lhs - rhs)
        if abs(slack) <= tol:
            status = "BINDING"
        elif slack > tol:
            status = "NON-BINDING"
        else:
            status = "VIOLATED(?)"  # should not happen at optimum
        label = constraint_labels[i] if i < len(constraint_labels) else f"row {i+1}"
        rows.append({"id": f"C{i+1}", "label": label, "sense": sense,
                     "LHS": lhs, "RHS": rhs, "slack(≥0 by sense)": slack, "status": status})

    df_bind = pd.DataFrame(rows, columns=["id","label","sense","LHS","RHS","slack(≥0 by sense)","status"])
    print("\n--- CONSTRAINT STATUS @ OPTIMUM (original model) ---")
    print(df_bind.to_string(index=False))
except Exception as _e:
    print("\n[Binding-check skipped due to error]", _e)

# -----------------------------
# (3) SAG — Simplex adjacency graph (saved + shown)
# -----------------------------
def build_sag_table(path_phase1, names_phase1, path_phase2, names_phase2):
    """Combine Phase-I and Phase-II BFS snapshots into one readable table."""
    rows=[]; node=0
    def add(path, names, tag):
        nonlocal node
        for snap in path:
            bi = snap["basis"]; xv = snap["x"]; z = snap["z"]
            rec = {"node":node, "phase":tag, "Z":z,
                   "BI_idx":"{"+", ".join(str(j+1) for j in bi)+"}",
                   "BI_names":"{"+", ".join(names[j] for j in bi)+"}"}
            for v in var_names:
                rec[v] = xv[names.index(v)] if v in names else 0.0
            rows.append(rec); node += 1
    add(path_phase1, names_phase1, "I")
    add(path_phase2, names_phase2, "II")
    return pd.DataFrame(rows)

def plot_adjacency_readable(path_phase1, names_phase1,
                            path_phase2, names_phase2,
                            nodes_per_row=4, node_size=1800, font_size=9,
                            filename_png="SAG_full.png", filename_pdf="SAG_full.pdf",
                            show_plot=True):
    """
    Readable Simplex Adjacency Graph (SAG). 
    Each node is a BFS; edges correspond to one pivot operation.
    """
    combined = [(snap, names_phase1, "I") for snap in path_phase1] + \
               [(snap, names_phase2, "II") for snap in path_phase2]
    n = len(combined); rows = math.ceil(n / nodes_per_row)
    xs, ys = [], []
    for k in range(n):
        r = k // nodes_per_row; c = k % nodes_per_row
        xs.append(c); ys.append(-r)

    fig = plt.figure(figsize=(min(22, 4 + 3.2*nodes_per_row), 4 + 2.4*rows))
    for i, (snap, names_here, tag) in enumerate(combined):
        bi = snap["basis"]; z = snap["z"]; xv = snap["x"]
        bi_idx   = "{" + ", ".join(str(j+1) for j in bi) + "}"
        bi_names = "{" + ", ".join(names_here[j] for j in bi) + "}"
        lines=[]
        for grp in [("x1","x2","x3"),("x4","x5","x6"),("x7","x8","x9")]:
            lines.append("  ".join(f"{v}={xv[names_here.index(v)]:.3g}" if v in names_here else f"{v}=—"
                                   for v in grp))
        label = f"Node {i} (Phase {tag})\nBI={bi_idx}\nB={bi_names}\nZ={z:.3g}\n" + "\n".join(lines)
        plt.scatter(xs[i], ys[i], s=node_size, alpha=0.55 if i < n-1 else 0.75,
                    color="#4c78a8", edgecolor="k")
        plt.annotate(label, (xs[i], ys[i]), ha="center", va="center", fontsize=font_size)
        if i < n-1:
            plt.annotate("", xy=(xs[i+1], ys[i+1]), xytext=(xs[i], ys[i]),
                         arrowprops=dict(arrowstyle="->", color="gray"))

    plt.axis("off")
    plt.title("Simplex adjacency path (node=BFS; edge=one pivot)", fontsize=12)
    plt.tight_layout()

    # Save to absolute paths in the current working directory
    cwd = os.getcwd()
    out_png = os.path.abspath(os.path.join(cwd, filename_png))
    out_pdf = os.path.abspath(os.path.join(cwd, filename_pdf))
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, dpi=300, bbox_inches="tight")
    print(f"[SAG] Saved PNG → {out_png}")
    print(f"[SAG] Saved PDF → {out_pdf}")

    if show_plot:
        plt.show()
    else:
        plt.close(fig)

t_sag = time.perf_counter()
nodes_df = build_sag_table(path1, names_all, path2, names2)
print("\nSAG nodes (BI and all x1..x9):")
print(nodes_df.to_string(index=False))
plot_adjacency_readable(path1, names_all, path2, names2,
                        nodes_per_row=4, node_size=1800, font_size=9,
                        filename_png="SAG_full.png", filename_pdf="SAG_full.pdf",
                        show_plot=True)
print_perf("SAG (build + plot + save)", t_sag)

# ---------------------------------------------------------
# (4) Build B, B^{-1}, N, c_B, c_N and REDUCED COSTS
# ---------------------------------------------------------
t_mats = time.perf_counter()
# Extract canonical constraint matrix from the final tableau
A_can = T2f[1:, :-1]            # size m_eq x n_reduced (columns = names2)
b_eq  = T2f[1:, -1]
m_eq  = A_can.shape[0]

B_cols = Bf
N_cols = [j for j in range(A_can.shape[1]) if j not in B_cols]
B_mat  = A_can[:, B_cols]
N_mat  = A_can[:, N_cols]
B_inv  = np.linalg.inv(B_mat)

# Cost vector across current columns; decision vars carry original weights
c_full = np.zeros(A_can.shape[1])
for j, nm in enumerate(names2):
    if nm in var_names: c_full[j] = c[var_names.index(nm)]
cB = c_full[B_cols]
cN = c_full[N_cols]

# Reduced costs of non-basics:  r̄ = c_N − c_B^T B^{-1} N
reduced = cN - cB @ B_inv @ N_mat
xB      = b_eq.copy()           # basic variable values (since B is canonical)
yT      = cB @ B_inv            # dual prices (row vector y^T)

print("\n--- MATRICES ---")
print("B shape:", B_mat.shape, "  N shape:", N_mat.shape)
print("Max |B - I| (0 at canonical BFS) =", float(np.max(np.abs(B_mat - np.eye(m_eq)))))
print("Reduced costs (non-basics):", reduced)
print_perf("Matrices & reduced costs", t_mats)

# ---------------------------------------------------------
# (6) Solve the DUAL directly (PuLP/CBC) and print y
# ---------------------------------------------------------
t_dual = time.perf_counter()
try:
    import pulp
    dual = pulp.LpProblem("WorkoutLP_dual", pulp.LpMinimize)
    y=[]
    # Dual variable signs depend on primal constraint sense:
    #   primal ≤  → y ≥ 0      primal ≥  → y ≤ 0      primal = → y free
    for i in range(m):
        if   sense_list[i] == "<=": y.append(pulp.LpVariable(f"y{i+1}", lowBound=0))
        elif sense_list[i] == ">=": y.append(pulp.LpVariable(f"y{i+1}", upBound=0))
        else:
            yp = pulp.LpVariable(f"y{i+1}_p", lowBound=0)
            ym = pulp.LpVariable(f"y{i+1}_m", lowBound=0)
            y.append(yp - ym)  # free
    dual += pulp.lpSum(b[i]*y[i] for i in range(m))  # minimize b^T y
    # Dual constraints: A^T y ≥ c  (because primal is max with x ≥ 0)
    for j in range(n):
        dual += pulp.lpSum(A[i,j]*y[i] for i in range(m)) >= c[j], f"dual_col_{var_names[j]}"
    dual.solve(pulp.PULP_CBC_CMD(msg=False))
    print("\nDUAL status:", pulp.LpStatus[dual.status])
    print("DUAL objective b^T y =", pulp.value(dual.objective), "  (should equal Z*)")
    for i in range(m):
        yi = pulp.value(y[i])
        sign = ">=0" if sense_list[i]=="<=" else "<=0" if sense_list[i]==">=" else "free"
        print(f"  y[{i+1:>2d}] ({sign:>4s}) = {yi:.6g}")
    print_perf("Dual (PuLP/CBC)", t_dual)
except Exception as e:
    print("Dual solve failed:", e)
    print_perf("Dual attempt (failed)", t_dual)

# =====================================================================
# (PERF) Total script runtime + final memory snapshot — ADDED PER REQUEST
# =====================================================================
print_perf("TOTAL script runtime", _SCRIPT_T0)
