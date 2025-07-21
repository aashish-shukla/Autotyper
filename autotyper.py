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

def human_type(text):
    """Type text character by character with human-like behavior"""
    global typing_state
    
    if not text:
        print("[WARNING] No text to type!")
        return
    
    print(f"[INFO] 🚀 Starting to type {len(text)} characters...")
    print(f"[INFO] 🎮 Controls: F8=Pause | F9=Resume/Start | F10=Stop")
    
    for i, char in enumerate(text):
        # Check for pause
        while typing_state == TYPING_PAUSED:
            time.sleep(0.1)  # Wait while paused
            
        # Check for stop
        if typing_state == TYPING_STOPPED:
            print(f"\n[INFO] 🛑 Typing stopped at character {i+1}/{len(text)}")
            break
        
        # Handle special characters properly
        if char == '\n':
            pyautogui.press('enter')
        elif char == '\t':
            pyautogui.press('tab')
        elif char == '\r':
            continue  # Skip carriage returns
        else:
            pyautogui.write(char)
        
        # Human-like typing speed with variation
        if char in '.!?':
            time.sleep(random.uniform(0.2, 0.5))  # Sentence endings
        elif char in ',;:':
            time.sleep(random.uniform(0.1, 0.3))  # Punctuation
        elif char == ' ':
            time.sleep(random.uniform(0.05, 0.15))  # Spaces
        else:
            time.sleep(random.uniform(0.03, 0.12))  # Normal chars
        
        # Occasional thinking pauses
        if random.random() < 0.05:  # 5% chance
            time.sleep(random.uniform(0.3, 0.8))
    
    # Auto-stop after completion
    if typing_state == TYPING_ACTIVE:
        print(f"\n[SUCCESS] ✅ Finished typing all {len(text)} characters!")
    
    typing_state = TYPING_STOPPED

def start_typing():
    """Start typing clipboard content"""
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
    typing_thread = threading.Thread(target=human_type, args=(text,), daemon=True)
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

def setup_hotkeys():
    """Setup the three hotkeys for typing control using function keys"""
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
        
        # Use function keys that work reliably on macOS
        hotkeys = [
            ('f9', 'F9 - Start/Resume', resume_or_start),
            ('f8', 'F8 - Pause', pause_typing),
            ('f10', 'F10 - Stop', stop_typing)
        ]
        
        successful_count = 0
        
        print("[INFO] 🎹 Registering hotkeys...")
        for hotkey, description, callback in hotkeys:
            try:
                keyboard.add_hotkey(hotkey, callback)
                print(f"[INFO] ✅ {description}")
                successful_count += 1
            except Exception as e:
                print(f"[WARNING] ❌ Failed to register {description}: {str(e)[:50]}...")
        
        if successful_count > 0:
            print(f"\n[SUCCESS] 🎉 {successful_count}/3 hotkeys registered!")
            print("[INFO] 🎮 HOTKEY CONTROLS:")
            print("   • F9  - Start typing / Resume if paused")
            print("   • F8  - Pause typing")
            print("   • F10 - Stop typing completely")
            print("\n[INFO] ▶️  Press F9 to start typing clipboard content!")
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
    """Try alternative hotkey combinations if function keys fail"""
    try:
        import keyboard
        
        print("[INFO] 🔄 Trying alternative hotkey combinations...")
        
        # Try different combinations that work better on macOS
        alternative_hotkeys = [
            # Try with explicit key codes
            ('ctrl+shift+1', 'Ctrl+Shift+1 - Start/Resume', resume_or_start),
            ('ctrl+shift+2', 'Ctrl+Shift+2 - Pause', pause_typing),
            ('ctrl+shift+3', 'Ctrl+Shift+3 - Stop', stop_typing),
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
            print(f"\n[SUCCESS] 🎉 {successful_count}/3 alternative hotkeys registered!")
            print("[INFO] 🎮 ALTERNATIVE HOTKEY CONTROLS:")
            print("   • Ctrl+Shift+1 - Start typing / Resume if paused")
            print("   • Ctrl+Shift+2 - Pause typing")
            print("   • Ctrl+Shift+3 - Stop typing completely")
            print("\n[INFO] ▶️  Press Ctrl+Shift+1 to start typing clipboard content!")
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
    
    try:
        clip = pyperclip.paste()
        if clip and clip.strip():
            char_count = len(clip)
            word_count = len(clip.split())
            line_count = clip.count('\n') + 1
            print(f"📋 Clipboard: {char_count} chars, {word_count} words, {line_count} lines")
            
            preview = clip.replace('\n', '↵').replace('\t', '→').replace('\r', '')
            print(f"👀 Preview: {preview[:80]}{'...' if len(preview) > 80 else ''}")
        else:
            print("📋 Clipboard: Empty")
    except Exception:
        print("📋 Clipboard: Unreadable")

def manual_mode():
    """Simple manual mode for when hotkeys fail"""
    global typing_state
    
    print("\n" + "="*60)
    print("           📝 MANUAL MODE - macOS Compatible")
    print("="*60)
    print("\n💡 HOW TO USE:")
    print("   1. 📋 Copy text to clipboard (Cmd+C)")
    print("   2. ⏎  Press Enter below to start typing")
    print("   3. 🎯 Click where you want text typed (3 second countdown)")
    print("   4. ⌨️  Watch as text types naturally!")
    
    while True:
        try:
            show_status()
            
            command = input("\n>>> [Enter]=Start Typing | 'q'=Quit: ").strip().lower()
            
            if command in ['q', 'quit', 'exit']:
                break
            else:
                # Start typing
                start_typing()
                
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
    print("           🤖 AutoTyper v3.1 - macOS Compatible Edition")
    print("="*70)
    print("[INFO] 🚀 Hotkey-controlled clipboard auto-typer")
    print("[INFO] 📋 Types ONLY clipboard content with human-like behavior")
    print("[INFO] 🍎 Optimized for macOS compatibility")
    
    # Show initial status
    show_status()
    
    # Try to setup hotkeys with multiple fallback options
    print("\n[INFO] 🎹 Setting up hotkey controls...")
    
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
