import pygame
from pygame.locals import *
import random
from settings import *

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Breakout')

#background
BG = pygame.image.load(BG_IMAGE_PATH).convert()
background = pygame.transform.scale(BG, (SCREEN_WIDTH, SCREEN_HEIGHT))

#font 
font = pygame.font.Font("Projekt-main/images/font/lemonmilk.otf", 27)
font1 = pygame.font.Font("Projekt-main/images/font/lemonmilk.otf", 50)



#menu obtížností
in_menu = True
selected_level = 2 


#vykreslení pozadí
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


#stěna z bloků
class wall():
    def __init__(self):
        self.width = SCREEN_WIDTH // COLS
        self.height = 50

    def clear_wall(self):  #odebrání bloků při konci hry
        self.blocks = []  

    def create_wall(self):
        self.blocks = []
        
        
        #Výběr úrovně a nastavení bloků
        current_rows = ROWS
        if selected_level == 1: #easy
            current_rows = 5 # 
        elif selected_level == 3: #hard
            current_rows = 7
        else:
            current_rows = 6 #medium 

		#vytvoření jednotlivých bloků
        block_individual = []
        for row in range(current_rows):
            block_row = []
            for col in range(COLS):
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                
                #nastavení síly bloku podle řady a obtížnosti
                strength = 1 
                
                if selected_level == 3: 
                    if row < 2: 
                        strength = 3 
                    elif row < 6: 
                        strength = 2 
                    else: 
                        strength = 1 
                
                else: 
                    if row < 2:
                        strength = 3
                    elif row < 4:
                        strength = 2
                    elif row < 6:
                        strength = 1
                
                
                block_individual = [rect, strength]
                block_row.append(block_individual)
            self.blocks.append(block_row)

#vykreslení stěny
    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                #barva bloku podle síly
                if block[1] == 3:
                    block_col = BLOCK_RED
                elif block[1] == 2:
                    block_col = BLOCK_ORANGE
                elif block[1] == 1:
                    block_col = BLOCK_YELLOW
                pygame.draw.rect(screen, block_col, block[0])
                pygame.draw.rect(screen, OUTLINE_COL, (block[0]), 2)



#pálka
class paddle():
    def __init__(self):
        self.reset()

#pohyb pálky
    def move(self): 
        self.direction = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if key[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
            self.direction = 1
#vykreslení pálky
    def draw(self):
        pygame.draw.rect(screen, PADDLE_COL, self.rect)
        pygame.draw.rect(screen, PADDLE_OUTLINE, self.rect, 3)


    def reset(self):
        # Základní velikost pálky
        self.height = 15
        
        # Změna velikosti pálky podle obtížnosti
        base_width = int(90 * SCREEN_WIDTH // 600) 
        
        if selected_level == 1: 
            self.width = base_width + 30
        elif selected_level == 3: 
            self.width = base_width - 30
        else: 
            self.width = base_width

        self.x = int((SCREEN_WIDTH / 2) - (self.width / 2))
        self.y = SCREEN_HEIGHT - (self.height * 2)
        self.speed = 5 
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0


#míček
class game_ball():
    def __init__(self, x, y):
        self.reset(x, y)

	#pohyb míčku
    def move(self):

        #kolize
        collision_thresh = 12

        wall_destroyed = 1
        row_count = 0
        for row in wall.blocks:
            item_count = 0
            for item in row:
                #úprava kolize
                if self.rect.colliderect(item[0]):
                    if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0:
                        self.speed_y *= -1
                    if abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0:
                        self.speed_y *= -1                      
                    if abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0:
                        self.speed_x *= -1
                    if abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0:
                        self.speed_x *= -1
                    #změna síly bloku po zásahu míčkem
                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1
                    else:
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)

                #kontrola jestli blok je zničený po zásahu
                if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0
                item_count += 1
            row_count += 1
        if wall_destroyed == 1:
            self.GAME_OVER = 1



        #kolize se stěnami
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x *= -1

        #kolize s horní a dolní hranou
        if self.rect.top < 0:
            self.speed_y *= -1
        if self.rect.bottom > SCREEN_HEIGHT:
            self.GAME_OVER = -1


        #kolize s pálkou
        if self.rect.colliderect(player_paddle):
            #kolize z vrchu pálky
            if abs(self.rect.bottom - player_paddle.rect.top) < collision_thresh and self.speed_y > 0:
                self.speed_y *= -1
                self.speed_x += player_paddle.direction
                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max
            else:
                self.speed_x *= -1



        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.GAME_OVER


    def draw(self):
        pygame.draw.circle(screen, PADDLE_COL, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
        pygame.draw.circle(screen, PADDLE_OUTLINE, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad, 3)



    def reset(self, x, y):
        self.ball_rad = 10
        self.x = x - self.ball_rad
        self.y = y
        self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = random.choice([-1, 1]) * random.uniform(2, 5)
        
        #rychlost míčku podle obtížnosti
        if selected_level == 1:
            self.speed_y = -3 
        else:
            self.speed_y = -4 
            
        self.speed_max = 5
        self.GAME_OVER = 0



#vytváření všech 3 objektů - stěna, pálka, míček
wall = wall()
player_paddle = paddle()
ball = game_ball(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)


run = True
while run:

    clock.tick(FPS)
    
    screen.blit(BG, (0, 0))

    #Menu obtížností
    if in_menu:
        draw_text('VYBER OBTÍŽNOST:', font1, text_col, 45, 100)
        draw_text('1 - LEHKÁ (EASY)', font, BLOCK_YELLOW, 180, 250)
        draw_text('2 - STŘEDNÍ (MEDIUM)', font, BLOCK_ORANGE, 150, 300)
        draw_text('3 - TĚŽKÁ (HARD)', font, BLOCK_RED, 180, 350)
        
        key = pygame.key.get_pressed()
        start_game = False
        
        if key[pygame.K_1]:
            selected_level = 1
            start_game = True
        elif key[pygame.K_2]:
            selected_level = 2
            start_game = True
        elif key[pygame.K_3]:
            selected_level = 3
            start_game = True
            
        if start_game:
            in_menu = False
            # Resetování hry s novou obtížností
            player_paddle.reset()
            ball.reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)
            wall.create_wall()

    else:
        #Zapnutí hry
        wall.draw_wall()
        player_paddle.draw()
        ball.draw()

        if LIVE_BALL:
            player_paddle.move()
            GAME_OVER = ball.move()
            if GAME_OVER != 0:
                LIVE_BALL = False

        if not LIVE_BALL:
            if GAME_OVER == 0:
                draw_text('KLIKNI PRO START', font, text_col, 160, 430)
            elif GAME_OVER == 1:
                draw_text('VYHRÁL SI!', font1, text_col_green, 130, 180)
                draw_text('KLIKNI PRO MENU', font, text_col, 165, 300)
            elif GAME_OVER == -1:
                wall.clear_wall()
                draw_text('PROHRÁL SI!', font1, text_col_red, 120, 180)
                draw_text('KLIKNI PRO MENU', font, text_col, 165, 300)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        # Ovládání hry
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            if not in_menu:
                if LIVE_BALL == False:
                    if GAME_OVER != 0:
                        in_menu = True
                        GAME_OVER = 0
                    else:
                        LIVE_BALL = True
                        ball.reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)

    pygame.display.update()

pygame.quit()