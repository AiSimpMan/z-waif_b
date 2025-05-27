# utils/tts_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class TTSInterface(ABC):
    """
    Abstract Base Class for Text-to-Speech engine implementations.
    """

    @abstractmethod
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the TTS engine with optional configuration.
        'config' might contain engine-specific settings like paths, API keys, etc.
        For local engines, it might contain paths to models or default voice parameters.
        """
        pass

    @abstractmethod
    def speak(self, text: str, voice_config_id: str = None, **kwargs) -> None:
        """
        Synthesize and play the given text.
        
        Args:
            text (str): The text to be spoken.
            voice_config_id (str, optional): An identifier for a pre-defined voice 
                                             configuration (e.g., "voice_profile_1"). 
                                             The engine would look up actual parameters 
                                             based on this ID from its main config.
            **kwargs: Additional engine-specific parameters that might override or
                      supplement the voice_config_id profile.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop any currently ongoing speech.
        """
        pass

    @abstractmethod
    def is_speaking(self) -> bool:
        """
        Check if the TTS engine is currently synthesizing or playing speech.
        
        Returns:
            bool: True if speaking, False otherwise.
        """
        pass

    @abstractmethod
    def get_voice_config_defaults(self) -> Dict[str, Any]:
        """
        Returns a dictionary of default voice parameters for this engine.
        Example: {'language': 'en', 'speaker_id': 'default', 'speed': 1.0}
        """
        pass

    # Optional: Method to list available pre-defined voice configurations or speakers
    # @abstractmethod
    # def list_voice_profiles(self) -> List[str]:
    #     """
    #     Returns a list of available voice profile identifiers.
    #     """
    #     return []
