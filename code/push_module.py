"""
Push Module - updated 10/9/2026

Usage:
- Connection with the main dashboard to POST data from raspberry Pi 5
- Data being push:
    - Emotions
    - Emotions confidence level
    - Gesture 
    - Gesture confidence level
- Device ID is the ID of current raspberry Pi 5
- The url is the Dashboard URL; where the data will be outputted
- The Token is the restAPI to send data to raspberry Pi [Dashboard]
- The data will later be stored in the Main Dashboard InfluxDB
- The image from the Raspberry Pi will be deleted immediately after being push to the dashboard
- While in the dashboard, the image will be in cache form and deleted after 30 minutes

To paste in the inference code:
from push_module import push_result

push_result(detected_emotion, confidence_score, frame_jpeg_bytes, inf_speed, gesture_cf, gesture_label)
# the name in the () is based on what you assign in the code
"""


import requests
from enum import Enum

PI5_URL = "http://10.0.30.7:3000/api/emotion/ingest"
TOKEN   = "e591962c78716e9fbd2677d2125b2375"


def push_result (emotion, confidence, frame_jpeg_bytes, inference_speed_ms, gesture, gesture_score):
    files = {
        'image': ('frame.jpg', frame_jpeg_bytes, 'image/jpeg')
        }
    data  = {
        'emotion'          : emotion,
        'confidence'       : confidence,
        'inferenceSpeedMs' : inference_speed_ms,
        'gestureLabel'     : gesture,
        'gestureScore'     : gesture_score,
        'deviceId'         : 'pi_1',
        'modelVersion'     : 'v1'
    } 

    headers = {'x-emotion-token': TOKEN}

    try:
        r = requests.post(PI5_URL, files=files, data=data, headers=headers, timeout=5)
        print(f"Pushed: {r.status_code} {r.text}")
    except requests.RequestException as e:
        print(f"Push failed: {e}")

