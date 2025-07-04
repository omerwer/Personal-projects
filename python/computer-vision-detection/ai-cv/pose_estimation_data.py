from db import JSONDatabase
from ultralytics import YOLO
import cv2
import os



class PoseEstimationData:
    def __init__(self, id, db_path, videos_folder_path):
        self.id = id
        self.db = JSONDatabase(db_path)
        self.videos_folder = videos_folder_path
        self.pe_model = YOLO('yolo11n-pose.pt')
        self.data = self.db.data
        self.bad_videos = {}


    def run_pe_and_update_db(self):
        for session_id, session_data in self.data["participants"][self.id]["sessions"].items():
            for activity_id, activity_data in session_data['activities'].items():
                necessary_duration = activity_data.get('necessary_duration')

                for video_id, video_data in activity_data['video_recordings'].items():
                    video_duration = video_data['metadata'].get('duration')

                    if video_duration < necessary_duration:
                        print(f'{video_id} video is not long enough, Please redo.')
                    else:
                        cap = cv2.VideoCapture(os.path.join(self.videos_folder, f'{video_id}.mp4'))
                        
                        kp_data_per_video = {}

                        frame_idx = 0
                        while cap.isOpened():
                            ret, frame = cap.read()
                            if not ret:
                                break

                            keypoints = {}
                            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000  

                            results = self.pe_model(frame)

                            for i, result in enumerate(results):
                                keypoints[i] = result.keypoints.data.tolist()

                            if "frame_num" not in kp_data_per_video:
                                kp_data_per_video["frame_num"] = {}

                            kp_data_per_video["frame_num"][frame_idx] = {
                                "timestamp": timestamp,
                                "calculated_keypoints": keypoints
                            }

                            frame_idx = frame_idx + 1
                        
                    self.db.update(
                        ["participants", self.id, "sessions", session_id, "activities", activity_id, "video_recordings", video_id, "keypoints"],
                        kp_data_per_video
                    )
                                
                    

                