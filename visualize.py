import argparse

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot(csv_path):
    df = pd.read_csv(csv_path)

    fig, axes = plt.subplots(3, 2, figsize=(14, 12))

    # ---- 1. Speed & angular velocity ----
    ax = axes[0, 0]
    ax.plot(df["time_norm"], df["stick_speed"], label="Stick speed (m/s)", color="blue")
    ax.plot(df["time_norm"], df["angular_velocity"], label="Ang. velocity (rad/s)", color="orange")
    ax.set_xlabel("Normalised swing time")
    ax.set_ylabel("Value")
    ax.set_title("Speed & angular velocity")
    ax.legend(fontsize=8)
    ax.grid(True)

    # ---- 2. Acceleration & jerk ----
    ax = axes[0, 1]
    ax.plot(df["time_norm"], df["acceleration"], label="Acceleration (m/s²)", color="red")
    ax.plot(df["time_norm"], df["jerk"], label="Jerk (m/s³)", color="purple", alpha=0.6)
    ax.set_xlabel("Normalised swing time")
    ax.set_ylabel("Value")
    ax.set_title("Acceleration & jerk")
    ax.legend(fontsize=8)
    ax.grid(True)

    # ---- 3. Stick tip trajectory (raw vs filtered) ----
    ax = axes[1, 0]
    if "tip_x_m_raw" in df.columns:
        ax.plot(df["tip_x_m_raw"], df["tip_y_m_raw"], label="Raw", color="red", alpha=0.5)
    ax.plot(df["tip_x_m"], df["tip_y_m"], label="Filtered (Kalman+RTS+poly)", color="green")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("Stick tip trajectory")
    ax.invert_yaxis()
    ax.legend(fontsize=8)
    ax.grid(True)

    # ---- 4. Hip / shoulder / X-factor ----
    ax = axes[1, 1]
    for col, label, color in [
        ("hip_angle_deg", "Hip angle", "teal"),
        ("shoulder_angle_deg", "Shoulder angle", "coral"),
        ("x_factor_deg", "X-factor", "black"),
    ]:
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors="coerce")
            ax.plot(df["time_norm"], vals, label=label, color=color)
    ax.set_xlabel("Normalised swing time")
    ax.set_ylabel("Degrees")
    ax.set_title("Hip & shoulder rotation / X-factor")
    ax.legend(fontsize=8)
    ax.grid(True)

    # ---- 5. Wrist angle ----
    ax = axes[2, 0]
    if "wrist_angle_deg" in df.columns:
        vals = pd.to_numeric(df["wrist_angle_deg"], errors="coerce")
        ax.plot(df["time_norm"], vals, label="Wrist angle", color="navy")
    ax.set_xlabel("Normalised swing time")
    ax.set_ylabel("Degrees")
    ax.set_title("Wrist angle (elbow-wrist-hand)")
    ax.legend(fontsize=8)
    ax.grid(True)

    # ---- 6. Arc radius / curvature / path efficiency ----
    ax = axes[2, 1]
    if "arc_radius_px" in df.columns:
        vals = pd.to_numeric(df["arc_radius_px"], errors="coerce")
        ax.plot(df["time_norm"], vals, label="Arc radius (px)", color="darkgreen")
    if "curvature_1_m" in df.columns:
        vals = pd.to_numeric(df["curvature_1_m"], errors="coerce")
        ax.plot(df["time_norm"], vals, label="Curvature (1/m)", color="brown")
    if "path_efficiency" in df.columns:
        vals = pd.to_numeric(df["path_efficiency"], errors="coerce")
        ax.plot(df["time_norm"], vals, label="Path efficiency", color="black", linestyle="--")
    ax.set_xlabel("Normalised swing time")
    ax.set_ylabel("Value")
    ax.set_title("Arc radius / curvature / path efficiency")
    ax.legend(fontsize=8)
    ax.grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot swing analysis from CSV.")
    parser.add_argument(
        "--csv",
        default="swing_analysis.csv",
        help="Path to the swing_analysis CSV file (default: swing_analysis.csv)",
    )
    args = parser.parse_args()
    plot(args.csv)
