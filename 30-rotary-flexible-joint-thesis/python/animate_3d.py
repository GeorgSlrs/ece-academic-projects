"""
animate_3d.py
=============
Convenience wrapper:

- CLI θέλει απλά: animate_3d(sim)
- GUI χρησιμοποιεί RFJ3DPlayer απευθείας (non-blocking)
"""

from __future__ import annotations
from typing import Dict, Any
import matplotlib.pyplot as plt
from rfj_player_3d import RFJ3DPlayer


def animate_3d(sim: Dict[str,Any], speed: float = 1.0, loop: bool = True,
               save: bool = False, filename: str = "RFJ_3D.mp4", show: bool = True):
    player = RFJ3DPlayer(speed=speed, loop=loop)
    player.set_sim(sim)
    ani = player.start()

    if save:
        ani.save(filename, fps=30, dpi=180)
        print(f"[animate_3d] saved: {filename}")

    if show:
        plt.show()

    return player, ani