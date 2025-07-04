from datetime import datetime
import time
import os
import cv2

class VideoRecording:
    def __init__(self, db, participant_id, session_id, activity_id, video_id, duration, save_dir):
        self.db = db
        self.participant_id = participant_id
        self.session_id = session_id
        self.activity_id = activity_id
        self.id = video_id
        self.save_dir = save_dir
        self.duration = duration
        self.start_time = datetime.now()
        self.end_time = None

        os.makedirs(self.save_dir, exist_ok=True)

        self.video_path = os.path.join(self.save_dir, f"{self.id}.mp4")

        self.metadata = {
            "resolution": None,
            "framerate": None,
            "duration": self.duration,
            "timestamp": self.start_time.isoformat(),
            "num_framedrops": 0
        }

        self.db.update(
            ["participants", self.participant_id, "sessions", self.session_id, "activities", self.activity_id, "video_recordings", self.id],
            {
                "save_dir": self.save_dir,
                "video_path": self.video_path,
                "start_time": self.start_time.isoformat(),
                "end_time": None,
                "metadata": self.metadata
            }
        )

        self._record_video()

    def _record_video(self):
        """Records a video from the webcam using OpenCV."""
        # cap = cv2.VideoCapture(0)  # Open webcam
        cap = cv2.VideoCapture("udp://127.0.0.1:8090")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        fps = 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.metadata["resolution"] = f"{width}x{height}"
        self.metadata["framerate"] = fps

        out = cv2.VideoWriter(self.video_path, fourcc, fps, (width, height))

        start = time.time()
        num_frames = 0
        while (time.time() - start) < self.duration:
            ret, frame = cap.read()
            if not ret:
                self.metadata["num_framedrops"] += 1
                continue
            out.write(frame)
            num_frames += 1
            cv2.imshow("Recording", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

        self.end_time = datetime.now()
        self.metadata["duration"] = (self.end_time - self.start_time).total_seconds()

        self.db.update(
            ["participants", self.participant_id, "sessions", self.session_id, "activities", self.activity_id, "video_recordings", self.id, "end_time"],
            self.end_time.isoformat()
        )
        self.db.update(
            ["participants", self.participant_id, "sessions", self.session_id, "activities", self.activity_id, "video_recordings", self.id, "metadata"],
            self.metadata
        )