import math
import cv2

from analysis import linear_speed, angle, angular_velocity, detect_impact
from drawing import draw_skeleton, draw_stick, draw_ball
from utils_filter import MedianFilter2D, is_physical
from config import STICK_REAL_LENGTH_M, MAX_VEL_PX, MAX_ACC_PX, MEDIAN_WIN
from kalman import Kalman2D


class SwingAnalyzer:
    def __init__(self, data, fps, screen_size):
        self.data = data
        self.dt = 1.0 / fps
        self.screen_w, self.screen_h = screen_size

        # =========================
        # Buffers
        # =========================
        self.times = []
        self.speeds = []
        self.ang_vels = []
        self.accels = []
        self.ang_accels = []
        self.energies = []
        self.jerks = []
        self.tip_ball_distances = []

        self.tip_positions_raw = []   # raw tip positions (px)
        self.tip_positions = []       # filtered tip positions (px)
        self.tip_positions_m = []     # filtered tip positions (m)

        # =========================
        # Previous frame state
        # =========================
        self.prev_tip = None
        self.prev_speed = 0.0
        self.prev_ang = 0.0
        self.prev_ang_vel = 0.0
        self.prev_acc = 0.0
        self.prev_v_px = None

        # =========================
        # Filters
        # =========================
        self.kalman = Kalman2D(q_pos=0.2, q_vel=0.05, r_meas=1)
        self.median = MedianFilter2D(win=MEDIAN_WIN)

        # =========================
        # Impact
        # =========================
        self.impact_idx = None

        # =========================
        # Pixel-to-meter calibration
        # =========================
        self.scale_m = None

    # =========================
    # Calibration
    # =========================
    def calibrate(self, base, tip):
        dx = tip[0] - base[0]
        dy = tip[1] - base[1]
        dist_px = math.hypot(dx, dy)

        if dist_px > 0:
            self.scale_m = STICK_REAL_LENGTH_M / dist_px
        else:
            self.scale_m = 1.0

    # =========================
    # Frame processing
    # =========================
    def process_frame(self, idx, frame_img, frame):
        pts = frame["landmarks"][0]

        # Draw skeleton + stick + ball
        draw_skeleton(frame_img, pts, frame_img.shape[1], frame_img.shape[0])
        base, tip = draw_stick(frame_img, pts, frame_img.shape[1], frame_img.shape[0])
        ball = draw_ball(frame_img, frame, frame_img.shape[1], frame_img.shape[0])

        # First frame → calibration
        if self.scale_m is None and base and tip:
            self.calibrate(base, tip)

        # =========================
        # RAW TIP
        # =========================
        self.tip_positions_raw.append(tip)

        # =========================
        # Outlier rejection (physics gating)
        # =========================
        if tip and self.prev_tip:
            valid = is_physical(
                self.prev_tip,
                tip,
                self.dt,
                self.prev_v_px,
                MAX_VEL_PX,
                MAX_ACC_PX
            )
        else:
            valid = True

        meas = tip if valid else None

        # =========================
        # Median filter
        # =========================
        med = self.median.update(meas)

        # =========================
        # Kalman filter
        # =========================
        if med:
            x = self.kalman.update(med, self.dt)
        elif tip:
            # fallback init if median not ready but raw exists
            x = self.kalman.update(tip, self.dt)
        else:
            # no measurement
            x = self.kalman.predict(self.dt)

        # Always extract (x,y)
        tip_filtered = (float(x[0, 0]), float(x[1, 0]))

        self.tip_positions.append(tip_filtered)

        # =========================
        # Metric conversion
        # =========================
        if tip_filtered and self.scale_m:
            self.tip_positions_m.append(
                (tip_filtered[0] * self.scale_m, tip_filtered[1] * self.scale_m)
            )
        else:
            self.tip_positions_m.append((0.0, 0.0))

        # =========================
        # Time
        # =========================
        t = idx * self.dt
        self.times.append(t)

        # =========================
        # Linear speed (m/s)
        # =========================
        v = linear_speed(self.prev_tip, tip_filtered, self.dt) * (self.scale_m or 1)
        self.speeds.append(v)

        # =========================
        # Acceleration
        # =========================
        acc = (v - self.prev_speed) / self.dt
        self.accels.append(acc)

        # =========================
        # Angle & angular velocity
        # =========================
        ang = angle(base, tip_filtered)
        w = angular_velocity(self.prev_ang, ang, self.dt)
        self.ang_vels.append(w)
        self.ang_accels.append((w - self.prev_ang_vel) / self.dt)

        # =========================
        # Energy / jerk
        # =========================
        self.energies.append(v * v)
        self.jerks.append((acc - self.prev_acc) / self.dt)

        # =========================
        # Distance to ball
        # =========================
        if tip_filtered and ball:
            dist = math.hypot(tip_filtered[0] - ball[0], tip_filtered[1] - ball[1])
        else:
            dist = None

        self.tip_ball_distances.append(dist)

        # =========================
        # Impact detection
        # =========================
        if self.impact_idx is None and dist is not None and dist < 20:
            self.impact_idx = idx

        # =========================
        # Update previous state
        # =========================
        if self.prev_tip and tip_filtered:
            self.prev_v_px = math.hypot(
                tip_filtered[0] - self.prev_tip[0],
                tip_filtered[1] - self.prev_tip[1]
            ) / self.dt

        self.prev_tip = tip_filtered
        self.prev_speed = v
        self.prev_ang = ang
        self.prev_ang_vel = w
        self.prev_acc = acc

    # =========================
    # Trajectory drawing
    # =========================
    def draw_trajectory(self, frame_img):
        # Raw trajectory (red)
        raw_points = [p for p in self.tip_positions_raw if p is not None]
        for i in range(1, len(raw_points)):
            cv2.line(
                frame_img,
                (int(raw_points[i-1][0]), int(raw_points[i-1][1])),
                (int(raw_points[i][0]), int(raw_points[i][1])),
                (0, 0, 255),
                1
            )

        # Filtered trajectory (green)
        filt_points = [p for p in self.tip_positions if p is not None]
        for i in range(1, len(filt_points)):
            cv2.line(
                frame_img,
                (int(filt_points[i-1][0]), int(filt_points[i-1][1])),
                (int(filt_points[i][0]), int(filt_points[i][1])),
                (0, 255, 0),
                2
            )

    # =========================
    # Finalization / CSV rows
    # =========================
    def finalize(self):
        if self.impact_idx is None:
            self.impact_idx = detect_impact(
                self.speeds,
                self.accels,
                self.tip_ball_distances
            )

        t0 = self.times[0]
        t1 = self.times[self.impact_idx]

        # safety: avoid division by zero
        if abs(t1 - t0) < 1e-9:
            t1 = t0 + self.dt
        rows = []

        for i in range(self.impact_idx + 1):
            tn = (self.times[i] - t0) / (t1 - t0) if (t1 - t0) != 0 else 0.0

            tip_filtered_m = self.tip_positions_m[i]

            tip_raw_px = self.tip_positions_raw[i]
            if tip_raw_px and self.scale_m:
                tip_raw_m = (
                    tip_raw_px[0] * self.scale_m,
                    tip_raw_px[1] * self.scale_m
                )
            else:
                tip_raw_m = (0.0, 0.0)

            rows.append([
                self.times[i],
                self.speeds[i],
                self.ang_vels[i],
                self.accels[i],
                self.ang_accels[i],
                self.energies[i],
                self.jerks[i],
                tn,
                tip_filtered_m[0],
                tip_filtered_m[1],
                tip_raw_m[0],
                tip_raw_m[1]
            ])

        return rows
