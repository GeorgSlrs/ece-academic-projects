# =====================================================================
# CIRCUIT TRAINING — MILP (PuLP/CBC) with ONE HAMILTONIAN PATH
# =====================================================================
# WHAT THIS SCRIPT DOES (high level):
#   • Builds a Mixed-Integer Linear Program (MILP) that picks an ordered circuit
#     of 27 exercises (ALL of them) subject to muscle-usage and intensity rules.
#   • Enforces a SINGLE directed Hamiltonian path that visits each exercise once.
#   • Minimizes total time = sum(durations) + sum(transition times).
#   • Solves with CBC via PuLP, then reconstructs and prints the ordered path.
#
# MODELING INSIGHT (paper form; no explicit start/end binaries):
#   VARIABLES:
#     • included[i] ∈ {0,1}       (x_i in the paper): whether exercise i is selected
#     • next[i->j] ∈ {0,1}        (f_ij in the paper): arc i→j is used (i≠j)
#     • order[i]  ∈ [0, N]        (s_i in the paper): position index for MTZ
#
#   CORE CONSTRAINTS (paper equations numbering in comments):
#     (2.1)   ∑ included = N
#     (2.2)   ∑ next     = N - 1
#     (2.3)   next[i->j] ≤ included[i]
#     (2.4)   next[i->j] ≤ included[j]
#     (2.5)   ∑_j next[i->j] ≤ 1        (at most one successor per node)
#     (2.6)   ∑_i next[i->j] ≤ 1        (at most one predecessor per node)
#     (2.7)   MTZ (no cycles): order[i] - order[j] + (N+1)*next[i->j] ≤ N, ∀i≠j
#     (2.9)   order[i] ≤ N * (outdeg(i)+indeg(i))   (order=0 if i has no incident arc)
#     (2.10)  ∑ order = N(N+1)/2
#
#   DOMAIN RULES (paper-style; same spirit as your original code):
#     • No two primaries in a row for the same muscle (forbid those arcs).
#     • No "three in a row" using the same muscle (pairwise ≤ 1 on consecutive arcs).
#     • Muscle totals (how many selected hit a muscle) within [lower, upper].
#     • No two high-intensity back-to-back (forbid those arcs).
#     • Average MET band for the selected set.
#
#   EXTRA PRINTS (for sanity / report):
#     • A small "PARAMETERS" digest (data summary).
#     • The number of decision variables (columns) and constraints (rows) we BUILT.
#     • A derivation-by-formula "expected constraints" count (so you see where 5710 comes from).
# =====================================================================

from __future__ import annotations
import time
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# OPTIONAL: memory reporting (handy but not essential). If psutil missing, skip.
# -----------------------------------------------------------------------------
try:
    import psutil
    HAVE_PSUTIL = True
except Exception:
    HAVE_PSUTIL = False

def rss_MB():
    """Return current resident memory (MB) if psutil is available; else None."""
    return psutil.Process().memory_info().rss/1024**2 if HAVE_PSUTIL else None

# -----------------------------------------------------------------------------
# SOLVER IMPORT (PuLP gives free access to the CBC MILP solver)
# -----------------------------------------------------------------------------
try:
    import pulp  # pip install pulp
except ImportError as e:
    raise SystemExit(
        "PuLP is not installed. Install it first:\n"
        "  pip install pulp\n"
        "Then run the script with:\n"
        "  py circuit_milp.py"
    )

# -----------------------------------------------------------------------------
# VERBOSITY & DEBUG TOGGLES
# -----------------------------------------------------------------------------
SHOW_SOLVER_LOG = True       # Set False to suppress CBC’s console chatter
DEBUG_DEGREE_REPORT = False  # Set True to print per-node in/out degrees after solve
DEBUG_PRINT_ARCS    = False  # Set True to print raw arc list (i -> j); normally OFF

# =====================================================================
# (1) DATA — the 27-exercise, 10-muscle instance
# =====================================================================
# EXERCISE SET (nodes of the path)
E = [
    "bench_press","chest_fly","dips","push_up",
    "pull_up","shoulder_press","upright_row","bent_over_row","lat_pulldown","biceps_curl",
    "deadlift","squat","back_extension","crunch","exercise_wheel","side_plank","leg_press",
    "lunge","push_up_rotation","jumping_jack","jumping_squat","burpee","mountain_climber",
    "plyo_lunge","lunge_jump","step_up","battle_rope"
]

# MUSCLE GROUPS (used for load balancing rules)
M = ["chest","shoulders","triceps","biceps","lats","trapezius",
     "lower_back","abs","quads","glutes_hams"]

# We are selecting EVERY exercise (you asked for all 27)
N_chosen = 27

# ----------------------
# Duration per exercise (minutes)
# ----------------------
duration = {
    "bench_press":0.42, "chest_fly":0.40, "dips":0.42, "push_up":0.40,
    "pull_up":0.40, "shoulder_press":0.40, "upright_row":0.40, "bent_over_row":0.42, "lat_pulldown":0.40, "biceps_curl":0.38,
    "deadlift":0.45, "squat":0.42, "back_extension":0.40, "crunch":0.35, "exercise_wheel":0.33, "side_plank":0.33, "leg_press":0.40,
    "lunge":0.40, "push_up_rotation":0.40, "jumping_jack":0.35, "jumping_squat":0.40, "burpee":0.45, "mountain_climber":0.38,
    "plyo_lunge":0.40, "lunge_jump":0.38, "step_up":0.40, "battle_rope":0.40
}

# ----------------------
# Transition times t[i,j] (minutes)
# ----------------------
# Defaults to ~0.12 min (≈ 7.2 seconds); some pairs longer to reflect station changes.
t = pd.DataFrame(0.12, index=E, columns=E)
for e in E:
    t.loc[e, e] = 0.0  # no self-arc

# Specific longer transitions (hand-tuned)
for (i, j), val in {
    ("exercise_wheel","jumping_squat"):0.25,
    ("jumping_squat","exercise_wheel"):0.25,
    ("upright_row","biceps_curl"):0.20,
    ("deadlift","squat"):0.20,
    ("squat","deadlift"):0.20,
    ("bench_press","chest_fly"):0.18,
    ("chest_fly","bench_press"):0.18,
    ("pull_up","lat_pulldown"):0.22,
    ("lat_pulldown","pull_up"):0.22,
    ("battle_rope","biceps_curl"):0.20,
    ("bent_over_row","deadlift"):0.22,
    ("deadlift","bent_over_row"):0.22,
}.items():
    t.loc[i, j] = val

# ----------------------
# Intensity (MET) data
# ----------------------
MET = {
    "bench_press":7.0, "chest_fly":6.5, "dips":8.0, "push_up":7.0,
    "pull_up":8.0, "shoulder_press":7.5, "upright_row":6.5, "bent_over_row":6.8, "lat_pulldown":6.8, "biceps_curl":6.5,
    "deadlift":8.0, "squat":8.0, "back_extension":6.0, "crunch":6.0, "exercise_wheel":7.5, "side_plank":6.0, "leg_press":7.0,
    "lunge":7.5, "push_up_rotation":7.5, "jumping_jack":7.0, "jumping_squat":8.5, "burpee":9.5, "mountain_climber":8.0,
    "plyo_lunge":8.5, "lunge_jump":8.0, "step_up":7.0, "battle_rope":8.5
}
T_MET = 8.0
high = {e: 1 if MET[e] >= T_MET else 0 for e in E}  # 1 if high intensity

# ----------------------
# Muscle work matrix  w_im ∈ {0,1,2}
# ----------------------
# 0 = unused, 1 = secondary work, 2 = primary work on muscle m by exercise e.
work = pd.DataFrame(0, index=E, columns=M)

# Chest family
work.loc["bench_press",      ["chest","triceps","shoulders"]] = [2,1,1]
work.loc["chest_fly",        ["chest","shoulders"]]           = [2,1]
work.loc["dips",             ["chest","triceps"]]             = [2,2]
work.loc["push_up",          ["chest","triceps","abs"]]       = [2,1,1]
work.loc["push_up_rotation", ["chest","shoulders","triceps","abs"]] = [2,1,1,1]

# Back / pulls
work.loc["pull_up",          ["lats","biceps"]]               = [2,1]
work.loc["bent_over_row",    ["lats","trapezius","biceps","lower_back"]] = [2,1,1,1]
work.loc["lat_pulldown",     ["lats","biceps"]]               = [2,1]

# Shoulders
work.loc["shoulder_press",   ["shoulders","triceps"]]         = [2,1]
work.loc["upright_row",      ["shoulders","trapezius"]]       = [2,1]
work.loc["battle_rope",      ["shoulders","trapezius","abs","biceps","triceps"]] = [2,1,1,1,1]

# Arms
work.loc["biceps_curl",      ["biceps"]]                      = [2]

# Posterior chain / legs / core
work.loc["deadlift",         ["lower_back","glutes_hams","quads","trapezius"]] = [2,2,1,1]
work.loc["squat",            ["quads","glutes_hams"]]         = [2,2]
work.loc["back_extension",   ["lower_back","glutes_hams"]]    = [2,1]
work.loc["crunch",           ["abs"]]                         = [2]
work.loc["exercise_wheel",   ["abs","lower_back"]]            = [2,1]
work.loc["side_plank",       ["abs"]]                         = [2]
work.loc["leg_press",        ["quads","glutes_hams"]]         = [2,1]
work.loc["lunge",            ["quads","glutes_hams"]]         = [2,2]
work.loc["jumping_jack",     ["quads","glutes_hams","shoulders"]] = [1,1,1]
work.loc["jumping_squat",    ["quads","glutes_hams"]]         = [2,2]
work.loc["burpee",           ["quads","glutes_hams","chest","shoulders","triceps","abs"]] = [2,2,1,1,1,1]
work.loc["mountain_climber", ["abs","quads","shoulders"]]     = [2,1,1]
work.loc["plyo_lunge",       ["quads","glutes_hams"]]         = [2,2]
work.loc["lunge_jump",       ["quads","glutes_hams"]]         = [2,2]
work.loc["step_up",          ["quads","glutes_hams"]]         = [2,1]

# Binary mask "used" = 1{ w_im > 0 }
used = (work > 0).astype(int)

# ----------------------
# Muscle totals (global load bounds)
# ----------------------
muscle_lower_limit = {"chest":3,"shoulders":3,"triceps":3,"biceps":3,"lats":1,"trapezius":0,
                      "lower_back":3,"abs":5,"quads":5,"glutes_hams":5}
muscle_upper_limit = {"chest":20,"shoulders":20,"triceps":20,"biceps":12,"lats":10,"trapezius":12,
                      "lower_back":12,"abs":16,"quads":24,"glutes_hams":24}

# ----------------------
# Average MET band constraints
# ----------------------
intensity_lower_limit = 6.5
intensity_upper_limit = 9.2

# =====================================================================
# (2) BUILD AND SOLVE THE MILP (single Hamiltonian path; paper-only equations)
# =====================================================================
t0 = time.perf_counter()
print(f"[{(time.perf_counter()-t0):5.2f}s | RSS≈{(rss_MB() or 0):.1f} MB] Data ready.")
print("PARAMETERS")
print(f"  |E|={len(E)} exercises, |M|={len(M)} muscles, N={N_chosen}")
print(f"  mean(duration)={np.mean(list(duration.values())):.3f} min")
print(f"  mean(MET)={np.mean(list(MET.values())):.2f}  (high if >= {T_MET})")
print(f"  mean(transition>0)={t.values[t.values>0].mean():.3f} min\n")

# ----------------------
# Create PuLP problem: MINIMIZE total time (durations + transitions)
# ----------------------
prob = pulp.LpProblem("CircuitTraining", pulp.LpMinimize)

# ----------------------
# Decision variables (paper notation: x_i, f_ij, s_i)
# ----------------------
included = {e: pulp.LpVariable(f"included[{e}]", 0, 1, cat="Binary") for e in E}  # x_i
next_ex  = {(i, j): pulp.LpVariable(f"next[{i}->{j}]", 0, 1, cat="Binary")
            for i in E for j in E if i != j}                                     # f_ij
order    = {e: pulp.LpVariable(f"order[{e}]", lowBound=0, upBound=N_chosen,
                               cat="Continuous") for e in E}                      # s_i

# ----------------------
# Objective function
# ----------------------
prob += (
    pulp.lpSum(duration[e] * included[e] for e in E) +
    pulp.lpSum(t.loc[i, j] * next_ex[(i, j)] for i in E for j in E if i != j)
), "total_time"

# ----------------------
# CORE: Paper's equations (2.1)–(2.10)
# ----------------------

# (2.1) pick exactly N exercises
prob += pulp.lpSum(included[e] for e in E) == N_chosen, "number_of_exercises_in_circuit"

# (2.2) total arcs equals N-1
prob += pulp.lpSum(next_ex[(i, j)] for i in E for j in E if i != j) == N_chosen - 1, \
        "number_of_following_exercises_in_circuit"

# (2.3)–(2.4) link f_ij to x_i, x_j
for i in E:
    for j in E:
        if i == j:
            continue
        prob += next_ex[(i, j)] <= included[i], f"follow_only_if_included_i[{i}->{j}]"
        prob += next_ex[(i, j)] <= included[j], f"follow_only_if_included_j[{i}->{j}]"

# (2.5) at most one outgoing per node
for i in E:
    prob += pulp.lpSum(next_ex[(i, j)] for j in E if j != i) <= 1, f"at_most_one_follows[{i}]"

# (2.6) at most one incoming per node
for j in E:
    prob += pulp.lpSum(next_ex[(i, j)] for i in E if i != j) <= 1, f"at_most_one_precedes[{j}]"

# (2.7) MTZ / no-cycle; BIG = N+1, RHS = N   (paper form)
BIG = N_chosen + 1
for i in E:
    for j in E:
        if i == j:
            continue
        prob += order[i] - order[j] + BIG * next_ex[(i, j)] <= N_chosen, f"no_cycle[{i}->{j}]"

# (2.9) dummy-zero-if-isolated: if node i has no incident arc, force order[i]=0
for i in E:
    prob += order[i] <= N_chosen * (
        pulp.lpSum(next_ex[(i, j)] for j in E if j != i) +
        pulp.lpSum(next_ex[(j, i)] for j in E if j != i)
    ), f"dummy_zero_if_not_included[{i}]"

# (2.10) sum of orders equals N(N+1)/2 (clean scaling; uniqueness of 1..N)
prob += pulp.lpSum(order[e] for e in E) == N_chosen * (N_chosen + 1) / 2, "sum_of_orders"

# ----------------------
# DOMAIN-SPECIFIC RULES (paper-style; same spirit as your old code)
# ----------------------

# (A) No two primaries in a row for the same muscle m: forbid those arcs
for m in M:
    prim = [e for e in E if work.loc[e, m] == 2]
    for i in prim:
        for j in prim:
            if i != j:
                prob += next_ex[(i, j)] == 0, f"no_two_primaries[{m},{i}->{j}]"

# (B) No "three in a row" using the same muscle m:
for m in M:
    used_m = [e for e in E if used.loc[e, m] == 1]
    for i in used_m:
        for j in used_m:
            if i == j:
                continue
            for k in used_m:
                if k == j or k == i:
                    continue
                prob += next_ex[(i, j)] + next_ex[(j, k)] <= 1, f"no_three_in_row[{m},{i}->{j}->{k}]"

# (C) Muscle totals (global load bounds): how many selected exercises hit muscle m
for m in M:
    prob += pulp.lpSum(used.loc[e, m] * included[e] for e in E) >= muscle_lower_limit[m], f"muscle_total_lb[{m}]"
    prob += pulp.lpSum(used.loc[e, m] * included[e] for e in E) <= muscle_upper_limit[m], f"muscle_total_ub[{m}]"

# (D) No two high-intensity exercises back-to-back:
for i in E:
    for j in E:
        if i != j and high[i] == 1 and high[j] == 1:
            prob += next_ex[(i, j)] == 0, f"no_two_high[{i}->{j}]"

# (E) Average MET over the selected set within a band:
prob += pulp.lpSum(MET[e] * included[e] for e in E) >= intensity_lower_limit * N_chosen, "intensity_lb"
prob += pulp.lpSum(MET[e] * included[e] for e in E) <= intensity_upper_limit * N_chosen, "intensity_ub"

# ----------------------
# >>> NEW: PRINT MODEL SIZE (decision variables & constraints) BEFORE SOLVE
# ----------------------
all_vars = prob.variables()  # decision variables only (PuLP objects)
num_vars = len(all_vars)
num_rows = len(prob.constraints)  # constraints we built (before presolve)

# Derive counts used in the "formula explanation" so you can see 5710:
N = N_chosen
pairs = N * (N - 1)
# Count primaries per muscle and "used" per muscle for the sums:
p_m_list = [int((work[m] == 2).sum()) for m in M]
a_m_list = [int(used[m].sum()) for m in M]
h = sum(high.values())

count_select_N = 1                       # (2.1)
count_arcs_Nm1 = 1                       # (2.2)
count_link_ij  = 2 * pairs               # (2.3)+(2.4)
count_out_le1  = N                        # (2.5)
count_in_le1   = N                        # (2.6)
count_mtz      = pairs                    # (2.7)
count_iso0     = N                        # (2.9)
count_sumorder = 1                        # (2.10)
count_no2prim  = sum(p * (p - 1) for p in p_m_list)
count_no3row   = sum(a * (a - 1) * (a - 2) for a in a_m_list)
count_muscle_total = 2 * len(M)          # lower+upper per muscle
count_no_high  = h * (h - 1)              # ordered pairs
count_metband  = 2

expected_constraints = (
    count_select_N + count_arcs_Nm1 + count_link_ij + count_out_le1 + count_in_le1 +
    count_mtz + count_iso0 + count_sumorder + count_no2prim + count_no3row +
    count_muscle_total + count_no_high + count_metband
)

print("MODEL SIZE (pre-presolve)")
print(f"  Decision variables (columns): {num_vars}")
print(f"  Constraints (rows):           {num_rows}")
print("  By-formula expected rows breakdown:")
print(f"    (2.1) select N                : {count_select_N}")
print(f"    (2.2) arcs N-1                : {count_arcs_Nm1}")
print(f"    (2.3)+(2.4) link f to x       : {count_link_ij}")
print(f"    (2.5) out-degree ≤ 1          : {count_out_le1}")
print(f"    (2.6) in-degree ≤ 1           : {count_in_le1}")
print(f"    (2.7) MTZ pairs               : {count_mtz}")
print(f"    (2.9) order zero if isolated  : {count_iso0}")
print(f"    (2.10) sum of orders          : {count_sumorder}")
print(f"    no two primaries in a row     : {count_no2prim}")
print(f"    no three-in-a-row per muscle  : {count_no3row}")
print(f"    muscle totals (lb+ub)         : {count_muscle_total}")
print(f"    no high→high                  : {count_no_high}")
print(f"    MET band (lb+ub)              : {count_metband}")
print(f"  EXPECTED TOTAL                  : {expected_constraints}\n")

# ----------------------
# SOLVE the MILP with CBC
# ----------------------
solver = pulp.PULP_CBC_CMD(msg=SHOW_SOLVER_LOG)
t_solve = time.perf_counter()
prob.solve(solver)
t_solve = time.perf_counter() - t_solve

# =====================================================================
# (3) READ SOLUTION + RECONSTRUCT THE SINGLE ORDERED PATH
# =====================================================================
status = pulp.LpStatus[prob.status]
print("\n=== MILP (CBC) RESULT ===")
print("Status:", status)
obj_val = pulp.value(prob.objective)
print("Objective (minutes):", float(obj_val) if obj_val is not None else None)

if status != "Optimal":
    print("[WARN] Model status is not Optimal. The constraints may be too tight or conflicting.")
    print(f"[Solve time: {t_solve:.2f}s | RSS≈{(rss_MB() or 0):.1f} MB]")
    raise SystemExit(0)

# Selected set (should be all 27 by construction)
sel = [e for e in E if (included[e].value() or 0) > 0.5]
print(f"Selected count = {len(sel)} (expected {N_chosen})")

# >>> Print inclusion binaries x_i for all exercises
print("\nInclusion variables x[e] (included[e]):")
for e in E:
    val = included[e].value()
    x = int(round(val)) if val is not None else None
    print(f"  x[{e}] = {x}")

# Build successor (succ) and predecessor (pred) maps from chosen arcs next[i->j]=1
succ, pred, arc_list = {}, {}, []
for i in E:
    for j in E:
        if i == j:
            continue
        val = next_ex[(i, j)].value()
        if val is not None and val > 0.5:
            succ[i] = j
            pred[j] = i
            arc_list.append((i, j))

if DEBUG_PRINT_ARCS:
    print("\n[DEBUG] Raw arcs with next=1 (each is an edge in the path):")
    for (i, j) in arc_list:
        print(f"  {i} -> {j}")

print("\nArc count chosen:", len(arc_list), "(expected N-1 =", N_chosen-1, ")")

# Identify the true start node (no predecessor)
start_node = next((e for e in sel if e not in pred), None)

# Reconstruct the path by walking succ from the start node
path = []
if start_node is not None:
    cur = start_node
    seen = set()
    while cur is not None and cur not in seen:
        path.append(cur)
        seen.add(cur)
        cur = succ.get(cur, None)

# Sanity check: path length should be N (27). If not, print diagnostics.
if len(path) == N_chosen:
    print("\nPath (ordered):")
    print("  " + " -> ".join(path))
else:
    print("\n[WARN] Reconstructed path length =", len(path), f"(expected {N_chosen}).")
    if path:
        print("Partial path:")
        print("  " + " -> ".join(path))
    leftovers = [e for e in sel if e not in set(path)]
    if leftovers:
        print("Unreached selected nodes:", leftovers)

# Optional: degree report per node
if DEBUG_DEGREE_REPORT:
    print("\n[DEBUG] Degree report (in, out) for selected nodes:")
    for e in sel:
        out_deg = sum(1 for j in E if j != e and (next_ex[(e, j)].value() or 0) > 0.5)
        in_deg  = sum(1 for i in E if i != e and (next_ex[(i, e)].value() or 0) > 0.5)
        print(f"  {e:18s}  in={in_deg}  out={out_deg}")

print(f"\n[Solve time: {t_solve:.2f}s | RSS≈{(rss_MB() or 0):.1f} MB]")
