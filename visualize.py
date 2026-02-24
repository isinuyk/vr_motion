import pandas as pd
import matplotlib.pyplot as plt

# Load CSV exported by main.py
df = pd.read_csv("swing_analysis.csv")

plt.figure(figsize=(12, 8))

# ------------------------------
# Subplot 1: stick speed & angular velocity
# ------------------------------
plt.subplot(2,1,1)
plt.plot(df["time_norm"], df["stick_speed"], label="Stick speed (m/s)", color='blue')
plt.plot(df["time_norm"], df["angular_velocity"], label="Angular velocity (rad/s)", color='orange')
plt.xlabel("Normalized swing time")
plt.ylabel("Value")
plt.title("Stick speed & angular velocity")
plt.legend()
plt.grid(True)

# ------------------------------
# Subplot 2: stick tip trajectory
# ------------------------------
plt.subplot(2,1,2)
# Raw trajectory (red)
if "tip_x_m_raw" in df.columns:
    plt.plot(df["tip_x_m_raw"], df["tip_y_m_raw"], label="Raw stick tip", color='red', alpha=0.6)
else:
    # If raw meters not in CSV, approximate by using filtered for both for demonstration
    plt.plot(df["tip_x_m"], df["tip_y_m"], label="Raw stick tip (approx)", color='red', alpha=0.6)

# Filtered trajectory (green)
plt.plot(df["tip_x_m"], df["tip_y_m"], label="Kalman filtered stick tip", color='green')

plt.xlabel("X position (m)")
plt.ylabel("Y position (m)")
plt.title("Stick tip trajectory: raw vs filtered")
plt.gca().invert_yaxis()  # match image coordinates
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
