import activity
from datetime import datetime


class Session:
    def __init__(self, db, activities_list, participant_id, session_id):
        self.db = db
        self.participant_id = participant_id
        self.id = session_id
        self.start_time = datetime.now()
        self.end_time = None
        self.activities = []

        self.data = self.db.data

        if self.id in self.data["participants"][self.participant_id]["sessions"]:
            self.num_activities = self.data["participants"][self.participant_id]["sessions"][self.id].get("num_activities", 0)
        else:
            self.num_activities = 0
            self.db.update(
                ["participants", self.participant_id, "sessions", self.id], 
                {
                "start_time": self.start_time.isoformat(),
                "end_time": None,
                "num_activities" : self.num_activities, 
                "activities": {}
                }
            )
        
        for actv in activities_list:
            if actv == "A Pose":
                self.activities.append(activity.APose(self.db, self.participant_id, self.id, self.id + '_' + str(self.num_activities+1), actv))
            elif actv == "Stationary Walking":
                self.activities.append(activity.StationaryWalking(self.db, self.participant_id, self.id, self.id + '_' + str(self.num_activities+1), actv))

            self.num_activities = self.num_activities + 1

        self._end_session()


    def _end_session(self):
        """End the session."""
        self.end_time = datetime.now()
        self.db.update(["participants", self.participant_id, "sessions", self.id, "end_time"], self.end_time.isoformat())