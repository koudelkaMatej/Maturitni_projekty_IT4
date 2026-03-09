import pygame
import sys
import random
import os


# --- NASTAVENÍ ---
GAME_WIDTH = 360
GAME_HEIGHT = 640


# Pták
bird_width = 48
bird_height = 34
bird_x = GAME_WIDTH / 8
bird_y = GAME_HEIGHT / 2


# Trubky
pipe_width = 64
pipe_height = 512
pipe_x = GAME_WIDTH
pipe_y = 0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "Obrazky")


def image_path(filename):
    return os.path.join(IMAGES_DIR, filename)


class Bird(pygame.Rect):
    def __init__(self, images):
        pygame.Rect.__init__(self, bird_x, bird_y, bird_width, bird_height)
        self.images = images
        self.index = 0
        self.counter = 0
        self.img = self.images[self.index]


    def animate(self):
        self.counter += 1
        if self.counter > 5:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.img = self.images[self.index]


class Pipe(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, pipe_x, pipe_y, pipe_width, pipe_height)
        self.img = img
        self.passed = False


# --- NAČÍTÁNÍ OBRÁZKŮ ---
bird_images = []
try:
    background_image = pygame.image.load(image_path("flappybirdbg.png"))
    img1 = pygame.image.load(image_path("redbird-downflap.png"))
    img2 = pygame.image.load(image_path("redbird-midflap.png"))
    img3 = pygame.image.load(image_path("redbird-upflap.png"))
    img1 = pygame.transform.scale(img1, (bird_width, bird_height))
    img2 = pygame.transform.scale(img2, (bird_width, bird_height))
    img3 = pygame.transform.scale(img3, (bird_width, bird_height))
    bird_images = [img1, img2, img3]


    top_pipe_image = pygame.image.load(image_path("toppipe.png"))
    top_pipe_image = pygame.transform.scale(top_pipe_image, (pipe_width, pipe_height))
    bottom_pipe_image = pygame.image.load(image_path("bottompipe.png"))
    bottom_pipe_image = pygame.transform.scale(bottom_pipe_image, (pipe_width, pipe_height))
except:
    background_image = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)); background_image.fill((0, 0, 0))
    ctverec = pygame.Surface((bird_width, bird_height)); ctverec.fill((255, 255, 0))
    bird_images = [ctverec, ctverec, ctverec]
    top_pipe_image = pygame.Surface((pipe_width, pipe_height)); top_pipe_image.fill((0, 255, 0))
    bottom_pipe_image = pygame.Surface((pipe_width, pipe_height)); bottom_pipe_image.fill((0, 255, 0))


bird = None
pipes = []
velocity_y = 0
score = 0
game_over = False
window = None
sounds = None
effects_enabled = False
sound_enabled = True


def set_sound_enabled(enabled):
    global sound_enabled
    sound_enabled = bool(enabled)
    if sounds and "flap" in sounds:
        sounds["flap"].set_volume(0.35 if sound_enabled else 0.0)


def init_audio():
    global sounds, effects_enabled
    effects_enabled = False
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
        flap_path = image_path("flap.mp3")
        sounds = {"flap": pygame.mixer.Sound(flap_path)}
        sounds["flap"].set_volume(0.35 if sound_enabled else 0.0)
        effects_enabled = True
    except Exception:
        sounds = None


def stop_audio():
    return


def create_pipes():
    # 1. ZMĚNA: RANDOM VERTIKÁLNÍ MEZERA (Díra mezi trubkami)
    # Vygenerujeme náhodnou velikost díry mezi 140 a 240 pixely
    opening_space = random.randint(140, 240)
   
    # Náhodná výška spodní hrany horní trubky
    random_pipe_y = pipe_y - pipe_height/4 - random.random()*(pipe_height/2)
   
    top_pipe = Pipe(top_pipe_image)
    top_pipe.y = random_pipe_y
    pipes.append(top_pipe)
   
    bottom_pipe = Pipe(bottom_pipe_image)
    # Spodní trubku posuneme o tu naši náhodnou díru (opening_space)
    bottom_pipe.y = top_pipe.y + top_pipe.height + opening_space
    pipes.append(bottom_pipe)


def move():
    global velocity_y, score, game_over
    velocity_y += 0.4
    bird.y += velocity_y
    bird.y = max(bird.y, 0)
    bird.animate()


    if bird.y > GAME_HEIGHT:
        game_over = True
        return


    for pipe in pipes:
        pipe.x -= 2
        if not pipe.passed and bird.x > pipe.x + pipe.width:
            score += 0.5
            pipe.passed = True
        if bird.colliderect(pipe):
            game_over = True
            return


    while len(pipes) > 0 and pipes[0].x < -pipe_width:
        pipes.pop(0)


def draw():
    window.blit(background_image, (0, 0))
    window.blit(bird.img, bird)
    for pipe in pipes:
        window.blit(pipe.img, pipe)
    score_font = pygame.font.SysFont("Trebuchet MS", 62, bold=True)
    score_text = score_font.render(str(int(score)), True, (255, 255, 255))
    score_shadow = score_font.render(str(int(score)), True, (20, 30, 48))
    score_x = (GAME_WIDTH - score_text.get_width()) // 2
    window.blit(score_shadow, (score_x + 2, 18))
    window.blit(score_text, (score_x, 14))

    if game_over:
        over_font = pygame.font.SysFont("Trebuchet MS", 28, bold=True)
        message = over_font.render("GAME OVER", True, (255, 255, 255))
        hint_font = pygame.font.SysFont("Trebuchet MS", 16, bold=True)
        hint = hint_font.render("Stiskni SPACE pro navrat", True, (255, 230, 170))
        box = pygame.Rect(38, 255, 285, 90)
        pygame.draw.rect(window, (15, 23, 42), box, border_radius=14)
        pygame.draw.rect(window, (255, 120, 120), box, width=2, border_radius=14)
        window.blit(message, (box.x + 60, box.y + 14))
        window.blit(hint, (box.x + 32, box.y + 52))


def spustit_hru(hlavni_okno):
    global window, bird, pipes, velocity_y, score, game_over
    window = hlavni_okno
    bird = Bird(bird_images)
    pipes = []
    velocity_y = 0
    score = 0
    game_over = False
    init_audio()
   
    clock = pygame.time.Clock()
    pipe_timer = pygame.USEREVENT + 1
   
    # Nastavíme první trubku za 1500 ms (1.5 sekundy)
    pygame.time.set_timer(pipe_timer, 1500)
   
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
           
            # 2. ZMĚNA: RANDOM HORIZONTÁLNÍ MEZERA (Časovač)
            if event.type == pipe_timer and not game_over:
                create_pipes() # Vytvoříme trubku teď
               
                # A HNED potom přenastavíme budík na náhodný čas pro PŘÍŠTÍ trubku
                # Náhodně mezi 1200 ms (rychle) a 2200 ms (pomalů/velká mezera)
                pygame.time.set_timer(pipe_timer, random.randint(1200, 2200))


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_over:
                        velocity_y = -6
                        if effects_enabled and sounds and sound_enabled:
                            sounds["flap"].play()
                    else:
                        stop_audio()
                        return score


        if not game_over:
            move()
        draw()
        pygame.display.update()
        clock.tick(60)
    return score


