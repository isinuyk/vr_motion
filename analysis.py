import math
from config import IMPACT_DIST_PX

def linear_speed(p0, p1, dt):
    if not p0 or not p1 or dt <= 0:
        return 0.0
    return math.hypot(p1[0]-p0[0], p1[1]-p0[1]) / dt

def angle(p0, p1):
    if not p0 or not p1:
        return None
    return math.atan2(p1[1]-p0[1], p1[0]-p0[0])

def angular_velocity(a0, a1, dt):
    if a0 is None or a1 is None or dt <= 0:
        return 0.0
    da = a1 - a0
    while da > math.pi:
        da -= 2*math.pi
    while da < -math.pi:
        da += 2*math.pi
    return da / dt

def detect_impact(speeds, accels, tip_ball_distances, threshold_px=IMPACT_DIST_PX):
    # Combine speed peak, acceleration peak, and ball distance
    impact_idx = speeds.index(max(speeds))
    for i, d in enumerate(tip_ball_distances):
        if d is not None and d < threshold_px:
            impact_idx = i
            break
    return impact_idx
