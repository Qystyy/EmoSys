"""
PERSONAL ARCHIVE PURPOSES
"""

import cv2
from picamera2 import Picamera2 
import time
import numpy as np

print("Opening camera...")
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)}
))
picam2.start()
time.sleep(3)

picam2.set_controls({
    "AeEnable": True,
    "AwbEnable": True
})

print("Camera started")

while True:

    # Capture frame from Picamera2
    frame = picam2.capture_array()
    # colour calibration fix for the green hue for picam 1 (remove is not needed)
    matrix = np.array([
        [1.0,  0.0,  0.0],
        [0.0,  0.85, 0.0],
        [0.0,  0.0,  1.0]
    ])

    frame = cv2.transform(frame, matrix)   

    cv2.imshow("testing", frame)
        
    if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q')]:
        print("End Program...")
        break
        
picam2.stop()
cv2.destroyAllWindows()
