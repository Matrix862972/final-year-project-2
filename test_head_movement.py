#!/usr/bin/env python3
"""
Head Movement Detection Test Script
This script tests the head movement detection functionality independently
"""

import cv2
import mediapipe as mp
import numpy as np
import time

def test_head_movement_detection():
    """Test head movement detection with real-time feedback"""
    
    # Initialize MediaPipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    print("=== Head Movement Detection Test ===")
    print("Instructions:")
    print("- Look straight ahead (should show 'Forward')")
    print("- Turn left and right slowly")
    print("- Look up and down")
    print("- Press 'q' to quit")
    print("- Press 's' to make detection more sensitive")
    print("- Press 'l' to make detection less sensitive")
    print()
    
    # Threshold values (updated to match new relaxed main application settings)
    thresholds = {
        'left': -15,    # Relaxed from -5 to match new main app setting
        'right': 15,    # Relaxed from 5 to match new main app setting
        'down': -15,    # Relaxed from -8 to match new main app setting
        'up': 20        # Relaxed from 10 to match new main app setting
    }
    
    while True:
        success, image = cap.read()
        if not success:
            print("Failed to read from camera")
            break
            
        # Flip the image horizontally for a later selfie-view display
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Get the result
        results = face_mesh.process(image)
        
        # Convert back to BGR for OpenCV
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        img_h, img_w, img_c = image.shape
        face_3d = []
        face_2d = []
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw face mesh for visual feedback
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())
                
                # Extract key landmarks for pose estimation
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                        if idx == 1:
                            nose_2d = (lm.x * img_w, lm.y * img_h)
                            nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 8000)

                        x, y = int(lm.x * img_w), int(lm.y * img_h)
                        face_2d.append([x, y])
                        face_3d.append([x, y, lm.z])

                # Convert to numpy arrays
                face_2d = np.array(face_2d, dtype=np.float64)
                face_3d = np.array(face_3d, dtype=np.float64)

                # Camera matrix
                focal_length = 1 * img_w
                cam_matrix = np.array([[focal_length, 0, img_h / 2],
                                     [0, focal_length, img_w / 2],
                                     [0, 0, 1]])

                # Distortion matrix
                dist_matrix = np.zeros((4, 1), dtype=np.float64)

                # Solve PnP
                success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                # Get rotational matrix
                rmat, jac = cv2.Rodrigues(rot_vec)

                # Get angles
                angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                # Get the rotation degrees
                x = angles[0] * 360
                y = angles[1] * 360
                
                # Determine head position with current thresholds
                textHead = ''
                color = (0, 255, 0)  # Green for forward
                
                if y < thresholds['left']:
                    textHead = "Looking Left"
                    color = (0, 0, 255)  # Red
                elif y > thresholds['right']:
                    textHead = "Looking Right"
                    color = (0, 0, 255)  # Red
                elif x < thresholds['down']:
                    textHead = "Looking Down"
                    color = (0, 0, 255)  # Red
                elif x > thresholds['up']:
                    textHead = "Looking Up"
                    color = (0, 0, 255)  # Red
                else:
                    textHead = "Forward"
                    color = (0, 255, 0)  # Green

                # Display information on image
                cv2.putText(image, textHead, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                cv2.putText(image, f"X: {x:.1f} Y: {y:.1f}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Display thresholds
                cv2.putText(image, f"Thresholds - L:{thresholds['left']} R:{thresholds['right']} D:{thresholds['down']} U:{thresholds['up']}", 
                           (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Display instructions
                cv2.putText(image, "Press 's' for more sensitive, 'l' for less sensitive, 'q' to quit", 
                           (20, img_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Show the image
        cv2.imshow('Head Movement Detection Test', image)
        
        # Handle key presses
        key = cv2.waitKey(5) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):  # More sensitive
            thresholds['left'] += 1
            thresholds['right'] -= 1
            thresholds['down'] += 1
            thresholds['up'] -= 1
            print(f"More sensitive: {thresholds}")
        elif key == ord('l'):  # Less sensitive
            thresholds['left'] -= 1
            thresholds['right'] += 1
            thresholds['down'] -= 1
            thresholds['up'] += 1
            print(f"Less sensitive: {thresholds}")

    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nFinal thresholds: {thresholds}")
    print("You can use these values to update the main utils.py file")

if __name__ == "__main__":
    test_head_movement_detection()
