# menu.py – Herní menu (přihlášení, registrace, nastavení) Pixel Invaders

import pygame, random, json
from datetime import datetime
from settings import *


def log_event(msg):
    try:
        with open("game_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] {msg}\n")
    except:
        pass


class Menu:
    """
    Obsluhuje interaktivní grafické uživatelské rozhraní mimo vlastní hru. 
    Zpracovává textové vstupy do formulářů pro registraci a přihlášení, vizuální stav 
    tlačítek, uložení nastavení rozlišení a spojení s databází.
    """
    def __init__(self, screen, db, has_save):
        self.screen    = screen
        self.virtual   = pygame.Surface((800, 600))
        self.db        = db
        self.has_save  = has_save
        self.clock     = pygame.time.Clock()
        self.state     = "MAIN"
        self.is_fullscreen = bool(self.screen.get_flags() & pygame.FULLSCREEN)

        # Formulářový stav (sdílený přihlášením i registrací)
        self._reset_form()

        # Scale tracking pro ostrý text v libovolném rozlišení
        self._scale = 1.0; self._off_x = 0; self._off_y = 0
        self._last_scale = None
        self._sfont_big  = pygame.font.Font(None, 74)
        self._sfont      = pygame.font.Font(None, 36)
        self._sfont_sm   = pygame.font.Font(None, 26)
        self._pending    = []  # text vykreslený přímo na screen

        # Parallax hvězdy
        b = lambda: random.randint(50, 150)
        self.stars = [
            [random.randint(0,800), random.randint(0,600),
             random.uniform(0.2,1.5), random.choice([1,2]), (v:=b(), v, v)]
            for _ in range(120)
        ]

    # ── Pomocné metody ────────────────────────────────────────────────────────

    def _reset_form(self):
        self.f_username = ""; self.f_password = ""; self.f_password2 = ""
        self.f_focus    = "username"; self.f_error = ""

    def _sx(self, x): return int(x * self._scale) + self._off_x
    def _sy(self, y): return int(y * self._scale) + self._off_y

    def change_resolution(self, width, height, fullscreen):
        """
        Dynamicky změní rozlišení a režim celoobrazovkového zobrazení 
        voláním display.set_mode. Následně tyto hodnoty zapíše do konfiguračního souboru 
        config.json (File I/O operace) pro trvalé uchování volby uživatele na příští spuštění.
        """
        self.screen = pygame.display.set_mode((0, 0) if fullscreen else (width, height),
                                              pygame.FULLSCREEN if fullscreen else 0)
        self.is_fullscreen = fullscreen
        try:
            with open("config.json", "w") as f:
                json.dump({"width": width, "height": height, "fullscreen": fullscreen}, f)
        except:
            pass

    # ── Vykreslovací pomocníci ────────────────────────────────────────────────

    def _blit(self, surf, pos):
        """Přidá surface do fronty pro vykreslení přímo na screen."""
        self._pending.append((surf, pos))

    def draw_button(self, text, cx, y, active=True, mpos=(0, 0), width=300):
        rect  = pygame.Rect(0, 0, width, 50); rect.center = (cx, y)
        hover = active and rect.collidepoint(mpos)
        pygame.draw.rect(self.virtual, (0,80,120) if hover else (10,20,30), rect, border_radius=4)
        pygame.draw.rect(self.virtual, (0,200,255) if active else (50,50,50), rect, 2, border_radius=4)
        surf = self._sfont.render(text, True, (255,255,255) if active else (100,100,100))
        self._blit(surf, surf.get_rect(center=(self._sx(rect.centerx), self._sy(rect.centery))))
        return rect, active

    def _shadow_text(self, text, font, color, cx, cy, offset=3):
        scx, scy = self._sx(cx), self._sy(cy)
        off = max(1, int(offset * self._scale))
        self._blit(font.render(text, True, (0,0,0)), font.render(text, True, (0,0,0)).get_rect(center=(scx+off, scy+off)))
        self._blit(font.render(text, True, color),   font.render(text, True, color).get_rect(center=(scx, scy)))

    def _draw_input(self, label, value, cx, y, focused, secret=False):
        lbl = self._sfont_sm.render(label, True, (160, 180, 200))
        self._blit(lbl, lbl.get_rect(centerx=self._sx(cx), bottom=self._sy(y - 6)))
        box = pygame.Rect(0, 0, 320, 46); box.center = (cx, y + 23)
        pygame.draw.rect(self.virtual, (10, 18, 30), box, border_radius=5)
        pygame.draw.rect(self.virtual, (0,210,255) if focused else (60,80,100), box, 2, border_radius=5)
        display = "●" * len(value) if secret else value
        ts = self._sfont.render(display, True, WHITE)
        tx, ty = self._sx(box.x + 14), self._sy(box.y + 10)
        self._blit(ts, (tx, ty))
        if focused and pygame.time.get_ticks() % 1000 < 500:
            cur = pygame.Surface((2, max(4, int(26 * self._scale)))); cur.fill((0, 200, 255))
            self._blit(cur, (tx + ts.get_width() + 2, ty))

    # ── Hlavní draw ───────────────────────────────────────────────────────────

    def draw(self, mpos):
        self._pending = []
        self.virtual.fill((5, 5, 18))

        # Hvězdy
        for s in self.stars:
            s[1] += s[2]
            if s[1] > 600: s[1] = 0; s[0] = random.randint(0, 800)
            pygame.draw.rect(self.virtual, s[4], (int(s[0]), int(s[1]), s[3], s[3]))

        self._shadow_text("PIXEL INVADERS", self._sfont_big, (0, 255, 255), 400, 100)
        buttons = {}

        if self.state == "MAIN":
            by = 200
            buttons["REGISTER"] = self.draw_button("Registrovat",  400, by,       True,           mpos)
            buttons["LOGIN"]    = self.draw_button("Přihlásit se", 400, by + 70,  True,           mpos)
            buttons["RESUME"]   = self.draw_button("Pokračovat",   400, by + 140, self.has_save,  mpos)
            buttons["OPTIONS"]  = self.draw_button("Možnosti",     400, by + 210, True,           mpos)
            buttons["QUIT"]     = self.draw_button("Konec",        400, by + 280, True,           mpos)

        elif self.state == "OPTIONS":
            by = 200
            buttons["RES_800"]    = self.draw_button("800x600 (Okno)",     400, by,       True, mpos)
            buttons["RES_1024"]   = self.draw_button("1024x768 (Okno)",    400, by + 70,  True, mpos)
            buttons["FULLSCREEN"] = self.draw_button("Fullscreen Zap/Vyp", 400, by + 140, True, mpos)
            buttons["BACK"]       = self.draw_button("Zpět",               400, by + 230, True, mpos)

        elif self.state == "REGISTER":
            self._shadow_text("Nový účet", self._sfont, (0, 220, 255), 400, 150)
            by = 200
            self._draw_input("Přezdívka",     self.f_username,  400, by,       self.f_focus == "username")
            self._draw_input("Heslo",         self.f_password,  400, by + 90,  self.f_focus == "password",  secret=True)
            self._draw_input("Potvrdit heslo",self.f_password2, 400, by + 180, self.f_focus == "password2", secret=True)
            buttons["DO_REGISTER"] = self.draw_button("Vytvořit účet", 400, by + 260, True, mpos)
            buttons["BACK"]        = self.draw_button("Zpět",          400, by + 320, True, mpos, width=160)
            hint = self._sfont_sm.render("Tab = přepnout pole   |   Enter = potvrdit", True, (100,120,140))
            self._blit(hint, hint.get_rect(centerx=self._sx(400), top=self._sy(by + 360)))
            if self.f_error: self._shadow_text(self.f_error, self._sfont_sm, (255, 70, 70), 400, by + 395)

        elif self.state == "LOGIN":
            self._shadow_text("Přihlášení", self._sfont, (0, 220, 255), 400, 150)
            by = 220
            self._draw_input("Přezdívka", self.f_username, 400, by,       self.f_focus == "username")
            self._draw_input("Heslo",     self.f_password, 400, by + 90,  self.f_focus == "password", secret=True)
            buttons["DO_LOGIN"] = self.draw_button("Přihlásit se", 400, by + 180, True, mpos)
            buttons["BACK"]     = self.draw_button("Zpět",         400, by + 240, True, mpos, width=160)
            hint = self._sfont_sm.render("Tab = přepnout pole   |   Enter = potvrdit", True, (100,120,140))
            self._blit(hint, hint.get_rect(centerx=self._sx(400), top=self._sy(by + 290)))
            if self.f_error: self._shadow_text(self.f_error, self._sfont_sm, (255, 70, 70), 400, by + 325)

        db_txt = "✅ Databáze Připojena" if self.db.connection else "⚠ Databáze Offline"
        self._shadow_text(db_txt, self._sfont_sm, (60,255,60) if self.db.connection else (255,150,0), 400, 570)
        return buttons

    # ── Vstupní logika ────────────────────────────────────────────────────────

    def _handle_text_input(self, event, fields):
        """Zpracuje stisk klávesy v textovém poli."""
        if event.key == pygame.K_TAB:
            self.f_focus = fields[(fields.index(self.f_focus) + 1) % len(fields)]
            return
        self.f_error = ""
        if event.key == pygame.K_BACKSPACE:
            if   self.f_focus == "username":  self.f_username  = self.f_username[:-1]
            elif self.f_focus == "password":  self.f_password  = self.f_password[:-1]
            elif self.f_focus == "password2": self.f_password2 = self.f_password2[:-1]
        elif event.unicode.isprintable():
            if   self.f_focus == "username"  and len(self.f_username)  < 15: self.f_username  += event.unicode
            elif self.f_focus == "password"  and len(self.f_password)  < 30: self.f_password  += event.unicode
            elif self.f_focus == "password2" and len(self.f_password2) < 30: self.f_password2 += event.unicode

    def _try_register(self):
        name, pw, pw2 = self.f_username.strip(), self.f_password, self.f_password2
        if len(name) < 3:   self.f_error = "Přezdívka musí mít aspoň 3 znaky.";  return None
        if len(pw)   < 4:   self.f_error = "Heslo musí mít aspoň 4 znaky.";      return None
        if pw != pw2:        self.f_error = "Hesla se neshodují.";                 return None
        if not self.db.register_user(name, pw):
            self.f_error = "Přezdívka je již obsazena.";                          return None
        log_event(f"Hráč '{name}' úspěšně zaregistrován.")
        return self.db.get_user(name)

    def _try_login(self):
        name, pw = self.f_username.strip(), self.f_password
        if not name or not pw: self.f_error = "Vyplňte přezdívku i heslo."; return None
        user = self.db.login_user(name, pw)
        if user is None:       self.f_error = "Špatná přezdívka nebo heslo."; return None
        log_event(f"Hráč '{name}' se přihlásil.")
        return user

    # ── Hlavní smyčka ─────────────────────────────────────────────────────────

    def run(self):
        while True:
            self.clock.tick(FPS)

            # Scale pro aktuální velikost okna
            w, h   = self.screen.get_size()
            scale  = min(w / 800, h / 600)
            new_w  = int(800 * scale); new_h = int(600 * scale)
            off_x  = (w - new_w) // 2;  off_y = (h - new_h) // 2
            self._scale = scale; self._off_x = off_x; self._off_y = off_y

            if self._last_scale != scale:
                self._last_scale = scale
                self._sfont_big  = pygame.font.Font(None, max(1, int(74 * scale)))
                self._sfont      = pygame.font.Font(None, max(1, int(36 * scale)))
                self._sfont_sm   = pygame.font.Font(None, max(1, int(26 * scale)))

            mx, my  = pygame.mouse.get_pos()
            mpos    = ((mx - off_x) / scale, (my - off_y) / scale)
            buttons = self.draw(mpos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return ("QUIT", None)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "MAIN":
                        for key, (rect, active) in buttons.items():
                            if active and rect.collidepoint(mpos):
                                if   key == "QUIT":     return ("QUIT", None)
                                elif key == "RESUME":   return ("RESUME", None)
                                elif key == "OPTIONS":  self.state = "OPTIONS"
                                elif key == "REGISTER": self._reset_form(); self.state = "REGISTER"
                                elif key == "LOGIN":    self._reset_form(); self.state = "LOGIN"

                    elif self.state == "OPTIONS":
                        for key, (rect, active) in buttons.items():
                            if active and rect.collidepoint(mpos):
                                if   key == "BACK":        self.state = "MAIN"
                                elif key == "RES_800":     self.change_resolution(800,  600, False)
                                elif key == "RES_1024":    self.change_resolution(1024, 768, False)
                                elif key == "FULLSCREEN":
                                    self.change_resolution(0, 0, not self.is_fullscreen) if self.is_fullscreen \
                                    else self.change_resolution(0, 0, True)

                    elif self.state == "REGISTER":
                        for key, (rect, active) in buttons.items():
                            if active and rect.collidepoint(mpos):
                                if   key == "BACK":        self.state = "MAIN"
                                elif key == "DO_REGISTER":
                                    user = self._try_register()
                                    if user: return ("NEW", user, 1)
                        for field, fy in [("username", 200), ("password", 290), ("password2", 380)]:
                            if pygame.Rect(240, fy, 320, 46).collidepoint(mpos): self.f_focus = field

                    elif self.state == "LOGIN":
                        for key, (rect, active) in buttons.items():
                            if active and rect.collidepoint(mpos):
                                if   key == "BACK":     self.state = "MAIN"
                                elif key == "DO_LOGIN":
                                    user = self._try_login()
                                    if user: return ("NEW", user, 1)
                        for field, fy in [("username", 220), ("password", 310)]:
                            if pygame.Rect(240, fy, 320, 46).collidepoint(mpos): self.f_focus = field

                elif event.type == pygame.KEYDOWN:
                    if self.state == "REGISTER":
                        if   event.key == pygame.K_ESCAPE: self.state = "MAIN"
                        elif event.key == pygame.K_RETURN:
                            user = self._try_register()
                            if user: return ("NEW", user, 1)
                        else: self._handle_text_input(event, ["username", "password", "password2"])

                    elif self.state == "LOGIN":
                        if   event.key == pygame.K_ESCAPE: self.state = "MAIN"
                        elif event.key == pygame.K_RETURN:
                            user = self._try_login()
                            if user: return ("NEW", user, 1)
                        else: self._handle_text_input(event, ["username", "password"])

            # Render
            self.screen.fill((0, 0, 0))
            self.screen.blit(pygame.transform.scale(self.virtual, (new_w, new_h)), (off_x, off_y))
            for surf, pos in self._pending:
                self.screen.blit(surf, pos)
            pygame.display.flip()
