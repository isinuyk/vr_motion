import os

# Colors (BGR)
COLOR_BODY = (200, 200, 200)
COLOR_STICK = (0, 180, 255)
COLOR_BALL = (0, 0, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_TRAJECTORY = (0, 255, 0)

DOT_RADIUS = 4
LINE_THICKNESS = 2
IMPACT_DIST_PX = 20

# Physical calibration
STICK_REAL_LENGTH_M = 1.0  # meters - adjust to your actual stick length
MEDIAN_WIN = 5             # median pre-filter window
STICK_CAL_WIN = 15         # running-median window for stick-length calibration

# Valid filter profiles:
# - "realtime": lower latency, simpler/leaner path
# - "scientific": best offline quality and stability
FILTER_PROFILE = os.environ.get("VR_MOTION_FILTER_PROFILE", "scientific").strip().lower()


PROFILE_PRESETS = {
    "realtime": {
        # Keep line close to raw and avoid heavy post-processing.
        "TRAJ_POLY_WIN": 5,
        "TRAJ_POLY_DEG": 2,
        "TRAJ_BLEND_RAW": 0.55,
        "TRAJ_MAX_DEV_PX": 7.0,
        "TRAJ_LAPLACE_PASSES": 0,
        "TRAJ_LAPLACE_ALPHA": 0.40,
        "TRAJ_CLOSED_DIST_PX": 16.0,
        "TRAJ_CLOSED_MIN_COS": 0.50,
        "TRAJ_DESPIKE_THRESH_PX": 18.0,
        "TRAJ_DESPIKE_MAX_NEIGHBOR_PX": 30.0,
        "TRAJ_DESPIKE_PASSES": 1,
        "MAX_KF_PREDICT_GAP": 2,
        "TRAJ_POST_DESPIKE_THRESH_PX": 0.0,
        "TRAJ_POST_DESPIKE_MAX_NEIGHBOR_PX": 0.0,
        "TRAJ_POST_DESPIKE_PASSES": 0,
        "KF_MAX_MEAS_SPEED_PX_S": 3000.0,
        "KF_MAX_MEAS_ACCEL_PX_S2": 45000.0,
        "KF_ADAPTIVE_RESIDUAL_PX": 12.0,
        "KF_ADAPTIVE_R_MULT_MAX": 6.0,
    },
    "scientific": {
        # Stronger smoothing and stricter constraints for analysis/export quality.
        "TRAJ_POLY_WIN": 7,
        "TRAJ_POLY_DEG": 2,
        "TRAJ_BLEND_RAW": 0.34,
        "TRAJ_MAX_DEV_PX": 9.0,
        "TRAJ_LAPLACE_PASSES": 3,
        "TRAJ_LAPLACE_ALPHA": 0.45,
        "TRAJ_CLOSED_DIST_PX": 20.0,
        "TRAJ_CLOSED_MIN_COS": 0.35,
        "TRAJ_DESPIKE_THRESH_PX": 16.0,
        "TRAJ_DESPIKE_MAX_NEIGHBOR_PX": 30.0,
        "TRAJ_DESPIKE_PASSES": 2,
        "MAX_KF_PREDICT_GAP": 2,
        "TRAJ_POST_DESPIKE_THRESH_PX": 9.0,
        "TRAJ_POST_DESPIKE_MAX_NEIGHBOR_PX": 26.0,
        "TRAJ_POST_DESPIKE_PASSES": 1,
        "KF_MAX_MEAS_SPEED_PX_S": 2600.0,
        "KF_MAX_MEAS_ACCEL_PX_S2": 38000.0,
        "KF_ADAPTIVE_RESIDUAL_PX": 10.0,
        "KF_ADAPTIVE_R_MULT_MAX": 9.0,
    },
}


def set_filter_profile(profile_name):
    """
    Apply one of the predefined filter profiles by mutating module constants.
    Returns the normalized profile name.
    """
    global FILTER_PROFILE
    name = (profile_name or "").strip().lower()
    if name not in PROFILE_PRESETS:
        raise ValueError(f"Unknown FILTER_PROFILE '{profile_name}'. Use: {sorted(PROFILE_PRESETS)}")
    FILTER_PROFILE = name
    for key, val in PROFILE_PRESETS[name].items():
        globals()[key] = val
    return FILTER_PROFILE


# Apply selected profile at import time so other modules see finalized constants.
set_filter_profile(FILTER_PROFILE)
