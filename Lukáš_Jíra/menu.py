import pygame
import sys
import os
import math
import array
import hra
import databaze
import web


pygame.init()
databaze.vytvorit_tabulku()


SIRKA = 360
VYSKA = 640
okno = pygame.display.set_mode((SIRKA, VYSKA))
pygame.display.set_caption("Maturitní Projekt - Menu")


BILA = (255, 255, 255)
CERNA = (0, 0, 0)
ZELENA = (80, 200, 120); SVETLE_ZELENA = (100, 255, 150)
ORANZOVA = (255, 165, 0); SVETLE_ORANZOVA = (255, 200, 100)
CERVENA = (200, 50, 50); SVETLE_CERVENA = (255, 100, 100)
MODRA = (100, 149, 237)
ZLUTA = (255, 255, 0)


font_velky = pygame.font.SysFont("Comic Sans MS", 50, bold=True)
font_tlacitka = pygame.font.SysFont("Arial", 30, bold=True)
font_mezi = pygame.font.SysFont("Arial", 28)
font_maly = pygame.font.SysFont("Arial", 20)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "Obrazky")
menu_music_channel = None
menu_music_sound = None


def image_path(filename):
    return os.path.join(IMAGES_DIR, filename)


def _generate_ambient_loop():
    sample_rate = 44100
    notes = [(220, 0.6), (262, 0.6), (294, 0.7), (262, 0.6)]
    volume = 0.03
    data = array.array("h")
    for frequency, seconds in notes:
        total = int(sample_rate * seconds)
        fade = int(total * 0.12)
        for i in range(total):
            envelope = 1.0
            if i < fade:
                envelope = i / max(1, fade)
            elif i > total - fade:
                envelope = (total - i) / max(1, fade)
            sample = int(
                32767
                * volume
                * envelope
                * math.sin((2 * math.pi * frequency * i) / sample_rate)
            )
            data.append(sample)
        pause = int(sample_rate * 0.08)
        for _ in range(pause):
            data.append(0)
    return pygame.mixer.Sound(buffer=data.tobytes())


def start_menu_music():
    global menu_music_channel, menu_music_sound
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
        if menu_music_sound is None:
            menu_music_sound = _generate_ambient_loop()
        if menu_music_channel is None:
            menu_music_channel = pygame.mixer.Channel(1)
        menu_music_channel.set_volume(0.22)
        if not menu_music_channel.get_busy():
            menu_music_channel.play(menu_music_sound, loops=-1)
    except Exception:
        menu_music_channel = None


def stop_menu_music():
    global menu_music_channel
    if menu_music_channel:
        menu_music_channel.stop()


try:
    pozadi_img = pygame.image.load(image_path("flappybirdbg.png"))
    pozadi_img = pygame.transform.scale(pozadi_img, (SIRKA, VYSKA))
    ptak_img = pygame.image.load(image_path("redbird-midflap.png"))
    ptak_img = pygame.transform.scale(ptak_img, (60, 45))
except:
    pozadi_img = pygame.Surface((SIRKA, VYSKA)); pozadi_img.fill(MODRA)
    ptak_img = pygame.Surface((60, 45)); ptak_img.fill(ZLUTA)


def napis(text, font, y, barva=BILA):
    img = font.render(text, True, barva)
    rect = img.get_rect(center=(SIRKA/2, y))
    okno.blit(img, rect)


def nakresli_tlacitko(text, x, y, sirka, vyska, barva_neaktivni, barva_aktivni):
    mys_x, mys_y = pygame.mouse.get_pos()
    kliknuti = pygame.mouse.get_pressed()
    tlacitko_rect = pygame.Rect(x, y, sirka, vyska)
    zmacknuto = False


    if tlacitko_rect.collidepoint(mys_x, mys_y):
        pygame.draw.rect(okno, barva_aktivni, tlacitko_rect, border_radius=15)
        if kliknuti[0] == 1:
            zmacknuto = True
    else:
        pygame.draw.rect(okno, barva_neaktivni, tlacitko_rect, border_radius=15)


    max_text_width = sirka - 16
    font_size = 30
    btn_font = pygame.font.SysFont("Arial", font_size, bold=True)
    text_surf = btn_font.render(text, True, BILA)
    while text_surf.get_width() > max_text_width and font_size > 16:
        font_size -= 1
        btn_font = pygame.font.SysFont("Arial", font_size, bold=True)
        text_surf = btn_font.render(text, True, BILA)
    text_rect = text_surf.get_rect(center=tlacitko_rect.center)
    okno.blit(text_surf, text_rect)
    return zmacknuto


# --- NOVÉ: FUNKCE PRO PSANÍ NA KLÁVESNICI ---
def zadej_text(nadpis_text):
    """Vytvoří jednoduchou obrazovku pro psaní jména/hesla."""
    napsany_text = ""
    bezi_zadavani = True
   
    while bezi_zadavani:
        okno.blit(pozadi_img, (0,0))
        napis(nadpis_text, font_tlacitka, 150, CERNA)
       
        # Kreslení políčka
        pygame.draw.rect(okno, BILA, (40, 250, 280, 50))
        napis(napsany_text + "|", font_tlacitka, 275, CERNA)
       
        napis("Zadej a stiskni ENTER", font_maly, 350, CERNA)
        pygame.display.update()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: # Potvrdil Enterem
                    return napsany_text
                elif event.key == pygame.K_BACKSPACE: # Maže
                    napsany_text = napsany_text[:-1]
                else: # Píše znaky
                    napsany_text += event.unicode


# --- HLAVNÍ SMYČKA ---
def hlavni_menu():
    import webbrowser
    bezi = True
    posledni_body = 0
    prihlaseny_hrac = None
    zprava_na_obrazovce = ""
    zvuk_zapnuty = True
    hra.set_sound_enabled(zvuk_zapnuty)


    while bezi:
        okno.blit(pozadi_img, (0,0))


        # Nadpis a pták
        nadpis_stin = font_velky.render("FLAPPY BIRD", True, CERNA)
        okno.blit(nadpis_stin, nadpis_stin.get_rect(center=(SIRKA/2 + 3, 83)))
        okno.blit(font_velky.render("FLAPPY BIRD", True, BILA), nadpis_stin.get_rect(center=(SIRKA/2, 80)))
        okno.blit(ptak_img, (SIRKA/2 - 30, 130))


        # Info text (např. chyba při přihlášení)
        if zprava_na_obrazovce != "":
            napis(zprava_na_obrazovce, font_maly, 180, ZLUTA)


        # --- HRÁČ NENÍ PŘIHLÁŠENÝ ---
        if prihlaseny_hrac is None:
            napis("Pro hraní si vytvoř účet na webu.", font_mezi, 210, BILA)
           
            # Jen 2 tlačítka: Přihlásit a Konec
            if nakresli_tlacitko("PŘIHLÁSIT SE", 60, 270, 240, 60, ORANZOVA, SVETLE_ORANZOVA):
                pygame.time.delay(300)
                jmeno = zadej_text("Jméno:")
                heslo = zadej_text("Heslo:")
                if databaze.prihlaseni(jmeno, heslo):
                    prihlaseny_hrac = jmeno
                    zprava_na_obrazovce = ""
                else:
                    zprava_na_obrazovce = "Špatné jméno nebo heslo!"


            if nakresli_tlacitko("KONEC", 80, 350, 200, 60, CERVENA, SVETLE_CERVENA):
                bezi = False

            text_zvuk = "ZVUK: ZAP" if zvuk_zapnuty else "ZVUK: VYP"
            if nakresli_tlacitko(text_zvuk, 80, 430, 200, 50, MODRA, (130, 180, 255)):
                zvuk_zapnuty = not zvuk_zapnuty
                hra.set_sound_enabled(zvuk_zapnuty)
                pygame.time.delay(200)


        # --- HRÁČ JE PŘIHLÁŠENÝ ---
        else:
            # Jméno svítí v horní části menu
            napis(f"Hráč: {prihlaseny_hrac}", font_maly, 210, CERNA)


            # Odemkly se mu tlačítka pro hru a web
            if nakresli_tlacitko("HRÁT", 80, 250, 200, 60, ZELENA, SVETLE_ZELENA):
                posledni_body = hra.spustit_hru(okno)
                if posledni_body > 0:
                    databaze.pridat_vysledek(prihlaseny_hrac, int(posledni_body))
                pygame.time.delay(300)


            if nakresli_tlacitko("WEB A VÝSLEDKY", 50, 330, 260, 60, ORANZOVA, SVETLE_ORANZOVA):
                webbrowser.open("http://127.0.0.1:5000")
                pygame.time.delay(300)


            if nakresli_tlacitko("ODHLÁSIT", 80, 410, 200, 60, CERVENA, SVETLE_CERVENA):
                prihlaseny_hrac = None
                zprava_na_obrazovce = "Byl jsi odhlášen."
                pygame.time.delay(300)

            text_zvuk = "ZVUK: ZAP" if zvuk_zapnuty else "ZVUK: VYP"
            if nakresli_tlacitko(text_zvuk, 80, 490, 200, 50, MODRA, (130, 180, 255)):
                zvuk_zapnuty = not zvuk_zapnuty
                hra.set_sound_enabled(zvuk_zapnuty)
                pygame.time.delay(200)


        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                bezi = False


    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    hlavni_menu()
