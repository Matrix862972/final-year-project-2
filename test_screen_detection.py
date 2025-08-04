#!/usr/bin/env python3
"""
Screen Detection Test Script
This script tests the screen/window detection functionality
"""

import pygetwindow as gw
import time

def test_screen_detection():
    """Test screen detection functionality"""
    
    print("=== Screen Detection Test ===")
    print("This will monitor window changes for 30 seconds")
    print("Try switching between different applications to test detection")
    print()
    
    # Expected exam window title (should match your browser)
    exam_window_titles = [
        "Chrome",
        "Google Chrome",
        "Exam — Google Chrome",
        "Online Exam Proctor",
        "Mozilla Firefox",
        "Edge"
    ]
    
    active_window_title = None
    
    for i in range(30):  # Test for 30 seconds
        try:
            # Get the current active window
            new_active_window = gw.getActiveWindow()
            
            if new_active_window is not None:
                current_title = new_active_window.title
                
                # Check if window changed
                if current_title != active_window_title:
                    active_window_title = current_title
                    print(f"[{i:2d}s] Window changed to: '{current_title}'")
                    
                    # Check if it's exam window or not
                    is_exam_window = any(exam_title in current_title for exam_title in exam_window_titles)
                    
                    if is_exam_window:
                        status = "✅ STAY IN TEST"
                        print(f"      Status: {status}")
                    else:
                        status = "❌ MOVE AWAY FROM TEST - VIOLATION!"
                        print(f"      Status: {status}")
                else:
                    # Same window, just show status
                    is_exam_window = any(exam_title in current_title for exam_title in exam_window_titles)
                    status = "✅ OK" if is_exam_window else "❌ VIOLATION"
                    print(f"[{i:2d}s] Current: '{current_title[:30]}...' - {status}", end='\r')
            else:
                print(f"[{i:2d}s] No active window detected")
                
        except Exception as e:
            print(f"[{i:2d}s] Error: {e}")
            
        time.sleep(1)
    
    print("\n\nScreen detection test completed!")
    print("Summary:")
    print("- Switching to any non-exam window should trigger 'Move away from Test'")
    print("- Staying in browser/exam window should show 'Stay in the Test'")

if __name__ == "__main__":
    test_screen_detection()
