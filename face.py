import cv2
import mediapipe as mp

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Style for drawing the dots (landmarks)
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))

# Initialize video capture from the default camera

input_to_take = 0 # Use 0 for webcam, 1 for DroidCam, etc.

video_capture  = cv2.VideoCapture(input_to_take, cv2.CAP_DSHOW)
video_capture .set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_capture .set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Starting camera feed. Press 'q' to exit.")

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame. Exiting.")
        break

    # Flip the image horizontally for a mirror-like view
    frame = cv2.flip(frame, 1)
    
    # Convert the BGR image to RGB for Mediapipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and find face landmarks
    results = face_mesh.process(rgb_frame)

    # If face landmarks are detected, draw them on the frame
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Draw only the landmark dots, not the connecting lines
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=None,  # Set to None to avoid drawing connections
                landmark_drawing_spec=drawing_spec)

    # Display the resulting frame
    cv2.imshow('Face Landmarks', frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# Release the capture and destroy all windows
video_capture.release()
cv2.destroyAllWindows()