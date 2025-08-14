import sys
import face_recognition
from concurrent.futures import ThreadPoolExecutor
import cv2
import mediapipe as mp
import numpy as np
import time
import math
import random
import os
import json
import shutil
import keyboard
import pyautogui
import pygetwindow as gw
import webbrowser
import pyperclip
from ultralytics import YOLO
import threading
from multiprocessing import Process
import pyaudio
import struct
import wave
import datetime
import subprocess

#Variables
#All Related
Globalflag = False
Student_Name = ''
start_time = [0, 0, 0, 0, 0]
end_time = [0, 0, 0, 0, 0]
recorded_durations = []
prev_state = ['Verified Student appeared', 
              "Forward", 
              "Only one person is detected",
              "Stay in the Test",
              "No Electronic Device Detected"]
flag = [False, False, False, False, False]

# Individual FPS variables for each video writer
FACE_DETECTION_FPS = 20      # Writer[0] - Face Detection violations
HEAD_MOVEMENT_FPS = 20       # Writer[1] - Head Movement violations  
MTOP_DETECTION_FPS = 20      # Writer[2] - Multiple Person violations
SCREEN_DETECTION_FPS = 5     # Writer[3] - Screen Detection violations
ELECTRONIC_DEVICE_FPS = 10   # Writer[4] - Electronic Device violations

capb= cv2.VideoCapture(0)
width= int(capb.get(cv2.CAP_PROP_FRAME_WIDTH))
height= int(capb.get(cv2.CAP_PROP_FRAME_HEIGHT))
capb.release()
# Set default dimensions for electronic device detection (can be adjusted as needed)
EDWidth = 1920
EDHeight = 1080
# Ensure the OutputVideos directory exists
video_dir = os.path.join("static", "OutputVideos")
os.makedirs(video_dir, exist_ok=True)

# Create video files in the proper directory
video = [
    os.path.join(video_dir, str(random.randint(1,50000))+".mp4"),
    os.path.join(video_dir, str(random.randint(1,50000))+".mp4"),
    os.path.join(video_dir, str(random.randint(1,50000))+".mp4"),
    os.path.join(video_dir, str(random.randint(1,50000))+".mp4"),
    os.path.join(video_dir, str(random.randint(1,50000))+".mp4")
]
writer = [cv2.VideoWriter(video[0], cv2.VideoWriter_fourcc(*'mp4v'), FACE_DETECTION_FPS, (width,height)), 
          cv2.VideoWriter(video[1], cv2.VideoWriter_fourcc(*'mp4v'), HEAD_MOVEMENT_FPS, (width,height)), 
          cv2.VideoWriter(video[2], cv2.VideoWriter_fourcc(*'mp4v'), MTOP_DETECTION_FPS, (width,height)), 
          cv2.VideoWriter(video[3], cv2.VideoWriter_fourcc(*'mp4v'), SCREEN_DETECTION_FPS, (1920, 1080)), 
          cv2.VideoWriter(video[4], cv2.VideoWriter_fourcc(*'mp4v'), ELECTRONIC_DEVICE_FPS , (EDWidth,EDHeight))]

#More than One Person Related
mpFaceDetection = mp.solutions.face_detection  # Detect the face
mpDraw = mp.solutions.drawing_utils  # Draw the required Things for BBox
faceDetection = mpFaceDetection.FaceDetection(0.5)# Increased sensitivity: 0.75 -> 0.5 for better multiple person detection

#Screen Related
shorcuts = []
active_window = None # Store the initial active window and its title
active_window_title = "Google Chrome"  # Updated for Chrome browser
exam_window_title = active_window_title

#ED Related
my_file = open("utils/coco.txt", "r") # opening the file in read mode
data = my_file.read() # reading the file
class_list = data.split("\n") # replacing end splitting the text | when newline ('\n') is seen.
my_file.close()
detected_things = []
detection_colors = [] # Generate random colors for class list
for i in range(len(class_list)):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    detection_colors.append((b, g, r))
model = YOLO("yolo11n.pt")
EDFlag = False

#Voice Related
TRIGGER_RMS = 15  # start recording above 15
RATE = 16000  # sample rate
TIMEOUT_SECS = 3  # silence time after which recording stops
FRAME_SECS = 0.25  # length of frame(chunks) to be processed at once in secs
CUSHION_SECS = 1  # amount of recording before and after sound
SHORT_NORMALIZE = (1.0 / 32768.0)
FORMAT = pyaudio.paInt16
CHANNELS = 1
SHORT_WIDTH = 2
CHUNK = int(RATE * FRAME_SECS)
CUSHION_FRAMES = int(CUSHION_SECS / FRAME_SECS)
TIMEOUT_FRAMES = int(TIMEOUT_SECS / FRAME_SECS)
f_name_directory = 'static/OutputAudios'  # Fixed path to use relative directory
# Capture
cap = None

# Camera Producer-Consumer System (Double Buffer Implementation)
write_frame = None  # Producer writes to this buffer
read_frame = None   # Consumers read from this buffer
frame_lock = threading.Lock()  # Only for quick buffer swap
frame_ready = threading.Event()
camera_thread = None


#Database and Files Related
# function to add data to JSON
def write_json(new_data, filename='violation.json'):
    # Create file with empty list if it doesn't exist
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump([], f)

    # Now open and handle possible empty/corrupt file
    try:
        with open(filename, 'r+') as file:
            try:
                file_data = json.load(file)
                if not isinstance(file_data, list):
                    file_data = []
            except json.JSONDecodeError:
                file_data = []
            file_data.append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent=4)
            file.truncate()
    except Exception as e:
        print(f"Error in write_json: {e}")

#Function to move the files to the Output Folders
def move_file_to_output_folder(file_name,folder_name='OutputVideos'):
    # Get the current working directory (project folder)
    current_directory = os.getcwd()
    # Define the paths for the source file and destination folder
    source_path = os.path.join(current_directory, file_name)
    destination_path = os.path.join(current_directory, 'static', folder_name, file_name)
    try:
        # Use 'shutil.move' to move the file to the destination folder
        shutil.move(source_path, destination_path)
        print('Your video is moved to'+folder_name)
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found in the project folder.")
    except shutil.Error as e:
        print(f"Error: Failed to move the file. {e}")

#Function to reduce video file's data rate to 100 kbps
def reduceBitRate(input_file, output_file):
    target_bitrate = "1000k"  # Set your desired target bitrate here
    
    # Try to find FFmpeg executable
    ffmpeg_paths = [
        "ffmpeg",  # If FFmpeg is in PATH
        "C:/Program Files/ffmpeg/bin/ffmpeg.exe",
        "C:/ffmpeg/bin/ffmpeg.exe",
        "C:/Users/kaungmyat/Downloads/ffmpeg-2023-08-28-git-b5273c619d-essentials_build/ffmpeg-2023-08-28-git-b5273c619d-essentials_build/bin/ffmpeg.exe"
    ]
    
    ffmpeg_path = None
    for path in ffmpeg_paths:
        try:
            # Test if FFmpeg exists and is executable
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
        print("FFmpeg not found. Skipping bitrate conversion.")
        print("Install FFmpeg or add it to PATH for video compression.")
        # Just copy the file if FFmpeg is not available
        try:
            shutil.copy2(input_file, output_file)
            print(f"Copied {input_file} to {output_file} (no compression)")
        except Exception as e:
            print(f"Error copying file: {e}")
        return
    
    # Run FFmpeg command to lower the bitrate
    command = [
        ffmpeg_path,
        "-i", input_file,
        "-b:v", target_bitrate,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        "-b:a", "192k",
        "-y",  # Overwrite output file
        output_file
    ]
    
    try:
        result = subprocess.run(command, 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        if result.returncode == 0:
            print("Bitrate conversion completed.")
        else:
            print(f"FFmpeg error: {result.stderr}")
            # Fallback to copying
            shutil.copy2(input_file, output_file)
    except subprocess.TimeoutExpired:
        print("FFmpeg timeout. Copying file without compression.")
        shutil.copy2(input_file, output_file)
    except Exception as e:
        print(f"Error during conversion: {e}")
        shutil.copy2(input_file, output_file)

#Recordings related
#Recording Function for Face Verification
def faceDetectionRecording(img, text):
    global start_time, end_time, recorded_durations, prev_state, flag, writer, width, height
    print("Running FaceDetection Recording Function")
    print(text)
    if text != 'Verified Student appeared' and prev_state[0] == 'Verified Student appeared':
        start_time[0] = time.time()
        for _ in range(2):
            writer[0].write(img)
    elif text != 'Verified Student appeared' and str(text) == prev_state[0] and (time.time() - start_time[0]) > 3:
        flag[0] = True
        for _ in range(2):
            writer[0].write(img)
    elif text != 'Verified Student appeared' and str(text) == prev_state[0] and (time.time() - start_time[0]) <= 3:
        flag[0] = False
        for _ in range(2):
            writer[0].write(img)
    else:
        if prev_state[0] != "Verified Student appeared":
            writer[0].release()
            end_time[0] = time.time()
            duration = math.ceil((end_time[0] - start_time[0]) / 3)
            outputVideo = os.path.join(video_dir, 'FDViolation' + os.path.basename(video[0]))
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
            os.remove(video[0])
            print(recorded_durations)
            video[0] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[0] = cv2.VideoWriter(video[0], cv2.VideoWriter_fourcc(*'mp4v'), FACE_DETECTION_FPS, (width, height))
            flag[0] = False
    prev_state[0] = text

#Recording Function for Head Movement Detection
def Head_record_duration(text,img):
    global start_time, end_time, recorded_durations, prev_state, flag,writer, width, height
    print("Running HeadMovement Recording Function")
    print(text)
    if text != "Forward":
        if str(text) != prev_state[1] and prev_state[1] == "Forward":
            start_time[1] = time.time()
            for _ in range(2):
                writer[1].write(img)
        elif str(text) != prev_state[1] and prev_state[1] != "Forward":
            writer[1].release()
            end_time[1] = time.time()
            duration = math.ceil((end_time[1] - start_time[1])/7)
            outputVideo = os.path.join(video_dir, 'HeadViolation' + os.path.basename(video[1]))
            HeadViolation = {
                "Name": prev_state[1],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[1])),
                "Duration": str(duration) + " seconds",
                "Mark": duration,
                "Link": outputVideo,
                "RId": get_resultId()
            }
            if flag[1]:
                recorded_durations.append(HeadViolation)
                write_json(HeadViolation)
                reduceBitRate(video[1], outputVideo)
                move_file_to_output_folder(outputVideo)
            os.remove(video[1])
            print(recorded_durations)
            start_time[1] = time.time()
            video[1] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[1] = cv2.VideoWriter(video[1], cv2.VideoWriter_fourcc(*'mp4v'), HEAD_MOVEMENT_FPS, (width,height))
            flag[1] = False
        elif str(text) == prev_state[1] and (time.time() - start_time[1]) > 3:
            flag[1] = True
            for _ in range(2):
                writer[1].write(img)
        elif str(text) == prev_state[1] and (time.time() - start_time[1]) <= 3:
            flag[1] = False
            for _ in range(2):
                writer[1].write(img)
        prev_state[1] = text
    else:
        if prev_state[1] != "Forward":
            writer[1].release()
            end_time[1] = time.time()
            duration = math.ceil((end_time[1] - start_time[1])/7)
            outputVideo = os.path.join(video_dir, 'HeadViolation' + os.path.basename(video[1]))
            HeadViolation = {
                "Name": prev_state[1],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[1])),
                "Duration": str(duration) + " seconds",
                "Mark": duration,
                "Link": outputVideo,
                "RId": get_resultId()
            }
            if flag[1]:
                recorded_durations.append(HeadViolation)
                write_json(HeadViolation)
                reduceBitRate(video[1], outputVideo)
                move_file_to_output_folder(outputVideo)
            os.remove(video[1])
            print(recorded_durations)
            video[1] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[1] = cv2.VideoWriter(video[1], cv2.VideoWriter_fourcc(*'mp4v'), HEAD_MOVEMENT_FPS, (width,height))
            flag[1] = False
        prev_state[1] = text

#Recording Function for More than one person Detection
def MTOP_record_duration(text, img):
    global start_time, end_time, recorded_durations, prev_state, flag, writer, width, height
    print("Running MTOP Recording Function")
    print(text)
    if text != 'Only one person is detected' and prev_state[2] == 'Only one person is detected':
        start_time[2] = time.time()
        for _ in range(2):
            writer[2].write(img)
    elif text != 'Only one person is detected' and str(text) == prev_state[2] and (time.time() - start_time[2]) > 3:
        flag[2] = True
        for _ in range(2):
            writer[2].write(img)
    elif text != 'Only one person is detected' and str(text) == prev_state[2] and (time.time() - start_time[2]) <= 3:
        flag[2] = False
        for _ in range(2):
            writer[2].write(img)
    else:
        if prev_state[2] != "Only one person is detected":
            writer[2].release()
            end_time[2] = time.time()
            duration = math.ceil((end_time[2] - start_time[2])/3)
            outputVideo = os.path.join(video_dir, 'MTOPViolation' + os.path.basename(video[2]))
            MTOPViolation = {
                "Name": prev_state[2],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[2])),
                "Duration": str(duration) + " seconds",
                "Mark": math.floor(1.5 * duration),
                "Link": outputVideo,
                "RId": get_resultId()
            }
            if flag[2]:
                recorded_durations.append(MTOPViolation)
                write_json(MTOPViolation)
                reduceBitRate(video[2], outputVideo)
                move_file_to_output_folder(outputVideo)
            os.remove(video[2])
            print(recorded_durations)
            video[2] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[2] = cv2.VideoWriter(video[2], cv2.VideoWriter_fourcc(*'mp4v'), MTOP_DETECTION_FPS, (width,height))
            flag[2] = False
    prev_state[2] = text

#Recording Function for Screen Detection
def SD_record_duration(text, img):
    global start_time, end_time, prev_state, flag, writer, width, height
    print("Running SD Recording Function")
    print(text)
    if text != "Stay in the Test" and prev_state[3] == "Stay in the Test":
        start_time[3] = time.time()
        print(f"Start SD Recording, start time is {start_time[3]} and array is {start_time}")
        for _ in range(2):
            writer[3].write(img)
    elif text != "Stay in the Test" and str(text) == prev_state[3] and (time.time() - start_time[3]) > 3:
        flag[3] = True
        for _ in range(2):
            writer[3].write(img)
    elif text != "Stay in the Test" and str(text) == prev_state[3] and (time.time() - start_time[3]) <= 3:
        flag[3] = False
        for _ in range(2):
            writer[3].write(img)
    else:
        if prev_state[3] != "Stay in the Test":
            writer[3].release()
            end_time[3] = time.time()
            duration = math.ceil((end_time[3] - start_time[3])/4)
            outputVideo = os.path.join(video_dir, 'SDViolation' + os.path.basename(video[3]))
            SDViolation = {
                "Name": prev_state[3],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[3])),
                "Duration": str(duration) + " seconds",
                "Mark": (2 * duration),
                "Link": outputVideo,
                "RId": get_resultId()
            }
            if flag[3]:
                recorded_durations.append(SDViolation)
                write_json(SDViolation)
                reduceBitRate(video[3], outputVideo)
                move_file_to_output_folder(outputVideo)
            os.remove(video[3])
            print(recorded_durations)
            video[3] = os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[3] = cv2.VideoWriter(video[3], cv2.VideoWriter_fourcc(*'mp4v'), SCREEN_DETECTION_FPS, (1920, 1080))
            flag[3] = False
    prev_state[3] = text

# Function to capture the screen using PyAutoGUI and return the frame as a NumPy array
def capture_screen():
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

#Recording Function for Electronic Devices Detection
def EDD_record_duration(text, img):
    global start_time, end_time, prev_state, flag, writer,recorded_Images,EDD_Duration, video, EDWidth, EDHeight
    print(text)
    if text == "Electronic Device Detected":
        if prev_state[4] == "No Electronic Device Detected":
            start_time[4] = time.time()
            # Initialize frame counter for this detection event
            EDD_record_duration.frame_count = 0
        # Debug: Check frame shape and writer properties
        print(f"[DEBUG] Frame shape: {img.shape}")
        print(f"[DEBUG] Writer[4] is opened: {writer[4].isOpened()}")
        print(f"[DEBUG] Writer[4] size: {EDWidth}x{EDHeight}")
        # Ensure frame matches writer dimensions
        if img.shape[1] != EDWidth or img.shape[0] != EDHeight:
            print(f"[DEBUG] Resizing frame from {img.shape[1]}x{img.shape[0]} to {EDWidth}x{EDHeight}")
            img = cv2.resize(img, (EDWidth, EDHeight))
        writer[4].write(img)
        # Increment and print frame counter
        if not hasattr(EDD_record_duration, 'frame_count'):
            EDD_record_duration.frame_count = 1
        else:
            EDD_record_duration.frame_count += 1
        # If detected for more than 3 seconds, set flag
        if (time.time() - start_time[4]) > 3:
            flag[4] = True
        else:
            flag[4] = False
    else:
        # Detection ended, process video
        if prev_state[4] == "Electronic Device Detected":
            # Reset frame counter for next event
            EDD_record_duration.frame_count = 0
            writer[4].release()
            end_time[4] = time.time()
            duration = math.ceil(end_time[4] - start_time[4])
            base_filename = os.path.basename(video[4])
            outputVideo = os.path.join(video_dir, 'EDViolation' + base_filename)
            EDViolation = {
                "Name": prev_state[4],
                "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time[4])),
                "Duration": str(duration) + " seconds",
                "Mark": math.floor(1.5 * duration),
                "Link": os.path.relpath(outputVideo, start=os.getcwd()),
                "RId": get_resultId()
            }
            if flag[4]:
                try:
                    file_size = os.path.getsize(video[4])
                except Exception as e:
                    print(f"Error checking file size for {video[4]}: {e}")
                    file_size = 0
                if file_size > 10240:
                    write_json(EDViolation)
                    reduceBitRate(video[4], outputVideo)
                    move_file_to_output_folder(outputVideo)
            os.remove(video[4])
            video[4]= os.path.join(video_dir, str(random.randint(1, 50000)) + ".mp4")
            writer[4] = cv2.VideoWriter(video[4], cv2.VideoWriter_fourcc(*'mp4v'), ELECTRONIC_DEVICE_FPS , (EDWidth,EDHeight))
            flag[4] = False
    prev_state[4] = text

#system Related
def camera_producer_thread():
    """Double-buffered camera producer thread for optimal performance"""
    global Globalflag, cap, write_frame, read_frame, frame_lock, frame_ready
    print("Camera producer thread started (double buffering)")
    
    last_frame_time = 0
    target_fps = 20  # Limit camera FPS to prevent overwhelming
    frame_interval = 1.0 / target_fps
    
    while Globalflag:
        current_time = time.time()
        
        # Rate limiting: only capture at target FPS
        if current_time - last_frame_time >= frame_interval:
            if cap is not None and cap.isOpened():
                success, frame = cap.read()
                if success and frame is not None and frame.size > 0:
                    # Write to write_frame (no lock needed - producer only)
                    write_frame = frame.copy()
                    
                    # Quick buffer swap (minimal lock time)
                    with frame_lock:
                        read_frame = write_frame
                    
                    frame_ready.set()  # Signal that new frame is available
                    last_frame_time = current_time
            else:
                time.sleep(0.01)  # Small delay if camera not available
        else:
            time.sleep(0.001)  # Small sleep to prevent busy waiting
    
    print("Camera producer thread stopped")

def get_camera_frame(timeout=1.0):
    """Get current frame using double buffering (thread-safe but minimal locking)"""
    global read_frame, frame_lock, frame_ready
    
    # Wait for frame to be ready with timeout
    if frame_ready.wait(timeout):
        # Quick lock to copy the frame reference (very fast)
        with frame_lock:
            if read_frame is not None:
                frame_copy = read_frame.copy()  # Each thread gets its own copy
                return frame_copy
    return None

def deleteTrashVideos():
    global video, writer
    
    # First, safely release any active video writers to unlock files
    try:
        for i, vid_writer in enumerate(writer):
            if vid_writer is not None:
                vid_writer.release()
    except Exception as e:
        pass
    
    # Check both root directory and OutputVideos directory for temp files
    directories_to_check = [
        os.getcwd(),  # Current directory (root of project)
        os.path.join(os.getcwd(), "static", "OutputVideos")  # OutputVideos directory
    ]
    
    deleted_count = 0
    current_video_files = [os.path.basename(v) for v in video if v]  # Get current active video filenames
    
    for directory in directories_to_check:
        if not os.path.exists(directory):
            continue
            
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Check if it's a file (not directory)
            if not os.path.isfile(file_path):
                continue
                
            # For MP4 files: delete small temporary files with numeric names
            if filename.lower().endswith('.mp4'):
                # Only delete if:
                # 1. Filename is purely numeric (temp files)
                # 2. File size is very small (< 10KB) indicating incomplete/temp file
                # 3. Does NOT contain "Violation" (those are important processed files)
                # 4. NOT currently being used by video writers
                
                if (filename.replace('.mp4', '').isdigit() and 
                    'Violation' not in filename and
                    filename not in current_video_files):
                    
                    try:
                        # Check file size - delete if very small (indicates temp/incomplete file)
                        file_size = os.path.getsize(file_path)
                        if file_size < 10240:  # Less than 10KB
                            os.remove(file_path)
                            deleted_count += 1
                    except OSError as e:
                        pass
            
            # For WAV files: delete temporary voice violation files in root directory  
            elif (filename.lower().endswith('.wav') and 
                  'VoiceViolation' in filename and
                  directory == os.getcwd()):  # Only delete wav files from root, not OutputAudios
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except OSError as e:
                    pass
    
    # Reinitialize video writers after cleanup
    reinitialize_video_writers()

def reinitialize_video_writers():
    """Reinitialize video writers after cleanup"""
    global video, writer, video_dir, width, height, EDWidth, EDHeight
    
    try:
        # Create new video file paths
        video = [
            os.path.join(video_dir, str(random.randint(1,50000))+".mp4"),
            os.path.join(video_dir, str(random.randint(1,50000))+".mp4"),
            os.path.join(video_dir, str(random.randint(1,50000))+".mp4"),
            os.path.join(video_dir, str(random.randint(1,50000))+".mp4"),
            os.path.join(video_dir, str(random.randint(1,50000))+".mp4")
        ]
        
        # Create new video writers
        writer = [
            cv2.VideoWriter(video[0], cv2.VideoWriter_fourcc(*'mp4v'), FACE_DETECTION_FPS, (width,height)), 
            cv2.VideoWriter(video[1], cv2.VideoWriter_fourcc(*'mp4v'), HEAD_MOVEMENT_FPS, (width,height)), 
            cv2.VideoWriter(video[2], cv2.VideoWriter_fourcc(*'mp4v'), MTOP_DETECTION_FPS, (width,height)), 
            cv2.VideoWriter(video[3], cv2.VideoWriter_fourcc(*'mp4v'), SCREEN_DETECTION_FPS, (1920, 1080)), 
            cv2.VideoWriter(video[4], cv2.VideoWriter_fourcc(*'mp4v'), ELECTRONIC_DEVICE_FPS, (EDWidth,EDHeight))
        ]
        
    except Exception as e:
        pass

def cleanup_all_videos():
    """Complete cleanup function for application shutdown - releases all writers and cleans temp files"""
    global video, writer, Globalflag
    
    print("Starting complete video cleanup...")
    
    # Stop all detection processes
    Globalflag = False
    
    # Release all video writers and remove temp files
    try:
        for i, vid_writer in enumerate(writer):
            if vid_writer is not None:
                vid_writer.release()
                print(f"Released video writer {i}")
                
                # Remove the temp file after releasing writer
                if i < len(video) and video[i] and os.path.exists(video[i]):
                    try:
                        os.remove(video[i])
                        print(f"Removed temp file: {video[i]}")
                    except OSError as e:
                        print(f"Could not remove {video[i]}: {e}")
    except Exception as e:
        print(f"Error during writer cleanup: {e}")
    
    # Now clean any remaining temp files
    deleteTrashVideos()
    
    print("Complete video cleanup finished")

#Models Related
#One: Face Detection Function
def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'

class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True

    def __init__(self):
        self.encode_faces()

    def encode_faces(self):
        # Only process image files (jpg, jpeg, png)
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        for image in os.listdir('static/Profiles'):
            if image.lower().endswith(valid_extensions):
                try:
                    face_image = face_recognition.load_image_file(f"static/Profiles/{image}")
                    face_encodings = face_recognition.face_encodings(face_image)
                    if face_encodings:  # Check if any faces were found
                        face_encoding = face_encodings[0]
                        self.known_face_encodings.append(face_encoding)
                        self.known_face_names.append(image)
                    else:
                        print(f"No face found in {image}")
                except Exception as e:
                    print(f"Error processing {image}: {e}")
        print(f"Loaded {len(self.known_face_names)} face profiles: {self.known_face_names}")

    def run_recognition(self):
        global Globalflag
        print(f'Face Detection Flag is {Globalflag}')
        text = ""

        while Globalflag:
            frame = get_camera_frame()
            if frame is None:
                print("No image captured for face detection")
                continue
                
            text = "Verified Student disappeared"
            print("Running Face Verification Function")
            # Only process every other frame of video to save time
            if self.process_current_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                #rgb_small_frame = small_frame[:, :, ::-1]
                rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

                # Find all the faces and face encodings in the current frame of video
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding,tolerance=0.85)
                    name = "Unknown"
                    confidence = '???'

                    # Calculate the shortest distance to face
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        tempname = str(self.known_face_names[best_match_index]).split('_')[0]
                        tempconfidence = face_confidence(face_distances[best_match_index])
                        if tempname == Student_Name and float(tempconfidence[:-1]) >= 84:
                            name = tempname
                            confidence = tempconfidence

                    self.face_names.append(f'{name} ({confidence})')

            self.process_current_frame = not self.process_current_frame

            # Display the results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                if "Unknown" not in name:
                    # Create the frame with the name
                    text = "Verified Student appeared"
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            # Display the resulting image
           # cv2.imshow('Face Recognition', frame)
            print(text)
            faceDetectionRecording(frame, text)
            # Hit 'q' on the keyboard to quit!

#Second: Head Movement Detection Function
def headMovmentDetection(image, face_mesh):
    print("Running HeadMovement Function")
    # Flip the image horizontally for a later selfie-view display
    # Also convert the color space from BGR to RGB
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # To improve performance
    image.flags.writeable = False

    # Get the result
    results = face_mesh.process(image)

    # To improve performance
    image.flags.writeable = True

    # Convert the color space from RGB to BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    img_h, img_w, img_c = image.shape
    face_3d = []
    face_2d = []

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):
                if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                    if idx == 1:
                        nose_2d = (lm.x * img_w, lm.y * img_h)
                        nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 8000)

                    x, y = int(lm.x * img_w), int(lm.y * img_h)

                    # Get the 2D Coordinates
                    face_2d.append([x, y])

                    # Get the 3D Coordinates
                    face_3d.append([x, y, lm.z])

                    # Convert it to the NumPy array
            face_2d = np.array(face_2d, dtype=np.float64)

            # Convert it to the NumPy array
            face_3d = np.array(face_3d, dtype=np.float64)

            # The camera matrix
            focal_length = 1 * img_w

            cam_matrix = np.array([[focal_length, 0, img_h / 2],
                                   [0, focal_length, img_w / 2],
                                   [0, 0, 1]])

            # The Distance Matrix
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            # Solve PnP
            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

            # Get rotational matrix
            rmat, jac = cv2.Rodrigues(rot_vec)

            # Get angles
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            # Get the y rotation degree
            x = angles[0] * 360
            y = angles[1] * 360
            # print(y)
            textHead = ''
            # See where the user's head tilting (relaxed thresholds for natural movement)
            if y < -15:  # Relaxed from -5 to allow more natural left movement
                textHead = "Looking Left"
            elif y > 15:  # Relaxed from 5 to allow more natural right movement
                textHead = "Looking Right"
            elif x < -15:  # Relaxed from -8 to allow more natural down movement
                textHead = "Looking Down"
            elif x > 20:  # Relaxed from 10 to allow more natural up movement
                textHead = "Looking Up"
            else:
                textHead = "Forward"
            # Add the text on the image
            cv2.putText(image, textHead, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            Head_record_duration(textHead, image)


#Third : More than one person Detection Function
def MTOP_Detection(img):
    print("Running MTOP Function")
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = faceDetection.process(imgRGB)
    textMTOP = ''
    if results.detections:
        for id, detection in enumerate(results.detections):
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, ic = img.shape
            bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                int(bboxC.width * iw), int(bboxC.height * ih)
            # Drawing the recantangle
            cv2.rectangle(img, bbox, (255, 0, 255), 2)
            # cv2.putText(img, f'{int(detection.score[0] * 100)}%', (bbox[0], bbox[1] - 20), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 10)
        if id > 0:
            textMTOP = "More than one person is detected."
        else:
            textMTOP = "Only one person is detected"
    else:
        textMTOP="Only one person is detected"
    MTOP_record_duration(textMTOP, img)
    print(textMTOP)

#Fourth : Screen Detection Function ( Key-words and Screens)
def shortcut_handler(event):
    if event.event_type == keyboard.KEY_DOWN:
        shortcut = ''
        # Check for Ctrl+C
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('c'):
            shortcut += 'Ctrl+C'
            print("Ctrl+C shortcut detected!")
        # Check for Ctrl+V
        elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('v'):
            shortcut += 'Ctrl+V'
            print("Ctrl+V shortcut detected!")
        # Check for Ctrl+A
        elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('a'):
            shortcut += 'Ctrl+A'
            print("Ctrl+A shortcut detected!")
        # Check for Ctrl+X
        elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('x'):
            shortcut += 'Ctrl+X'
            print("Ctrl+X shortcut detected!")
        # Check for Alt+Shift+Tab
        elif keyboard.is_pressed('alt') and keyboard.is_pressed('shift') and keyboard.is_pressed('tab'):
            shortcut += 'Alt+Shift+Tab'
            print("Alt+Shift+Tab shortcut detected!")
        # Check for Win+Tab
        elif keyboard.is_pressed('win') and keyboard.is_pressed('tab'):
            shortcut += 'Win+Tab'
            print("Win+Tab shortcut detected!")
        # Check for Alt+Esc
        elif keyboard.is_pressed('alt') and keyboard.is_pressed('esc'):
            shortcut += 'Alt+Esc'
            print("Alt+Esc shortcut detected!")
        # Check for Alt+Tab
        elif keyboard.is_pressed('alt') and keyboard.is_pressed('tab'):
            shortcut += 'Alt+Tab'
            print("Alt+Tab shortcut detected!")
        # Check for Ctrl+Esc
        elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('esc'):
            shortcut += 'Ctrl+Esc'
            print("Ctrl+Esc shortcut detected!")
        # Check for Function Keys F1
        elif keyboard.is_pressed('f1'):
            shortcut += 'F1'
            print("F1 shortcut detected")
        # Check for Function Keys F2
        elif keyboard.is_pressed('f2'):
            shortcut += 'F2'
            print("F2 shortcut detected!")
        # Check for Function Keys F3
        elif keyboard.is_pressed('f3'):
            shortcut += 'F3'
            print("F3 shortcut detected!")
        # Check for Window Key
        elif keyboard.is_pressed('win'):
            shortcut += 'Window'
            print("Window shortcut detected!")
        # Check for Ctrl+Alt+Del
        elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('alt') and keyboard.is_pressed('del'):
            shortcut += 'Ctrl+Alt+Del'
            print("Ctrl+Alt+Del shortcut detected!")
        # Check for Prt Scn
        elif keyboard.is_pressed('print_screen'):
            shortcut += 'Prt Scn'
            print("Prt Scn shortcut detected!")
        # Check for Ctrl+T
        elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('t'):
            shortcut += 'Ctrl+T'
            print("Ctrl+T shortcut detected!")
        # Check for Ctrl+W
        elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('w'):
            shortcut += 'Ctrl+W'
            print("Ctrl+W shortcut detected!")
        # Check for Ctrl+Z
        elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('z'):
            shortcut += 'Ctrl+Z'
            print("Ctrl+Z shortcut detected!")
        shorcuts.append(shortcut) if shortcut != "" else None

def screenDetection():
    global active_window, active_window_title, exam_window_title
    textScreen = ""
    
    # Get current active window
    new_active_window = gw.getActiveWindow()
    frame = capture_screen()

    # Titles that are allowed for the exam tab
    allowed_exam_titles = [
        "Exam — Google Chrome",
        "Exam - Google Chrome", 
        "localhost:5000 — Google Chrome",
        "localhost:5000 - Google Chrome",
        "Google Chrome",  # Generic Chrome (when tab title doesn't show)
        "Chrome"  # Sometimes just shows as Chrome
    ]

    if new_active_window is not None:
        current_title = new_active_window.title
        
        # Debug prints
        print(f"[DEBUG] Current window title: '{current_title}'")
        print(f"[DEBUG] Previous window title: '{active_window_title}'")
        print(f"[DEBUG] Contains 'Google Chrome': {'Google Chrome' in current_title}")
        print(f"[DEBUG] Contains 'Chrome': {'Chrome' in current_title}")
        print(f"[DEBUG] Contains ' — ': {' — ' in current_title}")
        print(f"[DEBUG] Contains ' - ': {' - ' in current_title}")
        print(f"[DEBUG] In allowed list: {current_title in allowed_exam_titles}")

        # --- CASE 1: User switched to another app (not Chrome at all) ---
        if "Google Chrome" not in current_title and "Chrome" not in current_title:
            print(f"[DEBUG] CASE 1: Not Chrome - '{current_title}'")
            if current_title != active_window_title:
                print("Moved to Another Application:", current_title)
                active_window = new_active_window
                active_window_title = new_active_window.title
            textScreen = "Move away from the Test"

        # --- CASE 2: User is in Chrome but potentially wrong tab ---
        elif current_title not in allowed_exam_titles:
            print(f"[DEBUG] CASE 2: Chrome but not in allowed list - '{current_title}'")
            # Only flag as violation if it's a specific tab title (contains " — " or " - ")
            if " — " in current_title or " - " in current_title:
                print(f"[DEBUG] CASE 2a: Specific tab detected (contains dash) - VIOLATION")
                if current_title != active_window_title:
                    print("Switched to Another Tab:", current_title)
                    active_window = new_active_window
                    active_window_title = new_active_window.title
                textScreen = "Move away from the Test"
            else:
                print(f"[DEBUG] CASE 2b: Generic Chrome title - ALLOWED")
                # Generic Chrome title, assume it's okay
                textScreen = "Stay in the Test"

        # --- CASE 3: User is in the correct exam tab ---
        else:
            print(f"[DEBUG] CASE 3: In allowed exam tab - '{current_title}'")
            textScreen = "Stay in the Test"
    else:
        print(f"[DEBUG] No active window detected")
        textScreen = "No active window detected"

    print(f"[DEBUG] Final decision: '{textScreen}'")
    print("=" * 50)
    SD_record_duration(textScreen, frame)
    print(textScreen)

#Fifth : Electronic Devices Detection Function
def electronicDevicesDetection(frame):
    global model, EDFlag
    # Predict on image
    detect_params = model.predict(source=[frame], conf=0.25, save=False)  # Reduced sensitivity: 0.45 -> 0.25
    # Convert tensor array to numpy
    DP = detect_params[0].numpy()
    for result in detect_params:  # iterate results
        boxes = result.boxes.cpu().numpy()  # get boxes on cpu in numpy
        for box in boxes:  # iterate boxes
            r = box.xyxy[0].astype(int)  # get corner points as int
            detected_obj = result.names[int(box.cls[0])]
            if (detected_obj == 'cell phone' or detected_obj == 'remote' or detected_obj == 'laptop' or detected_obj == 'laptop,book'): EDFlag = True
    textED = ''
    # Display the resulting frame
    if EDFlag:
        textED = 'Electronic Device Detected'
    else:
        textED = "No Electronic Device Detected"
    EDD_record_duration(textED, frame)
    print(textED)
    # Note: EDFlag is NOT reset here anymore - it will be managed by the caller

#Sixth Function : Voice Detection
class Recorder:
    @staticmethod
    def rms(frame):
        count = len(frame) / SHORT_WIDTH
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        try:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      output=True,
                                      frames_per_buffer=CHUNK)
            self.time = time.time()
            self.quiet = []
            self.quiet_idx = -1
            self.timeout = 0
            self.microphone_available = True
            print("Microphone initialized successfully")
        except Exception as e:
            print(f"Error initializing microphone: {e}")
            self.microphone_available = False
            self.p = None
            self.stream = None

    def record(self):
        global Globalflag
        print('')
        print(f'Voice Flag is {Globalflag}')
        
        if not hasattr(self, 'microphone_available') or not self.microphone_available:
            print("Microphone not available, skipping audio recording")
            return
            
        sound = []
        start = time.time()
        begin_time = None
        while Globalflag:
            try:
                data = self.stream.read(CHUNK)
                rms_val = self.rms(data)
                if self.inSound(data):
                    sound.append(data)
                    if begin_time == None:
                        begin_time = datetime.datetime.now()
                else:
                    if len(sound) > 0:
                        duration=math.floor((datetime.datetime.now()-begin_time).total_seconds())
                        self.write(sound, begin_time, duration)
                        sound.clear()
                        begin_time = None
                    else:
                        self.queueQuiet(data)

                curr = time.time()
                secs = int(curr - start)
                tout = 0 if self.timeout == 0 else int(self.timeout - curr)
                label = 'Listening' if self.timeout == 0 else 'Recording'
                print('[+] %s: Level=[%4.2f] Secs=[%d] Timeout=[%d]' % (label, rms_val, secs, tout), end='\r')
            except Exception as e:
                print(f"Error in audio recording: {e}")
                break

    # quiet is a circular buffer of size cushion
    def queueQuiet(self, data):
        self.quiet_idx += 1
        # start over again on overflow
        if self.quiet_idx == CUSHION_FRAMES:
            self.quiet_idx = 0

        # fill up the queue
        if len(self.quiet) < CUSHION_FRAMES:
            self.quiet.append(data)
        # replace the element on the index in a cicular loop like this 0 -> 1 -> 2 -> 3 -> 0 and so on...
        else:
            self.quiet[self.quiet_idx] = data

    def dequeueQuiet(self, sound):
        if len(self.quiet) == 0:
            return sound

        ret = []

        if len(self.quiet) < CUSHION_FRAMES:
            ret.append(self.quiet)
            ret.extend(sound)
        else:
            ret.extend(self.quiet[self.quiet_idx + 1:])
            ret.extend(self.quiet[:self.quiet_idx + 1])
            ret.extend(sound)

        return ret

    def inSound(self, data):
        rms = self.rms(data)
        curr = time.time()

        if rms > TRIGGER_RMS:
            self.timeout = curr + TIMEOUT_SECS
            return True

        if curr < self.timeout:
            return True

        self.timeout = 0
        return False

    def write(self, sound, begin_time, duration):
        # insert the pre-sound quiet frames into sound
        sound = self.dequeueQuiet(sound)

        # sound ends with TIMEOUT_FRAMES of quiet
        # remove all but CUSHION_FRAMES
        keep_frames = len(sound) - TIMEOUT_FRAMES + CUSHION_FRAMES
        recording = b''.join(sound[0:keep_frames])
        filename = str(random.randint(1,50000))+"VoiceViolation"
        pathname = os.path.join(f_name_directory, '{}.wav'.format(filename))
        wf = wave.open(pathname, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        voiceViolation = {
            "Name": "Common Noise is detected.",
            "Time": begin_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration": str(duration) + " seconds",
            "Mark": duration,
            "Link": '{}.wav'.format(filename),
            "RId": get_resultId()
        }
        write_json(voiceViolation)
        print('[+] Saved: {}'.format(pathname))

    def test_microphone(self):
        """Test microphone sensitivity and display real-time audio levels"""
        if not hasattr(self, 'microphone_available') or not self.microphone_available:
            print("Microphone not available for testing")
            return
            
        print("Testing microphone... Make some noise! Press Ctrl+C to stop")
        try:
            for i in range(100):  # Test for ~25 seconds
                data = self.stream.read(CHUNK)
                rms_val = self.rms(data)
                trigger_status = "TRIGGERED" if rms_val > TRIGGER_RMS else "quiet"
                print(f'Audio Level: {rms_val:.2f} | Trigger: {TRIGGER_RMS} | Status: {trigger_status}')
                time.sleep(0.25)
        except KeyboardInterrupt:
            print("\nMicrophone test stopped")
        except Exception as e:
            print(f"Error during microphone test: {e}")

def cheat_Detection1():
    deleteTrashVideos()
    global Globalflag
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    print(f'CD1 Flag is {Globalflag}')
    while Globalflag:
        image = get_camera_frame()
        if image is not None:
            headMovmentDetection(image, face_mesh)
        else:
            print("No image captured for head movement detection")
    deleteTrashVideos()

def screen_detection_thread():
    global Globalflag
    print(f'Screen Detection Thread Flag is {Globalflag}')
    deleteTrashVideos()
    while Globalflag:
        # Screen detection doesn't need camera frames, it captures screen directly
        screenDetection()
        time.sleep(0.1)  # Small delay for screen detection
    deleteTrashVideos()

def mtop_detection_thread():
    global Globalflag
    print(f'MTOP Detection Thread Flag is {Globalflag}')
    deleteTrashVideos()
    while Globalflag:
        image = get_camera_frame()
        if image is not None:
            MTOP_Detection(image)
        else:
            print("No image captured for MTOP detection")
    deleteTrashVideos()

def electronic_device_detection_thread():
    global Globalflag, EDFlag
    print(f'Electronic Device Detection Thread Flag is {Globalflag}')
    deleteTrashVideos()
    while Globalflag:
        image = get_camera_frame()
        if image is not None:
            EDFlag = False
            print("Electronic device detection is active")
            electronicDevicesDetection(image)
        else:
            print("No image captured for electronic device detection")
    deleteTrashVideos()

#Query Related
#Function to give the next resut id
def get_resultId():
    try:
        with open('result.json', 'r') as file:
            try:
                file_data = json.load(file)
                if not file_data:
                    return 1
                valid_data = [entry for entry in file_data if isinstance(entry.get("Id"), int)]
                if not valid_data:
                    return 1
                valid_data.sort(key=lambda x: x["Id"])
                return valid_data[-1]["Id"] + 1
            except json.JSONDecodeError:
                # File is empty or malformed
                return 1
    except FileNotFoundError:
        # File does not exist
        return 1

#Function to give the trust score
def get_TrustScore(Rid):
    try:
        with open('violation.json', 'r') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            filtered_data = [item for item in file_data if item.get("RId") == Rid]
            total_mark = sum(item.get("Mark", 0) for item in filtered_data)
            return total_mark
    except FileNotFoundError:
        # File does not exist
        print("violation.json not found.")
        return 0
    except json.JSONDecodeError:
        # File is empty or not valid JSON
        print("violation.json is empty or corrupt.")
        return 0
    except Exception as e:
        # Handle missing keys or other errors
        print(f"Error in get_TrustScore: {e}")
        return 0

#Function to give all results
def getResults():
    try:
        with open('result.json', 'r+') as file:
            # First we load existing data into a dict.
            result_data = json.load(file)
            return result_data
    except FileNotFoundError:
        # File does not exist, return empty list or dict as appropriate
        return []
    except json.JSONDecodeError:
        # File is empty or not valid JSON, return empty list or dict as appropriate
        return []
    except Exception as e:
        # Log or handle other exceptions as needed
        print(f"Error reading results: {e}")
        return []

#Function to give result details
def getResultDetails(rid):
    try:
        rid = int(rid)
        with open('result.json', 'r') as res_file:
            result_data = json.load(res_file)
            filtered_result = [item for item in result_data if item.get("Id") == rid]

        with open('violation.json', 'r') as vio_file:
            violation_data = json.load(vio_file)
            filtered_violations = [item for item in violation_data if item.get("RId") == rid]

        return {
            "Result": filtered_result,
            "Violation": filtered_violations
        }
    except FileNotFoundError as e:
        print(f"File missing: {e.filename}")
        return {}
    except json.JSONDecodeError:
        print("Invalid JSON format in result or violation file.")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}

a = Recorder()
fr = FaceRecognition()
