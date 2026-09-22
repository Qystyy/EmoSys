# EmoSys — Facial Emotion & Behaviour Recognition System

> Personal archive of my internship project and development work on **EmoSys**, an AI-based facial emotion and behaviour recognition system developed during my internship at SMD Semiconductor Sdn Bhd.

---

## 📌 Project Overview

**EmoSys** is a computer vision system developed to recognize facial emotions and behavioural gestures from camera input.

The project started with **basic facial emotion recognition (FER)** and was later expanded to include **compound emotion recognition** and **gesture recognition**.

The system was also developed with embedded deployment in mind, using **Raspberry Pi** hardware and a local dashboard for displaying and storing inference results.

The main components explored throughout the project are:

* Facial detection
* Basic facial emotion recognition
* Compound emotion recognition
* Gesture recognition
* User-personalised gesture recognition
* Confidence scoring
* Emotion and gesture history
* Local dashboard
* InfluxDB data storage
* Raspberry Pi deployment
* Model quantization and optimization
* TFLite inference

---

# 🧩 System Components

The current EmoSys concept can be divided into three main recognition components:

```text
                    Camera Input
                         │
                         ▼
                 ┌───────────────┐
                 │ Face Detection│
                 └───────┬───────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        Facial Emotion          Gesture /
        Recognition             Behaviour
              │                 Recognition
              │                     │
              └──────────┬──────────┘
                         ▼
                  Inference Results
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        Local Dashboard          Database
                                (InfluxDB)
```

The three major recognition areas are:

### 1. Basic FER

Recognition of seven basic facial emotions:

* Angry
* Disgust
* Fear
* Happy
* Neutral
* Sad
* Surprise

### 2. Compound Emotion Recognition

Recognition of more detailed compound emotion categories using a MobileNetV2-based model.

### 3. Gesture Recognition

Recognition of behavioural gestures using a dedicated gesture model, with an additional personalised model for user-specific calibration.

---

# 🎯 Project Objectives

The main objectives of EmoSys were to:

1. Develop a lightweight facial emotion recognition model.
2. Detect faces from live camera input.
3. Recognize basic and compound emotions.
4. Explore behavioural gesture recognition.
5. Develop a personalised gesture recognition approach.
6. Optimize models for embedded deployment.
7. Deploy inference on Raspberry Pi hardware.
8. Provide real-time results through a local dashboard.
9. Store emotion and gesture history.


---

# 🧠 Overall Pipeline

The general EmoSys pipeline is:

```text
Camera
   │
   ▼
Face / Landmark Detection
   │
   ├───────────────────────┐
   │                       │
   ▼                       ▼
Emotion Model         Gesture Model
   │                       │
   ▼                       ▼
Emotion Result        Gesture Result
   │                       │
   └───────────┬───────────┘
               ▼
        Result Processing
               │
       ┌───────┴────────┐
       ▼                ▼
   Dashboard         InfluxDB
       │
       ▼
 Historical Results
```

---

# 😊 Facial Emotion Recognition

## Basic Emotion Model

The original FER system focused on seven emotion categories:

| ID | Emotion  |
| -: | -------- |
|  0 | Angry    |
|  1 | Disgust  |
|  2 | Fear     |
|  3 | Happy    |
|  4 | Neutral  |
|  5 | Sad      |
|  6 | Surprise |

The project experimented with different CNN architectures before moving toward **MobileNetV2** as the main lightweight architecture.

---

# 🧠 MobileNetV2 FER Model

MobileNetV2 was selected because it provides a balance between:

* Model size
* Inference speed
* Accuracy
* Embedded-device suitability

The general architecture was:

```text
Input Image
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
Emotion Classification
```

Transfer learning was used so that the model could start from a pretrained feature extractor rather than training the entire network from scratch.

---

# 🔍 Face Detection

**YuNet** was used for face detection.

One of the models explored was:

```text
face_detection_yunet_2023mar.onnx
```

The general inference flow was:

```text
Camera Frame
     │
     ▼
YuNet Face Detection
     │
     ▼
Face Bounding Box
     │
     ▼
Face Crop
     │
     ▼
Resize / Preprocess
     │
     ▼
FER Model
```

A detection threshold was also adjusted during development to control the balance between detecting valid faces and avoiding false detections.

---

# 🌈 Compound Emotion Recognition

The project was later extended from seven basic emotions to a more detailed **compound emotion** model.

The current model uses a **MobileNetV2-based architecture** with:

```text
Input Size: 160 × 160
Backbone: MobileNetV2
Training: Transfer Learning + Fine-Tuning
Output Classes: 12
```

## Compound Emotion Classes

|  # | Emotion    |
| -: | ---------- |
|  1 | Appalled   |
|  2 | Bitter     |
|  3 | Delighted  |
|  4 | Disgusted  |
|  5 | Fearful    |
|  6 | Infuriated |
|  7 | Neutral    |
|  8 | Outraged   |
|  9 | Sad        |
| 10 | Startled   |
| 11 | Surprised  |
| 12 | Thrilled   |

The compound emotion model uses the FER model as a starting point before further fine-tuning for the additional emotion categories.

---

# 📊 Compound Emotion Experiments

The compound emotion dataset was processed into separate training and testing sets.

The model used:

* MobileNetV2
* 160 × 160 input
* Sparse categorical cross-entropy
* Transfer learning
* Fine-tuning
* Quantization-aware training

Multiple fine-tuning phases were tested by progressively unfreezing more layers of the backbone.

The model reached approximately **53–54% test accuracy** in later experiments.

The relatively lower performance compared with basic FER highlighted the difficulty of distinguishing between visually similar compound emotions.

---

# 🧮 Model Calibration

A class-bias calibration experiment was performed on the compound emotion model.

The process adjusted the raw output logits before selecting the predicted class:

```text
TFLite Model
     │
     ▼
Raw Logits
     │
     ▼
Class Bias
     │
     ▼
Adjusted Logits
     │
     ▼
Predicted Emotion
```

The calibration set achieved:

```text
Macro F1: 71.28%
```

However, the independent test results did not improve:

| Metric   | Before Calibration | After Calibration |
| -------- | -----------------: | ----------------: |
| Accuracy |             52.94% |            51.63% |
| Macro F1 |             52.78% |            50.85% |

This experiment demonstrated that calibration performance does not necessarily translate into improved performance on unseen data.

---

# ✋ Gesture Recognition

Gesture recognition was added as another recognition component of EmoSys.

Unlike the emotion datasets, the gesture dataset was **collected internally for the project** rather than obtained from an external dataset website.

The current dataset contains data from **6 people** and covers **7 gesture classes**.

## Gesture Classes

|  # | Gesture         |
| -: | --------------- |
|  1 | Neutral         |
|  2 | Eye Scratch     |
|  3 | Head Scratch    |
|  4 | Chin Rest       |
|  5 | Nose Scratching |
|  6 | Neck Rubbing    |
|  7 | Fidgeting       |

These gestures were selected to represent common face-touching and body-related behaviours that could potentially complement facial emotion information.

---

# 🧠 Gesture Model Architecture

Two gesture models were developed:

### Base Gesture Model

The base model is trained using the general gesture dataset and provides the default gesture recognition capability.

```text
Gesture Dataset
      │
      ▼
Preprocessing
      │
      ▼
Base Gesture Model
      │
      ▼
7 Gesture Classes
```

### Personalised Gesture Model

A second model was developed to adapt gesture recognition to an individual user's landmark positions and movement patterns.

A separate calibration process is used to collect the user's landmark information.

```text
User Calibration
       │
       ▼
Personal Landmark Information
       │
       ▼
Personalised Gesture Model
       │
       ▼
User-Specific Recognition
```

The purpose of the personalised model is to account for differences between people, such as:

* Face position
* Body proportions
* Landmark positions
* Natural movement patterns
* Individual gesture style

---

# 🔄 Gesture Model Selection

The main inference code supports both the base and personalised models.

The logic is approximately:

```text
                 Start Inference
                       │
                       ▼
             Personalised Model
                  available?
                 /           \
               Yes            No
                │              │
                ▼              ▼
        Personalised       Base Model
           Model
                │              │
                └──────┬───────┘
                       ▼
                Gesture Result
```

If a personalised model exists, it is used for inference.

If no personalised model is available, the system falls back to the base gesture model.

This allows the system to operate without requiring every user to complete personal calibration.

---

# 📍 Landmark-Based Gesture Recognition

Gesture recognition makes use of landmark information to describe the user's position and movement.

The general concept is:

```text
Camera
   │
   ▼
Landmark Detection
   │
   ▼
Landmark Coordinates
   │
   ▼
Feature Processing
   │
   ▼
Gesture Model
   │
   ▼
Gesture Prediction
```

The landmark information allows the model to distinguish gestures based on the relative position of body or facial landmarks rather than relying only on raw image appearance.

---

# 📈 Gesture Model Evaluation

The gesture models were evaluated using the same general machine-learning evaluation concepts used throughout the project.

Useful evaluation outputs include:

### Accuracy / Loss Curves

Used to observe how model performance changes during training.

### Confusion Matrix

Used to identify which gesture classes are being confused with one another.

### F1-Score

Used to evaluate the balance between precision and recall, particularly when some gesture classes are harder to recognize.

Because the gesture model was developed by another part of the project team, not all original training metrics and per-class results were available for this personal archive.

---

# ⚙️ Model Optimization

Several model optimization techniques were explored throughout EmoSys.

## Quantization-Aware Training

QAT was used to prepare neural networks for quantized deployment.

```text
Normal Training
      │
      ▼
QAT
      │
      ▼
Quantized Model
      │
      ▼
TFLite
```

QAT attempts to make the model more tolerant of the numerical changes introduced during quantization.

---

## Post-Training Quantization

PTQ was also tested by converting an already-trained model into a quantized format.

The main benefit is reduced:

* Model size
* Memory usage
* Storage requirements

However, accuracy may decrease after quantization.

---

## TFLite Conversion

TensorFlow Lite was used as the deployment format for lightweight inference.

```text
Keras Model
    │
    ▼
Optimization / Quantization
    │
    ▼
TFLite Model
    │
    ▼
Embedded Inference
```

This was particularly useful for Raspberry Pi deployment experiments.

---

# 🥧 Raspberry Pi Deployment

A major development goal was to move inference from a conventional laptop environment toward Raspberry Pi hardware.

The intended architecture was:

```text
             Camera
                │
                ▼
         Raspberry Pi
                │
        ┌───────┴────────┐
        ▼                ▼
 Face Detection      Landmark Detection
        │                │
        ▼                ▼
 Emotion Model       Gesture Model
        │                │
        └───────┬────────┘
                ▼
         Result Processing
                │
        ┌───────┴────────┐
        ▼                ▼
    Dashboard         InfluxDB
```

The Raspberry Pi setup was also investigated for headless operation, where a monitor is not required.

---

# 🖥️ Dashboard

The EmoSys dashboard was developed to provide a local interface for viewing inference results.

The dashboard can present information such as:

* Current emotion
* Emotion confidence
* Top-3 emotion predictions
* Emotion history
* Gesture results
* Historical graphs
* Prediction logs

The goal was to provide a simple interface for observing the system without needing to interact directly with the inference process.

---

# 🗄️ InfluxDB

**InfluxDB** was explored for storing time-series inference data.

The basic flow is:

```text
Inference
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

Instead of storing every camera frame, prediction information can be written periodically to reduce unnecessary database operations.

Example information:

```text
Timestamp
Emotion
Confidence
Gesture
```

---

# 🔌 Communication

The project explored communication between different system components using REST APIs and MQTT-related approaches.

A possible architecture was:

```text
Pi #1
Inference
   │
   │ REST / MQTT
   ▼
Pi #2
Dashboard + Database
```

This separation allows inference and visualization components to operate independently.

---

# 🖼️ Data Preprocessing

Different datasets required different preprocessing steps during development.

The general preprocessing pipeline was:

```text
Input Image
     │
     ▼
Resize
     │
     ▼
Channel Conversion
     │
     ▼
RGB Conversion
     │
     ▼
Normalization
     │
     ▼
Model Input
```

Particular attention was required when working with grayscale datasets because the MobileNetV2 model expects three-channel RGB input.

---

# 📊 Model Evaluation

Several evaluation methods were used throughout the project.

## Accuracy

Measures the percentage of predictions that are correct.

Useful for getting an overall view of model performance.

---

## Precision

Measures how often predictions for a particular class are actually correct.

Useful for identifying false-positive problems.

---

## Recall

Measures how many actual samples of a class were successfully detected.

Useful for identifying missed predictions.

---

## F1-Score

Combines precision and recall into a single metric.

Useful when both false positives and false negatives matter.

---

## Confusion Matrix

Shows which classes are being confused with each other.

Example:

```text
                 Predicted
              A    B    C
Actual A     80   10   10
       B      8   75   17
       C      5   12   83
```

This helps identify specific weaknesses that overall accuracy cannot show.

---

# 🧪 Development Experiments

A significant portion of the project involved experimentation and debugging.

Areas investigated included:

* Dataset label mapping
* Dataset path issues
* Dataset preprocessing
* Transfer learning
* MobileNetV2 configurations
* Learning rates
* Frozen/unfrozen layers
* Class weighting
* Label smoothing
* Focal loss
* Batch normalization
* PTQ
* QAT
* TFLite conversion
* Logit calibration
* Raspberry Pi deployment
* Headless operation
* Database communication
* Dashboard integration
* Gesture recognition
* Personalised gesture calibration

Not every experiment resulted in an improvement.

These experiments are retained as part of the development history to document what was tested and what was learned.

---

# 💡 Key Development Lessons

## Dataset preparation is critical

Incorrect class mappings, paths, or preprocessing can produce misleading training and evaluation results.

---

## Higher accuracy does not always mean a better system

Different datasets, evaluation splits, and metrics can produce very different results.

A model should therefore be evaluated using multiple metrics rather than accuracy alone.

---

## Embedded deployment changes the requirements

A model that performs well on a laptop may still be unsuitable for Raspberry Pi due to:

* Model size
* Memory usage
* Inference speed
* Library compatibility
* Hardware limitations

---

## Personalisation can matter for gesture recognition

People naturally perform the same gesture differently.

Personal calibration was therefore explored to make gesture recognition more specific to an individual user.

---

## Calibration needs independent evaluation

The compound emotion calibration experiment showed that improving a calibration set does not necessarily improve performance on unseen test data.

---

# 🚧 Current Limitations

The current system has several limitations.

### Emotion Recognition

* Basic FER remains sensitive to facial pose and image quality.
* Compound emotion recognition is significantly more difficult.
* Similar emotions can be easily confused.
* Dataset size and diversity limit generalization.
* Real-world lighting may differ from training data.

### Gesture Recognition

* Current gesture dataset contains data from only 6 people.
* The number of gesture classes is limited.
* Individual gesture styles vary between users.
* Personal calibration is required for the personalised model.
* The available training/evaluation metrics for the gesture model are limited in this archive.

### System

* Raspberry Pi performance may limit real-time inference.
* Headless deployment can introduce GUI/display issues.
* Communication between components adds additional system complexity.

---

# 🔮 Future Improvements

Possible future improvements include:

* Larger and more diverse gesture datasets
* More users for gesture training
* Improved personalised calibration
* Better compound emotion accuracy
* Temporal emotion modelling
* Temporal gesture modelling
* Multi-modal emotion and behaviour recognition
* Improved uncertainty estimation
* Further model compression
* Raspberry Pi inference optimization
* More robust real-world testing
* Improved dashboard visualization
* Better handling of different lighting and camera conditions

---

# Archive Structure

```text
EmoSys/
│
├── README.md
│
├── model/
│    ├── notebooks/
│        ├── emosys_fer_model_training/
│        ├── cer_mobilenetc2/
│        ├── gesture_finetune_p_model.py/
│        └── gesture_model_training.py/
│    ├── tflite/
│        ├── emosys_fer/
│        ├── emosys_ce/
│        ├── gesture_model_personal/
│        └── gesture_model/
│
├── code/
│   ├── influxdb_handler/
│   ├── main_inference/
│   ├── push_module/
│   └── test_cam/
│   
│
├── run_counter/
│   └── emosys_run_counter/
│
├── face_detection_yunet_20023mar.onnx
│
├── labels_CE.json
│
├── labels_FER.json
│
├── model_info.txt
│
├── model_requirements.txt
│
├── pose_landmarker_lite.task
│
└── requirements.txt
```

---

# 🔐 Confidentiality

This repository is maintained as a **personal archive** of the development process.

Because the project was developed during an internship and some components are subject to company confidentiality and NDA restrictions, this repository should **not contain confidential company information**.

Do not upload:

* Internal source code that cannot be redistributed
* API keys
* Passwords
* Tokens
* Private URLs
* Internal IP addresses
* Proprietary datasets
* NDA-protected material
* Internal documentation
* Confidential meeting materials
* Sensitive company information

Where an experiment depends on confidential material, only a high-level description should be retained here.

---

# 🛠️ Technologies Explored

| Area                          | Technology                                            |
| ----------------------------- | ----------------------------------------------------- |
| Programming                   | Python                                                |
| Deep Learning                 | TensorFlow / Keras                                    |
| FER Model                     | MobileNetV2                                           |
| Face Detection                | YuNet                                                 |
| Gesture / Landmark Processing | MediaPipe                                             |
| Model Format                  | Keras / TFLite                                        |
| Optimization                  | PTQ / QAT                                             |
| Computer Vision               | OpenCV                                                |
| Hardware                      | Raspberry Pi                                          |
| Database                      | InfluxDB                                              |
| Communication                 | REST API / MQTT                                       |
| Dashboard                     | Local Web Dashboard                                   |
| Evaluation                    | Accuracy / Precision / Recall / F1 / Confusion Matrix |

---

# 🧭 Development Timeline

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
PTQ / QAT
   │
   ▼
TFLite
   │
   ▼
Raspberry Pi Deployment
   │
   ├───────────────┐
   │               │
   ▼               ▼
Dashboard       InfluxDB
   │
   ▼
Compound Emotion
   │
   ▼
Logit Calibration
   │
   ▼
Gesture Recognition
   │
   ▼
Personalised Gesture Model
```

---

# 📌 Current Project State

EmoSys has progressed from a basic facial emotion recognition prototype into a broader **emotion and behaviour recognition system**.

The current development areas include:

### Facial Emotion Recognition

Basic seven-class FER using a lightweight MobileNetV2-based model.

### Compound Emotion Recognition

A 12-class model exploring more detailed emotional categories.

### Gesture Recognition

A seven-class gesture recognition model trained using an internally collected dataset.

### Personalised Gesture Recognition

A second gesture model that can be used after user-specific calibration.

### Embedded Deployment

Raspberry Pi deployment using lightweight TFLite models.

### Dashboard & Data

Local visualization and time-series storage using a dashboard and InfluxDB.

---

# 📚 Personal Project Notes

EmoSys involved a combination of machine-learning development, computer vision, embedded deployment, and system integration.

The project was not developed as a single linear process. Many parts involved repeated experimentation:

```text
Try
 ↓
Evaluate
 ↓
Find Problem
 ↓
Modify
 ↓
Test Again
```

Some experiments produced improvements while others demonstrated limitations.

Keeping these experiments is useful for documenting the reasoning behind later changes and for understanding the practical challenges involved in taking an ML model from **dataset → training → optimization → deployment → real-world inference**.

---

## 📅 Archive Information

**Project:** EmoSys
**Project Type:** Internship Project
**Focus:** Facial Emotion, Compound Emotion & Gesture Recognition
**Primary Framework:** TensorFlow / Keras
**Primary FER Architecture:** MobileNetV2
**Face Detection:** YuNet
**Gesture Processing:** MediaPipe / Gesture Models
**Deployment Target:** Raspberry Pi
**Status:** Archived Development Project
**Year:** 2026

> This README is a personal technical archive. It intentionally provides a high-level description of the project and does not reproduce confidential implementation details.
