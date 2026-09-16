"""
noise_models.py
===============
Small reusable helpers for sensor/command imperfections.

We keep these as small pure functions so they are easy to test.

Included:
- quantize()         : encoder quantization
- gauss()            : Gaussian noise
- random_walk()      : drift / bias random walk
- dropout_hold()     : measurement dropout (hold last)
- DelayLine          : fixed integer delay in samples
- pwm_ripple()       : simple sinusoidal ripple model
- deadzone()         : driver deadband model (common in H-bridges)
"""

from __future__ import annotations
import numpy as np


def quantize(x: float, q: float) -> float:
    """x_hat = q * round(x/q). If q<=0 -> no quantization."""
    q = float(q)
    if q <= 0:
        return float(x)
    return float(q * np.round(float(x) / q))


def gauss(rng: np.random.Generator, sigma: float) -> float:
    """Gaussian noise N(0, sigma^2)."""
    sigma = float(sigma)
    if sigma <= 0:
        return 0.0
    return float(sigma * rng.standard_normal())


def random_walk(prev: float, rng: np.random.Generator, sigma_rw: float) -> float:
    """Random walk drift: b[k] = b[k-1] + sigma_rw*w[k]."""
    return float(prev + gauss(rng, sigma_rw))


def dropout_hold(x: float, hold_last: float, rng: np.random.Generator, p_drop: float) -> float:
    """
    With probability p_drop, we output the last value (hold_last).
    This mimics missed sensor samples / serial packet loss.
    """
    p_drop = float(p_drop)
    if p_drop <= 0:
        return float(x)
    if rng.random() < p_drop:
        return float(hold_last)
    return float(x)


class DelayLine:
    """Fixed integer delay line for commands (in controller ticks)."""
    def __init__(self, steps: int, init_value: float = 0.0):
        self.steps = max(0, int(steps))
        self.buf = [float(init_value)] * (self.steps + 1)

    def reset(self, value: float = 0.0):
        self.buf = [float(value)] * (self.steps + 1)

    def push(self, x: float) -> float:
        """Push new x, return the delayed output y."""
        self.buf.append(float(x))
        y = self.buf.pop(0)
        return float(y)


def pwm_ripple(t: float, amp: float, freq_hz: float) -> float:
    """Simple sinusoidal PWM ripple approximation."""
    amp = float(amp)
    if amp == 0:
        return 0.0
    return float(amp * np.sin(2.0*np.pi*float(freq_hz)*float(t)))


def deadzone(u: float, dz: float) -> float:
    """
    Deadzone nonlinearity:
      if |u| <= dz -> 0
      else         -> sign(u)*(|u|-dz)

    This mimics driver/H-bridge deadband.
    """
    u = float(u)
    dz = float(dz)
    if dz <= 0:
        return u
    if abs(u) <= dz:
        return 0.0
    return np.sign(u) * (abs(u) - dz)