import pygame
from pygame.locals import *
from packages import funkce, okno_volby, nickname, snake
from settings import *
import mysql.connector, getpass, time
#Získání uživatelského jména pro doporučení uživatelského jména
user = getpass.getuser()
#Samotné napojení se na databázi
mydb = mysql.connector.connect(
    host = host
    ,user = username
    ,password = password
    ,database = database
)
mycursor = mydb.cursor()
#inicializace
pygame.init()
#Okno
šířka_okna = 600
výška_okna = 600
okno = pygame.display.set_mode((šířka_okna, výška_okna))
pygame.display.set_caption("Had")
#Proměnné
kliknuto = False
fps = 10
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
stisk = 0
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
#Volba nickname
user = nickname.otazka(user,okno,šířka_okna,výška_okna,font_mensi,povolené_znaky)
#Kontrola Existence Table Score
nove_hodnoty = False
try:
    mycursor.execute(f"""SELECT * FROM `Score`""")
    myresult = mycursor.fetchall() 
except mysql.connector.errors.ProgrammingError: 
    mycursor.execute("""CREATE TABLE `Score`(
        username text,
        Easy int,
        Medium int,
        Hard int
                     
    )""")
    mydb.commit()
#Kontrola Existence Hodnot pro aktuálního uživatele
try:
    mycursor.execute(f"""SELECT * FROM `Score` WHERE username = '{user}'""")
    myresult = mycursor.fetchall()
    if myresult == []:
        nove_hodnoty = True
except mysql.connector.errors.ProgrammingError: 
    nove_hodnoty = True
if nove_hodnoty == True:#Vytvoření nových hodnot
    mycursor.execute(f"""INSERT INTO `Score`
(username, Easy, Medium, Hard) VALUES
('{user}', 0, 0, 0);
""")
    mydb.commit()
#Volba obtížnosti
obtiznost, pozice_hada, směr = okno_volby.choice(šířka_okna,výška_okna,velikost_blocku,okno,bg,font,font_mensi,fps,outline,modra,body_inner,obtiznosti,mycursor,mydb,user,sloupce,host,username,password,database)
Had2.setPozice(pozice_hada)
#Zahájení odpočtu času
start = time.time()
#Začátek hry
while run:
    cas = round(time.time() - start, 2)#Výpočet času pro správnou funkci fps
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
        jidlo = funkce.vytvoření_jídla(obtiznost,obtiznosti,velikost_blocku,šířka_okna,výška_okna,jidlo,okno)
    jidlo.vykresli()
    #Kolize s jídlem
    if jidlo.kolize(Had2.getPozice()):
        nove_jidlo = True
        #Prodloužení hada
        Had2.dalsi_block(směr,velikost_blocku)
        score += 1 #Přidání score
    #Logika fps
    if cas > 1 / fps:
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
                obtiznost, pozice_hada, směr = okno_volby.choice(šířka_okna,výška_okna,velikost_blocku,okno,bg,font,font_mensi,fps,outline,modra,body_inner,obtiznosti,mycursor,mydb,user,sloupce,host,username,password,database)
                Had2.setPozice(pozice_hada)
    hlava = 1#Proměnná, která nám zajistí, že podmínka ve for loopu níže bude splněna pouze jednou, pro získání jiné barvy pro block představující hlavu
    if konec_hry == False or prohra == 0:
        hlava = Had2.vykresli(okno,outline,body_inner,velikost_blocku,modra,hlava)
    #update displaye
    pygame.display.update()
pygame.quit()
mycursor.close()
mydb.close()
