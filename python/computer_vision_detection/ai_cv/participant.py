from db import JSONDatabase
from session import Session

class Participant:
    def __init__(self, db_folder_path, participant_id, name, age):
        self.db = JSONDatabase(db_folder_path + "database.json")
        self.id = str(participant_id)
        self.name = name
        self.age = age
        self.activities_list = ["A Pose", "Stationary Walking"]

        self.data = self.db.data

        if self.id in self.data["participants"]:
            self.num_sessions = self.data["participants"][self.id].get("num_sessions", 0) + 1
        else:
            self.num_sessions = 1
            self.db.update(
                ["participants", self.id],
                {
                    "name": self.name,
                    "id": self.id,
                    "age": self.age,
                    "num_sessions": self.num_sessions,
                    "sessions": {}
                }
            )

        self.session = Session(self.db,  self.activities_list, self.id, self.id + '_' + str(self.num_sessions))

        self.db.update(
            ["participants", self.id, "num_sessions"],
            self.num_sessions
        )
