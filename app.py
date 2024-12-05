from flask import Flask, render_template, Response
from ultralytics import YOLO
import cv2
import numpy as np

app = Flask(__name__)

# Load YOLO model
model = YOLO(r"./best.pt")

# Initialize webcam
cap = cv2.VideoCapture(0)


def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # YOLO inference
        results = model(frame)
        annotated_image = results[0].plot()

        if annotated_image is None or not isinstance(annotated_image, np.ndarray):
            print("Annotated image is invalid!")
            continue

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_image)
        frame = buffer.tobytes()

        # Yield as a byte stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Route to serve the video feed."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/harsh")
def hars():
    return "harshhhhhh"

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
