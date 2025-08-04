#!/usr/bin/env python3
"""
Face Recognition Test Script
Tests the face verification system with real-time feedback
"""

import cv2
import face_recognition
import numpy as np
import os

def test_face_recognition():
    """Test face recognition detection with real profiles"""
    
    print("=== Face Recognition Test ===")
    print("This will test face verification against your registered profiles")
    print("Press 'q' to quit, 'c' to capture a test profile")
    print()
    
    # Load known faces from profiles
    known_face_encodings = []
    known_face_names = []
    
    profiles_dir = 'static/Profiles'
    if not os.path.exists(profiles_dir):
        print(f"❌ Error: {profiles_dir} directory not found!")
        print("Please run the main application first to create profiles")
        return
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    profile_files = [f for f in os.listdir(profiles_dir) if f.lower().endswith(valid_extensions)]
    
    if not profile_files:
        print(f"❌ No profile images found in {profiles_dir}")
        print("Please add some profile images first")
        return
    
    print(f"Loading {len(profile_files)} profile(s)...")
    for image_file in profile_files:
        try:
            face_image = face_recognition.load_image_file(f"{profiles_dir}/{image_file}")
            face_encodings = face_recognition.face_encodings(face_image)
            if face_encodings:
                face_encoding = face_encodings[0]
                known_face_encodings.append(face_encoding)
                known_face_names.append(image_file.split('_')[0])  # Extract name
                print(f"✅ Loaded: {image_file}")
            else:
                print(f"❌ No face found in: {image_file}")
        except Exception as e:
            print(f"❌ Error loading {image_file}: {e}")
    
    if not known_face_encodings:
        print("❌ No valid face profiles loaded!")
        return
    
    print(f"\n📊 Loaded {len(known_face_encodings)} face profile(s)")
    print("Starting camera...")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read from camera")
            break
        
        # Find faces in current frame
        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Default status
        status_text = "Verified Student disappeared"
        status_color = (0, 0, 255)  # Red
        confidence_text = ""
        
        # Check each face
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            
            name = "Unknown"
            confidence = 0
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    # Calculate confidence (simplified)
                    confidence = max(0, (1.0 - face_distances[best_match_index]) * 100)
                    
                    if confidence >= 84:  # Threshold from main code
                        status_text = "Verified Student appeared"
                        status_color = (0, 255, 0)  # Green
                    
            confidence_text = f"{confidence:.1f}%"
            
            # Draw rectangle and label
            cv2.rectangle(frame, (left, top), (right, bottom), status_color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), status_color, cv2.FILLED)
            cv2.putText(frame, f"{name} ({confidence_text})", (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        # Display status
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Face Recognition Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Face recognition test completed!")

if __name__ == "__main__":
    test_face_recognition()
