import pygame
import sys
import random
import os
import sqlite3

# --- KONFIGURACE A DATABÁZE ---
DB_NAME = "snake_game.db"

def init_db():
    """Inicializuje databázi při startu"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS highscores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def load_high_scores():
    """Načte 10 nejlepších unikátních výsledků"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT name, MAX(score) as top_score FROM highscores GROUP BY name ORDER BY top_score DESC LIMIT 10')
    scores = cursor.fetchall()
    conn.close()
    return scores

def save_high_score(name, score):
    """Uloží výsledek a aktualizuje webový žebříček"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO highscores (name, score) VALUES (?, ?)', (name, score))
    conn.commit()
    conn.close()
    generate_html_leaderboard()

def generate_html_leaderboard():
    """Vytvoří index.html se síní slávy"""
    scores = load_high_scores()
    html_content = """
    <!DOCTYPE html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <title>Snake Leaderboard</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: white; display: flex; justify-content: center; padding-top: 50px; }
            .leaderboard { background: #2d2d2d; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 400px; border: 2px solid #4caf50; }
            h1 { text-align: center; color: #4caf50; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #444; }
            .rank { color: gold; font-weight: bold; }
            .score { text-align: right; color: #4caf50; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="leaderboard">
            <h1>🐍 Síň slávy</h1>
            <table>
                <tr><th>#</th><th>Hráč</th><th style="text-align:right">Skóre</th></tr>
    """
    for i, (name, score) in enumerate(scores):
        html_content += f"<tr><td class='rank'>{i+1}.</td><td>{name}</td><td class='score'>{score}</td></tr>"
    
    html_content += "</table></div></body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# --- PYGAME SETUP ---
pygame.init()
init_db()
generate_html_leaderboard() # Vytvoří index.html hned při startu

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - Final Edition")

# Barvy
WHITE, BLACK, BLUE = (255, 255, 255), (0, 0, 0), (50, 150, 255)
DARK_GREEN, LIGHT_GRASS = (31, 122, 31), (35, 140, 35)
RED, GREEN, YELLOW = (200, 0, 0), (0, 255, 0), (255, 215, 0)

font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 80)
SNAKE_SIZE = 20
clock = pygame.time.Clock()

# Tlačítka (Rects)
play_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50)
hs_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)
back_button = pygame.Rect(20, 20, 120, 50)

def reset_game():
    return {
        "pos": [[WIDTH//2, HEIGHT//2]],
        "dir": (0, 0),
        "food": (random.randrange(0, (WIDTH-20)//20)*20, random.randrange(0, (HEIGHT-20)//20)*20),
        "score": 0,
        "dead": False
    }

def draw_grass():
    for y in range(0, HEIGHT, SNAKE_SIZE):
        for x in range(0, WIDTH, SNAKE_SIZE):
            color = LIGHT_GRASS if (x // SNAKE_SIZE + y // SNAKE_SIZE) % 2 == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (x, y, SNAKE_SIZE, SNAKE_SIZE))

def draw_button(rect, text):
    """Vykreslí tlačítko s modrou výplní a černým rámečkem"""
    pygame.draw.rect(screen, BLUE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# Globální stavy
current_state = "menu"
user_name = ""
game = reset_game()

# --- HLAVNÍ SMYČKA ---
running = True
while running:
    screen.fill(DARK_GREEN)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 1. Psaní jména
        if current_state == "input_name":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_name.strip():
                        game = reset_game()
                        current_state = "game"
                elif event.key == pygame.K_BACKSPACE:
                    user_name = user_name[:-1]
                else:
                    if len(user_name) < 12:
                        user_name += event.unicode

        # 2. Ovládání hada (WSAD + Šipky)
        elif current_state == "game" and not game["dead"]:
            if event.type == pygame.KEYDOWN:
                if (event.key in [pygame.K_w, pygame.K_UP]) and game["dir"] != (0, 20):
                    game["dir"] = (0, -20)
                elif (event.key in [pygame.K_s, pygame.K_DOWN]) and game["dir"] != (0, -20):
                    game["dir"] = (0, 20)
                elif (event.key in [pygame.K_a, pygame.K_LEFT]) and game["dir"] != (20, 0):
                    game["dir"] = (-20, 0)
                elif (event.key in [pygame.K_d, pygame.K_RIGHT]) and game["dir"] != (-20, 0):
                    game["dir"] = (20, 0)

        # 3. Kliknutí myší (Funguje ve všech stavech)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == "menu":
                if play_button.collidepoint(event.pos):
                    current_state = "input_name"
                elif hs_button.collidepoint(event.pos):
                    current_state = "highscore"
            
            # Opravené tlačítko zpět pro všechny ostatní obrazovky
            elif current_state in ["input_name", "highscore", "game"]:
                if back_button.collidepoint(event.pos):
                    current_state = "menu"
                    game["dir"] = (0, 0)

    # --- RENDEROVÁNÍ ---
    if current_state == "menu":
        draw_button(play_button, "Hrát")
        draw_button(hs_button, "Žebříček")

    elif current_state == "input_name":
        draw_button(back_button, "Zpět")
        prompt = font.render("Napiš jméno a stiskni ENTER:", True, WHITE)
        name_txt = big_font.render(user_name + "_", True, YELLOW)
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 100))
        screen.blit(name_txt, (WIDTH//2 - name_txt.get_width()//2, HEIGHT//2))

    elif current_state == "highscore":
        draw_button(back_button, "Zpět")
        # Velký žlutý nápis
        title_surf = big_font.render("Nejlepší skóre", True, YELLOW)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 80))
        
        scores = load_high_scores()
        for i, (n, s) in enumerate(scores):
            txt = font.render(f"{i+1}. {n}: {s}", True, WHITE)
            screen.blit(txt, (WIDTH//2-100, 200 + i*40))

    elif current_state == "game":
        draw_grass()
        draw_button(back_button, "Zpět")

        if not game["dead"]:
            # Logika pohybu
            if game["dir"] != (0, 0):
                new_head = [game["pos"][0][0] + game["dir"][0], game["pos"][0][1] + game["dir"][1]]
                game["pos"].insert(0, new_head)
                if game["pos"][0][0] == game["food"][0] and game["pos"][0][1] == game["food"][1]:
                    game["score"] += 1
                    game["food"] = (random.randrange(0, (WIDTH-20)//20)*20, random.randrange(0, (HEIGHT-20)//20)*20)
                else:
                    game["pos"].pop()
                
                h = game["pos"][0]
                # Kolize
                if h[0]<0 or h[0]>=WIDTH or h[1]<0 or h[1]>=HEIGHT or h in game["pos"][1:]:
                    game["dead"] = True
                    save_high_score(user_name, game["score"])

            # Vykreslení jídla a hada
            pygame.draw.rect(screen, RED, (game["food"][0], game["food"][1], 20, 20))
            for i, seg in enumerate(game["pos"]):
                color = (0, 200, 0) if i == 0 else GREEN
                pygame.draw.rect(screen, color, (seg[0], seg[1], 20, 20))
            
            # Průběžné skóre
            screen.blit(font.render(f"Skóre: {game['score']}", True, WHITE), (WIDTH-150, 20))
        else:
            # Game Over Overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0,0))
            msg = big_font.render(f"KONEC, {user_name}!", True, RED)
            score_msg = font.render(f"Konečné skóre: {game['score']}", True, WHITE)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 50))
            screen.blit(score_msg, (WIDTH//2 - score_msg.get_width()//2, HEIGHT//2 + 50))

    pygame.display.flip()
    clock.tick(15)

pygame.quit()
sys.exit()