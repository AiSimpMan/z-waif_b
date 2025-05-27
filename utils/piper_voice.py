# utils/piper_voice.py
import os
import subprocess
import time
import wave # For reading WAV properties if needed

# Project-specific imports
import utils.hotkeys
import utils.voice_splitter
import utils.soundboard
import utils.settings # To get PIPER_VOICE_MODEL etc.
import utils.audio # For play_wav
import API.api_controller # For speak_only_spokento logic
# import utils.zw_logging # Placeholder for logging

# --- Global State for this module ---
is_speaking_flag: bool = False
cut_voice_signal: bool = False
current_piper_process = None # To store the Popen object
current_playback_process = None # Placeholder if we make playback a subprocess

# --- Constants ---
TEMP_WAV_FILENAME = "temp_piper_output.wav"
# Ensure this path is writable, e.g., in a 'temp' folder or utils/resource
# Using os.path.join for platform compatibility
RESOURCE_DIR = os.path.join(os.path.dirname(__file__), "resource")
TEMP_WAV_FILEPATH = os.path.join(RESOURCE_DIR, TEMP_WAV_FILENAME)

# --- Core Functions ---
def speak_line(s_message: str, refuse_pause: bool):
    global is_speaking_flag, cut_voice_signal, current_piper_process, current_playback_process
    
    # print(f"DEBUG: speak_line called with: {s_message[:30]}...") # Temporary debug

    if is_speaking_flag:
        # print("DEBUG: TTS: Already speaking, request ignored.")
        return

    set_speaking_state(True)
    cut_voice_signal = False
    
    if not os.path.exists(RESOURCE_DIR):
        try:
            os.makedirs(RESOURCE_DIR, exist_ok=True)
            # print(f"DEBUG: Created directory: {RESOURCE_DIR}")
        except Exception as e:
            # print(f"Error creating resource directory {RESOURCE_DIR}: {e}")
            set_speaking_state(False)
            return


    chunky_message = utils.voice_splitter.split_into_sentences(s_message)
    # print(f"DEBUG: Split into {len(chunky_message)} chunks.")

    for i, chunk in enumerate(chunky_message):
        # print(f"DEBUG: Processing chunk {i+1}/{len(chunky_message)}: {chunk[:30]}...")
        if cut_voice_signal or utils.hotkeys.NEXT_PRESSED or utils.hotkeys.REDO_PRESSED:
            # print("DEBUG: Cut signal or hotkey pressed, breaking chunk loop.")
            break 

        try:
            pure_chunk = utils.soundboard.extract_soundboard(chunk)
            # print(f"DEBUG: After soundboard: {pure_chunk[:30]}...")

            if utils.settings.speak_only_spokento and                not API.api_controller.last_message_received_has_own_name:
                # print("DEBUG: Condition speak_only_spokento not met, skipping chunk.")
                continue

            pure_chunk = pure_chunk.replace("*", "")
            for exclam in ["!!!!!", "!!!!", "!!!", "!!"]:
                pure_chunk = pure_chunk.replace(exclam, "!")
            
            if not pure_chunk.strip():
                # print("DEBUG: Chunk empty after processing, skipping.")
                continue

            # print(f"DEBUG: Final pure_chunk to speak: {pure_chunk[:30]}...")
            
            # --- Piper Execution ---
            voice_model = getattr(utils.settings, 'PIPER_VOICE_MODEL', 'en_US-lessac-medium')
            data_dir = getattr(utils.settings, 'PIPER_DATA_DIR', None)

            command = ['piper', '--model', voice_model, '--output_file', TEMP_WAV_FILEPATH]
            if data_dir:
                command.extend(['--data-dir', data_dir])
            
            # print(f"DEBUG: TTS: Running Piper: {' '.join(command)}")
            
            # Ensure no previous temp file lingers if Piper fails to overwrite
            if os.path.exists(TEMP_WAV_FILEPATH):
                try:
                    os.remove(TEMP_WAV_FILEPATH)
                except OSError: # nosemgrep: general-exception-loss
                    pass # nosemgrep: general-exception-loss

            current_piper_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                # Encode pure_chunk to bytes for stdin
                stdout_data, stderr_data = current_piper_process.communicate(input=pure_chunk.encode('utf-8'), timeout=30) # Increased timeout
                if current_piper_process.returncode != 0:
                    # print(f"DEBUG: TTS: Piper error (retcode {current_piper_process.returncode}): {stderr_data.decode('utf-8', errors='ignore')}")
                    current_piper_process = None # Reset process
                    continue 
            except subprocess.TimeoutExpired:
                # print("DEBUG: TTS: Piper process timed out.")
                current_piper_process.kill()
                current_piper_process.wait() # Ensure it's cleaned up
                current_piper_process = None # Reset process
                continue
            finally:
                if current_piper_process and current_piper_process.poll() is None: # Should be caught by timeout or communicate finish
                    current_piper_process.kill()
                    current_piper_process.wait()
                current_piper_process = None


            if cut_voice_signal: 
                # print("DEBUG: Cut signal after Piper run, breaking.")
                break 

            # --- Playback ---
            if os.path.exists(TEMP_WAV_FILEPATH) and os.path.getsize(TEMP_WAV_FILEPATH) > 0:
                # print(f"DEBUG: TTS: Playing {TEMP_WAV_FILEPATH}")
                # This is blocking. For true interruption during playback, utils.audio.play_wav would need modification.
                utils.audio.play_wav(TEMP_WAV_FILEPATH) 
                try:
                    os.remove(TEMP_WAV_FILEPATH)
                    # print(f"DEBUG: Removed temp WAV: {TEMP_WAV_FILEPATH}")
                except OSError as e:
                    # print(f"DEBUG: TTS: Error deleting temp WAV: {e}")
                    pass
            else:
                # print(f"DEBUG: TTS: Temp WAV file not found or empty after Piper run: {TEMP_WAV_FILEPATH}")
                pass
            
            if not refuse_pause:
                time.sleep(0.05)
            else:
                time.sleep(0.001)

        except Exception as e:
            # print(f"DEBUG: TTS: Error in speak_line chunk processing: {e}")
            # Consider logging this with utils.zw_logging if available
            pass # Continue to next chunk or cleanup
        
        if cut_voice_signal: 
            # print("DEBUG: Cut signal at end of chunk try-except, breaking.")
            break 
            
    # Cleanup and final state
    if current_piper_process and current_piper_process.poll() is None: 
        # print("DEBUG: Cleaning up lingering Piper process post-loop.")
        current_piper_process.kill()
        current_piper_process.wait()
        current_piper_process = None
        
    if os.path.exists(TEMP_WAV_FILEPATH): 
        try:
            # print(f"DEBUG: Cleaning up temp WAV post-loop: {TEMP_WAV_FILEPATH}")
            os.remove(TEMP_WAV_FILEPATH)
        except OSError: # nosemgrep: general-exception-loss
            pass # nosemgrep: general-exception-loss

    utils.hotkeys.cooldown_listener_timer() 
    set_speaking_state(False)
    cut_voice_signal = False 
    # print("DEBUG: speak_line finished.")

def check_if_speaking() -> bool:
    global is_speaking_flag
    return is_speaking_flag

def set_speaking_state(is_now_speaking: bool):
    global is_speaking_flag
    # print(f"DEBUG: set_speaking_state to {is_now_speaking}")
    is_speaking_flag = is_now_speaking

def force_cut_voice_globally():
    global cut_voice_signal, current_piper_process, current_playback_process
    # print("DEBUG: TTS: Force cut voice signal received.")
    cut_voice_signal = True
    if current_piper_process and current_piper_process.poll() is None:
        # print("DEBUG: Terminating active Piper process.")
        try:
            current_piper_process.terminate() 
            current_piper_process.wait(timeout=1.0) 
        except subprocess.TimeoutExpired:
            # print("DEBUG: Piper process did not terminate gracefully, killing.")
            current_piper_process.kill()
            current_piper_process.wait()
        except Exception as e:
            # print(f"DEBUG: Exception while terminating Piper: {e}")
            pass # nosemgrep: general-exception-loss
        current_piper_process = None
    
    # If utils.audio.play_wav were made interruptible (e.g., by running in a separate process
    # or by checking a flag internally), this is where you'd signal it or kill its process.
    # For now, if play_wav is blocking, this cut will only prevent subsequent chunks
    # or stop Piper from generating the current one if it hasn't finished.
    # print("DEBUG: force_cut_voice_globally actions complete.")
