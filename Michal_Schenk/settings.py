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
    with open("user_settings.json", "r") as f:
        return json.load(f)

def save_setting(key, value):
    with open("user_settings.json", "r") as f:
        settings = json.load(f)
    settings[key] = value
    with open("user_settings.json", "w") as f:
        json.dump(settings, f, indent=4)








