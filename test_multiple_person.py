#!/usr/bin/env python3
"""
Multiple Person Detection Test Script
Tests the detection of multiple persons in the video feed
"""

import cv2
import mediapipe as mp
import time

def test_multiple_person_detection():
    """Test multiple person detection using MediaPipe"""
    
    print("=== Multiple Person Detection Test ===")
    print("This will detect multiple faces/persons in the camera feed")
    print("Try having different people in the frame or showing photos")
    print("Press 'q' to quit")
    print()
    
    # Initialize MediaPipe face detection
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    violation_count = 0
    start_time = time.time()
    
    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read from camera")
                break
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb_frame)
            
            # Count faces
            num_faces = 0
            if results.detections:
                num_faces = len(results.detections)
                
                # Draw detections
                for detection in results.detections:
                    mp_drawing.draw_detection(frame, detection)
            
            # Determine status
            if num_faces == 0:
                status_text = "No Person Detected"
                status_color = (0, 165, 255)  # Orange
            elif num_faces == 1:
                status_text = "✅ Single Person - OK"
                status_color = (0, 255, 0)  # Green
            else:
                status_text = f"❌ {num_faces} Persons - VIOLATION!"
                status_color = (0, 0, 255)  # Red
                violation_count += 1
            
            # Display information
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
            cv2.putText(frame, f"Faces Detected: {num_faces}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Violations: {violation_count}", (10, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Time: {int(time.time() - start_time)}s", (10, 130), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Multiple Person Detection Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()
    
    elapsed_time = int(time.time() - start_time)
    print(f"\nMultiple person detection test completed!")
    print(f"Summary:")
    print(f"- Test duration: {elapsed_time} seconds")
    print(f"- Total violations: {violation_count}")
    print(f"- Trigger: Having more than 1 person in the frame")

if __name__ == "__main__":
    test_multiple_person_detection()
