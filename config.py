# Colors (BGR)
COLOR_BODY = (200, 200, 200)
COLOR_STICK = (0, 180, 255)
COLOR_BALL = (0, 0, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_TRAJECTORY = (0, 255, 0)  # green trajectory

DOT_RADIUS = 4
LINE_THICKNESS = 2
IMPACT_DIST_PX = 20

# Physical calibration
STICK_REAL_LENGTH_M = 1.0  # meters, adjust to your actual stick length
PIXEL_TO_M = None          # calculated dynamically from stick landmarks

MAX_VEL_PX = 120        # px/frame
MAX_ACC_PX = 200        # px/frame²
MEDIAN_WIN = 5 