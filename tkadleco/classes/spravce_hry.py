"""
spravce_hry.py - Správce herní logiky
Autor: [tvoje jméno]

Hlavní třída řídící celou herní logiku:
  - správa záchranářských jednotek a událostí na mapě
  - výpočet skóre: správné vyřešení = +1 bod, timeout = -1 bod (minimum 0)
  - plovoucí notifikace při vypršení události
  - komunikace se žebříčkem přes SpravceSite
"""

import pygame
from classes.mys import get_pos
import random
from classes.udalost import Udalost, TYPY_UDALOSTI
from classes.jednotka import Jednotka
from classes.mapa import Mapa
from classes.rozhrani import Rozhrani
from classes.sit import SpravceSite
from config import *


class SpravceHry:
    """
    Řídí herní logiku: generování událostí, pohyb jednotek, skóre a UI.

    Skórování:
      +1 bod  — správná jednotka dorazila k události včas
      -1 bod  — událost vypršela bez vyřešení (minimum skóre je 0)
    """

    def __init__(self, screen, obtiznost="Střední"):
        """
        Inicializace herního správce.

        Args:
            screen:     Pygame surface (game_surface z main.py, 1000×700)
            obtiznost:  'Lehká' | 'Střední' | 'Těžká'
        """
        self.screen = screen

        # Pomocné třídy pro vykreslování mapy a HUD
        self.mapa     = Mapa()
        self.rozhrani = Rozhrani()

        # Tři záchranářské jednotky umístěné na základně dole
        self.jednotky = [
            Jednotka("Policie", (120, 605), (0, 0)),
            Jednotka("Sanitka", (290, 605), (0, 0)),
            Jednotka("Hasiči",  (460, 605), (0, 0)),
        ]

        # Aktivní události na mapě (instance třídy Udalost)
        self.udalosti = []

        # Aktuálně vybraná jednotka (hráč na ni klikl)
        self.vybrana_jednotka = None

        # Skóre: +1 za vyřešení, -1 za timeout (neklesne pod 0)
        self.skore = 0

        # Plovoucí notifikace zobrazené přes herní plochu
        # Formát: {"text": str, "barva": tuple, "timer": int}
        self.notifikace = []

        self.obtiznost = obtiznost
        self.spawn_timer = 0
        # Počet snímků mezi automatickým generováním nových událostí
        self.interval_udalosti = self._ziskej_interval(obtiznost)

        # Herní časovač — hra trvá 1 minutu (60 000 ms)
        self.start_time  = pygame.time.get_ticks()
        self.trvani_hry  = 60_000
        self.konec_hry   = False

        # Lokální highscore pro aktuální sezení (neskladuje se na server)
        self.highscore = {"Lehká": 0, "Střední": 0, "Těžká": 0}

        # Síťová komunikace pro odesílání skóre na žebříček
        self.sit            = SpravceSite()
        self.hrac_jmeno     = ""
        self.skore_odeslano = False

        # Fonty pro end-game overlay
        self.font_velky = pygame.font.Font(None, 70)
        self.font_maly  = pygame.font.Font(None, 40)

        # Recty end-game UI — definované jednou, sdílené draw() i handle_event()
        self._tl_odeslat = pygame.Rect(WIDTH // 2 - 110, 340, 220, 52)
        self._tl_menu    = pygame.Rect(WIDTH // 2 - 110, 415, 220, 52)
        self._input_rect = pygame.Rect(WIDTH // 2 - 120, 280, 240, 44)

    # ------------------------------------------------------------------ #

    def _ziskej_interval(self, obtiznost):
        """
        Vrátí interval generování událostí podle obtížnosti.

        Returns:
            int: Počet snímků (při 60 FPS: 300=5s, 180=3s, 90=1.5s)
        """
        return {"Lehká": 300, "Střední": 180, "Těžká": 90}.get(obtiznost, 180)

    # ------------------------------------------------------------------ #

    def handle_event(self, udalost):
        """
        Zpracování vstupů od hráče (myš, klávesnice).

        Returns:
            'menu'    — hráč chce zpět do menu (ESC nebo tlačítko)
            None      — žádná akce
        """
        # ESC vždy vrátí do menu
        if udalost.type == pygame.KEYDOWN and udalost.key == pygame.K_ESCAPE:
            return "menu"

        # --- Konec hry: zadání jména a odeslání skóre ---
        if self.konec_hry:
            if udalost.type == pygame.KEYDOWN:
                # Mazání posledního znaku
                if udalost.key == pygame.K_BACKSPACE:
                    self.hrac_jmeno = self.hrac_jmeno[:-1]
                # Přidání znaku (max 12, pouze alfanumerické)
                elif len(self.hrac_jmeno) < 12 and udalost.unicode.isalnum():
                    self.hrac_jmeno += udalost.unicode

            if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
                poz = get_pos()
                # Odeslat skóre (pouze pokud je zadáno jméno a ještě nebylo odesláno)
                if not self.skore_odeslano and len(self.hrac_jmeno) > 0:
                    if self._tl_odeslat.collidepoint(poz):
                        self.sit.odesli_skore(self.hrac_jmeno, self.skore)
                        self.skore_odeslano = True
                # Zpět do menu
                if self._tl_menu.collidepoint(poz):
                    return "menu"
            return

        # --- Běžná hra: výběr jednotky a přiřazení k události ---
        if udalost.type == pygame.MOUSEBUTTONDOWN and udalost.button == 1:
            poz = get_pos()

            # Nejprve odznač všechny jednotky
            for j in self.jednotky:
                j._vybrana = False

            # Zjisti, zda hráč klikl na některou jednotku
            for j in self.jednotky:
                if j.je_kliknuta(poz):
                    self.vybrana_jednotka = j
                    j._vybrana = True
                    return

            # Zjisti, zda hráč klikl na událost a má vybranou jednotku
            for u in self.udalosti:
                if u.je_kliknuta(poz) and self.vybrana_jednotka:
                    # BUG FIX: Pokud tato jednotka již jede k jiné události,
                    # zruš její přiřazení tam — jinak by se vyřešily obě najednou.
                    for stara_u in self.udalosti:
                        if stara_u is not u and stara_u.prirazena_jednotka is self.vybrana_jednotka:
                            stara_u.prirazena_jednotka = None

                    # Přiřaď jednotku k nové události a vyšli ji
                    self.vybrana_jednotka.jede_na(u.pozice)
                    u.prirad_jednotku(self.vybrana_jednotka)
                    return

    # ------------------------------------------------------------------ #

    def update(self):
        """
        Herní logika volaná každý snímek (60× za sekundu).

        Pořadí:
          1. Kontrola konce hry (vypršení času)
          2. Generování nových událostí
          3. Aktualizace událostí + vyhodnocení skóre
          4. Pohyb jednotek
        """
        if self.konec_hry:
            return

        # 1. Konec hry po uplynutí herního času
        if pygame.time.get_ticks() - self.start_time >= self.trvani_hry:
            self.konec_hry = True
            # Ulož highscore pro aktuální obtížnost
            if self.skore > self.highscore[self.obtiznost]:
                self.highscore[self.obtiznost] = self.skore
            return

        # 2. Generuj novou událost po uplynutí intervalu
        self.spawn_timer += 1
        if self.spawn_timer >= self.interval_udalosti:
            self._spawn_nahodnou_udalost()
            self.spawn_timer = 0

        # 3. Aktualizuj každou aktivní událost
        for u in list(self.udalosti):
            u.update()
            if not u.aktivni:
                self.udalosti.remove(u)
                if u.prirazena_jednotka:
                    # Správná jednotka dorazila → přidej bod
                    self.skore += 1
                else:
                    # Timeout: nikdo nedorazil → odeber bod (min 0)
                    self.skore = max(0, self.skore - 1)
                    self._pridej_notifikaci("-1 bod!  Událost vypršela", CERVENA)

        # 4. Posuň všechny jednotky směrem k jejich cíli
        for j in self.jednotky:
            j.update()

    # ------------------------------------------------------------------ #

    def _pridej_notifikaci(self, text, barva):
        """
        Přidá plovoucí zprávu zobrazenou na herní ploše.

        Zpráva se zobrazí 2.5 sekundy a plynně zmizí.

        Args:
            text (str):   Text zprávy
            barva (tuple): RGB barva textu
        """
        self.notifikace.append({"text": text, "barva": barva, "timer": 120})

    def _vykresli_notifikace(self):
        """
        Vykreslí všechny aktivní plovoucí notifikace těsně pod HUD.

        Každá notifikace má tmavé barevné pozadí a bílý text,
        takže je čitelná přes libovolné pozadí mapy.
        Plynně mizí na konci životnosti (2 sekundy).

        Oprava: nepoužíváme SRCALPHA + set_alpha dohromady —
        tato kombinace v pygame způsobuje chybné vykreslení.
        Místo toho voláme set_alpha() přímo na klasické Surface.
        """
        font_notif = pygame.font.Font(None, 44)
        PAD = 10  # vnitřní odsazení textu od okraje panelu
        y   = 100  # těsně pod HUD panelem (který končí u y≈90)

        for notif in self.notifikace:
            # Alfa: plná po většinu doby, plynně klesá v posledních ~60 snímcích
            alfa = min(255, notif["timer"] * 4)

            surf = font_notif.render(notif["text"], True, BILA)
            panel_w = surf.get_width()  + PAD * 2
            panel_h = surf.get_height() + PAD

            # Barevné pozadí — klasická Surface, set_alpha funguje správně
            bg = pygame.Surface((panel_w, panel_h))
            bg.fill(notif["barva"])
            bg.set_alpha(int(alfa * 0.85))

            # Bílý text — taktéž klasická Surface
            surf.set_alpha(alfa)

            bx = WIDTH // 2 - panel_w // 2
            self.screen.blit(bg,   (bx, y))
            self.screen.blit(surf, (bx + PAD, y + PAD // 2))

            y += panel_h + 4
            notif["timer"] -= 1

        # Odstraň notifikace s vypršeným časovačem
        self.notifikace = [n for n in self.notifikace if n["timer"] > 0]

    # ------------------------------------------------------------------ #

    def draw(self):
        """
        Vykreslení celé herní scény.

        Pořadí vrstev (od spodu nahoru):
          1. Mapa (vymaže obrazovku)
          2. Události
          3. Jednotky
          4. HUD (skóre, počet událostí)
          5. Časomíra
          6. Spodní info panel
          7. Plovoucí notifikace
          8. End-game overlay (pouze při konci hry)
        """
        # 1. Mapa jako spodní vrstva (interně volá screen.fill)
        self.mapa.draw(self.screen)

        # 2. Aktivní události na mapě
        for u in self.udalosti:
            u.draw(self.screen)

        # 3. Záchranářské jednotky
        for j in self.jednotky:
            j.draw(self.screen)

        # 4. HUD overlay (skóre, počet událostí, nápověda ESC)
        self.rozhrani.draw(self.screen, len(self.udalosti), self.skore)

        if not self.konec_hry:
            # 5. Časomíra vpravo nahoře (červeně posledních 15 sekund)
            zbyle_ms   = max(0, self.trvani_hry - (pygame.time.get_ticks() - self.start_time))
            zbyle_s    = zbyle_ms // 1000
            barva_casu = CERVENA if zbyle_s < 15 else BILA
            cas_text   = self.font_maly.render(f"Čas: {zbyle_s}s", True, barva_casu)
            panel      = pygame.Surface((cas_text.get_width() + 16, 34), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 140))
            self.screen.blit(panel,    (WIDTH - cas_text.get_width() - 24, 44))
            self.screen.blit(cas_text, (WIDTH - cas_text.get_width() - 16, 50))

            # 6. Spodní info panel (název vybrané jednotky + legenda)
            self._vykresli_spodni_panel()

            # 7. Plovoucí notifikace (timeout = -1 bod apod.)
            self._vykresli_notifikace()

        if self.konec_hry:
            # 8. End-game overlay překryje vše ostatní
            self._vykresli_konec_hry()

    def _vykresli_spodni_panel(self):
        """
        Spodní informační panel:
          - název aktuálně vybrané jednotky
          - legenda typů událostí (typ → požadovaná jednotka)
        """
        font_info = pygame.font.Font(None, 28)

        # Název vybrané jednotky — zobrazí se nad základnou
        if self.vybrana_jednotka:
            txt   = font_info.render(f"Vybráno: {self.vybrana_jednotka.jmeno}", True, ZLUTA)
            panel = pygame.Surface((txt.get_width() + 20, 30), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 160))
            self.screen.blit(panel, (WIDTH // 2 - txt.get_width() // 2 - 10, HEIGHT - 150))
            self.screen.blit(txt,   (WIDTH // 2 - txt.get_width() // 2,       HEIGHT - 147))

        # Legenda — malá tabulka vpravo dole
        from classes.udalost import TYPY_UDALOSTI
        leg_font  = pygame.font.Font(None, 22)
        x_leg     = WIDTH - 220
        y_leg     = HEIGHT - 128
        leg_panel = pygame.Surface((210, len(TYPY_UDALOSTI) * 20 + 10), pygame.SRCALPHA)
        leg_panel.fill((0, 0, 0, 140))
        self.screen.blit(leg_panel, (x_leg - 5, y_leg - 5))
        for typ, info in TYPY_UDALOSTI.items():
            # Barevná tečka odpovídá barvě události
            pygame.draw.circle(self.screen, info["barva"], (x_leg + 6, y_leg + 7), 6)
            leg_txt = leg_font.render(f"{typ} → {info['vyzaduje']}", True, (200, 200, 200))
            self.screen.blit(leg_txt, (x_leg + 16, y_leg))
            y_leg += 20

    def _vykresli_konec_hry(self):
        """
        End-game overlay zobrazený po vypršení herního času.

        Obsahuje:
          - celkové skóre
          - nejlepší výsledek v dané obtížnosti
          - vstupní pole pro jméno hráče
          - tlačítko Odeslat skóre / Zpět do menu
        """
        # Poloprůhledný černý overlay přes celou herní plochu
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(210)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Nadpis
        t = self.font_velky.render("Konec hry!", True, BILA)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 80))

        # Celkové skóre (+1 za vyřešení, -1 za timeout)
        st = self.font_maly.render(f"Skóre: {self.skore} bodů", True, ZLUTA)
        self.screen.blit(st, (WIDTH // 2 - st.get_width() // 2, 155))

        # Nejlepší výsledek pro aktuální obtížnost
        hs_t = self.font_maly.render(
            f"Nejlepší ({self.obtiznost}): {self.highscore[self.obtiznost]}",
            True, (180, 180, 180))
        self.screen.blit(hs_t, (WIDTH // 2 - hs_t.get_width() // 2, 200))

        if not self.skore_odeslano:
            # Výzva k zadání jména
            vyzva = self.font_maly.render("Zadej své jméno:", True, BILA)
            self.screen.blit(vyzva, (WIDTH // 2 - vyzva.get_width() // 2, 245))

            # Vstupní pole — šedé pozadí + bílý rámeček
            pygame.draw.rect(self.screen, (60, 60, 60), self._input_rect, border_radius=6)
            pygame.draw.rect(self.screen, BILA,         self._input_rect, 2, border_radius=6)
            jmeno_surf = self.font_maly.render(self.hrac_jmeno + "|", True, BILA)
            self.screen.blit(jmeno_surf, (
                self._input_rect.centerx - jmeno_surf.get_width() // 2,
                self._input_rect.centery - jmeno_surf.get_height() // 2))

            # Tlačítko Odeslat — zezelená až po zadání jména
            barva_tl = ZELENA if len(self.hrac_jmeno) > 0 else (80, 80, 80)
            pygame.draw.rect(self.screen, barva_tl, self._tl_odeslat, border_radius=8)
            txt_o = self.font_maly.render("Odeslat skóre", True,
                                          CERNA if len(self.hrac_jmeno) > 0 else BILA)
            self.screen.blit(txt_o, (
                self._tl_odeslat.centerx - txt_o.get_width() // 2,
                self._tl_odeslat.centery - txt_o.get_height() // 2))
        else:
            # Potvrzení úspěšného odeslání
            ok = self.font_maly.render("Skóre úspěšně odesláno!", True, ZELENA)
            self.screen.blit(ok, (WIDTH // 2 - ok.get_width() // 2, 315))

        # Tlačítko Zpět do menu — vždy viditelné
        pygame.draw.rect(self.screen, CERVENA, self._tl_menu, border_radius=8)
        txt_m = self.font_maly.render("Zpět do menu", True, BILA)
        self.screen.blit(txt_m, (
            self._tl_menu.centerx - txt_m.get_width() // 2,
            self._tl_menu.centery - txt_m.get_height() // 2))

    def _spawn_nahodnou_udalost(self):
        """
        Vygeneruje náhodnou událost na náhodném místě herní mapy.

        Pozice je omezena okraji mapy (aby události nepadaly do základny dole).
        """
        x   = random.randint(100, WIDTH - 100)
        y   = random.randint(80,  HEIGHT - 200)
        typ = random.choice(list(TYPY_UDALOSTI.keys()))
        self.udalosti.append(Udalost(typ, (x, y)))
