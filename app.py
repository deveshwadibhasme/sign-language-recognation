import cv2
import mediapipe as mp
import pyttsx3
import time
import math

# Initialize Mediapipe & TTS
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

engine = pyttsx3.init()

def speak(text):
    """Function to speak the given text."""
    if text:
        
        engine.say(text)
        engine.runAndWait()

def get_handedness(hand_landmarks):
    """Determines if the hand is left or right."""
    if hand_landmarks.landmark[0].x > hand_landmarks.landmark[9].x:
        return "Right"
    else:
        return "Left"

def recognize_gesture(hand_landmarks):
    """
    Recognizes a gesture from the given hand landmarks.
    """
    lm = hand_landmarks.landmark
    handedness = get_handedness(hand_landmarks)

    # Finger extension status
    index_up = lm[8].y < lm[6].y
    middle_up = lm[12].y < lm[10].y
    ring_up = lm[16].y < lm[14].y
    pinky_up = lm[20].y < lm[18].y

    # Thumb status
    if handedness == "Right":
        thumb_up = lm[4].x < lm[3].x
    else: # Left Hand
        thumb_up = lm[4].x > lm[3].x

    # --- Gesture Definitions (from most specific to most general) ---

    # PLEASE: Flat hand, thumb out, fingers together.
    dist_index_pinky = math.sqrt((lm[8].x - lm[20].x)**2 + (lm[8].y - lm[20].y)**2)
    if thumb_up and index_up and middle_up and ring_up and pinky_up and dist_index_pinky < 0.1:
        return "Please"

    # AWESOME: Middle finger down, others up.
    if thumb_up and index_up and not middle_up and ring_up and pinky_up:
        return "Awesome"

    # THREE: Thumb, Index, Middle up.
    if thumb_up and index_up and middle_up and not ring_up and not pinky_up:
        return "Three"

    # QUESTION: Hooked index finger on a fist.
    index_hooked = (lm[6].y < lm[5].y) and (lm[8].y > lm[7].y)
    if not thumb_up and index_hooked and not middle_up and not ring_up and not pinky_up:
        return "Question"
        
    if not thumb_up and index_up and middle_up and ring_up and not pinky_up:
        return "Water"

    # EAT / BUNCHED HAND: Fingers and thumb bunched together.
    dist_thumb_index = math.sqrt((lm[4].x - lm[8].x)**2 + (lm[4].y - lm[8].y)**2)
    dist_thumb_middle = math.sqrt((lm[4].x - lm[12].x)**2 + (lm[4].y - lm[12].y)**2)
    if dist_thumb_index < 0.06 and dist_thumb_middle < 0.06 and not pinky_up:
        return "Eat"

    # I WANT TO TALK: Claw-like hand, fingers partially curled.
    # index_curve = math.sqrt((lm[8].x - lm[5].x)**2 + (lm[8].y - lm[5].y)**2)
    # middle_curve = math.sqrt((lm[12].x - lm[9].x)**2 + (lm[12].y - lm[9].y)**2)
    # ring_curve = math.sqrt((lm[16].x - lm[13].x)**2 + (lm[16].y - lm[13].y)**2)
    # if (0.2 < index_curve < 0.4 and
    #     0.2 < middle_curve < 0.4 and
    #     0.2 < ring_curve < 0.4 and
    #     dist_thumb_index > 0.15):
    #     return "I want to talk"

    # I LOVE YOU: Thumb, Index, Pinky are up. Middle, Ring are down.
    if thumb_up and index_up and not middle_up and not ring_up and pinky_up:
        return "I Love You"

    # VICTORY/PEACE: Index and Middle are up.
    if not thumb_up and index_up and middle_up and not ring_up and not pinky_up:
        return "Victory"

    # CALL ME: Thumb and Pinky are up. Others are down.
    if thumb_up and not index_up and not middle_up and not ring_up and pinky_up:
        return "Call me"

    # HELLO / OPEN HAND: All fingers are up.
    if thumb_up and index_up and middle_up and ring_up and pinky_up:
        return "HELLO"
        
    # OKAY: Index, Middle, Ring, Pinky are up. Thumb tip is close to index tip.
    if not thumb_up and index_up and middle_up and ring_up and pinky_up and dist_thumb_index < 0.1:
        return "Okay"

    # YES / THUMBS UP: Thumb is up, other four fingers are folded.
    thumb_vertically_up = lm[4].y < lm[2].y
    if thumb_vertically_up and not index_up and not middle_up and not ring_up and not pinky_up:
        return "YES"

    # NO / THUMBS DOWN: Thumb is pointing down, other four fingers are folded.
    thumb_vertically_down = lm[4].y > lm[2].y
    if thumb_vertically_down and not index_up and not middle_up and not ring_up and not pinky_up:
        return "NO"

    # HELP / FIST: All fingers are folded.
    if not thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
        return "HELP"
        
    # POINTING: Index finger is up, others are down.
    if not thumb_up and index_up and not middle_up and not ring_up and not pinky_up:
        return "Pointing"


    return None


# --- Main Application Logic ---
# input_to_take = "http://192.168.15.193:4747/video"
input_to_take = 1 # Use 0 for webcam, 1 for DroidCam, etc.

cap = cv2.VideoCapture(input_to_take, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

last_gesture = None
gesture_start_time = 0
last_spoken_time = 0
speak_delay = 3   # seconds to wait before repeating a gesture
hold_time = 1     # seconds a gesture must be held to be recognized

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame. Check camera connection.")
        time.sleep(1)
        continue
    
    img = cv2.flip(img, 1) # Flip horizontally for a mirror-view
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    current_gesture = None
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            current_gesture = recognize_gesture(hand_landmarks)

    current_time = time.time()

    if current_gesture:
        # If the gesture is new, reset the timer
        if current_gesture != last_gesture:
            gesture_start_time = current_time
            last_gesture = current_gesture
        
        # If gesture has been held long enough
        elif current_time - gesture_start_time >= hold_time:
            # And if enough time has passed since the last spoken word
            if current_time - last_spoken_time > speak_delay:
                speak(current_gesture)
                last_spoken_time = current_time # Reset speak timer

        # Display the currently detected gesture
        cv2.putText(img, current_gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        print(f"Detected: {current_gesture}")

    else:
        # If no gesture is detected, reset the state
        last_gesture = None
        gesture_start_time = 0

    cv2.imshow("Sign Language to Speech", img)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
