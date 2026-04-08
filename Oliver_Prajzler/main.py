import pygame
import sys
import random
# Importujeme vše z našich modulů
from config import *
from database import *
from game_logic import *

# --- INICIALIZACE ---
pygame.init()
init_db() # Tato funkce teď inicializuje tabulky v MySQL na dbs.spskladno.cz
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hadík - Školní Online Edice")

font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 80)
clock = pygame.time.Clock()

# --- DEFINICE TLAČÍTEK ---
btn_back = pygame.Rect(20, 20, 120, 50)
btn_play = pygame.Rect(500, 250, 200, 50)
btn_shop = pygame.Rect(500, 320, 200, 50)
btn_hs = pygame.Rect(500, 390, 200, 50)

# Herní stavy
state = "startup"
user_name = ""
view_mode = "normal"
game = None

def draw_btn(rect, text, color=BLUE):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    txt = font.render(text, True, WHITE)
    screen.blit(txt, txt.get_rect(center=rect.center))

# --- HLAVNÍ SMYČKA ---
running = True
while running:
    now = pygame.time.get_ticks()
    screen.fill(DARK_GREEN) 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 1. ZADÁNÍ JMÉNA
        if state == "startup":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and user_name.strip():
                    state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    user_name = user_name[:-1]
                else:
                    if len(user_name) < 12:
                        user_name += event.unicode

        # 2. HLAVNÍ MENU
        elif state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            if btn_play.collidepoint(event.pos): state = "select"
            elif btn_shop.collidepoint(event.pos): state = "shop"
            elif btn_hs.collidepoint(event.pos): state = "highscore"

        # 3. VÝBĚR OBTÍŽNOSTI
        elif state == "select" and event.type == pygame.MOUSEBUTTONDOWN:
            # Načteme data o skinu ze školní DB
            p_data = get_player_data(user_name)
            s_color = SKINS[p_data["skin"]]
            
            if btn_back.collidepoint(event.pos): state = "menu"
            elif pygame.Rect(500,250,200,50).collidepoint(event.pos): 
                game = reset_game("easy", s_color); state = "game"
            elif pygame.Rect(500,320,200,50).collidepoint(event.pos): 
                game = reset_game("normal", s_color); state = "game"
            elif pygame.Rect(500,390,200,50).collidepoint(event.pos): 
                game = reset_game("hardcore", s_color); state = "game"

        # 4. OBCHOD (SHOP) - OPRAVENO (Bez sqlite3)
        elif state == "shop" and event.type == pygame.MOUSEBUTTONDOWN:
            if btn_back.collidepoint(event.pos): state = "menu"
            for i, (s_name, s_price) in enumerate(SKIN_PRICES.items()):
                if pygame.Rect(300, 150 + i*70, 200, 50).collidepoint(event.pos):
                    # Tato funkce v database.py vyřeší vše online přes MySQL
                    handle_skin_purchase(user_name, s_name, s_price)

        # 5. HRA
        elif state == "game":
            if event.type == pygame.MOUSEBUTTONDOWN and btn_back.collidepoint(event.pos):
                state = "menu"
            if not game["dead"] and event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_w, pygame.K_UP] and game["dir"] != (0, 20): game["dir"] = (0, -20)
                elif event.key in [pygame.K_s, pygame.K_DOWN] and game["dir"] != (0, -20): game["dir"] = (0, 20)
                elif event.key in [pygame.K_a, pygame.K_LEFT] and game["dir"] != (20, 0): game["dir"] = (-20, 0)
                elif event.key in [pygame.K_d, pygame.K_RIGHT] and game["dir"] != (-20, 0): game["dir"] = (20, 0)

        # 6. ŽEBŘÍČKY
        elif state == "highscore" and event.type == pygame.MOUSEBUTTONDOWN:
            if btn_back.collidepoint(event.pos): state = "menu"
            if pygame.Rect(400, 140, 120, 40).collidepoint(event.pos): view_mode = "easy"
            elif pygame.Rect(540, 140, 120, 40).collidepoint(event.pos): view_mode = "normal"
            elif pygame.Rect(680, 140, 120, 40).collidepoint(event.pos): view_mode = "hardcore"

    # --- VYKRESLOVÁNÍ ---
    if state == "startup":
        txt = font.render("Zadej své jméno pro přihlášení do DB:", True, WHITE)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 300))
        screen.blit(big_font.render(user_name + "_", True, YELLOW), (500, 380))

    elif state == "menu":
        p_data = get_player_data(user_name)
        screen.blit(font.render(f"Hráč: {user_name} | J: {p_data['apples']}", True, WHITE), (20, 20))
        draw_btn(btn_play, "Hrát"); draw_btn(btn_shop, "Obchod"); draw_btn(btn_hs, "Žebříčky")

    elif state == "select":
        draw_btn(btn_back, "Zpět")
        draw_btn(pygame.Rect(500,250,200,50), "Easy")
        draw_btn(pygame.Rect(500,320,200,50), "Normal")
        draw_btn(pygame.Rect(500,390,200,50), "Hardcore")

    elif state == "shop":
        p_data = get_player_data(user_name)
        draw_btn(btn_back, "Zpět")
        screen.blit(font.render(f"Máš: {p_data['apples']} J", True, YELLOW), (500, 50))
        # Zobrazení skinů
        for i, (s_name, s_price) in enumerate(SKIN_PRICES.items()):
            # Barva tlačítka podle toho, jestli je skin aktivní
            btn_color = GREEN if s_name == p_data["skin"] else BLUE
            draw_btn(pygame.Rect(300, 150+i*70, 200, 50), s_name, btn_color)
            screen.blit(font.render(f"Cena: {s_price} J", True, WHITE), (520, 165+i*70))
            pygame.draw.rect(screen, SKINS[s_name], (250, 160+i*70, 30, 30))

    elif state == "game":
        # Tráva
        for y in range(0, HEIGHT, 20):
            for x in range(0, WIDTH, 20):
                pygame.draw.rect(screen, LIGHT_GRASS if (x//20+y//20)%2==0 else DARK_GREEN, (x, y, 20, 20))
        
        draw_btn(btn_back, "Zpět")

        if not game["dead"]:
            if now > game["timeout"]: game["speed"] = game["base_speed"]
            
            # Power-upy
            if len(game["powerups"]) < 3 and random.random() < 0.05:
                game["powerups"].append({"pos": (random.randrange(0,60)*20, random.randrange(0,40)*20), "type": random.choice(["slow", "fast"]), "time": now})
            game["powerups"] = [p for p in game["powerups"] if now - p["time"] < 10000]

            # Pohyb hada
            if game["dir"] != (0,0):
                h = [game["pos"][0][0] + game["dir"][0], game["pos"][0][1] + game["dir"][1]]
                game["pos"].insert(0, h)
                
                # Snědení jablka
                if h[0] == game["food"][0] and h[1] == game["food"][1]:
                    game["score"] += 1
                    update_apples(user_name, 1) # Synchronizace do online DB
                    game["food"] = (random.randrange(0,60)*20, random.randrange(0,40)*20)
                else: 
                    game["pos"].pop()

                # Kolize s power-upy
                for p in game["powerups"][:]:
                    if h[0] == p["pos"][0] and h[1] == p["pos"][1]:
                        game["speed"] = game["base_speed"]//2 if p["type"]=="slow" else game["base_speed"]*2
                        game["timeout"] = now + 3000
                        game["powerups"].remove(p)

                # Smrt (Zdi, Tělo)
                if h[0]<0 or h[0]>=WIDTH or h[1]<0 or h[1]>=HEIGHT or h in game["pos"][1:]:
                    game["dead"] = True
                    save_high_score(user_name, game["score"], game["mode"]) # Uložení do online žebříčku

            # Vykreslení
            pygame.draw.rect(screen, RED, (game["food"][0], game["food"][1], 20, 20))
            for p in game["powerups"]:
                p_color = LIGHT_BLUE if p["type"]=="slow" else PURPLE
                pygame.draw.circle(screen, p_color, (p["pos"][0]+10, p["pos"][1]+10), 10)
            
            for i, s in enumerate(game["pos"]):
                color = game["skin_color"]
                if i == 0: color = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40)) # Hlava
                pygame.draw.rect(screen, color, (s[0], s[1], 20, 20))
                pygame.draw.rect(screen, BLACK, (s[0], s[1], 20, 20), 1) # Ohraničení
            
            screen.blit(font.render(f"Skóre: {game['score']}", True, WHITE), (1050, 20))
        else:
            screen.blit(big_font.render("KONEC!", True, RED), (WIDTH//2 - 100, HEIGHT//2))

    elif state == "highscore":
        draw_btn(btn_back, "Zpět")
        draw_btn(pygame.Rect(400, 140, 120, 40), "Easy", GREEN if view_mode=="easy" else BLUE)
        draw_btn(pygame.Rect(540, 140, 120, 40), "Normal", GREEN if view_mode=="normal" else BLUE)
        draw_btn(pygame.Rect(680, 140, 120, 40), "Hardcore", GREEN if view_mode=="hardcore" else BLUE)
        
        # Načtení online žebříčku
        scores = load_high_scores(view_mode)
        for i, (n, s) in enumerate(scores):
            screen.blit(font.render(f"{i+1}. {n}: {s}", True, WHITE), (500, 220 + i*40))

    pygame.display.flip()
    clock.tick(game["speed"] if state == "game" else 30)

pygame.quit()