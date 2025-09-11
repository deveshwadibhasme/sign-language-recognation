import cv2
import mediapipe as mp
import pyttsx3
import time

# Initialize Mediapipe & TTS
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)  # detect 1 hand for simplicity
mp_draw = mp.solutions.drawing_utils

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def recognize_gesture(hand_landmarks):
    # Thumb
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]

    # Index
    index_tip = hand_landmarks.landmark[8]
    index_pip = hand_landmarks.landmark[6]

    # Middle
    middle_tip = hand_landmarks.landmark[12]
    middle_pip = hand_landmarks.landmark[10]

    # Ring
    ring_tip = hand_landmarks.landmark[16]
    ring_pip = hand_landmarks.landmark[14]

    # Pinky
    pinky_tip = hand_landmarks.landmark[20]
    pinky_pip = hand_landmarks.landmark[18]

    # Determine if fingers are folded 
    index_folded = index_tip.y > index_pip.y
    middle_folded = middle_tip.y > middle_pip.y
    ring_folded = ring_tip.y > ring_pip.y
    pinky_folded = pinky_tip.y > pinky_pip.y
    thumb_folded = thumb_tip.x > thumb_ip.x # For a right hand

    # 👋 Open Hand (HELLO) = all fingers raised
    if (index_tip.y < index_pip.y and
        middle_tip.y < middle_pip.y and
        ring_tip.y < ring_pip.y and
        pinky_tip.y < pinky_pip.y):
        return "HELLO"

    # HELP = fist
    elif index_folded and middle_folded and ring_folded and pinky_folded and thumb_folded:
        return "HELP"

    # 👍 YES = all fingers folded + thumb up
    elif index_folded and middle_folded and ring_folded and pinky_folded and thumb_tip.y < thumb_ip.y:
        return "YES"

    # 👎 NO = all fingers folded + thumb down
    elif index_folded and middle_folded and ring_folded and pinky_folded and thumb_tip.y > thumb_ip.y:
        return "NO"
    
    elif index_tip.y < index_pip.y and middle_folded and ring_folded and pinky_tip.y < pinky_pip.y:
        return "Thank You"

    else:
        return None

# Open camera
cap = cv2.VideoCapture(0)

last_gesture = None
gesture_start_time = 0
last_spoken_time = 0
speak_delay = 4   
hold_time = 1   # gesture must be held this long to count

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    gesture = None
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = recognize_gesture(hand_landmarks)

    if gesture:
        cv2.putText(img, gesture, (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (0, 255, 0), 3)
        print("Detected:", gesture)

        current_time = time.time()

        # if gesture changes, reset timer
        if gesture != last_gesture:
            gesture_start_time = current_time
            last_gesture = gesture

        # only accept gesture if held for hold_time
        if current_time - gesture_start_time > hold_time:
            if current_time - last_spoken_time > speak_delay:
                speak(gesture)
                last_spoken_time = current_time

    cv2.imshow("Sign Language to Speech", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
