from flask import Flask, render_template
from flask_socketio import SocketIO
from ultralytics import YOLO
import cv2
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import logging
import time
from queue import Queue
from threading import Thread

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory task queue
task_queue = Queue()

# Load the YOLO model once at startup
model = YOLO("./best.pt")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def decode_frame(base64_frame):
    """Decode a base64 string to a numpy array (OpenCV image)."""
    try:
        img_data = base64.b64decode(base64_frame)
        return cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        logging.error(f"Error decoding frame: {e}")
        return None

def encode_frame(image):
    """Encode a numpy array (OpenCV image) to base64."""
    try:
        pil_img = Image.fromarray(image)
        buffer = BytesIO()
        pil_img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error encoding frame: {e}")
        return None

def process_frame(frame_data):
    """Process a frame using YOLO and return an annotated base64-encoded frame."""
    frame = decode_frame(frame_data)
    if frame is None:
        raise ValueError("Invalid frame data")

    results = model(frame)
    annotated_image = results[0].plot()

    return encode_frame(annotated_image)

def process_and_emit():
    """Process tasks in the queue and emit results to the client."""
    while True:
        # Wait for a task to process
        frame_data = task_queue.get()
        if frame_data is None:  # Shutdown signal
            break
        try:
            annotated_frame = process_frame(frame_data)
            if annotated_frame:
                socketio.emit('annotated_frame', {'frame': annotated_frame})
            else:
                raise ValueError("Processing returned no annotated frame")
        except Exception as e:
            logging.error(f"Error processing frame: {e}")
            socketio.emit('error', {'message': f"Error processing frame: {str(e)}"})

@socketio.on('frame')
def handle_frame(frame_data):
    """Handle incoming frame data from the client."""
    logging.info("Received a new frame for processing")
    # Add the frame data to the task queue for background processing
    task_queue.put(frame_data)

    # Ensure the task processing is running in the background
    if not hasattr(handle_frame, 'task_thread'):
        handle_frame.task_thread = Thread(target=process_and_emit)
        handle_frame.task_thread.daemon = True
        handle_frame.task_thread.start()

@app.route('/')
def index():
    """Render the main webpage."""
    return render_template('index.html')

if __name__ == "__main__":
    logging.info("Starting Flask-SocketIO app...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
