import pygame

# rozměry okna hry
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

# fonty a texty
pygame.font.init()
FONT_PATH = "pazderao/images/font/lemonmilk.otf"
font = pygame.font.Font(FONT_PATH, 27)
font1 = pygame.font.Font(FONT_PATH, 50)
font2 = pygame.font.Font(FONT_PATH, 17)

# cesty
BG_IMAGE_PATH = "pazderao/images/background.jpg"
CESTA_PRO_DATA = "pazderao/data/casy.txt" 
IMG_PATH_PLUS = "pazderao/images/plus.png" 
IMG_PATH_MINUS = "pazderao/images/minus.png"
IMG_PATH_BALL = "pazderao/images/ball.png"

# nastavení herní mechaniky
COLS = 6
ROWS = 7
clock = pygame.time.Clock()
FPS = 70
LIVE_BALL = False
GAME_OVER = 0
PADDLE_INFLUENCE = 1.1
MIN_X_SPEED = 1.5 

# rozměry bonusů
BOOST_SIZE = (30, 30)

# barvy pro různé stavy a objekty
text_col = (255, 255, 255)
text_col_red = (255, 0, 0)
text_col_green = (0, 255, 0)

BLOCK_YELLOW = (223, 188, 9) 
BLOCK_ORANGE = (246, 137, 27)
BLOCK_RED = (250, 85, 35)

OUTLINE_COL = (0, 0, 0)
PADDLE_COL = (0, 204, 102)
PADDLE_OUTLINE = (100, 100, 100)

# nastavení tlačítek v menu
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
BUTTON_COL = (70, 70, 70)
BUTTON_HOVER_COL = (100, 100, 100)
BUTTON_TEXT_COL = (255, 255, 255)

# čtverec pro tlačítko tabulky na obrazovce
table_button_rect = pygame.Rect(10, SCREEN_HEIGHT - 40, 100, 30)

# údaje pro připojení k databázi + doplňky 
host = "dbs.spskladno.cz"
username = "vyuka16"
password = "spsnet"
database = "vyuka16"
WEB_URL = "http://127.0.0.1:5000/"
povolené_znaky = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "

player_name = ""
entering_name = True 
in_menu = False