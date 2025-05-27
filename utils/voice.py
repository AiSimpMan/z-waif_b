# utils/voice.py

import importlib
import utils.settings # To get ACTIVE_TTS_ENGINE and engine-specific configs
from utils.tts_interface import TTSInterface

# --- Global variable for the loaded TTS engine instance ---
_active_tts_engine: TTSInterface = None

def _load_tts_engine():
    global _active_tts_engine
    if _active_tts_engine is not None:
        return _active_tts_engine

    engine_name = getattr(utils.settings, 'ACTIVE_TTS_ENGINE', 'espeak').lower() # Default to espeak
    tts_config = getattr(utils.settings, 'TTS_ENGINE_CONFIG', {}).get(engine_name, {})

    try:
        # print(f"TTS Manager: Attempting to load engine: {engine_name}") # Debug
        module_path = f"utils.{engine_name}_tts" # e.g., utils.espeak_tts
        engine_module = importlib.import_module(module_path)
        
        # Convention: Engine class is named 'Engine' within its module (e.g., espeak_tts.Engine)
        engine_class = getattr(engine_module, 'Engine') 
        _active_tts_engine = engine_class(tts_config)
        # print(f"TTS Manager: Successfully loaded {engine_name} engine.") # Debug
    except ImportError as e:
        print(f"TTS Manager: Error importing engine module {module_path}: {e}")
        _active_tts_engine = None
    except AttributeError as e:
        print(f"TTS Manager: Error getting 'Engine' class from {module_path}: {e}")
        _active_tts_engine = None
    except Exception as e:
        print(f"TTS Manager: Generic error loading TTS engine {engine_name}: {e}")
        _active_tts_engine = None

    return _active_tts_engine

def speak_line(s_message: str, refuse_pause: bool = False, voice_config_id: str = None, **kwargs):
    """
    Main function to speak a line using the active TTS engine.
    
    Args:
        s_message (str): The text to be spoken.
        refuse_pause (bool): Hint for the engine regarding inter-phrase pausing.
                             (Actual handling depends on engine implementation)
        voice_config_id (str, optional): Identifier for a specific voice profile.
        **kwargs: Additional engine-specific parameters.
    """
    engine = _load_tts_engine()
    if engine:
        # The `refuse_pause` concept might need to be an internal detail of the engine
        # or passed via kwargs if the engine supports such fine-grained control.
        # For now, we pass it via kwargs.
        kwargs['refuse_pause'] = refuse_pause
        engine.speak(s_message, voice_config_id=voice_config_id, **kwargs)
    else:
        print("TTS Manager: No active TTS engine loaded. Cannot speak.")

def check_if_speaking() -> bool:
    """
    Checks if the active TTS engine is currently speaking.
    """
    engine = _load_tts_engine()
    if engine:
        return engine.is_speaking()
    return False

def force_cut_voice():
    """
    Forces the active TTS engine to stop speaking.
    """
    engine = _load_tts_engine()
    if engine:
        engine.stop()
    else:
        print("TTS Manager: No active TTS engine loaded. Nothing to stop.")

# Ensure engine is loaded at startup (optional, alternatively lazy load on first call)
# _load_tts_engine()

# Example of how settings might be structured in utils/settings.py:
# ACTIVE_TTS_ENGINE = "espeak"  # or "coqui", "piper" etc.
# TTS_ENGINE_CONFIG = {
#     "espeak": {
#         "default_voice_params": { 
#             "variant": "en-us+f3", "pitch": 70, "speed": 160 
#         },
#         "voice_profiles": {
#             "z_waif_a": {"variant": "en-us+f3", "pitch": 70, "speed": 160},
#             "z_waif_b": {"variant": "en-us+m3", "pitch": 40, "speed": 150} 
#         }
#     },
#     "coqui": {
#         "model_name": "tts_models/en/ljspeech/tacotron2-DDC",
#         "speaker_wav": "path/to/speaker.wav" # for voice cloning
#     }
# }
