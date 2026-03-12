import pygame
from pygame.locals import *
import random
from Timer import GameTimer 
from settings import *


pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Breakout')

game_timer = GameTimer() #načtení timeru

#background a boosty
BG = pygame.image.load(BG_IMAGE_PATH).convert()
background = pygame.transform.scale(BG, (SCREEN_WIDTH, SCREEN_HEIGHT))
img_plus = pygame.transform.scale(pygame.image.load(IMG_PATH_PLUS).convert_alpha(), BOOST_SIZE)
img_minus = pygame.transform.scale(pygame.image.load(IMG_PATH_MINUS).convert_alpha(), BOOST_SIZE)
img_ball = pygame.transform.scale(pygame.image.load(IMG_PATH_BALL).convert_alpha(), BOOST_SIZE)
 
#font 
font = pygame.font.Font("pazderao/images/font/lemonmilk.otf", 27)
font1 = pygame.font.Font("pazderao/images/font/lemonmilk.otf", 50)

#menu obtížností
in_menu = True
selected_level = 2 

#vykreslení pozadí
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Boosty
class boost():
    def __init__(self, x, y, b_type):
        self.b_type = b_type
        # Použijeme velikost ze settings
        self.rect = pygame.Rect(x, y, BOOST_SIZE[0], BOOST_SIZE[1])
        self.speed = 3

    def move(self):
        self.rect.y += self.speed
        return self.rect.top < SCREEN_HEIGHT 

    def draw(self):
        if self.b_type == 'plus':
            screen.blit(img_plus, self.rect)
        elif self.b_type == 'minus':
            screen.blit(img_minus, self.rect)
        elif self.b_type == 'ball':
            screen.blit(img_ball, self.rect)


#stěna z bloků
class wall():
    def __init__(self):
        self.width = SCREEN_WIDTH // COLS
        self.height = 50

    def clear_wall(self):  #odebrání bloků při konci hry
        self.blocks = []  

    def create_wall(self):
        self.blocks = []
        current_rows = ROWS
        if selected_level == 1: current_rows = 5 
        elif selected_level == 3: current_rows = 6
        else: current_rows = 6 

        for row in range(current_rows):
            block_row = []
            for col in range(COLS):
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                strength = 1 
                if selected_level == 3: 
                    if row < 2: strength = 3 
                    elif row < 6: strength = 2 
                    else: strength = 1 
                else: 
                    if row < 2: strength = 3
                    elif row < 4: strength = 2
                    elif row < 6: strength = 1
                
                block_individual = [rect, strength]
                block_row.append(block_individual)
            self.blocks.append(block_row)

    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                if block[1] == 3: block_col = BLOCK_RED
                elif block[1] == 2: block_col = BLOCK_ORANGE
                elif block[1] == 1: block_col = BLOCK_YELLOW
                if block[1] > 0: # kreslíme jen existující bloky
                    pygame.draw.rect(screen, block_col, block[0])
                    pygame.draw.rect(screen, OUTLINE_COL, (block[0]), 2)

#pálka
class paddle():
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
        if selected_level == 1: self.width = base_width + 30
        elif selected_level == 3: self.width = base_width 
        else: self.width = base_width

        self.x = int((SCREEN_WIDTH / 2) - (self.width / 2))
        self.y = SCREEN_HEIGHT - (self.height * 2)
        self.speed = 5 
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0

#míček
class game_ball():
    def __init__(self, x, y):
        self.speed_max = 5
        self.reset(x, y)

    def move(self):
        collision_thresh = 12
        wall_destroyed = 1
        row_count = 0
        for row in wall.blocks:
            item_count = 0
            for item in row:
                if self.rect.colliderect(item[0]) and item[1] > 0:
                    if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0: self.speed_y *= -1
                    if abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0: self.speed_y *= -1                      
                    if abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0: self.speed_x *= -1
                    if abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0: self.speed_x *= -1
                    
                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1
                    else:
                        wall.blocks[row_count][item_count][1] = 0 # Blok je zničen
                        # --- ŠANCE NA VYPADNUTÍ BOOSTU (20%) ---
                        if random.random() < 0.2:
                            active_boosts.append(boost(item[0].centerx, item[0].centery, random.choice(['plus', 'minus', 'ball'])))

                if wall.blocks[row_count][item_count][1] > 0:
                    wall_destroyed = 0
                item_count += 1
            row_count += 1
        
        if wall_destroyed == 1: self.GAME_OVER = 1

        if self.rect.left < 0:
            self.rect.left = 0 
            self.speed_x *= -1
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH 
            self.speed_x *= -1
        if self.rect.top < 0:
            self.rect.top = 0
            self.speed_y *= -1
        if self.rect.bottom > SCREEN_HEIGHT: return "dead"

        if self.rect.colliderect(player_paddle):
            if self.speed_y > 0:
                self.rect.bottom = player_paddle.rect.top 
                self.speed_y *= -1
                
                # Výpočet pozice dopadu na pálku
                paddle_center = player_paddle.rect.centerx
                ball_center = self.rect.centerx
                distance_from_center = ball_center - paddle_center
                
                # Výpočet poměru (-1.0 až 1.0)
                max_distance = player_paddle.rect.width / 2
                ratio = distance_from_center / max_distance
                
                # Nastavení nové rychlosti X podle místa dopadu a citlivosti ze settings
                self.speed_x = ratio * self.speed_max * PADDLE_INFLUENCE

        if abs(self.speed_x) < MIN_X_SPEED:
            self.speed_x = MIN_X_SPEED if self.speed_x >= 0 else -MIN_X_SPEED
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        return self.GAME_OVER

    def draw(self):
        pygame.draw.circle(screen, PADDLE_COL, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
        pygame.draw.circle(screen, PADDLE_OUTLINE, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad, 3)

    def reset(self, x, y):
        self.ball_rad = 10
        self.rect = Rect(x - self.ball_rad, y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = random.choice([-1, 1]) * random.uniform(2, 5)
        if selected_level == 1:
            self.speed_y = -3    # Easy (pomalý)
        elif selected_level == 3:
            self.speed_y = -5    # Hard 
            self.speed_max = 6   
        else:
            self.speed_y = -4    # Medium (střední)
            self.speed_max = 5
        self.GAME_OVER = 0

#vytváření objektů
wall = wall()
player_paddle = paddle()
balls = [] # Seznam pro míčky
active_boosts = [] # Seznam pro padající ovoce
paddle_timer = 0 # Časovač pro pálku

run = True
while run:
    clock.tick(FPS)
    screen.blit(background, (0, 0))

    if in_menu:
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
            balls = [game_ball(player_paddle.rect.centerx, player_paddle.rect.top)]
            wall.create_wall()
            game_timer.start()
            active_boosts = []
    else:
        wall.draw_wall()
        player_paddle.draw()
        game_timer.draw(screen, font, (255, 255, 255), 20, 20)
        for b in balls: b.draw()
        for bst in active_boosts: bst.draw()

        if LIVE_BALL:
            player_paddle.move()
            
            # --- LOGIKA ČASOVAČE PÁLKY (10 sekund) ---
            if paddle_timer > 0:
                if pygame.time.get_ticks() - paddle_timer > 10000:
                    # Reset šířky pálky
                    current_x = player_paddle.rect.centerx
                    player_paddle.reset()
                    player_paddle.rect.centerx = current_x
                    paddle_timer = 0

            # Pohyb a správa míčků
            for b in balls[:]:
                GAME_OVER = b.move()
                if GAME_OVER == "dead":
                    balls.remove(b)
                elif GAME_OVER != 0:
                    LIVE_BALL = False

            if not balls: # Pokud došly všechny míčky
                GAME_OVER = -1
                LIVE_BALL = False

            # --- LOGIKA PADÁNÍ A SBÍRÁNÍ OVOCE ---
            for bst in active_boosts[:]:
                if not bst.move():
                    active_boosts.remove(bst)
                elif bst.rect.colliderect(player_paddle.rect):
                    if bst.b_type == 'plus':
                        player_paddle.rect.inflate_ip(60, 0) # Rozšíří pálku
                        paddle_timer = pygame.time.get_ticks()
                    elif bst.b_type == 'minus':
                        player_paddle.rect.width = max(40, player_paddle.rect.width - 40) # Zmenší pálku
                        paddle_timer = pygame.time.get_ticks()
                    elif bst.b_type == 'ball':
                        balls.append(game_ball(player_paddle.rect.centerx, player_paddle.rect.top))
                    active_boosts.remove(bst)

        if not LIVE_BALL:
            if GAME_OVER == 0: draw_text('KLIKNI PRO SPUŠTĚNÍ HRY', font, text_col, 110, 430), game_timer.stop()
            elif GAME_OVER == 1:
                game_timer.stop()        
                game_timer.save_time(CESTA_PRO_DATA)
                draw_text('VYHRÁL SI!', font1, text_col_green, 130, 180)
                draw_text('KLIKNI PRO NÁVRÁT DO MENU', font, text_col, 80, 300)
            elif GAME_OVER == -1:
                game_timer.stop()        
                wall.clear_wall()
                draw_text('PROHRÁL SI!', font1, text_col_red, 120, 180)
                draw_text('KLIKNI PRO NÁVRÁT DO MENU', font, text_col, 80, 300)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            if not in_menu:
                if LIVE_BALL == False:
                    if GAME_OVER != 0:
                        in_menu = True
                        GAME_OVER = 0
                    else:
                        LIVE_BALL = True
                        balls = [game_ball(player_paddle.rect.centerx, player_paddle.rect.top)]
                        game_timer.start()

    pygame.display.update()

pygame.quit()