import pygame
from pygame.locals import *
import random
import webbrowser
import sys, subprocess
from timer import GameTimer 
from settings import *
from menu import *



pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Breakout')

game_timer = GameTimer() # timer

BG = pygame.image.load(BG_IMAGE_PATH).convert()
background = pygame.transform.scale(BG, (SCREEN_WIDTH, SCREEN_HEIGHT))
img_plus = pygame.transform.scale(pygame.image.load(IMG_PATH_PLUS).convert_alpha(), BOOST_SIZE)
img_minus = pygame.transform.scale(pygame.image.load(IMG_PATH_MINUS).convert_alpha(), BOOST_SIZE)
img_ball = pygame.transform.scale(pygame.image.load(IMG_PATH_BALL).convert_alpha(), BOOST_SIZE)

in_menu = True
selected_level = 2 

def draw_text(text, font, text_col, x, y): # psaní textu na obrazovku
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

class boost(): # věci co padají z cihel
    def __init__(self, x, y, b_type):
        self.b_type = b_type
        self.rect = pygame.Rect(x, y, BOOST_SIZE[0], BOOST_SIZE[1])
        self.speed = 3

    def move(self):
        self.rect.y += self.speed
        return self.rect.top < SCREEN_HEIGHT 

    def draw(self):
        if self.b_type == 'plus': screen.blit(img_plus, self.rect)
        elif self.b_type == 'minus': screen.blit(img_minus, self.rect)
        elif self.b_type == 'ball': screen.blit(img_ball, self.rect)

class wall(): # nastavení cihel
    def __init__(self):
        self.width = SCREEN_WIDTH // COLS
        self.height = 50
        self.blocks = []

    def clear_wall(self): self.blocks = [] # smaže cihly

    def create_wall(self):
        self.blocks = []
        if selected_level == 1: current_rows = 5 
        else: current_rows = 6 

        for row in range(current_rows):
            block_row = []
            for col in range(COLS):
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                
                if selected_level == 3:
                    strength = 3 if row < 2 else (2 if row < 6 else 1)
                else:
                    strength = 3 if row < 2 else (2 if row < 4 else 1)
                
                block_row.append([rect, strength])
            self.blocks.append(block_row)

    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                if block[1] == 3: block_col = BLOCK_RED
                elif block[1] == 2: block_col = BLOCK_ORANGE
                elif block[1] == 1: block_col = BLOCK_YELLOW
                if block[1] > 0:
                    pygame.draw.rect(screen, block_col, block[0])
                    pygame.draw.rect(screen, OUTLINE_COL, (block[0]), 2)

class paddle(): # pálka dole
    def __init__(self):
        self.reset()

    def move(self): 
        self.direction = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if key[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
            self.direction = 1

    def draw(self):
        pygame.draw.rect(screen, PADDLE_COL, self.rect)
        pygame.draw.rect(screen, PADDLE_OUTLINE, self.rect, 3)

    def reset(self):
        self.height = 15
        base_width = int(90 * SCREEN_WIDTH // 600) 
        self.width = base_width + 30 if selected_level == 1 else base_width
        self.x = int((SCREEN_WIDTH / 2) - (self.width / 2))
        self.y = SCREEN_HEIGHT - (self.height * 2)
        self.speed = 5 
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0

class game_ball(): # míček
    def __init__(self, x, y):
        self.speed_max = 5
        self.reset(x, y)

    def reset(self, x, y):
        self.ball_rad = 10
        self.rect = Rect(x - self.ball_rad, y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = random.choice([-1, 1]) * random.uniform(2, 5)
        if selected_level == 1: self.speed_y = -3
        elif selected_level == 3: self.speed_y = -5; self.speed_max = 6
        else: self.speed_y = -4; self.speed_max = 5

    def draw(self):
        pygame.draw.circle(screen, PADDLE_COL, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
        pygame.draw.circle(screen, PADDLE_OUTLINE, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad, 3)

    def move(self, player_paddle, wall, active_boosts, boost_class):
        collision_thresh = 12
        wall_destroyed = 1
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left < 0:
            self.rect.left = 0
            self.speed_x *= -1
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.speed_x *= -1
        if self.rect.top < 0:
            self.rect.top = 0
            self.speed_y *= -1
        if self.rect.bottom > SCREEN_HEIGHT:
            return "dead"

        for row_idx, row in enumerate(wall.blocks):
            for col_idx, item in enumerate(row):
                if self.rect.colliderect(item[0]) and item[1] > 0:
                    if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0:
                        self.rect.bottom = item[0].top
                        self.speed_y *= -1
                    elif abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0:
                        self.rect.top = item[0].bottom
                        self.speed_y *= -1                       
                    elif abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0:
                        self.rect.right = item[0].left
                        self.speed_x *= -1
                    elif abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0:
                        self.rect.left = item[0].right
                        self.speed_x *= -1
                    
                    if wall.blocks[row_idx][col_idx][1] > 1:
                        wall.blocks[row_idx][col_idx][1] -= 1
                    else:
                        wall.blocks[row_idx][col_idx][1] = 0
                        if random.random() < 0.2:
                            active_boosts.append(boost_class(item[0].centerx, item[0].centery, random.choice(['plus', 'minus', 'ball'])))

                if wall.blocks[row_idx][col_idx][1] > 0: 
                    wall_destroyed = 0
        
        if wall_destroyed == 1: 
            return 1 # vyhra

        if self.rect.colliderect(player_paddle):
            if self.speed_y > 0:
                self.rect.bottom = player_paddle.rect.top 
                self.speed_y *= -1
                diff = self.rect.centerx - player_paddle.rect.centerx
                self.speed_x = (diff / (player_paddle.rect.width / 2)) * self.speed_max * PADDLE_INFLUENCE

        if abs(self.speed_x) < MIN_X_SPEED:
            self.speed_x = MIN_X_SPEED if self.speed_x >= 0 else -MIN_X_SPEED
            
        return 0

wall = wall()
player_paddle = paddle()
balls = [] 
active_boosts = [] 
paddle_timer = 0 
is_paused = False
pause_menu = PauseMenu(font)

run = True
while run:
    clock.tick(FPS)
    screen.blit(background, (0, 0))
    
    if entering_name:
        draw_text('JMENO:', font1, text_col, 60, 200)
        input_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 300, 300, 50)
        pygame.draw.rect(screen, BUTTON_COL, input_rect)
        pygame.draw.rect(screen, OUTLINE_COL, input_rect, 2)
        draw_text(player_name, font, text_col, input_rect.x + 10, input_rect.y + 10)
        draw_text('STISKNI ENTER PRO START', font2, text_col, 170, 400)

    elif in_menu:
        pygame.draw.rect(screen, (255, 255, 255), table_button_rect, 1)
        draw_text('TABULKA', font2, (255, 255, 255), 20, SCREEN_HEIGHT - 35)
        draw_text('VYBER OBTÍŽNOST:', font1, text_col, 45, 100)
        draw_text('1 - LEHKÁ (EASY)', font, BLOCK_YELLOW, 180, 250)
        draw_text('2 - STŘEDNÍ (MEDIUM)', font, BLOCK_ORANGE, 150, 300)
        draw_text('3 - TĚŽKÁ (HARD)', font, BLOCK_RED, 180, 350)
        
        key = pygame.key.get_pressed()
        start_game = False
        if key[pygame.K_1]: selected_level = 1; start_game = True
        elif key[pygame.K_2]: selected_level = 2; start_game = True
        elif key[pygame.K_3]: selected_level = 3; start_game = True
            
        if start_game:
            in_menu = False
            player_paddle.reset()
            balls = [game_ball(player_paddle.rect.centerx, player_paddle.rect.top - 20)]
            wall.create_wall()
            active_boosts = []
            GAME_OVER = 0
            LIVE_BALL = False
    else:
        wall.draw_wall()
        player_paddle.draw()
        game_timer.draw(screen, font, (255, 255, 255), 20, 20)
        for b in balls: b.draw()
        for bst in active_boosts: bst.draw()

        if not is_paused:
            if LIVE_BALL:
                player_paddle.move()
                
                if paddle_timer > 0:
                    if pygame.time.get_ticks() - paddle_timer > 10000:
                        curr_x = player_paddle.rect.centerx
                        player_paddle.reset()
                        player_paddle.rect.centerx = curr_x
                        paddle_timer = 0

                for b in balls[:]:
                    res = b.move(player_paddle, wall, active_boosts, boost)
                    if res == "dead": 
                        balls.remove(b)
                    elif res == 1: # VYHRA
                        GAME_OVER = 1
                        LIVE_BALL = False
                        game_timer.stop()
                        game_timer.save_time(selected_level, player_name)

                if not balls and GAME_OVER == 0:
                    GAME_OVER = -1
                    LIVE_BALL = False
                    game_timer.stop()

                for bst in active_boosts[:]:
                    if not bst.move(): 
                        active_boosts.remove(bst)
                    elif bst.rect.colliderect(player_paddle.rect):
                        if bst.b_type == 'plus':
                            player_paddle.rect.inflate_ip(60, 0)
                            paddle_timer = pygame.time.get_ticks()
                        elif bst.b_type == 'minus':
                            player_paddle.rect.width = max(40, player_paddle.rect.width - 40)
                            paddle_timer = pygame.time.get_ticks()
                        elif bst.b_type == 'ball':
                            balls.append(game_ball(player_paddle.rect.centerx, player_paddle.rect.top - 20))
                        active_boosts.remove(bst)

            if not LIVE_BALL:
                if GAME_OVER == 0: 
                    draw_text('KLIKNI PRO SPUSTENI HRY', font, text_col, 110, 430)
                elif GAME_OVER == 1:
                    draw_text('VYHRAL SI!', font1, text_col_green, 130, 300)
                    draw_text('KLIKNI PRO NAVRAT DO MENU', font, text_col, 80, 400)
                elif GAME_OVER == -1:
                    draw_text('PROHRAL SI!', font1, text_col_red, 120, 300)
                    draw_text('KLIKNI PRO NAVRAT DO MENU', font, text_col, 80, 400)
        else:
            action = pause_menu.draw(screen)
            if action == "resume":
                is_paused = False
                game_timer.resume()
            elif action == "quit":
                is_paused = False; in_menu = True; LIVE_BALL = False; GAME_OVER = 0; game_timer.reset() 

    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False
        
        if entering_name and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(player_name) > 0:
                entering_name = False; in_menu = True
            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            elif len(player_name) < 12 and event.unicode.isprintable():
                player_name += event.unicode

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not in_menu and GAME_OVER == 0:
                is_paused = not is_paused
                if is_paused: game_timer.pause()
                else: game_timer.resume()

        if event.type == pygame.MOUSEBUTTONDOWN and in_menu:
            if table_button_rect.collidepoint(pygame.mouse.get_pos()):
                try:
                    # spuštění webu současně se hrou
                    subprocess.Popen([sys.executable, "web.py"])
                    pygame.time.delay(500)
                except:
                    pass 
                
                webbrowser.open("http://127.0.0.1:5000/tab")
        
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            if not in_menu and not is_paused: 
                if not LIVE_BALL:
                    if GAME_OVER != 0:
                        in_menu = True 
                        GAME_OVER = 0
                        game_timer.reset()
                    else:
                        LIVE_BALL = True
                        balls = [game_ball(player_paddle.rect.centerx, player_paddle.rect.top - 20)]
                        game_timer.start()

    pygame.display.update()

pygame.quit()