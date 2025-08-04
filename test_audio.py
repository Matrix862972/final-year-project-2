#!/usr/bin/env python3
"""
Audio Detection Test Script for Online Exam Proctor
This script helps test and debug the audio detection system.
"""

import sys
import os
import time

# Add the current directory to the path so we can import utils
sys.path.append(os.path.dirname(__file__))

try:
    import utils
    
    print("=== Audio Detection Test ===")
    print("This script will test the microphone and audio detection system.")
    print()
    
    # Test 1: Check if microphone is available
    print("1. Testing microphone initialization...")
    recorder = utils.Recorder()
    
    if hasattr(recorder, 'microphone_available') and recorder.microphone_available:
        print("✓ Microphone initialized successfully!")
        
        # Test 2: Test audio sensitivity
        print("\n2. Testing audio sensitivity...")
        print("Make some noise (talk, clap, etc.) and watch the audio levels.")
        print("Audio will be detected when level > 3.0")
        print("Press Ctrl+C to stop the test.\n")
        
        recorder.test_microphone()
        
    else:
        print("✗ Microphone initialization failed!")
        print("Possible issues:")
        print("- No microphone connected")
        print("- Microphone permissions not granted")
        print("- Audio device in use by another application")
        
    # Test 3: Check Globalflag
    print(f"\n3. Current Globalflag status: {utils.Globalflag}")
    print("Note: Audio recording only works when Globalflag is True")
    print("This flag is set to True when an exam starts.")
    
    # Test 4: Check output directory
    print(f"\n4. Audio output directory: {utils.f_name_directory}")
    if os.path.exists(utils.f_name_directory):
        print("✓ Output directory exists")
    else:
        print("✗ Output directory doesn't exist")
        print("Creating directory...")
        os.makedirs(utils.f_name_directory, exist_ok=True)
        print("✓ Directory created")
    
    print("\n=== Test Complete ===")
    print("If audio detection is still not working:")
    print("1. Ensure microphone permissions are granted")
    print("2. Check if another app is using the microphone")
    print("3. Try increasing audio levels or making louder sounds")
    print("4. The Globalflag must be True for recording to start")
    
except ImportError as e:
    print(f"Error importing utils: {e}")
except Exception as e:
    print(f"Error during test: {e}")
