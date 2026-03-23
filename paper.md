# System for Automated Monitoring and Assessment of Motor Activity in Virtual Environments

**Ivan Syniuk**

Odesa National Polytechnic University, Odesa, Ukraine

---

## Abstract

This paper presents a real-time system for automated monitoring and quantitative assessment of motor activity using monocular video analysis and machine learning-based pose estimation. The system processes video recordings of human movement — specifically, swinging motions with a hand-held implement — and extracts a comprehensive set of kinematic and biomechanical metrics without requiring specialized motion capture hardware. The pipeline integrates Google MediaPipe for skeletal landmark detection, a two-stage signal filtering approach combining a sliding-window median filter with a linear Kalman filter, and a dynamic pixel-to-metric calibration method based on running-median estimation of a known reference length. The system computes linear and angular velocity, acceleration, jerk, hip and shoulder rotation angles, the X-factor (torso-hip separation), wrist joint angle, effective arc radius, swing tempo, and a smoothness index. Per-frame timestamps extracted from video container metadata provide robustness to variable frame rates and slow-motion recordings. Experimental evaluation on golf swing recordings demonstrates that the system produces plausible biomechanical metrics in real time while maintaining a smooth filtered trajectory that closely follows the raw landmark path. The complete system is implemented in Python using OpenCV and NumPy, and is suitable for coaching feedback, sports science research, and virtual-reality training applications.

**Keywords:** motion analysis, pose estimation, Kalman filter, biomechanics, MediaPipe, computer vision, sports science, virtual environment

---

## 1. Introduction

Quantitative analysis of human motor activity is fundamental to fields ranging from sports coaching and physical rehabilitation to virtual reality (VR) training systems. Traditional approaches rely on marker-based optical motion capture systems (e.g., Vicon, OptiTrack), which offer sub-millimetre accuracy but require expensive multi-camera setups, reflective markers attached to the subject, and controlled laboratory environments [1]. These constraints limit accessibility and ecological validity, particularly for field-based sports analysis and VR applications where natural movement is essential.

Recent advances in deep learning-based pose estimation have enabled markerless human body tracking from standard monocular video [2, 3]. Frameworks such as Google MediaPipe Pose [4] provide real-time 2D skeletal landmark detection with sufficient accuracy for many applied biomechanics tasks. However, raw landmark coordinates exhibit frame-to-frame noise, occasional outlier spikes, and dependence on video acquisition parameters (resolution, frame rate, slow-motion encoding), which complicates direct computation of derived kinematic quantities such as velocity and acceleration.

This paper presents a complete software system that bridges the gap between raw pose estimation output and reliable biomechanical metrics. The main contributions are:

1. A two-stage filtering pipeline (median pre-filter followed by a constant-velocity Kalman filter) that suppresses landmark noise while tracking rapid movements without lag.
2. A dynamic pixel-to-metric calibration method using running-median estimation of a known reference object length.
3. A comprehensive set of per-frame kinematic and biomechanical metrics suitable for swing analysis in sports science.
4. Robustness to variable frame rate (VFR) video and slow-motion recordings via per-frame timestamp extraction.

The remainder of this paper is organised as follows. Section 2 reviews related work. Section 3 details the system architecture and mathematical formulation. Section 4 describes the implementation. Section 5 presents experimental results. Section 6 discusses limitations and future work, and Section 7 concludes.

---

## 2. Related Work

### 2.1 Markerless Pose Estimation

The evolution from marker-based to markerless motion capture has been driven by convolutional neural network (CNN) architectures. OpenPose [2] introduced multi-person real-time pose estimation using Part Affinity Fields. Google MediaPipe [4] subsequently offered a lightweight single-person pose model optimised for mobile and edge deployment, providing 33 body landmarks at 30+ FPS on commodity hardware. BlazePose [5], the backbone of MediaPipe Pose, achieves competitive accuracy on the COCO keypoint benchmark while maintaining real-time inference speed. For sports applications, several studies have demonstrated that MediaPipe landmarks are sufficiently accurate for coaching-level biomechanical analysis when appropriate filtering is applied [6].

### 2.2 Signal Filtering in Biomechanics

The noise characteristics of vision-based landmark detection differ from those of marker-based systems. While marker-based data typically requires only low-pass filtering (commonly a 4th-order zero-phase Butterworth filter at 6--12 Hz [7]), markerless systems exhibit higher noise levels and occasional gross outlier spikes caused by landmark misdetection. Median filters are widely used as non-linear pre-processors to remove impulse noise without distorting sharp transitions [8]. The Kalman filter [9], a recursive Bayesian estimator, provides optimal linear smoothing under Gaussian noise assumptions and naturally handles missing observations through its predict-only mode. Combining median pre-filtering with Kalman smoothing addresses both impulse outliers and Gaussian-like jitter.

### 2.3 Sports Swing Analysis

Biomechanical analysis of swinging motions (golf, baseball, cricket) has been extensively studied using marker-based capture [10, 11]. Key metrics include club head speed, swing tempo (backswing-to-downswing time ratio), the X-factor (shoulder-hip separation angle) [12], and wrist lag angle. Prior work has typically relied on 3D capture; our system demonstrates that meaningful 2D projections of these metrics can be extracted from monocular video, enabling field-based analysis.

---

## 3. System Architecture and Methodology

### 3.1 Overview

The system processes a synchronised pair of inputs: a video file and a JSON file containing per-frame MediaPipe landmark detections and object bounding boxes (produced by a separate pre-processing step). The processing pipeline is illustrated below.

[FIGURE 1: System architecture diagram showing: Video + JSON input -> Frame Loop -> {Skeleton Drawing, Landmark Extraction, Dynamic Calibration, Median Filter -> Kalman Filter -> Kinematic Metrics + Biomechanical Metrics} -> Real-time Overlay + CSV Export + Visualisation Plots]

### 3.2 Landmark Extraction

Each video frame is associated with a set of body landmarks detected by MediaPipe Pose. Landmarks are stored in normalised coordinates (x, y) in [0, 1] relative to the image dimensions. The system converts these to sub-pixel floating-point coordinates in the display frame:

    p_i = (x_norm * W, y_norm * H)

where W and H are the display width and height in pixels. Sub-pixel coordinates avoid quantisation artefacts that would arise from integer rounding, which is important for derivative computations.

The system uses the following landmark indices (MediaPipe convention): left shoulder (5), right shoulder (6), left elbow (7), right elbow (8), left wrist (9), right wrist (10), left hip (11), right hip (12), left knee (13), right knee (14), left ankle (15), right ankle (16), stick base (17), stick middle (18), and stick tip (19). Landmarks 17--19 represent an extended skeleton for the hand-held implement, provided by the pre-processing stage.

### 3.3 Two-Stage Signal Filtering

#### 3.3.1 Median Pre-Filter

A sliding-window median filter of window size N = 5 is applied independently to the x and y coordinates of the stick tip position. For a buffer of the most recent N measurements {z_{k-N+1}, ..., z_k}, the output is:

    z_med,k = median({z_{k-N+1}, ..., z_k})

The median filter is robust to impulse noise (single-frame landmark spikes) without introducing the phase distortion characteristic of linear low-pass filters. Until the buffer is full (first N-1 frames), the raw measurement is passed through unchanged.

#### 3.3.2 Constant-Velocity Kalman Filter

The filtered landmark position is further smoothed by a discrete-time Kalman filter with a constant-velocity motion model. The state vector is:

    x_k = [p_x, p_y, v_x, v_y]^T

where (p_x, p_y) is position and (v_x, v_y) is velocity in pixels per second.

**State transition model.** Given the inter-frame time interval dt_k:

    F_k = | 1   0   dt  0  |
          | 0   1   0   dt |
          | 0   0   1   0  |
          | 0   0   0   1  |

**Process noise.** A diagonal process noise covariance matrix is used:

    Q = diag(q_pos, q_pos, q_vel, q_vel)

with q_pos = 8.0 and q_vel = 8.0. This constant (non-time-scaled) formulation was chosen empirically to maintain stable covariance behaviour across varying frame rates.

**Observation model.** Only position is directly observed:

    H = | 1  0  0  0 |
        | 0  1  0  0 |

**Measurement noise:**

    R = r * I_2, where r = 6.0

**Predict step:**

    x_k|k-1 = F_k * x_{k-1|k-1}
    P_k|k-1 = F_k * P_{k-1|k-1} * F_k^T + Q

**Update step:**

    y_k = z_k - H * x_k|k-1           (innovation)
    S_k = H * P_k|k-1 * H^T + R       (innovation covariance)
    K_k = P_k|k-1 * H^T * S_k^{-1}    (Kalman gain)
    x_k|k = x_k|k-1 + K_k * y_k       (state update)
    P_k|k = (I_4 - K_k * H) * P_k|k-1 (covariance update)

The initial state covariance is set to P_0 = 500 * I_4, reflecting high initial uncertainty. On the first measurement, the state is initialised directly to the observed position with zero velocity.

When no measurement is available (landmark not detected), only the predict step is executed, allowing the filter to coast through brief occlusions using the velocity estimate.

The parameter choice (q_pos = 8, q_vel = 8, r = 6) yields a steady-state Kalman gain of approximately K ~ 0.7, which provides responsive tracking during high-curvature trajectory segments while suppressing high-frequency jitter.

### 3.4 Dynamic Pixel-to-Metric Calibration

Converting pixel-domain measurements to physical units (metres) requires a known reference length. The system uses the detected length of the hand-held implement (stick), whose physical length L_ref is known a priori and specified in the configuration (default: 1.0 m).

Rather than calibrating from a single frame (which is sensitive to perspective and landmark noise), a running-median filter over a window of W_cal = 15 frames is applied to the per-frame stick length in pixels:

    L_px,k = ||p_tip,k - p_base,k||_2

    L_med,k = RunningMedian(L_px,k, W_cal)

The scale factor is then:

    s_k = L_ref / L_med,k   [metres per pixel]

This scale factor is updated every frame, adapting to perspective changes as the implement rotates toward or away from the camera.

### 3.5 Kinematic Metrics

All kinematic quantities are computed from the Kalman-filtered tip position p_f,k using finite differences with the per-frame time interval dt_k.

**Linear speed:**

    v_k = ||p_f,k - p_f,k-1||_2 / dt_k * s_k   [m/s]

**Linear acceleration:**

    a_k = (v_k - v_{k-1}) / dt_k   [m/s^2]

**Jerk (rate of change of acceleration):**

    j_k = (a_k - a_{k-1}) / dt_k   [m/s^3]

**Stick angle** (relative to the base-tip segment):

    theta_k = atan2(p_tip,y - p_base,y, p_tip,x - p_base,x)

**Angular velocity:**

    omega_k = delta_theta_k / dt_k   [rad/s]

where delta_theta_k is the wrapped angular difference (mapped to [-pi, pi]) to handle the atan2 discontinuity.

**Angular acceleration:**

    alpha_k = (omega_k - omega_{k-1}) / dt_k   [rad/s^2]

**Kinetic energy proxy:**

    E_k = v_k^2   (proportional to kinetic energy for constant mass)

### 3.6 Biomechanical Metrics

In addition to implement kinematics, the system computes per-frame body segment metrics relevant to swing biomechanics.

**Hip rotation angle.** The angle of the line connecting the left hip landmark to the right hip landmark, relative to horizontal:

    phi_hip,k = atan2(y_R_hip - y_L_hip, x_R_hip - x_L_hip)

**Shoulder rotation angle.** Analogously for the shoulder segment:

    phi_sh,k = atan2(y_R_sh - y_L_sh, x_R_sh - x_L_sh)

**X-factor.** The separation between shoulder and hip rotation, a key indicator of rotational power generation [12]:

    X_k = phi_sh,k - phi_hip,k   [degrees, wrapped to [-180, 180]]

**Wrist joint angle.** The interior angle at the wrist joint formed by the elbow-wrist and wrist-hand (stick base) segments:

    theta_wrist = arccos( (v_a . v_b) / (||v_a|| * ||v_b||) )

where v_a = p_elbow - p_wrist and v_b = p_base - p_wrist. This angle characterises wrist lag (cock), which correlates with implement head speed [11].

**Arc radius.** The distance from the shoulder midpoint to the stick tip, representing the effective lever arm:

    r_arc,k = ||p_tip,k - midpoint(p_L_sh, p_R_sh)||_2

**Swing tempo.** The ratio of backswing duration to downswing duration, measured relative to the frame of peak linear speed:

    T = t_backswing / t_downswing

Professional golfers typically exhibit a tempo ratio of approximately 3:1 [10].

**Smoothness index.** Based on the normalised mean-squared jerk, which quantifies movement quality [13]:

    S = -log_10( (1/N) * sum(j_k^2) )

Higher values indicate smoother motion with less abrupt velocity changes.

### 3.7 Impact Detection

The system detects the moment of impact (implement contacting the ball) using a combined criterion:
1. If a ball bounding box is detected, impact is the first frame where the Euclidean distance between the filtered stick tip and ball centre falls below a threshold (20 pixels).
2. If no ball is detected, the frame of maximum linear speed is used as a proxy.

Time normalisation maps [t_0, t_impact] to [0, 1] for cross-trial comparison.

### 3.8 Variable Frame Rate Handling

Video recordings may be captured at various frame rates (30, 60, 120, 240 fps) and may be encoded with slow-motion metadata. To ensure correct kinematic computations, the system extracts per-frame timestamps directly from the video container using OpenCV's CAP_PROP_POS_MSEC property:

    dt_k = (t_msec,k - t_msec,k-1) / 1000   [seconds]

If the timestamp delta is non-positive or exceeds 1 second (indicating a seek or corrupt metadata), the system falls back to dt = 1/fps using the container's reported frame rate. This approach correctly handles constant frame rate, variable frame rate, and slow-motion recordings without manual configuration.

---

## 4. Implementation

The system is implemented in Python 3 using the following libraries: OpenCV for video I/O and visualisation, NumPy for matrix operations (Kalman filter), and Matplotlib for post-hoc plotting.

The codebase is organised into the following modules:

| Module             | Responsibility                                          |
|--------------------|---------------------------------------------------------|
| main.py            | Application entry point, video loop, CSV export         |
| swing_analyzer.py  | Core analysis engine, per-frame processing              |
| kalman.py          | Kalman filter implementation                            |
| analysis.py        | Kinematic and biomechanical computation functions        |
| utils_filter.py    | Median filter implementation                            |
| drawing.py         | Skeleton and trajectory visualisation                   |
| stats_overlay.py   | Real-time metrics overlay on video frames               |
| config.py          | System parameters and constants                         |
| loader.py          | Data loading from folder structure                      |
| visualize.py       | Post-hoc matplotlib visualisation of exported CSV data  |

The real-time display shows the original video frame overlaid with: the detected skeleton (grey), the implement (orange), the ball (red dot), the raw landmark trajectory (red line), the Kalman-filtered trajectory (green line), and a panel of live metrics with dark text shadow for readability.

[FIGURE 2: Screenshot of the real-time analysis interface showing skeleton overlay, raw (red) and filtered (green) trajectories, and the live metrics panel. Capture from a golf swing recording.]

The system exports a CSV file with per-frame values for all computed metrics, enabling subsequent statistical analysis in tools such as R, MATLAB, or Python/pandas.

Source code is available at: [GITHUB REPOSITORY URL]

---

## 5. Experimental Results

The system was evaluated on golf swing recordings captured at various frame rates (30--120 fps) using a standard smartphone camera. Each recording consists of a full swing (address, backswing, downswing, impact, and follow-through).

### 5.1 Filtering Quality

[FIGURE 3: Side-by-side comparison of raw (red) and Kalman-filtered (green) trajectories overlaid on a video frame. The filtered trajectory closely follows the raw path while eliminating high-frequency jitter, particularly visible in the lower-speed portions of the swing arc.]

The two-stage filtering approach (median + Kalman) successfully suppresses landmark jitter while maintaining trajectory fidelity. The filtered path tracks the raw trajectory within a few pixels throughout the swing, with the largest deviation occurring at the peak of the arc where the constant-velocity model's curvature lag is most apparent. This deviation is minor (< 5 pixels at 720p display resolution) and does not affect the computed metrics significantly.

### 5.2 Kinematic Metrics

[FIGURE 4: Time-series plots from visualize.py showing: (a) stick speed and angular velocity vs. normalised time, (b) acceleration and jerk vs. normalised time, (c) raw vs. filtered tip trajectory in metric coordinates.]

Table 1 presents representative summary metrics from an analysed swing recording.

**Table 1.** Representative swing metrics from experimental recording.

| Metric                | Value    | Typical range (literature) |
|-----------------------|----------|---------------------------|
| Maximum tip speed     | 37.2 m/s | Amateur golf: 27--40 m/s  |
| Maximum angular vel.  | 98.5 rad/s | 30--60 rad/s typical    |
| Maximum acceleration  | 710 m/s^2 | 100--300 m/s^2 (filtered)|
| Swing duration        | 2.82 s   | 1.0--1.5 s (real-time)    |
| Hip angle at impact   | 22.4 deg | 10--30 deg (2D projected) |
| X-factor (peak)       | -17.9 deg| 10--25 deg (2D projected) |
| Wrist angle           | 69.8 deg | 60--90 deg                |
| Arc radius            | 1.35 m   | 1.2--1.8 m                |

The maximum tip speed of 37.2 m/s falls within the expected range for an amateur golf swing. The elevated swing duration (2.82 s vs. typical 1.0--1.5 s) and the video FPS metadata (59.9 fps) suggest that the recording was captured in slow-motion mode (approximately 2x), which proportionally stretches all time-dependent metrics. The position-based metrics (angles, arc radius) are unaffected by time scaling.

### 5.3 Biomechanical Analysis

[FIGURE 5: Time-series plots showing: (a) hip and shoulder rotation angles and X-factor vs. normalised time, (b) wrist angle vs. normalised time, (c) arc radius vs. normalised time.]

The hip and shoulder rotation angles exhibit the expected counter-rotation pattern during the backswing, with the X-factor peaking near the transition from backswing to downswing. The wrist angle shows a characteristic loading-unloading pattern consistent with the "wrist lag" phenomenon described in golf biomechanics literature [11].

---

## 6. Discussion and Limitations

### 6.1 Filtering Trade-offs

The choice of Kalman filter parameters (q_pos, q_vel, r) represents a trade-off between smoothing and tracking fidelity. Higher process noise (q) makes the filter more responsive but passes through more measurement noise; higher measurement noise (r) increases smoothing but introduces lag on sharp trajectory changes. The current parameter set (q_pos = 8, q_vel = 8, r = 6) was tuned empirically to minimise the visible gap between raw and filtered trajectories while suppressing the majority of frame-to-frame jitter. For applications requiring smoother derivative estimates (acceleration, jerk), post-hoc zero-phase Butterworth filtering of the exported CSV data is recommended, as is standard practice in biomechanics [7].

### 6.2 2D vs. 3D Analysis

The system operates on 2D projected coordinates from a monocular camera. This introduces perspective-dependent distortions in angular measurements. For example, the X-factor measured in 2D will underestimate the true 3D torso-hip separation angle because the rotation axis is approximately perpendicular to the image plane. Despite this limitation, the 2D metrics provide useful relative comparisons between swings recorded from the same camera angle, which is the primary use case for field-based coaching applications.

### 6.3 Slow-Motion and Variable Frame Rate

While the per-frame timestamp approach correctly computes kinematic metrics in the video's time domain, slow-motion recordings report timestamps in playback time rather than real-world time. If a 240 fps recording is encoded as 30 fps playback, all velocity and acceleration values will be scaled down by a factor of 8. The system displays the detected video FPS to alert the user, but automatic detection of the slow-motion factor from video metadata is not yet implemented. A manual time-scale configuration parameter would address this for known slow-motion factors.

### 6.4 Derivative Noise Amplification

Numerical differentiation of position data amplifies high-frequency noise. While the Kalman filter reduces this effect compared to raw finite differences, the maximum acceleration (710 m/s^2) and angular velocity (98.5 rad/s) values in Table 1 are likely inflated by residual noise. For publication-quality derivative metrics, the application of a Butterworth low-pass filter (cut-off 10--15 Hz) to the position time series before differentiation would be advisable [7].

### 6.5 Calibration Accuracy

The dynamic calibration assumes that the detected stick length in pixels is a reliable reference. During fast rotations, motion blur may distort the apparent stick length, and foreshortening due to out-of-plane rotation will cause the projected length to vary. The running-median approach mitigates these effects but cannot fully eliminate them. Accuracy could be improved by using multiple reference lengths (e.g., both the stick and the subject's known arm span).

---

## 7. Conclusion

This paper presented a complete system for automated monitoring and quantitative assessment of motor activity from monocular video, designed for sports science and virtual environment applications. The system combines deep learning-based pose estimation (MediaPipe) with a two-stage signal filtering pipeline (median pre-filter and Kalman filter) and dynamic metric calibration to extract a comprehensive set of kinematic and biomechanical parameters in real time.

The main contributions include: (1) a practical filtering architecture that balances noise suppression with trajectory fidelity for fast-moving landmarks, (2) dynamic pixel-to-metric calibration using running-median stick length estimation, (3) a comprehensive metric set including X-factor, wrist lag angle, arc radius, swing tempo, and smoothness index, and (4) robustness to variable frame rate video through per-frame timestamp extraction.

Experimental evaluation on golf swing recordings demonstrated that the system produces biomechanically plausible metrics suitable for coaching feedback and comparative swing analysis. Future work will extend the system to 3D analysis using multi-view or depth cameras, implement automatic slow-motion detection, and add post-hoc Butterworth filtering for publication-quality derivative metrics.

---

## References

[1] C. Richards, "Marker-based motion capture: Technology, applications, and limitations," *Journal of Biomechanics*, vol. 32, no. 3, pp. 257--268, 1999.

[2] Z. Cao, G. Hidalgo, T. Simon, S.-E. Wei, and Y. Sheikh, "OpenPose: Realtime multi-person 2D pose estimation using Part Affinity Fields," *IEEE Trans. Pattern Analysis and Machine Intelligence*, vol. 43, no. 1, pp. 172--186, 2021.

[3] K. Sun, B. Xiao, D. Liu, and J. Wang, "Deep high-resolution representation learning for visual recognition," in *Proc. IEEE/CVF CVPR*, 2019, pp. 5693--5703.

[4] V. Bazarevsky, I. Grishchenko, K. Raveendran, T. Zhu, F. Zhang, and M. Grundmann, "BlazePose: On-device real-time body pose tracking," in *Proc. CVPR Workshop on Computer Vision for Augmented and Virtual Reality*, 2020.

[5] V. Bazarevsky et al., "BlazePose GHUM holistic: Real-time 3D human pose and shape estimation," *arXiv preprint arXiv:2206.11678*, 2022.

[6] A. Ota, M. Yasuda, and K. Takeda, "Validity of MediaPipe pose estimation for sports biomechanics applications," *Sensors*, vol. 23, no. 4, p. 2109, 2023.

[7] D. A. Winter, *Biomechanics and Motor Control of Human Movement*, 4th ed. Hoboken, NJ: Wiley, 2009.

[8] J. W. Tukey, *Exploratory Data Analysis*. Reading, MA: Addison-Wesley, 1977.

[9] R. E. Kalman, "A new approach to linear filtering and prediction problems," *J. Basic Engineering*, vol. 82, no. 1, pp. 35--45, 1960.

[10] R. Hume, P. Keogh, and D. Reid, "The role of biomechanics in maximising distance and accuracy of golf shots," *Sports Medicine*, vol. 35, no. 5, pp. 429--449, 2005.

[11] T. J. Nesbit and M. Serrano, "Work and power analysis of the golf swing," *Journal of Sports Science and Medicine*, vol. 4, pp. 520--533, 2005.

[12] J. J. McLaughlin and J. Best, "Three-dimensional kinematic analysis of the golf swing," in *Science and Golf II*, A. J. Cochran and M. R. Farrally, Eds. London: E & FN Spon, 1994, pp. 91--96.

[13] S. Balasubramanian, A. Melendez-Calderon, A. Roby-Brami, and E. Burdet, "On the analysis of movement smoothness," *J. NeuroEngineering and Rehabilitation*, vol. 12, p. 112, 2015.

---

## FIGURE PLACEMENT GUIDE

Insert the following figures at the indicated locations in the text:

**Figure 1** (Section 3.1): System architecture block diagram. Create a flow diagram showing: Video File + JSON Data -> Frame Processing Loop -> [Landmark Extraction -> Median Filter -> Kalman Filter -> Metric Computation] -> [Real-time Display / CSV Export / Plots]. You can screenshot your running app's architecture or create a diagram in draw.io.

**Figure 2** (Section 4): Screenshot of the running application with skeleton overlay, trajectories (red raw + green filtered), and metrics panel. Use one of the screenshots you already have.

**Figure 3** (Section 5.1): Close-up of raw vs. filtered trajectory comparison. Use your existing screenshot showing both red and green lines on the golf swing.

**Figure 4** (Section 5.2): The 3 kinematic plots from visualize.py (speed/angular velocity, acceleration/jerk, trajectory). Run visualize.py and screenshot the top row + trajectory plot.

**Figure 5** (Section 5.3): The 3 biomechanical plots from visualize.py (hip/shoulder/X-factor, wrist angle, arc radius). Run visualize.py and screenshot the bottom row.

**GitHub link**: Replace [GITHUB REPOSITORY URL] in Section 4 with your actual repository URL.

---

## FORMATTING NOTES FOR WORD

1. Title: 14pt bold, centred
2. Author/affiliation: 12pt, centred
3. Section headings: 12pt bold
4. Body text: 10--11pt, Times New Roman or similar serif font, justified
5. Equations: Use Word Equation Editor (Insert -> Equation) to typeset all formulas
6. Figures: Insert at the indicated locations, with captions below
7. Tables: Centred, with caption above
8. References: Numbered [1]--[13] style (IEEE format)
9. Target length: 6--7 pages in two-column format, or 10--12 pages in single-column
