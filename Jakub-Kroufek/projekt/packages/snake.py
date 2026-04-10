import pygame
class Snake:
    def __init__(self, výška_okna, šířka_okna, velikost_blocku):
        pozice_hada = [[int(šířka_okna / 2), int(výška_okna / 2)]]#list pozic blocků + přidání prvního blocku
        pozice_hada.append([int(šířka_okna / 2) - velikost_blocku, int(výška_okna / 2) ])#Druhý block
        pozice_hada.append([int(šířka_okna / 2) -velikost_blocku * 2, int(výška_okna / 2)])#Třetí block
        pozice_hada.append([int(šířka_okna / 2) - velikost_blocku * 3, int(výška_okna / 2)])#Čtvrtý block
        self.pozice_hada = pozice_hada
    def pohyb(self,event,směr):
        if event.key == pygame.K_w and směr != 3:#Pokud stiskneme W a proměnná směr není 3, což by znamenalo že had se pohybuje směrem dolu, tak se změní proměnná směr na 1, což znamená, že pojede nahoru
            směr = 1
        if event.key == pygame.K_d and směr != 4:#Pokud stiskneme D a proměnná směr není 4, což by znamenalo že had se pohybuje směrem doleva, tak se změní proměnná směr na 2, což znamená, že pojede doprava
            směr = 2
        if event.key == pygame.K_s and směr != 1:#Pokud stiskneme S a proměnná směr není 1, což by znamenalo že had se pohybuje směrem nahoru, tak se změní proměnná směr na 1, což znamená, že pojede dolu
            směr = 3
        if event.key == pygame.K_a and směr != 2:#Pokud stiskneme A a proměnná směr není 2, což by znamenalo že had se pohybuje směrem doprava, tak se změní proměnná směr na 1, což znamená, že pojede doleva
            směr = 4
        return směr
    def getPozice(self):
        return self.pozice_hada
    def posun(self,směr,velikost_blocku):
        pozice_hada = self.pozice_hada
        pozice_hada = pozice_hada[-1:] + pozice_hada[:-1]
        if směr == 1:
            pozice_hada[0][0] = pozice_hada[1][0]
            pozice_hada[0][1] = pozice_hada[1][1] - velikost_blocku
        elif směr == 3:
            pozice_hada[0][0] = pozice_hada[1][0]
            pozice_hada[0][1] = pozice_hada[1][1] + velikost_blocku
        elif směr == 2:
            pozice_hada[0][1] = pozice_hada[1][1]
            pozice_hada[0][0] = pozice_hada[1][0] + velikost_blocku
        elif směr == 4:
            pozice_hada[0][1] = pozice_hada[1][1]
            pozice_hada[0][0] = pozice_hada[1][0] - velikost_blocku
        self.pozice_hada = pozice_hada
    def pruchod(self,velikost_blocku,šířka_okna,výška_okna):
        pozice_hada = self.pozice_hada
        if pozice_hada[0][0] > šířka_okna + velikost_blocku * 3:
            pozice_hada = [[0, pozice_hada[0][1]]]
            pozice_hada.append([0 - velikost_blocku, pozice_hada[0][1]])
            pozice_hada.append([0 -velikost_blocku * 2, pozice_hada[0][1]])
            pozice_hada.append([0 - velikost_blocku * 3, pozice_hada[0][1]])
        if pozice_hada[0][0] < 0 - velikost_blocku * 3:
            pozice_hada = [[šířka_okna, pozice_hada[0][1]]]
            pozice_hada.append([šířka_okna + velikost_blocku, pozice_hada[0][1]])
            pozice_hada.append([šířka_okna + velikost_blocku * 2, pozice_hada[0][1]])
            pozice_hada.append([šířka_okna + velikost_blocku * 3, pozice_hada[0][1]])
        if pozice_hada[0][1] > výška_okna + velikost_blocku * 3:
            pozice_hada = [[pozice_hada[0][0], 0]]
            pozice_hada.append([pozice_hada[0][0], 0 - velikost_blocku])
            pozice_hada.append([pozice_hada[0][0], 0 - velikost_blocku * 2])
            pozice_hada.append([pozice_hada[0][0], 0 - velikost_blocku * 3])
        if pozice_hada[0][1] < 0 - velikost_blocku * 3:
            pozice_hada = [[pozice_hada[0][0], výška_okna]]
            pozice_hada.append([pozice_hada[0][0], výška_okna + velikost_blocku])
            pozice_hada.append([pozice_hada[0][0], výška_okna + velikost_blocku * 2])
            pozice_hada.append([pozice_hada[0][0], výška_okna + velikost_blocku * 3])
        self.pozice_hada = pozice_hada
    def dalsi_block(self,směr,velikost_blocku):
        pozice_hada = self.pozice_hada
        prodlouzeny_block = list(pozice_hada[-1])
        if směr == 1:
            prodlouzeny_block[1] += velikost_blocku#Pokud se had pohybuje nahoru, prodlouží se o velikost velikost_blocku na y souřadnici, což reprezentuje jeden block
        elif směr == 3:
            prodlouzeny_block[1] -= velikost_blocku#Pokud se had pohybuje dolu, zmenší se o velikost velikost_blocku na y souřadnici, což reprezentuje jeden block
        elif směr == 2:
            prodlouzeny_block[0] -= velikost_blocku#Pokud se had pohybuje doleva, zmenší se o velikost velikost_blocku na x souřadnici, což reprezentuje jeden block
        if směr == 4:
            prodlouzeny_block[0] += velikost_blocku#Pokud se had pohybuje doprava, zvětší se o velikost velikost_blocku na x souřadnici, což reprezentuje jeden block
        #Připojení blocku za sebrání jídla k hadovi
        pozice_hada.append(prodlouzeny_block)
        self.pozice_hada = pozice_hada
    def vykresli(self,okno,outline,body_inner,velikost_blocku,modra,hlava):
        pozice_hada = self.pozice_hada
        for x in pozice_hada:
            if hlava == 0:#Ostatní blocky mimo hlavu, neboli tělo
                pygame.draw.rect(okno, outline, (x[0], x[1], velikost_blocku, velikost_blocku))#Vykreslení větší blocku pod menší block, pro získání efektu stínu/obrysu
                pygame.draw.rect(okno, body_inner, (x[0] + 1, x[1] + 1, velikost_blocku - 2, velikost_blocku - 2))#Vykreslení menšího blocku na větší block, pro uplatnění efektu
            if hlava == 1:#Podmínka za celý for loop proběhne jednou
                pygame.draw.rect(okno, outline, (x[0], x[1], velikost_blocku, velikost_blocku))#Vykreslení větší blocku pod menší block, pro získání efektu stínu/obrysu
                pygame.draw.rect(okno, modra, (x[0] + 1, x[1] + 1, velikost_blocku - 2, velikost_blocku - 2))#Vykreslení menšího blocku na větší block, pro uplatnění efektu
                hlava = 0
        self.pozice_hada = pozice_hada
        return hlava
    def setPozice(self,pozice_hada):
        self.pozice_hada = pozice_hada