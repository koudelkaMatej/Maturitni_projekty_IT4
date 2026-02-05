import pygame
import random

from settings import *
from player import Player
from enemy import Enemy
from bullet import Bullet
from score_manager import ScoreManager
from image_loader import ImageLoader


class Game:

    def __init__(self, screen, username):

        pygame.init()

        self.screen = screen
        self.username = username

        pygame.display.set_caption("Goblin Invasion")

        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.exit_game = False

        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Načtení obrázků
        self.image_loader = ImageLoader()

        # Score manager
        self.score_manager = ScoreManager(username)

        self.current_level = 1

        self.init_game()

    # ------------------------------------------------

    def init_game(self):

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()

        # Hráč
        self.player = Player(self.image_loader)
        self.all_sprites.add(self.player)

        # Nepřátelé
        self.create_enemies()

        self.running = True
        self.game_over = False
        self.exit_game = False

    # ------------------------------------------------

    def create_enemies(self):

        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):

                if row == 0:
                    enemy_type = "mega_goblin"
                elif row == 1:
                    enemy_type = "strong"
                else:
                    enemy_type = "basic"

                enemy = Enemy(
                    col * 70 + 50,
                    row * 50 + 50,
                    enemy_type,
                    self.image_loader
                )

                self.all_sprites.add(enemy)
                self.enemies.add(enemy)

    # ------------------------------------------------

    def events(self):

        for event in pygame.event.get():

            # Zavření okna
            if event.type == pygame.QUIT:

                self.running = False
                self.exit_game = True

            elif event.type == pygame.KEYDOWN:

                # Střelba
                if event.key == pygame.K_SPACE and not self.game_over:

                    if self.player.shoot():

                        bullet = Bullet(
                            self.player.rect.centerx,
                            self.player.rect.top,
                            image_loader=self.image_loader,
                            is_player_bullet=True
                        )

                        self.all_sprites.add(bullet)
                        self.bullets.add(bullet)

                # Restart po game over
                elif event.key == pygame.K_r and self.game_over:

                    self.score_manager.reset()
                    self.current_level = 1
                    self.init_game()

                # ESC = konec
                elif event.key == pygame.K_ESCAPE:

                    self.running = False
                    self.exit_game = True

    # ------------------------------------------------

    def update(self):

        if self.game_over:
            return

        self.all_sprites.update()

        # Zásahy nepřátel
        hits = pygame.sprite.groupcollide(
            self.enemies,
            self.bullets,
            False,
            True
        )

        for enemy, bullets in hits.items():

            if not enemy.is_dying and enemy.hit():
                self.score_manager.enemy_killed(enemy.enemy_type)

        # Zásahy hráče
        player_hits = pygame.sprite.spritecollide(
            self.player,
            self.enemy_bullets,
            True
        )

        for bullet in player_hits:

            if self.player.take_damage():

                if self.player.health <= 0:
                    self.game_over = True

        # Náhodná střelba nepřátel
        if random.random() < 0.01 and self.enemies:

            enemy = random.choice(list(self.enemies))

            if not enemy.is_dying:

                bullet = Bullet(
                    enemy.rect.centerx,
                    enemy.rect.bottom,
                    -1,
                    self.image_loader,
                    is_player_bullet=False
                )

                self.all_sprites.add(bullet)
                self.enemy_bullets.add(bullet)

        # Pohyb nepřátel
        for enemy in self.enemies:

            if enemy.rect.bottom >= SCREEN_HEIGHT - 50:

                self.game_over = True
                break

            if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:

                for e in self.enemies:
                    if not e.is_dying:
                        e.reverse_and_drop()

                break

        # Odstranění mrtvých
        dead = []

        for enemy in self.enemies:

            if enemy.is_dying and enemy.death_animation:
                if enemy.death_animation.is_finished():
                    dead.append(enemy)

        for enemy in dead:
            enemy.kill()

        # Nový level
        if len(self.enemies) == 0 and not self.game_over:

            self.score_manager.level_completed()
            self.current_level += 1
            self.create_enemies()

    # ------------------------------------------------

    def draw(self):

        bg = self.image_loader.get_level_background(self.current_level)

        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill(DARK_GREEN)

        self.all_sprites.draw(self.screen)

        # Death animace
        for enemy in self.enemies:

            if enemy.is_dying and enemy.death_animation:
                enemy.draw_death_animation(self.screen)

        # HUD
        health = self.font.render(
            f"Health: {self.player.health}",
            True,
            WHITE
        )

        self.screen.blit(health, (10, 10))

        score = self.font.render(
            self.score_manager.get_text(),
            True,
            WHITE
        )

        self.screen.blit(score, (10, 45))

        level = self.small_font.render(
            f"Level: {self.current_level}",
            True,
            WHITE
        )

        self.screen.blit(level, (650, 10))

        # GAME OVER obrazovka
        if self.game_over:

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)

            self.screen.blit(overlay, (0, 0))

            over = self.font.render("GAME OVER", True, RED)
            restart = self.font.render("R = Restart", True, WHITE)
            esc = self.font.render("ESC = Exit", True, GRAY)

            self.screen.blit(over, (300, 200))
            self.screen.blit(restart, (300, 250))
            self.screen.blit(esc, (300, 300))

        pygame.display.flip()

    # ------------------------------------------------

    def run(self):

        while self.running:

            self.clock.tick(FPS)

            self.events()
            self.update()
            self.draw()

            if self.exit_game:
                return "EXIT"

        return "MENU"
