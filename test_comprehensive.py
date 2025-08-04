#!/usr/bin/env python3
"""
Comprehensive Detection Test Script
Tests head movement and screen detection with the new sensitive thresholds
"""

import cv2
import mediapipe as mp
import numpy as np
import pygetwindow as gw
import time
import threading

class DetectionTester:
    def __init__(self):
        self.running = True
        self.head_status = "Forward"
        self.screen_status = "Stay in the Test"
        
        # More sensitive thresholds (matching updated utils.py)
        self.head_thresholds = {
            'left': -5,    # More sensitive
            'right': 5,    # More sensitive  
            'down': -8,    # More sensitive
            'up': 10       # More sensitive
        }
        
    def test_head_movement(self):
        """Test head movement detection in a separate thread"""
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        cap = cv2.VideoCapture(0)
        
        while self.running:
            success, image = cap.read()
            if not success:
                continue
                
            # Process image
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = face_mesh.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            img_h, img_w, img_c = image.shape
            face_3d = []
            face_2d = []
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    for idx, lm in enumerate(face_landmarks.landmark):
                        if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                            x, y = int(lm.x * img_w), int(lm.y * img_h)
                            face_2d.append([x, y])
                            face_3d.append([x, y, lm.z])

                    face_2d = np.array(face_2d, dtype=np.float64)
                    face_3d = np.array(face_3d, dtype=np.float64)

                    focal_length = 1 * img_w
                    cam_matrix = np.array([[focal_length, 0, img_h / 2],
                                         [0, focal_length, img_w / 2],
                                         [0, 0, 1]])
                    dist_matrix = np.zeros((4, 1), dtype=np.float64)

                    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
                    rmat, jac = cv2.Rodrigues(rot_vec)
                    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                    x = angles[0] * 360
                    y = angles[1] * 360
                    
                    # Apply new sensitive thresholds
                    if y < self.head_thresholds['left']:
                        self.head_status = "Looking Left"
                    elif y > self.head_thresholds['right']:
                        self.head_status = "Looking Right"
                    elif x < self.head_thresholds['down']:
                        self.head_status = "Looking Down"
                    elif x > self.head_thresholds['up']:
                        self.head_status = "Looking Up"
                    else:
                        self.head_status = "Forward"
                        
            time.sleep(0.1)  # Small delay
            
        cap.release()
    
    def test_screen_detection(self):
        """Test screen detection in main thread"""
        exam_window_title = "Exam — Mozilla Firefox"
        
        while self.running:
            try:
                new_active_window = gw.getActiveWindow()
                
                if new_active_window is not None and new_active_window.title != exam_window_title:
                    self.screen_status = "Move away from the Test"
                else:
                    self.screen_status = "Stay in the Test"
                    
            except Exception as e:
                self.screen_status = f"Error: {e}"
                
            time.sleep(0.5)
    
    def run_test(self):
        """Run comprehensive detection test"""
        print("=== Comprehensive Detection Test ===")
        print("Testing with NEW SENSITIVE thresholds:")
        print(f"Head Movement - Left: {self.head_thresholds['left']}, Right: {self.head_thresholds['right']}")
        print(f"              Down: {self.head_thresholds['down']}, Up: {self.head_thresholds['up']}")
        print()
        print("Instructions:")
        print("1. Test head movements (left, right, up, down)")
        print("2. Switch between windows to test screen detection")
        print("3. Press Ctrl+C to stop")
        print()
        
        # Start head movement detection in separate thread
        head_thread = threading.Thread(target=self.test_head_movement)
        head_thread.daemon = True
        head_thread.start()
        
        try:
            # Run screen detection in main thread
            start_time = time.time()
            while True:
                self.test_screen_detection()
                
                # Print status every second
                elapsed = int(time.time() - start_time)
                print(f"[{elapsed:3d}s] Head: {self.head_status:15} | Screen: {self.screen_status}", end='\r')
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nTest stopped by user")
            self.running = False
            
        print("Test completed!")

if __name__ == "__main__":
    tester = DetectionTester()
    tester.run_test()
