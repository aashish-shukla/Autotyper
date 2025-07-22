import pyautogui
import pyperclip
import time
import random
import threading
import sys

# Typing states
TYPING_STOPPED = 0
TYPING_ACTIVE = 1
TYPING_PAUSED = 2

typing_state = TYPING_STOPPED
typing_thread = None

# WPM Configuration
DEFAULT_BASE_WPM = 85  # Base typing speed (increased from 65)
WPM_VARIATION = 0.3    # 30% variation (±25 WPM from base)
FATIGUE_FACTOR = 0.12  # 12% slowdown over time (reduced from 15%)
BURST_CHANCE = 0.10    # 10% chance of fast burst (increased from 8%)
HESITATION_CHANCE = 0.04  # 4% chance of hesitation (reduced from 5%)

# Enhanced human-like timing
MICRO_PAUSE_CHANCE = 0.15  # 15% chance of tiny micro-pauses
RHYTHM_VARIATION = 0.4     # 40% rhythm variation between keystrokes
TYPING_FLOW_STATES = ['steady', 'rushed', 'careful', 'thinking']

def get_typing_flow_state():
    """Randomly select a typing flow state that affects multiple characters"""
    return random.choice(TYPING_FLOW_STATES)

def calculate_char_delay(base_wpm, char, position, total_chars, flow_state='steady'):
    """Calculate delay for a character based on WPM and various human factors"""
    
    # Apply fatigue (gradual slowdown)
    fatigue_multiplier = 1 + (FATIGUE_FACTOR * position / total_chars)
    current_wpm = base_wpm / fatigue_multiplier
    
    # Random WPM variation for each character
    wpm_modifier = random.uniform(1 - WPM_VARIATION, 1 + WPM_VARIATION)
    current_wpm *= wpm_modifier
    
    # Micro-rhythm variations (small random delays between keystrokes)
    rhythm_modifier = random.uniform(1 - RHYTHM_VARIATION, 1 + RHYTHM_VARIATION)
    
    # Flow state modifiers
    flow_modifiers = {
        'steady': 1.0,      # Normal typing
        'rushed': 0.7,      # Typing quickly
        'careful': 1.4,     # Deliberate typing
        'thinking': 1.8     # Thoughtful typing
    }
    flow_modifier = flow_modifiers.get(flow_state, 1.0)
    
    # Character-specific modifiers (enhanced)
    char_modifier = 1.0
    if char in '.!?':
        char_modifier = random.uniform(2.5, 4.0)  # Variable pause for sentence endings
    elif char in ',;:':
        char_modifier = random.uniform(1.5, 2.5)  # Variable pause for punctuation
    elif char == ' ':
        char_modifier = random.uniform(0.6, 1.0)  # Spaces vary in speed
    elif char.isupper():
        char_modifier = random.uniform(1.1, 1.4)  # Capitals vary slightly
    elif char.isdigit():
        char_modifier = random.uniform(1.2, 1.6)  # Numbers need thought
    elif char in '()[]{}':
        char_modifier = random.uniform(1.3, 1.7)  # Brackets need precision
    elif char in '"\'':
        char_modifier = random.uniform(1.0, 1.3)  # Quotes need care
    elif char in '!@#$%^&*':
        char_modifier = random.uniform(1.4, 1.8)  # Special symbols slower
    
    # Common letter combinations (faster for familiar patterns)
    # This would be implemented with context from previous characters
    
    # Special typing patterns
    if random.random() < BURST_CHANCE:
        char_modifier *= random.uniform(0.3, 0.6)  # Variable fast burst
    elif random.random() < HESITATION_CHANCE:
        char_modifier *= random.uniform(2.0, 3.5)  # Variable hesitation
    elif random.random() < MICRO_PAUSE_CHANCE:
        char_modifier *= random.uniform(1.2, 1.8)  # Small micro-pauses
    
    # Convert WPM to character delay
    chars_per_second = (current_wpm * 5) / 60
    base_delay = 1.0 / chars_per_second
    
    # Apply all modifiers
    final_delay = base_delay * char_modifier * rhythm_modifier * flow_modifier
    
    # Add tiny random jitter (±10ms) to make it more natural
    jitter = random.uniform(-0.01, 0.01)
    final_delay = max(0.01, final_delay + jitter)  # Minimum 10ms delay
    
    return final_delay

def human_type(text, base_wpm=DEFAULT_BASE_WPM):
    """Type text character by character with enhanced human-like behavior"""
    global typing_state
    
    if not text:
        print("[WARNING] No text to type!")
        return
    
    print(f"[INFO] 🚀 Starting to type {len(text)} characters...")
    print(f"[INFO] ⚡ Target WPM: {base_wpm} (±{int(base_wpm * WPM_VARIATION)})")
    print(f"[INFO] 🎮 Controls: F8=Pause | F9=Resume/Start | F10=Stop")
    
    start_time = time.time()
    chars_typed = 0
    current_flow_state = get_typing_flow_state()
    flow_change_counter = 0
    
    print(f"[INFO] 🌊 Starting with '{current_flow_state}' typing flow")
    
    for i, char in enumerate(text):
        # Check for pause
        while typing_state == TYPING_PAUSED:
            time.sleep(0.1)
            
        # Check for stop
        if typing_state == TYPING_STOPPED:
            print(f"\n[INFO] 🛑 Typing stopped at character {i+1}/{len(text)}")
            break
        
        # Change typing flow state occasionally (every 20-50 characters)
        flow_change_counter += 1
        if flow_change_counter > random.randint(20, 50):
            current_flow_state = get_typing_flow_state()
            flow_change_counter = 0
            # Uncomment to see flow changes: print(f"[DEBUG] Flow changed to: {current_flow_state}")
        
        # Handle special characters properly
        if char == '\n':
            pyautogui.press('enter')
        elif char == '\t':
            pyautogui.press('tab')
        elif char == '\r':
            continue
        else:
            pyautogui.write(char)
        
        chars_typed += 1
        
        # Calculate human-like delay with enhanced variability
        delay = calculate_char_delay(base_wpm, char, i, len(text), current_flow_state)
        time.sleep(delay)
        
        # Progress update every 50 characters
        if chars_typed % 50 == 0:
            elapsed_time = time.time() - start_time
            current_wpm = (chars_typed / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0
            progress = (chars_typed / len(text)) * 100
            print(f"[PROGRESS] {progress:.1f}% | Current WPM: {current_wpm:.1f} | Flow: {current_flow_state}")
    
    # Auto-stop after completion
    if typing_state == TYPING_ACTIVE:
        elapsed_time = time.time() - start_time
        final_wpm = (chars_typed / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0
        print(f"\n[SUCCESS] ✅ Finished typing {chars_typed} characters!")
        print(f"[STATS] ⏱️  Total time: {elapsed_time:.1f}s | Average WPM: {final_wpm:.1f}")
    
    typing_state = TYPING_STOPPED

def start_typing(custom_wpm=None):
    """Start typing clipboard content with optional custom WPM"""
    global typing_state, typing_thread
    
    if typing_state == TYPING_ACTIVE:
        print("[INFO] ⚠️  Already typing! Use F8 to pause or F10 to stop.")
        return
    
    # Get clipboard content
    try:
        text = pyperclip.paste()
    except Exception as e:
        print(f"[ERROR] ❌ Could not access clipboard: {e}")
        return
    
    # Validate clipboard content
    if not text or not text.strip():
        print("[WARNING] ⚠️  Clipboard is empty or contains only whitespace!")
        return
    
    # Show what will be typed
    char_count = len(text)
    line_count = text.count('\n') + 1
    word_count = len(text.split())
    
    print(f"\n[INFO] 📋 Ready to type clipboard content:")
    print(f"[INFO] 📊 Stats: {char_count} chars, {word_count} words, {line_count} lines")
    
    # Calculate estimated time
    wpm = custom_wpm or DEFAULT_BASE_WPM
    estimated_time = (word_count / wpm) * 60
    print(f"[INFO] ⏱️  Estimated time at {wpm} WPM: {estimated_time:.1f} seconds")
    
    # Show preview
    preview = text.replace('\n', '↵').replace('\t', '→').replace('\r', '')
    print(f"[INFO] 👀 Preview: {preview[:100]}{'...' if len(preview) > 100 else ''}")
    
    # Countdown
    print(f"[INFO] ⏰ Typing starts in 3 seconds... Position your cursor!")
    for i in range(3, 0, -1):
        print(f"[INFO] ⏱️  {i}...")
        time.sleep(1)
    
    # Start typing
    typing_state = TYPING_ACTIVE
    typing_thread = threading.Thread(target=human_type, args=(text, wpm), daemon=True)
    typing_thread.start()

def pause_typing():
    """Pause typing"""
    global typing_state
    
    if typing_state == TYPING_ACTIVE:
        typing_state = TYPING_PAUSED
        print(f"\n[INFO] ⏸️  Typing PAUSED. Press F9 to resume.")
    else:
        print(f"[INFO] ⚠️  No active typing to pause. Use F9 to start.")

def stop_typing():
    """Stop typing completely"""
    global typing_state
    
    if typing_state in [TYPING_ACTIVE, TYPING_PAUSED]:
        typing_state = TYPING_STOPPED
        print(f"\n[INFO] 🛑 Typing STOPPED.")
    else:
        print(f"[INFO] ⚠️  No active typing to stop.")

def resume_or_start():
    """Resume if paused, or start new typing"""
    global typing_state
    
    if typing_state == TYPING_PAUSED:
        typing_state = TYPING_ACTIVE
        print(f"\n[INFO] ▶️  Typing RESUMED.")
    else:
        start_typing()

def test_accessibility_permissions():
    """Test if we have proper accessibility permissions"""
    try:
        import keyboard
        
        # Quick permission test
        keyboard.is_pressed('space')
        
        def test_listen():
            try:
                keyboard.wait('f12', timeout=0.01)
            except:
                pass
        
        test_thread = threading.Thread(target=test_listen, daemon=True)
        test_thread.start()
        test_thread.join(timeout=0.1)
        
        return True
        
    except OSError as e:
        if "administrator" in str(e).lower() or "error 13" in str(e).lower():
            return False
        raise e
    except Exception:
        return False

def start_typing_slow():
    """Start typing in slow mode (50 WPM)"""
    global DEFAULT_BASE_WPM
    DEFAULT_BASE_WPM = 50
    print(f"\n[INFO] 🐌 SLOW MODE activated: {DEFAULT_BASE_WPM} WPM")
    start_typing()

def start_typing_normal():
    """Start typing in normal mode (85 WPM)"""
    global DEFAULT_BASE_WPM
    DEFAULT_BASE_WPM = 85
    print(f"\n[INFO] ⚡ NORMAL MODE activated: {DEFAULT_BASE_WPM} WPM")
    start_typing()

def start_typing_fast():
    """Start typing in fast mode (120 WPM)"""
    global DEFAULT_BASE_WPM
    DEFAULT_BASE_WPM = 120
    print(f"\n[INFO] 🚀 FAST MODE activated: {DEFAULT_BASE_WPM} WPM")
    start_typing()

def start_typing_custom_100():
    """Start typing at 100 WPM"""
    print(f"\n[INFO] 🎯 CUSTOM 100 WPM MODE activated")
    start_typing(100)

def start_typing_custom_150():
    """Start typing at 150 WPM"""
    print(f"\n[INFO] 🎯 CUSTOM 150 WPM MODE activated")
    start_typing(150)

def setup_hotkeys():
    """Setup enhanced hotkeys for typing control with individual mode hotkeys"""
    try:
        import keyboard
        
        print("[INFO] 🔐 Testing accessibility permissions...")
        
        if not test_accessibility_permissions():
            print("[ERROR] ❌ Accessibility permissions required!")
            print("[INFO] 🔧 To enable hotkeys:")
            print("   1. System Preferences > Security & Privacy > Privacy > Accessibility")
            print("   2. Add Terminal (or Python) to the allowed apps")
            print("   3. Restart this program")
            return False
        
        # Enhanced hotkey layout with individual mode controls
        hotkeys = [
            # Basic controls
            ('f9', 'F9 - Resume/General Start', resume_or_start),
            ('f8', 'F8 - Pause', pause_typing),
            ('f10', 'F10 - Stop', stop_typing),
            
            # Speed mode hotkeys
            ('f1', 'F1 - Slow Mode (50 WPM)', start_typing_slow),
            ('f2', 'F2 - Normal Mode (85 WPM)', start_typing_normal),
            ('f3', 'F3 - Fast Mode (120 WPM)', start_typing_fast),
            ('f4', 'F4 - Custom 100 WPM', start_typing_custom_100),
            ('f5', 'F5 - Custom 150 WPM', start_typing_custom_150),
        ]
        
        successful_count = 0
        
        print("[INFO] 🎹 Registering enhanced hotkeys...")
        for hotkey, description, callback in hotkeys:
            try:
                keyboard.add_hotkey(hotkey, callback)
                print(f"[INFO] ✅ {description}")
                successful_count += 1
            except Exception as e:
                print(f"[WARNING] ❌ Failed to register {description}: {str(e)[:50]}...")
        
        if successful_count > 0:
            print(f"\n[SUCCESS] 🎉 {successful_count}/{len(hotkeys)} hotkeys registered!")
            print("[INFO] 🎮 ENHANCED HOTKEY CONTROLS:")
            print("\n   📊 SPEED MODES:")
            print("   • F1 - 🐌 Slow Mode (50 WPM)")
            print("   • F2 - ⚡ Normal Mode (85 WPM)")
            print("   • F3 - 🚀 Fast Mode (120 WPM)")
            print("   • F4 - 🎯 Custom 100 WPM")
            print("   • F5 - 🎯 Custom 150 WPM")
            print("\n   🎮 PLAYBACK CONTROLS:")
            print("   • F8 - ⏸️  Pause typing")
            print("   • F9 - ▶️  Resume/General start")
            print("   • F10 - ⏹️  Stop typing")
            print("\n[INFO] 🚀 Press F1-F5 to start typing in different speed modes!")
            print("[INFO] 🛑 Press Ctrl+C to exit")
            
            try:
                keyboard.wait()  # Keep listening for hotkeys
            except KeyboardInterrupt:
                print("\n[INFO] 👋 Exiting AutoTyper...")
                return True
            
        else:
            print("[ERROR] ❌ No hotkeys could be registered.")
            return False
        
    except ImportError:
        print("[ERROR] 📦 Keyboard library not available.")
        print("[INFO] 💻 Install with: pip install keyboard")
        return False
    except Exception as e:
        print(f"[ERROR] ⚠️  Hotkey setup failed: {e}")
        return False

def try_alternative_hotkeys():
    """Try alternative hotkey combinations with individual modes"""
    try:
        import keyboard
        
        print("[INFO] 🔄 Trying alternative hotkey combinations...")
        
        # Alternative combinations for better macOS compatibility
        alternative_hotkeys = [
            # Basic controls
            ('ctrl+shift+9', 'Ctrl+Shift+9 - Resume/Start', resume_or_start),
            ('ctrl+shift+8', 'Ctrl+Shift+8 - Pause', pause_typing),
            ('ctrl+shift+0', 'Ctrl+Shift+0 - Stop', stop_typing),
            
            # Speed mode alternatives
            ('ctrl+shift+1', 'Ctrl+Shift+1 - Slow Mode (50 WPM)', start_typing_slow),
            ('ctrl+shift+2', 'Ctrl+Shift+2 - Normal Mode (85 WPM)', start_typing_normal),
            ('ctrl+shift+3', 'Ctrl+Shift+3 - Fast Mode (120 WPM)', start_typing_fast),
            ('ctrl+shift+4', 'Ctrl+Shift+4 - Custom 100 WPM', start_typing_custom_100),
            ('ctrl+shift+5', 'Ctrl+Shift+5 - Custom 150 WPM', start_typing_custom_150),
        ]
        
        successful_count = 0
        
        for hotkey, description, callback in alternative_hotkeys:
            try:
                keyboard.add_hotkey(hotkey, callback)
                print(f"[INFO] ✅ {description}")
                successful_count += 1
            except Exception as e:
                print(f"[WARNING] ❌ Failed to register {description}: {str(e)[:50]}...")
        
        if successful_count > 0:
            print(f"\n[SUCCESS] 🎉 {successful_count}/{len(alternative_hotkeys)} alternative hotkeys registered!")
            print("[INFO] 🎮 ALTERNATIVE HOTKEY CONTROLS:")
            print("\n   📊 SPEED MODES:")
            print("   • Ctrl+Shift+1 - 🐌 Slow Mode (50 WPM)")
            print("   • Ctrl+Shift+2 - ⚡ Normal Mode (85 WPM)")
            print("   • Ctrl+Shift+3 - 🚀 Fast Mode (120 WPM)")
            print("   • Ctrl+Shift+4 - 🎯 Custom 100 WPM")
            print("   • Ctrl+Shift+5 - 🎯 Custom 150 WPM")
            print("\n   🎮 PLAYBACK CONTROLS:")
            print("   • Ctrl+Shift+8 - ⏸️  Pause typing")
            print("   • Ctrl+Shift+9 - ▶️  Resume/General start")
            print("   • Ctrl+Shift+0 - ⏹️  Stop typing")
            print("\n[INFO] 🚀 Press Ctrl+Shift+1-5 to start typing in different speeds!")
            print("[INFO] 🛑 Press Ctrl+C to exit")
            
            try:
                keyboard.wait()  # Keep listening for hotkeys
            except KeyboardInterrupt:
                print("\n[INFO] 👋 Exiting AutoTyper...")
                return True
            
            return True
        else:
            return False
        
    except Exception as e:
        print(f"[ERROR] ⚠️  Alternative hotkey setup failed: {e}")
        return False

def show_status():
    """Show current typing status and clipboard info"""
    state_names = {
        TYPING_STOPPED: "🔴 STOPPED",
        TYPING_ACTIVE: "🟢 ACTIVE", 
        TYPING_PAUSED: "🟡 PAUSED"
    }
    
    print(f"\n📊 STATUS: {state_names.get(typing_state, 'UNKNOWN')}")
    print(f"⚡ Current WPM Setting: {DEFAULT_BASE_WPM} (±{int(DEFAULT_BASE_WPM * WPM_VARIATION)})")
    
    try:
        clip = pyperclip.paste()
        if clip and clip.strip():
            char_count = len(clip)
            word_count = len(clip.split())
            line_count = clip.count('\n') + 1
            estimated_time = (word_count / DEFAULT_BASE_WPM) * 60
            
            print(f"📋 Clipboard: {char_count} chars, {word_count} words, {line_count} lines")
            print(f"⏱️  Estimated typing time: {estimated_time:.1f} seconds")
            
            preview = clip.replace('\n', '↵').replace('\t', '→').replace('\r', '')
            print(f"👀 Preview: {preview[:80]}{'...' if len(preview) > 80 else ''}")
        else:
            print("📋 Clipboard: Empty")
    except Exception:
        print("📋 Clipboard: Unreadable")

def manual_mode():
    """Enhanced manual mode with WPM options and hotkey info"""
    global typing_state, DEFAULT_BASE_WPM
    
    print("\n" + "="*60)
    print("           📝 MANUAL MODE - macOS Compatible")
    print("="*60)
    print("\n💡 HOW TO USE:")
    print("   1. 📋 Copy text to clipboard (Cmd+C)")
    print("   2. ⏎  Press Enter to start typing")
    print("   3. 🎯 Click where you want text typed (3 second countdown)")
    print("   4. ⌨️  Watch as text types naturally!")
    print(f"\n⚡ WPM PRESETS & SHORTCUTS:")
    print("   • 1 = Slow (50 WPM) - 🐌 Careful typing")
    print("   • 2 = Normal (85 WPM) - ⚡ Average speed")
    print("   • 3 = Fast (120 WPM) - 🚀 Quick typing")
    print("   • 4 = Custom 100 WPM - 🎯 Precise speed")
    print("   • 5 = Custom 150 WPM - 🎯 Very fast")
    print("   • [number] = Custom WPM (e.g., '175')")
    print("   • Enter = Use current default")
    print(f"\n💡 TIP: If hotkeys worked, you could use F1-F5 or Ctrl+Shift+1-5!")
    
    while True:
        try:
            show_status()
            
            command = input("\n>>> [1/2/3/4/5/Enter/WPM]=Start | 'q'=Quit: ").strip().lower()
            
            if command in ['q', 'quit', 'exit']:
                break
            elif command == '1':
                start_typing_slow()
            elif command == '2' or command == '':
                start_typing_normal()
            elif command == '3':
                start_typing_fast()
            elif command == '4':
                start_typing_custom_100()
            elif command == '5':
                start_typing_custom_150()
            elif command.isdigit():
                custom_wpm = int(command)
                if 10 <= custom_wpm <= 250:
                    print(f"[INFO] ⚡ Custom WPM: {custom_wpm}")
                    start_typing(custom_wpm)
                else:
                    print("[ERROR] ❌ WPM must be between 10-250")
            else:
                print("[ERROR] ❌ Invalid command. Use '1', '2', '3', '4', '5', a number, or Enter")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    print("\n👋 Thanks for using AutoTyper!")

def main():
    """Main function - optimized for macOS compatibility"""
    print("="*70)
    print("           🤖 AutoTyper v3.4 - Individual Mode Hotkeys Edition")
    print("="*70)
    print("[INFO] 🚀 Hotkey-controlled clipboard auto-typer")
    print("[INFO] 📋 Types ONLY clipboard content with human-like behavior")
    print("[INFO] ⚡ Features individual hotkeys for each speed mode")
    print("[INFO] 🍎 Optimized for macOS compatibility")
    
    # Show initial status
    show_status()
    
    # Try to setup hotkeys with multiple fallback options
    print("\n[INFO] 🎹 Setting up enhanced hotkey controls...")
    
    if setup_hotkeys():
        print("[INFO] ✅ AutoTyper session completed.")
    elif try_alternative_hotkeys():
        print("[INFO] ✅ AutoTyper session completed with alternative hotkeys.")
    else:
        print("\n[INFO] 📝 Hotkey setup failed. Starting Manual Mode...")
        print("[INFO] 🍎 Manual mode works without accessibility permissions!")
        manual_mode()
    
    # Cleanup
    global typing_state
    typing_state = TYPING_STOPPED
    print("\n👋 Thanks for using AutoTyper!")
    print("🍎 macOS Tip: Grant accessibility permissions for hotkey mode")

if __name__ == "__main__":
    main()
