import webbrowser
import random
import requests
import pygame

API_BASE = "http://127.0.0.1:5000"
REGISTER_URL = API_BASE + "/register"

# ----- COLORS -----
COL_BG = (11, 16, 32)
COL_PANEL = (25, 30, 55)
COL_PANEL2 = (35, 40, 70)
COL_BORDER = (124, 92, 255)
COL_TEXT = (235, 240, 255)
COL_MUTED = (180, 190, 220)
COL_BAD = (255, 77, 77)
COL_GOOD = (25, 195, 125)


def draw_text(screen, font, text, x, y, color=COL_TEXT, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)
    return rect


class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, screen, font):
        pygame.draw.rect(screen, COL_PANEL2, self.rect, border_radius=14)
        pygame.draw.rect(screen, COL_BORDER, self.rect, width=2, border_radius=14)
        draw_text(screen, font, self.text, self.rect.centerx, self.rect.centery, color=COL_TEXT, center=True)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class InputBox:
    def __init__(self, x, y, w, h, placeholder="", password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.password = password
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                pass
            else:
                if len(self.text) < 24 and event.unicode.isprintable():
                    self.text += event.unicode

    def draw(self, screen, font):
        pygame.draw.rect(screen, COL_PANEL, self.rect, border_radius=12)

        border = COL_BORDER if self.active else (120, 130, 170)
        pygame.draw.rect(screen, border, self.rect, width=2, border_radius=12)

        shown = ("•" * len(self.text)) if self.password else self.text
        if shown:
            txt_surf = font.render(shown, True, COL_TEXT)
        else:
            txt_surf = font.render(self.placeholder, True, COL_MUTED)

        text_pos = (self.rect.x + 12, self.rect.y + 12)
        screen.blit(txt_surf, text_pos)

        if self.active:
            self.cursor_timer += 1
            if (self.cursor_timer // 30) % 2 == 0:
                cx = text_pos[0] + txt_surf.get_width() + 2
                cy = text_pos[1]
                pygame.draw.line(screen, COL_TEXT, (cx, cy), (cx, cy + txt_surf.get_height()), 2)


# ---------- API ----------
def app_login(username, password):
    r = requests.post(API_BASE + "/api/app-login", json={"username": username, "password": password}, timeout=6)
    if r.status_code == 200:
        data = r.json()
        return ("ok", data["token"], data.get("username", username))
    if r.status_code == 404:
        return ("no_user", None, None)
    return ("bad", None, None)


def post_score(token, score, apples, duration_ms):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        API_BASE + "/api/score",
        json={"score": score, "apples": apples, "duration_ms": duration_ms},
        headers=headers,
        timeout=6,
    )
    return r.status_code == 200


def wait_to_start(screen, username):
    clock = pygame.time.Clock()
    W, H = screen.get_size()
    font_big = pygame.font.SysFont("Segoe UI", 34, bold=True)
    font = pygame.font.SysFont("Segoe UI", 18)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "quit"
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return "start"

        screen.fill(COL_BG)

        panel = pygame.Rect(60, 180, W - 120, 260)
        pygame.draw.rect(screen, COL_PANEL, panel, border_radius=18)
        pygame.draw.rect(screen, COL_BORDER, panel, width=2, border_radius=18)

        draw_text(screen, font_big, "Připraveno ke hře", panel.centerx, panel.y + 55, center=True)
        draw_text(screen, font, f"Hráč: {username}", panel.centerx, panel.y + 110, color=COL_MUTED, center=True)
        draw_text(screen, font, "Stiskni SPACE nebo ENTER pro start", panel.centerx, panel.y + 160, color=COL_TEXT, center=True)
        draw_text(screen, font_small, "ESC = zpět / konec", panel.centerx, panel.y + 205, color=COL_MUTED, center=True)

        pygame.display.flip()
        clock.tick(60)


# ---------- Snake game ----------
def run_snake(screen, token, username):
    clock = pygame.time.Clock()
    W, H = screen.get_size()

    GRID = 24
    CELL = 20

    board_w = GRID * CELL
    board_h = GRID * CELL
    board_x = (W - board_w) // 2
    board_y = 150

    def cell_rect(cx, cy):
        return pygame.Rect(board_x + cx * CELL, board_y + cy * CELL, CELL - 1, CELL - 1)

    # state
    snake = [(8, 12), (7, 12), (6, 12)]
    dirx, diry = (1, 0)
    ndirx, ndiry = (1, 0)

    score = 0
    apples = 0
    tick_ms = 140
    last_tick = pygame.time.get_ticks()
    start = pygame.time.get_ticks()

    # food types
    APPLE = "APPLE"
    SPEED = "SPEED"
    SLOW = "SLOW"
    POISON = "POISON"

    def spawn_food():
        r = random.random()
        t = APPLE
        if 0.78 < r <= 0.90:
            t = SPEED
        elif 0.90 < r <= 0.98:
            t = SLOW
        elif r > 0.98:
            t = POISON

        while True:
            x = random.randrange(GRID)
            y = random.randrange(GRID)
            if (x, y) not in snake:
                return (x, y, t)

    food = spawn_food()

    font_big = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font = pygame.font.SysFont("Segoe UI", 18)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    alive = True
    saved_msg = ""
    saved_color = COL_MUTED

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "quit"

                if alive:
                    if e.key == pygame.K_UP and diry != 1:
                        ndirx, ndiry = (0, -1)
                    elif e.key == pygame.K_DOWN and diry != -1:
                        ndirx, ndiry = (0, 1)
                    elif e.key == pygame.K_LEFT and dirx != 1:
                        ndirx, ndiry = (-1, 0)
                    elif e.key == pygame.K_RIGHT and dirx != -1:
                        ndirx, ndiry = (1, 0)
                else:
                    if e.key == pygame.K_r:
                        return "restart"

        now = pygame.time.get_ticks()

        if alive and now - last_tick >= tick_ms:
            last_tick = now
            dirx, diry = ndirx, ndiry

            hx, hy = snake[0]
            nh = (hx + dirx, hy + diry)

            if nh[0] < 0 or nh[0] >= GRID or nh[1] < 0 or nh[1] >= GRID:
                alive = False
            elif nh in snake[:-1]:
                alive = False
            else:
                snake.insert(0, nh)

                fx, fy, ft = food
                if nh[0] == fx and nh[1] == fy:
                    score += 10
                    if ft == APPLE:
                        apples += 1
                    elif ft == SPEED:
                        tick_ms = max(60, tick_ms - 20)
                    elif ft == SLOW:
                        tick_ms = min(220, tick_ms + 20)
                    elif ft == POISON:
                        alive = False
                    food = spawn_food()
                else:
                    snake.pop()

            if not alive:
                duration_ms = now - start
                ok = post_score(token, score, apples, duration_ms)
                saved_msg = "Skóre uloženo ✅" if ok else "Uložení selhalo ❌"
                saved_color = COL_GOOD if ok else COL_BAD

        # ----- DRAW -----
        screen.fill(COL_BG)

        top_panel = pygame.Rect(40, 20, W - 80, 100)
        pygame.draw.rect(screen, COL_PANEL, top_panel, border_radius=16)
        pygame.draw.rect(screen, COL_BORDER, top_panel, width=2, border_radius=16)

        draw_text(screen, font_big, "Smart Snake", top_panel.x + 20, top_panel.y + 12, color=COL_TEXT)
        draw_text(screen, font, f"Hráč: {username}", top_panel.x + 20, top_panel.y + 50, color=COL_MUTED)
        draw_text(screen, font, f"Score: {score}   Apples: {apples}", top_panel.right - 280, top_panel.y + 50, color=COL_MUTED)

        board_frame = pygame.Rect(board_x - 8, board_y - 8, board_w + 16, board_h + 16)
        pygame.draw.rect(screen, COL_PANEL, board_frame, border_radius=18)
        pygame.draw.rect(screen, COL_BORDER, board_frame, width=2, border_radius=18)

        fx, fy, ft = food
        if ft == APPLE:
            fcol = (220, 60, 60)
        elif ft == SPEED:
            fcol = (255, 200, 40)
        elif ft == SLOW:
            fcol = (40, 200, 140)
        else:
            fcol = (160, 80, 220)
        pygame.draw.rect(screen, fcol, cell_rect(fx, fy), border_radius=6)

        for i, (sx, sy) in enumerate(snake):
            r = cell_rect(sx, sy)
            if i == 0:
                pygame.draw.rect(screen, (240, 245, 255), r, border_radius=6)
            else:
                pygame.draw.rect(screen, (80, 90, 140), r, border_radius=6)

        info_rect = pygame.Rect(board_x, board_y + board_h + 20, board_w, 70)
        pygame.draw.rect(screen, COL_PANEL, info_rect, border_radius=14)
        pygame.draw.rect(screen, COL_BORDER, info_rect, width=2, border_radius=14)
        draw_text(
            screen,
            font_small,
            "Šipky = pohyb | ESC = konec | R = restart po smrti",
            info_rect.centerx,
            info_rect.centery,
            color=COL_MUTED,
            center=True,
        )

        if not alive:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            draw_text(screen, font_big, "GAME OVER", W // 2, H // 2 - 30, center=True)
            draw_text(screen, font, saved_msg, W // 2, H // 2 + 6, color=saved_color, center=True)
            draw_text(screen, font, "Stiskni R pro restart", W // 2, H // 2 + 36, color=COL_MUTED, center=True)

        pygame.display.flip()
        clock.tick(60)


def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 700))
    pygame.display.set_caption("Smart Snake (Desktop App)")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("Segoe UI", 34, bold=True)
    font = pygame.font.SysFont("Segoe UI", 18)
    font_small = pygame.font.SysFont("Segoe UI", 14)

    W, H = screen.get_size()
    center_x = W // 2

    user_in = InputBox(center_x - 160, 260, 320, 48, "Username")
    pass_in = InputBox(center_x - 160, 320, 320, 48, "Password", password=True)

    btn_login = Button((center_x - 160, 390, 320, 52), "Přihlásit se")
    btn_register = Button((center_x - 160, 460, 320, 52), "Registrovat na webu")

    msg = ""
    msg_color = COL_MUTED

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return

            user_in.handle_event(e)
            pass_in.handle_event(e)

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_TAB:
                    user_in.active, pass_in.active = pass_in.active, user_in.active

            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_login.clicked(e.pos):
                    u = user_in.text.strip()
                    p = pass_in.text
                    if len(u) < 3 or len(p) < 1:
                        msg = "Vyplň username a password."
                        msg_color = COL_BAD
                    else:
                        try:
                            status, token, uname = app_login(u, p)
                            if status == "ok":
                                msg = "OK, přihlášeno."
                                msg_color = COL_GOOD

                                ready = wait_to_start(screen, uname)
                                if ready == "quit":
                                    pygame.quit()
                                    return

                                res = run_snake(screen, token, uname)
                                if res == "quit":
                                    pygame.quit()
                                    return
                                if res == "restart":
                                    continue

                            elif status == "no_user":
                                msg = "Účet neexistuje. Zaregistruj se na webu."
                                msg_color = COL_BAD
                            else:
                                msg = "Špatné heslo nebo login."
                                msg_color = COL_BAD

                        except Exception:
                            msg = "Server neběží. Spusť nejdřív: python app.py"
                            msg_color = COL_BAD

                if btn_register.clicked(e.pos):
                    webbrowser.open(REGISTER_URL)

        # ----- DRAW LOGIN -----
        screen.fill(COL_BG)

        panel = pygame.Rect(60, 60, W - 120, 160)
        pygame.draw.rect(screen, COL_PANEL, panel, border_radius=18)
        pygame.draw.rect(screen, COL_BORDER, panel, width=2, border_radius=18)

        draw_text(screen, font_big, "Smart Snake – Desktop Aplikace", panel.x + 20, panel.y + 18)
        draw_text(screen, font, "Přihlášení do aplikace (účty se vytváří na webu).", panel.x + 20, panel.y + 70, color=COL_MUTED)
        draw_text(screen, font_small, f"Registrace: {REGISTER_URL}", panel.x + 20, panel.y + 102, color=COL_MUTED)

        user_in.draw(screen, font)
        pass_in.draw(screen, font)
        btn_login.draw(screen, font)
        btn_register.draw(screen, font)

        if msg:
            draw_text(screen, font, msg, center_x, 540, color=msg_color, center=True)

        draw_text(screen, font_small, "Tip: TAB přepíná pole | Klikni do pole a piš.", center_x, 585, color=COL_MUTED, center=True)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()