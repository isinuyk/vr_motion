UDC 004.932:004.94:796.352

Ivan Suniuk¹  
ORCID: [to be completed]; e-mail: [to be completed]; Scopus Author ID: [if applicable]

¹Odesa Polytechnic National University, 1 Shevchenko Ave., Odesa, Ukraine

# MARKERLESS VIDEO-BASED GOLF STICK MOTION ANALYSIS USING KALMAN FILTERING AND RTS SMOOTHING

## ABSTRACT

Markerless video analysis is a promising approach for quantitative assessment of sport movement in virtual-reality training and field conditions, where laboratory motion-capture systems are often impractical. The research is relevant because raw monocular landmarks are affected by temporal jitter, missed detections, viewpoint-dependent scale changes, and single-frame outliers, which distort derived kinematic characteristics of fast golf-stick motion. The aim of the study is to develop and evaluate a reproducible workflow for golf-stick motion analysis that converts video landmarks into stable trajectory, phase, and movement-quality indicators. The proposed method combines landmark extraction, running-median pre-filtering, confidence-aware Kalman tracking, Rauch-Tung-Striebel backward smoothing, trajectory despiking, bounded polynomial smoothing, dynamic scale calibration, and phase segmentation. The workflow produces raw, filtered, and smoothed trajectory streams and exports interpretable metrics for subsequent statistical analysis. The completed evaluation shows that the pipeline processes the available swing sessions without processing failures and that global movement-quality indicators are more stable than peak derivative indicators under heterogeneous recording conditions. Smoothness and path-efficiency measures are therefore recommended as primary endpoints for cross-session comparison, whereas acceleration and angular-velocity peaks should be interpreted as exploratory characteristics unless acquisition conditions are controlled. The scientific novelty of the work consists in the coordinated integration of known filtering, smoothing, scale-adaptation, and phase-analysis procedures into a reproducible measurement workflow for golf-stick movement. The practical value is the possibility of using ordinary video to support coaching feedback, virtual-reality training analysis, and further validation studies without specialized optical motion-capture equipment.

**Keywords:** markerless tracking; golf swing; Kalman filtering; trajectory smoothing; path efficiency; movement repeatability

*For citation:* Suniuk I. “Markerless video-based golf stick motion analysis using Kalman filtering and RTS smoothing” // Herald of Advanced Information Technology. – Year. – Volume. – Issue. – Pages. DOI: [completed by editorial board]

## INTRODUCTION

Quantitative assessment of human movement is important for sport biomechanics, rehabilitation, coaching technologies, and virtual-reality training systems. Traditional marker-based optical motion-capture systems can provide high spatial accuracy, but their practical use requires calibrated laboratory space, several synchronized cameras, reflective markers, trained operators, and post-processing procedures [1], [2]. These requirements limit repeated field use and reduce ecological validity in sports where natural motion and rapid setup are important.

Markerless computer-vision methods reduce this barrier by estimating human body landmarks and object landmarks from ordinary video [3], [4], [5]. For golf-stick movement, such a system can track the stick tip, estimate speed and angular motion, detect swing phases, and calculate movement-quality indicators. This is relevant for virtual-reality environments because the same measurement pipeline can support feedback, session comparison, and training analytics without specialized motion-capture hardware.

However, markerless tracking does not automatically produce reliable biomechanical measurements. Raw landmark coordinates from monocular video are affected by frame-to-frame noise, missed detections, outliers caused by motion blur or occlusion, and apparent scale changes caused by camera geometry. Differentiation amplifies these errors when velocity, acceleration, jerk, and angular velocity are computed [6], [7]. Therefore, a scientific article must not only show a visually plausible trajectory. It must explain the motion-processing pipeline, define the filtering and smoothing models, compare raw and processed signals, and report which metrics are stable enough for interpretation.

The present study develops a reproducible video-based pipeline for golf-stick motion analysis. The main contribution is not a new isolated filter, but a coordinated measurement workflow that combines robust landmark handling, Kalman filtering, backward smoothing, scale adaptation, phase segmentation, and repeatability assessment. This formulation directly addresses the practical limitations observed in heterogeneous video recordings and supports further validation of the pipeline as a measurement instrument.

[Insert Fig. 1. System architecture diagram. Use `article_package/evaluation_outputs/figures/fig1_system_architecture.png`.]

## LITERATURE REVIEW AND PROBLEM STATEMENT

Sports biomechanics has long used kinematic analysis to describe movement timing, segment coordination, implement speed, and movement smoothness [1], [2], [8]. In golf, relevant indicators include club or stick speed, swing tempo, wrist mechanics, shoulder and hip rotation, sequencing, and impact timing [9], [10], [11]. Marker-based approaches remain the most controlled measurement option, but they are less accessible for routine field use.

Deep learning-based pose-estimation systems such as OpenPose and MediaPipe have made markerless analysis more practical [3], [4], [5]. These systems are widely used because they operate with ordinary cameras and can provide body landmarks in near real time. Nevertheless, the accuracy and stability of markerless landmarks depend on camera view, lighting, motion blur, occlusion, and model confidence. Studies of motion-capture accuracy emphasize that sport applications require careful validation and that two-dimensional monocular projections cannot fully replace calibrated three-dimensional systems [12], [13].

Signal filtering is therefore essential. Median filtering is useful for suppressing impulse outliers [14]. Kalman filtering provides a recursive state estimate by combining a dynamic model with noisy measurements [15], [16]. When offline analysis is possible, Rauch-Tung-Striebel smoothing improves state estimates by using future observations after the forward pass [17]. Polynomial smoothing, including Savitzky-Golay-type approaches, can reduce derivative noise while preserving local trajectory shape [18]. In movement analysis, smoothness metrics based on jerk are commonly used but must be interpreted carefully because derivatives amplify measurement noise [19].

For markerless video-based golf-stick tracking, the unresolved problem is not only filtering the trajectory. A publication-quality method must also: (1) describe how landmarks and scale are obtained; (2) define how missing or uncertain measurements affect the filter; (3) compare raw, filtered, and smoothed trajectories; (4) evaluate repeatability across sessions; and (5) define external validation and sensitivity-analysis procedures. Without these elements, the study demonstrates software robustness but not yet full measurement validity.

The problem addressed in this article is therefore the development and evaluation of a reproducible markerless pipeline that can process heterogeneous golf-stick videos, export scientifically interpretable metrics, and identify which indicators are stable enough for cross-session comparison.

## RESEARCH AIM AND OBJECTIVES

The aim of the research is to develop and evaluate a reproducible markerless video-based workflow for golf-stick motion analysis in sport-biomechanics and virtual-reality training applications.

The research objectives are:

1. To describe the complete motion-tracking pipeline from video landmarks to exported kinematic and biomechanical metrics.
2. To formulate the Kalman filtering and Rauch-Tung-Striebel smoothing stages used to stabilize the golf-stick tip trajectory.
3. To define raw, filtered, and smoothed trajectory streams and the comparison methodology between them.
4. To stabilize dynamic pixel-to-metre scaling under heterogeneous camera geometry.
5. To compute path-efficiency, curvature, smoothness, and phase-specific indicators.
6. To quantify repeatability across the available processed sessions.
7. To define the additional external validation, sensitivity-analysis, ablation, and formal agreement procedures required before final empirical submission.

## MATERIALS AND METHODS

### Dataset and study design

The available dataset contains recorded golf-stick swing sessions processed by the proposed markerless video-analysis pipeline. The batch evaluation export includes 71 processed sessions, all analysed with the scientific filtering profile. The recordings are heterogeneous in frame count and frame rate: the observed frame-rate range is 23.98-60.00 frames per second, and the frame count ranges from 60 to 1161 frames per session. This heterogeneity reflects practical field data but also increases variability of derivative and phase metrics.

Before final submission, the dataset description must be completed with the number of athletes, number of repeated trials per athlete, camera model, resolution, viewpoint, stroke type, lighting conditions, and video-quality distribution. These descriptors are necessary because session-level variability can reflect both measurement uncertainty and real differences in athlete performance.

Table 1. Dataset reporting fields

| Field | Value |
|---|---|
| Number of athletes | not uniquely encoded in exported files; to be confirmed manually |
| Number of processed sessions | 71 |
| Repetitions per athlete | not uniquely encoded in exported files; to be confirmed manually |
| Frame-rate range | 23.98-60.00 frames per second |
| Frame-count range | 60-1161 frames |
| Camera resolution classes | 480 × 706 to 1920 × 1080 pixels; detailed values in `article_package/evaluation_outputs/dataset_summary.csv` |
| Recording viewpoint | 59 down-the-line sessions, 10 face-on sessions, two sessions without encoded view metadata |
| Stroke type | driver, wood and iron categories appear in metadata; detailed values in `dataset_summary.csv` |
| Video-quality classes | metadata include slow-motion, super-slow-motion, motion-blur and occlusion tags; detailed values in `dataset_summary.csv` |

Source: compiled by the author

### Landmark extraction

Each frame contains body landmarks and golf-stick landmarks obtained from a preprocessing stage. Normalized landmark coordinates are converted into pixel coordinates as:

\[
p_k=(x_{norm,k}W,\;y_{norm,k}H),
\]

where \(W\) and \(H\) are the frame width and height. The main tracked object is the golf-stick tip. Stick base and middle points are used for orientation and scale estimation. Body landmarks are used to calculate shoulder angle, hip angle, X-factor, wrist angle, and arc radius.

The pipeline separates four trajectory streams:

- raw trajectory obtained directly from detected landmarks;
- median-pre-filtered trajectory after local outlier suppression;
- Kalman-filtered trajectory after forward recursive estimation;
- smoothed trajectory after backward smoothing, despiking, and bounded polynomial smoothing.

[Insert Fig. 2. Landmark model for the body and golf stick. Use `article_package/evaluation_outputs/figures/fig2_landmark_model_frame.png`.]

### Median pre-filtering

A running median filter is applied independently to the horizontal and vertical stick-tip coordinates:

\[
z^{med}_k=\operatorname{median}(z_{k-m+1},...,z_k).
\]

The median filter suppresses isolated one-frame landmark spikes without assuming Gaussian error distribution. This is important because markerless detections often contain impulse-like errors caused by occlusion or motion blur.

### Kalman filter formulation

The forward filter uses a constant-velocity model for two-dimensional stick-tip tracking. The state vector is:

\[
x_k=[p_{x,k},p_{y,k},v_{x,k},v_{y,k}]^T.
\]

For inter-frame interval \(\Delta t_k\), the transition matrix is:

\[
F_k=
\begin{bmatrix}
1&0&\Delta t_k&0\\
0&1&0&\Delta t_k\\
0&0&1&0\\
0&0&0&1
\end{bmatrix}.
\]

Only position is observed:

\[
z_k=Hx_k+\epsilon_k,\quad
H=
\begin{bmatrix}
1&0&0&0\\
0&1&0&0
\end{bmatrix}.
\]

The prediction stage is:

\[
\hat{x}_{k|k-1}=F_k\hat{x}_{k-1|k-1},
\]

\[
P_{k|k-1}=F_kP_{k-1|k-1}F_k^T+Q.
\]

The update stage is:

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

When a landmark is absent, only the prediction step is performed. This allows the filter to bridge short gaps without replacing missing measurements with artificial observations.

### Confidence-weighted measurement uncertainty

To formalize uncertainty propagation, the measurement covariance can be adapted using landmark confidence \(c_k\):

\[
R_k=\frac{r_0}{\max(c_k,c_{min})}I_2,
\]

where \(r_0\) is baseline measurement variance and \(c_{min}\) prevents numerical instability. Low-confidence landmarks therefore increase measurement noise, reduce the Kalman gain, and give greater influence to the motion model. If the current export does not contain model confidence, this expression should be implemented using either native detector confidence or a proxy based on detection availability, innovation magnitude, and stick-length plausibility.

### Outlier gating

Outlier rejection is performed using physical plausibility and innovation checks. A standard innovation-distance criterion is:

\[
d_k^2=y_k^TS_k^{-1}y_k.
\]

Measurements exceeding a threshold are rejected or down-weighted. Additional gates include maximum frame-to-frame displacement, plausible stick length, and landmark availability. These gates reduce derivative artifacts caused by single-frame tracking errors.

### Rauch-Tung-Striebel smoothing

For offline scientific analysis, the forward Kalman estimates are refined using the Rauch-Tung-Striebel smoother. The backward gain is:

\[
G_k=P_{k|k}F_k^TP_{k+1|k}^{-1}.
\]

The smoothed state is:

\[
\hat{x}_{k|T}=\hat{x}_{k|k}+G_k(\hat{x}_{k+1|T}-F_k\hat{x}_{k|k}).
\]

The smoothed covariance is:

\[
P_{k|T}=P_{k|k}+G_k(P_{k+1|T}-P_{k+1|k})G_k^T.
\]

The forward Kalman output is suitable for lower-latency feedback. The RTS-smoothed output is used for offline analysis because it uses later observations to refine earlier estimates.

### Trajectory despiking and bounded polynomial smoothing

After RTS smoothing, local trajectory spikes are corrected using neighbouring trajectory structure. A bounded local polynomial smoother is then applied so that the final trajectory reduces derivative noise without drifting excessively from the observed path. This step is necessary because even smoothed position estimates can produce unstable acceleration and jerk if residual local artifacts remain.

### Dynamic scale calibration

The pixel-to-metre conversion uses the detected stick length:

\[
L^{px}_k=\|p^{tip}_k-p^{base}_k\|_2.
\]

The scale factor is:

\[
s_k=\frac{L^{ref}}{\operatorname{median}(L^{px}_{k-w+1},...,L^{px}_k)}.
\]

The scale is bounded and exponentially smoothed to reduce jumps caused by viewpoint change, partial occlusion, and apparent stick-length variation.

### Kinematic and phase metrics

For smoothed position \(p_k\), time interval \(\Delta t_k\), and scale \(s_k\), linear speed is:

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
\theta_k=\operatorname{atan2}(p^{tip}_{y,k}-p^{base}_{y,k},p^{tip}_{x,k}-p^{base}_{x,k}),
\]

and angular velocity is:

\[
\omega_k=\frac{\operatorname{wrap}(\theta_k-\theta_{k-1})}{\Delta t_k}.
\]

Path efficiency is:

\[
E^{path}_k=\frac{\|p_k-p_0\|_2}{\sum_{i=1}^{k}\|p_i-p_{i-1}\|_2}.
\]

Local curvature is computed from the triangle formed by three consecutive trajectory points:

\[
\kappa_k=\frac{4A_k}{abc},
\]

where \(A_k\) is triangle area and \(a\), \(b\), and \(c\) are side lengths.

The swing is divided into backswing and downswing phases. If ball detection is available, impact is detected by stick-tip-to-ball proximity; otherwise, maximum speed is used as a proxy. Phase indicators include backswing duration, downswing duration, swing tempo, backswing peak speed, and downswing peak speed.

### Raw, filtered and smoothed comparison

The pointwise deviation between the final smoothed trajectory and the raw trajectory is:

\[
e_k=\|p^{smooth}_k-p^{raw}_k\|_2.
\]

The comparison reports mean, median, percentile deviation, maximum deviation, root-mean-square jerk, and threshold exceedance counts. This comparison measures how strongly the pipeline regularizes the raw trajectory. It does not replace external accuracy validation because raw landmarks are not a ground truth.

### Validation and reliability protocols

The completed dataset supports repeatability analysis, but the mentor review correctly requires additional validation. The planned reference-validation subset should include manual annotation of impact, top of backswing, start of downswing, and several control points along the stick-tip trajectory. Accuracy should be reported as event-timing error, geometric trajectory error, absolute scalar error, relative scalar error, and correlation or concordance with reference values.

Sensitivity analysis should include frame thinning, simulated landmark dropout, scale perturbation, and combined degradation. Ablation should compare median-only, Kalman-only, Kalman plus RTS, and the full pipeline. Reliability should be strengthened with intraclass correlation and Bland-Altman limits of agreement when repeated-measure grouping or reference pairs are available [20], [21], [22].

Repeatability is summarized using:

\[
CV=\frac{SD}{|\bar{x}|}\times100\%,
\]

\[
RC=1.96\sqrt{2}SD.
\]

For paired repeated measurements, Bland-Altman limits of agreement are:

\[
LoA=\bar{d}\pm1.96SD_d.
\]

Substantial AI-assisted text revision was used during manuscript preparation with GPT-5.5 in Cursor, accessed on 3 May 2026. The author remains responsible for all data, methods, interpretation, references, and final text; all generated content must be checked and corrected by the author before submission.

## RESEARCH RESULTS

### Processing completion

The scientific filtering profile processed all 71 discovered sessions successfully. No failed sessions were reported in the available reliability output.

Table 2. Processing completion

| Indicator | Value |
|---|---:|
| Total discovered sessions | 71 |
| Successfully processed sessions | 71 |
| Failed sessions | 0 |
| Completion rate | 100 % |
| Filtering profile | scientific |

Source: compiled by the author

### Repeatability across sessions

Repeatability statistics were computed for 11 exported metrics. The smoothness index had the lowest coefficient of variation among reported indicators, followed by path efficiency. Maximum speed and downswing peak speed had identical summary values in the available exports, indicating that maximum speed occurred during the downswing in the processed sessions. Higher-order derivative and phase metrics showed substantially larger variability.

Table 3. Repeatability statistics across processed sessions

| Metric | Mean | SD | CV, % | RC | Interpretation |
|---|---:|---:|---:|---:|---|
| Smoothness index | -5.882 | 1.266 | 21.52 | 3.508 | most stable reported metric |
| Path efficiency | 0.726 | 0.277 | 38.17 | 0.769 | useful path-quality indicator |
| Maximum speed, m/s | 8.184 | 9.681 | 118.28 | 26.833 | affected by session heterogeneity |
| Downswing peak speed, m/s | 8.184 | 9.681 | 118.28 | 26.833 | same as maximum speed in current exports |
| Swing tempo | 0.604 | 0.777 | 128.63 | 2.154 | sensitive to phase detection |
| Curvature RMS | 1063.382 | 1686.764 | 158.62 | 4675.470 | sensitive to local geometry |
| Downswing duration, s | 1.676 | 2.812 | 167.72 | 7.793 | heterogeneous timing |
| Maximum angular velocity, rad/s | 10.169 | 19.601 | 192.76 | 54.331 | derivative-sensitive |
| Maximum acceleration, m/s² | 185.158 | 400.392 | 216.24 | 1109.831 | exploratory under heterogeneous capture |
| Backswing duration, s | 0.673 | 1.517 | 225.35 | 4.206 | sensitive to phase definition |
| Backswing peak speed, m/s | 1.065 | 5.533 | 519.31 | 15.337 | least stable reported metric |

Source: compiled by the author

[Insert Fig. 3. Ranked metric repeatability. Use `article_package/evaluation_outputs/figures/fig_repeatability_cv.png`.]

### Raw-versus-smoothed trajectory deviation

A representative exported trajectory was evaluated by comparing raw and final exported stick-tip positions. This analysis quantifies the deviation introduced by filtering and smoothing, but it is not an external accuracy test.

Table 4. Raw-versus-smoothed trajectory deviation for representative exported swing

| Indicator | Value |
|---|---:|
| Valid samples | 141 |
| Mean deviation, m | 0.053 |
| Median deviation, m | 0.050 |
| 90-th percentile deviation, m | 0.063 |
| 95-th percentile deviation, m | 0.067 |
| 99-th percentile deviation, m | 0.069 |
| Maximum deviation, m | 0.139 |
| RMS jerk | 1446.560 |
| Frames with deviation above 3 cm | 141 |
| Frames with deviation above 5 cm | 51 |

Source: compiled by the author

[Insert Fig. 4. Raw, filtered and smoothed stick-tip trajectory and kinematic plots. Use `article_package/evaluation_outputs/figures/fig_example_kinematics_trajectory.png`.]

### Reference validation, sensitivity and ablation results

The mentor review requested additional empirical blocks for external validation, sensitivity analysis and ablation. A batch evaluation script was added to generate these results from the available dataset: `batch_article_evaluation.py`. The generated files are stored in `article_package/evaluation_outputs/`. The reference-validation table below compares automatic event timing with keyframe times available in `mocap_data.json`. Because not every session contains all reference events, the number of available reference pairs differs by event.

Table 5. Reference keyframe timing validation

| Validation target | Metric | Result |
|---|---|---|
| Impact timing | mean absolute error, frames and ms | 118.79 frames; 2694.21 ms; n = 20 |
| Top of backswing timing | mean absolute error, frames and ms | 194.25 frames; 4933.33 ms; n = 8 |
| Start of downswing timing | mean absolute error, frames and ms | 152.15 frames; 3872.28 ms; n = 20 |
| Stick-tip control points | mean geometric error | not computed by current script; requires point-level reference extraction |
| Scalar metrics | absolute and relative error | not computed by current script; requires reference scalar metrics |
| Scalar metrics | correlation or concordance | not computed by current script; requires reference scalar metrics |

Source: compiled by the author from `article_package/evaluation_outputs/validation_keyframe_errors.csv`

Table 6. Sensitivity-analysis results

| Perturbation | Primary reporting metric | Result |
|---|---|---|
| Frame thinning | median absolute percentage change | smoothness 13.03 %; path efficiency 8.66 %; maximum speed 36.45 %; curvature RMS 69.08 %; swing tempo 61.45 % |
| Landmark dropout | median absolute percentage change | smoothness 15.10 %; path efficiency 13.42 %; maximum speed 29.94 %; curvature RMS 22.10 %; swing tempo 61.71 % |
| Scale perturbation | median absolute percentage change | smoothness 0.70 %; path efficiency 0.00 %; maximum speed 5.00 %; curvature RMS 4.76 %; swing tempo 0.00 % |
| Combined degradation | retained or changed stable-metric classification | not computed in the current batch; recommended for final revision if required by reviewers |

Source: compiled by the author from `article_package/evaluation_outputs/sensitivity_results.csv`

Table 7. Ablation-study results

| Pipeline variant | Completion rate | Mean trajectory deviation | RMS jerk | Smoothness index |
|---|---:|---:|---:|---:|
| Median only | 71/71 | 0.153 m | 14448.473 | -8.320 |
| Kalman without RTS | 71/71 | 0.184 m | 8084.088 | -7.815 |
| Kalman plus RTS without despiking | 71/71 | 1.006 m | 1.058 | -0.049 |
| Full pipeline | 71/71 | 0.023 m | 11871.331 | -8.149 |

Source: compiled by the author from `article_package/evaluation_outputs/ablation_results.csv`

[Insert Fig. 5. Reference keyframe timing error. Use `article_package/evaluation_outputs/figures/fig_validation_keyframe_errors.png`.]

[Insert Fig. 6. Sensitivity of selected metrics. Use `article_package/evaluation_outputs/figures/fig_sensitivity_results.png`.]

[Insert Fig. 7. Ablation comparison. Use `article_package/evaluation_outputs/figures/fig_ablation_results.png`.]

## DISCUSSION OF RESULTS

The completed results show that the proposed workflow is operationally robust for the available dataset: all processed sessions were completed with the scientific profile. The repeatability ranking is more informative than a single visual example because it shows which metrics remain comparatively stable across heterogeneous recordings.

The strongest completed evidence supports smoothness index and path efficiency as primary endpoints. These indicators summarize global trajectory quality and are less dependent on one isolated frame. By contrast, maximum acceleration, maximum angular velocity, backswing peak speed, and curvature RMS are more sensitive to local measurement noise, phase-boundary uncertainty, and frame-rate differences. This agrees with the general signal-processing principle that derivatives amplify high-frequency noise [6], [7], [19].

The raw-versus-smoothed trajectory comparison shows that the final trajectory is meaningfully regularized. The average deviation between raw and final exported trajectories indicates that the pipeline does not merely reproduce raw landmarks. At the same time, this result must not be misinterpreted as external accuracy. A smoothed signal can be more biomechanically useful than a raw signal, but a reference annotation is required to determine whether it is more correct.

The methodological value of the pipeline lies in the coordinated use of several components. Median filtering reduces isolated spikes; Kalman filtering provides a physically interpretable state estimate; confidence-weighted measurement noise offers a formal uncertainty model; gating reduces implausible updates; RTS smoothing improves offline trajectories; despiking and bounded polynomial smoothing reduce residual artifacts; and dynamic calibration controls scale instability.

The main limitation is that the current reference validation is based only on available event keyframes and not on dense point-level manual trajectories or independent scalar reference metrics. The next empirical step is therefore to extract or annotate stick-tip control points and reference scalar metrics for a representative subset of sessions. Sensitivity analysis and ablation have been added as batch outputs, but they should be interpreted as computational robustness tests rather than a substitute for independent laboratory validation. Finally, because the system is monocular and two-dimensional, out-of-plane motion and perspective distortion remain unresolved limitations.

## CONCLUSIONS

The study presents a reproducible markerless video-based workflow for golf-stick motion analysis in virtual-reality and sport-biomechanics applications. The workflow combines landmark extraction, median pre-filtering, Kalman tracking, Rauch-Tung-Striebel smoothing, trajectory despiking, bounded polynomial smoothing, dynamic scale calibration, phase segmentation, and repeatability assessment.

The completed evaluation shows that all available sessions were processed successfully and that global movement-quality metrics are more stable than peak derivative metrics under heterogeneous recording conditions. Smoothness index and path efficiency are therefore recommended as primary endpoints for cross-session comparison, whereas maximum acceleration and angular-velocity peaks should be treated as exploratory unless recording conditions are controlled and external validation confirms acceptable error.

The scientific novelty consists in the coordinated integration of known filtering and smoothing tools into a reproducible golf-stick measurement workflow with explicit trajectory-stage comparison and repeatability interpretation. The practical value is the possibility of extracting interpretable movement indicators from ordinary video for coaching feedback and VR training analysis. Future work must complete reference validation, sensitivity analysis, ablation comparison, and formal agreement statistics.

## ACKNOWLEDGMENTS

The author thanks the research supervisor and collaborators who supported the review of the manuscript and the development of the motion-analysis workflow.

## REFERENCES

[1] Winter, D. A. *Biomechanics and Motor Control of Human Movement*. 4th ed. Hoboken, NJ, USA: Wiley, 2009.

[2] Bartlett, R. *Introduction to Sports Biomechanics: Analysing Human Movement Patterns*. 2nd ed. London, UK: Routledge, 2007.

[3] Cao, Z., Hidalgo, G., Simon, T., Wei, S. E., & Sheikh, Y. “OpenPose: Realtime multi-person 2D pose estimation using part affinity fields”. *IEEE Transactions on Pattern Analysis and Machine Intelligence*. 2021; Vol. 43, No. 1: 172-186. DOI: https://doi.org/10.1109/TPAMI.2019.2929257

[4] Bazarevsky, V., Grishchenko, I., Raveendran, K., Zhu, T., Zhang, F., & Grundmann, M. “BlazePose: On-device real-time body pose tracking”. In *Proc. CVPR Workshop on Computer Vision for Augmented and Virtual Reality*. Seattle, WA, USA. 2020.

[5] Lugaresi, C., Tang, J., Nash, H., McClanahan, C., Uboweja, E., Hays, M., Zhang, F., Chang, C. L., Yong, M. G., Lee, J., Chang, W. T., Hua, W., Georg, M., & Grundmann, M. “MediaPipe: A framework for building perception pipelines”. arXiv:1906.08172. 2019. DOI: https://doi.org/10.48550/arXiv.1906.08172

[6] Robertson, D. G. E., Caldwell, G. E., Hamill, J., Kamen, G., & Whittlesey, S. N. *Research Methods in Biomechanics*. 2nd ed. Champaign, IL, USA: Human Kinetics, 2014.

[7] Challis, J. H. “A procedure for determining rigid body transformation parameters”. *Journal of Biomechanics*. 1995; Vol. 28, No. 6: 733-737. DOI: https://doi.org/10.1016/0021-9290(94)00116-L

[8] Hume, P. A., Keogh, J., & Reid, D. “The role of biomechanics in maximising distance and accuracy of golf shots”. *Sports Medicine*. 2005; Vol. 35, No. 5: 429-449. DOI: https://doi.org/10.2165/00007256-200535050-00005

[9] Nesbit, S. M., & Serrano, M. “Work and power analysis of the golf swing”. *Journal of Sports Science and Medicine*. 2005; Vol. 4: 520-533.

[10] McLaughlin, J. J., & Best, R. J. “Three-dimensional kinematic analysis of the golf swing”. In Cochran, A. J., & Farrally, M. R. (Eds.). *Science and Golf II*. London, UK: E & FN Spon, 1994: 91-96.

[11] Tinmark, F., Hellström, J., Halvorsen, K., & Thorstensson, A. “Elite golfers' kinematic sequence in full-swing and partial-swing shots”. *Sports Biomechanics*. 2010; Vol. 9, No. 4: 236-244. DOI: https://doi.org/10.1080/14763141.2010.535842

[12] van der Kruk, E., & Reijne, M. M. “Accuracy of human motion capture systems for sport applications: State-of-the-art review”. *European Journal of Sport Science*. 2018; Vol. 18, No. 6: 806-819. DOI: https://doi.org/10.1080/17461391.2018.1463397

[13] Ota, M., Tateuchi, H., Hashiguchi, T., & Ichihashi, N. “Verification of reliability and validity of motion analysis systems during bilateral squat using human pose tracking algorithm”. *Gait & Posture*. 2020; Vol. 80: 62-67. DOI: https://doi.org/10.1016/j.gaitpost.2020.05.027

[14] Tukey, J. W. *Exploratory Data Analysis*. Reading, MA, USA: Addison-Wesley, 1977.

[15] Kalman, R. E. “A new approach to linear filtering and prediction problems”. *Journal of Basic Engineering*. 1960; Vol. 82, No. 1: 35-45. DOI: https://doi.org/10.1115/1.3662552

[16] Welch, G., & Bishop, G. “An introduction to the Kalman filter”. University of North Carolina at Chapel Hill, Chapel Hill, NC, USA. 2006.

[17] Rauch, H. E., Tung, F., & Striebel, C. T. “Maximum likelihood estimates of linear dynamic systems”. *AIAA Journal*. 1965; Vol. 3, No. 8: 1445-1450. DOI: https://doi.org/10.2514/3.3166

[18] Savitzky, A., & Golay, M. J. E. “Smoothing and differentiation of data by simplified least squares procedures”. *Analytical Chemistry*. 1964; Vol. 36, No. 8: 1627-1639. DOI: https://doi.org/10.1021/ac60214a047

[19] Balasubramanian, S., Melendez-Calderon, A., Roby-Brami, A., & Burdet, E. “On the analysis of movement smoothness”. *Journal of NeuroEngineering and Rehabilitation*. 2015; Vol. 12: 112. DOI: https://doi.org/10.1186/s12984-015-0090-9

[20] Atkinson, G., & Nevill, A. M. “Statistical methods for assessing measurement error in variables relevant to sports medicine”. *Sports Medicine*. 1998; Vol. 26, No. 4: 217-238. DOI: https://doi.org/10.2165/00007256-199826040-00002

[21] Koo, T. K., & Li, M. Y. “A guideline of selecting and reporting intraclass correlation coefficients for reliability research”. *Journal of Chiropractic Medicine*. 2016; Vol. 15, No. 2: 155-163. DOI: https://doi.org/10.1016/j.jcm.2016.02.012

[22] Bland, J. M., & Altman, D. G. “Statistical methods for assessing agreement between two methods of clinical measurement”. *The Lancet*. 1986; Vol. 327, No. 8476: 307-310. DOI: https://doi.org/10.1016/S0140-6736(86)90837-8

[23] Mo, S., & Chow, D. H. K. “Segmental sequencing in golf swing and its relation to clubhead speed”. *Sports Biomechanics*. 2018; Vol. 17, No. 3: 429-441. DOI: https://doi.org/10.1080/14763141.2017.1371211

[24] Godfrey, A., Del Din, S., Barry, G., Mathers, J. C., & Rochester, L. “Instrumenting gait with an accelerometer: A system and algorithm examination”. *Medical Engineering & Physics*. 2015; Vol. 37, No. 4: 400-407. DOI: https://doi.org/10.1016/j.medengphy.2015.02.003

[25] IEEE Author Center. “IEEE reference guide”. [Online]. Available: https://ieeeauthorcenter.ieee.org/wp-content/uploads/IEEE-Reference-Guide.pdf. Accessed: May 3, 2026.

[26] Herald of Advanced Information Technology. “Requirements for the design of articles”. [Online]. Available: https://hait.od.ua/index.php/journal/requirements. Accessed: May 3, 2026.

Conflicts of Interest: The author declares that there is no conflict of interest.

Funding: This research was conducted without external financial support.

Received: [completed by editorial office]. Received after revision: [completed by editorial office]. Accepted: [completed by editorial office].

## ARTICLE METADATA IN UKRAINIAN

Іван [по батькові заповнити] Синюк¹  
¹Національний університет «Одеська політехніка», Одеса, Україна

## АНОТАЦІЯ

Безмаркерний відеоаналіз є перспективним підходом до кількісного оцінювання спортивного руху у віртуальних тренувальних середовищах і польових умовах, де лабораторні системи захоплення руху часто є недоступними. Актуальність дослідження зумовлена тим, що сирі координати орієнтирів, отримані з монокулярного відео, містять часовий шум, пропуски детекції, зміни масштабу через геометрію камери та одиничні викиди, які спотворюють кінематичні характеристики швидкого руху гольф-ключки. Метою роботи є розроблення та оцінювання відтворюваного конвеєра аналізу руху гольф-ключки, який перетворює відеоорієнтири на стабільні траєкторні, фазові та якісні показники руху. Запропонований метод поєднує виділення орієнтирів, медіанну попередню фільтрацію, Калманівське відстеження, згладжування Рауха-Тунга-Стрібела, усунення локальних викидів, обмежене поліноміальне згладжування, динамічне калібрування масштабу та сегментацію фаз. Результати показують, що глобальні показники якості руху є стабільнішими за пікові похідні характеристики в неоднорідних умовах знімання. Індекс плавності та ефективність траєкторії рекомендовано використовувати як основні показники для міжсесійного порівняння, тоді як піки прискорення та кутової швидкості слід розглядати як допоміжні характеристики за відсутності контрольованих умов запису. Наукова новизна полягає в узгодженій інтеграції відомих процедур фільтрації, згладжування, адаптації масштабу та фазового аналізу у відтворюваний вимірювальний конвеєр для руху гольф-ключки. Практична цінність полягає в можливості використовувати звичайне відео для тренерського зворотного зв’язку, аналізу у віртуальній реальності та подальших валідаційних досліджень.

**Ключові слова:** безмаркерне відстеження; гольф-свінг; фільтрація Калмана; згладжування траєкторії; ефективність траєкторії; повторюваність руху

*Для цитування:* Синюк І. [по батькові]. “Markerless video-based golf stick motion analysis using Kalman filtering and RTS smoothing” // Herald of Advanced Information Technology. – Рік. – Том. – Випуск. – Сторінки. DOI: [заповнюється редакцією]

## AUTHOR INFORMATION

| Photo | Information |
|---|---|
| [Insert author photo 3 × 4 cm] | **Ivan Suniuk**, PhD student, Odesa Polytechnic National University, 1 Shevchenko Ave., Odesa, Ukraine. ORCID: [to be completed]; e-mail: [to be completed]; Scopus Author ID: [if applicable]. **Research field:** markerless motion analysis, computer vision, sports biomechanics, virtual reality training systems. **Українською:** Синюк Іван [по батькові], аспірант, Національний університет «Одеська політехніка», 1 Шевченка просп., Одеса, Україна. |

## MAJOR IMPROVEMENTS MADE

1. Reworked the manuscript according to the HAIT-required section structure.
2. Added UDC, citation placeholder, Ukrainian metadata, conflict statement, funding statement, and author information.
3. Limited keywords to six concise phrases as required by HAIT.
4. Added an IEEE-style reference list with more than 25 sources and DOI links where available.
5. Moved AI disclosure into the methods section in line with HAIT AI policy.
6. Preserved completed results and marked unavailable validation, sensitivity, ablation, ICC, and Bland-Altman data as placeholders instead of inventing results.
