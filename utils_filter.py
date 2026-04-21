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


def _smooth_series_poly(values, window, degree):
    """Centered local polynomial smoothing (Savitzky-Golay style)."""
    n = len(values)
    if n == 0:
        return []
    if window < 3 or n < 3:
        return [float(v) for v in values]
    if window % 2 == 0:
        window += 1

    half = window // 2
    t = np.arange(n, dtype=float)
    out = []

    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        local_t = t[lo:hi] - t[i]
        local_y = np.asarray(values[lo:hi], dtype=float)
        if len(local_y) < 3:
            out.append(float(values[i]))
            continue
        local_deg = min(int(degree), len(local_y) - 1)
        coeffs = np.polyfit(local_t, local_y, local_deg)
        out.append(float(np.polyval(coeffs, 0.0)))
    return out


def _dist_point_to_segment(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx = bx - ax
    dy = by - ay
    denom = dx * dx + dy * dy
    if denom <= 1e-12:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / denom
    t = max(0.0, min(1.0, t))
    qx = ax + t * dx
    qy = ay + t * dy
    return math.hypot(px - qx, py - qy)


def despike_trajectory(points, thresh_px=16.0, max_neighbor_px=30.0, passes=1):
    """
    Remove one-frame trajectory spikes by replacing outlier point with midpoint
    of neighboring points when local geometry indicates a narrow unrealistic cusp.
    """
    if not points:
        return []
    out = [None if p is None else (float(p[0]), float(p[1])) for p in points]
    p_count = max(1, int(passes))
    t = float(thresh_px)
    nmax = float(max_neighbor_px)

    for _ in range(p_count):
        cur = out.copy()
        for i in range(1, len(out) - 1):
            p_prev = out[i - 1]
            p_cur = out[i]
            p_next = out[i + 1]
            if p_prev is None or p_cur is None or p_next is None:
                continue

            neigh_len = math.hypot(p_next[0] - p_prev[0], p_next[1] - p_prev[1])
            if neigh_len <= 1e-9 or neigh_len > nmax:
                continue

            spike_dist = _dist_point_to_segment(p_cur, p_prev, p_next)
            if spike_dist <= t:
                continue

            # Replace by local interpolation between neighbors.
            cur[i] = (
                0.5 * (p_prev[0] + p_next[0]),
                0.5 * (p_prev[1] + p_next[1]),
            )
        out = cur
    return out


def smooth_trajectory_poly(
    points,
    window=9,
    degree=3,
    raw_ref=None,
    raw_blend=0.0,
    max_dev_px=None,
    laplace_passes=0,
    laplace_alpha=0.5,
    closed_dist_px=None,
    closed_min_cos=0.0,
    post_despike_thresh_px=None,
    post_despike_max_neighbor_px=None,
    post_despike_passes=0,
):
    """
    Smooth (x, y) trajectory per contiguous valid segment with centered
    local polynomial interpolation and optional blending toward raw points.
    """
    if not points:
        return []

    out = [None] * len(points)
    i = 0
    while i < len(points):
        if points[i] is None:
            i += 1
            continue
        j = i
        while j < len(points) and points[j] is not None:
            j += 1

        seg = points[i:j]
        if len(seg) < 3:
            for k, p in enumerate(seg):
                out[i + k] = (float(p[0]), float(p[1]))
            i = j
            continue

        xs = [p[0] for p in seg]
        ys = [p[1] for p in seg]
        xs_s = _smooth_series_poly(xs, window=window, degree=degree)
        ys_s = _smooth_series_poly(ys, window=window, degree=degree)

        for k in range(len(seg)):
            x_s = xs_s[k]
            y_s = ys_s[k]
            idx = i + k
            if (
                raw_ref is not None
                and 0.0 < raw_blend <= 1.0
                and idx < len(raw_ref)
                and raw_ref[idx] is not None
            ):
                rx, ry = raw_ref[idx]
                x_s = (1.0 - raw_blend) * x_s + raw_blend * float(rx)
                y_s = (1.0 - raw_blend) * y_s + raw_blend * float(ry)

            if (
                raw_ref is not None
                and max_dev_px is not None
                and max_dev_px > 0
                and idx < len(raw_ref)
                and raw_ref[idx] is not None
            ):
                rx, ry = raw_ref[idx]
                dx = x_s - float(rx)
                dy = y_s - float(ry)
                dist = math.hypot(dx, dy)
                if dist > max_dev_px and dist > 1e-9:
                    s = max_dev_px / dist
                    x_s = float(rx) + dx * s
                    y_s = float(ry) + dy * s
            out[idx] = (float(x_s), float(y_s))

        if laplace_passes > 0 and len(seg) >= 3:
            start = i
            end = j
            a = min(max(float(laplace_alpha), 0.0), 1.0)
            is_closed = False
            if closed_dist_px is not None and len(seg) >= 8:
                p0 = seg[0]
                p1 = seg[-1]
                if p0 is not None and p1 is not None:
                    end_dist_ok = math.hypot(
                        p1[0] - p0[0], p1[1] - p0[1]
                    ) <= float(closed_dist_px)
                    tangent_ok = True
                    if len(seg) >= 4:
                        s0 = seg[0]
                        s1 = seg[1]
                        e0 = seg[-2]
                        e1 = seg[-1]
                        v0 = (s1[0] - s0[0], s1[1] - s0[1])
                        v1 = (e1[0] - e0[0], e1[1] - e0[1])
                        n0 = math.hypot(v0[0], v0[1])
                        n1 = math.hypot(v1[0], v1[1])
                        if n0 > 1e-9 and n1 > 1e-9:
                            cosang = (v0[0] * v1[0] + v0[1] * v1[1]) / (n0 * n1)
                            tangent_ok = cosang >= float(closed_min_cos)
                    is_closed = end_dist_ok and tangent_ok

            for _ in range(int(laplace_passes)):
                prev_vals = out[start:end]
                if is_closed:
                    idx_range = range(start, end)
                else:
                    idx_range = range(start + 1, end - 1)

                seg_len = end - start
                for u in idx_range:
                    loc = u - start
                    if is_closed:
                        l_loc = (loc - 1) % seg_len
                        r_loc = (loc + 1) % seg_len
                    else:
                        l_loc = loc - 1
                        r_loc = loc + 1

                    if prev_vals[l_loc] is None or prev_vals[loc] is None or prev_vals[r_loc] is None:
                        continue
                    px, py = prev_vals[l_loc]
                    cx, cy = prev_vals[loc]
                    nx, ny = prev_vals[r_loc]
                    x_s = (1.0 - a) * cx + a * 0.5 * (px + nx)
                    y_s = (1.0 - a) * cy + a * 0.5 * (py + ny)

                    if (
                        raw_ref is not None
                        and max_dev_px is not None
                        and max_dev_px > 0
                        and u < len(raw_ref)
                        and raw_ref[u] is not None
                    ):
                        rx, ry = raw_ref[u]
                        dx = x_s - float(rx)
                        dy = y_s - float(ry)
                        dist = math.hypot(dx, dy)
                        if dist > max_dev_px and dist > 1e-9:
                            s = max_dev_px / dist
                            x_s = float(rx) + dx * s
                            y_s = float(ry) + dy * s
                    out[u] = (float(x_s), float(y_s))
        i = j

    if post_despike_passes and post_despike_passes > 0:
        out = despike_trajectory(
            out,
            thresh_px=post_despike_thresh_px if post_despike_thresh_px is not None else 0.0,
            max_neighbor_px=(
                post_despike_max_neighbor_px
                if post_despike_max_neighbor_px is not None
                else 1e9
            ),
            passes=int(post_despike_passes),
        )

    return out


def is_physical(prev_p, p, dt, prev_v, max_v, max_a):
    # Type safety
    if prev_p is None or p is None:
        return True

    # Ensure tuples
    if not isinstance(prev_p, (tuple, list)) or not isinstance(p, (tuple, list)):
        return True

    if len(prev_p) < 2 or len(p) < 2:
        return True

    if dt is None or dt <= 1e-9:
        return True

    dx = p[0] - prev_p[0]
    dy = p[1] - prev_p[1]

    # Work in px/s for frame-rate-independent gating.
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
