# **🖐️ Gesture Control for macOS Menu Bar**

This Python application uses computer vision (MediaPipe) to detect specific hand gestures and translate them into system actions on macOS, primarily focusing on media control for **Spotify** and system controls for **Volume** and **Brightness**. It runs silently in your macOS Menu Bar (using rumps).

## **🚀 Features**

The application controls the following system and media actions:

| Category | Action | Gesture | Description |
| :---- | :---- | :---- | :---- |
| **System Toggle** | Pause/Resume | **Open Palm (✋)** | Toggles the gesture processing ON/OFF without quitting the app. Shows ⏸️ when paused. |
| **Volume Control** | Volume Up | **Index Finger Up (☝️)** | Index finger extended, held high in the camera frame (top 30%). |
| **Volume Control** | Volume Down | **Closed Fist (✊)** | All fingers curled into a fist. |
| **Volume Control** | Toggle Mute | **Rock-n-Roll (🤘)** | Thumb, Index, and Pinky extended (Middle and Ring curled). |
| **Media Control** | Next Track | **Thumbs Up (👍)** | Thumb extended and pointing upwards. |
| **Media Control** | Previous Track | **Thumbs Down (👎)** | Thumb extended and pointing downwards. |
| **Media Control** | Play/Pause | **Three Fingers (🤟)** | Index, Middle, and Ring fingers extended (Thumb and Pinky curled). |
| **Media Control** | Open Spotify | **Four Fingers (✋)** | Index, Middle, Ring, and Pinky extended (Thumb curled). |
| **System Control** | Brightness Up | **Two Fingers (👈)** | Index and Middle fingers extended, hand held on the **left side** of the frame. |
| **System Control** | Brightness Down | **Two Fingers (👉)** | Index and Middle fingers extended, hand held on the **right side** of the frame. |

## **⚙️ Prerequisites**

This application requires Python 3.x and is designed exclusively for **macOS** due to the use of AppleScript commands.

### **Installation**

1. Install Python Libraries:  
   You need OpenCV (for camera access), MediaPipe (for hand tracking), rumps (for the menu bar interface), and standard system libraries.  
   pip3 install opencv-python mediapipe rumps

2. Save the Code:  
   Save the provided Python script as gesture\_mac.py.

## **▶️ How to Run**

Execute the script from your terminal:

python3 gesture\_mac.py

### **Initial State**

Upon running, the application:

1. Initializes in the Menu Bar with a **🟢** icon, indicating it is active and running.  
2. Automatically starts the camera thread in the background.

## **⚠️ Important Notes on Usage**

* **Cooldowns:** Most gestures (especially media and app-launch) have a 1.0 second cooldown (COOLDOWN\_TIME) to prevent rapid, accidental triggers.  
* **Directional Controls:** The directional gestures (Volume Up/Down, Brightness Up/Down) execute commands continuously as long as the hand is held in the designated zone.  
* **Media Focus:** The media controls (playpause, next, prev) are hard-coded to interact specifically with the **Spotify** application via AppleScript.  
* **Troubleshooting:** If the app isn't detecting hands, ensure your camera is not being used by another application and that the lighting is good.