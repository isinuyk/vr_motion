import argparse
import csv
import copy
import json
import math
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config
from analysis import RunningMedian
from kalman import Kalman2D
from loader import load_folder
from rts_smoother import rts_smooth
from swing_analyzer import SwingAnalyzer
from utils_filter import MedianFilter2D, despike_trajectory, smooth_trajectory_poly


SESSION_METRICS = [
    "max_speed",
    "max_ang_vel",
    "max_accel",
    "swing_tempo",
    "smoothness_index",
    "path_efficiency",
    "curvature_rms",
    "backswing_duration",
    "downswing_duration",
    "backswing_peak_speed",
    "downswing_peak_speed",
]

EXPORT_HEADER = [
    "time",
    "stick_speed",
    "angular_velocity",
    "acceleration",
    "angular_acceleration",
    "energy_proxy",
    "jerk",
    "time_norm",
    "tip_x_m",
    "tip_y_m",
    "tip_x_m_raw",
    "tip_y_m_raw",
    "scale_m",
    "hip_angle_deg",
    "shoulder_angle_deg",
    "x_factor_deg",
    "wrist_angle_deg",
    "arc_radius_px",
    "curvature_1_m",
    "path_efficiency",
    "phase",
]


def _safe_float(value, default=np.nan):
    try:
        if value == "":
            return default
        return float(value)
    except Exception:
        return default


def _session_id(folder):
    return Path(folder).name


def discover_sessions(root):
    root = Path(root)
    sessions = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        if (folder / "mediapipe_data_full.json").exists() and (folder / "video_processed.mp4").exists():
            sessions.append(folder)
    return sessions


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def video_info(video_path):
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    cap.release()
    return fps, width, height, frames


def process_session(folder, profile="scientific", data_override=None, fps_override=None, stick_length_m=None):
    old_stick_len = config.STICK_REAL_LENGTH_M
    old_profile = config.FILTER_PROFILE
    try:
        if stick_length_m is not None:
            config.STICK_REAL_LENGTH_M = float(stick_length_m)
        config.set_filter_profile(profile)
        if data_override is None:
            data, video_path = load_folder(str(folder))
        else:
            data = data_override
            video_path = str(Path(folder) / "video_processed.mp4")
        fps, width, height, _ = video_info(video_path)
        if fps_override is not None:
            fps = fps_override
        analyzer = SwingAnalyzer(data, fps, (width, height))

        dt = 1.0 / fps if fps and fps > 0 else 1.0 / 30.0
        frame_img = np.zeros((height, width, 3), dtype=np.uint8)
        for idx, frame in enumerate(data):
            frame_img.fill(0)
            analyzer.process_frame(idx, frame_img, frame, dt=dt, t=idx * dt)

        rows = analyzer.finalize()
        summary = analyzer.summary()
        exp = analyzer._get_export_metrics()
        return {
            "ok": True,
            "data": data,
            "fps": fps,
            "width": width,
            "height": height,
            "frames": len(data),
            "rows": rows,
            "summary": summary,
            "impact_idx": exp["impact_idx"],
            "transition_idx": exp["transition_idx"],
            "impact_time": summary.get("impact_time", np.nan),
            "transition_time": summary.get("transition_time", np.nan),
            "analyzer": analyzer,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        config.STICK_REAL_LENGTH_M = old_stick_len
        config.set_filter_profile(old_profile)


def extract_reference_keyframes(folder):
    path = Path(folder) / "mocap_data.json"
    if not path.exists():
        return {}
    data = read_json(path)
    out = {}
    for item in data.get("keyframes", []):
        name = str(item.get("name", ""))
        t = _safe_float(item.get("time"))
        if np.isnan(t):
            continue
        low = name.lower()
        if "impact" in low:
            out["impact"] = t
        elif "top of backswing" in low or "(p4)" in low:
            out["top_backswing"] = t
        elif "downswing" in low or "transition" in low or "(p5)" in low:
            out["downswing_transition"] = t
        elif "address" in low or "(p1)" in low:
            out["address"] = t
    return out


def read_resource_metadata(folder):
    resource_path = Path(folder) / "resource_data.json"
    mocap_path = Path(folder) / "mocap_data.json"
    tags = []
    capture_tags = []
    row = {}
    if resource_path.exists():
        data = read_json(resource_path)
        tags = [str(t.get("tag", "")) for t in data.get("tags", []) if t.get("tag")]
        capture_tags = [
            f"{t.get('tagId')}={t.get('valueId')}"
            for t in data.get("captureTags", [])
            if t.get("tagId") or t.get("valueId")
        ]
        row.update(
            {
                "resource_status": data.get("status", ""),
                "filename": data.get("filename", ""),
                "tags": "; ".join(tags),
                "capture_tags": "; ".join(capture_tags),
            }
        )
    if mocap_path.exists():
        data = read_json(mocap_path)
        video = data.get("videoMetaData", {})
        row.update(
            {
                "mocap_status": data.get("status", ""),
                "view_id": data.get("viewId", ""),
                "preset_id": data.get("presetId", ""),
                "video_width": video.get("width", ""),
                "video_height": video.get("height", ""),
                "video_duration_s": video.get("duration", ""),
                "video_frames_meta": video.get("frames", ""),
                "video_fps_meta": video.get("fps", ""),
                "is_slow_motion": video.get("isVideoSlowMotion", ""),
            }
        )
    return row


def session_summary_row(folder, result):
    fps_cv, width, height, frames_cv = video_info(Path(folder) / "video_processed.mp4")
    row = {
        "session_id": _session_id(folder),
        "session_folder": str(folder),
        "processed": bool(result.get("ok")),
        "frames_json": result.get("frames", ""),
        "frames_video_cv": frames_cv,
        "video_fps_cv": fps_cv,
        "width_cv": width,
        "height_cv": height,
    }
    row.update(read_resource_metadata(folder))
    if result.get("ok"):
        summary = result["summary"]
        for metric in SESSION_METRICS:
            row[metric] = summary.get(metric, "")
        row["impact_time_auto_s"] = result.get("impact_time", "")
        row["transition_time_auto_s"] = result.get("transition_time", "")
        row["impact_idx_auto"] = result.get("impact_idx", "")
        row["transition_idx_auto"] = result.get("transition_idx", "")
    else:
        row["error"] = result.get("error", "")
    return row


def validation_rows(folder, result):
    refs = extract_reference_keyframes(folder)
    fps = result.get("fps", np.nan) if result.get("ok") else np.nan
    mappings = [
        ("impact", "impact_time", result.get("impact_time", np.nan), refs.get("impact", np.nan)),
        (
            "downswing_transition",
            "transition_time",
            result.get("transition_time", np.nan),
            refs.get("downswing_transition", np.nan),
        ),
        (
            "top_backswing",
            "transition_time_proxy",
            result.get("transition_time", np.nan),
            refs.get("top_backswing", np.nan),
        ),
    ]
    rows = []
    for event, auto_source, auto_t, ref_t in mappings:
        auto_t = _safe_float(auto_t)
        ref_t = _safe_float(ref_t)
        err_s = auto_t - ref_t if not (np.isnan(auto_t) or np.isnan(ref_t)) else np.nan
        rows.append(
            {
                "session_id": _session_id(folder),
                "event": event,
                "auto_source": auto_source,
                "auto_time_s": auto_t,
                "reference_time_s": ref_t,
                "error_s": err_s,
                "abs_error_s": abs(err_s) if not np.isnan(err_s) else np.nan,
                "error_ms": err_s * 1000.0 if not np.isnan(err_s) else np.nan,
                "abs_error_ms": abs(err_s) * 1000.0 if not np.isnan(err_s) else np.nan,
                "abs_error_frames": abs(err_s) * fps if not (np.isnan(err_s) or np.isnan(fps)) else np.nan,
            }
        )
    return rows


def rows_to_frame(rows):
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def repeatability_frame(session_df):
    rows = []
    for metric in SESSION_METRICS:
        vals = pd.to_numeric(session_df.get(metric), errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        if vals.empty:
            continue
        mean = float(vals.mean())
        std = float(vals.std(ddof=1)) if len(vals) > 1 else 0.0
        cv = abs(std / mean * 100.0) if abs(mean) > 1e-12 else np.nan
        rc = 1.96 * math.sqrt(2.0) * std
        rows.append(
            {
                "metric": metric,
                "n_sessions": int(len(vals)),
                "mean": mean,
                "std": std,
                "cv_percent": cv,
                "repeatability_coeff": rc,
                "min": float(vals.min()),
                "max": float(vals.max()),
            }
        )
    return pd.DataFrame(rows).sort_values("cv_percent", na_position="last")


def trajectory_deviation_from_rows(rows):
    if not rows:
        return {}
    df = pd.DataFrame(rows, columns=EXPORT_HEADER)
    for col in ["tip_x_m", "tip_y_m", "tip_x_m_raw", "tip_y_m_raw", "jerk"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    dev = np.sqrt((df["tip_x_m"] - df["tip_x_m_raw"]) ** 2 + (df["tip_y_m"] - df["tip_y_m_raw"]) ** 2).dropna()
    jerk = df["jerk"].replace([np.inf, -np.inf], np.nan).dropna()
    if dev.empty:
        return {}
    return {
        "samples": int(len(dev)),
        "mean_dev_m": float(dev.mean()),
        "median_dev_m": float(dev.median()),
        "p90_dev_m": float(dev.quantile(0.90)),
        "p95_dev_m": float(dev.quantile(0.95)),
        "p99_dev_m": float(dev.quantile(0.99)),
        "max_dev_m": float(dev.max()),
        "rms_jerk": float(math.sqrt(float((jerk ** 2).mean()))) if not jerk.empty else np.nan,
        "frames_dev_over_3cm": int((dev > 0.03).sum()),
        "frames_dev_over_5cm": int((dev > 0.05).sum()),
    }


def clone_with_landmark_dropout(data, drop_rate=0.10, seed=42):
    rng = np.random.default_rng(seed)
    out = copy.deepcopy(data)
    for frame in out:
        if rng.random() >= drop_rate:
            continue
        landmarks = frame.get("landmarks", [])
        if not landmarks:
            continue
        pts = landmarks[0]
        for idx in (17, 18, 19):
            if idx < len(pts):
                pts[idx]["x"] = None
                pts[idx]["y"] = None
    return out


def clone_frame_thinned(data, step=2):
    return copy.deepcopy(data[::step])


def sensitivity_rows(folder, baseline_result):
    if not baseline_result.get("ok"):
        return []
    base = baseline_result["summary"]
    rows = []
    scenarios = [
        ("frame_thinning_2x", {"data_override": clone_frame_thinned(baseline_result["data"], 2), "fps_override": baseline_result["fps"] / 2.0}),
        ("landmark_dropout_10_percent", {"data_override": clone_with_landmark_dropout(baseline_result["data"], 0.10, seed=hash(_session_id(folder)) % (2**32))}),
        ("scale_reference_plus_5_percent", {"stick_length_m": config.STICK_REAL_LENGTH_M * 1.05}),
    ]
    for scenario, kwargs in scenarios:
        res = process_session(folder, profile="scientific", **kwargs)
        row = {"session_id": _session_id(folder), "scenario": scenario, "processed": bool(res.get("ok"))}
        if res.get("ok"):
            for metric in ["max_speed", "smoothness_index", "path_efficiency", "curvature_rms", "swing_tempo"]:
                b = _safe_float(base.get(metric))
                v = _safe_float(res["summary"].get(metric))
                row[f"{metric}_baseline"] = b
                row[f"{metric}_scenario"] = v
                row[f"{metric}_delta"] = v - b if not (np.isnan(v) or np.isnan(b)) else np.nan
                row[f"{metric}_pct_change"] = ((v - b) / b * 100.0) if not (np.isnan(v) or np.isnan(b) or abs(b) < 1e-12) else np.nan
        else:
            row["error"] = res.get("error", "")
        rows.append(row)
    return rows


def _extract_raw_tip_base(data, width, height):
    tips = []
    bases = []
    for frame in data:
        pts = frame.get("landmarks", [[]])[0]
        def pt(i):
            if i >= len(pts):
                return None
            x = pts[i].get("x")
            y = pts[i].get("y")
            if x is None or y is None:
                return None
            return (float(x) * width, float(y) * height)
        tips.append(pt(19))
        bases.append(pt(17))
    return tips, bases


def _scale_series(raw_tips, bases):
    med = RunningMedian(win=config.STICK_CAL_WIN)
    scale = None
    out = []
    for tip, base in zip(raw_tips, bases):
        if tip and base:
            med_len = med.update(math.hypot(tip[0] - base[0], tip[1] - base[1]))
            if med_len and med_len > 0:
                raw_scale = config.STICK_REAL_LENGTH_M / med_len
                if scale is None:
                    scale = raw_scale
                else:
                    lo = scale * 0.97
                    hi = scale * 1.03
                    bounded = min(max(raw_scale, lo), hi)
                    scale = 0.8 * scale + 0.2 * bounded
        out.append(scale if scale else np.nan)
    return out


def _median_trajectory(raw_tips):
    filt = MedianFilter2D(win=config.MEDIAN_WIN)
    return [filt.update(p) if p is not None else None for p in raw_tips]


def _kalman_trajectory(points, fps):
    kf = Kalman2D(q_pos=8.0, q_vel=8.0, r_meas=6.0)
    dt = 1.0 / fps if fps and fps > 0 else 1.0 / 30.0
    out = []
    states = []
    covs = []
    dts = []
    for p in points:
        if p is None:
            x = kf.predict(dt) if kf.initialized else None
        else:
            x = kf.update(p, dt)
        if x is None:
            out.append(None)
            states.append(None)
            covs.append(None)
            dts.append(None)
        else:
            out.append((float(x[0, 0]), float(x[1, 0])))
            states.append(kf.x.copy())
            covs.append(kf.P.copy())
            dts.append(dt)
    return out, states, covs, dts, kf


def _rts_trajectory(states, covs, dts, kf):
    n = len(states)
    out = [None] * n
    i = 0
    while i < n:
        if states[i] is None:
            i += 1
            continue
        j = i
        while j < n and states[j] is not None:
            j += 1
        seg_states = [s.copy() for s in states[i:j]]
        seg_covs = [p.copy() for p in covs[i:j]]
        seg_fs = [kf.transition(dts[k + 1]) for k in range(i, j - 1)]
        if len(seg_states) >= 3 and len(seg_fs) == len(seg_states) - 1:
            xs, _ = rts_smooth(seg_states, seg_covs, seg_fs)
        else:
            xs = seg_states
        for k, x in enumerate(xs):
            out[i + k] = (float(x[0, 0]), float(x[1, 0]))
        i = j
    return out


def _trajectory_stats(raw, processed, bases, scales, fps):
    dev = []
    speeds = []
    accels = []
    jerks = []
    prev = None
    prev_speed = None
    prev_acc = None
    dt = 1.0 / fps if fps and fps > 0 else 1.0 / 30.0
    for p_raw, p, scale in zip(raw, processed, scales):
        if p_raw is not None and p is not None and not np.isnan(scale):
            dev.append(math.hypot((p[0] - p_raw[0]) * scale, (p[1] - p_raw[1]) * scale))
        if p is None or prev is None or np.isnan(scale):
            speeds.append(0.0)
            accels.append(0.0)
            jerks.append(0.0)
        else:
            speed = math.hypot(p[0] - prev[0], p[1] - prev[1]) / dt * scale
            accel = (speed - prev_speed) / dt if prev_speed is not None else 0.0
            jerk = (accel - prev_acc) / dt if prev_acc is not None else 0.0
            speeds.append(speed)
            accels.append(accel)
            jerks.append(jerk)
            prev_speed = speed
            prev_acc = accel
        if p is not None:
            prev = p
    dev_arr = np.array(dev, dtype=float)
    jerk_arr = np.array([j for j in jerks if abs(j) > 0], dtype=float)
    mean_sq_jerk = float(np.mean(jerk_arr ** 2)) if len(jerk_arr) else 0.0
    return {
        "samples": int(len(processed)),
        "valid_deviation_samples": int(len(dev_arr)),
        "mean_dev_m": float(np.mean(dev_arr)) if len(dev_arr) else np.nan,
        "p95_dev_m": float(np.quantile(dev_arr, 0.95)) if len(dev_arr) else np.nan,
        "max_dev_m": float(np.max(dev_arr)) if len(dev_arr) else np.nan,
        "rms_jerk": math.sqrt(mean_sq_jerk) if mean_sq_jerk > 0 else 0.0,
        "smoothness_index": -math.log10(mean_sq_jerk + 1e-9),
        "max_speed": float(np.max(speeds)) if speeds else 0.0,
        "max_accel": float(np.max(accels)) if accels else 0.0,
    }


def ablation_rows(folder, baseline_result):
    if not baseline_result.get("ok"):
        return []
    data = baseline_result["data"]
    fps = baseline_result["fps"]
    width = baseline_result["width"]
    height = baseline_result["height"]
    raw, bases = _extract_raw_tip_base(data, width, height)
    scales = _scale_series(raw, bases)
    med = _median_trajectory(raw)
    kalman, states, covs, dts, kf = _kalman_trajectory(med, fps)
    rts = _rts_trajectory(states, covs, dts, kf)
    full = baseline_result["analyzer"]._get_export_metrics()["smoothed_tip_px"]
    variants = {
        "median_only": med,
        "kalman_without_rts": kalman,
        "kalman_plus_rts_without_despiking": rts,
        "full_pipeline": full,
    }
    rows = []
    for name, traj in variants.items():
        stats = _trajectory_stats(raw, traj, bases, scales, fps)
        rows.append({"session_id": _session_id(folder), "pipeline_variant": name, "processed": True, **stats})
    return rows


def save_example_export(result, out_dir):
    if not result.get("ok"):
        return None
    path = out_dir / "example_swing_analysis.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(EXPORT_HEADER)
        writer.writerows(result["rows"])
    return path


def save_figures(out_dir, session_df, repeatability_df, validation_df, sensitivity_df, ablation_df, example_csv):
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    if not session_df.empty:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        pd.to_numeric(session_df["video_fps_cv"], errors="coerce").dropna().hist(ax=axes[0], bins=12)
        axes[0].set_title("Video frame-rate distribution")
        axes[0].set_xlabel("FPS")
        axes[0].set_ylabel("Sessions")
        pd.to_numeric(session_df["frames_json"], errors="coerce").dropna().hist(ax=axes[1], bins=12)
        axes[1].set_title("Frame-count distribution")
        axes[1].set_xlabel("Frames")
        axes[1].set_ylabel("Sessions")
        fig.tight_layout()
        fig.savefig(fig_dir / "fig_dataset_fps_frames.png", dpi=300)
        plt.close(fig)

    if not repeatability_df.empty:
        top = repeatability_df.sort_values("cv_percent").head(12)
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.barh(top["metric"], top["cv_percent"])
        ax.invert_yaxis()
        ax.set_xlabel("Coefficient of variation, %")
        ax.set_title("Ranked metric repeatability")
        fig.tight_layout()
        fig.savefig(fig_dir / "fig_repeatability_cv.png", dpi=300)
        plt.close(fig)

    if not validation_df.empty:
        val = validation_df.dropna(subset=["abs_error_ms"])
        if not val.empty:
            grouped = val.groupby("event")["abs_error_ms"].mean().sort_values()
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(grouped.index, grouped.values)
            ax.set_ylabel("Mean absolute error, ms")
            ax.set_title("Reference keyframe timing error")
            ax.tick_params(axis="x", rotation=20)
            fig.tight_layout()
            fig.savefig(fig_dir / "fig_validation_keyframe_errors.png", dpi=300)
            plt.close(fig)

    if not sensitivity_df.empty:
        cols = [c for c in sensitivity_df.columns if c.endswith("_pct_change")]
        if cols:
            records = []
            for scenario, g in sensitivity_df.groupby("scenario"):
                for col in cols:
                    records.append(
                        {
                            "scenario": scenario,
                            "metric": col.replace("_pct_change", ""),
                            "median_abs_pct_change": pd.to_numeric(g[col], errors="coerce").abs().median(),
                        }
                    )
            sens_plot = pd.DataFrame(records).dropna()
            if not sens_plot.empty:
                pivot = sens_plot.pivot(index="metric", columns="scenario", values="median_abs_pct_change")
                fig, ax = plt.subplots(figsize=(10, 5))
                pivot.plot(kind="bar", ax=ax)
                ax.set_ylabel("Median absolute change, %")
                ax.set_title("Sensitivity of selected metrics")
                fig.tight_layout()
                fig.savefig(fig_dir / "fig_sensitivity_results.png", dpi=300)
                plt.close(fig)

    if not ablation_df.empty:
        fig, ax = plt.subplots(figsize=(9, 5))
        plot_df = (
            ablation_df.groupby("pipeline_variant")["rms_jerk"]
            .median()
            .reindex(["median_only", "kalman_without_rts", "kalman_plus_rts_without_despiking", "full_pipeline"])
            .dropna()
        )
        ax.barh(plot_df.index, plot_df.values)
        ax.set_xlabel("Median RMS jerk")
        ax.set_title("Ablation comparison by jerk reduction")
        fig.tight_layout()
        fig.savefig(fig_dir / "fig_ablation_results.png", dpi=300)
        plt.close(fig)

    if example_csv and Path(example_csv).exists():
        df = pd.read_csv(example_csv)
        fig, axes = plt.subplots(2, 2, figsize=(11, 8))
        axes[0, 0].plot(df["time_norm"], df["stick_speed"], label="Stick speed")
        axes[0, 0].plot(df["time_norm"], df["angular_velocity"], label="Angular velocity")
        axes[0, 0].set_title("Speed and angular velocity")
        axes[0, 0].legend(fontsize=8)
        axes[0, 1].plot(df["time_norm"], df["acceleration"], label="Acceleration")
        axes[0, 1].plot(df["time_norm"], df["jerk"], label="Jerk", alpha=0.7)
        axes[0, 1].set_title("Acceleration and jerk")
        axes[0, 1].legend(fontsize=8)
        axes[1, 0].plot(df["tip_x_m_raw"], df["tip_y_m_raw"], label="Raw", alpha=0.6)
        axes[1, 0].plot(df["tip_x_m"], df["tip_y_m"], label="Smoothed")
        axes[1, 0].invert_yaxis()
        axes[1, 0].set_title("Raw vs smoothed trajectory")
        axes[1, 0].legend(fontsize=8)
        axes[1, 1].plot(df["time_norm"], df["path_efficiency"], label="Path efficiency")
        curv = pd.to_numeric(df["curvature_1_m"], errors="coerce")
        axes[1, 1].plot(df["time_norm"], curv, label="Curvature")
        axes[1, 1].set_title("Path efficiency and curvature")
        axes[1, 1].legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(fig_dir / "fig_example_kinematics_trajectory.png", dpi=300)
        plt.close(fig)


def write_summary_markdown(out_dir, session_df, repeatability_df, validation_df, sensitivity_df, ablation_df):
    lines = ["# Batch Article Evaluation Summary", ""]
    lines.append(f"- Sessions processed: {int(session_df['processed'].sum()) if not session_df.empty else 0}/{len(session_df)}")
    if not repeatability_df.empty:
        best = repeatability_df.sort_values("cv_percent").head(3)
        lines.append("- Most repeatable metrics: " + ", ".join(f"{r.metric} (CV={r.cv_percent:.2f}%)" for r in best.itertuples()))
    if not validation_df.empty:
        val = validation_df.dropna(subset=["abs_error_ms"])
        if not val.empty:
            lines.append("- Mean absolute keyframe timing error by event:")
            for event, value in val.groupby("event")["abs_error_ms"].mean().items():
                lines.append(f"  - {event}: {value:.1f} ms")
    lines.extend(
        [
            "",
            "Generated files:",
            "- dataset_summary.csv",
            "- validation_keyframe_errors.csv",
            "- sensitivity_results.csv",
            "- ablation_results.csv",
            "- repeatability_repeatability.csv",
            "- trajectory_deviation_summary.csv",
            "- figures/*.png",
        ]
    )
    (out_dir / "batch_evaluation_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate article evaluation CSVs and figures for all sessions.")
    parser.add_argument("--dataset-root", required=True, help="Root folder containing session subfolders.")
    parser.add_argument("--out-dir", default="article_package/evaluation_outputs", help="Output directory.")
    parser.add_argument("--limit", type=int, default=None, help="Optional number of sessions for a quick run.")
    parser.add_argument("--skip-sensitivity", action="store_true", help="Skip sensitivity scenarios.")
    parser.add_argument("--skip-ablation", action="store_true", help="Skip ablation scenarios.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sessions = discover_sessions(args.dataset_root)
    if args.limit:
        sessions = sessions[: args.limit]
    if not sessions:
        raise RuntimeError(f"No valid session folders found under {args.dataset_root}")

    session_rows = []
    validation_all = []
    sensitivity_all = []
    ablation_all = []
    trajectory_rows = []
    first_ok_result = None

    for idx, folder in enumerate(sessions, start=1):
        print(f"[{idx}/{len(sessions)}] {folder.name}")
        result = process_session(folder, profile="scientific")
        if first_ok_result is None and result.get("ok"):
            first_ok_result = result
        session_rows.append(session_summary_row(folder, result))
        validation_all.extend(validation_rows(folder, result))
        if result.get("ok"):
            traj = trajectory_deviation_from_rows(result["rows"])
            if traj:
                trajectory_rows.append({"session_id": _session_id(folder), **traj})
            if not args.skip_sensitivity:
                sensitivity_all.extend(sensitivity_rows(folder, result))
            if not args.skip_ablation:
                ablation_all.extend(ablation_rows(folder, result))

    session_df = rows_to_frame(session_rows)
    validation_df = rows_to_frame(validation_all)
    sensitivity_df = rows_to_frame(sensitivity_all)
    ablation_df = rows_to_frame(ablation_all)
    trajectory_df = rows_to_frame(trajectory_rows)
    repeatability_df = repeatability_frame(session_df[session_df["processed"] == True]) if not session_df.empty else pd.DataFrame()

    session_df.to_csv(out_dir / "dataset_summary.csv", index=False)
    validation_df.to_csv(out_dir / "validation_keyframe_errors.csv", index=False)
    sensitivity_df.to_csv(out_dir / "sensitivity_results.csv", index=False)
    ablation_df.to_csv(out_dir / "ablation_results.csv", index=False)
    trajectory_df.to_csv(out_dir / "trajectory_deviation_summary.csv", index=False)
    repeatability_df.to_csv(out_dir / "repeatability_repeatability.csv", index=False)

    example_csv = save_example_export(first_ok_result, out_dir) if first_ok_result else None
    save_figures(out_dir, session_df, repeatability_df, validation_df, sensitivity_df, ablation_df, example_csv)
    write_summary_markdown(out_dir, session_df, repeatability_df, validation_df, sensitivity_df, ablation_df)
    print(f"Saved outputs to {out_dir}")


if __name__ == "__main__":
    main()
