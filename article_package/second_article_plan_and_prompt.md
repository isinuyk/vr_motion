# Second Article Plan and Agent Prompt

## Working Title

Robustness and Validation of a Markerless Video-Based Golf Swing Motion-Analysis Workflow Under Heterogeneous Recording Conditions

Alternative titles:

- Validation and Sensitivity Analysis of Markerless Golf-Stick Motion Tracking for Sport-Biomechanics Applications
- Robustness of Kalman- and RTS-Smoothed Markerless Golf Swing Metrics Under Frame-Rate, Landmark, and Scale Perturbations
- Accuracy, Repeatability, and Robustness of Video-Based Golf-Stick Kinematic Indicators for VR Training Analytics

## Purpose of This Document

This Markdown file is a future-use planning brief and prompt for writing a second research article related to the existing VR/golf motion-analysis project.

It does not implement code and does not generate the article now. It records:

- what was already done in the first article;
- what the second article should focus on;
- what data, scripts, CSV files, graphs, and validation outputs should be implemented later;
- what HAIT-style formatting requirements should be remembered;
- a ready-to-send prompt for another AI agent when the author is ready to work on the second article.

## Background: What the First Article Covered

The first article was prepared as a HAIT-aligned manuscript:

`article_package/Стаття_Аспірант_Синюк_HAIT_aligned_final_with_figures_wordsafe.docx`

The first article focused mainly on the method and workflow:

- markerless video-based golf-stick motion analysis;
- body and golf-stick landmark extraction;
- conversion of normalized landmarks into pixel coordinates;
- median pre-filtering;
- confidence-aware Kalman filtering;
- Rauch-Tung-Striebel backward smoothing;
- trajectory despiking;
- bounded polynomial smoothing;
- dynamic scale calibration;
- extraction of kinematic and biomechanical metrics;
- raw, filtered, and smoothed trajectory comparison;
- session-level repeatability;
- diagnostic validation, sensitivity, and ablation results.

The first article intentionally framed some results cautiously because the validation and ablation outputs were diagnostic, not yet a controlled accuracy study. This creates a strong opportunity for a second article focused specifically on validation, robustness, and metric reliability.

## Recommended Focus for the Second Article

The strongest and least repetitive second article would be:

**Validation and robustness analysis of the markerless golf-stick motion-analysis workflow.**

The first article answers:

> How is the markerless motion-analysis workflow designed and what metrics does it produce?

The second article should answer:

> How accurate, robust, and reliable are the generated swing events, trajectories, and metrics under reference annotation and controlled perturbations?

This makes the second article complementary, not redundant. It also supports a future dissertation structure:

- Article 1: system and methodological pipeline.
- Article 2: validation, robustness, and reliability evidence.
- Dissertation: integrated method development, experimental validation, and sport/VR application.

## Possible Research Aim

The aim of the second study is to evaluate the accuracy, robustness, and reliability of a markerless video-based golf-stick motion-analysis workflow under heterogeneous recording conditions and controlled input perturbations.

## Possible Research Objectives

1. To construct a manually annotated reference subset for key swing events and selected stick-tip trajectory control points.
2. To quantify event-detection accuracy for impact, top of backswing, and downswing transition.
3. To estimate geometric trajectory error between automatically processed stick-tip positions and manually annotated reference points.
4. To evaluate the sensitivity of exported metrics to frame thinning, simulated landmark dropout, scale perturbation, and combined degradation.
5. To compare processing variants through an ablation study: raw landmarks, median-only filtering, Kalman filtering, Kalman plus RTS smoothing, and the full pipeline.
6. To identify which kinematic and movement-quality metrics are robust enough for cross-session comparison.
7. To formulate practical recommendations for using markerless golf-swing metrics in VR training and sport-biomechanics applications.

## Possible Hypotheses

H1. Global movement-quality metrics such as smoothness index and path efficiency are more robust under heterogeneous capture conditions than peak derivative metrics such as maximum acceleration and maximum angular velocity.

H2. Confidence-aware Kalman filtering followed by RTS smoothing reduces trajectory jitter while preserving the main swing path better than median-only filtering or Kalman filtering without backward smoothing.

H3. Event timing accuracy is more sensitive to phase-boundary definition and frame rate than global trajectory-shape metrics.

H4. Scale perturbation has a predictable effect on metric magnitude, while landmark dropout and frame thinning produce larger changes in derivative-based metrics.

## Data Already Available in the Project

Known project context from the first article work:

- There are 71 processed golf-stick swing sessions.
- Existing metadata include frame count, frame rate, resolution, viewpoint, stroke type, and video-quality tags.
- Existing generated outputs are stored under:
  - `article_package/evaluation_outputs/`
  - `article_package/evaluation_outputs/figures/`
- Existing or previously generated files include:
  - `dataset_summary.csv`
  - `validation_keyframe_errors.csv`
  - `sensitivity_results.csv`
  - `ablation_results.csv`
  - `repeatability_repeatability.csv`
  - `trajectory_deviation_summary.csv`
  - `batch_evaluation_summary.md`
  - `fig_repeatability_cv.png`
  - `fig_example_kinematics_trajectory.png`
  - `fig_validation_keyframe_errors.png`
  - `fig_sensitivity_results.png`
  - `fig_ablation_results.png`
- Existing analysis scripts include:
  - `batch_article_evaluation.py`
  - `evaluate_filters.py`
  - `parameter_sweep.py`
  - `swing_analyzer.py`
  - `analysis.py`
  - `kalman.py`
  - `rts_smoother.py`
  - `utils_filter.py`
  - `drawing.py`

The second article should not simply reuse these outputs unchanged. It should improve them into a controlled validation and robustness study.

## New Data or Annotation Needed

The most important missing piece is a stronger reference subset.

Recommended manual annotations:

- impact frame/time;
- top of backswing frame/time;
- downswing transition frame/time;
- optional address/start frame;
- 5-10 stick-tip control points per selected swing;
- optional stick-base or stick-midpoint reference points;
- optional ball position at impact;
- optional quality tags: occlusion, blur, camera viewpoint, slow-motion, super-slow-motion.

Recommended annotation format:

`reference_annotations.csv`

Suggested columns:

- `session_id`
- `video_path` or `source_id`
- `fps`
- `frame_width`
- `frame_height`
- `event_name`
- `reference_frame`
- `reference_time_s`
- `point_name`
- `x_px`
- `y_px`
- `annotator_id`
- `annotation_round`
- `quality_note`

If two annotators are available, add inter-annotator reliability:

- mean absolute disagreement in frames/ms;
- mean point distance in pixels;
- ICC or agreement statistics where applicable.

## Scripts to Implement Later

Do not implement now. These are recommended future scripts.

### 1. `prepare_reference_subset.py`

Purpose:

- select representative sessions for manual annotation;
- balance by viewpoint, frame rate, resolution, stroke type, and quality tags;
- export a list of videos/sessions for annotation.

Outputs:

- `second_article_outputs/reference_subset.csv`
- `second_article_outputs/reference_subset_summary.csv`

Recommended selection:

- 20-30 sessions minimum for event validation;
- 10-15 sessions with point-level annotations;
- include good, medium, and difficult recordings.

### 2. `validate_events_against_reference.py`

Purpose:

- compare automatic event detections with manual reference events;
- compute signed and absolute timing errors.

Outputs:

- `second_article_outputs/event_validation_errors.csv`
- `second_article_outputs/event_validation_summary.csv`
- `second_article_outputs/figures/fig_event_error_by_event.png`
- `second_article_outputs/figures/fig_event_error_bland_altman.png`

Metrics:

- signed error in frames;
- absolute error in frames;
- signed error in milliseconds;
- absolute error in milliseconds;
- median absolute error;
- 95th percentile absolute error;
- detection failure rate;
- Bland-Altman mean bias and limits of agreement.

### 3. `validate_trajectory_against_reference.py`

Purpose:

- compare processed stick-tip trajectories with manually annotated reference points;
- evaluate geometric error.

Outputs:

- `second_article_outputs/trajectory_reference_errors.csv`
- `second_article_outputs/trajectory_reference_summary.csv`
- `second_article_outputs/figures/fig_trajectory_error_distribution.png`
- `second_article_outputs/figures/fig_trajectory_error_by_phase.png`

Metrics:

- Euclidean error in pixels;
- Euclidean error in normalized coordinates;
- Euclidean error in metres if scale is reliable;
- phase-specific error: backswing, downswing, impact region;
- error by viewpoint and quality tag.

### 4. `run_sensitivity_study.py`

Purpose:

- run controlled perturbations on the same sessions;
- measure metric stability.

Perturbations:

- frame thinning: every 2nd frame, every 3rd frame;
- simulated landmark dropout: 5%, 10%, 20%;
- coordinate jitter: small Gaussian noise added to landmarks;
- scale perturbation: +/- 5%, +/- 10%;
- combined degradation: frame thinning + dropout + jitter;
- optional viewpoint subgroup analysis.

Outputs:

- `second_article_outputs/sensitivity_results.csv`
- `second_article_outputs/sensitivity_summary.csv`
- `second_article_outputs/figures/fig_sensitivity_metric_heatmap.png`
- `second_article_outputs/figures/fig_sensitivity_by_perturbation.png`

Metrics:

- absolute change;
- percentage change;
- median absolute percentage change;
- rank stability;
- classification stability for robust vs exploratory metrics.

### 5. `run_ablation_study.py`

Purpose:

- compare processing variants on the same sessions and same metric definitions;
- avoid the inconsistency seen in the first diagnostic ablation table.

Variants:

- raw landmarks;
- median-only;
- Kalman only;
- Kalman + RTS;
- Kalman + RTS + despiking;
- full pipeline with polynomial smoothing and scale bounding.

Important requirement:

- compute all derivative metrics from the final trajectory of each variant using the same derivative function and the same time base.

Outputs:

- `second_article_outputs/ablation_results.csv`
- `second_article_outputs/ablation_summary.csv`
- `second_article_outputs/figures/fig_ablation_trajectory_deviation.png`
- `second_article_outputs/figures/fig_ablation_jerk_reduction.png`
- `second_article_outputs/figures/fig_ablation_metric_stability.png`

Metrics:

- trajectory deviation from reference or from selected baseline;
- RMS jerk;
- smoothness index;
- path efficiency;
- event timing stability;
- processing success rate;
- missing-data bridging performance.

### 6. `compute_reliability_statistics.py`

Purpose:

- compute stronger reliability statistics if repeated trials or repeated annotations are available.

Outputs:

- `second_article_outputs/reliability_statistics.csv`
- `second_article_outputs/figures/fig_bland_altman_selected_metrics.png`
- `second_article_outputs/figures/fig_icc_metric_ranking.png`

Metrics:

- coefficient of variation;
- repeatability coefficient;
- intraclass correlation coefficient if grouping exists;
- Bland-Altman limits of agreement;
- standard error of measurement;
- minimal detectable change.

## Main Figures for the Second Article

Suggested figures:

1. Study design and validation workflow.
2. Example manually annotated frame with reference stick-tip points.
3. Event timing error by swing event.
4. Trajectory point error distribution.
5. Sensitivity heatmap by metric and perturbation.
6. Ablation comparison of processing variants.
7. Bland-Altman or agreement plot for selected robust metrics.

Fig. 2 should use a permitted/anonymized video frame, not a real user frame without consent.

## Main Tables for the Second Article

Suggested tables:

1. Dataset and reference subset characteristics.
2. Manual annotation protocol.
3. Event timing validation results.
4. Trajectory reference error results.
5. Sensitivity analysis summary.
6. Ablation comparison.
7. Robustness ranking of metrics.
8. Limitations and recommended metric-use categories.

## Recommended Metric Categories

The second article should classify metrics into practical categories.

Potential robust metrics:

- smoothness index;
- path efficiency;
- normalized trajectory deviation;
- possibly tempo if phase detection is improved.

Potential exploratory metrics:

- maximum acceleration;
- maximum angular velocity;
- curvature RMS;
- backswing peak speed;
- phase durations if event detection remains unstable.

Potential reporting categories:

- robust under heterogeneous capture;
- usable with controlled acquisition;
- exploratory only;
- not recommended without external validation.

## Scientific Cautions

The second article must avoid overclaiming.

Do not claim:

- laboratory-grade accuracy unless compared with a trusted reference;
- dense 3D biomechanical validity from monocular 2D video;
- robust event detection if timing errors remain in seconds;
- repeatability across athletes if athlete/trial grouping is not known.

It is acceptable and scientifically strong to report negative findings:

- event detection requires recalibration;
- derivative metrics are unstable under heterogeneous video;
- some metrics are robust while others should remain exploratory.

## HAIT Formatting Requirements to Remember

Official HAIT requirements page:

`https://hait.od.ua/index.php/journal/requirements`

Key requirements used in the first article:

- Microsoft Word DOCX.
- A4 page.
- Portrait orientation.
- Margins: top, left, right = 2 cm; bottom = 2.5 cm.
- Font: Times New Roman, 11 pt.
- Single line spacing.
- Justified body text.
- Paragraph indent: 0.75 cm.
- Main body in two columns.
- UDC, author list, title, abstract, keywords, citation text, references, and back matter in single column.
- Minimum 25 references is preferred by HAIT; the first article had 24 after removing meta references, so the second article should target 25-30 scientific references.
- In-text citations use IEEE numbering style.
- References should be in English and formatted according to IEEE-style requirements.
- Figures and tables must be cited in running text.
- Figure/table source notes: 8 pt bold italic.
- Formulas must be editable Word equations, not images.
- Formula numbering is required only when formulas are referenced by number in the text.
- Ukrainian metadata are required after the English article.

## Suggested Article Structure

1. UDC, authors, affiliations, title, abstract, keywords, citation line.
2. INTRODUCTION
   - problem of validating markerless sport-motion systems;
   - limitations of monocular video;
   - need for robustness and uncertainty evaluation.
3. LITERATURE REVIEW AND PROBLEM STATEMENT
   - markerless pose estimation in sport;
   - golf swing analysis;
   - validation of motion-analysis systems;
   - filtering and derivative-noise problems.
4. RESEARCH AIM AND OBJECTIVES
5. MATERIALS AND METHODS
   - dataset and reference subset;
   - manual annotation protocol;
   - automatic processing workflow;
   - event validation;
   - trajectory validation;
   - sensitivity perturbations;
   - ablation variants;
   - statistical analysis.
6. RESEARCH RESULTS
   - dataset/reference subset;
   - event timing error;
   - trajectory error;
   - sensitivity analysis;
   - ablation analysis;
   - metric robustness ranking.
7. DISCUSSION OF RESULTS
   - which metrics are usable;
   - why derivatives are unstable;
   - implications for VR feedback;
   - limitations.
8. CONCLUSIONS
9. ACKNOWLEDGMENTS
10. REFERENCES
11. Ukrainian metadata.
12. Author information.

## Ready-to-Send Prompt for a Future Agent

```text
You are an expert academic researcher, scientific editor, and Python data-analysis assistant specializing in computer vision, sport biomechanics, markerless motion analysis, and Scopus-level manuscript preparation.

I need help preparing a second research article related to my existing project:

Project topic:
Markerless video-based golf-stick motion analysis for VR/sport-biomechanics applications.

First article already completed:
It focused on the full methodological pipeline: landmark extraction, median pre-filtering, confidence-aware Kalman filtering, RTS smoothing, trajectory despiking, polynomial smoothing, dynamic scale calibration, kinematic metric extraction, raw-vs-smoothed comparison, session-level repeatability, and diagnostic validation/sensitivity/ablation outputs.

The second article must not repeat the first one. It should focus on:
Validation, robustness, sensitivity analysis, ablation, and metric reliability of the markerless golf-stick motion-analysis workflow.

Target journal formatting style:
Herald of Advanced Information Technology (HAIT)
Official requirements:
https://hait.od.ua/index.php/journal/requirements

Important HAIT requirements:
- DOCX manuscript.
- Times New Roman 11 pt.
- Margins: top/left/right 2 cm; bottom 2.5 cm.
- Main body in two columns.
- Metadata, abstract, keywords, references, and Ukrainian metadata in single column.
- Figures and tables must be cited in text.
- Figure/table source notes: 8 pt bold italic.
- In-text citations use IEEE numbering.
- References should be scientific, English-language, and preferably 25-30 sources.
- Formulas must be editable Word equations, not images.
- Formula numbering is required only when formulas are referenced by number.

Existing project files likely relevant:
- batch_article_evaluation.py
- evaluate_filters.py
- parameter_sweep.py
- swing_analyzer.py
- analysis.py
- kalman.py
- rts_smoother.py
- utils_filter.py
- drawing.py
- article_package/evaluation_outputs/dataset_summary.csv
- article_package/evaluation_outputs/validation_keyframe_errors.csv
- article_package/evaluation_outputs/sensitivity_results.csv
- article_package/evaluation_outputs/ablation_results.csv
- article_package/evaluation_outputs/repeatability_repeatability.csv
- article_package/evaluation_outputs/trajectory_deviation_summary.csv
- article_package/evaluation_outputs/figures/

Important note:
The first article treated validation/sensitivity/ablation results as diagnostic because some values were not strong enough for final accuracy claims. The second article should improve these outputs and make them the main scientific contribution.

Please help me plan and then implement the second article workflow.

Do not immediately write the final article. First:
1. Inspect the existing project structure and available outputs.
2. Identify what additional reference annotations are needed.
3. Propose the exact experimental design for the second article.
4. Define scripts to implement, CSV outputs to generate, figures to produce, and tables to include.
5. Identify which results can be reused from the first article and which must be recalculated.
6. Highlight scientific risks, especially overclaiming accuracy without reference data.

Recommended new outputs to implement:
- second_article_outputs/reference_subset.csv
- second_article_outputs/reference_subset_summary.csv
- second_article_outputs/reference_annotations.csv, if manual labels are available
- second_article_outputs/event_validation_errors.csv
- second_article_outputs/event_validation_summary.csv
- second_article_outputs/trajectory_reference_errors.csv
- second_article_outputs/trajectory_reference_summary.csv
- second_article_outputs/sensitivity_results.csv
- second_article_outputs/sensitivity_summary.csv
- second_article_outputs/ablation_results.csv
- second_article_outputs/ablation_summary.csv
- second_article_outputs/reliability_statistics.csv
- second_article_outputs/figures/fig_event_error_by_event.png
- second_article_outputs/figures/fig_trajectory_error_distribution.png
- second_article_outputs/figures/fig_sensitivity_metric_heatmap.png
- second_article_outputs/figures/fig_ablation_trajectory_deviation.png
- second_article_outputs/figures/fig_bland_altman_selected_metrics.png

Recommended research aim:
To evaluate the accuracy, robustness, and reliability of a markerless video-based golf-stick motion-analysis workflow under heterogeneous recording conditions and controlled input perturbations.

Recommended objectives:
1. Construct a manually annotated reference subset for key swing events and selected stick-tip trajectory control points.
2. Quantify event-detection accuracy for impact, top of backswing, and downswing transition.
3. Estimate geometric trajectory error between automatically processed stick-tip positions and manually annotated reference points.
4. Evaluate sensitivity of exported metrics to frame thinning, landmark dropout, coordinate jitter, scale perturbation, and combined degradation.
5. Compare processing variants through an ablation study.
6. Identify which metrics are robust enough for cross-session comparison.
7. Formulate recommendations for VR training and sport-biomechanics use.

Expected article structure:
- INTRODUCTION
- LITERATURE REVIEW AND PROBLEM STATEMENT
- RESEARCH AIM AND OBJECTIVES
- MATERIALS AND METHODS
- RESEARCH RESULTS
- DISCUSSION OF RESULTS
- CONCLUSIONS
- ACKNOWLEDGMENTS
- REFERENCES
- Ukrainian metadata
- Author information

Please begin by analyzing the current project and producing a detailed implementation plan, not by writing the final paper immediately.
```

## Final Note

The second article becomes strongest if manual reference annotations are added. Without them, the article can still be a robustness/sensitivity study, but it should not claim full external accuracy validation.
