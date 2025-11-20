import cv2
import mediapipe as mp
import rumps
import threading
import time
import subprocess

# --- CONFIGURATION ---
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CONFIDENCE_THRESHOLD = 0.7
COOLDOWN_TIME = 1.0  # Seconds between triggers (for media/app launch)

class GestureControlApp(rumps.App):
    def __init__(self):
        # Initial menu bar icon is the Hand emoji
        super(GestureControlApp, self).__init__("🖐️", quit_button="Quit App")
        self.menu = ["Start Camera", "Stop Camera", None]
        self.running = False           # Controls the camera thread (App running state)
        self.gestures_active = True    # Controls gesture processing (Pause/Resume state)
        self.thread = None
        self.last_trigger_time = 0     # Cooldown timer
        
        # MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        
        # Start automatically
        self.start_camera(None)

    @rumps.clicked("Start Camera")
    def start_camera(self, _):
        if not self.running:
            self.running = True
            self.title = "🟢"  # Green circle = Active
            self.thread = threading.Thread(target=self.run_vision_loop, daemon=True)
            self.thread.start()

    @rumps.clicked("Stop Camera")
    def stop_camera(self, _):
        self.running = False
        self.title = "🔴"  # Red circle = Inactive

    def update_status(self, emoji):
        """Briefly updates the menu bar icon to show the detected gesture."""
        self.title = emoji
        # Reset to Green after 1 second if the system is still running/active
        threading.Timer(1.0, lambda: setattr(self, 'title', "🟢") if self.running and self.gestures_active else None).start()

    # --- SYSTEM COMMANDS (Using AppleScript for Mac control) ---
    def run_applescript(self, script):
        subprocess.run(["osascript", "-e", script])

    def change_volume(self, direction):
        # We increase the volume step from 5 to 10 for faster feedback.
        # This is the only change needed here.
        script = f"set volume output volume (output volume of (get volume settings) {direction} 10)" 
        self.run_applescript(script)

    def change_brightness(self, direction):
        # direction: "+" or "-" (maps to high/low key codes)
        key_code = 144 if direction == "+" else 145
        script = f'''
        tell application "System Events"
            key code {key_code}
        end tell
        '''
        self.run_applescript(script)

    def media_control(self, action):
        """Controls Spotify explicitly."""
        app_name = "Spotify"
        
        if action == "playpause":
            script = f'tell application "{app_name}" to playpause'
        elif action == "next":
            script = f'tell application "{app_name}" to next track'
        elif action == "prev":
            script = f'tell application "{app_name}" to previous track'

        self.run_applescript(script)

    def open_spotify(self):
        """Opens the Spotify application."""
        subprocess.run(["open", "-a", "Spotify"])

    # --- GESTURE LOGIC HELPERS ---
    def count_fingers(self, lm):
        """Returns a list of 5 booleans (True if finger is extended)."""
        fingers = []
        tips = [4, 8, 12, 16, 20]
        
        # Thumb: Checks X axis for right-hand detection (simplified)
        if lm[tips[0]].x < lm[tips[0] - 1].x: 
            fingers.append(True)
        else:
            fingers.append(False)

        # 4 Fingers: Check Y axis (Tip above PIP joint)
        for id in range(1, 5):
            if lm[tips[id]].y < lm[tips[id] - 2].y:
                fingers.append(True)
            else:
                fingers.append(False)
        return fingers

    # --- MAIN VISION LOOP ---
    def run_vision_loop(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, CAMERA_WIDTH)
        cap.set(4, CAMERA_HEIGHT)

        with self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=CONFIDENCE_THRESHOLD,
            min_tracking_confidence=0.5) as hands:

            while self.running:
                success, img = cap.read()
                if not success:
                    time.sleep(0.1)
                    continue

                img.flags.writeable = False
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = hands.process(img)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        lm_list = hand_landmarks.landmark
                        fingers = self.count_fingers(lm_list)
                        total_fingers = fingers.count(True)

                        # --- RECOGNITION LOGIC ---
                        current_time = time.time()
                        
                        # 0. STOP/RESUME TOGGLE (Five Fingers Spread)
                        if total_fingers == 5:
                            if current_time - self.last_trigger_time > COOLDOWN_TIME:
                                self.gestures_active = not self.gestures_active
                                
                                if self.gestures_active:
                                    self.update_status("✅") # Active
                                else:
                                    self.title = "⏸️" # Paused (Don't auto-reset title)
                                    
                                self.last_trigger_time = current_time
                                continue # Skip all other checks this frame

                        # Stop all other processing if paused
                        if not self.gestures_active:
                            continue 
                            
                        # 1. Thumbs Up (Next Song)
                        if fingers[0] and total_fingers == 1 and lm_list[4].y < lm_list[3].y:
                             if current_time - self.last_trigger_time > COOLDOWN_TIME:
                                self.update_status("👍")
                                self.media_control("next")
                                self.last_trigger_time = current_time

                        # 2. Thumbs Down (Previous Song)
                        elif fingers[0] and total_fingers == 1 and lm_list[4].y > lm_list[3].y:
                             if current_time - self.last_trigger_time > COOLDOWN_TIME:
                                self.update_status("👎")
                                self.media_control("prev")
                                self.last_trigger_time = current_time

                        # 3. Three Fingers (Play/Pause)
                        elif fingers[1] and fingers[2] and fingers[3] and not fingers[4]:
                            if current_time - self.last_trigger_time > COOLDOWN_TIME:
                                self.update_status("🤟")
                                self.media_control("playpause")
                                self.last_trigger_time = current_time

                        # 4. Four Fingers (Open Spotify)
                        elif total_fingers == 4 and not fingers[0]: # Thumb folded
                            if current_time - self.last_trigger_time > COOLDOWN_TIME:
                                self.update_status("✋")
                                self.open_spotify()
                                self.last_trigger_time = current_time

                        # 5. Volume Control (Index Finger Only)
                        # 5. Volume Control (Index Finger Only)
                        elif fingers[1] and total_fingers == 1:
                            y_pos = lm_list[8].y # Landmark 8 is the tip of the Index Finger
                            
                            # Volume UP: Index finger is in the top portion of the camera view
                            if y_pos < 0.3: # Top of screen
                                self.update_status("☝️")
                                self.change_volume("+")
                            
                            # Volume DOWN: Index finger is in the bottom portion of the camera view
                            # 5.b. Volume DOWN (NEW GESTURE: Closed Fist ✊)
                        elif total_fingers == 0:
                            self.update_status("🤘")
                            self.change_volume("-")

                        # 6. Brightness (Two Fingers)
                        elif fingers[1] and fingers[2] and total_fingers == 2:
                            x_pos = lm_list[8].x
                            
                            # Brightness INCREASE (Hand is on the left side of the frame)
                            # User moves hand RIGHT, hand appears on Left side (x_pos < 0.3)
                
                time.sleep(0.05) 

        cap.release()

if __name__ == "__main__":
    app = GestureControlApp()
    app.run()