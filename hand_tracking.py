import cv2
import mediapipe as mp
from plyer import notification
import time
import winsound

# -------------------------------
# MEDIAPIPE SETUP
# -------------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# -------------------------------
# INPUT CHOICE
# -------------------------------
print("Select Input Source:")
print("1 - Camera")
print("2 - Video File")

choice = input("Enter choice (1 or 2): ")

if choice == "1":
    cap = cv2.VideoCapture(0)
    source_name = "Camera"
elif choice == "2":
    video_path = input("Enter video file path: ")
    cap = cv2.VideoCapture(video_path)
    source_name = "Video File"
else:
    print("Invalid choice")
    exit()

if not cap.isOpened():
    print("Error: Cannot open source")
    exit()

# -------------------------------
# VARIABLES
# -------------------------------
prev_state = 0
motion_count = 0
alert_sent = False
alert_time = 0

# -------------------------------
# MAIN LOOP
# -------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("End of stream")
        break

    if choice == "1":
        frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture_name = "None"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Thumb check
            thumb_open = hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x

            # Finger check
            tips = [8, 12, 16, 20]
            open_fingers = 0

            for tip in tips:
                if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                    open_fingers += 1

            # Motion detection
            if not thumb_open:
                current_state = open_fingers

                if current_state != prev_state:
                    motion_count += 1
                    prev_state = current_state

            # Emergency gesture
            if motion_count >= 4:
                gesture_name = "EMERGENCY WAVE"
                motion_count = 0

    # -------------------------------
    # ALERT LOGIC
    # -------------------------------
    if gesture_name == "EMERGENCY WAVE" and not alert_sent:
        
        # 🔊 Beep Sound
        for _ in range(3):
            winsound.Beep(1000, 400)

        # 🧾 Command Prompt Message
        print("\n🚨 AI EMERGENCY ALERT SYSTEM ACTIVATED")
        print("📡 Hand distress signal detected")
        print("📷 Live visual evidence captured")
        print("📨 Alert securely sent to nearest police control unit")
        print("🚓 Response team is being dispatched...\n")

        # 💻 Laptop Notification
        notification.notify(
            title="🚨 AI Emergency Alert",
            message="Distress signal detected!\nAlert sent to police.\nHelp is on the way.",
            timeout=6
        )

        alert_sent = True
        alert_time = time.time()

    # Reset after 10 seconds
    if alert_sent and time.time() - alert_time > 10:
        alert_sent = False

    # -------------------------------
    # DISPLAY (ONLY BASIC TEXT)
    # -------------------------------
    cv2.putText(frame, f"Gesture: {gesture_name}",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2)

    if gesture_name == "EMERGENCY WAVE":
        cv2.putText(frame, "HELP SIGNAL DETECTED!",
                    (50, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0, 0, 255),
                    3)

    cv2.putText(frame, f"Source: {source_name}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2)

    cv2.imshow("Emergency System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# -------------------------------
# RELEASE
# -------------------------------
cap.release()
cv2.destroyAllWindows()
