# EmoSys — Facial Emotion Recognition System

> Personal archive of my internship project and development work for **EmoSys**, a facial emotion recognition (FER) system developed during my internship at SMD Semiconductor Sdn Bhd.

---

## Project Overview

**EmoSys** is a facial emotion recognition system designed to detect a person's facial emotion from a camera feed and present the recognition results through a local dashboard.

The project started as a software-based facial emotion recognition prototype and was later developed toward a more embedded setup using **Raspberry Pi**, with the goal of reducing dependency on a laptop for deployment.

The system includes:

* Facial detection
* Facial emotion classification
* Emotion confidence scoring
* Stress-related interpretation
* Real-time emotion display
* Emotion history logging
* Local dashboard
* Embedded deployment experiments
* Model quantization for lightweight deployment

The project also explored extending the system beyond the seven basic emotions into **compound emotion categories**.

---

## Project Context

**Company:** SMD Semiconductor Sdn Bhd
**Department:** Product Development Engineering
**Team:** Product Development — Software
**Project:** EmoSys
**Project Type:** Internship Project

This repository is maintained as a **personal archive** of my development process, experiments, models, notes, and technical decisions.

> ⚠️ Some parts of the original project are subject to company confidentiality and NDA restrictions. This archive should therefore not contain proprietary source code, internal documents, credentials, confidential datasets, or other restricted information.

---

# Project Objectives

The main objectives of EmoSys were to:

1. Develop a facial emotion recognition model.
2. Detect facial expressions from live camera input.
3. Run emotion inference with lightweight models.
4. Explore deployment on Raspberry Pi hardware.
5. Display recognition results through a local dashboard.
6. Record emotion history for later analysis.
7. Explore stress-related indicators based on detected emotions.
8. Investigate model optimization and quantization.
9. Explore compound emotion recognition as an extension of basic FER.

---

# System Concept

The general EmoSys pipeline can be represented as:

```text
                 Camera
                    │
                    ▼
             Face Detection
                    │
                    ▼
             Face Preprocessing
                    │
                    ▼
          Emotion Recognition Model
                    │
                    ▼
             Emotion Prediction
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Confidence          Stress Logic
          │                   │
          └─────────┬─────────┘
                    ▼
              Local Dashboard
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Database             Logs
```

The intended deployment direction was:

```text
Camera
   │
   ▼
Raspberry Pi
   │
   ├── Face Detection
   ├── FER Inference
   └── Prediction Output
            │
            ▼
      Local Network
            │
            ▼
   Raspberry Pi Dashboard
            │
      ┌─────┴─────┐
      ▼           ▼
   InfluxDB      Web UI
```

---

# 🔍 Facial Emotion Recognition

## Basic Emotion Model

The initial FER system focused on the seven commonly used basic emotion categories:

| ID | Emotion  |
| -: | -------- |
|  0 | Angry    |
|  1 | Disgust  |
|  2 | Fear     |
|  3 | Happy    |
|  4 | Neutral  |
|  5 | Sad      |
|  6 | Surprise |

The model development involved experimenting with different CNN architectures and training strategies.

---

# Model Development

## Initial Model Experiments

Several model configurations were explored during development.

The project initially experimented with **EfficientNet-Lite** before moving toward **MobileNetV2** because a lightweight architecture was more suitable for the eventual embedded deployment.

The general direction became:

```text
Initial FER
     │
     ▼
EfficientNet-Lite
     │
     ▼
MobileNetV2
     │
     ▼
Quantization experiments
     │
     ▼
Raspberry Pi deployment
```

---

## MobileNetV2

The final direction for the basic FER model used **MobileNetV2** as the backbone.

The model was selected because it provides a useful balance between:

* Model size
* Inference speed
* Accuracy
* Embedded-device suitability

Transfer learning was used instead of training the entire network from scratch.

Typical training structure:

```text
Image
  │
  ▼
MobileNetV2 Backbone
  │
  ▼
Global Average Pooling
  │
  ▼
Dense Layer
  │
  ▼
Dropout
  │
  ▼
7-Class Emotion Output
```

---

# 📊 Dataset Experiments

Several datasets and dataset configurations were explored during development.

The project encountered several dataset-related issues, including:

* Class mapping inconsistencies
* Incorrect folder paths
* Dataset splitting problems
* Background information affecting predictions
* Limited samples for some emotions
* Differences between training and deployment images

One important debugging discovery involved incorrect emotion mapping between dataset labels and the model's expected class order.

After correcting the mapping, the recognition performance changed significantly.

This reinforced the importance of verifying:

```text
Dataset label
      ↓
Folder name
      ↓
Class index
      ↓
Model output index
      ↓
Inference label
```

rather than assuming that the class ordering is correct.

---

# ⚙️ Quantization

Model optimization was an important part of the project because the final goal was lightweight deployment.

The project investigated:

* Post-Training Quantization (PTQ)
* Quantization-Aware Training (QAT)
* TFLite conversion
* INT8 inference

The general process was:

```text
Trained Keras Model
        │
        ▼
       QAT
        │
        ▼
 Quantized Model
        │
        ▼
   TFLite Model
        │
        ▼
Embedded Inference
```

One of the main observations was that **quantization can reduce model accuracy**, so evaluation was performed both before and after quantization.

Example development observations included model sizes changing from approximately:

```text
Original model  → ~20 MB
TFLite model   → ~2 MB
```

The exact size depends on the model configuration and conversion method.

---

# 🧮 Quantization-Aware Training

QAT was explored to reduce the accuracy loss caused by post-training quantization.

The training process used multiple fine-tuning phases with progressively more of the MobileNetV2 backbone being unfrozen.

Example progression:

```text
Phase 1
↓
Freeze most backbone layers
Train classification layers

Phase 2
↓
Unfreeze additional layers
Fine-tune

Phase 3
↓
Unfreeze more backbone layers
Fine-tune

↓
Quantized TFLite model
```

The project also experimented with:

* Learning-rate adjustments
* Class weighting
* Label smoothing
* Focal loss
* Batch normalization changes
* Different input resolutions
* Different MobileNetV2 configurations

---

# 🌈 Compound Emotion Recognition

After developing the basic seven-emotion system, the project explored **compound emotions**.

The compound emotion model expanded the number of categories beyond the basic FER classes.

Current compound emotion categories explored included:

| Emotion    |
| ---------- |
| Appalled   |
| Bitter     |
| Delighted  |
| Disgusted  |
| Fearful    |
| Infuriated |
| Neutral    |
| Outraged   |
| Sad        |
| Startled   |
| Surprised  |
| Thrilled   |

The idea was to investigate whether the same lightweight FER approach could be extended to more nuanced emotional categories.

---

# Compound Emotion Model

The compound emotion experiment used:

```text
MobileNetV2
Input: 160 × 160
        │
        ▼
Feature Extraction
        │
        ▼
Classification
        │
        ▼
12 Compound Emotion Classes
```

A pretrained MobileNetV2-based FER model was used as the starting point instead of training the entire network from scratch.

The compound emotion model was trained using transfer learning and fine-tuning.

---

# 📈 Compound Emotion Results

The compound emotion model presented a significantly harder classification problem than the basic seven-emotion model.

One of the later experiments produced approximately:

```text
Test Accuracy
≈ 53–54%
```

The model did not show an obvious catastrophic overfitting pattern from the training curves, suggesting that the difficulty was not simply caused by the model memorizing the training data.

Potential factors investigated included:

* Similarity between compound emotions
* Dataset size
* Facial-expression ambiguity
* Label ambiguity
* Differences between subjects
* Limited samples
* Dataset quality
* Image preprocessing
* Basic emotion overlap

This experiment is kept as part of the project history even where the results were not strong, since it helped identify the limitations of extending a basic FER model to more complex emotional categories.

---

# 🧪 Calibration Experiment

Another experiment investigated whether model output logits could be calibrated using class-specific bias values.

The process was:

```text
TFLite Model
     │
     ▼
Raw Logits
     │
     ▼
Class Bias Calibration
     │
     ▼
Adjusted Prediction
```

The calibration experiment achieved approximately:

```text
Calibration-set Macro F1:
71.28%
```

However, when evaluated on the separate test set, the calibration did not improve the final performance:

| Metric   | Before |  After |
| -------- | -----: | -----: |
| Accuracy | 52.94% | 51.63% |
| Macro F1 | 52.78% | 50.85% |

This was an important result because it showed that optimization on the calibration set did not necessarily generalize to the test set.

---

# 📷 Face Detection

The project used **YuNet** for face detection.

One of the models experimented with was:

```text
face_detection_yunet_2023mar.onnx
```

A relatively high detection threshold was used during development to reduce false detections.

Example:

```text
score_threshold = 0.9
```

The detected face region was then passed to the FER model.

General pipeline:

```text
Camera Frame
     │
     ▼
YuNet Face Detection
     │
     ▼
Bounding Box
     │
     ▼
Crop Face
     │
     ▼
Resize
     │
     ▼
FER Model
```

---

# 🖼️ Image Preprocessing

Preprocessing was investigated as part of the model improvement process.

The intended preprocessing pipeline included:

```text
Input Image
     │
     ▼
Resize
     │
     ▼
Grayscale / RGB Handling
     │
     ▼
Convert to 3 Channels
     │
     ▼
Normalize
     │
     ▼
Model Input
```

This was particularly important because some datasets contained grayscale images while the MobileNetV2 backbone expected three-channel input.

---

# 😐 Emotion Output

The inference system was designed to provide more than a single predicted label.

Example output information:

```text
Emotion: Happy
Confidence: 87.3%
```

The system also experimented with displaying the **Top-3 emotion predictions**:

```text
1. Happy       87.3%
2. Neutral      8.4%
3. Surprise     2.1%
```

This provides additional information when the model is uncertain between multiple emotions.

---

# 📊 Emotion History

Emotion predictions were logged over time so that the system could show changes rather than only the current prediction.

Example concept:

```text
Time        Emotion       Confidence
-------------------------------------
10:30:01    Neutral       82%
10:30:06    Happy         76%
10:30:11    Neutral       71%
10:30:16    Sad           64%
```

The system explored storing this information in a database and displaying it through a dashboard.

---

# 🧠 Stress Interpretation

The system also explored using detected emotional states as an indicator for stress-related behaviour.

This was implemented as a **rule-based interpretation layer**, rather than treating the FER model itself as a medical or psychological diagnostic system.

Conceptually:

```text
Emotion Predictions
        │
        ▼
Temporal / Rule Logic
        │
        ▼
Stress Indicator
```

The interface experimented with:

* Current stress state
* Stress spikes
* Sustained emotion
* Emotion history

The intention was to identify potentially concerning patterns rather than diagnose a medical condition.

---

# 📊 Dashboard

A local dashboard was explored for displaying real-time system information.

Potential dashboard information included:

* Current detected emotion
* Confidence
* Top-3 predictions
* Emotion history
* Stress indicator
* Historical graph
* Recent prediction logs

The dashboard was intended to run locally so that the system could operate without depending on an external cloud service.

---

# 🗄️ Database

**InfluxDB** was investigated for storing time-series emotion data.

The conceptual architecture was:

```text
FER Inference
     │
     ▼
Prediction Data
     │
     ▼
InfluxDB
     │
     ▼
Dashboard
```

The system explored periodically writing prediction results rather than continuously storing every camera frame.

For example:

```text
Camera:
    continuous

Inference:
    continuous

Database:
    periodic writes
```

This reduces unnecessary database writes while still preserving useful historical information.

---

# 🔌 Rest API Exploration

The project also investigated communication between Raspberry Pi components.

One possible architecture was:

```text
Pi #1
FER Inference
    │
    │ RestApi 
    ▼
Pi #2
Dashboard + Database
```

The purpose of separating the components was to allow:

* FER inference to focus on processing
* Dashboard to focus on visualization
* Database to focus on historical storage

---

# Raspberry Pi Deployment

A major development direction was moving EmoSys from a laptop-based prototype toward Raspberry Pi hardware.

Target architecture:

```text
             Camera
                │
                ▼
        Raspberry Pi
                │
       ┌────────┴────────┐
       │                 │
 Face Detection      FER Model
       │                 │
       └────────┬────────┘
                ▼
          Prediction
                │
                ▼
        Local Dashboard
```

The goal was to make the system usable with minimal external hardware.

---

# 🖥️ Headless Operation

The system was also tested in a headless environment where the Raspberry Pi did not have a monitor connected.

This exposed several practical issues, including GUI/display dependencies.

For example, OpenCV applications using GUI backends may fail when no graphical display is available.

This led to investigating a separation between:

```text
Camera / Inference
        │
        ▼
Backend Processing
        │
        ▼
Web Dashboard
```

instead of relying on a desktop GUI running directly on the Raspberry Pi.

---

# ✋ Gesture Recognition Exploration

Beyond facial expressions, the project also explored using **MediaPipe landmarks** to identify behavioural cues.

Potential gestures included:

* Hand-to-nose movement
* Face touching
* Hand fidgeting
* Chin resting
* Neck rubbing
* Nose scratching
* Eye rubbing

The general concept was:

```text
Camera
  │
  ▼
MediaPipe Landmarks
  │
  ▼
Feature Extraction
  │
  ▼
Gesture / Behaviour Recognition
```

This was considered as a potential complementary signal to facial emotion recognition.
NOTES: The model data need to be collected using the suppose environment of suppose product output

---

# 🧪 Development Lessons

Some of the most important lessons from the project were not related directly to model accuracy.

## 1. Dataset quality matters

A strong model cannot compensate for inconsistent or poorly prepared data.

Important checks include:

* Class labels
* Folder structure
* Train/test separation
* Class mapping
* Duplicate images
* Image quality
* Subject distribution

---

## 2. Accuracy is not enough

For emotion recognition, accuracy alone can hide problems.

Other metrics are important:

* Precision
* Recall
* F1-score
* Macro F1
* Confusion matrix
* Per-class performance

This became especially important for the compound emotion model.

---

## 3. Quantization changes model behaviour

Reducing the model size is useful for embedded deployment, but quantization can reduce prediction performance.

Therefore:

```text
Float Model Accuracy
        ≠
Quantized Model Accuracy
```

The quantized model needs to be evaluated separately.

---

## 4. Calibration does not guarantee better generalization

The class-bias experiment showed that improving performance on a calibration set does not necessarily improve performance on an independent test set.

This highlighted the importance of keeping calibration and test data separate.

---

## 5. Deployment introduces different problems

A model that works on a laptop may still have problems on an embedded device.

Examples encountered/investigated:

* GUI dependencies
* Display availability
* Inference speed
* Model size
* TFLite compatibility
* Python package compatibility
* Camera access
* Communication between devices

Therefore, deployment should be considered from the beginning rather than only after model training.

---

# 🗂️ Suggested Archive Structure

A personal archive for the project can be organized approximately as:

```text
EmoSys/
│
├── README.md
│
├── docs/
│   ├── project-notes/
│   ├── weekly-updates/
│   ├── architecture/
│   └── experiments/
│
├── models/
│   ├── basic-fer/
│   ├── compound-fer/
│   ├── qat/
│   └── tflite/
│
├── notebooks/
│   ├── training/
│   ├── evaluation/
│   └── calibration/
│
├── src/
│   ├── face-detection/
│   ├── inference/
│   ├── dashboard/
│   └── preprocessing/
│
├── experiments/
│   ├── dataset/
│   ├── quantization/
│   ├── compound-emotion/
│   └── gesture/
│
├── results/
│   ├── graphs/
│   ├── confusion-matrices/
│   └── evaluation/
│
└── archive/
    └── old-experiments/
```

> The actual folder structure may differ depending on which files are retained in the personal archive.

---

# 🔐 Confidentiality

This archive is intended for **personal documentation and learning purposes**.

Do not include:

* Company source code that cannot be redistributed
* Internal repositories
* Internal credentials
* Passwords
* API keys
* Private IP addresses
* Confidential architecture documents
* Proprietary datasets
* NDA-protected information
* Internal meeting materials
* Sensitive company information

If an experiment depends on confidential material, keep only a **high-level description** and record the actual implementation separately in the appropriate internal location.

---

# 📚 Main Technologies Explored

| Area               | Technology                      |
| ------------------ | ------------------------------- |
| Programming        | Python                          |
| Deep Learning      | TensorFlow / Keras              |
| Model              | MobileNetV2                     |
| Face Detection     | YuNet                           |
| Model Format       | Keras / TFLite                  |
| Quantization       | PTQ / QAT                       |
| Computer Vision    | OpenCV                          |
| Embedded Platform  | Raspberry Pi                    |
| Dashboard          | Local Web Dashboard             |
| Database           | InfluxDB                        |
| Communication      | MQTT / REST API                 |
| Landmark Detection | MediaPipe                       |
| Dataset Evaluation | Accuracy, Precision, Recall, F1 |

---

# 🧭 Overall Development Timeline

```text
Basic FER
   │
   ▼
Dataset Investigation
   │
   ▼
MobileNetV2
   │
   ▼
Model Improvement
   │
   ▼
Quantization
   │
   ├── PTQ
   │
   └── QAT
   │
   ▼
TFLite
   │
   ▼
Raspberry Pi
   │
   ▼
Dashboard + Database
   │
   ▼
Compound Emotion Exploration
   │
   ▼
Calibration Experiments
   │
   ▼
Gesture / Behaviour Exploration
```

---

# 📌 Current State

The project progressed from a basic facial emotion recognition prototype toward a more complete embedded-oriented system.

The main areas explored were:

* Basic seven-emotion FER
* MobileNetV2 transfer learning
* Face detection using YuNet
* Model quantization
* Quantization-aware training
* TFLite deployment
* Raspberry Pi deployment
* Local dashboard
* Emotion history
* Stress-related rule logic
* Compound emotion recognition
* Logit calibration
* MediaPipe gesture exploration

The compound emotion model remains an experimental area, with performance substantially lower than the basic FER system.

---

# 📝 Personal Notes

This project involved a lot of trial-and-error rather than a single straight development path.

Some experiments improved the system, while others revealed problems in:

* Dataset preparation
* Label mapping
* Model architecture
* Training configuration
* Quantization
* Deployment
* Evaluation methodology

Keeping these failed or weaker experiments is intentional.

They document **what was tried, what happened, and why later approaches were changed**.

---

# 🚧 Known Limitations

The main limitations identified during development include:

* FER predictions are sensitive to image quality and facial pose.
* Compound emotions are considerably harder to classify.
* Dataset size limits generalization.
* Similar emotional classes can be difficult to distinguish.
* Quantization can reduce accuracy.
* Calibration can improve one dataset split while hurting another.
* Stress interpretation should not be treated as medical diagnosis.
* Headless Raspberry Pi deployment requires careful handling of GUI dependencies.
* Real-world lighting and camera conditions may differ significantly from training data.
* Behavioural cues require temporal information and cannot always be inferred reliably from a single frame.

---

# 🔮 Possible Future Improvements

Possible future directions include:

* Larger and more diverse datasets
* Face-aligned training data
* Better data augmentation
* Temporal emotion modelling
* Improved compound emotion classification
* Multi-modal emotion recognition
* Facial landmark features
* Gesture/behaviour recognition
* Better stress-state modelling
* Raspberry Pi performance optimization
* More robust calibration
* Confidence/uncertainty estimation
* Real-world testing under different lighting and poses
* Further model compression

---

# 💭 Final Reflection

EmoSys was an exploration of the full machine-learning development pipeline rather than only model training.

The project covered:

```text
Data
 ↓
Preprocessing
 ↓
Training
 ↓
Evaluation
 ↓
Optimization
 ↓
Quantization
 ↓
Inference
 ↓
Embedded Deployment
 ↓
Visualization
```

One of the biggest takeaways from the project was that **building an ML system is more than achieving a high training accuracy**.

Dataset correctness, evaluation methodology, model size, deployment constraints, hardware limitations, and real-world behaviour all affect whether the final system is actually usable.

This README serves as a personal record of that development process.

---

## 📅 Archive Information

**Project:** EmoSys
**Type:** Internship Project
**Focus:** Facial Emotion Recognition / Embedded AI
**Primary Framework:** TensorFlow / Keras
**Primary Model:** MobileNetV2
**Deployment Target:** Raspberry Pi
**Status:** Archived / Development History

> This document is a personal technical archive and may contain simplified descriptions of experiments rather than the exact final internal implementation.
