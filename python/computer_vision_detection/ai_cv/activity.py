from datetime import datetime
from video_recording import VideoRecording

class Activity:
    def __init__(self, db, participant_id, session_id, activity_id, type):
        self.db = db
        self.participant_id = participant_id
        self.session_id = session_id
        self.id = activity_id
        self.start_time = datetime.now()
        self.end_time = None
        self.type = type
        
        self.data = self.db.data

        if self.id in self.data["participants"][self.participant_id]["sessions"][self.session_id]["activities"]:
            self.video_recordings_num = self.data["participants"][self.participant_id]["sessions"][self.session_id]["activities"][self.id].get("num_video_recordings", 0) + 1
        else:
            self.video_recordings_num = 1
            self.db.update(
                ["participants", self.participant_id, "sessions", self.session_id, "activities", self.id], {
                "start_time": self.start_time.isoformat(),
                "end_time": None,
                "type": type,
                "necessary_duration" : 0,
                "video_recordings_num" : self.video_recordings_num,
                "video_recordings": {}
                }
            )


    def _end_activity(self):
        """End the activity."""
        self.end_time = datetime.now()
        self.db.update(["participants", self.participant_id, "sessions", self.session_id, "activities", self.id, "end_time"], self.end_time.isoformat())



class APose(Activity):
    def __init__(self, db, participant_id, session_id, activity_id, type, duration=10):
        super().__init__(db, participant_id, session_id, activity_id, type)
        self.duration = duration

        self.db.update(["participants", self.participant_id, "sessions", self.session_id, "activities", self.id, "necessary_duration"], duration)

        self.video_recordings = VideoRecording(self.db, self.participant_id, self.session_id, self.id, self.id + '_' + type.replace(' ', '_') + "_" + str(self.video_recordings_num), duration, './video_recordings/')

        self._end_activity()

class StationaryWalking(Activity):
    def __init__(self, db, participant_id, session_id, activity_id, type, duration=30):
        super().__init__(db, participant_id, session_id, activity_id, type)
        self.duration = duration

        self.db.update(["participants", self.participant_id, "sessions", self.session_id, "activities", self.id, "necessary_duration"], duration)

        self.video_recordings = VideoRecording(self.db, self.participant_id, self.session_id, self.id, self.id + '_' + type.replace(' ', '_') + "_" + str(self.video_recordings_num), duration, './video_recordings/')

        self._end_activity()
