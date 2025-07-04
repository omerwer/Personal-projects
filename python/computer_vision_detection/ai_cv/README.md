# 🩺 Patient Pose‑Estimation Pipeline

A lightweight Python system that **collects patient metadata, records
activity videos, and runs pose estimation** (Ultralytics YOLO‑N‑Pose) on
each recording. All results are persisted in a clean, hierarchical JSON
database for later analysis.

<table>
<tr>
<td align="center"><b>Patient → Session → Activity → Video → Keypoints</b></td>
<td>

```
database.json
└── participants/
    └── 265465/
        ├── name: "Todd"
        ├── age: 39
        └── sessions/
            └── 265465_1/
                ├── start_time
                ├── activities/
                │   ├── 265465_1_1/ ← "A Pose"
                │   │   └── video_recordings/
                │   │       └── 265465_1_1_A_Pose_1/
                │   │           ├── metadata
                │   │           └── keypoints
                │   └── 265465_1_2/ ← "Stationary Walking"
                └── end_time
```

</td></tr></table>

---

## ✨ Features

| Module                        | What it does                                                                     |
| ----------------------------- | -------------------------------------------------------------------------------- |
| **`participant.py`**          | Registers a participant and spins up a new session                               |
| **`session.py`**              | Starts a session, triggers each activity in sequence                             |
| **`activity.py`**             | Defines activities (`A Pose`, `Stationary Walking`) and attaches video recording |
| **`video_recording.py`**      | Records webcam / UDP stream to `.mp4`, stores rich metadata                      |
| **`pose_estimation_data.py`** | Runs YOLOv8‑pose on every video, timestamps each frame’s keypoints               |
| **`db.py`**                   | Thin JSON “DB” wrapper with hierarchical update helper                           |
| **`requirements.txt`**        | Exact package list (Ultralytics, OpenCV, etc.)                                   |

---

## 📂 Project Layout

```
├─ activity.py
├─ db.py
├─ main.py
├─ participant.py
├─ pose_estimation_data.py
├─ session.py
├─ video_recording.py
├─ requirements.txt
├─ video_recordings/          # auto‑created, stores .mp4 files
└─ database.json              # auto‑created, hierarchical patient DB
```

---

## 🚀 Quick Start

1. **Clone & set up environment**

   ```bash
   git clone https://github.com/omerwer/Personal-projects
   cd Personal-projects/python/computer_vision_detection/ai_cv
   python -m venv .venv
   source .venv/bin/activate     # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **(Optional) Download the pose model once**

   The first run of Ultralytics will auto‑download `yolo11n‑pose.pt`.
   For offline deployments, place it next to the scripts.

3. **Run the demo pipeline**

   ```bash
   # main.py records two activities for patient 265465, then
   # launches pose estimation on the captured videos.
   python main.py
   ```

4. **Inspect results**

   * `database.json` – check the nested structure for timestamps,
     video metadata, and "keypoints" arrays
   * `video_recordings/*.mp4` – raw recordings

---

## ⚙️ Configuration Highlights

| Setting                | Where                     | Default                        | Notes                               |
| ---------------------- | ------------------------- | ------------------------------ | ----------------------------------- |
| **Video source**       | `video_recording.py`      | `"udp://127.0.0.1:8090"`       | Change to `0` for local webcam      |
| **FPS / codec**        | `video_recording.py`      | 30 FPS, `mp4v`                 | Tweak for quality vs. size          |
| **Model path**         | `pose_estimation_data.py` | `'yolo11n-pose.pt'`            | Could swap to any YOLO‑pose variant |
| **Required durations** | `activity.py`             | `10 s` (A Pose), `30 s` (Walk) | Stored in DB for validation         |

---

## 🧠 Flow Overview

```mermaid
graph TD
    subgraph Data Flow
      A([main.py]) -->|create| B[Participant]
      B --> C[Session]
      C -->|for act in ["A Pose", "Stationary Walking"]| D(Activity)
      D --> E[VideoRecording]
      E -->|.mp4 + metadata| DB[(JSON DB)]
      E -->|.mp4| F[PoseEstimationData]
      F -->|keypoints JSON| DB
    end
```

1. **Participant / Session** are created → logged in `database.json`.
2. Each **Activity** starts a **VideoRecording** thread that writes a local
   `.mp4` and metadata (resolution, framerate, duration, frame drops).
3. After recording finishes, **PoseEstimationData** iterates every video,
   runs YOLO‑pose frame‑by‑frame, stores 2‑D keypoints alongside each
   timestamp.
4. Keypoints are merged back into the same nested path in the DB.                                                        |

---

## 📜 License

Distributed under the MIT License
