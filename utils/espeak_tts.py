# utils/espeak_tts.py
import os
import subprocess
import time
import shutil # For shutil.which to check for espeak-ng command

from utils.tts_interface import TTSInterface
from typing import Dict, Any

# Project-specific imports (mirrors piper_voice.py for now)
import utils.hotkeys
import utils.voice_splitter
import utils.soundboard
import utils.settings # To get default espeak params
import utils.audio # For play_wav
import API.api_controller # For speak_only_spokento logic

# --- Constants ---
TEMP_WAV_FILENAME = "espeak_temp_output.wav"
RESOURCE_DIR = os.path.join(os.path.dirname(__file__), "resource")
TEMP_WAV_FILEPATH = os.path.join(RESOURCE_DIR, TEMP_WAV_FILENAME)

class Engine(TTSInterface):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.config = config if config else {}
        self.is_speaking_flag: bool = False
        self.cut_voice_signal: bool = False
        self.current_process = None
        self.espeak_command = shutil.which("espeak-ng")

        if not self.espeak_command:
            print("ESPEAK_TTS: WARNING - espeak-ng command not found in PATH. TTS will not function.")
        
        # Ensure resource directory exists
        if not os.path.exists(RESOURCE_DIR):
            try:
                os.makedirs(RESOURCE_DIR, exist_ok=True)
            except Exception as e:
                print(f"ESPEAK_TTS: Error creating resource directory {RESOURCE_DIR}: {e}")

    def _get_effective_voice_params(self, voice_config_id: str = None, **kwargs) -> Dict[str, Any]:
        params = self.config.get('default_voice_params', {}).copy()
        # print(f"ESPEAK_TTS DEBUG: Initial params: {params}")
        if voice_config_id:
            profile_params = self.config.get('voice_profiles', {}).get(voice_config_id, {})
            # print(f"ESPEAK_TTS DEBUG: Profile '{voice_config_id}' params: {profile_params}")
            params.update(profile_params)
        # print(f"ESPEAK_TTS DEBUG: Params after profile: {params}")
        params.update(kwargs)
        # print(f"ESPEAK_TTS DEBUG: Final effective params: {params}")
        return params

    def speak(self, text: str, voice_config_id: str = None, **kwargs) -> None:
        if not self.espeak_command:
            print("ESPEAK_TTS: espeak-ng command not found. Cannot speak.")
            return

        if self.is_speaking_flag:
            # print("ESPEAK_TTS DEBUG: Already speaking, request ignored.")
            return

        self.is_speaking_flag = True
        self.cut_voice_signal = False
        
        refuse_pause = kwargs.pop('refuse_pause', False) # Get refuse_pause from kwargs

        chunky_message = utils.voice_splitter.split_into_sentences(text)

        for chunk in chunky_message:
            if self.cut_voice_signal or utils.hotkeys.NEXT_PRESSED or utils.hotkeys.REDO_PRESSED:
                break

            try:
                pure_chunk = utils.soundboard.extract_soundboard(chunk)

                if utils.settings.speak_only_spokento and                    not API.api_controller.last_message_received_has_own_name:
                    continue

                pure_chunk = pure_chunk.replace("*", "")
                for exclam in ["!!!!!", "!!!!", "!!!", "!!"]:
                    pure_chunk = pure_chunk.replace(exclam, "!")
                
                if not pure_chunk.strip():
                    continue

                voice_params = self._get_effective_voice_params(voice_config_id, **kwargs)
                
                variant = voice_params.get('variant', 'en-us') # Default to en-us
                pitch = str(voice_params.get('pitch', 50))
                speed = str(voice_params.get('speed', 160))
                word_gap = str(voice_params.get('word_gap', 0)) # espeak default is 0 (no pause)

                command = [
                    self.espeak_command,
                    '-v', variant,
                    '-p', pitch,
                    '-s', speed,
                    '-g', word_gap, # Word gap in units of 10ms
                    '-w', TEMP_WAV_FILEPATH, # Output to WAV file
                    f'"{pure_chunk}"' # Text to speak, quoted
                ]
                # On Windows, Popen might need shell=True if command includes quotes directly,
                # or pass the text via stdin instead of as a direct argument.
                # For simplicity and cross-platform, let's try without shell=True first.
                # If issues arise, using stdin for text is more robust for espeak-ng.
                # Alternative: espeak-ng takes text from stdin if no text argument and not -f
                # For now, direct text argument. If quoting is an issue, will revise to use stdin pipe.
                # Using subprocess.list2cmdline might be safer for complex args or just pass raw text last.
                # Let's try to pass the text as the last argument without quotes in the list first.
                
                final_command = [
                    self.espeak_command,
                    '-v', variant, '-p', pitch, '-s', speed, '-g', word_gap,
                    '-w', TEMP_WAV_FILEPATH,
                    pure_chunk # Pass raw chunk here
                ]

                # print(f"ESPEAK_TTS DEBUG: Running command: {' '.join(final_command)}")

                if os.path.exists(TEMP_WAV_FILEPATH):
                    try:
                        os.remove(TEMP_WAV_FILEPATH)
                    except OSError: # nosemgrep: general-exception-loss
                        pass # nosemgrep: general-exception-loss
                
                self.current_process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    _, stderr_data = self.current_process.communicate(timeout=15)
                    if self.current_process.returncode != 0:
                        # print(f"ESPEAK_TTS: Error (retcode {self.current_process.returncode}): {stderr_data.decode('utf-8', errors='ignore')}")
                        self.current_process = None
                        continue
                except subprocess.TimeoutExpired:
                    # print("ESPEAK_TTS: Process timed out.")
                    self.current_process.kill()
                    self.current_process.wait()
                    self.current_process = None
                    continue
                finally:
                    if self.current_process and self.current_process.poll() is None:
                        self.current_process.kill()
                        self.current_process.wait()
                    self.current_process = None
                
                if self.cut_voice_signal: break

                if os.path.exists(TEMP_WAV_FILEPATH) and os.path.getsize(TEMP_WAV_FILEPATH) > 0:
                    utils.audio.play_wav(TEMP_WAV_FILEPATH)
                    try:
                        os.remove(TEMP_WAV_FILEPATH)
                    except OSError: # nosemgrep: general-exception-loss
                        pass # nosemgrep: general-exception-loss
                else:
                    # print(f"ESPEAK_TTS DEBUG: Temp WAV file not found or empty: {TEMP_WAV_FILEPATH}")
                    pass

                if not refuse_pause: # refuse_pause was popped from kwargs
                    time.sleep(0.05)
                else:
                    time.sleep(0.001)

            except Exception as e:
                # print(f"ESPEAK_TTS: Error in speak_line chunk: {e}")
                pass
            
            if self.cut_voice_signal: break
        
        if self.current_process and self.current_process.poll() is None:
            self.current_process.kill()
            self.current_process.wait()
        self.current_process = None

        if os.path.exists(TEMP_WAV_FILEPATH):
            try:
                os.remove(TEMP_WAV_FILEPATH)
            except OSError: # nosemgrep: general-exception-loss
                pass # nosemgrep: general-exception-loss

        utils.hotkeys.cooldown_listener_timer()
        self.is_speaking_flag = False
        self.cut_voice_signal = False

    def stop(self) -> None:
        # print("ESPEAK_TTS DEBUG: stop() called.")
        self.cut_voice_signal = True
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
                self.current_process.wait()
            except Exception: # nosemgrep: general-exception-loss
                pass # nosemgrep: general-exception-loss
            self.current_process = None
        # Add logic here if utils.audio.play_wav needs to be manually stopped.

    def is_speaking(self) -> bool:
        return self.is_speaking_flag

    def get_voice_config_defaults(self) -> Dict[str, Any]:
        return self.config.get('default_voice_params', {}).copy()
