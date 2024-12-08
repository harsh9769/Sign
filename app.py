from flask import Flask, render_template
from flask_socketio import SocketIO
from ultralytics import YOLO
import cv2
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import logging
import redis

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", message_queue="redis://redis:6379")  # Use Redis service name

# Redis connection
redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

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


@socketio.on('frame')
def handle_frame(frame_data):
    """Handle incoming frame data from the client."""
    logging.info("Received a new frame for processing")
    task_id = f"frame_task_{redis_client.incr('task_id')}"
    redis_client.set(task_id, frame_data)
    socketio.start_background_task(target=process_and_emit, task_id=task_id)


def process_and_emit(task_id):
    """Process the frame from Redis and emit the result to the client."""
    try:
        frame_data = redis_client.get(task_id)
        if not frame_data:
            raise ValueError("No frame data found in Redis")

        annotated_frame = process_frame(frame_data)
        if annotated_frame:
            socketio.emit('annotated_frame', {'frame': annotated_frame})
        else:
            raise ValueError("Processing returned no annotated frame")
    except Exception as e:
        logging.error(f"Error processing frame: {e}")
        socketio.emit('error', {'message': f"Error processing frame: {str(e)}"})
    finally:
        redis_client.delete(task_id)


@app.route('/')
def index():
    """Render the main webpage."""
    return render_template('index.html')


if __name__ == "__main__":
    logging.info("Starting Flask-SocketIO app...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
