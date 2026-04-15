# settings.py – Globální konstanty a nastavení hry Pixel Invaders
# Všechny stěžejní balanční a vizuální parametry jsou definovány centrálně na tomto místě.
# Úprava jediné konstanty (např. rychlost pohybu, body, fps) se automaticky a bezpečně
# zpropaguje mapováním napříč celým herním kódem.
# ── Okno & výkon ────────────────────────────────────────────────
SCREEN_WIDTH  = 800    # Šířka virtuálního herního plátna (px)
SCREEN_HEIGHT = 600    # Výška virtuálního herního plátna (px)
FPS           = 60     # Maximální počet snímků za sekundu

# ── Barvy (RGB) ─────────────────────────────────────────────────
WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0)
RED          = (255, 0,   0)
GREEN        = (0,   255, 0)
BLUE         = (0,   0,   255)
YELLOW       = (255, 255, 0)
ORANGE       = (255, 165, 0)
GRAY         = (128, 128, 128)
DARK_GREEN   = (0,   80,  0)
FOREST_GREEN = (34,  139, 34)
BROWN        = (139, 69,  19)
PURPLE       = (128, 0,   128)

# ── Hráč ────────────────────────────────────────────────────────
PLAYER_SPEED          = 5     # Počet pixelů pohybu za snímek
PLAYER_HEALTH         = 100   # Počáteční životy hráče
PLAYER_SHOOT_COOLDOWN = 400   # Minimální prodleva mezi výstřely (ms)

# ── Nepřátelé – dynamická obtížnost ─────────────────────────────
# Rychlost a střelba se stupňují s každým levelem; hard-capy zabrání nehratelnosti
ENEMY_BASE_SPEED  = 0.3    # Vodorovná rychlost v Levelu 1 (px/snímek)
ENEMY_SPEED_SCALE = 0.2    # Přírůstek rychlosti za každý level

ENEMY_ROWS = 3   # Počet řad nepřátel (pro referenci layoutu)
ENEMY_COLS = 8   # Počet sloupců nepřátel (pro referenci layoutu)

# ── Střely ──────────────────────────────────────────────────────
BULLET_SPEED             = 8       # Rychlost hráčovy střely (px/snímek)
ENEMY_BULLET_BASE_SPEED  = 4       # Základní rychlost nepřátelské střely v Levelu 1
ENEMY_BULLET_SCALE       = 0.5     # Přírůstek rychlosti za každý level
ENEMY_SHOOT_CHANCE_BASE  = 0.001   # Pravděpodobnost výstřelu v Levelu 1 (per snímek)
ENEMY_SHOOT_CHANCE_SCALE = 0.0008  # Přírůstek pravděpodobnosti za každý level

# ── Bodování ────────────────────────────────────────────────────
SCORE_BASIC      = 10    # Body za základního nepřítele (zelený)
SCORE_STRONG     = 20    # Body za silného nepřítele (oranžový)
SCORE_MEGA       = 50    # Body za mega nepřítele (červený)
SCORE_LEVEL_DONE = 200   # Bonus za dokončení levelu