# kalman.py

import numpy as np


class Kalman2D:
    """
    Constant-velocity Kalman filter for 2-D position tracking.
    State: [x, y, vx, vy]

    q_pos / q_vel  – process noise per step.  Larger → follows measurements
                     more closely (less smoothing, less lag on curves).
    r_meas         – measurement noise.  Larger → more smoothing.
    """
    def __init__(self, q_pos=8.0, q_vel=8.0, r_meas=6.0):
        self.x = np.zeros((4, 1))
        self.P = np.eye(4) * 500.0

        self.Q_diag = np.diag([q_pos, q_pos, q_vel, q_vel])
        self.r = r_meas

        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=float)

        self.initialized = False

    @property
    def base_r(self):
        return float(self.r)

    def _F(self, dt):
        return np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1,  0],
            [0, 0, 0,  1]
        ])

    def transition(self, dt):
        return self._F(dt)

    def predict(self, dt):
        F = self._F(dt)
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + self.Q_diag
        return self.x

    def predict_measurement(self, dt, r_meas=None):
        """Return one-step predicted measurement mean/covariance without mutating state."""
        F = self._F(dt)
        x_pred = F @ self.x
        P_pred = F @ self.P @ F.T + self.Q_diag
        r = self.r if r_meas is None else float(r_meas)
        R = np.eye(2) * r
        z_pred = self.H @ x_pred
        S = self.H @ P_pred @ self.H.T + R
        return z_pred, S

    def update(self, z, dt, r_meas=None):
        z = np.array(z, dtype=float).reshape(2, 1)

        if not self.initialized:
            self.x[0, 0] = z[0, 0]
            self.x[1, 0] = z[1, 0]
            self.initialized = True
            return self.x

        self.predict(dt)

        r = self.r if r_meas is None else float(r_meas)
        R = np.eye(2) * r
        y = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + R
        # solve S^T K^T = (P H^T)^T  — avoids explicit matrix inversion
        K = np.linalg.solve(S.T, (self.P @ self.H.T).T).T

        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P

        return self.x
