import json

SCREEN_WIDTH = 1200 #px
SCREEN_HEIGHT = 800 #px

FPS = 60

GAME_TITLE = "DEEP IN THE RED"



# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (70, 130, 255)
DARK_BLUE = (50, 100, 200)



def load_settings():
    """Load persisted user settings from disk. Returns the deserialized configuration as a dictionary.

    Returns:
        dict: A mapping of user setting keys to their stored values loaded from 'user_settings.json'.
    """
    with open("user_settings.json", "r") as f:
        return json.load(f)

def save_setting(key, value):
    """Update a single user setting and persist it to disk. This function modifies the stored configuration without affecting other settings.

    Args:
        key: The setting name to update.
        value: The new value to store for the given setting key.
    """
    with open("user_settings.json", "r") as f:
        settings = json.load(f)
    settings[key] = value
    with open("user_settings.json", "w") as f:
        json.dump(settings, f, indent=4)








