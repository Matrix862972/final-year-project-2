#!/usr/bin/env python3
"""Test script for the new double-buffered producer-consumer system"""
import time
import threading
import cv2
import utils

def test_double_buffer_system():
    """Test the double buffer system with multiple consumer threads"""
    print("🧪 Testing Double-Buffered Producer-Consumer System")
    print("=" * 55)
    
    # Initialize camera
    utils.cap = cv2.VideoCapture(0)
    if not utils.cap.isOpened():
        print("❌ Error: Could not open camera")
        return
    
    # Set global flag to start detection
    utils.Globalflag = True
    
    # Start camera producer thread
    camera_thread = threading.Thread(target=utils.camera_producer_thread, daemon=True)
    camera_thread.start()
    print("📹 Double-buffered camera producer thread started")
    
    # Test frame sharing with multiple consumers
    test_consumers = []
    
    def test_consumer(consumer_id, num_frames=5):
        """Test consumer that gets frames and reports success"""
        frames_received = 0
        total_lock_time = 0
        
        for i in range(num_frames):
            start_time = time.time()
            frame = utils.get_camera_frame(timeout=2.0)
            lock_time = time.time() - start_time
            total_lock_time += lock_time
            
            if frame is not None:
                frames_received += 1
                print(f"  Consumer {consumer_id}: Frame {i+1}/{num_frames} received ✅ (shape: {frame.shape}, lock_time: {lock_time:.4f}s)")
            else:
                print(f"  Consumer {consumer_id}: Frame {i+1}/{num_frames} TIMEOUT ❌")
            time.sleep(0.05)  # Small delay between frame requests
        
        avg_lock_time = total_lock_time / num_frames if num_frames > 0 else 0
        print(f"📊 Consumer {consumer_id} Summary: {frames_received}/{num_frames} frames, avg lock time: {avg_lock_time:.4f}s")
        return frames_received
    
    # Start multiple test consumers
    print("\n🔀 Starting 4 test consumers (testing double buffering)...")
    for i in range(4):
        consumer_thread = threading.Thread(
            target=test_consumer, 
            args=(f"C{i+1}", 3),  # 3 frames per consumer
            daemon=True
        )
        test_consumers.append(consumer_thread)
        consumer_thread.start()
    
    # Wait for all consumers to finish
    for thread in test_consumers:
        thread.join(timeout=10)
    
    # Test frame independence (each consumer gets its own copy)
    print("\n🎯 Testing Frame Independence...")
    frame1 = utils.get_camera_frame()
    frame2 = utils.get_camera_frame()
    
    if frame1 is not None and frame2 is not None:
        # Modify frame1 to test independence
        original_pixel = frame1[0, 0].copy()
        frame1[0, 0] = [255, 255, 255]  # Make corner white
        
        # Check if frame2 is unaffected
        if not (frame2[0, 0] == [255, 255, 255]).all():
            print("  ✅ Frame independence confirmed - double buffering works correctly")
        else:
            print("  ❌ Frame independence FAILED - copies are linked")
    
    # Test buffer performance
    print("\n⚡ Testing Double Buffer Performance...")
    start_time = time.time()
    frames_obtained = 0
    for i in range(10):
        frame = utils.get_camera_frame(timeout=0.1)
        if frame is not None:
            frames_obtained += 1
    
    total_time = time.time() - start_time
    fps = frames_obtained / total_time if total_time > 0 else 0
    print(f"  📈 Performance: {frames_obtained}/10 frames in {total_time:.2f}s ({fps:.1f} FPS)")
    
    # Stop the system
    print("\n🛑 Stopping test...")
    utils.Globalflag = False
    time.sleep(1)  # Give producer time to stop
    
    if utils.cap.isOpened():
        utils.cap.release()
    
    print("✅ Double buffer test completed!")

if __name__ == "__main__":
    test_double_buffer_system()
