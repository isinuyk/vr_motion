import math
import cv2

from analysis import (
    linear_speed, angle, angular_velocity, detect_impact,
    segment_angle, joint_angle_3pt, midpoint, RunningMedian,
)
from drawing import draw_skeleton, draw_stick, draw_ball
from utils_filter import MedianFilter2D
from config import STICK_REAL_LENGTH_M, MEDIAN_WIN, STICK_CAL_WIN
from kalman import Kalman2D


class SwingAnalyzer:
    def __init__(self, data, fps, screen_size):
        self.data = data
        self.dt = 1.0 / fps if fps and fps > 0 else 1.0 / 30.0
        self.screen_w, self.screen_h = screen_size

        # ---- time / core kinematics ----
        self.times = []
        self.speeds = []
        self.ang_vels = []
        self.accels = []
        self.ang_accels = []
        self.energies = []
        self.jerks = []
        self.tip_ball_distances = []

        # ---- trajectory buffers ----
        self.tip_positions_raw = []
        self.tip_positions = []
        self.tip_positions_m = []

        # ---- biomechanics buffers ----
        self.hip_angles = []
        self.shoulder_angles = []
        self.x_factors = []
        self.wrist_angles = []
        self.arc_radii = []
        self.stick_lengths_px = []

        # ---- previous-frame state ----
        self.prev_tip = None
        self.prev_speed = 0.0
        self.prev_ang = 0.0
        self.prev_ang_vel = 0.0
        self.prev_acc = 0.0

        # ---- filters ----
        self.kalman = Kalman2D(q_pos=8.0, q_vel=8.0, r_meas=6.0)
        self.median = MedianFilter2D(win=MEDIAN_WIN)

        # ---- dynamic calibration ----
        self.stick_len_median = RunningMedian(win=STICK_CAL_WIN)
        self.scale_m = None

        # ---- impact ----
        self.impact_idx = None

    # ------------------------------------------------------------------ #
    #  Calibration (updated every frame with running median)
    # ------------------------------------------------------------------ #
    def _update_calibration(self, stick_len_px):
        med = self.stick_len_median.update(stick_len_px)
        if med and med > 0:
            self.scale_m = STICK_REAL_LENGTH_M / med

    # ------------------------------------------------------------------ #
    #  Landmark helper
    # ------------------------------------------------------------------ #
    @staticmethod
    def _lm_px(pts, i, w, h):
        if i >= len(pts):
            return None
        p = pts[i]
        x = p.get("x")
        y = p.get("y")
        if x is None or y is None:
            return None
        return (float(x) * w, float(y) * h)

    # ------------------------------------------------------------------ #
    #  Process one frame
    # ------------------------------------------------------------------ #
    def process_frame(self, idx, frame_img, frame, dt=None, t=None):
        dt = self.dt if dt is None else max(float(dt), 1e-6)
        pts = frame["landmarks"][0]
        w, h = frame_img.shape[1], frame_img.shape[0]
        lm = lambda i: self._lm_px(pts, i, w, h)

        # ---- draw visuals ----
        draw_skeleton(frame_img, pts, w, h)
        draw_stick(frame_img, pts, w, h)
        ball = draw_ball(frame_img, frame, w, h)

        # ---- key landmarks (float, subpixel) ----
        base = lm(17)
        tip = lm(19)
        l_shoulder = lm(5)
        r_shoulder = lm(6)
        l_hip = lm(11)
        r_hip = lm(12)
        l_elbow = lm(7)
        r_elbow = lm(8)
        l_wrist = lm(9)
        r_wrist = lm(10)

        # ---- dynamic stick-length calibration ----
        if base and tip:
            slen = math.hypot(tip[0] - base[0], tip[1] - base[1])
            self.stick_lengths_px.append(slen)
            self._update_calibration(slen)
        else:
            self.stick_lengths_px.append(None)

        # ---- raw tip ----
        self.tip_positions_raw.append(tip)

        # ---- median → Kalman ----
        med = self.median.update(tip)
        if med:
            x = self.kalman.update(med, dt)
        elif tip:
            x = self.kalman.update(tip, dt)
        else:
            x = self.kalman.predict(dt)

        tip_f = (float(x[0, 0]), float(x[1, 0]))
        self.tip_positions.append(tip_f)

        # ---- metric conversion ----
        if tip_f and self.scale_m:
            self.tip_positions_m.append(
                (tip_f[0] * self.scale_m, tip_f[1] * self.scale_m)
            )
        else:
            self.tip_positions_m.append((0.0, 0.0))

        # ---- time ----
        if t is None:
            t = (self.times[-1] + dt) if self.times else 0.0
        self.times.append(float(t))

        # ---- linear speed (m/s) ----
        v = linear_speed(self.prev_tip, tip_f, dt) * (self.scale_m or 1)
        self.speeds.append(v)

        # ---- acceleration ----
        acc = (v - self.prev_speed) / dt
        self.accels.append(acc)

        # ---- angle / angular velocity ----
        ang = angle(base, tip_f)
        w_ang = angular_velocity(self.prev_ang, ang, dt)
        self.ang_vels.append(w_ang)
        self.ang_accels.append(
            (w_ang - self.prev_ang_vel) / dt if dt > 0 else 0.0
        )

        # ---- energy proxy & jerk ----
        self.energies.append(v * v)
        self.jerks.append((acc - self.prev_acc) / dt if dt > 0 else 0.0)

        # ---- hip angle (degrees from horizontal) ----
        hip_a = segment_angle(l_hip, r_hip)
        self.hip_angles.append(math.degrees(hip_a) if hip_a is not None else None)

        # ---- shoulder angle ----
        sh_a = segment_angle(l_shoulder, r_shoulder)
        self.shoulder_angles.append(math.degrees(sh_a) if sh_a is not None else None)

        # ---- X-factor (shoulder – hip rotation) ----
        if hip_a is not None and sh_a is not None:
            xf = math.degrees(sh_a) - math.degrees(hip_a)
            while xf > 180:
                xf -= 360
            while xf < -180:
                xf += 360
            self.x_factors.append(xf)
        else:
            self.x_factors.append(None)

        # ---- wrist angle (use the lead wrist, assumed right-handed → right side) ----
        wa = joint_angle_3pt(r_elbow, r_wrist, base)
        self.wrist_angles.append(wa)

        # ---- arc radius (shoulder-mid → tip) ----
        sh_mid = midpoint(l_shoulder, r_shoulder)
        if sh_mid and tip_f:
            self.arc_radii.append(math.hypot(tip_f[0] - sh_mid[0], tip_f[1] - sh_mid[1]))
        else:
            self.arc_radii.append(None)

        # ---- ball distance / impact ----
        if tip_f and ball:
            dist = math.hypot(tip_f[0] - ball[0], tip_f[1] - ball[1])
        else:
            dist = None
        self.tip_ball_distances.append(dist)

        if self.impact_idx is None and dist is not None and dist < 20:
            self.impact_idx = idx

        # ---- save previous state ----
        self.prev_tip = tip_f
        self.prev_speed = v
        self.prev_ang = ang
        self.prev_ang_vel = w_ang
        self.prev_acc = acc

    # ------------------------------------------------------------------ #
    #  Draw trajectories
    # ------------------------------------------------------------------ #
    def draw_trajectory(self, frame_img):
        raw = [p for p in self.tip_positions_raw if p is not None]
        for i in range(1, len(raw)):
            cv2.line(
                frame_img,
                (int(raw[i - 1][0]), int(raw[i - 1][1])),
                (int(raw[i][0]), int(raw[i][1])),
                (0, 0, 255), 1,
            )

        filt = [p for p in self.tip_positions if p is not None]
        for i in range(1, len(filt)):
            cv2.line(
                frame_img,
                (int(filt[i - 1][0]), int(filt[i - 1][1])),
                (int(filt[i][0]), int(filt[i][1])),
                (0, 255, 0), 2,
            )

    # ------------------------------------------------------------------ #
    #  Summary metrics (computed once after all frames)
    # ------------------------------------------------------------------ #
    def summary(self):
        """Return a dict of scalar summary metrics for the swing."""
        n = len(self.times)
        if n < 2:
            return {}

        peak_speed_idx = self.speeds.index(max(self.speeds)) if self.speeds else 0

        # Backswing = frames 0 → peak_speed; downswing = peak_speed → impact
        impact = self.impact_idx if self.impact_idx else n - 1
        t_back = self.times[peak_speed_idx] - self.times[0] if peak_speed_idx > 0 else 0
        t_down = self.times[impact] - self.times[peak_speed_idx] if impact > peak_speed_idx else 0
        tempo = t_back / t_down if t_down > 0 else 0.0

        valid_jerks = [abs(j) for j in self.jerks if j != 0]
        smoothness = 0.0
        if valid_jerks:
            mean_sq_jerk = sum(j * j for j in valid_jerks) / len(valid_jerks)
            smoothness = -math.log10(mean_sq_jerk + 1e-9)

        valid_xf = [x for x in self.x_factors if x is not None]
        max_xf = max(valid_xf, key=abs) if valid_xf else 0.0

        return {
            "max_speed": max(self.speeds) if self.speeds else 0,
            "max_ang_vel": max(self.ang_vels) if self.ang_vels else 0,
            "max_accel": max(self.accels) if self.accels else 0,
            "swing_duration": self.times[-1] - self.times[0],
            "swing_tempo": tempo,
            "smoothness_index": smoothness,
            "max_x_factor": max_xf,
        }

    # ------------------------------------------------------------------ #
    #  Finalize & export rows
    # ------------------------------------------------------------------ #
    def finalize(self):
        if self.impact_idx is None:
            self.impact_idx = detect_impact(
                self.speeds, self.accels, self.tip_ball_distances,
            )

        t0 = self.times[0]
        t1 = self.times[self.impact_idx]
        if abs(t1 - t0) < 1e-9:
            t1 = t0 + self.dt

        rows = []
        for i in range(self.impact_idx + 1):
            tn = (self.times[i] - t0) / (t1 - t0) if (t1 - t0) != 0 else 0.0

            tip_fm = self.tip_positions_m[i]
            tip_raw_px = self.tip_positions_raw[i]
            if tip_raw_px and self.scale_m:
                tip_raw_m = (tip_raw_px[0] * self.scale_m, tip_raw_px[1] * self.scale_m)
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
                tip_fm[0],
                tip_fm[1],
                tip_raw_m[0],
                tip_raw_m[1],
                self.hip_angles[i] if self.hip_angles[i] is not None else "",
                self.shoulder_angles[i] if self.shoulder_angles[i] is not None else "",
                self.x_factors[i] if self.x_factors[i] is not None else "",
                self.wrist_angles[i] if self.wrist_angles[i] is not None else "",
                self.arc_radii[i] if self.arc_radii[i] is not None else "",
            ])

        return rows
