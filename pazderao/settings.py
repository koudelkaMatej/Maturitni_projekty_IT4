import pygame

# Rozměry okna
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600


#font 
pygame.font.init()
FONT_PATH = "pazderao/images/font/lemonmilk.otf"
font = pygame.font.Font("pazderao/images/font/lemonmilk.otf", 27)
font1 = pygame.font.Font("pazderao/images/font/lemonmilk.otf", 50)
font2 = pygame.font.Font("pazderao/images/font/lemonmilk.otf", 17)

# Cesty k souborům
BG_IMAGE_PATH = "pazderao/images/background.jpg"
FONT_PATH = "pazderao/images/font/lemonmilk.otf"
CESTA_PRO_DATA = "pazderao/data/casy.txt" #pro timer.py
IMG_PATH_PLUS = "pazderao/images/plus.png" # pro boosty
IMG_PATH_MINUS = "pazderao/images/minus.png"
IMG_PATH_BALL = "pazderao/images/ball.png"

# Základní nastavení hry
COLS = 6
ROWS = 7
clock = pygame.time.Clock()
FPS = 70
LIVE_BALL = False
GAME_OVER = 0
PADDLE_INFLUENCE = 1.1
MIN_X_SPEED = 1.5 


# Velikost boostů
BOOST_SIZE = (30, 30)

# Grafika
text_col = (255, 255, 255)
text_col_red = (255, 0, 0)
text_col_green = (0, 255, 0)

BLOCK_YELLOW = (223, 188, 9) # Barvy bloků
BLOCK_ORANGE = (246, 137, 27)
BLOCK_RED = (250, 85, 35)

OUTLINE_COL = (0, 0, 0) # Ostatní barvy
PADDLE_COL = (0, 204, 102)
PADDLE_OUTLINE = (100, 100, 100)

TEXT_COL = (255, 255, 255) # Barvy textů
TEXT_COL_RED = (255, 0, 0)
TEXT_COL_GREEN = (0, 255, 0)

# Nastavení menu 
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
BUTTON_COL = (70, 70, 70)          # Základní barva tlačítka
BUTTON_HOVER_COL = (100, 100, 100) # Barva po přejetí myší
BUTTON_TEXT_COL = (255, 255, 255)

#tlačítko tabulka
table_button_rect = pygame.Rect(10, SCREEN_HEIGHT - 40, 100, 30)
