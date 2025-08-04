#!/usr/bin/env python3
"""
Electronic Device Detection Test Script
Tests the YOLO-based object detection for phones, laptops, etc.
"""

import cv2
from ultralytics import YOLO
import numpy as np

def test_electronic_device_detection():
    """Test electronic device detection using YOLO"""
    
    print("=== Electronic Device Detection Test ===")
    print("This will detect electronic devices like phones, laptops, tablets")
    print("Try showing your phone, laptop, or other devices to the camera")
    print("Press 'q' to quit")
    print()
    
    # Load YOLO model
    try:
        model = YOLO('yolov8n.pt')
        print("✅ YOLO model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading YOLO model: {e}")
        return
    
    # Electronic device class IDs from COCO dataset
    electronic_devices = {
        63: 'laptop',
        67: 'cell phone',
        72: 'tv',
        73: 'laptop',  # Alternative ID
        76: 'keyboard',
        77: 'mouse'
    }
    
    print("Monitored devices:")
    for device_id, device_name in electronic_devices.items():
        print(f"  - {device_name} (ID: {device_id})")
    print()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    violation_count = 0
    detected_devices = set()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read from camera")
            break
        
        # Run YOLO detection
        results = model(frame, verbose=False)
        
        current_devices = []
        
        # Process detections
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Check if it's an electronic device with good confidence
                    if class_id in electronic_devices and confidence > 0.5:
                        device_name = electronic_devices[class_id]
                        current_devices.append(device_name)
                        detected_devices.add(device_name)
                        
                        # Draw bounding box
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(frame, f"{device_name} {confidence:.2f}", 
                                   (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Determine status
        if current_devices:
            status_text = f"❌ VIOLATION: {', '.join(set(current_devices))} detected"
            status_color = (0, 0, 255)  # Red
            violation_count += 1
        else:
            status_text = "✅ No electronic devices detected"
            status_color = (0, 255, 0)  # Green
        
        # Display information
        cv2.putText(frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        cv2.putText(frame, f"Violations: {violation_count}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if detected_devices:
            devices_text = f"Detected: {', '.join(detected_devices)}"
            cv2.putText(frame, devices_text, (10, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Electronic Device Detection Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nElectronic device detection test completed!")
    print(f"Summary:")
    print(f"- Total violations: {violation_count}")
    print(f"- Devices detected during test: {list(detected_devices)}")
    print(f"- Trigger: Any electronic device (phone, laptop, etc.) in view")

if __name__ == "__main__":
    test_electronic_device_detection()
