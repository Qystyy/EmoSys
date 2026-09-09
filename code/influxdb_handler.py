from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

class InfluxDBHandler:
    
    def __init__(self):
        self.url    = "http://localhost:8086"
        self.token  = "P94COCY0PTnw_oA0Dvtlv9y2ZWirIteioLJpmlkOm_PXPcX-LDO3V-Axe6mJGqIWy47uX06lP8fJKNEPOqu4cA=="
        self.org    = "EmoSys"
        self.bucket = "emotionDB"

        self.client = InfluxDBClient(
            url    = self.url,
            token  = self.token,
            org = self.org
        )

        self.write_api  = self.client.write_api(
            write_options = SYNCHRONOUS
        )

        self.last_saved = 0
        self.interval   = 5 #seconds

    
    def write_prediction(self, fid, emotion, confidence, posture_score, posture, habit_label, habit_cf):
        current_time = time.time()

        if current_time - self.last_saved < self.interval:
            return

        point = (
            Point("FER Prediction")
            .tag("device", "pi1")
            .tag("face_id", int(fid))
            .field("emotion", emotion)
            .field("confidence", float(confidence))
            .field("posture_score", float(posture_score))
            .field("posture", posture)
            .field("habit_label", habit_label)
            .field("habit_cf", float(habit_cf))
        )

        self.write_api.write(
            bucket = self.bucket,
            org    = self.org,
            record = point
        )

        self.last_saved = current_time

    def close(self):
        self.write_api.close()
        self.client.close()


"""
in the inference code;

from influxdb_handler import InfluxDBHandler

db = InfluxDBHandler()

#In the while loop, after the prediction complete its calculation,

            emotion = top1_label
            confidence = top1_conf

            db.write_prediction(
                fid,
                emotion,
                confidence,
                posture_score,
                posture,
                habit_label,
                habit_cf,
            )
"""