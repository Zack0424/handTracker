import cv2
import mediapipe as mp
import threading
import vgamepad as vg


# Define a global variable to store hand positions
steering = ()
throttle = ()





# gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
# gamepad.update()
def set_gamepad_joystick_positions(steering, throttle):
    gamepad.left_joystick_float(steering,0)

    gamepad.left_trigger(100)
    if throttle > 0:
        gamepad.right_trigger_float(throttle)
        gamepad.left_trigger_float(0)
        gamepad.update()
    if throttle < 0:
        gamepad.right_trigger_float(0)
        gamepad.left_trigger_float(-throttle)
        gamepad.update()

    if throttle == 0:
        gamepad.right_trigger_float(0)
        gamepad.left_trigger_float(0)
    gamepad.update()
    # else:
    #     gamepad.left_trigger_float(0)
    #     gamepad.right_trigger_float(0)

def hand_landmark_worker(results, frame_shape):
    global steering, throttle

    if results.multi_hand_landmarks:
        steering_visible = False
        throttle_visible = False
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Get the positions of the hand landmarks
            landmark_positions = []
            for landmark in hand_landmarks.landmark:
                x = int(landmark.x * frame_shape[1])
                y = int(landmark.y * frame_shape[0])
                landmark_positions.append((x, y))

            # Calculate the center of the hand
            hand_center = (
                sum([x for x, _ in landmark_positions]) // len(landmark_positions),
                sum([y for _, y in landmark_positions]) // len(landmark_positions)
            )
            if hand_center[0] < frame_shape[1] // 2:
                steering = (hand_center[0],240)
                steering_visible = True
            if hand_center[0] > frame_shape[1] // 2:
                throttle = (480,hand_center[1])
                throttle_visible = True
        if not steering_visible:
            steering = (160, 240)
        if not throttle_visible:
            throttle = (480, 240)

    else:
        steering = (160, 240)
        throttle = (480, 240)



def get_right_camera() -> int:

    while True:
        x = input("Please input the ID of your webcam, press q to quit: ")
        if x == "q":
            quit()
        try:
            x = int(x)
            return x
        except Exception as ex:
            print("Please input only the ID (number): ")

def get_hand_centers(camera_number = 0):
    cap = cv2.VideoCapture(camera_number)  # Open the webcam

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 60)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()

    while True:
        ret, frame = cap.read()  # Read frames from the webcam


        if not ret:
            break
        frame = cv2.flip(frame, 1)

        frame_width = frame.shape[1]
        frame_height = frame.shape[0]

        # Calculate the x-coordinate of the vertical line in the middle
        mid_x = frame_width // 2

        # Convert the image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image with the hand tracking model
        results = hands.process(image_rgb)

        # Create a thread for hand landmark calculation
        landmark_thread = threading.Thread(target=hand_landmark_worker, args=(results, frame.shape))
        landmark_thread.start()

        # Print the position and hand number
        steering_on_axis = (steering[0] - 160)/160
        throttle_on_axis = (240 - throttle[1])/240

        set_gamepad_joystick_positions(steering_on_axis,throttle_on_axis)

        print(f"steering: {steering_on_axis}, throttle: {throttle_on_axis}")

        # Draw a circle at the center of the hand
        if steering:
            cv2.circle(frame, steering, 5, (0, 255, 0), -1)
        if throttle:
            cv2.circle(frame, throttle, 5, (0, 0, 255), -1)

        # Draw a vertical line in the middle of the frame
        cv2.line(frame, (mid_x, 0), (mid_x, frame_height), (0, 0, 255), 2)

        # Display the frame with the vertical line
        cv2.imshow('Hand Tracking', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def get_all_cameras():
    index = 0
    arr = []
    while True:
        try:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                arr.append(index)
            cap.release()
            index += 1
        except IndexError:
            break
    return arr


def select_camera():
    all_cameras = get_all_cameras()
    while True:
        try:
            selected_camera = int(input(f"{all_cameras} select the camera you want to use from this list: "))
            print("Starting application!\nPlease be patient, this may take some time!")
            break
        except Exception:
            pass
    return selected_camera
if __name__ == '__main__':
    print("Thank you for using this hand tracking app!\nPlease wait a second while it checks your available cameras")
    while True:
        try:
            camera_number = select_camera()
            gamepad = vg.VDS4Gamepad()
            break
        except Exception:
            pass
    get_hand_centers(camera_number)

