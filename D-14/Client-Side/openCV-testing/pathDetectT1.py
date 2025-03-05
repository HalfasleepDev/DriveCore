import cv2
import numpy as np

#Path detection local test

# URL of video stream
VIDEO_URL = "http://192.168.1.100:5000/video-feed"  # use the flask stream from the raspberry pi

# Open video stream
cap = cv2.VideoCapture(VIDEO_URL)

if not cap.isOpened():
    print("Error: Unable to connect to the video stream.")
    exit()

def process_frame(frame):
    """Processes a single frame for path detection."""
    frame = cv2.resize(frame, (640, 480))  # Resize for consistency
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # Reduce noise

    # Edge Detection
    edges = cv2.Canny(blurred, 50, 150)

    # Convert to HSV for color-based path detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define color range for path detection (Adjust as needed)
    lower_bound = np.array([20, 100, 100])  # Example: Yellow path
    upper_bound = np.array([40, 255, 255])

    # Create a mask for the path
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Combine edges and color mask
    combined = cv2.bitwise_or(edges, mask)

    # Find contours
    contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw detected path
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 3)  # Green path outline

        # Fit a polynomial curve for a smooth path
        points = np.array(largest_contour).reshape(-1, 2)
        if len(points) > 5:  # Ensure we have enough points for fitting
            fit = np.polyfit(points[:, 1], points[:, 0], 2)  # Quadratic fit
            y_vals = np.linspace(min(points[:, 1]), max(points[:, 1]), num=50)
            x_vals = np.polyval(fit, y_vals)

            # Draw the fitted curve
            for i in range(len(x_vals) - 1):
                cv2.line(frame, (int(x_vals[i]), int(y_vals[i])), (int(x_vals[i + 1]), int(y_vals[i + 1])), (255, 0, 0), 2)  # Blue smooth path

    return frame, edges, mask

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to receive frame.")
        break

    processed_frame, edges, mask = process_frame(frame)

    # Display the results
    cv2.imshow("Original Video", processed_frame)
    cv2.imshow("Edge Detection", edges)
    cv2.imshow("Color Mask", mask)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
