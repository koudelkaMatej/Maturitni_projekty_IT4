import pygame

WIDTH, HEIGHT = 1200, 800
SNAKE_SIZE = 20

# Barvy
WHITE, BLACK, BLUE = (255, 255, 255), (0, 0, 0), (50, 150, 255)
RED, GREEN, YELLOW = (200, 0, 0), (0, 255, 0), (255, 215, 0)
DARK_GREEN, LIGHT_GRASS = (31, 122, 31), (35, 140, 35)
GRAY, PURPLE, LIGHT_BLUE = (100, 100, 100), (160, 32, 240), (0, 255, 255)

# Skiny
SKINS = {
    "Základní": (0, 200, 0),
    "Modrý": (0, 100, 255),
    "Zlatý": (255, 215, 0),
    "Růžový": (255, 105, 180),
    "Ohnivý": (255, 69, 0)
}
SKIN_PRICES = {"Základní": 0, "Modrý": 20, "Zlatý": 100, "Růžový": 50, "Ohnivý": 150}