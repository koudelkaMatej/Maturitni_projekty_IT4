"""
Hlavní herní modul pro Platformer s Pygame.
Obsahuje herní smyčku, třídy pro hráče, svět, překážky a integraci s databází a nastavením.
"""

import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path
import time
import sys
import os

# Vlastní moduly
import database
import settings

# Zjištění absolutní cesty ke složce se skriptem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diagnostika - výpis aktuálního stavu
print("Aktuální pracovní adresář:", os.getcwd())
print("Složka se skriptem:", BASE_DIR)
print("Složka img existuje?", os.path.exists(os.path.join(BASE_DIR, 'img')))
if os.path.exists(os.path.join(BASE_DIR, 'img')):
    print("Obsah složky img:", os.listdir(os.path.join(BASE_DIR, 'img')))

# Inicializace Pygame a mixeru
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Catformer')

# Inicializace databáze
database.init_db()

# Načtení nastavení hlasitosti
config = settings.load_settings()
music_volume = config['music_volume']
sfx_volume = config['sfx_volume']
mixer.music.set_volume(music_volume)

# Definice fontů (s podporou diakritiky)
try:
    # Pro Windows/macOS
    font = pygame.font.SysFont('Arial', 70)
    font_score = pygame.font.SysFont('Arial', 30)
    font_small = pygame.font.SysFont('Arial', 20)
except:
    try:
        # Pro Linux
        font = pygame.font.SysFont('DejaVuSans', 70)
        font_score = pygame.font.SysFont('DejaVuSans', 30)
        font_small = pygame.font.SysFont('DejaVuSans', 20)
    except:
        # Krajní fallback
        font = pygame.font.Font(None, 70)
        font_score = pygame.font.Font(None, 30)
        font_small = pygame.font.Font(None, 20)

# Herní proměnné
tile_size = 50
game_over = 0
main_menu = True
settings_menu = False
show_leaderboard = False
input_name = False
player_name = ""
level = 1
max_levels = 7
score = 0
current_game_id = None
game_over_saved = False

# Barvy
white = (255, 255, 255)
blue = (0, 0, 255)

# Funkce pro usnadnění cesty
def img_path(filename):
    return os.path.join(BASE_DIR, 'img', filename)

# Načtení obrázků (s absolutní cestou)
try:
    bg_img = pygame.image.load(img_path('sky.png'))
    restart_img = pygame.image.load(img_path('restart_btn.png'))
    start_img = pygame.image.load(img_path('start_btn.png'))
    exit_img = pygame.image.load(img_path('exit_btn.png'))
    settings_img = pygame.image.load(img_path('settings_btn.png'))
    leaderboard_img = pygame.image.load(img_path('leaderboard_btn.png'))
except pygame.error as e:
    print(f"Chyba při načítání obrázků: {e}")
    print("Ujistěte se, že všechny obrázky jsou ve složce 'img'.")
    sys.exit(1)

back_img = exit_img  # použijeme exit jako tlačítko zpět

# Načtení zvuků
try:
    pygame.mixer.music.load(img_path('music.wav'))
    pygame.mixer.music.play(-1, 0.0, 5000)
    coin_fx = pygame.mixer.Sound(img_path('coin.wav'))
    coin_fx.set_volume(sfx_volume)
    jump_fx = pygame.mixer.Sound(img_path('jump.wav'))
    jump_fx.set_volume(sfx_volume)
    game_over_fx = pygame.mixer.Sound(img_path('game_over.wav'))
    game_over_fx.set_volume(sfx_volume)
except pygame.error as e:
    print(f"Chyba při načítání zvuků: {e}")
    print("Některé zvuky mohou chybět, hra poběží dál.")
    # Vytvoříme tiché zvuky, aby hra nespadla
    coin_fx = pygame.mixer.Sound(buffer=bytes([0]*1000))
    jump_fx = pygame.mixer.Sound(buffer=bytes([0]*1000))
    game_over_fx = pygame.mixer.Sound(buffer=bytes([0]*1000))

# Pomocné funkce
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def trim_image(img):
    rect = img.get_bounding_rect()
    trimmed = pygame.Surface(rect.size, pygame.SRCALPHA)
    trimmed.blit(img, (0, 0), rect)
    return trimmed

# Třída Button
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        screen.blit(self.image, self.rect)
        return action

# Třída Player
class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and not self.jumped and not self.in_air:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if not key[pygame.K_UP]:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]

            # animace
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]

            # gravitace
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # kolize s dlaždicemi
            self.in_air = True
            for tile in world.tile_list:
                # x
                if tile[1].colliderect(self.hitbox.x + dx, self.hitbox.y, self.width, self.height):
                    dx = 0
                # y
                if tile[1].colliderect(self.hitbox.x, self.hitbox.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.hitbox.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.hitbox.bottom
                        self.vel_y = 0
                        self.in_air = False

            # kolize s nepřáteli
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()

            # kolize s lávou
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # kolize s východem
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # kolize s platformami
            for platform in platform_group:
                if platform.rect.colliderect(self.hitbox.x + dx, self.hitbox.y, self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.hitbox.x, self.hitbox.y + dy, self.width, self.height):
                    if abs((self.hitbox.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.hitbox.top
                    elif abs((self.hitbox.bottom + dy) - platform.rect.top) < col_thresh:
                        self.hitbox.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    if platform.move_x != 0:
                        self.hitbox.x += platform.move_direction

            # aktualizace pozice
            self.hitbox.x += dx
            self.hitbox.y += dy
            self.rect.centerx = self.hitbox.centerx
            self.rect.bottom = self.hitbox.bottom

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
            if self.hitbox.y > 200:
                self.hitbox.y -= 5
            self.rect.centerx = self.hitbox.centerx
            self.rect.bottom = self.hitbox.bottom

        screen.blit(self.image, self.rect)
        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(img_path(f'cat{num}.png'))
            img_right = pygame.transform.scale(img_right, (tile_size, tile_size))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load(img_path('ghost.png'))
        self.dead_image = pygame.transform.scale(self.dead_image, (tile_size, tile_size))
        self.image = self.images_right[self.index]

        self.width = int(tile_size * 0.6)
        self.height = int(tile_size * 0.8)
        self.hitbox = pygame.Rect(x, y, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.hitbox.centerx
        self.rect.bottom = self.hitbox.bottom

        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

# Třída World
class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        dirt_img = pygame.image.load(img_path('dirt.png'))
        grass_img = pygame.image.load(img_path('grass.png'))

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

# Třída Enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(img_path('blob.png'))
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

# Třída Platform
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(img_path('platform.png'))
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

# Třída Lava
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(img_path('lava.png'))
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Třída Coin
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(img_path('coin.png'))
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Třída Exit
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(img_path('exit.png'))
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Vytvoření skupin a hráče
player = Player(100, screen_height - 130)
blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Dummy coin pro zobrazení skóre
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# Načtení prvního levelu (soubory level1_data, level2_data, ... v hlavní složce)
if path.exists(os.path.join(BASE_DIR, f'level{level}_data')):
    with open(os.path.join(BASE_DIR, f'level{level}_data'), 'rb') as pickle_in:
        world_data = pickle.load(pickle_in)
    world = World(world_data)
else:
    print(f"Soubor level{level}_data nebyl nalezen!")
    world = World([])  # prázdný svět, aby hra nespadla

def reset_level(level):
    player.reset(100, screen_height - 130)
    blob_group.empty()
    platform_group.empty()
    coin_group.empty()
    lava_group.empty()
    exit_group.empty()
    if path.exists(os.path.join(BASE_DIR, f'level{level}_data')):
        with open(os.path.join(BASE_DIR, f'level{level}_data'), 'rb') as pickle_in:
            world_data = pickle.load(pickle_in)
        new_world = World(world_data)
        # znovu přidáme dummy coin
        score_coin = Coin(tile_size // 2, tile_size // 2)
        coin_group.add(score_coin)
        return new_world
    else:
        print(f"Soubor level{level}_data nebyl nalezen!")
        return World([])

# -------------------- ÚPRAVA TLAČÍTEK --------------------
# Zmenšíme tlačítka na rozumnou velikost
start_img = pygame.transform.scale(start_img, (300, 150))
exit_img = pygame.transform.scale(exit_img, (300, 150))
settings_img = pygame.transform.scale(settings_img, (300, 150))
leaderboard_img = pygame.transform.scale(leaderboard_img, (300, 150))
back_img = pygame.transform.scale(back_img, (300, 150))
restart_img = pygame.transform.scale(restart_img, (200, 100))

# Oříznutí (odstranění průhledných okrajů)
start_img = trim_image(start_img)
exit_img = trim_image(exit_img)
settings_img = trim_image(settings_img)
leaderboard_img = trim_image(leaderboard_img)
back_img = trim_image(back_img)

# Střed obrazovky pro každé tlačítko zvlášť
start_x = (screen_width - start_img.get_width()) // 2
settings_x = (screen_width - settings_img.get_width()) // 2
leaderboard_x = (screen_width - leaderboard_img.get_width()) // 2
exit_x = (screen_width - exit_img.get_width()) // 2
back_x = (screen_width - back_img.get_width()) // 2

# Vertikální pozice s rozestupy
start_y = screen_height // 2 - 200
settings_y = start_y + 160
leaderboard_y = settings_y + 160
exit_y = leaderboard_y + 160
back_y = screen_height // 2 + 250   # pro tlačítko zpět

# Vytvoření tlačítek menu
start_button = Button(start_x, start_y, start_img)
settings_button = Button(settings_x, settings_y, settings_img)
leaderboard_button = Button(leaderboard_x, leaderboard_y, leaderboard_img)
exit_button = Button(exit_x, exit_y, exit_img)

# Tlačítka pro restart a návrat do menu (po smrti) - také je lépe vycentrujeme
restart_button = Button(screen_width // 2 - 250, screen_height // 2 + 100, restart_img)
menu_button = Button(screen_width // 2 + 50, screen_height // 2 + 100, exit_img)

# Tlačítko zpět (pro settings a leaderboard)
back_button = Button(back_x, back_y, back_img)
# ---------------------------------------------------------

# Hlavní smyčka
run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))

    if main_menu:
        if exit_button.draw():
            run = False
        if start_button.draw():
            input_name = True
            main_menu = False
            player_name = ""
        if settings_button.draw():
            settings_menu = True
            main_menu = False
        if leaderboard_button.draw():
            show_leaderboard = True
            main_menu = False

    elif settings_menu:
        draw_text("Nastavení", font, white, 300, 100)
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            music_volume = min(1.0, music_volume + 0.01)
            mixer.music.set_volume(music_volume)
            pygame.time.delay(100)
        if keys[K_DOWN]:
            music_volume = max(0.0, music_volume - 0.01)
            mixer.music.set_volume(music_volume)
            pygame.time.delay(100)
        if keys[K_RIGHT]:
            sfx_volume = min(1.0, sfx_volume + 0.01)
            coin_fx.set_volume(sfx_volume)
            jump_fx.set_volume(sfx_volume)
            game_over_fx.set_volume(sfx_volume)
            pygame.time.delay(100)
        if keys[K_LEFT]:
            sfx_volume = max(0.0, sfx_volume - 0.01)
            coin_fx.set_volume(sfx_volume)
            jump_fx.set_volume(sfx_volume)
            game_over_fx.set_volume(sfx_volume)
            pygame.time.delay(100)

        draw_text(f"Hudba: {int(music_volume*100)}%", font_score, white, 300, 200)
        draw_text(f"Efekty: {int(sfx_volume*100)}%", font_score, white, 300, 250)
        draw_text("Šipky nahoru/dolu - hudba, doleva/doprava - efekty", font_small, white, 200, 350)

        if back_button.draw():
            config['music_volume'] = music_volume
            config['sfx_volume'] = sfx_volume
            settings.save_settings(config)
            settings_menu = False
            main_menu = True

    elif show_leaderboard:
        draw_text("Žebříček nejlepších hráčů", font, white, 200, 50)
        leaderboard = database.get_leaderboard(10)
        if leaderboard:
            y = 150
            for idx, entry in enumerate(leaderboard, 1):
                text = f"{idx}. {entry['username']} - Level {entry['level']} - {entry['stars']} hvězd ({entry['date']})"
                draw_text(text, font_score, white, 100, y)
                y += 40
        else:
            draw_text("Žádná data k zobrazení.", font_score, white, 100, 200)
        if back_button.draw():
            show_leaderboard = False
            main_menu = True

    elif input_name:
        draw_text("Zadej své jméno:", font, white, 200, 200)
        pygame.draw.rect(screen, white, (200, 300, 400, 50), 2)
        draw_text(player_name, font_score, white, 210, 310)
        draw_text("Enter pro potvrzení, ESC pro návrat", font_small, white, 200, 400)

    else:
        world.draw()

        if game_over == 0:
            blob_group.update()
            platform_group.update()
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        # Uložení při smrti
        if game_over == -1 and not game_over_saved and current_game_id is not None:
            database.save_score(current_game_id, level, score)
            database.end_game(current_game_id)
            game_over_saved = True

        # Uložení při výhře (poslední level)
        if game_over == 1 and not game_over_saved and current_game_id is not None:
            if level == max_levels:
                database.save_score(current_game_id, level, score)
                database.end_game(current_game_id)
                game_over_saved = True

        # Obrazovka po smrti
        if game_over == -1:
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2 - 50)
            if restart_button.draw():
                world = reset_level(level)
                game_over = 0
                score = 0
                game_over_saved = False
                # Začneme novou hru pro stejného uživatele
                if player_name:
                    user = database.get_user_by_username(player_name)
                    if user:
                        current_game_id = database.start_game(user['id'])
            if menu_button.draw():
                main_menu = True
                input_name = False
                game_over = 0
                score = 0
                level = 1
                game_over_saved = False
                current_game_id = None
                # Reset světa na level 1
                if path.exists(os.path.join(BASE_DIR, f'level{level}_data')):
                    with open(os.path.join(BASE_DIR, f'level{level}_data'), 'rb') as pickle_in:
                        world_data = pickle.load(pickle_in)
                    world = World(world_data)
                    player.reset(100, screen_height - 130)

        # Dokončení levelu
        if game_over == 1:
            level += 1
            if level <= max_levels:
                world = reset_level(level)
                game_over = 0
                game_over_saved = False
            else:
                draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
                if restart_button.draw():
                    level = 1
                    world = reset_level(level)
                    game_over = 0
                    score = 0
                    game_over_saved = False
                    if player_name:
                        user = database.get_user_by_username(player_name)
                        if user:
                            current_game_id = database.start_game(user['id'])

    # Události
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == KEYDOWN:
            if input_name:
                if event.key == K_ESCAPE:
                    input_name = False
                    main_menu = True
                    player_name = ""
                elif event.key == K_RETURN:
                    if player_name.strip() != "":
                        user = database.get_user_by_username(player_name)
                        if not user:
                            user_id = database.add_user(player_name)
                        else:
                            user_id = user['id']
                        if user_id is not None:
                            current_game_id = database.start_game(user_id)
                        else:
                            current_game_id = None
                        input_name = False
                        level = 1
                        score = 0
                        game_over = 0
                        game_over_saved = False
                        if path.exists(os.path.join(BASE_DIR, f'level{level}_data')):
                            with open(os.path.join(BASE_DIR, f'level{level}_data'), 'rb') as pickle_in:
                                world_data = pickle.load(pickle_in)
                            world = World(world_data)
                            player.reset(100, screen_height - 130)
                elif event.key == K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if event.unicode and event.unicode.isprintable() and len(player_name) < 20:
                        player_name += event.unicode

    pygame.display.update()

pygame.quit()
sys.exit()