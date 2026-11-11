"""Small animation helpers driven by dt (seconds)."""
from __future__ import annotations

import math


def smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class Tween:
    """Goes 0 -> 1 over `duration` seconds with smoothstep easing."""

    def __init__(self, duration: float = 1.0, delay: float = 0.0):
        self.duration = max(1e-6, duration)
        self.time = -delay

    def update(self, dt: float) -> None:
        self.time += dt

    @property
    def raw(self) -> float:
        return max(0.0, min(1.0, self.time / self.duration))

    @property
    def value(self) -> float:
        return smooth(self.raw)

    @property
    def done(self) -> bool:
        return self.time >= self.duration


class Effect:
    """Short one-shot effect (shake / pulse / flash). `strength` fades 1 -> 0."""

    def __init__(self, duration: float):
        self.duration = duration
        self.time = duration  # inactive

    def start(self) -> None:
        self.time = 0.0

    def update(self, dt: float) -> None:
        self.time = min(self.duration, self.time + dt)

    @property
    def active(self) -> bool:
        return self.time < self.duration

    @property
    def strength(self) -> float:
        return 1.0 - self.time / self.duration if self.active else 0.0


class Shake(Effect):
    def __init__(self, duration: float = 0.4, amplitude: float = 10):
        super().__init__(duration)
        self.amplitude = amplitude

    @property
    def offset(self) -> float:
        return math.sin(self.time * 60) * self.amplitude * self.strength


class Pulse(Effect):
    def __init__(self, duration: float = 0.8):
        super().__init__(duration)

    @property
    def scale(self) -> float:
        """1 -> grows -> back to 1."""
        return 1.0 + 0.6 * math.sin(math.pi * (1 - self.strength)) if self.active else 1.0


class Blink:
    """Endless gentle blink, used for hints."""

    def __init__(self, speed: float = 3.0):
        self.speed = speed
        self.time = 0.0

    def update(self, dt: float) -> None:
        self.time += dt

    @property
    def alpha(self) -> float:
        return 0.5 + 0.5 * math.sin(self.time * self.speed)
