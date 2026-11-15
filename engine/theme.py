"""Colors and sizes: change the look in one place. (Texts live in textos.py.)"""

BG = (0, 0, 0)
GRID_BG = (34, 40, 56)
GRID = (40, 110, 160)
GRID_MAJOR = (70, 150, 200)
AXIS = (200, 205, 220)
TEXT = (230, 232, 240)
TEXT_DIM = (130, 136, 155)

I_HAT = (120, 220, 110)      # green
J_HAT = (240, 90, 90)        # red
VEC = (250, 210, 60)         # yellow
VEC2 = (110, 190, 250)       # blue
RESULT = (220, 130, 250)     # purple
GHOST = (200, 200, 220)
AREA = (250, 210, 60)

OK = (110, 230, 140)
BAD = (240, 80, 80)
PANEL = (24, 28, 42)
PANEL_HI = (44, 52, 76)

HANDLE_RADIUS_PX = 22        # touch-friendly hit area
VECTOR_WIDTH_PX = 4
WORLD_RADIUS = 5             # grid units visible from origin to the nearest screen edge


def escurecer(cor, k: float) -> tuple:
    """The colour `cor` with its brightness multiplied by `k` (0 = black, 1 = unchanged)."""
    return tuple(int(v * k) for v in cor[:3])


def piscar(cor, alpha: float, minimo: float = 0.35) -> tuple:
    """For blinking hints: `alpha` 0..1 goes from `minimo` brightness to the full colour."""
    return escurecer(cor, minimo + (1 - minimo) * alpha)
