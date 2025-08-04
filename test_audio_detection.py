#!/usr/bin/env python3
"""
Audio Detection Test Script
Tests the microphone audio monitoring and voice detection
"""

import pyaudio
import numpy as np
import threading
import time
import wave
import os

class AudioTester:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.audio_data = []
        self.violation_count = 0
        self.total_detections = 0
        
    def calculate_rms(self, data):
        """Calculate RMS (Root Mean Square) of audio data"""
        return np.sqrt(np.mean(data**2))
    
    def record_audio(self, duration=30):
        """Record and analyze audio for violations"""
        print(f"🎤 Recording audio for {duration} seconds...")
        print("Try speaking, making noise, or staying quiet to test detection")
        
        # Open audio stream
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        start_time = time.time()
        self.is_recording = True
        
        while self.is_recording and (time.time() - start_time) < duration:
            try:
                # Read audio data
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                audio_np = np.frombuffer(data, dtype=np.int16)
                
                # Calculate RMS level
                rms = self.calculate_rms(audio_np)
                
                # Audio detection threshold (set to handle very loud fan noise)
                if rms > 30:  # High threshold for very loud environment
                    self.violation_count += 1
                    status = f"❌ TALKING DETECTED - RMS: {rms:.2f}"
                    color_code = "\033[91m"  # Red
                else:
                    status = f"✅ QUIET - RMS: {rms:.2f}"
                    color_code = "\033[92m"  # Green
                
                # Display real-time status
                elapsed = int(time.time() - start_time)
                print(f"\r[{elapsed:2d}s] {color_code}{status}\033[0m | Violations: {self.violation_count}", 
                      end='', flush=True)
                
                self.total_detections += 1
                self.audio_data.append(audio_np)
                
                time.sleep(0.1)  # Small delay to prevent overwhelming output
                
            except Exception as e:
                print(f"\nError during recording: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        self.is_recording = False
        print("\n")  # New line after recording
    
    def save_test_audio(self):
        """Save recorded audio for analysis"""
        if not self.audio_data:
            return
        
        # Create output directory if it doesn't exist
        output_dir = "static/OutputAudios"
        os.makedirs(output_dir, exist_ok=True)
        
        # Combine all audio data
        combined_audio = np.concatenate(self.audio_data)
        
        # Save as WAV file
        filename = f"{output_dir}/audio_test_{int(time.time())}.wav"
        
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(combined_audio.tobytes())
            
            print(f"✅ Test audio saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
    
    def test_microphone_levels(self):
        """Test microphone input levels"""
        print("=== Microphone Level Test ===")
        print("Testing your microphone input levels...")
        print("Speak normally and observe the RMS values")
        print("Press Ctrl+C to stop")
        print()
        
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        try:
            max_rms = 0
            sample_count = 0
            
            while True:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                audio_np = np.frombuffer(data, dtype=np.int16)
                rms = self.calculate_rms(audio_np)
                
                max_rms = max(max_rms, rms)
                sample_count += 1
                
                # Visual RMS meter
                meter_length = 50
                meter_fill = int((rms / 100) * meter_length)
                meter = "█" * meter_fill + "░" * (meter_length - meter_fill)
                
                threshold_indicator = "🔊 TALKING" if rms > 30 else "🔇 quiet"
                
                print(f"\rRMS: {rms:6.2f} |{meter}| Max: {max_rms:6.2f} | {threshold_indicator}", 
                      end='', flush=True)
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print(f"\n\nMicrophone test completed!")
            print(f"Maximum RMS detected: {max_rms:.2f}")
            print(f"Detection threshold: 30.0 (set for very loud fan environment)")
            print(f"Samples tested: {sample_count}")
        
        stream.stop_stream()
        stream.close()
    
    def close(self):
        """Clean up audio resources"""
        self.audio.terminate()

def test_audio_detection():
    """Main audio detection test function"""
    
    print("=== Audio Detection Test ===")
    print("This will test the microphone monitoring system")
    print("Choose a test mode:")
    print("1. Real-time audio monitoring (30 seconds)")
    print("2. Microphone level testing (manual stop)")
    print()
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        tester = AudioTester()
        
        if choice == "1":
            print("\n--- Audio Violation Detection Test ---")
            tester.record_audio(30)
            
            print(f"Audio detection test completed!")
            print(f"Summary:")
            print(f"- Total violations: {tester.violation_count}")
            print(f"- Total samples: {tester.total_detections}")
            print(f"- Violation rate: {(tester.violation_count/max(1,tester.total_detections)*100):.1f}%")
            print(f"- Trigger: Speaking or making noise above RMS threshold of 30.0 (very loud fan environment)")
            
            # Save audio for analysis
            tester.save_test_audio()
            
        elif choice == "2":
            tester.test_microphone_levels()
        else:
            print("Invalid choice. Running default audio monitoring test...")
            tester.record_audio(30)
        
        tester.close()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"Error during audio test: {e}")

if __name__ == "__main__":
    test_audio_detection()
