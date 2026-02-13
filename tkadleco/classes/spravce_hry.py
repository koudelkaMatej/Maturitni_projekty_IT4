import pygame
import random
from .udalost import Udalost
from .jednotka import Jednotka
from .mapa import Mapa
from .rozhrani import Rozhrani
from .sit import SpravceSite
from config import *

class SpravceHry:
    def __init__(self, screen, obtiznost="Střední"):
        self.screen = screen
        self.mapa = Mapa()
        self.rozhrani = Rozhrani()
        self.jednotky = [
            Jednotka("Policie", (100, 600), (0, 0), (0, 0, 255)),
            Jednotka("Hasiči", (200, 600), (0, 0), (255, 0, 0)),
            Jednotka("Sanitka", (300, 600), (0, 0), (255, 255, 255))
        ]
        self.udalosti = []
        self.vybrana_jednotka = None
        self.skore = 0

        self.obtiznost = obtiznost
        self.spawn_timer = 0
        self.interval_udalosti = self.ziskej_interval(obtiznost)

        self.start_time = pygame.time.get_ticks()
        self.trvani_hry = 10_000 
        self.konec_hry = False

        self.highscore = {"Lehká":0, "Střední":0, "Těžká":0}

        self.sit = SpravceSite()
        self.hrac_jmeno = ""
        self.skore_odeslano = False

        try:
            self.sirena = pygame.mixer.Sound("assets/siren.wav")
        except:
            self.sirena = None

        # Fonty
        self.font_velky = pygame.font.Font(None, 70)
        self.font_maly = pygame.font.Font(None, 40)

    # --- TOTO JE TA FUNKCE, KTERÁ CHYBĚLA ---
    def ziskej_interval(self, obtiznost):
        if obtiznost == "Lehká":
            return 300
        elif obtiznost == "Střední":
            return 180
        elif obtiznost == "Těžká":
            return 90
        return 180
    # ----------------------------------------

    def handle_event(self, udalost):
        if udalost.type == pygame.KEYDOWN and udalost.key == pygame.K_ESCAPE:
            return "menu"

        # --- LOGIKA KONCE HRY (Zadávání jména) ---
        if self.konec_hry:
            # Psaní jména
            if udalost.type == pygame.KEYDOWN:
                if udalost.key == pygame.K_BACKSPACE:
                    self.hrac_jmeno = self.hrac_jmeno[:-1]
                else:
                    # Jen písmena a čísla, max 12 znaků
                    if len(self.hrac_jmeno) < 12 and udalost.unicode.isalnum():
                        self.hrac_jmeno += udalost.unicode
            
            # Klikání na tlačítka
            if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
                poz = pygame.mouse.get_pos()
                
                # Tlačítko ODESLAT SKÓRE (souřadnice 300, 300)
                if not self.skore_odeslano and len(self.hrac_jmeno) > 0:
                     if pygame.Rect(300, 300, 200, 50).collidepoint(poz):
                        print(f"Odesílám: {self.hrac_jmeno} - {self.skore}")
                        self.sit.odesli_skore(self.hrac_jmeno, self.skore)
                        self.skore_odeslano = True

                # Tlačítko ZPĚT DO MENU (souřadnice 300, 400)
                if pygame.Rect(300, 400, 200, 50).collidepoint(poz):
                    return "menu"
            return 
        # -----------------------------------------

        # --- LOGIKA BĚŽNÉ HRY ---
        if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
            poz = pygame.mouse.get_pos()

            # Vybrat jednotku
            for j in self.jednotky:
                if j.je_kliknuta(poz):
                    self.vybrana_jednotka = j
                    return

            # Klik na událost (poslat jednotku)
            for u in self.udalosti:
                if u.je_kliknuta(poz):
                    if self.vybrana_jednotka:
                        self.vybrana_jednotka.jede_na(u.pozice)
                        u.prirad_jednotku(self.vybrana_jednotka)
                        if self.sirena:
                            self.sirena.play()
            return

    def update(self):
        if self.konec_hry:
            return

        cas_aktualni = pygame.time.get_ticks()
        # Kontrola času
        if cas_aktualni - self.start_time >= self.trvani_hry:
            self.konec_hry = True
            if self.skore > self.highscore[self.obtiznost]:
                self.highscore[self.obtiznost] = self.skore
            return

        # Generování událostí
        self.spawn_timer += 1
        if self.spawn_timer >= self.interval_udalosti:
            self.spawn_nahodnou_udalost()
            self.spawn_timer = 0

        # Aktualizace událostí
        for u in list(self.udalosti):
            u.update()
            if not u.aktivni:
                self.udalosti.remove(u)
                self.skore += 1

        # Aktualizace jednotek
        for j in self.jednotky:
            j.update()

    def draw(self):
        # Vykreslení hry
        self.mapa.draw(self.screen)
        for u in self.udalosti:
            u.draw(self.screen)
        for j in self.jednotky:
            j.draw(self.screen)
        self.rozhrani.draw(self.screen, len(self.udalosti), self.skore)

        # Časovač
        if not self.konec_hry:
            cas_aktualni = pygame.time.get_ticks()
            zbyle_ms = max(0, self.trvani_hry - (cas_aktualni - self.start_time))
            zbyle_s = zbyle_ms // 1000
            cas_text = self.font_maly.render(f"Čas: {zbyle_s}s", True, BILA)
            self.screen.blit(cas_text, (WIDTH - 150, 20))

        # --- VYKRESLENÍ KONCE HRY (OVERLAY) ---
        if self.konec_hry:
            # Průhledné pozadí
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0,0,0))
            self.screen.blit(overlay, (0,0))

            # Nadpisy
            text = self.font_velky.render("Konec hry!", True, BILA)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, 100))

            skore_text = self.font_maly.render(f"Tvé skóre: {self.skore}", True, ZLUTA)
            self.screen.blit(skore_text, (WIDTH//2 - skore_text.get_width()//2, 160))

            # --- INPUT BOX PRO JMÉNO ---
            if not self.skore_odeslano:
                vyzva = self.font_maly.render("Zadej své jméno:", True, BILA)
                self.screen.blit(vyzva, (WIDTH//2 - vyzva.get_width()//2, 210))
                
                # Rámeček
                pygame.draw.rect(self.screen, BILA, (WIDTH//2 - 100, 250, 200, 40), 2)
                # Samotné jméno
                jmeno_text = self.font_maly.render(self.hrac_jmeno, True, BILA)
                self.screen.blit(jmeno_text, (WIDTH//2 - jmeno_text.get_width()//2, 258))

                # Tlačítko ODESLAT
                tl_odeslat = pygame.Rect(300, 300, 200, 50)
                # Zelené jen když máme jméno
                barva_tl = ZELENA if len(self.hrac_jmeno) > 0 else SEDA
                pygame.draw.rect(self.screen, barva_tl, tl_odeslat)
                txt_odeslat = self.font_maly.render("Odeslat", True, CERNA)
                self.screen.blit(txt_odeslat, (tl_odeslat.centerx - txt_odeslat.get_width()//2, tl_odeslat.centery - txt_odeslat.get_height()//2))
            
            else:
                # Zpráva po odeslání
                info = self.font_maly.render("Skóre úspěšně odesláno!", True, ZELENA)
                self.screen.blit(info, (WIDTH//2 - info.get_width()//2, 250))

            # Tlačítko MENU
            tl_menu = pygame.Rect(300, 400, 200, 50)
            pygame.draw.rect(self.screen, CERVENA, tl_menu)
            txt_menu = self.font_maly.render("Menu", True, CERNA)
            self.screen.blit(txt_menu, (tl_menu.centerx - txt_menu.get_width()//2, tl_menu.centery - txt_menu.get_height()//2))

    def spawn_nahodnou_udalost(self):
        x = random.randint(100, 900)
        y = random.randint(100, 500)
        typ = random.choice(["požár", "nehoda", "krádež"])
        self.udalosti.append(Udalost(typ, (x, y)))