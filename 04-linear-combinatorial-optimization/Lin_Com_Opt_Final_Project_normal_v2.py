# =====================================================================
# WORKOUT LP — TWO-PHASE SIMPLEX + TABLEAUX + READABLE SAG + SA (x1..x9 ONLY) + DUAL
# =====================================================================
# Public portfolio copy. Academic coursework.

import math
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys, time
try:
    import psutil
except Exception:
    psutil = None
try:
    import resource
except Exception:
    resource = None

_SCRIPT_T0 = time.perf_counter()

def _bytes_to_mb(x):
    return f"{(x / (1024*1024)):.2f} MB" if isinstance(x, (int, float)) and x is not None else "N/A"

def get_current_rss_bytes():
    if psutil is not None:
        try:
            return psutil.Process(os.getpid()).memory_info().rss
        except Exception:
            pass
    return None

def get_peak_rss_bytes():
    if resource is None:
        return None
    try:
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(peak if sys.platform.startswith("darwin") else peak * 1024)
    except Exception:
        return None

def print_perf(tag, t0):
    dt = time.perf_counter() - t0
    print(f"[PERF] {tag}: {dt:.6f} s | RSS={_bytes_to_mb(get_current_rss_bytes())} | Peak={_bytes_to_mb(get_peak_rss_bytes())}")

var_names = ["x1","x2","x3","x4","x5","x6","x7","x8","x9"]
c = np.array([5.0, 8.0, 6.5, 6.5, 4.0, 2.0, 3.0, 5.5, 1.5], dtype=float)
MIN_ACTIVE_RECOVERY = 8.0
A_list, b_list, sense_list = [], [], []
A_list.append([1,1,1,1,1,1,1,1,1]); b_list.append(60.0); sense_list.append("<=")
A_list.append([1,2,0,0,0,0,0.5,1.5,0.5]); b_list.append(10); sense_list.append(">=")
A_list.append([0,0.5,1,1,0.5,0,0,0.5,0]); b_list.append(8.0); sense_list.append(">=")
A_list.append([0,0,0,0,0,1,1,0,0]); b_list.append(6.0); sense_list.append(">=")
A_list.append([0,1,0,0,0,0,0,0,0]); b_list.append(8.0); sense_list.append("<=")
A_list.append([0,0,0,0,0,0,0,1,0]); b_list.append(6.0); sense_list.append("<=")
A_list.append([0,1,1,1,0,0,0,1,0]); b_list.append(28.0); sense_list.append("<=")
A_list.append([0,1,1,1,-2,-4,-4,1,-4]); b_list.append(0.0); sense_list.append("<=")
A_list.append([0,0,1,0,0,0,0,0,0]); b_list.append(18.0); sense_list.append("<=")
A_list.append([0,0,0,1,0,0,0,0,0]); b_list.append(18.0); sense_list.append("<=")
A_list.append([0,0,1,-1,0,0,0,0,0]); b_list.append(4.0); sense_list.append("<=")
A_list.append([0,0,-1,1,0,0,0,0,0]); b_list.append(4.0); sense_list.append("<=")
A_list.append([0,0,0,0,0,0,1,0,0]); b_list.append(12.0); sense_list.append("<=")
A_list.append([0,0,0,0,1,0,0,0,1]); b_list.append(8.0); sense_list.append(">=")
A_list.append([0,0,0,0,0,0,0,0,1]); b_list.append(MIN_ACTIVE_RECOVERY); sense_list.append(">=")
A_list.append([1,0,-0.8,-0.8,0,0,0,0,0]); b_list.append(0.0); sense_list.append(">=")
A = np.array(A_list, dtype=float)
b = np.array(b_list, dtype=float)
m, n = A.shape

def make_standard_form(A, b, sense, var_names):
    m, n = A.shape
    A_std = A.copy(); b_std = b.copy(); sense = sense.copy()
    names = var_names.copy(); basis, art_cols = [], []
    for i in range(m):
        if b_std[i] < 0:
            A_std[i,:] *= -1; b_std[i] *= -1
            if sense[i] == "<=": sense[i] = ">="
            elif sense[i] == ">=": sense[i] = "<="
    for i in range(m):
        if sense[i] == "<=":
            col = np.zeros((m,1)); col[i,0] = 1.0
            A_std = np.hstack((A_std, col)); names.append(f"s{i+1}"); basis.append(A_std.shape[1]-1)
        elif sense[i] == ">=":
            col = np.zeros((m,1)); col[i,0] = -1.0
            A_std = np.hstack((A_std, col)); names.append(f"u{i+1}")
            col = np.zeros((m,1)); col[i,0] = 1.0
            A_std = np.hstack((A_std, col)); names.append(f"a{i+1}")
            basis.append(A_std.shape[1]-1); art_cols.append(A_std.shape[1]-1)
        else:
            col = np.zeros((m,1)); col[i,0] = 1.0
            A_std = np.hstack((A_std, col)); names.append(f"a{i+1}")
            basis.append(A_std.shape[1]-1); art_cols.append(A_std.shape[1]-1)
    c1 = np.zeros(A_std.shape[1])
    for j in art_cols: c1[j] = -1.0
    return A_std, b_std, names, basis, art_cols, c1

def build_tableau(A_std, b_std, cost, basis):
    m, n = A_std.shape
    T = np.zeros((m+1, n+1))
    T[1:, :n] = A_std; T[1:, -1] = b_std
    T[0, :n] = cost
    cB = T[0, basis]
    for i, bcol in enumerate(basis, start=1):
        T[0, :] -= cB[i-1]*T[i,:]
    return T

def choose_entering(T, tol=1e-10):
    rc = T[0,:-1]
    candidates = np.where(rc > tol)[0]
    return None if len(candidates)==0 else int(candidates[np.argmax(rc[candidates])])

def ratio_test(T, j, tol=1e-12):
    col=T[1:,j]; rhs=T[1:,-1]
    valid=np.where(col>tol)[0]
    if len(valid)==0: return None
    ratios=rhs[valid]/col[valid]
    return int(valid[np.argmin(ratios)])+1

def pivot(T,i,j):
    T[i,:]/=T[i,j]
    for r in range(T.shape[0]):
        if r!=i: T[r,:]-=T[r,j]*T[i,:]

def simplex_loop(T,basis,names):
    while True:
        j=choose_entering(T)
        if j is None: break
        i=ratio_test(T,j)
        if i is None: raise RuntimeError("Unbounded")
        pivot(T,i,j); basis[i-1]=j
    return T,basis

if __name__ == "__main__":
    A_std,b_std,names,basis,art_cols,c1=make_standard_form(A,b,sense_list,var_names)
    T1=build_tableau(A_std,b_std,c1,basis.copy())
    T1,basis1=simplex_loop(T1,basis.copy(),names)
    print("Phase-I objective:", -T1[0,-1])
    print_perf("two-phase simplex demo", _SCRIPT_T0)
