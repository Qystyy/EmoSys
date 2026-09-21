"""
InfluxDB handler (Raspberry Pi 5 side) - updated 10/9/2026

Usage:
- To send output data from the model into the influxbd
- The data is mostly for reference without the usage of log
- The captured image will NOT be stored
- The current URL is the IP of the PI_1 where the main bucket is in
- The token is the generated token of the main bucket
    - It is limited to read and write for the emotionDB bucket
- Data being stored are:
    - Device ID
    - Face_ID
    - Emotion
    - Emotion Confidence Level
    - Posture
    - Posture Score
    - Gesture
    - Gesture Confidence Level

- A circuit breaker is added to avoid time waste
- Data is stored every 5 sec interval

Inference code implementation:

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
                gesture,
                gesture_confidence,
            )

"""


from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import threading
import time

class InfluxDBHandler:
    
    def __init__(self):
        self.url    = "<configure separately>"
        self.token  = "<configure separately>"
        self.org    = "EmoSys"
        self.bucket = "emotionDB"

        self.client = InfluxDBClient(
            url    = self.url,
            token  = self.token,
            org    = self.org,
            timeout = 2000  # 2 second timeout to fail fast
        )

        self.write_api  = self.client.write_api(
            write_options = SYNCHRONOUS
        )

        # Use a dictionary to track the last saved time for EACH face ID independently
        self.last_saved_per_face = {}
        self.interval = 5 # seconds

        # Circuit breaker: stop trying after N consecutive failures
        self._fail_count = 0
        self._max_failures = 3
        self._disabled = False

    def _write_async(self, face_id, emotion, confidence, point):
        """Runs in a background thread — never blocks the main loop."""
        try:
            self.write_api.write(
                bucket = self.bucket,
                org    = self.org,
                record = point
            )
            self.last_saved_per_face[face_id] = time.time()
            self._fail_count = 0  # reset on success
        except Exception as e:
            self._fail_count += 1
            if self._fail_count >= self._max_failures:
                self._disabled = True
                print(f"InfluxDB disabled after {self._max_failures} consecutive failures.")

    def write_prediction(self, face_id, emotion, confidence, posture_score, posture, gesture, gesture_confidence):

        if self._disabled:
            return

        current_time = time.time()
        
        # Check if this specific face ID exists in the dictionary and if it's on cooldown
        last_saved = self.last_saved_per_face.get(face_id, 0)
        
        if current_time - last_saved < self.interval:
            return

        # Mark as saved immediately so concurrent frames don't double-fire
        self.last_saved_per_face[face_id] = current_time

        point = (
            Point("FER Prediction")
            .tag("device", "pi_1")
            .tag("face_id", str(face_id))
            .field("emotion", emotion)
            .field("confidence", float(confidence))
            .field("posture_score", float(posture_score))
            .field("posture", posture)
            .field("gesture", gesture)
            .field("gesture_confidence", float(gesture_confidence))
        )

        # Fire-and-forget: write in a background daemon thread so the
        # camera loop is never blocked by network latency.
        t = threading.Thread(
            target = self._write_async,
            args   = (face_id, emotion, confidence, point),
            daemon = True   # thread dies automatically when main process exits
        )
        t.start()

    def close(self):
        self.write_api.close()
        self.client.close()

