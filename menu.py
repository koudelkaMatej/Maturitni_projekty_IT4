import pygame
from settings import *


class Menu:

    def __init__(self, screen):

        self.screen = screen

        self.font_big = pygame.font.Font(None, 60)
        self.font = pygame.font.Font(None, 36)

        self.clock = pygame.time.Clock()

        self.username = ""

    # --------------------------------

    def draw(self):

        self.screen.fill(DARK_GREEN)

        # Nadpis
        title = self.font_big.render("Goblin Invasion", True, YELLOW)
        self.screen.blit(title, (220, 80))

        # Text
        info = self.font.render("Zadej jméno hráče:", True, WHITE)
        self.screen.blit(info, (260, 200))

        # Input box
        box = pygame.Rect(250, 250, 300, 40)
        pygame.draw.rect(self.screen, WHITE, box, 2)

        name = self.font.render(self.username, True, WHITE)
        self.screen.blit(name, (box.x + 10, box.y + 5))

        # Nápověda
        hint = self.font.render("ENTER = Start | ESC = Exit", True, GRAY)
        self.screen.blit(hint, (220, 320))

        pygame.display.flip()

    # --------------------------------

    def run(self):

        running = True

        while running:

            self.clock.tick(FPS)

            for event in pygame.event.get():

                # Zavření okna
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:

                    # Start hry
                    if event.key == pygame.K_RETURN:

                        if len(self.username) >= 3:
                            return self.username

                    # Konec programu
                    elif event.key == pygame.K_ESCAPE:

                        return None

                    # Mazání
                    elif event.key == pygame.K_BACKSPACE:

                        self.username = self.username[:-1]

                    # Psani znaku
                    else:

                        if (
                            len(self.username) < 15
                            and event.unicode.isalnum()
                        ):
                            self.username += event.unicode

            self.draw()
