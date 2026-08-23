"""
projection_helper.py
====================

This file contains ONLY the nominal-trajectory "projection" helper used by the
hardware TVLQR runner.

Why this exists:
  - Your big script (RS_II_HW_4_new_model.py) may import heavy dependencies
    (cyipopt, matplotlib, etc.)
  - The hardware runner should stay lightweight and depend only on:
        numpy + pyCandle
  - So we put the projection method here as a tiny, clean dependency.

Function:
  pick_progress_farthest_inside_tube(x, X_nom, W, r)

Given the current state x and a nominal trajectory X_nom[k], it finds the
"farthest" index k along the nominal that is still within a weighted tube:
    dist(x, X_nom[k]) = sqrt( (x - X_nom[k])^T W (x - X_nom[k]) )

If no point is inside the tube, it returns the nearest point.

IMPORTANT HARDWARE FIX:
  Angles are periodic (wrap at +/-pi). If you don't wrap the angle differences,
  the projection can choose wildly wrong points near the discontinuity.
"""

import numpy as np


def _wrap_to_pi(a):
    """Wrap angle(s) to [-pi, pi]. Works with scalars or numpy arrays."""
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def pick_progress_farthest_inside_tube(x, X_nom, W, r):
    """
    Choose a reference index k_ref on the nominal trajectory.

    Inputs:
      x     : current state (4,)  -> [q1, q2, dq1, dq2]
      X_nom : nominal states (N,4)
      W     : weighting matrix (4,4) (positive definite)
      r     : tube radius (scalar)

    Returns:
      k_ref : chosen nominal index (int)
      dist  : weighted distance at that index (float)
    """
    x = np.asarray(x, dtype=float).reshape(-1)
    X_nom = np.asarray(X_nom, dtype=float)
    W = np.asarray(W, dtype=float)
    r = float(r)

    # dx[k] = X_nom[k] - x
    dx = X_nom - x[None, :]

    # IMPORTANT: wrap angle differences for q1,q2
    dx[:, 0] = _wrap_to_pi(dx[:, 0])
    dx[:, 1] = _wrap_to_pi(dx[:, 1])

    # squared weighted distances:
    # d2[k] = dx[k]^T W dx[k]
    d2 = np.einsum("ni,ij,nj->n", dx, W, dx)

    # Find all indices inside the tube
    inside = np.where(d2 <= (r * r))[0]

    if inside.size == 0:
        # No point inside: choose the closest
        k = int(np.argmin(d2))
        return k, float(np.sqrt(d2[k]))

    # Farthest (largest index) still inside tube
    k = int(inside[-1])
    return k, float(np.sqrt(d2[k]))
