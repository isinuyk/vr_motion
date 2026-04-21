import cv2
from analysis import midpoint
from config import COLOR_BODY, COLOR_STICK, COLOR_BALL, DOT_RADIUS, LINE_THICKNESS

_BALL_CLASS = 2
_BALL_RADIUS = 6


def safe_pt(pts, i, w, h):
    if i >= len(pts):
        return None
    p = pts[i]
    return (int(p["x"] * w), int(p["y"] * h))


def draw_dot(img, pt, color, r=DOT_RADIUS):
    if pt:
        cv2.circle(img, pt, r, color, -1)


def draw_line(img, p1, p2, color):
    if p1 and p2:
        cv2.line(img, p1, p2, color, LINE_THICKNESS)


def draw_skeleton(img, pts, w, h):
    # legs
    draw_line(img, safe_pt(pts, 11, w, h), safe_pt(pts, 13, w, h), COLOR_BODY)
    draw_line(img, safe_pt(pts, 13, w, h), safe_pt(pts, 15, w, h), COLOR_BODY)
    draw_line(img, safe_pt(pts, 12, w, h), safe_pt(pts, 14, w, h), COLOR_BODY)
    draw_line(img, safe_pt(pts, 14, w, h), safe_pt(pts, 16, w, h), COLOR_BODY)
    draw_line(img, safe_pt(pts, 11, w, h), safe_pt(pts, 12, w, h), COLOR_BODY)
    # torso — use shared midpoint() helper
    p11 = safe_pt(pts, 11, w, h)
    p12 = safe_pt(pts, 12, w, h)
    p5 = safe_pt(pts, 5, w, h)
    p6 = safe_pt(pts, 6, w, h)
    mid_hips = midpoint(p11, p12)
    mid_sh = midpoint(p5, p6)
    if mid_hips and mid_sh:
        mid_hips_i = (int(mid_hips[0]), int(mid_hips[1]))
        mid_sh_i = (int(mid_sh[0]), int(mid_sh[1]))
        draw_line(img, mid_hips_i, mid_sh_i, COLOR_BODY)
    draw_line(img, p5, p6, COLOR_BODY)
    # arms
    draw_line(img, p6, safe_pt(pts, 8, w, h), COLOR_BODY)
    draw_line(img, safe_pt(pts, 8, w, h), safe_pt(pts, 10, w, h), COLOR_BODY)
    draw_line(img, p5, safe_pt(pts, 7, w, h), COLOR_BODY)
    draw_line(img, safe_pt(pts, 7, w, h), safe_pt(pts, 9, w, h), COLOR_BODY)
    # joints
    for i in range(5, 17):
        draw_dot(img, safe_pt(pts, i, w, h), COLOR_BODY)
    for i in range(5):
        draw_dot(img, safe_pt(pts, i, w, h), COLOR_BODY)


def draw_stick(img, pts, w, h):
    p17 = safe_pt(pts, 17, w, h)
    p18 = safe_pt(pts, 18, w, h)
    p19 = safe_pt(pts, 19, w, h)
    draw_line(img, p17, p18, COLOR_STICK)
    draw_line(img, p18, p19, COLOR_STICK)
    draw_dot(img, p17, COLOR_STICK)
    draw_dot(img, p19, COLOR_STICK)
    return p17, p19


def draw_ball(img, frame, w, h):
    for bb in frame.get("bboxes", []):
        if int(bb.get("class", -1)) == _BALL_CLASS:
            cx = int((bb["x1"] + bb["x2"]) / 2 * w)
            cy = int((bb["y1"] + bb["y2"]) / 2 * h)
            cv2.circle(img, (cx, cy), _BALL_RADIUS, COLOR_BALL, -1)
            return (cx, cy)
    return None
