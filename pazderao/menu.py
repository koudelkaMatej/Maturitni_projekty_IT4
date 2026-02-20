import pygame
import button

pygame.init()

#rozlišení
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Main Menu")

game_paused = False
menu_state = "main"

#fonty
font = pygame.font.SysFont("arialblack", 30)

#barvy
TEXT_COL = (255, 255, 255)

#image load
resume_img = pygame.image.load("Projekt-main/images/button_resume.png").convert_alpha()
quit_img = pygame.image.load("Projekt-main/images/button_quit.png").convert_alpha()


#create button instances - centrované na obrazovce 600x600
# Resume button se bude centrovat horizontálně a vertikálně v horní polovině
resume_button = button.Button(int(SCREEN_WIDTH/2 - resume_img.get_width()/2), int(SCREEN_HEIGHT/2 - 100), resume_img, 1)
# Quit button se bude centrovat horizontálně a vertikálně v dolní polovině
quit_button = button.Button(int(SCREEN_WIDTH/2 - quit_img.get_width()/2), int(SCREEN_HEIGHT/2 + 50), quit_img, 1)

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

#game loop
run = True
while run:

  screen.fill((52, 78, 91))

  #kontrola menu
  if game_paused == True:
    if menu_state == "main":
      if resume_button.draw(screen):
        game_paused = False
        menu_state = "options"
      if quit_button.draw(screen):
        run = False

  else:
    # Text centrován na obrazovce
    text_surface = font.render("Stiskni mezerník pro menu", True, TEXT_COL)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(text_surface, text_rect)

  #event handler
  for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        game_paused = True
    if event.type == pygame.QUIT:
      run = False

  pygame.display.update()

pygame.quit()