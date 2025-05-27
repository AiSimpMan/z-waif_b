char_name = ""

hotkeys_locked = False
speak_shadowchats = False
speak_only_spokento = False

max_tokens = 300
stream_chats = True
newline_cut = False
asterisk_ban = False
supress_rp = False
stopping_strings = ["[System", "
User:", "---", "<|", "###"]

semi_auto_chat = False
hangout_mode = False

autochat_mininum_chat_frames = 149
use_silero_vad = True

alarm_time = "09:09"
model_preset = "Default"

cam_use_image_feed = False
cam_direct_talk = True
cam_image_preview = True
cam_use_screenshot = False
# cam_reply_after = False

# Valid values; "Faces", "Random", "None"
eyes_follow = "None"

# Tags and tasks
all_tag_list = []
cur_tags = []
all_task_char_list = []
cur_task_char = "None"

# Gaming
is_gaming_loop = False

minecraft_enabled = False
gaming_enabled = True
alarm_enabled = True
vtube_enabled = True
discord_enabled = True
rag_enabled = True
vision_enabled = True

# Piper TTS Settings (These will be effectively replaced/ignored by the new structure if ACTIVE_TTS_ENGINE is not 'piper')
PIPER_VOICE_MODEL = "en_US-lessac-medium"
PIPER_DATA_DIR = None

# TTS Engine Settings
ACTIVE_TTS_ENGINE = "espeak"  # Can be "espeak", or other future engines

TTS_ENGINE_CONFIG = {
    "espeak": {
        "default_voice_params": { 
            "variant": "en-us+f3",  # Example: English US female voice variant 3
            "pitch": 70,            # Pitch adjustment (0-99)
            "speed": 160,           # Speed in words-per-minute (approx 80-450)
            "word_gap": 0           # Pause between words in units of 10ms (e.g., 5 = 50ms)
        },
        "voice_profiles": {
            # These are examples; actual use would depend on how the application
            # decides which profile to use (e.g., for different characters).
            "profile1_female": {"variant": "en-us+f4", "pitch": 75, "speed": 150, "word_gap": 0},
            "profile2_male": {"variant": "en-us+m3", "pitch": 40, "speed": 160, "word_gap": 0},
        }
    },
    # "coqui": { # Example for a future Coqui TTS integration
    #     "model_name": "tts_models/en/ljspeech/tacotron2-DDC",
    #     "speaker_wav": None, # Path to speaker wav for voice cloning
    #     "language": "en"
    # },
    # "piper": { # Example for a future Piper TTS integration
    #     "model": "en_US-lessac-medium", # Voice model name
    #     "data_dir": None # Optional path to piper models directory
    # }
}

# Specific Espeak-NG settings (can be overridden by profiles or direct call)
# These are somewhat redundant if using default_voice_params from TTS_ENGINE_CONFIG,
# but kept for now if direct access was planned. Best practice would be to solely
# rely on the TTS_ENGINE_CONFIG structure for engine-specific params.
# For now, the espeak_tts.py Engine will primarily use TTS_ENGINE_CONFIG.
# These individual settings below might be deprecated or removed later.
ESPEAK_VOICE_VARIANT = "en-us+f3" 
ESPEAK_PITCH = 70            
ESPEAK_SPEED = 160           
ESPEAK_WORD_GAP = 0
