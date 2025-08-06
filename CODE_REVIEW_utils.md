import sys # Provides access to system-specific parameters and functions (e.g., sys.exit())
import face_recognition # Face recognition based on dlib — used for detecting and encoding faces
from concurrent.futures import ThreadPoolExecutor # For running cheat detection and face recognition concurrently
import cv2 # OpenCV library for video capture and image processing
import mediapipe as mp # Google's ML pipeline for face, pose, and hand tracking
import numpy as np # For handling image data arrays and numerical operations
import time # For delays, timestamps, and measuring duration
import math # Advanced math operations (e.g., floor, ceil)
import random # For generating random numbers (used in gamification)
import os # Interact with the operating system (file paths, environment)
import json # Read/write JSON files (used for storing results and logs)
import shutil # High-level file operations (copying/moving files)
import keyboard # Detects and handles keyboard activity (prohibited shortcut detection)
import pyautogui # GUI automation (e.g., screenshots, cursor location)
import pygetwindow as gw # Used to interact with and monitor open windows (e.g., enforce fullscreen)
import webbrowser # Opens URLs in the default browser (tutorials or help modules)
import pyperclip # Detects clipboard activity (e.g., copy-paste prevention)
from ultralytics import YOLO # Object detection model (used to detect phones, books, etc.)
import threading # Enables lightweight parallel execution of tasks
from multiprocessing import Process # For running isolated, CPU-intensive tasks in parallel
import pyaudio # Audio I/O interface (used to monitor and record microphone input)
import struct # Converts byte data for audio signal processing
import wave # Saves and loads audio recordings in .wav format
import datetime # For managing date and time (e.g., logs, exam times)
import subprocess # Run shell commands from Python (e.g., system diagnostics)

# 🔁 Control Flag for AI Monitoring Flow

Globalflag = False # Used to start/stop cheat detection activities

# 🧑 Student Information

Student_Name = '' # Stores the current student's name

# ⏱️ Time Tracking for Each Detection Module (5 modules)

start_time = [0, 0, 0, 0, 0] # Stores start timestamps for each check
end_time = [0, 0, 0, 0, 0] # Stores end timestamps for each check
recorded_durations = [] # Keeps track of total duration of suspicious events

# 🔁 Previous Detection State for Each Module

prev_state = [
'Verified Student appeared', # Face recognition
"Forward", # Eye gaze / attention detection
"Only one person is detected", # Multiple face detection
"Stay in the Test", # Browser/tab/window monitoring
"No Electronic Device Detected" # Object detection (e.g. phones, books)
]

# ⚠️ Flag for Detection Triggers

flag = [False, False, False, False, False] # True = suspicious behavior detected for that module

# 📷 Camera Properties Setup (Used for Frame Dimensions)

capb = cv2.VideoCapture(0) # Temporarily open webcam to get frame size
width = int(capb.get(cv2.CAP_PROP_FRAME_WIDTH)) # Get camera frame width
height = int(capb.get(cv2.CAP_PROP_FRAME_HEIGHT)) # Get camera frame height
capb.release() # Release the camera immediately to avoid locking

# 📱 Default Screen Dimensions for Electronic Device Detection

EDWidth = 1920 # Width of screen for device detection model (adjust if needed)
EDHeight = 1080 # Height of screen for device detection model (adjust if needed)

# 📁 Ensure Output Video Directory Exists

video_dir = os.path.join("static", "OutputVideos") # Path to save recorded videos
os.makedirs(video_dir, exist_ok=True) # Create the folder if it doesn't exist

📄 Markdown Documentation
markdown
Copy code

## 🎥 VideoWriter Initialization

This section sets up five separate video streams using OpenCV's `VideoWriter`, each saving to a distinct output file:

```python
writer = [
    cv2.VideoWriter(video[0], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height)),
    cv2.VideoWriter(video[1], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height)),
    cv2.VideoWriter(video[2], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height)),
    cv2.VideoWriter(video[3], cv2.VideoWriter_fourcc(*'mp4v'), 15, (1920, 1080)),
    cv2.VideoWriter(video[4], cv2.VideoWriter_fourcc(*'mp4v'), 20 , (EDWidth,EDHeight))
]
🧾 Notes:
mp4v is used as the video codec for .mp4 compatibility.

Three writers use the default webcam resolution.

One uses fixed Full HD resolution (1920x1080).

One uses EDWidth and EDHeight (used for screen or environment capture).

⚠️ Potential Issues:
If width or height is zero (e.g., if the webcam failed to initialize), the video writer may silently fail.

The video[x] file paths may still risk filename collisions if not made unique (see bug report earlier).

```

## 👥 Multiple Person Detection Configuration

This block initializes MediaPipe's face detection tools with increased sensitivity
to better detect unauthorized multiple faces during online exams.

```python
# More than One Person Related

# Import MediaPipe's face detection module
mpFaceDetection = mp.solutions.face_detection  # Detects faces

# Import drawing utilities from MediaPipe (to draw bounding boxes, etc.)
mpDraw = mp.solutions.drawing_utils  # Helps draw BBox and landmarks on frame

# Initialize face detector with sensitivity threshold
faceDetection = mpFaceDetection.FaceDetection(0.5)
# Increased sensitivity: previously 0.75 → now 0.5 to better detect multiple people


## 🧠 Section: Electronic Device (ED) Detection Initialization

### 📌 Purpose:
This code initializes the necessary components for detecting electronic devices (or other objects) using a pretrained YOLOv8 model. It loads class labels from the COCO dataset, assigns colors for each class (for bounding box drawing), and sets a control flag.

---
```

### 📄 Code with Line-by-Line Explanations

````python
# Open the COCO class labels file located in the utils directory
my_file = open("utils/coco.txt", "r")  # Opening the file in read mode

# Read the entire content of the file
data = my_file.read()  # Reading all the class names (e.g., "person", "laptop", etc.)

# Split the content by newline to get a list of class names
class_list = data.split("\n")  # Splitting the text into a list based on newlines

# Close the file after reading
my_file.close()  # Freeing up file resource

# Initialize an empty list to store the names of detected objects
detected_things = []  # Will store the names of objects detected during runtime

# Initialize a list to hold random color values for drawing bounding boxes for each class
detection_colors = []  # Colors for drawing different classes distinctly

# Generate a random RGB color for each class in the class list
for i in range(len(class_list)):
    r = random.randint(0, 255)  # Red component
    g = random.randint(0, 255)  # Green component
    b = random.randint(0, 255)  # Blue component
    detection_colors.append((b, g, r))  # Store in (B, G, R) format for OpenCV compatibility

# Load a pretrained YOLOv8 Nano model for object detection
model = YOLO("yolov8n.pt", "v8")  # Loads YOLOv8 Nano, a lightweight real-time model

# Flag to control if electronic device detection is currently active
EDFlag = False  # Used to toggle detection logic on/off during runtime


🎤 Voice Configuration (voice_settings.md)
Purpose
This section defines constants and setup parameters for real-time audio monitoring and recording. It's used to detect suspicious sounds like whispering, conversations, or any unauthorized audio activity during an exam.

Code with Explanations
```python
# Voice Related

TRIGGER_RMS = 30  # 🎚️ Start recording if volume level exceeds 30 (helps ignore loud background noise like fans)

RATE = 16000  # 🎧 Sampling rate: 16,000 samples per second (ideal for speech recognition)

TIMEOUT_SECS = 3  # 🕒 Recording stops after 3 seconds of continuous silence

FRAME_SECS = 0.25  # 🪵 Each audio frame processed is 0.25 seconds long (for detecting brief speech)

CUSHION_SECS = 1  # 🧤 Extra audio padding (1 second) before and after detected sound

SHORT_NORMALIZE = (1.0 / 32768.0)  # ⚖️ Normalize 16-bit audio sample to range [-1.0, 1.0]

FORMAT = pyaudio.paInt16  # 🎙️ 16-bit signed integer audio format (standard for most mics)

CHANNELS = 1  # 📡 Mono channel — only one microphone input needed

SHORT_WIDTH = 2  # 🧮 2 bytes per audio sample (16-bit audio = 2 bytes)

CHUNK = int(RATE * FRAME_SECS)  # 🍰 Number of samples per frame (e.g., 4000 samples for 0.25s)

CUSHION_FRAMES = int(CUSHION_SECS / FRAME_SECS)  # 🧣 Number of frames for cushion (pre and post audio buffer)

TIMEOUT_FRAMES = int(TIMEOUT_SECS / FRAME_SECS)  # ⏲️ Frames counted for silence-based timeout (e.g., 12 frames for 3s)

f_name_directory = 'static/OutputAudios'  # 📁 Directory path where audio recordings are saved


🗃️ JSON File Handling – write_json() Function
Purpose
This function appends new data (e.g., a detected violation or event) to an existing JSON file. The function is used for maintaining a log of actions like detected cheating attempts.

```python
# Database and Files Related

# 📄 Function to add new data to a JSON file
def write_json(new_data, filename='violation.json'):
    with open(filename, 'r+') as file:  # 🔓 Open the JSON file in read+write mode
        file_data = json.load(file)     # 📥 Load existing data from the file into a Python list/dict

        file_data.append(new_data)      # ➕ Append the new entry (new_data) to the existing list

        file.seek(0)                    # 📍 Move the file cursor to the beginning to overwrite the file

        json.dump(file_data, file, indent=4)  # 💾 Write the updated list back to the file with indentation


📁 Function: move_file_to_output_folder
Purpose
Moves a specified file (e.g., video, profile image) to a designated output folder inside the static/ directory. This is useful for organizing output assets like recorded media or profile captures.

Code with Comments
```python
# 📦 Function to move the files to the Output Folders
def move_file_to_output_folder(file_name, folder_name='OutputVideos'):
    # 🔍 Get the current working directory (project folder)
    current_directory = os.getcwd()

    # 📌 Construct the full source file path
    source_path = os.path.join(current_directory, file_name)

    # 📂 Construct the destination path inside the 'static' folder
    destination_path = os.path.join(current_directory, 'static', folder_name, file_name)

    try:
        # 🚚 Use 'shutil.move' to transfer the file from source to destination
        shutil.move(source_path, destination_path)
        print('Your video is moved to ' + folder_name)

    except FileNotFoundError:
        # ❌ Handles the case when the file doesn't exist in the source path
        print(f"Error: File '{file_name}' not found in the project folder.")

    except shutil.Error as e:
        # ⚠️ Handles other issues (e.g., file already exists, permission denied)
        print(f"Error: Failed to move the file. {e}")

    ## 🎞️ Function: reduceBitRate

### **Purpose**
Compresses a given video file by reducing its bitrate using FFmpeg. If FFmpeg is not found or fails, it copies the file as-is.

---

### **Code with Comments**
```python
# Function to reduce video file's data rate to 100 kbps
def reduceBitRate(input_file, output_file):
    target_bitrate = "1000k"  # ⚙️ Set your desired target bitrate here

    # 📍 Try to find FFmpeg executable from common install paths
    ffmpeg_paths = [
        "ffmpeg",  # Check if FFmpeg is available in system PATH
        "C:/Program Files/ffmpeg/bin/ffmpeg.exe",
        "C:/ffmpeg/bin/ffmpeg.exe",
        "C:/Users/kaungmyat/Downloads/ffmpeg-2023-08-28-git-b5273c619d-essentials_build/ffmpeg-2023-08-28-git-b5273c619d-essentials_build/bin/ffmpeg.exe"
    ]

    ffmpeg_path = None  # Will hold the valid FFmpeg path if found

    for path in ffmpeg_paths:
        try:
            # 🧪 Check if FFmpeg runs successfully
            result = subprocess.run([path, "-version"],
                                    capture_output=True,
                                    text=True,
                                    timeout=5)
            if result.returncode == 0:
                ffmpeg_path = path
                break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue

    if not ffmpeg_path:
        # 🚫 FFmpeg not found – fallback to copying
        print("FFmpeg not found. Skipping bitrate conversion.")
        print("Install FFmpeg or add it to PATH for video compression.")
        try:
            shutil.copy2(input_file, output_file)
            print(f"Copied {input_file} to {output_file} (no compression)")
        except Exception as e:
            print(f"Error copying file: {e}")
        return

    # ▶️ FFmpeg command to compress video
    command = [
        ffmpeg_path,
        "-i", input_file,         # Input video
        "-b:v", target_bitrate,   # Set video bitrate
        "-c:v", "libx264",        # Use H.264 codec for video
        "-c:a", "aac",            # Use AAC codec for audio
        "-strict", "experimental",
        "-b:a", "192k",           # Set audio bitrate
        "-y",                     # Overwrite if output exists
        output_file               # Output path
    ]

    try:
        # 🚀 Run FFmpeg compression
        result = subprocess.run(command,
                                capture_output=True,
                                text=True,
                                timeout=30)
        if result.returncode == 0:
            print("Bitrate conversion completed.")
        else:
            print(f"FFmpeg error: {result.stderr}")
            shutil.copy2(input_file, output_file)
    except subprocess.TimeoutExpired:
        print("FFmpeg timeout. Copying file without compression.")
        shutil.copy2(input_file, output_file)
    except Exception as e:
        print(f"Error during conversion: {e}")
        shutil.copy2(input_file, output_file)

````

## 🎥 Function: faceDetectionRecording(img, text)

### **Purpose**

This function records face detection violations during an online exam session and logs them. It detects when the verified student disappears and records that period for violation review.

---

### **Code with Inline Explanations**

````python
def faceDetectionRecording(img, text):
    # Global state variables used for tracking timing and recording
    global start_time, end_time, recorded_durations, prev_state, flag, writer, width, height

    print("Running FaceDetection Recording Function")
    print(text)

    # Violation just started: student disappeared
    if text != 'Verified Student appeared' and prev_state[0] == 'Verified Student appeared':
        start_time[0] = time.time()  # Start time of violation
        for _ in range(2): writer[0].write(img)  # Start recording

    # Ongoing violation > 3 sec
    elif text != 'Verified Student appeared' and str(text) == prev_state[0] and (time.time() - start_time[0]) > 3:
        flag[0] = True  # Mark this as a real violation
        for _ in range(2): writer[0].write(img)

    # Ongoing violation < 3 sec
    elif text != 'Verified Student appeared' and str(text) == prev_state[0] and (time.time() - start_time[0]) <= 3:
        flag[0] = False  # Short disturbance — ignore
        for _ in range(2): writer[0].write(img)

    # Student reappeared — stop recording
    else:
        if prev_state[0] != "Verified Student appeared":
            writer[0].release()
            end_time[0] = time.time()
            duration = math.ceil((end_time[0] - start_time[0]) / 3)
            outputVideo = 'FDViolation' + video[0]

            FDViolation = {
                "Name": prev_state[0],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[0])),
                "Duration": str(duration) + " seconds",
                "Mark": math.floor(2 * duration),
                "Link": outputVideo,
                "RId": get_resultId()
            }

            if flag[0]:
                recorded_durations.append(FDViolation)
                write_json(FDViolation)
                reduceBitRate(video[0], outputVideo)
                move_file_to_output_folder(outputVideo)

            os.remove(video[0])  # Delete original
            print(recorded_durations)

            # Prepare for next violation
            video[0] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[0] = cv2.VideoWriter(video[0], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width, height))
            flag[0] = False

    prev_state[0] = text  # Update state


Purpose
This function detects when a student moves their head away from the "Forward" position and logs that as a violation during the exam. It records a short video segment of the incident and writes metadata such as duration, timestamp, and severity.

Code with Line-by-Line Explanation
```python
# Function to record head movement violations
def Head_record_duration(text, img):
    # Access global variables for tracking violation states and video writers
    global start_time, end_time, recorded_durations, prev_state, flag, writer, width, height

    print("Running HeadMovement Recording Function")
    print(text)  # Print the current detected direction (e.g., Left, Right, etc.)

    # Case: Student is not looking "Forward"
    if text != "Forward":
        # If student just moved away from forward direction
        if str(text) != prev_state[1] and prev_state[1] == "Forward":
            start_time[1] = time.time()  # Start timer for violation
            for _ in range(2):
                writer[1].write(img)  # Record a couple of frames

        # If student changes head direction again during violation
        elif str(text) != prev_state[1] and prev_state[1] != "Forward":
            writer[1].release()  # Stop recording
            end_time[1] = time.time()  # Mark end time
            duration = math.ceil((end_time[1] - start_time[1])/7)  # Approximate violation duration

            outputVideo = 'HeadViolation' + video[1]  # Create filename for violation video

            # Create a metadata dictionary for this violation
            HeadViolation = {
                "Name": prev_state[1],  # Direction that caused violation
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[1])),
                "Duration": str(duration) + " seconds",
                "Mark": duration,  # Penalty score
                "Link": outputVideo,
                "RId": get_resultId()
            }

            # Save the violation only if flagged as valid
            if flag[1]:
                recorded_durations.append(HeadViolation)
                write_json(HeadViolation)
                reduceBitRate(video[1], outputVideo)  # Compress the video
                move_file_to_output_folder(outputVideo)  # Move it to output folder

            os.remove(video[1])  # Delete raw video
            print(recorded_durations)

            # Prepare a new writer for the next violation
            start_time[1] = time.time()
            video[1] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[1] = cv2.VideoWriter(video[1], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height))
            flag[1] = False  # Reset the flag

        # If student continues facing the same direction for more than 3 seconds
        elif str(text) == prev_state[1] and (time.time() - start_time[1]) > 3:
            flag[1] = True  # Mark as valid violation
            for _ in range(2):
                writer[1].write(img)  # Continue recording

        # If direction hasn't changed and duration is short (< 3s)
        elif str(text) == prev_state[1] and (time.time() - start_time[1]) <= 3:
            flag[1] = False  # Do not mark as violation
            for _ in range(2):
                writer[1].write(img)

        # Update previous state
        prev_state[1] = text

    # Case: Student is now looking forward again
    else:
        # If the previous state was a violation, wrap it up
        if prev_state[1] != "Forward":
            writer[1].release()
            end_time[1] = time.time()
            duration = math.ceil((end_time[1] - start_time[1])/7)
            outputVideo = 'HeadViolation' + video[1]

            # Create violation metadata
            HeadViolation = {
                "Name": prev_state[1],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[1])),
                "Duration": str(duration) + " seconds",
                "Mark": duration,
                "Link": outputVideo,
                "RId": get_resultId()
            }

            # Save violation if valid
            if flag[1]:
                recorded_durations.append(HeadViolation)
                write_json(HeadViolation)
                reduceBitRate(video[1], outputVideo)
                move_file_to_output_folder(outputVideo)

            os.remove(video[1])  # Delete raw video
            print(recorded_durations)

            # Prepare for next round of recording
            video[1] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[1] = cv2.VideoWriter(video[1], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height))
            flag[1] = False

        # Update state
        prev_state[1] = text

🧑‍🤝‍🧑 MTOP_record_duration Function
Purpose
This function monitors if more than one person is detected in front of the camera during an online exam session. If a second person is detected, it records a violation video, logs metadata like duration and timestamp, and stores the footage for review.

Code with Line-by-Line Explanation
python
Copy code
# Recording Function for More Than One Person Detection
def MTOP_record_duration(text, img):
    # Use global variables needed for tracking violations
    global start_time, end_time, recorded_durations, prev_state, flag, writer, width, height

    print("Running MTOP Recording Function")
    print(text)  # Log the current detection message for debugging

    # ➤ Case 1: Violation just started (a second person is newly detected)
    if text != 'Only one person is detected' and prev_state[2] == 'Only one person is detected':
        start_time[2] = time.time()  # Start the timer
        for _ in range(2):
            writer[2].write(img)  # Record a couple of frames to initialize

    # ➤ Case 2: Ongoing violation for more than 3 seconds
    elif text != 'Only one person is detected' and str(text) == prev_state[2] and (time.time() - start_time[2]) > 3:
        flag[2] = True  # Mark this as a valid violation
        for _ in range(2):
            writer[2].write(img)  # Record frames

    # ➤ Case 3: Ongoing violation but < 3 seconds
    elif text != 'Only one person is detected' and str(text) == prev_state[2] and (time.time() - start_time[2]) <= 3:
        flag[2] = False  # Don't mark as violation yet
        for _ in range(2):
            writer[2].write(img)

    # ➤ Case 4: User is back to single-person state after violation
    else:
        if prev_state[2] != "Only one person is detected":
            writer[2].release()  # Stop recording
            end_time[2] = time.time()  # Get end time of violation
            duration = math.ceil((end_time[2] - start_time[2]) / 3)  # Calculate duration

            outputVideo = 'MTOPViolation' + video[2]  # Create a name for the output file

            # Prepare metadata for this violation
            MTOPViolation = {
                "Name": prev_state[2],  # The previous state that caused the violation
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[2])),
                "Duration": str(duration) + " seconds",
                "Mark": math.floor(1.5 * duration),  # Penalty scoring logic
                "Link": outputVideo,  # Path to the saved violation video
                "RId": get_resultId()  # Associated result ID for this session
            }

            # Save the violation if it lasted long enough
            if flag[2]:
                recorded_durations.append(MTOPViolation)
                write_json(MTOPViolation)  # Log violation to JSON
                reduceBitRate(video[2], outputVideo)  # Compress video
                move_file_to_output_folder(outputVideo)  # Move to output folder

            os.remove(video[2])  # Delete raw uncompressed video
            print(recorded_durations)

            # Reinitialize for next violation
            video[2] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[2] = cv2.VideoWriter(video[2], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width, height))
            flag[2] = False  # Reset the violation flag

    # ➤ Update the previous state for comparison in the next frame
    prev_state[2] = text



    # 🖥️ Screen Detection Violation Recorder
def SD_record_duration(text, img):
    global start_time, end_time, prev_state, flag, writer, width, height

    print("Running SD Recording Function")
    print(text)

    # 🚨 Violation just started (user moved away from test screen)
    if text != "Stay in the Test" and prev_state[3] == "Stay in the Test":
        start_time[3] = time.time()
        print(f"Start SD Recording, start time is {start_time[3]} and array is {start_time}")
        for _ in range(2):
            writer[3].write(img)

    # ⏳ Violation is ongoing for more than 3 seconds
    elif text != "Stay in the Test" and str(text) == prev_state[3] and (time.time() - start_time[3]) > 3:
        flag[3] = True
        for _ in range(2):
            writer[3].write(img)

    # ⚠️ Violation ongoing but less than 3 seconds
    elif text != "Stay in the Test" and str(text) == prev_state[3] and (time.time() - start_time[3]) <= 3:
        flag[3] = False
        for _ in range(2):
            writer[3].write(img)

    # ✅ Back to normal (user returned to test screen)
    else:
        if prev_state[3] != "Stay in the Test":
            writer[3].release()
            end_time[3] = time.time()
            duration = math.ceil((end_time[3] - start_time[3])/4)
            outputVideo = 'SDViolation' + video[3]

            # 📦 Violation metadata
            SDViolation = {
                "Name": prev_state[3],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[3])),
                "Duration": str(duration) + " seconds",
                "Mark": (2 * duration),
                "Link": outputVideo,
                "RId": get_resultId()
            }

            # 💾 Save and archive if flagged
            if flag[3]:
                recorded_durations.append(SDViolation)
                write_json(SDViolation)
                reduceBitRate(video[3], outputVideo)
                move_file_to_output_folder(outputVideo)

            os.remove(video[3])
            print(recorded_durations)

            # 🔄 Reset for next violation
            video[3] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[3] = cv2.VideoWriter(video[3], cv2.VideoWriter_fourcc(*'mp4v'), 15, (1920, 1080))
            flag[3] = False

    # 🔁 Update previous state
    prev_state[3] = text


    # 📸 Function to capture a screenshot and convert it into an OpenCV-compatible NumPy array
def capture_screen():
    # Take a screenshot using PyAutoGUI (returns a PIL image in RGB format)
    screenshot = pyautogui.screenshot()

    # Convert the PIL image to a NumPy array (for OpenCV processing)
    frame = np.array(screenshot)

    # Convert the color format from RGB (PIL) to BGR (OpenCV standard)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Return the processed frame
    return frame


# 📹 Recording Function for Electronic Devices Detection
def EDD_record_duration(text, img):
    # Access global variables used for tracking and recording
    global start_time, end_time, prev_state, flag, writer, recorded_Images, EDD_Duration, video, EDWidth, EDHeight

    print(text)  # Debug print to show current detection text

    # 📍 Start recording when a new device is detected
    if text == "Electronic Device Detected" and prev_state[4] == "No Electronic Device Detected":
        start_time[4] = time.time()
        for _ in range(2):  # Write a couple of frames for context
            writer[4].write(img)

    # 🔁 Continue writing if violation persists beyond minimal time
    elif text == "Electronic Device Detected" and str(text) == prev_state[4] and (time.time() - start_time[4]) > 0:
        flag[4] = True
        for _ in range(2):
            writer[4].write(img)

    # 🔁 Short violation — don’t mark, but record
    elif text == "Electronic Device Detected" and str(text) == prev_state[4] and (time.time() - start_time[4]) <= 0:
        flag[4] = False
        for _ in range(2):
            writer[4].write(img)

    # ✅ End of violation — release video, calculate stats, and save
    else:
        if prev_state[4] == "Electronic Device Detected":
            writer[4].release()
            end_time[4] = time.time()
            duration = math.ceil((end_time[4] - start_time[4]) / 10)  # Normalize duration
            outputVideo = 'EDViolation' + video[4]  # New filename for violation

            # Build the violation record
            EDViolation = {
                "Name": prev_state[4],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[4])),
                "Duration": str(duration) + " seconds",
                "Mark": math.floor(1.5 * duration),
                "Link": outputVideo,
                "RId": get_resultId()
            }

            # If it's a real violation, save it
            if flag[4]:
                write_json(EDViolation)
                reduceBitRate(video[4], outputVideo)
                move_file_to_output_folder(outputVideo)

            os.remove(video[4])  # Delete old video
            # Prepare a new writer for next possible violation
            video[4] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[4] = cv2.VideoWriter(video[4], cv2.VideoWriter_fourcc(*'mp4v'), 10, (EDWidth, EDHeight))
            flag[4] = False  # Reset flag

    # Update previous state
    prev_state[4] = text

````

## 🔄 deleteTrashVideos()

This function scans the current working directory and removes temporary `.mp4` video files based on name patterns.

### 🎯 Purpose:

- To clean up leftover or auto-generated video recordings that are:
  - Numerically named (e.g., `12345.mp4`)
  - Labeled with `"Violation"` (e.g., `FDViolation12345.mp4`)
  - Have short names indicating they are likely temporary

### 🧠 Logic:

- Uses `os.listdir()` to iterate through files.
- Filters for `.mp4` files with:
  - Numeric-only names
  - Short length (<10 characters, excluding extension)
  - `"Violation"` in the filename
- Deletes matching files using `os.remove()`

### ⚠️ Note:

There’s a potential **logic bug** in:

```python
if filename.lower().endswith('.mp4') and filename.isdigit() or filename.endswith('.mp4'):


```

# 📷 FaceRecognition Class

## Purpose

A real-time facial recognition system that identifies a verified student and triggers recordings if they disappear during an exam.

---

## 📁 Initialization

- `__init__()`: Loads known faces from `static/Profiles` using `face_recognition`.

---

## 🔍 Face Encoding

- **Method**: `encode_faces()`
- Filters and encodes image files (.jpg, .png, etc.).
- Populates:
  - `known_face_encodings`
  - `known_face_names`

---

## 🎥 Recognition Loop

- **Method**: `run_recognition()`
- Captures video while `Globalflag` is True.
- Skips every alternate frame for performance.
- Converts image from BGR → RGB.
- Detects faces and matches with known encodings.
- Applies confidence threshold (≥ 84%) to identify a verified student.

---

## 🎯 Display and Recording

- Draws boxes and name labels using OpenCV.
- Calls `faceDetectionRecording()`:
  - If student disappears → triggers video logging.

---

## ⚠️ Dependencies

- `face_recognition`, `cv2`, `numpy`, system webcam.

---

## ✅ Example Output

- `"Verified Student appeared"` – Student matched and active.
- `"Verified Student disappeared"` – No face or mismatch.

---

Let me know if you want a **diagram or flowchart** of how this works end-to-end.

# 🤖 Head Movement Detection Function

## Function: `headMovmentDetection(image, face_mesh)`

### 🎯 Purpose

Detects head direction (left, right, up, down, forward) using facial landmarks with MediaPipe and OpenCV.

---

## ⚙️ Steps

1. **Preprocess Image**

   - Flips and converts to RGB for MediaPipe processing.

2. **Detect Facial Landmarks**

   - Uses `face_mesh.process()` to get landmarks.

3. **Extract Specific Key Points**

   - Nose, eyes, mouth corners, chin are used to estimate head pose.

4. **Estimate Pose**

   - Uses PnP and rotation matrix to calculate head angles.

5. **Interpret Head Direction**

   - Based on X and Y angles, determines head direction:
     - `Looking Left`
     - `Looking Right`
     - `Looking Up`
     - `Looking Down`
     - `Forward`

6. **Draw and Record**
   - Annotates frame with head direction.
   - Triggers recording logic via `Head_record_duration()`.

---

## 🧠 Notes

- Uses relaxed angle thresholds for natural movement.
- Records only when a change from "Forward" is detected.

# 🧍‍♂️🧍 More Than One Person Detection (MTOP)

## Function: `MTOP_Detection(img)`

### 🎯 Purpose

Detects whether **more than one person** is present in the video frame using face detection and triggers the MTOP recording system.

---

## 🛠️ Steps Involved

1. **Convert Color Format**

   - Converts the image from BGR to RGB to be compatible with MediaPipe.

2. **Run Face Detection**

   - Uses `faceDetection.process()` to identify faces in the frame.

3. **Count Detected Faces**

   - Draws bounding boxes around detected faces.
   - If `id > 0`, it implies more than one person is detected.

4. **Generate Output Message**

   - `"More than one person is detected."` if more than one face found.
   - `"Only one person is detected"` if only one face or none.

5. **Trigger Recording**

   - Sends the result and frame to `MTOP_record_duration()` to log and store violation footage.

6. **Console Output**
   - Prints the detection result for debugging.

---

## 🧠 Notes

- This method **does not identify individuals**, it only **counts faces**.
- If **no face is detected**, it assumes only one person to reduce false positives.
- Recording behavior is managed by `MTOP_record_duration()`.

---

## 📦 Dependencies

- `cv2` (OpenCV)
- `faceDetection` model (likely from MediaPipe)

# 🖥️ Shortcut Detection Function (Screen Monitoring)

## Function: `shortcut_handler(event)`

### 🎯 Purpose

Detects **specific keyboard shortcuts** that are commonly used to:

- Navigate away from full-screen apps
- Capture the screen
- Manipulate clipboard content
- Interrupt exam integrity

---

## 🧠 How It Works

1. **Trigger on Key Down**  
   Listens for key press events only (not releases).

2. **Detect Combinations**  
   Uses `keyboard.is_pressed()` to detect when known key combos are held down simultaneously.

3. **Logs Detected Shortcut**
   - Displays a message in the console.
   - Stores the shortcut in a global list called `shorcuts`.

---

## 🧪 Detected Shortcuts

| Category      | Combination       | Description                     |
| ------------- | ----------------- | ------------------------------- |
| Clipboard     | Ctrl+C / Ctrl+V   | Copy / Paste                    |
| Selection     | Ctrl+A / Ctrl+X   | Select All / Cut                |
| Navigation    | Alt+Tab, Win+Tab  | Switch apps or desktops         |
| Escapes       | Ctrl+Esc, Alt+Esc | Open start / Switch focus       |
| Function Keys | F1, F2, F3        | Common in help & IDEs           |
| Window Key    | Win               | Open start menu or toggle focus |
| Security      | Ctrl+Alt+Del      | Open security options           |
| Screenshot    | Prt Scn           | Capture screen                  |
| Tab Control   | Ctrl+T / Ctrl+W   | New tab / Close tab             |
| Undo          | Ctrl+Z            | Undo last action                |

---

## 🛡️ Use Case

This function is commonly used in **online proctoring systems** or **exam surveillance software** to monitor for attempts to:

- Cheat by copying/pasting
- Escape the fullscreen environment
- Use hidden tools or shortcuts

---

## ⚠️ Considerations

- The `keyboard` module requires **administrative privileges** on some platforms.
- May not work correctly in virtual machines or sandboxed environments.

### 📷 Electronic Devices Detection Function

**Function Name:** `electronicDevicesDetection(frame)`

**Purpose:**  
Detects electronic devices (like cell phones, laptops, remotes) using an object detection model in a given video frame and records evidence if found.

**Detection Logic:**

- Uses a trained object detection model (e.g., YOLOv8).
- Sets a sensitivity threshold of 0.25 (more sensitive).
- Searches for device labels such as:
  - `cell phone`
  - `remote`
  - `laptop`
  - `laptop,book`

**Recording:**
If a device is detected:

- The text is set to `"Electronic Device Detected"`.
- The function `EDD_record_duration()` is called to handle recording and storing the violation clip.

**Note:**

- `EDFlag` is managed by the outer calling loop and is not reset in this function.

**Inputs:**

- `frame`: OpenCV frame from video capture.

**Global Dependencies:**

- `model`: Preloaded object detection model.
- `EDFlag`: Boolean that tracks detection state.

**Output:**

- Printed result on the console.
- Calls a video recording trigger based on the detection.

# 🎙️ Recorder Class - Voice Detection and Recording

The `Recorder` class is designed to capture audio from a microphone, detect voice activity based on sound levels (RMS), and record voice violations. It operates continuously while a global flag is active and writes recorded audio to `.wav` files when a sound above a threshold is detected.

---

## ✅ Features

- Real-time voice activity detection using RMS.
- Buffered recording to include audio before and after sound spikes.
- Auto-saving detected speech events with timestamps.
- Handles microphone initialization and test routines.

---

## 🔧 Initialization

### `__init__(self)`

- Initializes the PyAudio stream with input/output settings.
- Sets up buffers and tracking variables.
- Handles microphone availability gracefully.

#### Parameters:

None

#### Initializes:

- `self.p`: PyAudio instance.
- `self.stream`: Opened audio stream.
- `self.quiet`: List used as a circular buffer for pre-speech frames.
- `self.timeout`: Timestamp when current sound detection expires.
- `self.microphone_available`: Indicates successful stream setup.

---

## 📈 Sound Processing

### `rms(frame)`

Calculates the Root Mean Square (RMS) value of the input audio frame to assess loudness.

#### Parameters:

- `frame`: Byte stream of audio data

#### Returns:

- `float`: RMS value scaled to 0–1000 range.

---

### `inSound(data)`

Determines whether the input data frame is loud enough to count as voice/sound.

#### Returns:

- `True`: If sound exceeds threshold or within timeout window.
- `False`: Otherwise.

---

## 🔄 Recording Flow

### `record(self)`

Main loop that runs while `Globalflag` is `True`. Detects sound using `rms`, manages buffer, and saves audio if voice is detected.

#### Process:

- Reads audio frames.
- Uses `inSound()` to decide if speech is occurring.
- Buffers pre-sound audio (`queueQuiet`).
- On sound end, writes the recording to file with metadata.

---

## 🧠 Buffer Management

### `queueQuiet(self, data)`

Stores quiet frames into a circular buffer so pre-sound can be captured when a voice is detected.

### `dequeueQuiet(self, sound)`

Adds buffered pre-sound frames to the start of the current voice recording.

---

## 💾 Writing Audio

### `write(self, sound, begin_time, duration)`

Writes the final audio byte stream to a `.wav` file, combining quiet buffer and speech, and logs the violation.

#### Metadata Recorded:

- `"Name"`: Common Noise is detected
- `"Time"`: Timestamp when sound began
- `"Duration"`: Recording duration (seconds)
- `"Mark"`: Numeric score or mark based on duration
- `"Link"`: File name of the saved audio
- `"RId"`: Result ID from external helper

---

## 🧪 Testing Utility

### `test_microphone(self)`

Optional tool to test microphone sensitivity and verify trigger threshold.

---

## 📦 Dependencies

- `pyaudio`
- `wave`
- `struct`
- `datetime`
- `math`
- `random`
- `time`
- Custom constants like: `CHUNK`, `RATE`, `FORMAT`, `TRIGGER_RMS`, etc.

---

## ⚠️ Notes & Assumptions

- Constants such as `SHORT_WIDTH`, `SHORT_NORMALIZE`, `TRIGGER_RMS`, `CUSHION_FRAMES`, etc., must be defined globally.
- The `get_resultId()` and `write_json()` helper functions must be available in the codebase.
- The recorder runs synchronously in the current thread; multithreading should be handled by the caller.

---

## 🐞 Potential Enhancements

- Gracefully close the audio stream and PyAudio instance with a `close()` method.
- Make trigger thresholds configurable via constructor arguments.
- Convert buffer logic to use `deque` for efficiency and reliability.

# 🎯 `cheat_Detection1()` – Head Movement Detection for Cheat Monitoring

This function initializes Mediapipe's FaceMesh model to detect head movement during a video stream. It serves as part of an exam proctoring system to catch behaviors like looking away from the screen.

---

## 🔧 Functionality

- Cleans up old temporary video files.
- Captures webcam feed.
- Uses Mediapipe's face mesh model to detect head orientations.
- Calls `headMovmentDetection()` on each frame to analyze movement.
- Stops running when `Globalflag` is set to `False`.
- Cleans up video files again at the end.

---

## 📥 Inputs

- **None** (depends on global variables):
  - `Globalflag`: A boolean controlling the active state of the detection loop.
  - `cap`: The OpenCV video capture object.
  - Assumes external availability of `deleteTrashVideos()` and `headMovmentDetection()`.

---

## 📤 Output

- No return value.
- Processes and possibly logs or stores head movement information via `headMovmentDetection`.

---

## ⚠️ Potential Bug

- The condition `if Globalflag:` wrapping `cap.release()` may **prevent camera release** if the loop ends due to `Globalflag = False`.

✅ **Recommended Fix**:

```python
cap.release()  # Always release camera after loop ends

```

## 🧱 Dependencies

cv2 (OpenCV)

mediapipe (mp.solutions.face_mesh)

cap: Initialized OpenCV video capture object

deleteTrashVideos()

headMovmentDetection()

# Function: `cheat_Detection2`

## 🔍 Purpose

Performs continuous real-time cheating detection during an online exam by analyzing webcam footage for:

- Presence of more than one person
- Switching windows (screen detection)
- Detection of electronic devices

---

## 📥 Inputs

- Accesses webcam frames using `cap.read()`
- Uses global flags and variables

---

## 📤 Outputs

- Calls external functions to log violations
- Sets global `EDFlag` for electronic device detection
- Triggers recording and file writing elsewhere

---

## 🌐 Global Variables Used

- `Globalflag`: Controls the main loop (True = continue monitoring)
- `shorcuts`: Presumably collects shortcut key logs (not used here)
- `EDFlag`: Boolean flag indicating if a device was detected in the current frame

---

## 🧠 Logic Summary

1. Cleans up any temporary `.mp4` videos using `deleteTrashVideos()`
2. Enters a `while` loop that:
   - Captures a webcam frame
   - Assigns the frame to three aliases for different detection functions
   - Resets `EDFlag` before checking for electronic devices
   - Runs:
     - `MTOP_Detection()` → checks for multiple people
     - `screenDetection()` → checks if exam tab/window is active
     - `electronicDevicesDetection()` → checks for phones, laptops, remotes, etc.
3. On exiting the loop:
   - Cleans up videos again
   - Tries to release the webcam

---

## ⚠️ Potential Bug

### 🎯 Bug Location

```python
if Globalflag:
    cap.release()

```

# Function: `get_resultId`

## 🔍 Purpose

Generates the **next unique result ID** by reading existing records in `result.json`, sorting them by ID, and returning the next available value.

---

## 🧠 Logic

1. Opens the `result.json` file in read/write mode.
2. Loads the JSON data into a list of dictionaries (`file_data`).
3. Sorts the list by the `Id` key to ensure correct order.
4. Returns the next result ID by taking the last ID and adding 1.

---

## 📤 Output

- Returns an integer: `last_existing_id + 1`

---

## ⚠️ Potential Issues

### 1. **Empty File Handling**

If `result.json` is empty, `json.load(file)` will raise an error.
**Fix Suggestion:**
Wrap in a try-except block or check for empty file content before loading.

### 2. **Missing or Malformed IDs**

If any item is missing an `"Id"` key or contains a non-integer value, the sort or return line may break.
**Fix Suggestion:**
Validate the structure and types during data loading or with try-except.

---

## ✅ Example

Assume `result.json` contains:

```json
[
  { "Id": 1, "Name": "Violation A" },
  { "Id": 2, "Name": "Violation B" }
]
```

### get_TrustScore(Rid)

**Description:**  
Calculates the total trust violation score for a given Result ID (`Rid`) by summing the `"Mark"` field from all entries in `violation.json` that match the provided `Rid`.

**Parameters:**

- `Rid` (int): The Result ID to search for in the JSON violation log.

**Returns:**

- `total_mark` (int): The sum of `"Mark"` values associated with the given Result ID.

**Functionality:**

- Opens the `violation.json` file in read/write mode.
- Loads all existing violation records into memory.
- Filters only the entries that match the provided `Rid`.
- Sums up the `"Mark"` scores from those records.
- Returns the total score.

**Used For:**

- Computing the violation trust score to assess the level of suspicious activity during an exam.

---

### 🐞 Potential Issues / Bugs

1. **File Not Found:**

   - If `violation.json` does not exist, `open()` will raise a `FileNotFoundError`.

2. **Empty or Corrupt File:**

   - If the JSON is malformed or empty, `json.load(file)` will raise a `JSONDecodeError`.

3. **KeyError on "RId" or "Mark":**

   - If any record in the JSON lacks the `"RId"` or `"Mark"` key, it will raise a `KeyError`.

4. **Wrong File Mode (`r+`):**

   - Since the function only reads the file, `r+` (read/write) is unnecessary. `r` (read-only) would be safer.

5. **No Matching Records:**
   - If `Rid` is not found, `filtered_data` is empty, and `sum()` correctly returns 0 — but if that’s not expected, it could be misleading.

### getResults()

**Description:**
Fetches all exam result records stored in the `result.json` file.

**Parameters:**

- None

**Returns:**

- `result_data` (list or dict): Parsed data from the `result.json` file, typically a list of dictionaries with each result.

**Functionality:**

- Opens the `result.json` file.
- Loads its contents as Python data.
- Returns all stored result entries.

---

### 🐞 Potential Issues / Bugs

1. **Unnecessary Write Access (`r+`):**

   - The function only reads the file, so `r` (read-only) is sufficient. `r+` allows writing, which is unsafe and unnecessary here.

2. **File Not Found:**

   - If `result.json` does not exist, this will raise a `FileNotFoundError`.

3. **Empty or Malformed JSON:**

   - If the file is empty or contains invalid JSON, `json.load(file)` will raise a `JSONDecodeError`.

4. **No Data Validation:**

   - The function assumes the file contains the correct data format (likely a list of result dictionaries). If not, it may return unexpected results.

5. **Hardcoded File Name:**
   - The function uses a fixed file path. It would be more flexible to accept the filename as a parameter.

---

### ✅ Suggested Fixes

- Use `open('result.json', 'r')` instead of `'r+'`.
- Wrap in `try-except` to catch `FileNotFoundError` or `JSONDecodeError`.
- Optionally add validation for expected data structure.

### getResultDetails(rid)

**Description:**
Fetches a specific result entry and its associated violation records based on the provided result ID (`rid`).

**Parameters:**

- `rid` (int or str): The result ID for which to retrieve detailed data.

**Returns:**

- A dictionary with:
  - `"Result"`: List of one or more result entries matching the ID.
  - `"Violation"`: List of violations related to the same result ID.

**Example Return:**

```json
{
  "Result": [{ "Id": 5, "Name": "Ali", "TrustScore": 85 }],
  "Violation": [
    { "RId": 5, "Name": "Head Turned", "Mark": 5 },
    { "RId": 5, "Name": "Phone Detected", "Mark": 10 }
  ]
}
```
