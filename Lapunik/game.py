# game.py – Jádro a hlavní logický cyklus arkádové části Pixel Invaders
# Obsahuje veškerou fyziku, kolize, matematické modely objektů i samotné vykreslování herního světa.
import pygame, random, math
from datetime import datetime
from settings import *


def log_event(msg):
    """Zapíše herní událost s časovým razítkem do souboru game_log.txt."""
    try:
        with open("game_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] {msg}\n")
    except:
        pass


# ── Pixel-art matice sprite (konstanty na úrovni modulu) ─────────────────────
PLAYER_MATRIX = [
    [0,0,0,1,0,0,0],
    [0,1,1,1,1,1,0],
    [1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1],
]
ENEMY_MATRIX = [
    [0,0,1,0,0,1,0,0],
    [0,0,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,0],
    [1,1,0,1,1,0,1,1],
    [1,1,1,1,1,1,1,1],
    [0,1,0,1,1,0,1,0],
    [1,0,0,0,0,0,0,1],
    [0,1,0,0,0,0,1,0],
]
BOSS_MATRIX = [
    [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0],
    [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,1,1,0,0,1,1,1,1,1,0,0,1,1,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,1,1,1,0,0,0,1,1,1,0,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,1,1,1,1,0,1,1,1,0,1,1,1,1,0],
    [0,0,1,1,0,0,1,1,1,0,0,1,1,0,0],
    [0,0,1,0,0,0,0,1,0,0,0,0,1,0,0],
    [0,1,1,0,0,0,0,0,0,0,0,0,1,1,0],
]


class Game:
    """
    Třída zastřešující jeden herní pokus (run) hráče. Obsahuje jak vnitřní herní logiku (update), 
    tak fyzické zpracování vstupů (events) a rendering grafiky (draw).
    Při dosažení Game Over nebo ukončení vrací řízení zpět do kontextu menu.
    """
    def __init__(self, screen, user, db, start_level=1):
        self.screen  = screen
        self.virtual = pygame.Surface((800, 600))  # Veškerý pixel art se kreslí sem, pak se promítne na okno.
        self.user    = user
        self.db      = db
        self.clock   = pygame.time.Clock()

        self.font_big = pygame.font.Font(None, 60)
        self.font     = pygame.font.Font(None, 36)
        self.font_sm  = pygame.font.Font(None, 26)

        self.score         = 0
        self.high_score    = user.get("highscore", 0)
        self.level         = start_level
        self.weapon_level  = 1
        self.combo_mult    = 1
        self.last_hit_time = pygame.time.get_ticks()
        self.running       = True
        self.game_over     = False

        # Parallax hvězdné pozadí: [x, y, rychlost, velikost, barva]
        b = lambda: random.randint(50, 200)
        self.stars = [
            [random.randint(0,800), random.randint(0,600),
             random.uniform(0.5,2.5), random.choice([1,2]), (v:=b(), v, v)]
            for _ in range(120)
        ]
        self.init_game()

    def init_game(self):
        """Resetuje stav hry – volá se na začátku i při přechodu do dalšího levelu."""
        self.player_rect   = pygame.Rect(380, 540, 40, 40)
        self.player_hp     = PLAYER_HEALTH
        self.enemies       = []
        self.bullets       = []
        self.enemy_bullets = []
        self.pickups       = []
        self.particles     = []
        self.shake         = 0
        self.has_shield    = False
        self.dash_timer    = 0
        self.dash_cooldown = 0
        self.create_enemies()

    def spawn_enemy(self, x, y, hp, color, points):
        self.enemies.append({
            "rect": pygame.Rect(x, y, 40, 40),
            "x": float(x), "y": float(y),
            "hp": hp, "color": color,
            "points": points, "dir": 1, "is_boss": False,
        })

    def create_enemies(self):
        """Sestaví formaci nepřátel dle aktuálního levelu (cyklus stage 1–5)."""
        R = (5, (255, 60, 60),  SCORE_MEGA)
        O = (2, (255, 150, 0),  SCORE_STRONG)
        G = (1, (60, 255, 60),  SCORE_BASIC)
        layouts = {1:[G,G,G], 2:[O,G,G], 3:[R,O,G], 4:[R,R,O]}
        stage = (self.level - 1) % 5 + 1

        if stage == 5:  # Boss level
            cycle    = (self.level - 1) // 5
            boss_hp  = 100 + cycle * 50
            boss_pts = 5000 + cycle * 2000
            self.enemies.append({
                "rect": pygame.Rect(325, 50, 150, 100),
                "x": 325.0, "y": 50.0,
                "hp": boss_hp, "color": (200, 0, 255),
                "points": boss_pts, "dir": 1, "is_boss": True,
            })
            return
        for row, e_type in enumerate(layouts[stage]):
            for col in range(10):
                self.spawn_enemy(col * 70 + 50, row * 50 + 50, *e_type)

    def get_difficulty(self):
        """Vrátí (rychlost nepřátel, rychlost střel, šance na střelbu) dle levelu."""
        lvl = self.level - 1
        return (
            min(ENEMY_BASE_SPEED  + lvl * ENEMY_SPEED_SCALE,  3.5),
            min(ENEMY_BULLET_BASE_SPEED + lvl * ENEMY_BULLET_SCALE, 14.0),
            min(ENEMY_SHOOT_CHANCE_BASE + lvl * ENEMY_SHOOT_CHANCE_SCALE, 0.02),
        )

    def spawn_particles(self, x, y, color, amount=15):
        """Vytvoří partíklový efekt na zadané pozici."""
        for _ in range(amount):
            self.particles.append([
                x + 20, y + 20,
                random.uniform(-5, 5), random.uniform(-5, 5),
                random.randint(4, 8), color, random.randint(20, 45),
            ])

    def trigger_game_over(self):
        """Aktivuje konec hry, spustí efekty a uloží skóre."""
        self.game_over = True
        self.shake     = 30
        self.spawn_particles(self.player_rect.x, self.player_rect.y, (0, 200, 255), 40)
        log_event(f"Hráč '{self.user.get('username','?')}' prohrál v Levelu {self.level} se skóre {self.score}.")
        if self.user.get("id"):
            self.db.save_score(self.user["id"], self.score)

    # ── Vstup ────────────────────────────────────────────────────────────────

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True; self.running = False

            if event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    self.running = False
                if self.game_over and k == pygame.K_r:
                    self.score = 0; self.level = 1; self.game_over = False; self.init_game()
                if k == pygame.K_p and not self.game_over:
                    self.score += SCORE_LEVEL_DONE; self.level += 1; self.init_game()
                if k in (pygame.K_LSHIFT, pygame.K_RSHIFT) and not self.game_over and self.dash_cooldown <= 0:
                    self.dash_timer = 15; self.dash_cooldown = 90

                if k == pygame.K_SPACE and not self.game_over:
                    cx, top, l, r = (self.player_rect.centerx, self.player_rect.top,
                                     self.player_rect.left, self.player_rect.right)
                    if   self.weapon_level == 1: self.bullets += [pygame.Rect(cx-2, top, 4, 12)]
                    elif self.weapon_level == 2: self.bullets += [pygame.Rect(l+5, top, 4, 12), pygame.Rect(r-9, top, 4, 12)]
                    else:                        self.bullets += [pygame.Rect(cx-2, top, 4, 12), pygame.Rect(l, top+5, 4, 12), pygame.Rect(r-4, top+5, 4, 12)]

    # ── Logika ───────────────────────────────────────────────────────────────

    def update(self):
        """
        Zajišťuje klíčové běhové výpočty hry pro aktuální snímek framerate:
        - Mechaniku komba na základě času bez poškození
        - Fyziku a lineární pohyb veškerých projektilů a hvězdného pozadí
        - Algoritmus kolizí (AABB obdélníkové kolize pomocí colliderect)
        - Náhodné generování herních bonusů (pickupů)
        """
        enemy_spd, bullet_spd, shoot_ch = self.get_difficulty()

        # Kombo: roste čím déle hráč nebyl zasažen
        secs = (pygame.time.get_ticks() - self.last_hit_time) / 1000
        self.combo_mult = 3 if secs > 25 else 2 if secs > 10 else 1

        # Náhodný spawn pickupu (~jednou za 15 s)
        if random.random() < 0.0011:
            self.pickups.append({
                "rect": pygame.Rect(random.randint(20, 780), -20, 20, 20),
                "type": random.choice(["HEAL", "GUN", "GUN", "SHIELD"]),
                "spawn_time": pygame.time.get_ticks(),
            })

        # Parallax hvězdy
        for s in self.stars:
            s[1] += s[2]
            if s[1] > 600: s[1] = 0; s[0] = random.randint(0, 800)

        # Pokud game_over – animujeme jen zbylé částice a skončíme
        if self.game_over:
            for p in self.particles[:]:
                p[0] += p[2]; p[1] += p[3]; p[6] -= 1
                if p[6] <= 0: self.particles.remove(p)
            return

        # Čítače
        if self.shake > 0:        self.shake -= 1
        if self.dash_cooldown > 0: self.dash_cooldown -= 1

        # Pohyb hráče
        spd = PLAYER_SPEED * 3 if self.dash_timer > 0 else PLAYER_SPEED
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT]  or keys[pygame.K_a]) and self.player_rect.left  > 0:   self.player_rect.x -= spd
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.player_rect.right < 800:  self.player_rect.x += spd
        if self.dash_timer > 0:
            self.dash_timer -= 1
            if self.dash_timer % 3 == 0:
                self.spawn_particles(self.player_rect.x, self.player_rect.y, (0, 255, 255), 5)

        # Частice
        for p in self.particles[:]:
            p[0] += p[2]; p[1] += p[3]; p[6] -= 1
            if p[6] <= 0: self.particles.remove(p)

        # Hráčovy střely
        for b in self.bullets[:]:
            b.y -= BULLET_SPEED
            if b.bottom < 0: self.bullets.remove(b)

        # Nepřátelské střely + kolize s hráčem
        for eb in self.enemy_bullets[:]:
            eb.y += int(bullet_spd)
            if eb.top > 600:
                self.enemy_bullets.remove(eb)
            elif eb.colliderect(self.player_rect):
                if self.dash_timer > 0: continue
                self.enemy_bullets.remove(eb)
                if self.has_shield:
                    self.has_shield = False
                    self.spawn_particles(self.player_rect.x, self.player_rect.y, (0, 255, 255), 30)
                    continue
                self.player_hp -= 10
                self.last_hit_time = pygame.time.get_ticks()
                self.weapon_level  = 1
                self.shake         = 15
                self.spawn_particles(self.player_rect.x, self.player_rect.y, (255, 50, 50), 10)
                if self.player_hp <= 0: self.trigger_game_over()

        # Pickupy
        for p in self.pickups[:]:
            p["rect"].y += 3
            if p["rect"].top > 600:
                self.pickups.remove(p)
            elif p["rect"].colliderect(self.player_rect):
                t = p["type"]
                if   t == "HEAL":   self.player_hp    = min(100, self.player_hp + 25)
                elif t == "GUN":    self.weapon_level  = min(3, self.weapon_level + 1)
                elif t == "SHIELD": self.has_shield    = True
                self.pickups.remove(p)

        # Nepřátelé – pohyb, střelba, odraz
        for e in self.enemies:
            e["x"] += enemy_spd * e["dir"]
            e["rect"].x = int(e["x"])
            if random.random() < shoot_ch * (5 if e.get("is_boss") else 1):
                self.enemy_bullets.append(pygame.Rect(e["rect"].centerx-2, e["rect"].bottom, 4, 12))
                if e.get("is_boss"):
                    self.enemy_bullets += [
                        pygame.Rect(e["rect"].left+10,  e["rect"].bottom-20, 4, 12),
                        pygame.Rect(e["rect"].right-14, e["rect"].bottom-20, 4, 12),
                    ]
            if e["rect"].right >= 800 or e["rect"].left <= 0:
                e["dir"] *= -1
                if not e.get("is_boss"): e["y"] += 35; e["rect"].y = int(e["y"])
            if e["rect"].bottom >= 540:
                self.trigger_game_over()

        # Kolize střel hráče s nepřáteli
        for b in self.bullets[:]:
            for e in self.enemies[:]:
                if b.colliderect(e["rect"]):
                    if b in self.bullets: self.bullets.remove(b)
                    e["hp"] -= self.combo_mult
                    self.spawn_particles(b.x, b.y, (255, 150, 0), 5)
                    if e["hp"] <= 0:
                        self.score = max(self.score + e["points"] * self.combo_mult, 0)
                        self.high_score  = max(self.high_score, self.score)
                        self.player_hp   = min(100, self.player_hp + 1)  # life-steal
                        if random.random() < (0.60 if e.get("is_boss") else 0.20):
                            self.pickups.append({
                                "rect": pygame.Rect(e["rect"].centerx-10, e["rect"].centery-10, 20, 20),
                                "type": random.choice(["HEAL","GUN","GUN","SHIELD"]),
                                "spawn_time": pygame.time.get_ticks(),
                            })
                        self.spawn_particles(e["rect"].x, e["rect"].y, e["color"], 25)
                        self.enemies.remove(e)

        # Přechod na další level
        if not self.enemies:
            self.score      += SCORE_LEVEL_DONE
            self.high_score  = max(self.high_score, self.score)
            self.level      += 1
            self.init_game()

    # ── Kreslení ─────────────────────────────────────────────────────────────

    def draw_pixel_matrix(self, matrix, color, x, y, scale=5, offset=(0, 0)):
        """Vykreslí binární matici jako pixel art na self.virtual."""
        dx, dy = offset
        for r, row in enumerate(matrix):
            for c, val in enumerate(row):
                if val:
                    pygame.draw.rect(self.virtual, color,
                                     (x + c*scale + dx, y + r*scale + dy, scale, scale))

    def draw(self):
        """
        Grafický engine hry. Kreslení probíhá dvoufázově (hybridní rendering):
        1. Herní objekty jako lodičky, partikly a pick-upy se renderují na virtuální 800x600 
           Surface s použitím pevné pixelové mřížky simulující retro vzhled.
        2. Tzv. GUI/HUD prvky (Texty, skóre, HP) se ihned po vyškálování virtuálního plátna 
           renderují přímo na nativní rozlišení obrazovky (screen), aby zůstaly ostré a nebyly rozmazané.
        """
        w, h   = self.screen.get_size()
        scale  = min(w / 800, h / 600)
        new_w  = int(800 * scale); new_h = int(600 * scale)
        off_x  = (w - new_w) // 2;  off_y = (h - new_h) // 2
        sx = lambda x: int(x * scale) + off_x
        sy = lambda y: int(y * scale) + off_y

        # Scaled font cache
        if getattr(self, "_lscale", None) != scale:
            self._lscale   = scale
            self._sfont_big = pygame.font.Font(None, max(1, int(60 * scale)))
            self._sfont     = pygame.font.Font(None, max(1, int(36 * scale)))
            self._sfont_sm  = pygame.font.Font(None, max(1, int(26 * scale)))
        FB, F, FS = self._sfont_big, self._sfont, self._sfont_sm

        # ── Virtual surface (pixel art, BEZ textu) ───────────────────────────
        self.virtual.fill((5, 5, 18))
        ox = random.randint(-5, 5) if self.shake > 0 else 0
        oy = random.randint(-5, 5) if self.shake > 0 else 0

        for s in self.stars:
            pygame.draw.rect(self.virtual, s[4], (int(s[0]), int(s[1]), s[3], s[3]))

        for b in self.bullets:
            pygame.draw.rect(self.virtual, (200, 255, 255), (b.x+ox, b.y+oy, b.w, b.h))
        for eb in self.enemy_bullets:
            pygame.draw.rect(self.virtual, (255, 80, 80), (eb.x+ox, eb.y+oy, eb.w, eb.h))
        for p in self.particles:
            size = p[4] * (p[6] / 45)
            if size > 0:
                pygame.draw.rect(self.virtual, p[5], (int(p[0]+ox), int(p[1]+oy), int(size), int(size)))

        if not self.game_over:
            self.draw_pixel_matrix(PLAYER_MATRIX, (0, 200, 255), self.player_rect.x, self.player_rect.y+10, 6, (ox, oy))
        for e in self.enemies:
            m, sc = (BOSS_MATRIX, 10) if e.get("is_boss") else (ENEMY_MATRIX, 5)
            self.draw_pixel_matrix(m, e["color"], e["rect"].x, e["rect"].y, sc, (ox, oy))

        # Pickupy
        PICKUP_DEFS = {"HEAL": ((0,255,100), "H"), "GUN": ((255,200,0), "W")}
        for p in self.pickups:
            color, ch = PICKUP_DEFS.get(p["type"], ((0,255,255), "S"))
            pulse = abs(math.sin((pygame.time.get_ticks() - p.get("spawn_time",0)) / 150)) * 8
            cx, cy = p["rect"].centerx+ox, p["rect"].centery+oy
            pygame.draw.circle(self.virtual, color, (cx, cy), int(12+pulse), 2)
            pygame.draw.rect(self.virtual, color, (p["rect"].x+ox, p["rect"].y+oy, p["rect"].w, p["rect"].h), border_radius=4)
            self.virtual.blit(self.font_sm.render(ch, True, (0,0,0)), self.font_sm.render(ch, True, (0,0,0)).get_rect(center=(cx, cy)))

        # Štít
        if self.has_shield and not self.game_over:
            t_ms = pygame.time.get_ticks()
            pr   = 28 + int(abs(math.sin(t_ms / 200)) * 6)
            shld = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(shld, (0, 220, 255, 60),  (50, 50), pr+4)
            pygame.draw.circle(shld, (0, 255, 255, 180), (50, 50), pr, 3)
            self.virtual.blit(shld, (self.player_rect.centerx+ox-50, self.player_rect.centery+oy-50))

        # Top bar
        bar = pygame.Surface((800, 44), pygame.SRCALPHA); bar.fill((8, 8, 16, 200))
        self.virtual.blit(bar, (0, 0))
        pygame.draw.line(self.virtual, (0, 200, 255), (0, 43), (800, 43), 1)

        # HP bar
        hp_r = max(0, self.player_hp / 100)
        HX, HY, HW, HH = 12, 570, 160, 14
        pygame.draw.rect(self.virtual, (40,40,50),   (HX-1, HY-1, HW+2, HH+2), border_radius=6)
        if hp_r > 0:
            pygame.draw.rect(self.virtual, (int(255*(1-hp_r)), int(255*hp_r), 40),
                             (HX, HY, int(HW*hp_r), HH), border_radius=5)
        pygame.draw.rect(self.virtual, (80,100,110), (HX-1, HY-1, HW+2, HH+2), 1, border_radius=6)

        # Dash bar
        DX, DY, DW = 790, 570, 80
        d_col = (0,255,255) if self.dash_cooldown <= 0 else (180,60,60)
        cd_r  = max(0, 1.0 - self.dash_cooldown / 90.0)
        pygame.draw.rect(self.virtual, (40,40,50),   (DX-DW-1, DY-1, DW+2, 14), border_radius=5)
        if cd_r > 0:
            pygame.draw.rect(self.virtual, d_col, (DX-DW, DY, int(DW*cd_r), 12), border_radius=4)
        pygame.draw.rect(self.virtual, (80,100,110), (DX-DW-1, DY-1, DW+2, 14), 1, border_radius=5)

        # Game Over rámeček
        if self.game_over:
            ov = pygame.Surface((800, 600), pygame.SRCALPHA); ov.fill((0,0,10,200))
            self.virtual.blit(ov, (0, 0))
            bx, by = 160, 180
            glow = pygame.Surface((496, 256), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255,50,50,40), (0, 0, 496, 256), border_radius=14)
            self.virtual.blit(glow, (bx-8, by-8))
            pygame.draw.rect(self.virtual, (14,14,20),  (bx, by, 480, 240), border_radius=10)
            pygame.draw.rect(self.virtual, (200,40,40), (bx, by, 480, 240), 2, border_radius=10)

        # ── Scale virtual → screen ───────────────────────────────────────────
        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.transform.scale(self.virtual, (new_w, new_h)), (off_x, off_y))

        # ── Text přímo na screen (ostrý v každém rozlišení) ──────────────────
        blit = self.screen.blit
        blit(FS.render("SKÓRE", True, (100,150,200)), (sx(12), sy(4)))
        blit(F.render(f"{self.score:,}", True, (255,255,255)), (sx(12), sy(20)))
        rs = FS.render(f"REKORD  {self.high_score:,}", True, (200,160,60))
        blit(rs, rs.get_rect(centerx=sx(400), top=sy(14)))
        blit(FS.render("LEVEL", True, (100,150,200)), (sx(745), sy(4)))
        lv = F.render(str(self.level), True, (255,220,60))
        blit(lv, lv.get_rect(right=sx(795), top=sy(20)))
        blit(FS.render(f"HP  {self.player_hp}", True, (200,220,220)), (sx(HX), sy(HY-16)))
        dl = FS.render("SHIFT", True, d_col)
        blit(dl, dl.get_rect(right=sx(DX), top=sy(DY-16)))

        if self.combo_mult > 1:
            alpha = 180 + int(abs(math.sin(pygame.time.get_ticks() / 300)) * 75)
            col   = (255,210,0) if self.combo_mult == 2 else (255,60,60)
            cs    = FB.render(f"COMBO ×{self.combo_mult}", True, col)
            cs.set_alpha(alpha)
            blit(cs, cs.get_rect(centerx=sx(400), top=sy(52)))

        if self.game_over:
            bx, by = 160, 180
            new_rec = self.score >= self.high_score and self.score > 0
            for surf, pos in [
                (FB.render("GAME OVER", True, (230,60,60)),              {"centerx": sx(400), "top": sy(by+24)}),
                (F.render(f"Skóre:  {self.score:,}", True, (220,220,220)), {"centerx": sx(400), "top": sy(by+95)}),
                (FS.render("— nový rekord —" if new_rec else f"Rekord:  {self.high_score:,}", True, (200,160,60)), {"centerx": sx(400), "top": sy(by+130)}),
                (FS.render("[R]  Hrát znovu       [ESC]  Menu", True, (110,130,150)), {"centerx": sx(400), "top": sy(by+195)}),
            ]:
                blit(surf, surf.get_rect(**pos))

        pygame.display.flip()

    # ── Hlavní smyčka ────────────────────────────────────────────────────────

    def run(self):
        """
        Řídící smyčka herního pokusu oddělující čtení vstupů a aplikaci pravidel (update) 
        od grafického výstupu (draw). Řízena framerate omezovačem (clock.tick).
        """
        self.running = True
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        if self.user.get("id"):
            self.db.save_score(self.user["id"], self.score)
        return "MENU"
