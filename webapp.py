import cv2
import mediapipe as mp
import time
import math
import queue
from flask import Flask, render_template, Response

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Core Application Setup ---
# A thread-safe queue to hold gesture text for the SSE stream
gesture_queue = queue.Queue()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# --- Gesture Recognition Logic (remains the same) ---
def get_handedness(hand_landmarks):
    if hand_landmarks.landmark[0].x > hand_landmarks.landmark[9].x:
        return "Right"
    else:
        return "Left"

def recognize_gesture(hand_landmarks):
    lm = hand_landmarks.landmark
    handedness = get_handedness(hand_landmarks)

    index_up = lm[8].y < lm[6].y
    middle_up = lm[12].y < lm[10].y
    ring_up = lm[16].y < lm[14].y
    pinky_up = lm[20].y < lm[18].y

    if handedness == "Right":
        thumb_up = lm[4].x < lm[3].x
    else: # Left Hand
        thumb_up = lm[4].x > lm[3].x

    dist_index_pinky = math.sqrt((lm[8].x - lm[20].x)**2 + (lm[8].y - lm[20].y)**2)
    if thumb_up and index_up and middle_up and ring_up and pinky_up and dist_index_pinky < 0.1:
        return "Please"

    if thumb_up and index_up and not middle_up and ring_up and pinky_up:
        return "Awesome"

    if thumb_up and index_up and middle_up and not ring_up and not pinky_up:
        return "Three"

    # index_hooked = (lm[6].y < lm[5].y) and (lm[8].y > lm[7].y)
    # if not thumb_up and index_hooked and not middle_up and not ring_up and not pinky_up:
    #     return "Question"
        
    if not thumb_up and index_up and middle_up and ring_up and not pinky_up:
        return "Water"

    dist_thumb_index = math.sqrt((lm[4].x - lm[8].x)**2 + (lm[4].y - lm[8].y)**2)
    dist_thumb_middle = math.sqrt((lm[4].x - lm[12].x)**2 + (lm[4].y - lm[12].y)**2)
    if dist_thumb_index < 0.06 and dist_thumb_middle < 0.06 and not pinky_up:
        return "Eat"

    # index_curve = math.sqrt((lm[8].x - lm[5].x)**2 + (lm[8].y - lm[5].y)**2)
    # middle_curve = math.sqrt((lm[12].x - lm[9].x)**2 + (lm[12].y - lm[9].y)**2)
    # if (0.2 < index_curve < 0.4 and 0.2 < middle_curve < 0.4 and dist_thumb_index > 0.15):
    #     return "I want to talk"

    if thumb_up and index_up and not middle_up and not ring_up and pinky_up:
        return "Thank You"

    if not thumb_up and index_up and middle_up and not ring_up and not pinky_up:
        return "Victory"

    if thumb_up and not index_up and not middle_up and not ring_up and pinky_up:
        return "Call me"

    if thumb_up and index_up and middle_up and ring_up and pinky_up:
        return "HELLO"
        
    if not thumb_up and index_up and middle_up and ring_up and pinky_up and dist_thumb_index < 0.1:
        return "Okay"

    thumb_vertically_up = lm[4].y < lm[2].y
    if thumb_vertically_up and not index_up and not middle_up and not ring_up and not pinky_up:
        return "YES"

    thumb_vertically_down = lm[4].y > lm[2].y
    if thumb_vertically_down and not index_up and not middle_up and not ring_up and not pinky_up:
        return "NO"

    if not thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
        return "HELP"
        
    if not thumb_up and index_up and not middle_up and not ring_up and not pinky_up:
        return "Pointing"

    return None

# --- Video and Gesture Processing ---
def video_processing():
    """Processes video, recognizes gestures, and puts them in a queue."""
    last_gesture = None
    gesture_start_time = 0
    hold_time = 1
    
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, img = cap.read()
        if not success:
            continue
        
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        current_gesture = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                current_gesture = recognize_gesture(hand_landmarks)

        current_time = time.time()
        if current_gesture:
            if current_gesture != last_gesture:
                gesture_start_time = current_time
                last_gesture = current_gesture
            elif current_time - gesture_start_time >= hold_time:
                # Put gesture in queue for SSE stream, ensuring not to repeat too fast
                if gesture_queue.empty():
                    gesture_queue.put(current_gesture)
                # Reset timer to enforce delay between spoken words
                gesture_start_time = current_time

            cv2.putText(img, current_gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            last_gesture = None

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_processing(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/gesture_events')
def gesture_events():
    def stream():
        while True:
            try:
                # Block until a gesture is available
                gesture = gesture_queue.get(timeout=1)
                yield f"data: {gesture}\n\n"
            except queue.Empty:
                # If queue is empty, continue waiting
                continue
    return Response(stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)