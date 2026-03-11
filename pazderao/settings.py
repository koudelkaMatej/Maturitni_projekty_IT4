import pygame

# Rozměry okna
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

# Cesty k souborům
BG_IMAGE_PATH = "pazderao/images/background.jpg"
FONT_PATH = "pazderao/images/font/lemonmilk.otf"

# Základní nastavení hry
COLS = 6
ROWS = 7
clock = pygame.time.Clock()
FPS = 60
LIVE_BALL = False
GAME_OVER = 0

# Grafika
text_col = (255, 255, 255)
text_col_red = (255, 0, 0)
text_col_green = (0, 255, 0)

# Barvy bloků
BLOCK_YELLOW = (223, 188, 9)
BLOCK_ORANGE = (246, 137, 27)
BLOCK_RED = (250, 85, 35)

# Ostatní barvy
OUTLINE_COL = (0, 0, 0)
PADDLE_COL = (0, 204, 102)
PADDLE_OUTLINE = (100, 100, 100)

# Barvy textů
TEXT_COL = (255, 255, 255)
TEXT_COL_RED = (255, 0, 0)
TEXT_COL_GREEN = (0, 255, 0)

