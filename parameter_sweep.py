import argparse
import importlib
import itertools
import json
import math
import time

import cv2
import numpy as np
import pandas as pd

import config
import swing_analyzer
from loader import load_folder


# Keep the grid reasonably sized so a full sweep is practical.
DEFAULT_GRID = {
    "TRAJ_POLY_WIN": [5, 7, 9],
    "TRAJ_POLY_DEG": [2, 3],
    "TRAJ_BLEND_RAW": [0.25, 0.40, 0.55],
    "TRAJ_MAX_DEV_PX": [6.0, 9.0, 12.0],
    "TRAJ_LAPLACE_PASSES": [1, 2, 3],
    "TRAJ_LAPLACE_ALPHA": [0.35, 0.45, 0.60],
    "TRAJ_DESPIKE_THRESH_PX": [12.0, 16.0, 20.0],
    "KF_ADAPTIVE_RESIDUAL_PX": [8.0, 10.0, 14.0],
}


def _combo_dicts(grid):
    keys = list(grid.keys())
    values = [grid[k] for k in keys]
    for vals in itertools.product(*values):
        combo = dict(zip(keys, vals))
        # Ensure valid polynomial settings.
        if combo["TRAJ_POLY_DEG"] >= combo["TRAJ_POLY_WIN"]:
            continue
        # Keep odd windows for centered local fitting.
        if combo["TRAJ_POLY_WIN"] % 2 == 0:
            continue
        yield combo


def _reload_analyzer_with_params(params, base_profile="scientific"):
    importlib.reload(config)
    config.set_filter_profile(base_profile)
    for k, v in params.items():
        setattr(config, k, v)
    sa = importlib.reload(swing_analyzer)
    return sa.SwingAnalyzer


def _safe_float(x, default=np.nan):
    try:
        return float(x)
    except Exception:
        return default


def _run_one_combo(data, fps, size, params, base_profile):
    SwingAnalyzer = _reload_analyzer_with_params(params, base_profile=base_profile)
    analyzer = SwingAnalyzer(data, fps, size)

    w, h = size
    frame_img = np.zeros((h, w, 3), dtype=np.uint8)
    dt = (1.0 / fps) if fps and fps > 0 else (1.0 / 30.0)

    for idx, frame in enumerate(data):
        # process_frame draws overlays into frame_img; reuse buffer for speed.
        frame_img.fill(0)
        analyzer.process_frame(idx, frame_img, frame, dt=dt, t=idx * dt)

    rows = analyzer.finalize()
    if not rows:
        raise RuntimeError("No rows produced by analyzer.finalize()")

    dev = []
    jerk = []
    for r in rows:
        tip_x = _safe_float(r[8])
        tip_y = _safe_float(r[9])
        raw_x = _safe_float(r[10])
        raw_y = _safe_float(r[11])
        if not np.isnan(tip_x) and not np.isnan(tip_y) and not np.isnan(raw_x) and not np.isnan(raw_y):
            dev.append(math.hypot(tip_x - raw_x, tip_y - raw_y))
        j = _safe_float(r[6])
        if not np.isnan(j):
            jerk.append(j)

    if not dev:
        raise RuntimeError("No valid deviation samples")
    if not jerk:
        raise RuntimeError("No valid jerk samples")

    dev_arr = np.array(dev, dtype=float)
    jerk_arr = np.array(jerk, dtype=float)
    summary = analyzer.summary()

    result = {
        **params,
        "samples": int(len(rows)),
        "mean_dev_m": float(np.mean(dev_arr)),
        "median_dev_m": float(np.median(dev_arr)),
        "p90_dev_m": float(np.quantile(dev_arr, 0.90)),
        "p95_dev_m": float(np.quantile(dev_arr, 0.95)),
        "max_dev_m": float(np.max(dev_arr)),
        "rms_jerk": float(np.sqrt(np.mean(jerk_arr ** 2))),
        "smoothness_index": float(summary.get("smoothness_index", 0.0)),
        "max_speed": float(summary.get("max_speed", 0.0)),
        "rejected_frames": int(getattr(analyzer, "rejected_tip_frames", 0)),
    }
    return result


def _norm_series(s):
    s = pd.to_numeric(s, errors="coerce")
    mn = s.min()
    mx = s.max()
    if pd.isna(mn) or pd.isna(mx) or abs(mx - mn) < 1e-12:
        return pd.Series(np.zeros(len(s)), index=s.index, dtype=float)
    return (s - mn) / (mx - mn)


def _pareto_front(df, cols):
    arr = df[cols].to_numpy(dtype=float)
    keep = np.ones(len(arr), dtype=bool)
    for i in range(len(arr)):
        if not keep[i]:
            continue
        dominates_i = np.all(arr <= arr[i], axis=1) & np.any(arr < arr[i], axis=1)
        if np.any(dominates_i):
            keep[i] = False
    return df[keep].copy()


def run_sweep(
    folder,
    alpha,
    top_k,
    max_combos,
    out_csv,
    pareto_csv,
    base_profile,
):
    data, video_path = load_folder(folder)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
    cap.release()
    size = (width, height)

    combos = list(_combo_dicts(DEFAULT_GRID))
    if max_combos is not None:
        combos = combos[: max(0, int(max_combos))]

    print(f"Dataset frames: {len(data)}")
    print(f"Video size/FPS: {width}x{height} @ {fps:.2f}")
    print(f"Base profile  : {base_profile}")
    print(f"Total combinations: {len(combos)}")
    print()

    results = []
    t_start = time.time()
    for idx, params in enumerate(combos, start=1):
        c_start = time.time()
        try:
            res = _run_one_combo(data, fps, size, params, base_profile=base_profile)
            results.append(res)
            elapsed = time.time() - c_start
            print(
                f"[{idx:04d}/{len(combos):04d}] ok "
                f"mean_dev={res['mean_dev_m']:.5f}m "
                f"p95_dev={res['p95_dev_m']:.5f}m "
                f"rms_jerk={res['rms_jerk']:.2f} "
                f"({elapsed:.2f}s)"
            )
        except Exception as e:
            elapsed = time.time() - c_start
            print(f"[{idx:04d}/{len(combos):04d}] fail ({elapsed:.2f}s): {e}")

    if not results:
        raise RuntimeError("Sweep produced no valid results")

    df = pd.DataFrame(results)

    # Multi-objective scalarization: lower is better on all terms.
    # alpha controls closeness-vs-smoothness emphasis.
    mean_dev_n = _norm_series(df["mean_dev_m"])
    p95_dev_n = _norm_series(df["p95_dev_m"])
    max_dev_n = _norm_series(df["max_dev_m"])
    rms_jerk_n = _norm_series(df["rms_jerk"])

    df["closeness_cost"] = 0.60 * mean_dev_n + 0.30 * p95_dev_n + 0.10 * max_dev_n
    df["smoothness_cost"] = rms_jerk_n
    df["objective_score"] = alpha * df["closeness_cost"] + (1.0 - alpha) * df["smoothness_cost"]

    df = df.sort_values("objective_score", ascending=True).reset_index(drop=True)
    pareto = _pareto_front(df, cols=["mean_dev_m", "rms_jerk"]).sort_values(
        ["mean_dev_m", "rms_jerk"], ascending=[True, True]
    )

    df.to_csv(out_csv, index=False)
    pareto.to_csv(pareto_csv, index=False)

    t_total = time.time() - t_start
    print()
    print(f"Sweep finished in {t_total:.1f}s")
    print(f"Saved full results: {out_csv}")
    print(f"Saved Pareto set  : {pareto_csv}")
    print()
    print(f"Top {min(top_k, len(df))} configs by objective_score")
    top = df.head(top_k)
    cols = [
        "objective_score",
        "mean_dev_m",
        "p95_dev_m",
        "max_dev_m",
        "rms_jerk",
        "TRAJ_BLEND_RAW",
        "TRAJ_MAX_DEV_PX",
        "TRAJ_LAPLACE_PASSES",
        "TRAJ_LAPLACE_ALPHA",
        "TRAJ_POLY_WIN",
        "TRAJ_POLY_DEG",
        "TRAJ_DESPIKE_THRESH_PX",
        "KF_ADAPTIVE_RESIDUAL_PX",
    ]
    print(top[cols].to_string(index=False))
    print()
    print("Best configuration JSON")
    print(json.dumps(top.iloc[0][list(DEFAULT_GRID.keys())].to_dict(), indent=2))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Grid search filter parameters for smoothness-vs-closeness tradeoff."
    )
    parser.add_argument(
        "--folder",
        required=True,
        help="Path to dataset folder containing mediapipe_data_full.json and video_processed.mp4",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.65,
        help="Weight for closeness cost in objective [0..1]. 1=only closeness, 0=only smoothness",
    )
    parser.add_argument("--top-k", type=int, default=10, help="Number of top rows to print")
    parser.add_argument(
        "--max-combos",
        type=int,
        default=None,
        help="Optional cap on number of tested combinations for quick runs",
    )
    parser.add_argument(
        "--out-csv",
        default="sweep_results.csv",
        help="Output CSV for all tested parameter combinations",
    )
    parser.add_argument(
        "--pareto-csv",
        default="sweep_pareto.csv",
        help="Output CSV for Pareto-optimal combinations (mean_dev_m vs rms_jerk)",
    )
    parser.add_argument(
        "--base-profile",
        choices=["realtime", "scientific"],
        default="scientific",
        help="Base profile before applying per-combo overrides",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    alpha = min(max(args.alpha, 0.0), 1.0)
    run_sweep(
        folder=args.folder,
        alpha=alpha,
        top_k=max(1, args.top_k),
        max_combos=args.max_combos,
        out_csv=args.out_csv,
        pareto_csv=args.pareto_csv,
        base_profile=args.base_profile,
    )
