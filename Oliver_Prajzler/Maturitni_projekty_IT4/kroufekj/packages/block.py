import pygame
class Block:
    def __init__(self,x,y,barva,okno,velikost):
        self.x = x
        self.y = y
        self.barva = barva
        self.okno = okno
        self.velikost = velikost
        self.cords = [self.x, self.y]
        self.animace = 0
    def vykresli(self):
        pygame.draw.rect(self.okno, self.barva, (self.x, self.y, self.velikost, self.velikost))
    def kolize(self,pozice_hada):
        if pozice_hada[0] == self.cords:
            return True
        else:
            return False
    def update_animation(self): #Aktualizování animace powerup blocku každou sekundu
        if self.animace < 4:
            self.animace += 1
        else:
            self.animace = 0
    def animate(self,okno): #Samotná animace powerupu
        font = pygame.font.SysFont(None, 20)
        otaznik = font.render("?", True, (0,0,0))
        otaznik_sqr = otaznik.get_rect(center=(self.x + self.velikost/2, self.y + self.velikost/2))
        stín_font = pygame.font.SysFont(None, 18)
        stín_surface = stín_font.render("?", True, (255,255,255))
        stín_rect = otaznik.get_rect(center=(self.x + self.velikost/2, self.y + self.velikost/2))
        pygame.draw.rect(self.okno, (255, 251, 0), (self.x, self.y, self.velikost, self.velikost))
        pygame.draw.rect(self.okno, (0,0,0), (self.x+1, self.y+1, self.velikost-2, self.velikost-2))
        pygame.draw.rect(self.okno, (255, 251, 0), (self.x+self.animace, self.y+self.animace, self.velikost-self.animace*2, self.velikost-self.animace*2))
        okno.blit(otaznik, otaznik_sqr)
        okno.blit(stín_surface, stín_rect)

        
        