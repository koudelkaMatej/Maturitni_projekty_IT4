import pygame
from pygame.locals import *
from packages import funkce,block,snake
import time, sys

def choice(šířka_okna,výška_okna,velikost_blocku,okno,bg,font,font_mensi,fps,outline,modra,body_inner,obtiznosti,mycursor,mydb,user,sloupce,host,username,password,database):
    easy_cords = [šířka_okna // 5, výška_okna // 3] #Souřadnice blocku reprezentující Easy obtížnost
    medium_cords = [šířka_okna // 2, výška_okna // 3] #Souřadnice blocku reprezentující Mid obtížnost
    hard_cords = [šířka_okna // 1.25, výška_okna // 3] #Souřadnice blocku reprezentující Hard obtížnost
    skore_cords = [4 * velikost_blocku, (výška_okna // 3) * 2 + velikost_blocku * 3] #Souřadnice blocku reprezentující vypsání dosažených hodnot skóre
    reset_cords = [šířka_okna // 1.5, (výška_okna // 3) - velikost_blocku * 3] #Souřadnice blocku reprezentující Možnost resetu hodnot skóre
    popis_cords = [šířka_okna - velikost_blocku * 4, (výška_okna // 3) * 2 + velikost_blocku * 3] #Souřadnice blocku reprezentující Popisky blocků
    žebříčky_cords = [šířka_okna // 2, (výška_okna // 3) * 2 + velikost_blocku * 3] #Souřadnice blocku reprezentující žebříčky
    easy = block.Block(easy_cords[0],easy_cords[1],(0,255,0),okno,velikost_blocku)
    medium = block.Block(medium_cords[0],medium_cords[1],(255,255,0),okno,velikost_blocku)
    hard = block.Block(hard_cords[0], hard_cords[1],(255,0,0),okno,velikost_blocku)
    skore = block.Block(skore_cords[0], skore_cords[1],(0, 255, 255),okno,velikost_blocku)
    reset = block.Block(reset_cords[0], reset_cords[1],(255, 0, 0),okno,velikost_blocku)
    popis = block.Block(popis_cords[0], popis_cords[1],(5, 110, 80),okno,velikost_blocku)
    žebříčky = block.Block(žebříčky_cords[0], žebříčky_cords[1],(255,192,203),okno,velikost_blocku)
    #Proměnné
    neměnit_směr = False
    timeout = 0
    zobraz_skore = False
    run = True
    konec_hry = False
    aktualizuj = False
    cekej = 0
    pauza = 0
    směr = 2
    pomoc = False
    stisk = 0
    prohra = 0
    zobraz_žebříčky = False
    start = time.time()
    Had = snake.Snake(výška_okna, šířka_okna, velikost_blocku)
    #Začátek Menu
    while run:
        cas = round(time.time() - start, 2)#Výpočet času pro správnou funkci fps
        funkce.vykreslení_okna(okno,bg)
        #Kontrola událostí provedených uživatelem
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN and stisk == 0 and neměnit_směr == False:
                směr = Had.pohyb(event, směr)
                stisk += 1
        if zobraz_skore == False and zobraz_žebříčky == False:
            funkce.vykresleni_volby(okno,font,šířka_okna)
            if pomoc == True:#Pokud hráč aktivuje nápovědu, tato funkce zobrazí popisky jednotlivých blocků
                funkce.popisky(easy_cords,medium_cords,hard_cords,okno,obtiznosti,font_mensi)
            #Vykreslení blocků pro možnost volby
            easy.vykresli()
            medium.vykresli()
            hard.vykresli()
            skore.vykresli()
            popis.vykresli()
            žebříčky.vykresli()
            #Vykreslení defaultních popisků blocků
            info = "Nápověda"
            info = font_mensi.render(info, True, (255, 255, 255))
            okno.blit(info, (popis_cords[0] - 40, popis_cords[1] + 30))
            info = "Žebříčky"
            info = font_mensi.render(info, True, (255, 255, 255))
            okno.blit(info, (žebříčky_cords[0] - 35, žebříčky_cords[1] + 30))
            info = "Nejvyšší skóre"
            info = font_mensi.render(info, True, (255, 255, 255))
            okno.blit(info, (skore_cords[0] - 64, skore_cords[1] + 30))
            if easy.kolize(Had.getPozice()):
                obtiznost = obtiznosti[0]
                break
            if medium.kolize(Had.getPozice()):
                obtiznost = obtiznosti[1]
                break
            if hard.kolize(Had.getPozice()):
                obtiznost = obtiznosti[2]
                break
            if skore.kolize(Had.getPozice()):
                if round(time.time() - timeout, 2) > 0.3:#Pokud hráč aktivuje možnost vykreslení skóre, na 0,3s se block stane nefunkčním, aby se zabránilo nechtěnému aktivování(jednodušeji řečeno, jedná se o odezvu)
                    zobraz_skore = True
                    proběhlo = False
                    timeout = time.time()
            if popis.kolize(Had.getPozice()):
                if round(time.time() - cekej, 2) > 0.3:#Pokud hráč aktivuje možnost nápovědy, na 0,3s se block stane nefunkčním, aby se zabránilo nechtěnému aktivování(jednodušeji řečeno, jedná se o odezvu)
                    cekej = time.time()
                    if pomoc == False:
                        pomoc = True
                    else:
                        pomoc = False
                else:
                    cekej = time.time()
            if žebříčky.kolize(Had.getPozice()):
                if round(time.time() - pauza, 2) > 0.3:#Pokud hráč aktivuje vypsání aktuálního žebříčku, na 0,3s se block stane nefunkčním, aby se zabránilo nechtěnému aktivování(jednodušeji řečeno, jedná se o odezvu)
                    pauza = time.time()
                    proběhlo = False
                    zobraz_žebříčky = True
        elif zobraz_žebříčky == True:#Menu žebříčků
            text = f"Nejlepší hráči:"
            umístění = font.render(text, True, (255, 255, 255))
            okno.blit(umístění, ((šířka_okna * 0.365), 3))
            #Request se databázi odešle jen jednou, a to ihned po aktivování možnosti zobrazení žebříčků
            if proběhlo == False:
                pozice = funkce.žebříček(sloupce, mycursor)
                proběhlo = True
            #vykreslení možnosti exitu
            info = "Exit"
            info = font_mensi.render(info, True, (255, 255, 255))
            okno.blit(info, (žebříčky_cords[0] - 15, žebříčky_cords[1] + 30))
            pygame.draw.rect(okno, (255,192,203), (žebříčky_cords[0], žebříčky_cords[1], velikost_blocku, velikost_blocku))
            for i in range(3):
                pocet = int(len(list(pozice[i]))) #Kontrola délky relativního prvku, aby se zamezilo nechtěným problémům
                hodnota = f"{obtiznosti[i]} -> {pozice[i]}"
                hodnota = font_mensi.render(hodnota, True, (255, 255, 255))
                okno.blit(hodnota, (50, (výška_okna // 8) * (2 + i)))
                box = Rect(25, (výška_okna // 8) * (2 + i) - 11, 160 + pocet * 11, 45)
                pygame.draw.rect(okno, (255, 0, 0), box, 2, 3)
            if round(time.time() - pauza, 2) > 0.3: #Opět odezva
                if žebříčky.kolize(Had.getPozice()): #kontrola kolize hlavy hada s blockem exitu, který je na stejné pozici jako block pro vstup do menu samotného
                    zobraz_žebříčky = False
                    pauza = time.time()
            
        else:#Menu >>skóre<<
            #Vykreslení možnosti resetování hodnot skóre
            info = "Reset hodnot"
            info = font_mensi.render(info, True, (255, 255, 255))
            okno.blit(info, (reset_cords[0] + 30, reset_cords[1]))
            reset.vykresli()
            #vykreslení možnosti exitu
            info = "Exit"
            info = font_mensi.render(info, True, (255, 255, 255))
            okno.blit(info, (skore_cords[0] - 15, skore_cords[1] + 30))
            if round(time.time() - timeout, 2) > 0.3: #Opět odezva
                pygame.draw.rect(okno, (0, 255, 255), (skore_cords[0], skore_cords[1], velikost_blocku, velikost_blocku))
                if skore.kolize(Had.getPozice()): #kontrola kolize hlavy hada s blockem exitu, který je na stejné pozici jako block pro vstup do menu samotného
                    zobraz_skore = False
                    timeout = time.time()
                if reset.kolize(Had.getPozice()): #Vynulování hodnot skóre
                    mycursor.execute(f"""
                    UPDATE `Score`
                    SET Easy = 0, Medium = 0, Hard = 0
                    WHERE username = '{user}'
                    """)
                    mydb.commit()   
                    hodnoty = [0, 0, 0]
            #Získávání hodnot skóre
            #Request se databázi odešle jen jednou, a to ihned po aktivování možnosti zobrazení hodnot nejvyššího skóre
            if proběhlo == False:
                mycursor.execute(f"""SELECT * FROM `Score` WHERE username = '{user}'""")
                myresult = mycursor.fetchall()
                hodnoty = list(myresult[0])
                for _ in range(2): hodnoty.pop(0)
                proběhlo = True
            #Vypsání hodnot skóre na obrazovku  
            for i in range(3):
                pocet = int(len(list(str(hodnoty[i]))))#Kontrola délky relativního prvku, aby se zamezilo nechtěným problémům
                hodnota = f"{obtiznosti[i]} : {hodnoty[i]}"
                hodnota = font_mensi.render(hodnota, True, (255, 255, 255))
                okno.blit(hodnota, (50, (výška_okna // 8) * (2 + i)))
                box = Rect(25, (výška_okna // 8) * (2 + i) - 11, 150 + pocet * 11, 45)
                pygame.draw.rect(okno, (255, 0, 0), box, 2, 3)
        if cas > 1 / fps:#logika fps
            aktualizuj = True
            start = time.time()
            stisk = 0
        if konec_hry == False:
            if aktualizuj == True:
                neměnit_směr = False
                #Posunutí hada o jeden block směrem, kterým hledí
                aktualizuj = False
                Had.posun(směr,velikost_blocku)
                konec_hry = funkce.kontrola_konce_hry(konec_hry, Had.getPozice(),šířka_okna,výška_okna,velikost_blocku)
        else:
            neměnit_směr = True
            #Efekt, umožňující průchozí strany okna
            Had.pruchod(velikost_blocku,šířka_okna,výška_okna)
            konec_hry = False
        hlava = 1#Proměnná, která nám zajistí, že podmínka ve for loopu níže bude splněna pouze jednou, pro získání jiné barvy pro block představující hlavu
        if konec_hry == False or prohra == 0:
            Had.vykresli(okno,outline,body_inner,velikost_blocku,modra,hlava)
        #update displaye
        pygame.display.update()
    return obtiznost, Had.getPozice(), směr
