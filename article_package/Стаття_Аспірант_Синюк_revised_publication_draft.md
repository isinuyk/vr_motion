# Markerless Video-Based Golf Stick Motion Analysis Using Kalman Filtering, RTS Smoothing, and Repeatability Assessment

Ivan Suniuk  
Odesa National Polytechnic University, Odesa, Ukraine  
E-mail: [to be completed]  
ORCID: [to be completed]

## Abstract

Markerless video analysis can make quantitative assessment of sport movement accessible outside specialized motion-capture laboratories, but its scientific use requires more than visually smooth trajectories. Raw landmark streams obtained from monocular video are affected by frame-rate variability, temporary landmark loss, camera-viewpoint changes, scale instability, and single-frame detection errors. These factors are especially problematic in golf-stick motion, where velocity, acceleration, angular velocity, and phase timing are computed from rapidly changing image-plane coordinates. This study presents a reproducible pipeline for golf-stick movement analysis in virtual-reality-oriented training and sport-biomechanics applications. The pipeline integrates landmark extraction, running-median pre-filtering, confidence-aware Kalman tracking, Rauch-Tung-Striebel backward smoothing, trajectory despiking, bounded local polynomial smoothing, dynamic scale calibration, phase segmentation, and export of scalar and time-series movement metrics. The method was evaluated on 71 recorded swing sessions processed with the scientific filtering profile. All sessions were processed successfully. Across sessions, the most stable metric was the smoothness index (mean -5.882, SD 1.266, CV 21.52%), followed by path efficiency (mean 0.726, SD 0.277, CV 38.17%). Higher-order derivative metrics were substantially less stable: maximum acceleration showed mean 185.16 m/s², SD 400.39 m/s², and CV 216.24%. A representative raw-versus-filtered trajectory check showed a mean deviation of 0.053 m and a median deviation of 0.050 m between exported raw and smoothed tip trajectories. The results support the use of smoothness and path-based indicators as primary endpoints for heterogeneous video recordings, while acceleration peaks should be treated as exploratory unless recording conditions are tightly controlled. The manuscript also defines a reference-validation protocol, a sensitivity-analysis protocol, and an ablation plan required for final external validation without inventing unavailable experimental results.

**Keywords:** markerless motion analysis; golf swing; Kalman filter; Rauch-Tung-Striebel smoother; trajectory smoothing; path efficiency; repeatability; virtual reality; sports biomechanics.

## 1. Introduction

Quantitative assessment of human motion is central to sport biomechanics, rehabilitation, coaching feedback, and virtual-reality (VR) training systems. Conventional marker-based motion-capture systems provide high spatial accuracy, but they require controlled laboratory conditions, multiple calibrated cameras, reflective markers, and trained operators. These requirements limit their applicability in field-based sport practice and in VR-oriented training contexts where natural movement, rapid setup, and repeated measurements are important.

Markerless video-based tracking offers a practical alternative. A standard camera and pose-estimation model can provide per-frame skeletal and implement landmarks without attaching markers to the athlete. For golf-stick movement, such a system can estimate the path of the stick tip, phase timing, speed profile, angular motion, torso and shoulder indicators, wrist angle, swing tempo, path efficiency, curvature, and smoothness. However, the direct use of raw image landmarks is scientifically unsafe. Monocular landmarks contain frame-to-frame jitter, missing detections, outliers caused by occlusion or motion blur, and scale changes caused by camera geometry. These errors are amplified when positions are differentiated to obtain velocity, acceleration, jerk, and angular velocity.

The practical research problem is therefore not only to build a working visualization tool, but to justify a reproducible measurement workflow. A scientifically useful pipeline must specify how landmarks are extracted, how missing or uncertain measurements are handled, how filtering and smoothing are formulated, how raw, filtered, and smoothed trajectories are compared, how phases are defined, and how metric repeatability is assessed across sessions. It must also identify which metrics are reliable enough for cross-session interpretation and which metrics should be considered exploratory.

This study addresses that problem by revising and extending a markerless golf-stick motion-analysis pipeline. Compared with a basic implementation, the revised pipeline removes first-frame derivative artifacts, unifies impact-detection logic, synchronizes summary and exported metrics, stabilizes dynamic scale estimation, adds path-efficiency, curvature, and phase-specific indicators, and reports repeatability across 71 processed sessions. The main contribution is not a new isolated filter. The contribution is a methodical integration of established signal-processing components with coordinated scale adaptation, phase analysis, robust export logic, and repeatability evidence under heterogeneous video conditions.

[Insert Figure 1: System Architecture Diagram]

## 2. Literature Review and Problem Statement

Biomechanical studies of golf and related striking movements show that timing, segment coordination, implement speed, wrist mechanics, and rotational sequencing are meaningful descriptors of performance. Marker-based studies have traditionally provided the most reliable measurement basis, but their practical cost and laboratory requirements restrict repeated use in coaching and VR training scenarios. Markerless human-pose estimation has reduced this barrier by allowing body landmarks to be estimated from ordinary video, and modern systems can operate close to real time.

Despite this accessibility, markerless motion analysis remains sensitive to measurement uncertainty. In computer-vision tracking, Kalman filtering and smoothing methods are widely used because they combine a motion model with noisy observations. Median filters are useful for impulse noise, while Kalman filters handle stochastic measurement noise and short gaps in observations. Backward smoothers such as the Rauch-Tung-Striebel (RTS) smoother improve offline trajectory estimates by using future observations after the forward filtering pass. Local polynomial and related smoothing methods can further reduce derivative noise when bounded to avoid excessive drift from the observed path.

For scientific publication, visual stability of the tracked signal is not sufficient. Markerless motion analysis should also include reference-based accuracy assessment, sensitivity analysis under changing recording conditions, and quantitative reliability or agreement statistics. The current dataset provides repeatability evidence across 71 sessions and trajectory-deviation evidence for one exported swing, but external validation against manually annotated reference events and formal agreement statistics are not yet available. The study therefore distinguishes between completed evidence and required validation steps.

The problem addressed in this manuscript is the development and evaluation of a reproducible markerless video pipeline for golf-stick motion analysis that can (i) process heterogeneous recordings, (ii) produce stable trajectories and interpretable movement-quality metrics, (iii) compare raw, filtered, and smoothed trajectories, and (iv) define a clear path toward external validation as a measurement instrument.

## 3. Aim and Objectives

The aim of the study is to develop and evaluate a reproducible markerless video-based workflow for golf-stick motion analysis suitable for VR training and sport-biomechanics research.

The objectives are:

1. To describe the complete motion-tracking pipeline from video landmarks to exported kinematic and biomechanical metrics.
2. To formulate the Kalman filtering and RTS smoothing stages used to stabilize the stick-tip trajectory.
3. To remove derivative initialization artifacts, unify impact-detection logic, and keep summary values consistent with exported CSV values.
4. To stabilize dynamic pixel-to-metre scaling under varying camera geometry.
5. To compute path efficiency, curvature, phase duration, peak speed, smoothness, and other phase-specific indicators.
6. To compare raw, filtered, and smoothed trajectories using trajectory-deviation and smoothness indicators.
7. To quantify repeatability across available sessions using mean, standard deviation, coefficient of variation, and repeatability coefficient.
8. To define the required reference-validation, sensitivity-analysis, ablation, and formal agreement protocols recommended before final submission.

## 4. Materials and Methods

### 4.1 Study Design and Dataset

The study uses recorded golf-stick swing sessions processed by a markerless video-analysis pipeline. The available reliability dataset contains 71 sessions, all of which were processed successfully with the scientific filtering profile. The sessions include heterogeneous frame counts and frame rates, including recordings near 24, 30, 50, and 60 frames per second. The current files do not specify the number of athletes, number of repetitions per athlete, camera position distribution, type of golf stroke, or distribution of video quality. These fields should be completed before journal submission because repeatability statistics depend on whether variation reflects measurement noise, athlete-to-athlete differences, session-to-session differences, or recording-condition differences.

Recommended dataset reporting fields:

| Field | Value for final manuscript |
|---|---|
| Number of athletes | [to be completed] |
| Number of sessions | 71 |
| Number of repeated trials per athlete | [to be completed] |
| Camera type and resolution | [to be completed] |
| Frame-rate range | approximately 24-60 fps in available processed sessions |
| Recording viewpoint | [to be completed] |
| Stroke type | [to be completed] |
| Video-quality classes | [to be completed] |

### 4.2 Input Data and Landmark Extraction

Each processed frame contains body landmarks and stick landmarks obtained from a preprocessing stage. Landmarks are represented in image coordinates and then converted into floating-point pixel coordinates. For a normalized landmark \(z_k = (x_{norm,k}, y_{norm,k})\) and frame dimensions \(W \times H\), the pixel coordinate is:

\[
p_k = (x_{norm,k} W,\; y_{norm,k} H).
\]

The main tracked point is the golf-stick tip. When available, the stick base and stick middle landmarks are also used to estimate stick orientation and scale. Body landmarks such as shoulders, hips, elbows, and wrists are used to compute biomechanical descriptors including shoulder angle, hip angle, X-factor, wrist angle, and effective arc radius.

The pipeline explicitly separates the following coordinate streams:

1. **Raw trajectory:** the direct measured stick-tip landmark after coordinate conversion.
2. **Pre-filtered trajectory:** the trajectory after local median filtering to reduce isolated spikes.
3. **Kalman-filtered trajectory:** the forward state estimate produced by the motion model and measurements.
4. **Smoothed trajectory:** the offline estimate after RTS backward smoothing, despiking, and bounded local polynomial smoothing.

[Insert Figure 2: Landmark Definition for Body and Golf Stick]

### 4.3 Median Pre-Filtering

A running median filter is applied independently to the \(x\) and \(y\) coordinates of the stick tip:

\[
z^{med}_k = \operatorname{median}(z_{k-m+1}, \ldots, z_k),
\]

where \(m\) is the median-window length. The median stage is included because markerless detections may contain isolated one-frame errors that are not well modeled by Gaussian noise. During the first frames, before the window is full, the available observations are used without introducing artificial padding.

### 4.4 Constant-Velocity Kalman Filter

The Kalman stage models the stick-tip position and velocity in the image plane. The state vector is:

\[
x_k = [p_{x,k},\; p_{y,k},\; v_{x,k},\; v_{y,k}]^T.
\]

For inter-frame interval \(\Delta t_k\), the transition matrix is:

\[
F_k =
\begin{bmatrix}
1 & 0 & \Delta t_k & 0 \\
0 & 1 & 0 & \Delta t_k \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}.
\]

Only position is observed:

\[
z_k = Hx_k + \epsilon_k,\quad
H =
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0
\end{bmatrix}.
\]

The prediction step is:

\[
\hat{x}_{k|k-1}=F_k\hat{x}_{k-1|k-1},
\]

\[
P_{k|k-1}=F_kP_{k-1|k-1}F_k^T+Q.
\]

The innovation, innovation covariance, Kalman gain, and update are:

\[
y_k=z_k-H\hat{x}_{k|k-1},
\]

\[
S_k=HP_{k|k-1}H^T+R_k,
\]

\[
K_k=P_{k|k-1}H^TS_k^{-1},
\]

\[
\hat{x}_{k|k}=\hat{x}_{k|k-1}+K_ky_k,
\]

\[
P_{k|k}=(I-K_kH)P_{k|k-1}.
\]

When a landmark is missing, the update step is skipped and the predicted state is retained. This allows short gaps to be bridged using the velocity model.

### 4.5 Confidence-Weighted Measurement Noise

The mentor review correctly noted that uncertainty should not only be mentioned but also modeled. The recommended formulation is a confidence-weighted measurement covariance. If the pose-estimation stage provides a landmark confidence score \(c_k \in (0,1]\), the measurement noise can be adapted as:

\[
R_k = \frac{r_0}{\max(c_k,c_{min})}I_2,
\]

where \(r_0\) is the baseline measurement variance and \(c_{min}\) prevents numerical instability. Low-confidence landmarks therefore increase \(R_k\), reduce the Kalman gain, and shift the estimate toward the motion model rather than the uncertain measurement. If confidence scores are unavailable in the exported data, this subsection should be implemented as a planned extension or replaced by a binary confidence proxy based on detection presence, residual gating, and stick-length plausibility.

### 4.6 Physical Gating and Outlier Handling

Before accepting a measurement, the pipeline checks whether the candidate point is physically plausible relative to the predicted state. The Mahalanobis innovation distance can be used:

\[
d_k^2 = y_k^T S_k^{-1} y_k.
\]

Measurements with \(d_k^2\) above a predefined threshold are treated as outliers and either rejected or down-weighted. Additional practical gates include maximum frame-to-frame displacement, stick-length plausibility, and landmark availability. These gates are important because a single erroneous frame can produce large acceleration and jerk artifacts.

### 4.7 Rauch-Tung-Striebel Backward Smoothing

For offline scientific analysis, the forward Kalman estimates are improved using RTS smoothing. After the forward pass has produced \(\hat{x}_{k|k}\), \(P_{k|k}\), and \(F_k\), the backward pass computes:

\[
P_{k+1|k}=F_kP_{k|k}F_k^T+Q,
\]

\[
G_k=P_{k|k}F_k^TP_{k+1|k}^{-1},
\]

\[
\hat{x}_{k|T}=\hat{x}_{k|k}+G_k(\hat{x}_{k+1|T}-F_k\hat{x}_{k|k}),
\]

\[
P_{k|T}=P_{k|k}+G_k(P_{k+1|T}-P_{k+1|k})G_k^T.
\]

The RTS smoother uses later observations to refine earlier state estimates. This is appropriate for post-hoc scientific analysis and figure generation, while the forward Kalman estimate remains suitable for lower-latency real-time feedback.

### 4.8 Trajectory Despiking and Bounded Polynomial Smoothing

After RTS smoothing, the trajectory is checked for residual spikes. Local deviations above a configured threshold are corrected using neighboring trajectory structure. A local polynomial smoother is then applied with bounded deviation from the measured trajectory so that the smoothed path does not become visually plausible but physically detached from the observed movement. This stage is designed to improve derivative stability while preserving trajectory fidelity.

### 4.9 Dynamic Pixel-to-Metre Scaling

Physical interpretation requires conversion from pixels to metres. The system uses stick length as a reference:

\[
L^{px}_k = \|p^{tip}_k - p^{base}_k\|_2.
\]

The instantaneous scale is:

\[
s_k = \frac{L^{ref}}{\operatorname{median}(L^{px}_{k-w+1}, \ldots, L^{px}_k)},
\]

where \(L^{ref}\) is the known physical stick length and \(w\) is the calibration window. To reduce scale jumps, the scale update is bounded and exponentially smoothed. This is necessary because apparent stick length changes with perspective, motion blur, partial occlusion, and landmark jitter.

### 4.10 Kinematic and Biomechanical Metrics

For smoothed position \(p_k\), inter-frame time interval \(\Delta t_k\), and scale \(s_k\), linear speed is:

\[
v_k=\frac{\|p_k-p_{k-1}\|_2}{\Delta t_k}s_k.
\]

Acceleration and jerk are:

\[
a_k=\frac{v_k-v_{k-1}}{\Delta t_k},
\]

\[
j_k=\frac{a_k-a_{k-1}}{\Delta t_k}.
\]

Stick angle is:

\[
\theta_k = \operatorname{atan2}(p^{tip}_{y,k}-p^{base}_{y,k},\;p^{tip}_{x,k}-p^{base}_{x,k}),
\]

and angular velocity is:

\[
\omega_k = \frac{\operatorname{wrap}(\theta_k-\theta_{k-1})}{\Delta t_k}.
\]

Path efficiency is computed as:

\[
E^{path}_k = \frac{\|p_k-p_0\|_2}{\sum_{i=1}^{k}\|p_i-p_{i-1}\|_2}.
\]

Curvature is estimated from local three-point geometry. For consecutive points \(p_{k-1}\), \(p_k\), and \(p_{k+1}\), curvature can be expressed as:

\[
\kappa_k = \frac{4A_k}{abc},
\]

where \(A_k\) is the triangle area and \(a\), \(b\), and \(c\) are side lengths. This provides a local measure of trajectory bending.

The smoothness index is based on jerk magnitude and is reported as a movement-quality indicator. In the available implementation, more stable smoothness estimates were observed than acceleration peaks across heterogeneous sessions.

### 4.11 Phase Segmentation

The swing is divided into backswing and downswing phases using transition detection before impact. Impact is detected by a unified rule: if a ball detection is available, impact is the first frame where stick-tip-to-ball distance falls below a threshold; otherwise, the frame of maximum speed is used as a proxy. Phase metrics include backswing duration, downswing duration, backswing peak speed, downswing peak speed, and swing tempo.

### 4.12 Raw, Filtered, and Smoothed Comparison

Comparison between trajectory stages is performed using pointwise Euclidean deviation:

\[
e_k = \|p^{smooth}_k-p^{raw}_k\|_2.
\]

Summary indicators include mean deviation, median deviation, 90th and 95th percentile deviation, maximum deviation, RMS jerk, and the number of frames above selected deviation thresholds. This comparison does not prove external accuracy, because raw landmarks are not a ground truth; it quantifies how far the final smoothed trajectory moves away from the measured signal.

### 4.13 Reference-Validation Protocol Required for Final Submission

To satisfy the mentor’s main scientific recommendation, an external validation subset should be added before submission. The recommended minimal protocol is:

1. Select a representative subset of sessions across frame rates and video-quality levels.
2. Manually annotate impact, top of backswing, and start of downswing.
3. Manually annotate 8-12 control points along the stick-tip trajectory.
4. Compare automatic phase-event timing with reference timing in frames and milliseconds.
5. Compare automatic and reference trajectory points using mean absolute geometric error.
6. Compare scalar metrics using absolute error, relative error, and correlation or concordance.

Table 1 should be completed only after the annotations are performed.

**Table 1. Reference-validation results to be completed before submission.**

| Validation target | Metric | Result |
|---|---|---|
| Impact timing | mean absolute error, frames/ms | [to be completed] |
| Top of backswing timing | mean absolute error, frames/ms | [to be completed] |
| Start of downswing timing | mean absolute error, frames/ms | [to be completed] |
| Stick-tip control points | mean geometric error | [to be completed] |
| Scalar metrics | absolute/relative error | [to be completed] |
| Scalar metrics | correlation/concordance | [to be completed] |

### 4.14 Sensitivity-Analysis Protocol Required for Final Submission

The sensitivity analysis should quantify how stable the metrics remain under controlled degradation of input conditions:

1. Frame thinning: repeat processing after reducing the effective frame rate.
2. Landmark dropout: randomly remove selected landmark observations at predefined rates.
3. Scale perturbation: perturb the stick-length scale or simulate small camera-position changes.
4. Robustness ranking: report which metrics change least and which change most.

This protocol directly tests the practical claim that the method is robust under heterogeneous video conditions.

**Table 2. Sensitivity-analysis results to be completed before submission.**

| Perturbation | Primary metric | Expected reporting format |
|---|---|---|
| Frame thinning | change in smoothness, path efficiency, max speed | percentage change from baseline |
| Landmark dropout | completion rate and trajectory deviation | percentage completion and deviation |
| Scale perturbation | metric stability | percentage change from baseline |
| Combined degradation | stable/unstable metric classification | retained or changed |

### 4.15 Ablation Protocol Required for Final Submission

An ablation study is recommended to demonstrate which pipeline components produce measurable benefit. The following configurations should be compared:

1. Median-only preprocessing.
2. Kalman filtering without RTS smoothing.
3. Kalman filtering plus RTS smoothing without despiking.
4. Full pipeline.

The comparison should report completion rate, raw-to-smoothed trajectory deviation, RMS jerk, smoothness index, path efficiency, and variability of key metrics across sessions.

**Table 3. Ablation-study results to be completed before submission.**

| Pipeline variant | Completion rate | Mean trajectory deviation | RMS jerk | Smoothness index | Comment |
|---|---:|---:|---:|---:|---|
| Median only | [to be completed] | [to be completed] | [to be completed] | [to be completed] | baseline |
| Kalman without RTS | [to be completed] | [to be completed] | [to be completed] | [to be completed] | forward filtering |
| Kalman + RTS without despiking | [to be completed] | [to be completed] | [to be completed] | [to be completed] | offline smoothing |
| Full pipeline | [to be completed] | [to be completed] | [to be completed] | [to be completed] | proposed workflow |

### 4.16 Repeatability and Agreement Statistics

For each metric, repeatability is summarized using mean, standard deviation, coefficient of variation, and repeatability coefficient:

\[
CV = \frac{SD}{|\bar{x}|}\times 100\%,
\]

\[
RC = 1.96\sqrt{2}SD.
\]

Formal agreement statistics should be added when repeated measurements are grouped by athlete or trial condition. The recommended model is ICC(2,1) or ICC(A,1), depending on whether the design treats raters/conditions as random or fixed. Bland-Altman limits of agreement should be reported for two or three primary metrics:

\[
LoA = \bar{d} \pm 1.96SD_d,
\]

where \(d\) is the difference between paired repeated or reference measurements. These statistics cannot be computed correctly from the currently available aggregate session table unless repeated-measure grouping or reference-pair structure is provided.

## 5. Results

### 5.1 Processing Completion

The scientific filtering profile processed all 71 discovered sessions successfully. No failed sessions were reported in the available reliability output.

**Table 4. Processing completion.**

| Indicator | Value |
|---|---:|
| Total discovered sessions | 71 |
| Successfully processed sessions | 71 |
| Failed sessions | 0 |
| Completion rate | 100% |
| Filtering profile | scientific |

### 5.2 Repeatability Across Sessions

Repeatability statistics were computed for 11 exported metrics across 71 sessions. The smoothness index had the lowest CV among the reported metrics (21.52%), followed by path efficiency (38.17%). Maximum speed and downswing peak speed had identical summary values in the current exports, which indicates that the maximum speed occurred during the downswing in the processed sessions. Higher-order derivative and phase metrics showed substantially larger variability.

**Table 5. Repeatability statistics across 71 sessions.**

| Metric | Mean | SD | CV, % | RC | Interpretation |
|---|---:|---:|---:|---:|---|
| Smoothness index | -5.882 | 1.266 | 21.52 | 3.508 | most stable reported metric |
| Path efficiency | 0.726 | 0.277 | 38.17 | 0.769 | useful path-quality indicator |
| Max speed, m/s | 8.184 | 9.681 | 118.28 | 26.833 | strongly affected by session heterogeneity |
| Downswing peak speed, m/s | 8.184 | 9.681 | 118.28 | 26.833 | same as maximum speed in current exports |
| Swing tempo | 0.604 | 0.777 | 128.63 | 2.154 | sensitive to phase detection and session type |
| Curvature RMS | 1063.382 | 1686.764 | 158.62 | 4675.470 | sensitive to local geometry |
| Downswing duration, s | 1.676 | 2.812 | 167.72 | 7.793 | heterogeneous timing |
| Max angular velocity, rad/s | 10.169 | 19.601 | 192.76 | 54.331 | derivative-sensitive |
| Max acceleration, m/s² | 185.158 | 400.392 | 216.24 | 1109.831 | exploratory under heterogeneous capture |
| Backswing duration, s | 0.673 | 1.517 | 225.35 | 4.206 | sensitive to phase definition |
| Backswing peak speed, m/s | 1.065 | 5.533 | 519.31 | 15.337 | least stable reported metric |

[Insert Figure 3: Session-Wise Distribution of Selected Swing Metrics]

### 5.3 Raw-versus-Smoothed Trajectory Deviation

A representative exported trajectory was evaluated by comparing the raw and final exported tip positions. This analysis does not establish ground-truth accuracy, but it quantifies the deviation introduced by the filtering and smoothing workflow.

**Table 6. Raw-versus-smoothed trajectory deviation for representative exported swing.**

| Indicator | Value |
|---|---:|
| Valid samples | 141 |
| Mean deviation | 0.053 m |
| Median deviation | 0.050 m |
| 90th percentile deviation | 0.063 m |
| 95th percentile deviation | 0.067 m |
| 99th percentile deviation | 0.069 m |
| Maximum deviation | 0.139 m |
| RMS jerk | 1446.560 |
| Frames with deviation > 3 cm | 141 |
| Frames with deviation > 5 cm | 51 |

The mean deviation indicates that the final trajectory is not simply a cosmetic overlay of the raw path; it meaningfully regularizes the signal. The high number of frames above 3 cm also shows why raw-versus-smoothed deviation should be interpreted jointly with external validation. A smoothed trajectory can be more biomechanically usable than raw landmarks, but external reference data are required to determine whether it is more accurate.

[Insert Figure 4: Raw vs Filtered vs Smoothed Stick-Tip Trajectory]

### 5.4 Interpretation of Metric Stability

The repeatability ranking suggests that movement-quality and path-shape metrics are more robust than peak derivative metrics in heterogeneous video recordings. Smoothness index and path efficiency summarize global movement properties and are less dependent on a single frame. In contrast, maximum acceleration, maximum angular velocity, and local curvature are affected by derivative amplification, short landmark errors, phase-boundary uncertainty, and frame-rate differences.

Therefore, the recommended primary endpoints for current heterogeneous recordings are:

1. Smoothness index.
2. Path efficiency.
3. Phase-level peak speed only when frame rate and scale are controlled.

The recommended exploratory endpoints are:

1. Maximum acceleration.
2. Maximum angular velocity.
3. Backswing peak speed.
4. Curvature RMS under uncontrolled camera conditions.

### 5.5 Results Still Required by Mentor Review

The mentor review requested external validation, sensitivity analysis, ablation comparison, and formal agreement statistics. The available data do not contain those completed experiments. To avoid inventing results, the final manuscript must add the completed values in Tables 1-3 and the ICC/Bland-Altman subsection after the required annotations and reruns are performed.

## 6. Discussion

The study demonstrates that a coordinated markerless pipeline can process heterogeneous golf-stick swing recordings and export interpretable motion metrics. The strongest completed evidence is the 100% processing completion across 71 sessions and the repeatability ranking showing that smoothness and path-efficiency metrics are more stable than higher-order derivative peaks. This supports the practical use of the pipeline for exploratory coaching feedback, movement-quality screening, and VR-oriented analysis where repeated low-cost measurement is valuable.

The central methodological point is that the reliability of the output depends on the entire processing chain. Median filtering reduces isolated landmark spikes; the Kalman filter provides a physically interpretable forward state estimate; confidence-weighted measurement noise can reduce the influence of uncertain landmarks; residual gating prevents implausible updates; RTS smoothing improves offline estimates by using future observations; despiking and bounded polynomial smoothing reduce remaining local artifacts; and dynamic scale calibration controls changes caused by apparent stick length.

The results also show why raw peak metrics should not be overinterpreted. Acceleration and angular velocity are derivatives of already noisy measurements, so their maxima are sensitive to frame timing, landmark jitter, outliers, and local smoothing choices. A single erroneous frame can dominate the reported peak. This explains why maximum acceleration had a CV above 200%, while smoothness and path efficiency were comparatively stable. For Scopus-level publication, the manuscript should present acceleration peaks as secondary or exploratory unless controlled recordings and external validation demonstrate acceptable error.

The mentor’s recommendation to add external validation is essential. Repeatability answers whether measurements are stable across processed sessions; it does not answer whether they are correct relative to an independent reference. A reference-validation subset with manual event labels and trajectory control points would allow the manuscript to report timing error, geometric trajectory error, and scalar metric error. This would transform the work from an implementation robustness study into a validated measurement-method study.

Sensitivity analysis is equally important. The introduction identifies variable frame rate, landmark loss, and camera-geometry changes as practical problems. The results section should therefore quantify how metrics change when frame rate is reduced, landmarks are dropped, or scale is perturbed. This would allow the paper to state not only that the pipeline works, but also the conditions under which it remains reliable.

The ablation study will clarify the contribution of each processing block. Without ablation, the full pipeline can be described but not causally justified. Comparing median-only, Kalman-only, Kalman+RTS, and full-pipeline variants would show whether each stage reduces trajectory deviation, jerk, failed sessions, or metric variability.

Several limitations remain. First, the pipeline uses monocular 2D data, so out-of-plane motion cannot be fully resolved. Second, dynamic scale calibration based on projected stick length is affected by perspective and foreshortening. Third, the available dataset description does not yet report athlete count, repetition structure, camera setup, or quality classes. Fourth, formal agreement statistics cannot be computed without paired repeated-measure or reference data. Fifth, the current manuscript must be aligned with the official journal requirements after the URL is provided.

## 7. Conclusions

This study presents a reproducible markerless golf-stick motion-analysis workflow that integrates landmark extraction, median pre-filtering, Kalman tracking, RTS smoothing, despiking, bounded local polynomial smoothing, dynamic scale calibration, phase segmentation, and repeatability assessment. The pipeline processed all 71 available sessions successfully.

The completed repeatability analysis indicates that smoothness index and path efficiency are the most stable reported metrics under heterogeneous recording conditions, whereas acceleration peaks, angular-velocity peaks, and some phase-specific speed metrics are substantially more variable. This supports the use of smoothness and path-based indicators as primary endpoints in the current dataset and the interpretation of high-order derivative peaks as exploratory metrics unless further controlled validation is performed.

The main scientific contribution is a coordinated measurement workflow rather than a new isolated filter. The revised method provides a structured basis for VR training and sport-biomechanics applications, but final publication should include the requested reference-validation results, sensitivity-analysis results, ablation comparison, and formal ICC/Bland-Altman agreement statistics.

[Insert Figure 5: Comparative Summary of Raw, Filtered, and Smoothed Metrics]

## Conflict of Interest

The author declares no conflict of interest related to this research, whether financial, personal, institutional, or otherwise, that could influence the research or its interpretation.

## Funding

The study was performed without external financial support.

## Data Availability

The manuscript uses processed session-level metrics and exported trajectory data generated by the described software pipeline. Additional processed datasets, scripts, and supplementary figures should be made available on reasonable request or deposited in a repository before submission, subject to participant privacy and institutional requirements.

## Use of Artificial Intelligence Tools

Language-level AI assistance was used during manuscript revision. The algorithms, code, parameter choices, numerical results, and final scientific interpretations must be verified by the author against reproducible outputs before submission.

## Author Contributions

Ivan Suniuk: conceptualization, methodology, software, data curation, validation planning, visualization, formal analysis, writing-original draft, and writing-revision.

## References

1. Winter, D. A. Biomechanics and Motor Control of Human Movement. 4th ed. Wiley; 2009.
2. Bartlett, R. Introduction to Sports Biomechanics: Analysing Human Movement Patterns. Routledge; 2007.
3. Cao, Z., Hidalgo, G., Simon, T., Wei, S. E., Sheikh, Y. OpenPose: Realtime multi-person 2D pose estimation using part affinity fields. IEEE Transactions on Pattern Analysis and Machine Intelligence. 2021;43(1):172-186.
4. Bazarevsky, V., Grishchenko, I., Raveendran, K., Zhu, T., Zhang, F., Grundmann, M. BlazePose: On-device real-time body pose tracking. Proceedings of the CVPR Workshop on Computer Vision for Augmented and Virtual Reality; 2020.
5. Kalman, R. E. A new approach to linear filtering and prediction problems. Journal of Basic Engineering. 1960;82(1):35-45.
6. Welch, G., Bishop, G. An Introduction to the Kalman Filter. University of North Carolina at Chapel Hill; 2006.
7. Rauch, H. E., Tung, F., Striebel, C. T. Maximum likelihood estimates of linear dynamic systems. AIAA Journal. 1965;3(8):1445-1450.
8. Savitzky, A., Golay, M. J. E. Smoothing and differentiation of data by simplified least squares procedures. Analytical Chemistry. 1964;36(8):1627-1639.
9. Hume, P. A., Keogh, J., Reid, D. The role of biomechanics in maximizing distance and accuracy of golf shots. Sports Medicine. 2005;35(5):429-449.
10. Nesbit, S. M., Serrano, M. Work and power analysis of the golf swing. Journal of Sports Science and Medicine. 2005;4:520-533.
11. McLaughlin, J. J., Best, R. J. Three-dimensional kinematic analysis of the golf swing. In: Cochran, A. J., Farrally, M. R., editors. Science and Golf II. E & FN Spon; 1994. p. 91-96.
12. van der Kruk, E., Reijne, M. M. Accuracy of human motion capture systems for sport applications: State-of-the-art review. European Journal of Sport Science. 2018;18(6):806-819.
13. Balasubramanian, S., Melendez-Calderon, A., Roby-Brami, A., Burdet, E. On the analysis of movement smoothness. Journal of NeuroEngineering and Rehabilitation. 2015;12:112.
14. Atkinson, G., Nevill, A. M. Statistical methods for assessing measurement error (reliability) in variables relevant to sports medicine. Sports Medicine. 1998;26(4):217-238.
15. Bland, J. M., Altman, D. G. Statistical methods for assessing agreement between two methods of clinical measurement. Lancet. 1986;327(8476):307-310.

## Author Information

Ivan Suniuk  
Department/Organization: [to be completed]  
Address: [to be completed]  
E-mail: [to be completed]  
ORCID ID: [to be completed]  
Scopus ID: [to be completed if available]  
Researcher ID: [to be completed if available]  
ResearchGate: [to be completed if available]

## Major Improvements Made

1. Reframed the article from an implementation description into a measurement-method manuscript.
2. Rewrote the abstract with problem, method, dataset, completed results, interpretation, and limitations.
3. Strengthened the introduction with a clearer problem statement and relevance to VR and sport biomechanics.
4. Added technical detail for landmark extraction, raw/filtered/smoothed trajectory definitions, Kalman filtering, confidence-weighted measurement noise, RTS smoothing, despiking, bounded polynomial smoothing, and dynamic scaling.
5. Added formulas for state transition, Kalman update, RTS smoother, velocity, acceleration, jerk, angular velocity, path efficiency, curvature, CV, RC, and Bland-Altman limits of agreement.
6. Integrated the mentor’s requests for reference validation, sensitivity analysis, ablation study, ICC, Bland-Altman agreement, uncertainty modeling, dataset description, and terminology cleanup.
7. Preserved existing numeric results and avoided inventing unavailable validation or sensitivity results.
8. Added required placeholders for figures and result tables that must be filled after additional experiments.
9. Reclassified stable metrics as primary endpoints and derivative peaks as exploratory under heterogeneous recordings.
10. Added a clear limitation statement explaining what remains necessary before final submission.
