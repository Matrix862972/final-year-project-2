#!/usr/bin/env python3
"""
Keyboard Shortcut Detection Test Script
Tests the detection of prohibited keyboard shortcuts during exam
"""

import keyboard
import time
import threading
from collections import defaultdict

class KeyboardMonitor:
    def __init__(self):
        self.violation_count = 0
        self.key_combinations = defaultdict(int)
        self.start_time = time.time()
        self.is_monitoring = False
        
        # Prohibited key combinations (from main code)
        self.prohibited_shortcuts = [
            'alt+tab',      # Switch windows
            'ctrl+alt+del', # Task manager
            'ctrl+shift+esc', # Task manager direct
            'win+d',        # Show desktop
            'win+l',        # Lock screen
            'win+r',        # Run dialog
            'alt+f4',       # Close window
            'ctrl+alt+t',   # Terminal (Linux)
            'cmd+tab',      # Switch apps (Mac)
            'cmd+space',    # Spotlight (Mac)
            'ctrl+c',       # Copy
            'ctrl+v',       # Paste
            'ctrl+x',       # Cut
            'ctrl+a',       # Select all
            'ctrl+z',       # Undo
            'ctrl+y',       # Redo
            'ctrl+s',       # Save
            'ctrl+o',       # Open
            'ctrl+n',       # New
            'ctrl+w',       # Close tab
            'ctrl+t',       # New tab
            'f11',          # Fullscreen toggle
            'alt+enter',    # Properties/fullscreen
        ]
    
    def on_key_combination(self, shortcut):
        """Handle detected key combination"""
        if not self.is_monitoring:
            return
            
        current_time = time.time()
        elapsed = int(current_time - self.start_time)
        
        self.key_combinations[shortcut] += 1
        
        if shortcut.lower() in [s.lower() for s in self.prohibited_shortcuts]:
            self.violation_count += 1
            print(f"[{elapsed:3d}s] ❌ VIOLATION: {shortcut.upper()} - Count: {self.violation_count}")
        else:
            print(f"[{elapsed:3d}s] ✅ Allowed: {shortcut}")
    
    def start_monitoring(self, duration=60):
        """Start monitoring keyboard shortcuts for specified duration"""
        
        print("=== Keyboard Shortcut Detection Test ===")
        print(f"Monitoring keyboard shortcuts for {duration} seconds")
        print("Try using various keyboard shortcuts to test detection")
        print()
        print("Prohibited shortcuts include:")
        for i, shortcut in enumerate(self.prohibited_shortcuts[:12]):  # Show first 12
            print(f"  - {shortcut}")
        if len(self.prohibited_shortcuts) > 12:
            print(f"  ... and {len(self.prohibited_shortcuts) - 12} more")
        print()
        print("Press ESC to stop monitoring early")
        print("-" * 50)
        
        self.is_monitoring = True
        self.start_time = time.time()
        
        # Register hotkeys for prohibited shortcuts
        for shortcut in self.prohibited_shortcuts:
            try:
                keyboard.add_hotkey(shortcut, 
                                   lambda s=shortcut: self.on_key_combination(s))
            except:
                pass  # Some shortcuts might not be valid on this system
        
        # Register some additional common shortcuts for testing
        additional_shortcuts = [
            'ctrl+enter', 'shift+enter', 'ctrl+shift+enter',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f12',
            'ctrl+1', 'ctrl+2', 'ctrl+3',
            'alt+1', 'alt+2', 'alt+3'
        ]
        
        for shortcut in additional_shortcuts:
            try:
                keyboard.add_hotkey(shortcut, 
                                   lambda s=shortcut: self.on_key_combination(s))
            except:
                pass
        
        # Monitor for ESC key to stop
        keyboard.add_hotkey('esc', self.stop_monitoring)
        
        # Wait for duration or until stopped
        try:
            while self.is_monitoring and (time.time() - self.start_time) < duration:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring and show results"""
        self.is_monitoring = False
        
        # Clear all hotkeys
        keyboard.clear_all_hotkeys()
        
        elapsed_time = int(time.time() - self.start_time)
        
        print("\n" + "=" * 50)
        print("Keyboard monitoring test completed!")
        print(f"Duration: {elapsed_time} seconds")
        print(f"Total violations: {self.violation_count}")
        
        if self.key_combinations:
            print("\nDetected shortcuts:")
            for shortcut, count in sorted(self.key_combinations.items()):
                is_prohibited = shortcut.lower() in [s.lower() for s in self.prohibited_shortcuts]
                status = "❌ PROHIBITED" if is_prohibited else "✅ Allowed"
                print(f"  {shortcut}: {count} times - {status}")
        else:
            print("No shortcuts detected during test")
        
        print(f"\nTrigger: Any prohibited keyboard shortcut usage")

def test_keyboard_shortcuts():
    """Main keyboard shortcut test function"""
    
    try:
        print("Starting keyboard shortcut monitoring...")
        print("Note: This test requires administrator privileges on some systems")
        print()
        
        duration = 60  # Test for 1 minute
        
        try:
            duration_input = input(f"Enter test duration in seconds (default {duration}): ").strip()
            if duration_input:
                duration = int(duration_input)
        except ValueError:
            print("Invalid input, using default duration")
        
        monitor = KeyboardMonitor()
        monitor.start_monitoring(duration)
        
    except PermissionError:
        print("❌ Error: This test requires administrator privileges")
        print("Please run the script as administrator")
    except Exception as e:
        print(f"❌ Error during keyboard monitoring: {e}")
        print("Some keyboard shortcuts might not be detectable on this system")

if __name__ == "__main__":
    test_keyboard_shortcuts()
