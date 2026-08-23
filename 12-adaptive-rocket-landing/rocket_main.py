"""
rocket_main.py
=============

THIS IS THE ONLY FILE YOU RUN.
------------------------------

You asked for a setup where you simply run ONE script and everything happens:
  - the adaptive autopilot controller runs
  - the live animation GUI runs (Start / Stop / Restart / End)
  - a log is saved when you press End
  - AFTER you press End, the plotting windows appear automatically

So this file is intentionally tiny: it just calls the "do everything" function
inside rocket_simulator.py.

Run:
  python rocket_main.py

(You do not need any command-line arguments.)

Files in this 3-file project:
  1) rocket_main.py      -> entry point (this file)
  2) rocket_simulator.py -> simulator + controller + GUI + plotting
  3) rocket_dynamics.py  -> pure dynamics only (x_dot = f(x,u))
"""

from __future__ import annotations

# The entire project logic lives here:
from rocket_simulator import run_everything


if __name__ == "__main__":
    run_everything()
