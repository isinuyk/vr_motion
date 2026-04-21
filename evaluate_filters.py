import math
import pandas as pd
import numpy as np


def _series_stats(s):
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if len(s) == 0:
        return {}
    return {
        "count": int(len(s)),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "p90": float(s.quantile(0.90)),
        "p95": float(s.quantile(0.95)),
        "p99": float(s.quantile(0.99)),
        "max": float(s.max()),
    }


def _print_stats(title, stats, unit=""):
    if not stats:
        print(f"{title}: no valid samples")
        return
    unit_s = f" {unit}" if unit else ""
    print(f"{title} ({stats['count']} samples)")
    print(f"  mean   : {stats['mean']:.6f}{unit_s}")
    print(f"  median : {stats['median']:.6f}{unit_s}")
    print(f"  p90    : {stats['p90']:.6f}{unit_s}")
    print(f"  p95    : {stats['p95']:.6f}{unit_s}")
    print(f"  p99    : {stats['p99']:.6f}{unit_s}")
    print(f"  max    : {stats['max']:.6f}{unit_s}")


def main():
    df = pd.read_csv("swing_analysis.csv")

    required = {"tip_x_m", "tip_y_m", "tip_x_m_raw", "tip_y_m_raw"}
    if not required.issubset(df.columns):
        missing = sorted(required - set(df.columns))
        raise RuntimeError(f"Missing required columns in swing_analysis.csv: {missing}")

    dev_m = np.sqrt(
        (df["tip_x_m"] - df["tip_x_m_raw"]) ** 2
        + (df["tip_y_m"] - df["tip_y_m_raw"]) ** 2
    )
    dev_stats = _series_stats(dev_m)
    _print_stats("Raw-vs-filtered trajectory deviation", dev_stats, unit="m")

    if "jerk" in df.columns:
        jerk = pd.to_numeric(df["jerk"], errors="coerce")
        rms_jerk = math.sqrt(float((jerk.fillna(0.0) ** 2).mean()))
        print(f"RMS jerk (exported trajectory): {rms_jerk:.6f}")

    over_3cm = int((pd.to_numeric(dev_m, errors="coerce") > 0.03).sum())
    over_5cm = int((pd.to_numeric(dev_m, errors="coerce") > 0.05).sum())
    print(f"Frames with deviation > 3 cm: {over_3cm}")
    print(f"Frames with deviation > 5 cm: {over_5cm}")


if __name__ == "__main__":
    main()
