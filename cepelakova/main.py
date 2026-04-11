from databaze import save_score_by_username, init_db, award_achievement
import pygame
from pygame.locals import *
import random
import math

# Inicializace Pygame a mixeru pro zvuk
pygame.init()
pygame.mixer.init()

# Nastavení FPS a velikosti okna
clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Turtle")

# Načtení fontů pro různé účely
font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 40)
fontt = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 30)
ui_font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 25)
start_y = screen_height // 2 - 50

# Barvy
white = (255, 255, 255)
alice_blue = (240,248,255)
blue = (21,105,199)

# Proměnné pro animaci a zvuk
title_base_y = 200
title_anim_counter = 0
volume_x = 520
music_on = True
sfx_on = True

# Herní proměnné
ground_scroll = 0
scroll_speed = 4
flying = True
game_over = False
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
pipes_stopped = False
countdown_active = True
countdown_time = 3 
countdown_start = pygame.time.get_ticks()
difficulty = "medium"
username = ""
score_saved = False

# Nastavení obtížnosti - mezery mezi trubkami a frekvence
gap_min = 180
gap_max = 220
pipe_frequency_min = 1250
pipe_frequency_max = 1550

countdown_active = False
countdown_ready = False 
countdown_time = 3
countdown_start = 0

# Ovládání myši a hlasitosti
mouse_released = True
sound_volume = 20
music_volume = 15
gravity = 0.5
jump_strength = -10

last_volume_change = 0
volume_delay = 120

# Načtení zvukových efektů
try:
    death_sound = pygame.mixer.Sound("sounds/death.wav")
    death_sound.set_volume(sound_volume / 100)
except:
    death_sound = None

try:
    score_sound = pygame.mixer.Sound("sounds/score.wav")
    score_sound.set_volume(sound_volume / 100)
except:
    score_sound = None

# Načtení hudby na pozadí
try:
    pygame.mixer.music.load("sounds/music.mp3")
    pygame.mixer.music.set_volume(music_volume / 100)
except:
    pass

# Načtení obrázků
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load("img/restart.png")
button_img = pygame.transform.scale(button_img, (200, 70))

start_img = pygame.image.load("img/start.png")
settings_img = pygame.image.load("img/settings.png")
exit_img = pygame.image.load("img/exit.png")

start_img = pygame.transform.scale(start_img, (220, 80))
settings_img = pygame.transform.scale(settings_img, (220, 80))
exit_img = pygame.transform.scale(exit_img, (220, 80))

# Tlačítka pro výběr obtížnosti
easy_img = pygame.image.load("img/easy.png")
medium_img = pygame.image.load("img/medium.png")
hard_img = pygame.image.load("img/hard.png")

easy_img = pygame.transform.scale(easy_img, (220, 80))
medium_img = pygame.transform.scale(medium_img, (220, 80))
hard_img = pygame.transform.scale(hard_img, (220, 80))

back_img = pygame.image.load("img/back.png")
back_img = pygame.transform.scale(back_img, (200, 70))

# Funkce pro vykreslení textu
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Funkce pro vykreslení textu s outline
def draw_text_with_outline(text, font, text_col, outline_col, x, y, outline_width=2):
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                img = font.render(text, True, outline_col)
                screen.blit(img, (x + dx, y + dy))
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Reset hry do výchozího stavu
def reset_game():
    global pipes_stopped, pass_pipe, flying, countdown_active, countdown_start, game_over, countdown_ready

    pipe_group.empty()

    flappy.rect.x = 100
    flappy.rect.y = start_y

    flappy.vel = 0
    flappy.clicked = False

    flappy.index = 0
    flappy.counter = 0

    pipes_stopped = False
    pass_pipe = False
    flying = True
    game_over = False

    countdown_active = False
    countdown_ready = True 

    global score_saved
    score_saved = False

    return 0

# Přehrání death sound
def play_death_sound():
    if sfx_on and death_sound:
        death_sound.play()

# Přehrání score sound
def play_score_sound():
    if sfx_on and score_sound:
        score_sound.play()

# Třída pro želvu
class Turtle(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # Načtení animačních snímků želvy
        self.images = [
            pygame.image.load(f'img/turtle{i}.png')
            for i in range(1, 4)]

        self.index = 0
        self.counter = 0

        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))

        self.vel = 0  # Rychlost pádu
        self.clicked = False

    def update(self):
        global flying, game_over

        # Aplikace gravitace
        self.vel += gravity
        if self.vel > 15:
            self.vel = 15

        # Pohyb želvy (pád)
        if self.rect.bottom < 790:
            self.rect.y += int(self.vel)

        # Skok na kliknutí myší
        if not game_over and not pipes_stopped:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = jump_strength
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

        # Animace mávání ploutvemi
        if not game_over:
            self.counter += 1
            if self.counter > 10:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0

        # Rotace želvy podle rychlosti pádu
        if game_over:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
        else:
            angle = -self.vel * 2
            if angle > 25:
                angle = 25
            if angle < -25:
                angle = -25
            self.image = pygame.transform.rotate(self.images[self.index], angle)

# Třída pro trubky (překážky)
class Pipe(pygame.sprite.Sprite):

    def __init__(self, x, y, position, gap):
        super().__init__()
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        # position 1 = horní trubka, -1 = dolní trubka
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(gap / 2)]

    def update(self):
        # Pohyb trubek doleva
        if not pipes_stopped:
            self.rect.x -= scroll_speed
            if self.rect.right < 0:
                self.kill()

# Třída pro tlačítka
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        global mouse_released
        action = False
        pos = pygame.mouse.get_pos()
        
        # Detekce kliknutí na tlačítko
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1 and mouse_released:
            action = True
            mouse_released = False  
        if pygame.mouse.get_pressed()[0] == 0:
            mouse_released = True  
        
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

# Vytvoření skupin pro sprite
turtle_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

# Vytvoření želvy
flappy = Turtle(100, start_y)
turtle_group.add(flappy)

# Vytvoření tlačítek
restart_button = Button(screen_width // 2 - 100, screen_height // 2 - 150, button_img)
back_game_button = Button(screen_width // 2 - 100, screen_height // 2 - 50, back_img)
start_button = Button(screen_width//2 - 100, 340, start_img)
settings_button = Button(screen_width//2 - 100, 440, settings_img)
exit_button = Button(screen_width//2 - 100, 540, exit_img)
easy_button = Button(screen_width//2 - 100, 340, easy_img)
medium_button = Button(screen_width//2 - 100, 440, medium_img)
hard_button = Button(screen_width//2 - 100, 540, hard_img)
back_menu_button = Button(screen_width // 2 - 100, 580, back_img)

# Stav hry
game_state = "menu"

# Hlavní herní smyčka
run = True

while run:

    # Menu
    if game_state == "menu":

        # Přehrávání hudby
        if music_on and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

        screen.blit(bg, (0,0))

        draw_text_with_outline("FLAPPY TURTLE", font, white, blue, 180, title_base_y, outline_width=3)

        # Tlačítka v menu
        if start_button.draw():
            game_state = "difficulty"
            pygame.event.clear()

        if settings_button.draw():
            game_state = "settings"
            mouse_released = True

        if exit_button.draw():
            run = False

        screen.blit(ground_img, (0,768))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()
        continue

    # výběr difficulty
    if game_state == "difficulty":

        if music_on and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

        screen.blit(bg, (0,0))

        draw_text_with_outline("SELECT DIFFICULTY", fontt, white, blue, 180, 200, outline_width=3)

        # Nastavení parametrů podle zvolené obtížnosti
        if easy_button.draw():
            difficulty = "easy"
            gap_min = 220
            gap_max = 280
            pipe_frequency_min = 1350
            pipe_frequency_max = 1650
            countdown_ready = True
            game_state = "username"

        if medium_button.draw():
            difficulty = "medium"
            gap_min = 180
            gap_max = 220
            pipe_frequency_min = 1250
            pipe_frequency_max = 1550
            countdown_ready = True
            game_state = "username"

        if hard_button.draw():
            difficulty = "hard"
            gap_min = 150
            gap_max = 200
            pipe_frequency_min = 1150
            pipe_frequency_max = 1450
            countdown_ready = True
            game_state = "username"

        screen.blit(ground_img, (0,768))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()
        continue

    # Zadání username
    if game_state == "username":
            
            if music_on and not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)

            screen.blit(bg, (0,0))

            draw_text_with_outline("ENTER USERNAME", fontt, white, blue, 225, 200, outline_width=3)

            # Vykreslení input pole
            input_width = 400
            input_height = 60
            input_x = screen_width // 2 - input_width // 2
            input_y = screen_height // 2 - 150

            pygame.draw.rect(screen, (255,255,255), (input_x, input_y, input_width, input_height))
            pygame.draw.rect(screen, blue, (input_x, input_y, input_width, input_height), 4)
            draw_text(username, fontt, blue, input_x + 20, input_y + 15)

            draw_text("PRESS ENTER", ui_font, white, screen_width//2 - 135, input_y + 90)

            # Zpracování vstupu z klávesnice
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN and len(username) > 0:
                        pygame.mixer.music.stop()
                        game_state = "game"

                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]

                    else:
                        if len(username) < 12:
                            username += event.unicode

            pygame.display.update()
            continue

    # Nastavení
    if game_state == "settings":

        screen.blit(bg, (0,0))

        draw_text_with_outline("SETTINGS", font, alice_blue, blue, 270, 200, outline_width=3)

        music_text = "ON" if music_on else "OFF"
        sfx_text = "ON" if sfx_on else "OFF"

        draw_text_with_outline("MUSIC", fontt, alice_blue, blue, 240,320, outline_width=2)
        draw_text_with_outline(music_text, fontt, white, blue, 520,320, outline_width=2)

        draw_text_with_outline("SFX", fontt, alice_blue, blue, 260,420, outline_width=2)
        draw_text_with_outline(sfx_text, fontt, white, blue, 520,420, outline_width=2)

        # Tlačítko zpět do menu
        if back_menu_button.draw():
            game_state = "menu"

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

            # Ovládání hlasitosti pomocí šipek
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LEFT:
                    music_volume = max(0, music_volume - 5)

                if event.key == pygame.K_RIGHT:
                    music_volume = min(100, music_volume + 5)

                pygame.mixer.music.set_volume(music_volume / 100)

                if event.key == pygame.K_a:
                    sound_volume = max(0, sound_volume - 5)

                if event.key == pygame.K_d:
                    sound_volume = min(100, sound_volume + 5)

                if death_sound:
                    death_sound.set_volume(sound_volume / 100)

                if score_sound:
                    score_sound.set_volume(sound_volume / 100)
        
        # Klikání na přepínače hudby/SFX
        pos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()

        time_now = pygame.time.get_ticks()

        if mouse[0] and time_now - last_volume_change > volume_delay:

            if 500 < pos[0] < 600 and 300 < pos[1] < 360:
                music_on = not music_on

                if music_on:
                    pygame.mixer.music.set_volume(music_volume / 100)
                else:
                    pygame.mixer.music.set_volume(0)

            if 500 < pos[0] < 600 and 400 < pos[1] < 460:
                sfx_on = not sfx_on

            last_volume_change = time_now

        screen.blit(ground_img, (0,768))

        pygame.display.update()
        continue

    # Samotná hra
    if game_state == "game":
        
        clock.tick(fps)
        screen.blit(bg, (0, 0))

        # Spuštění odpočítávání před začátkem hry
        if countdown_ready and not countdown_active:
            countdown_start = pygame.time.get_ticks()
            countdown_active = True
            countdown_ready = False

        # Zobrazení odpočítávání
        if countdown_active:
            seconds_passed = (pygame.time.get_ticks() - countdown_start) // 1000
            timer = countdown_time - seconds_passed
            if timer <= 0:
                countdown_active = False
            else:
                draw_text_with_outline(str(timer), font, alice_blue, blue, screen_width // 2 - 30, screen_height // 2 - 90, outline_width=3)
                flappy.index = 1
                flappy.vel = 0
                flappy.image = pygame.transform.rotate(flappy.images[1], 0)

    # Aktualizace po odpočítávání
    if not countdown_active:
        turtle_group.update()
        pipe_group.update()

        # Generování nových trubek
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency and not pipes_stopped:

            gap = random.randint(gap_min, gap_max)
            pipe_frequency = random.randint(pipe_frequency_min, pipe_frequency_max)

            center = random.randint(300, 550)

            btm = Pipe(screen_width, center, -1, gap)
            top = Pipe(screen_width, center, 1, gap)

            pipe_group.add(btm)
            pipe_group.add(top)

            last_pipe = time_now

        # Detekce projetí trubkou a přičtení skóre
        if len(pipe_group) > 0 and not pipes_stopped:
            first_pipe = pipe_group.sprites()[0]
            if flappy.rect.left > first_pipe.rect.left and flappy.rect.right < first_pipe.rect.right and not pass_pipe:
                pass_pipe = True
            if pass_pipe and flappy.rect.left > first_pipe.rect.right:
                score += 1
                play_score_sound()
                pass_pipe = False

    # Vykreslení želvy a trubek
    turtle_group.draw(screen)
    pipe_group.draw(screen)

    # Posun země (nekonečný scrolling)
    if not countdown_active and not game_over:
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0
    screen.blit(ground_img, (ground_scroll, 768))
    
    # Zobrazení tlačítek po smrti
    if game_over:
        if game_over:

            if restart_button.draw():
                score = reset_game()

            if back_game_button.draw():
                score = reset_game()
                username = ""
                game_state = "menu"

    # Zpracování událostí
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                if music_on:
                    pygame.mixer.music.play(-1)
                score = reset_game()
                username = ""
                game_state = "menu"

            if event.key == pygame.K_SPACE and not game_over and not countdown_active:
                flappy.vel = -10

    # Kolize s trubkami nebo okrajem obrazovky
    if not countdown_active and not pipes_stopped:

        if pygame.sprite.groupcollide(turtle_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
            pipes_stopped = True
            play_death_sound()

            # Uložení skóre do databáze
            if not score_saved:
                save_score_by_username(username, score, difficulty)
                score_saved = True

        # Pád na zem
        if flappy.rect.bottom >= 790:
            flappy.rect.bottom = 790
            game_over = True
            pipes_stopped = True
            flying = False
            play_death_sound()

            if not score_saved:
                save_score_by_username(username, score, difficulty)

                # Udělování achievementů podle dosaženého skóre a obtížnosti
                from databaze import get_user_by_username, award_achievement

                user = get_user_by_username(username)
                if user:
                    user_id = user["id"]
                    
                    award_achievement(user_id, "První krůček")
                    
                    if score >= 20:
                        award_achievement(user_id, "Skokan")
                    
                    if score >= 100:
                        award_achievement(user_id, "Veterán")
                    
                    if difficulty == "easy" and score >= 50:
                        award_achievement(user_id, "Obtížnost Easy")
                    
                    if difficulty == "medium" and score >= 50:
                        award_achievement(user_id, "Obtížnost Medium")
                    
                    if difficulty == "hard" and score >= 50:
                        award_achievement(user_id, "Obtížnost Hard")

    # Zobrazení aktuálního skóre
    if not countdown_active:
        draw_text_with_outline(str(score), font, alice_blue, blue, screen_width // 2 - 20, 20,outline_width=3)

    pygame.display.update()