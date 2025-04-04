import threading
from flask import Flask, Response
from picamera2 import Picamera2
import cv2

from getIpAddr import get_local_ip

app = Flask(__name__)

# Initialize camera
camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (1280, 720)}))
camera.start()

HOST = get_local_ip()

def generate_frames():
    """ Continuously capture frames and send them as an MJPEG stream. """
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video-feed')
def video_feed():
    """ Flask route for live video streaming """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    """ Run Flask server in a separate thread. """
    app.run(host=HOST, port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    # Keep the main program running
    try:
        while True:
            pass  # Other code or logic can run here
    except KeyboardInterrupt:
        print("\nShutting down Flask server...")
