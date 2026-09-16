"""
rfj_player_3d.py
================
Non-blocking 3D player object with Start/Stop/Restart.

Fixes:
- Adds pause/play/restart methods
- Removes FuncAnimation caching warning (cache_frame_data=False)
- Uses wall-clock mapping so sim-time doesn't crawl even at low FPS

Visuals:
- base plate, motor body, shaft, hub
- rotating link (phi)
- hub tick (theta)
- spring helix + damper line (shows alpha visually)
"""

from __future__ import annotations
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from typing import Dict, Any


def _rotz(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0],
                     [s,  c, 0],
                     [0,  0, 1]], float)


def _make_cylinder(radius: float, height: float, n: int = 40, z0: float = 0.0):
    ang = np.linspace(0, 2*np.pi, n)
    z = np.array([z0, z0 + height])
    A, Z = np.meshgrid(ang, z)
    X = radius*np.cos(A)
    Y = radius*np.sin(A)
    return X, Y, Z


def _make_box(L: float, W: float, H: float) -> np.ndarray:
    x0, x1 = 0.0, L
    y0, y1 = -W/2, W/2
    z0, z1 = -H/2, H/2
    return np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ], float)


def _faces(v: np.ndarray):
    return [
        [v[0], v[1], v[2], v[3]],
        [v[4], v[5], v[6], v[7]],
        [v[0], v[1], v[5], v[4]],
        [v[1], v[2], v[6], v[5]],
        [v[2], v[3], v[7], v[6]],
        [v[3], v[0], v[4], v[7]],
    ]


def _helix(p0: np.ndarray, p1: np.ndarray, turns: int = 8, amp: float = 0.006, n: int = 120):
    p0 = np.asarray(p0, float).reshape(3)
    p1 = np.asarray(p1, float).reshape(3)
    v = p1 - p0
    L = np.linalg.norm(v) + 1e-12
    u = v / L

    helper = np.array([1, 0, 0], float) if abs(u[2]) > 0.8 else np.array([0, 0, 1], float)
    n1 = np.cross(u, helper)
    n1 = n1 / (np.linalg.norm(n1) + 1e-12)
    n2 = np.cross(u, n1)

    s = np.linspace(0, L, n)
    ang = 2*np.pi*turns*s/L
    pts = (p0[None, :] +
           s[:, None]*u[None, :] +
           amp*np.cos(ang)[:, None]*n1[None, :] +
           amp*np.sin(ang)[:, None]*n2[None, :])
    return pts


class RFJ3DPlayer:
    def __init__(self, speed: float = 1.0, loop: bool = True):
        self.speed = float(speed)
        self.loop = bool(loop)

        self.sim = None
        self.t = None
        self.theta = None
        self.phi = None
        self.step_time = None

        # Playback state
        self._wall_t0 = time.perf_counter()
        self.playing = True
        self._paused_sim_time = None  # stores sim-time at pause

        # Figure / axes
        self.fig = plt.figure(figsize=(9.6, 6.4))
        try:
            self.fig.canvas.manager.set_window_title("RFJ 3D Player")
        except Exception:
            pass

        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.set_title("Rotary Flexible Joint (3D)")
        self.ax.set_xlabel("x [m]")
        self.ax.set_ylabel("y [m]")
        self.ax.set_zlabel("z [m]")
        self.ax.view_init(elev=22, azim=-58)

        # Geometry constants
        self.L_link = 0.30
        self.hub_r, self.hub_h = 0.020, 0.020
        self.shaft_r, self.shaft_h = 0.007, 0.030
        self.motor_r, self.motor_h = 0.030, 0.040
        self.link_w, self.link_h = 0.030, 0.012

        # Base plate
        plate_L, plate_W = 0.50, 0.40
        plate_z = -0.015
        plate = np.array([
            [-plate_L/2, -plate_W/2, plate_z],
            [ plate_L/2, -plate_W/2, plate_z],
            [ plate_L/2,  plate_W/2, plate_z],
            [-plate_L/2,  plate_W/2, plate_z],
        ])
        self.ax.add_collection3d(Poly3DCollection(
            [plate],
            facecolor=(0.965, 0.97, 0.985, 1.0),
            edgecolor=(0.86, 0.86, 0.9, 1.0),
        ))

        # Motor body (offset left)
        Xm, Ym, Zm = _make_cylinder(self.motor_r, self.motor_h, n=40, z0=0.0)
        self.ax.plot_surface(Xm - 0.045, Ym, Zm, linewidth=0, alpha=0.92, color=(0.55, 0.55, 0.58))

        # Shaft
        Xs, Ys, Zs = _make_cylinder(self.shaft_r, self.shaft_h, n=30, z0=self.motor_h*0.25)
        self.ax.plot_surface(Xs, Ys, Zs, linewidth=0, alpha=0.95, color=(0.35, 0.35, 0.38))

        # Hub cylinder
        Xc, Yc, Zc = _make_cylinder(self.hub_r, self.hub_h, n=40, z0=self.shaft_h + self.motor_h*0.25)
        self.ax.plot_surface(Xc, Yc, Zc, linewidth=0, alpha=0.98, color=(0.82, 0.82, 0.86))

        # Link height
        self.z_link = self.shaft_h + self.motor_h*0.25 + self.hub_h*0.6

        # Link (dynamic)
        self.link_v0 = _make_box(self.L_link, self.link_w, self.link_h)
        self.link_v0[:, 2] += self.z_link

        self.link_poly = Poly3DCollection(
            _faces(self.link_v0),
            facecolor=(0.22, 0.54, 0.93, 0.96),
            edgecolor=(0.15, 0.15, 0.2, 1.0),
        )
        self.ax.add_collection3d(self.link_poly)

        # Tick (dynamic)
        self.arm_r = self.hub_r * 1.1
        self.tick, = self.ax.plot(
            [0, self.hub_r], [0, 0], [self.z_link, self.z_link],
            lw=2.4, color=(0.15, 0.15, 0.2)
        )

        # Spring + damper (dynamic)
        self.spring_line, = self.ax.plot([], [], [], lw=2.2, color=(0.25, 0.25, 0.25))
        self.damper_line, = self.ax.plot([], [], [], lw=2.0, color=(0.20, 0.20, 0.25))

        self.gap_r = self.hub_r * 1.4
        self.sym = 0.018

        # HUD
        self.hud = self.ax.text2D(0.02, 0.95, "", transform=self.ax.transAxes, family="monospace")

        # Limits
        lim = 0.45
        self.ax.set_xlim(-lim, lim)
        self.ax.set_ylim(-lim, lim)
        self.ax.set_zlim(-0.06, 0.18)
        try:
            self.ax.set_box_aspect((1, 1, 0.55))
        except Exception:
            pass

        self.ani = None

    # ---------------------------
    # Playback controls
    # ---------------------------
    def pause(self):
        """Pause playback (freeze animation time)."""
        if not self.playing:
            return
        self.playing = False
        self._paused_sim_time = self._sim_time()

    def play(self):
        """Resume playback."""
        if self.playing:
            return
        self.playing = True
        if self._paused_sim_time is not None and self.t is not None:
            t0 = float(self.t[0])
            now = time.perf_counter()
            self._wall_t0 = now - (float(self._paused_sim_time) - t0) / max(self.speed, 1e-12)

    def restart(self):
        """Restart playback from the beginning."""
        self._wall_t0 = time.perf_counter()
        self.playing = True
        self._paused_sim_time = None

    def set_speed(self, speed: float):
        """Change playback speed while keeping current sim-time continuous if possible."""
        speed = float(speed)
        if speed <= 1e-12:
            speed = 1e-12

        if self.t is None:
            self.speed = speed
            self._wall_t0 = time.perf_counter()
            return

        # Keep current sim time continuous:
        ts = self._sim_time()
        self.speed = speed
        now = time.perf_counter()
        t0 = float(self.t[0])
        self._wall_t0 = now - (ts - t0) / self.speed

    # ---------------------------
    # Load new simulation
    # ---------------------------
    def set_sim(self, sim: Dict[str, Any]):
        self.sim = sim
        self.t = np.asarray(sim["t"], float)
        x = np.asarray(sim["x"], float)
        self.theta = x[:, 0]
        self.phi = x[:, 1]
        self.step_time = sim.get("ref_cfg", {}).get("step_time", None)

        self._wall_t0 = time.perf_counter()
        self.playing = True
        self._paused_sim_time = None

    # ---------------------------
    # Time mapping
    # ---------------------------
    def _sim_time(self) -> float:
        if self.t is None:
            return 0.0
        return float(self.t[0]) + self.speed * (time.perf_counter() - self._wall_t0)

    def _idx(self, ts: float) -> int:
        t0, tf = float(self.t[0]), float(self.t[-1])
        if ts <= t0:
            return 0
        if ts >= tf:
            return len(self.t) - 1
        j = int(np.searchsorted(self.t, ts))
        j = max(1, min(j, len(self.t) - 1))
        return j - 1 if abs(self.t[j - 1] - ts) <= abs(self.t[j] - ts) else j

    # ---------------------------
    # Animation update
    # ---------------------------
    def _update(self, _frame):
        # If paused, just keep drawing same frame
        if self.t is None:
            return self.tick, self.link_poly, self.spring_line, self.damper_line, self.hud

        if not self.playing:
            return self.tick, self.link_poly, self.spring_line, self.damper_line, self.hud

        t0, tf = float(self.t[0]), float(self.t[-1])
        ts = self._sim_time()

        if ts >= tf and self.loop:
            self._wall_t0 = time.perf_counter()
            ts = t0
        elif ts >= tf:
            ts = tf

        k = self._idx(ts)
        th = float(self.theta[k])
        ph = float(self.phi[k])

        # Tick
        self.tick.set_data([0, self.arm_r * np.cos(th)],
                           [0, self.arm_r * np.sin(th)])
        self.tick.set_3d_properties([self.z_link, self.z_link])

        # Link
        Rz = _rotz(ph)
        v = (Rz @ self.link_v0.T).T
        self.link_poly.set_verts(_faces(v))

        # Spring/damper anchors
        pm = np.array([self.arm_r * np.cos(th), self.arm_r * np.sin(th), self.z_link])
        pl = np.array([self.gap_r * np.cos(ph), self.gap_r * np.sin(ph), self.z_link])

        u = pl - pm
        u = u / (np.linalg.norm(u) + 1e-12)
        n = np.array([-u[1], u[0], 0.0])

        p0s = pm + self.sym * n
        p1s = pl + self.sym * n
        hel = _helix(p0s, p1s, turns=8, amp=0.006, n=120)
        self.spring_line.set_data(hel[:, 0], hel[:, 1])
        self.spring_line.set_3d_properties(hel[:, 2])

        p0d = pm - self.sym * n
        p1d = pl - self.sym * n
        self.damper_line.set_data([p0d[0], p1d[0]], [p0d[1], p1d[1]])
        self.damper_line.set_3d_properties([p0d[2], p1d[2]])

        alpha = th - ph
        if self.step_time is None:
            self.hud.set_text(
                f"t={self.t[k]:5.2f}   theta={th:+6.2f}   phi={ph:+6.2f}   alpha={alpha:+6.2f}"
            )
        else:
            self.hud.set_text(
                f"t={self.t[k]:5.2f} (step@{self.step_time:.2f}s)   "
                f"theta={th:+6.2f}   phi={ph:+6.2f}   alpha={alpha:+6.2f}"
            )

        return self.tick, self.link_poly, self.spring_line, self.damper_line, self.hud

    # ---------------------------
    # Start animation
    # ---------------------------
    def start(self):
        if self.ani is None:
            self.ani = FuncAnimation(
                self.fig,
                self._update,
                interval=33,
                blit=False,
                cache_frame_data=False,  # FIX warning
                save_count=300
            )
        return self.ani