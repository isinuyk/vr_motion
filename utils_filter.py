import math
from collections import deque
import numpy as np

class MedianFilter2D:
    def __init__(self, win=5):
        self.win = win
        self.buf_x = deque(maxlen=win)
        self.buf_y = deque(maxlen=win)

    def update(self, p):
        if p is None:
            return None
        self.buf_x.append(p[0])
        self.buf_y.append(p[1])
        if len(self.buf_x) < self.win:
            return p
        return (float(np.median(self.buf_x)), float(np.median(self.buf_y)))


def is_physical(prev_p, p, dt, prev_v, max_v, max_a):
    # Type safety
    if prev_p is None or p is None:
        return True

    # Ensure tuples
    if not isinstance(prev_p, (tuple, list)) or not isinstance(p, (tuple, list)):
        return True

    if len(prev_p) < 2 or len(p) < 2:
        return True

    dx = p[0] - prev_p[0]
    dy = p[1] - prev_p[1]

    v = math.hypot(dx, dy) / dt

    # Velocity gate
    if v > max_v:
        return False

    # Acceleration gate
    if prev_v is not None:
        a = abs(v - prev_v) / dt
        if a > max_a:
            return False

    return True
