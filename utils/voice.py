import os

# Import from the new Piper TTS implementation
# These functions will be created in the next step in 'utils/piper_voice.py'
from .piper_voice import (
    speak_line as piper_speak_line,
    check_if_speaking as piper_check_if_speaking,
    set_speaking_state as piper_set_speaking_state,
    force_cut_voice_globally as piper_force_cut_voice_globally
)

# These functions will be the public API for other modules in the project.
# They act as wrappers or direct calls to the piper_voice implementation.

def speak_line(s_message: str, refuse_pause: bool):
    """
    Main function to speak a line using the Piper TTS engine.
    Delegates to piper_voice.speak_line.
    """
    # Placeholder for actual call, assuming piper_speak_line will handle all logic
    # including setting its internal speaking state.
    return piper_speak_line(s_message, refuse_pause)

def check_if_speaking() -> bool:
    """
    Checks if Piper TTS is currently speaking.
    Delegates to piper_voice.check_if_speaking.
    """
    return piper_check_if_speaking()

def set_speaking(is_now_speaking: bool):
    """
    Sets the speaking state for Piper TTS.
    Delegates to piper_voice.set_speaking_state.
    This function might be used by other parts of the application if they need
    to manually influence the speaking state, though typically piper_voice
    will manage this internally during its speak_line operation.
    """
    piper_set_speaking_state(is_now_speaking)

def force_cut_voice():
    """
    Forces Piper TTS to stop speaking and cut any ongoing/pending speech.
    Delegates to piper_voice.force_cut_voice_globally.
    """
    piper_force_cut_voice_globally()
