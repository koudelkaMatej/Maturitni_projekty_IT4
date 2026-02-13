import pygame
from pygame.locals import *
from packages import funkce, okno_volby, nickname, snake
from settings import *
import mysql.connector, time, random
#Samotné napojení se na databázi
mydb = mysql.connector.connect(
    host = host
    ,user = username
    ,password = password
    ,database = database
)
mycursor = mydb.cursor(buffered=True)
#inicializace
pygame.init()
#Okno
šířka_okna = 600
výška_okna = 600
okno = pygame.display.set_mode((šířka_okna, výška_okna))
pygame.display.set_caption("Had")
#Proměnné
power_active = False
bonus_active = False
timer = 0
kliknuto = False
bps = 10
novy_nick = False
run = True
prohra = 0
stisk = 0
obtiznosti = ["Snadná", "Střední", "Obtížná"]
aktualizuj = False
velikost_blocku = 20#pixely na jednen block ve hře
směr = 1#1 je nahoru, 2 vpravo, 3 dolu a 4 vlevo
score = 0
konec_hry = False
run = True
prohra = 0
animace_zdvojnasobeni = False
stisk = 0
powered = 0
animace_casy =[]
start = time.time()
tlačítko = Rect(šířka_okna // 2 - 90, výška_okna // 2, 180, 45)
#Snake
Had2 = snake.Snake(výška_okna,šířka_okna,velikost_blocku)
#jídlo
jidlo = [0, 0]
nove_jidlo = True
prodlouzeny_block = [0, 0]
#font
font = pygame.font.SysFont(None, 40)
font_mensi = pygame.font.SysFont(None, 33)
#Barvy
bg = (0, 0, 0)
body_inner = (255, 255, 255)
outline = (100, 100, 200)
modra = (0, 0, 255)
#Pokud tabulka není, vytvoříme ji + fetchneme data
mycursor.execute("""
CREATE TABLE IF NOT EXISTS `Score` (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255),
    Easy INT DEFAULT 0,
    Medium INT DEFAULT 0,
    Hard INT DEFAULT 0)""")
mydb.commit()
mycursor.execute("SELECT username FROM `Score` WHERE username='host'")
result = mycursor.fetchall()
if result == []:
    mycursor.execute(f"""INSERT INTO `Score`
(username, password, Easy, Medium, Hard) VALUES
('host', '', 0, 0, 0);
""") 
mydb.commit()
#Volba nickname
user = nickname.otazka(okno,šířka_okna,výška_okna,font_mensi,povolené_znaky, mycursor)
#Volba obtížnosti
obtiznost, pozice_hada, směr = okno_volby.choice(šířka_okna,výška_okna,velikost_blocku,okno,bg,font,font_mensi,bps,outline,modra,body_inner,obtiznosti,mycursor,mydb,user,sloupce,host,username,password,database)
Had2.setPozice(pozice_hada)
#Zahájení odpočtu času
start = time.time()
#Začátek hry
while run:
    cas = round(time.time() - start, 2)#Výpočet času pro správnou funkci bps
    funkce.vykreslení_okna(okno,bg)
    funkce.vykreslení_score(score,obtiznosti,okno,obtiznost,font,šířka_okna)
    funkce.vykreslení_obtížnosti(obtiznost,font,okno,šířka_okna,výška_okna,obtiznosti)
    #Kontrola událostí provedených uživatelem
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN and stisk == 0:
            směr = Had2.pohyb(event,směr)
            stisk += 1
    #tvorba jídla
    if nove_jidlo == True:
        nove_jidlo = False
        jidlo = funkce.vytvoření_jídla(obtiznost,obtiznosti,velikost_blocku,šířka_okna,výška_okna,okno)
    jidlo.vykresli()
    #Kolize s jídlem
    if jidlo.kolize(Had2.getPozice()):
        nove_jidlo = True
        #Prodloužení hada
        Had2.dalsi_block(směr,velikost_blocku)
        score += 1 #Přidání score
    #PowerUp
    if timer >= bps * 10 and bonus_active == False: #Každých 10s se zjeví powerup
        bonus_active = True
        timer = 0
        bonus_block = funkce.vytvoření_jídla(obtiznosti[1],obtiznosti,velikost_blocku,šířka_okna,výška_okna,okno)
    #Řešení powerupů
    if bonus_active:
        bonus_block.animate(okno)
        if timer >= bps: #Každou seknundu se bude aktualizovat stav powerup animačního blocku
            timer = 0
            bonus_block.update_animation()
        if bonus_block.kolize(Had2.getPozice()): #Kontrola kolize blocku s hadem
            bonus_active = False
            power_active = True
            powered = random.randint(1,10)
            if powered != 10: #Zrychlení (90% šance)
                save_bps = bps
                bps *= 2
            elif powered == 10: #Zdvojnásobení skóre(10% šance)
                stav_animace_zdvojnasobeni = 0 #Stav pro animaci zdvojnásobení skóre
                animace_zdvojnasobeni = True
                pocatek_animace_zdvojnasobeni = time.time()
    if animace_zdvojnasobeni:#Animace pro zdvojnásobení skóre
        animace_zdvojnasobeni, stav_animace_zdvojnasobeni, animace_casy = funkce.double(score,font,okno,šířka_okna,stav_animace_zdvojnasobeni,pocatek_animace_zdvojnasobeni, animace_casy)
        if animace_zdvojnasobeni == False:
            if score != 0:
                score *= 2
    if powered > 0 and powered < 10: #Zrychlení pohybu hada
        bps = funkce.speedup(power_active,save_bps,bps,timer)
    #Logika bps
    if cas > 1 / bps:
        timer += 1
        aktualizuj = True
        start = time.time()
        stisk = 0
    if konec_hry == False:
        if aktualizuj == True:
            #Posunutí hada o jeden block směrem, kterým hledí
            aktualizuj = False
            Had2.posun(směr,velikost_blocku)
            konec_hry = funkce.kontrola_konce_hry(konec_hry, Had2.getPozice(),výška_okna,šířka_okna, velikost_blocku)
    else:
        prohra += 1
        if prohra == 1:
            pygame.time.delay(2000)
            změna = funkce.zápis_score(score,obtiznosti,obtiznost,mycursor,mydb,user,sloupce)
        okno.fill((0, 0, 0))
        funkce.vykresleni_konce_hry(font,okno,šířka_okna,výška_okna,změna,tlačítko,font_mensi)
        funkce.vykreslení_score(score,obtiznosti,okno,obtiznost,font,šířka_okna)
        
        if event.type == pygame.MOUSEBUTTONDOWN and kliknuto == False:#Kliknutní
            kliknuto = True
        if event.type == pygame.MOUSEBUTTONUP and kliknuto == True:#Upuštění
            kliknuto = False
        #Jen pro kontrolu, jestli uživatel skutečně kliknul, a nedrží jen tlačítko myši
            pos = pygame.mouse.get_pos()
            if tlačítko.collidepoint(pos):
                #Restart Proměnných
                animace_zdvojnasobeni = False
                power_active = False
                bonus_active = False
                timer = 0
                Had2 = snake.Snake(výška_okna,šířka_okna,velikost_blocku)
                směr = 1
                aktualizuj = False
                jidlo = [0, 0]
                nove_jidlo = True
                prodlouzeny_block = [0, 0]
                score = 0
                stisk = 0
                prohra = 0
                konec_hry = False
                animace_casy =[]
                obtiznost, pozice_hada, směr = okno_volby.choice(šířka_okna,výška_okna,velikost_blocku,okno,bg,font,font_mensi,bps,outline,modra,body_inner,obtiznosti,mycursor,mydb,user,sloupce,host,username,password,database)
                Had2.setPozice(pozice_hada)
    hlava = 1#Proměnná, která nám zajistí, že podmínka ve for loopu níže bude splněna pouze jednou, pro získání jiné barvy pro block představující hlavu
    if konec_hry == False or prohra == 0:
        hlava = Had2.vykresli(okno,outline,body_inner,velikost_blocku,modra,hlava)
    #update displaye
    pygame.display.update()
pygame.quit()
mycursor.close()
mydb.close()
