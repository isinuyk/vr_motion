# kalman.py

import numpy as np

class Kalman2D:
    # State: [x, y, vx, vy]
    def __init__(self, q_pos=0.05, q_vel=0.5, r_meas=15.0):
        self.x = np.zeros((4, 1))        # state vector
        self.P = np.eye(4) * 500.0       # covariance

        self.q_pos = q_pos
        self.q_vel = q_vel
        self.r = r_meas

        self.initialized = False

    def F(self, dt):
        return np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1,  0],
            [0, 0, 0,  1]
        ])

    def Q(self):
        return np.diag([
            self.q_pos, self.q_pos,
            self.q_vel, self.q_vel
        ])

    def H(self):
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])

    # -------------------------
    # Predict step
    # -------------------------
    def predict(self, dt):
        F = self.F(dt)
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + self.Q()
        return self.x

    # -------------------------
    # Update step
    # -------------------------
    def update(self, z, dt):
        z = np.array(z, dtype=float).reshape(2, 1)

        # Init on first measurement
        if not self.initialized:
            self.x[0, 0] = z[0, 0]
            self.x[1, 0] = z[1, 0]
            self.x[2, 0] = 0.0
            self.x[3, 0] = 0.0
            self.initialized = True
            return self.x

        # Predict
        self.predict(dt)

        # Update
        H = self.H()
        R = np.eye(2) * self.r

        y = z - H @ self.x
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)

        self.x = self.x + K @ y
        I = np.eye(4)
        self.P = (I - K @ H) @ self.P

        return self.x
