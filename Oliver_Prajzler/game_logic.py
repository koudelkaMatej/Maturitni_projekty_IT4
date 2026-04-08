import random
import pygame
from config import WIDTH, HEIGHT

def reset_game(mode, skin_color):
    speed = 15 if mode != "easy" else 8
    return {
        "mode": mode, "pos": [[600, 400]], "dir": (0, 0), "score": 0, "dead": False,
        "food": (random.randrange(0, 59)*20, random.randrange(0, 39)*20),
        "powerups": [], "obstacles": [], "last_obs": pygame.time.get_ticks(),
        "base_speed": speed, "speed": speed, "timeout": 0, "skin_color": skin_color
    }