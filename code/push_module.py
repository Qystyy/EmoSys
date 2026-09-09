import requests
from enum import Enum

PI5_URL = "http://10.0.30.7:3000/api/emotion/ingest"
TOKEN   = "e591962c78716e9fbd2677d2125b2375"

#def push_result (emotion, confidence, frame_jpeg_bytes, inference_speed_ms, posture_score, posture_label, habit_label, habit_cf):
def push_result (emotion, confidence, frame_jpeg_bytes, inference_speed_ms, gesture_score, gesture_label):
    files = {
        'image': ('frame.jpg', frame_jpeg_bytes, 'image/jpeg')
        }
    data  = {
        'emotion'          : emotion,
        'confidence'       : confidence,
        'inferenceSpeedMs' : inference_speed_ms,
        'gestureScore'     : gesture_score,
        'gestureLabel'     : gesture_label,
        #'postureScore'     : posture_score,
        #'postureLabel'     : posture_label,
        #'habitLabel'       : habit_label.value if isinstance(habit_label, Enum) else habit_label,
        #'habitScore'       : habit_cf,
        'deviceId'         : 'pi_1',
        'modelVersion'     : 'v1'
    } 

    headers = {'x-emotion-token': TOKEN}

    try:
        r = requests.post(PI5_URL, files=files, data=data, headers=headers, timeout=5)
        print(f"Pushed: {r.status_code} {r.text}")
    except requests.RequestException as e:
        print(f"Push failed: {e}")

#push_result(detected_emotion, confidence_score, current_frame_jpeg_bytes)
# call for send frames to server

