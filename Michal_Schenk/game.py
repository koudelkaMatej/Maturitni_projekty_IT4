import pygame
import sys
from enum import Enum
import random
import datetime

import settings
import objects

import db_handling
from db_handling import UserModel as User


# Initialize Pygame
pygame.init()




# Game states
class GameState(Enum):
    INTRO = 1
    MAIN_MENU = 2
    SETTINGS = 3
    PLAY = 4
    LEADERBOARD = 5
    QUIT = 6




#
#   INTRO STATE
#
class IntroScreen:
    """INTRO STATE"""
    def __init__(self):
        self.alpha = 0
        self.fade_speed = 3
        self.display_time = 0
        self.max_display_time = settings.FPS * 5

        self.texts = {
            'title': objects.Text(
                text=settings.GAME_TITLE,
                font=pygame.font.Font(None, 74),
                x=settings.SCREEN_WIDTH // 2,
                y=settings.SCREEN_HEIGHT // 2,
                color=(255,255,255),
                align="center"
            ),
            'subtitle': objects.Text(
                text="Press any key to skip",
                font=pygame.font.Font(None, 24),
                x=settings.SCREEN_WIDTH // 2,
                y=settings.SCREEN_HEIGHT // 2 + 30,
                color=(128,128,128),
                align="center"
            ),
            'inspiration_credit': objects.Text(
                text="Inspired by FLATHEAD @ Tim Oxton",
                font=pygame.font.Font(None, 24),
                x=settings.SCREEN_WIDTH // 2,
                y=settings.SCREEN_HEIGHT - 20,
                color=(255,255,255),
                align="center"
            )
        }
        
    def update(self):
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed)
        self.display_time += 1
        
        if self.display_time >= self.max_display_time:
            return GameState.MAIN_MENU
        return GameState.INTRO
    
    def draw(self, screen):
        screen.fill(settings.BLACK)

        for text in self.texts.values():
            text.set_alpha(self.alpha)
            text.draw(screen)
























#
#   MAIN MENU STATE
#
class MainMenuScreen:
    """MAIN MENU STATE"""
    def __init__(self):
        button_width = 300
        button_height = 60
        button_x = (settings.SCREEN_WIDTH - button_width) // 2
        start_y = 200
        spacing = 80
        
        self.buttons = {
            'play': objects.Button(
                    x=button_x, 
                    y=start_y, 
                    width=button_width, 
                    height=button_height, 
                    text="PLAY", 
                    font=pygame.font.Font(None, 24),
                    color=(255,255,255), 
                    hover_color=(0,0,0), 
                    bg_color=(0,0,0), 
                    bg_hover_color=(255,255,255)
                ),
            'settings': objects.Button(
                    x=button_x, 
                    y=start_y + spacing, 
                    width=button_width, 
                    height=button_height, 
                    text="SETTINGS", 
                    font=pygame.font.Font(None, 24),
                    color=(255,255,255), 
                    hover_color=(0,0,0), 
                    bg_color=(0,0,0), 
                    bg_hover_color=(255,255,255)
                ),
            'leaderboard': objects.Button(
                    x=button_x, 
                    y=start_y + spacing * 2, 
                    width=button_width, 
                    height=button_height, 
                    text="LEADERBOARD", 
                    font=pygame.font.Font(None, 24),
                    color=(255,255,255), 
                    hover_color=(0,0,0), 
                    bg_color=(0,0,0), 
                    bg_hover_color=(255,255,255)
                ),
            'quit': objects.Button(
                    x=button_x, 
                    y=start_y + spacing * 3, 
                    width=button_width, 
                    height=button_height, 
                    text="QUIT", 
                    font=pygame.font.Font(None, 24),
                    color=(255,255,255), 
                    hover_color=(0,0,0), 
                    bg_color=(0,0,0), 
                    bg_hover_color=(255,255,255)
                )
        }
    
        self.texts = {
            'title': objects.Text(
                text=settings.GAME_TITLE,
                font=pygame.font.Font(None, 74),
                x=settings.SCREEN_WIDTH // 2,
                y=100,
                color=(255,255,255),
                align="center"
            ),
            'copyright': objects.Text(
                text="Copyright © 2026 Michal Schenk",
                font=pygame.font.Font(None, 24),
                x=settings.SCREEN_WIDTH-10,
                y=settings.SCREEN_HEIGHT-10,
                color=(255,255,255),
                align="bottomright"
            ),
            'user': objects.Text(
                text="Anonymous (Settings)",
                prefix="Logged in as: ",
                font=pygame.font.Font(None, 24),
                x=settings.SCREEN_WIDTH//2,
                y=settings.SCREEN_HEIGHT-10,
                color=(255,255,255),
                align="bottom"
            )
        }


    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons['play'].is_clicked(mouse_pos, event):
                return GameState.PLAY
            elif self.buttons['settings'].is_clicked(mouse_pos, event):
                return GameState.SETTINGS
            elif self.buttons['leaderboard'].is_clicked(mouse_pos, event):
                return GameState.LEADERBOARD
            elif self.buttons['quit'].is_clicked(mouse_pos, event):
                return GameState.QUIT
        return GameState.MAIN_MENU
    
    def draw(self, screen, mouse_pos):
        screen.fill(settings.BLACK)
        
        for button in self.buttons.values():
            button.check_hover(mouse_pos)
            button.draw(screen)

        for text in self.texts.values():
            text.draw(screen)

        if settings.load_settings()["logged_in"]:
            self.texts['user'].set_text(settings.load_settings()["username"])
        else:
            self.texts['user'].set_text("Anonymous")



















#
#   SETTINGS STATE
#
class SettingsScreen:
    """Handles the settings screen"""
    def __init__(self):

        self.texts = {
            'title': objects.Text(
                text="SETTINGS",
                font=pygame.font.Font(None, 74),
                x=settings.SCREEN_WIDTH // 2,
                y=100,
                color=(255,255,255),
                align="center"
            )
        }

        self.buttons = {
            "back": objects.Button(50, settings.SCREEN_HEIGHT - 80, 150, 50, "BACK", color=(255,255,255), hover_color=(0,0,0)),
            "login": objects.Button(settings.SCREEN_WIDTH//2+300, settings.SCREEN_HEIGHT-40, 150, 40, "Login", color=(255,255,255), hover_color=(0,0,0)),
            "logout": objects.Button(settings.SCREEN_WIDTH//2-75, settings.SCREEN_HEIGHT-40, 150, 40, "Logout", color=(255,255,255), hover_color=(0,0,0))

        }


        self.volume_slider = objects.Slider(
            x=settings.SCREEN_WIDTH // 2 - 150,
            y=250,
            width=300,
            height=10,
            min_val=0,
            max_val=100,
            initial_val=settings.load_settings()['volume'],
            label="Volume (WIP)",
            suffix=" %",
            font=pygame.font.Font(None, 24),
            color=(255, 255, 255),
            bg_color=(50, 50, 50),
            handle_color=(255, 255, 255),
            handle_hover_color=(200, 200, 200)
        )


        self.username_input = objects.InputField(
            x=settings.SCREEN_WIDTH//2-300, 
            y=settings.SCREEN_HEIGHT-40, 
            width=300, 
            height=40,
            placeholder="Username",
            max_length=128
        )
        self.password_input = objects.InputField(
            x=settings.SCREEN_WIDTH//2, 
            y=settings.SCREEN_HEIGHT-40, 
            width=300, 
            height=40,
            placeholder="Password",
            max_length=128,
            password=True
        )
    
    def handle_event(self, event, mouse_pos):
        self.volume_slider.handle_event(event, mouse_pos)
        if self.buttons['back'].is_clicked(mouse_pos, event):
            return GameState.MAIN_MENU
        
        settings.save_setting("volume", self.volume_slider.get_value())

        username = self.username_input.handle_event(event)
        password = self.password_input.handle_event(event)
        if (username or password) == "submit" or self.buttons['login'].is_clicked(mouse_pos, event):
            user = db_handling.query_rows(db_handling.UserModel, {'username': self.username_input.get_text()})
            user = user[0] if user else None
            if user and user.check_password(self.password_input.get_text()):
                settings.save_setting("username", self.username_input.get_text())
                settings.save_setting("password", self.password_input.get_text())
                settings.save_setting("logged_in", True)
                self.username_input.clear()
                self.password_input.clear()
            else:
                print("ERR")

        if self.buttons['logout'].is_clicked(mouse_pos, event):
            settings.save_setting("username", "Anonymous")
            settings.save_setting("password", "")
            settings.save_setting("logged_in", False)
        
        return GameState.SETTINGS
    
    def draw(self, screen, mouse_pos):
        screen.fill(settings.BLACK)
        
        self.volume_slider.check_hover(mouse_pos)
        self.volume_slider.draw(screen)

        for button in self.buttons.values():
            button.check_hover(mouse_pos)
            button.draw(screen)

        if settings.load_settings()["logged_in"]:
            self.buttons['logout'].set_visibility(True, True)
            self.buttons['login'].set_visibility(False, False)
        else:
            self.buttons['login'].set_visibility(True, True)
            self.buttons['logout'].set_visibility(False, False)
            self.username_input.draw(screen)
            self.password_input.draw(screen)


        for text in self.texts.values():
            text.draw(screen)

    def update(self):
        self.username_input.update()
        self.password_input.update()













#
#   PLAY STATE
#
class PlayScreen:
    """GAME STATE"""
    def __init__(self):
        self.playing = True


        self.clue = None
        self.actual = None
        self.last_debt = 10
        self.current_debt = 10

        self.temporary_storage = 0
        self.permanent_storage = 0

        self.level = 1
        self.score = 0
        self.started_at = datetime.datetime.now()


        



        self.timer_manager = objects.TimerManager()
        self.timer_manager.add_timer("win_flash", 2000, self._reset)
        self.timer_manager.add_timer("lose_flash", 2000, self._reset)

        self.announcement_flash = objects.TimerSequence()
        for i in range(4):
            self.announcement_flash.add_step(250, lambda: self.texts['announcement'].set_alpha(0))
            self.announcement_flash.add_step(250, lambda: self.texts['announcement'].set_alpha(255))
            i += 1
        self.announcement_flash.add_step(500, lambda: self.texts['announcement'].set_visibility(False))

        self.time_remaining = 200
        self.timer_manager.add_timer("timer", 1000, self._timer)
        self.timer_manager.start_timer("timer")

        self.strikes = 0
        self.table = objects.LeaderboardTable(x=settings.SCREEN_WIDTH//2, y=settings.SCREEN_HEIGHT//2+300, width=int(settings.SCREEN_WIDTH*0.8), height=100, columns=["Rank", "User", "Level", "Score", "Date"], center_x=True, center_y=False, visible=False)
        



        self.texts = {
            'announcement': objects.Text(
                    text="DEBT",
                    x=settings.SCREEN_WIDTH//2,
                    y=settings.SCREEN_HEIGHT//2,
                    font=pygame.font.Font(None, 76),
                    bg_color=(0,0,0, 196),
                    padding=settings.SCREEN_WIDTH,
                    visible=False
                ),
            'debt': objects.Text(
                    text=str(self.current_debt),
                    x=settings.SCREEN_WIDTH//2,
                    y=100,
                    font=pygame.font.Font(None, 36),
                    prefix="DEBT: "
                ),
            'temporary_storage': objects.Text(
                    text=str(self.temporary_storage),
                    x=10,
                    y=10,
                    font=pygame.font.Font(None, 36),
                    align="topleft",
                    prefix="TEMPORARY: "
                ),
            'permanent_storage': objects.Text(
                text=str(self.permanent_storage),
                x=10,
                y=40,
                font=pygame.font.Font(None, 36),
                align="topleft",
                prefix="STORED: "
            ),
            'clue': objects.Text(
                    text="Begin",
                    x=settings.SCREEN_WIDTH//2,
                    y=250,
                    font=pygame.font.Font(None, 24)
            ),
            'timer': objects.Text(
                    text=str(self.time_remaining),
                    prefix="Remaining time: ",
                    x=settings.SCREEN_WIDTH,
                    y=0,
                    font=pygame.font.Font(None, 24),
                    align="topright"
                )
            ,
            'strikes': objects.Text(
                    text=str(self.strikes),
                    prefix="Strikes: ",
                    x=settings.SCREEN_WIDTH,
                    y=24,
                    font=pygame.font.Font(None, 24),
                    align="topright"
                )

        }

        self.buttons = {
            'start': objects.Button(
                    x=settings.SCREEN_WIDTH//2 - 50, 
                    y=settings.SCREEN_HEIGHT//2 - 50, 
                    width=100, 
                    height=100, 
                    text="Start", 
                    font=pygame.font.Font(None, 24),
                    color=(255,255,255), 
                    hover_color=(0,0,0), 
                    bg_color=(0,0,0), 
                    bg_hover_color=(255,255,255)
                ),
            'greater': objects.Button(
                    x=settings.SCREEN_WIDTH//2 + 50, 
                    y=settings.SCREEN_HEIGHT//2 - 50, 
                    width=50, 
                    height=50, 
                    text="Greater", 
                    font=pygame.font.Font(None, 16),
                    color=(255,255,255), 
                    hover_color=(0,0,0), 
                    bg_color=(0,0,0), 
                    bg_hover_color=(255,255,255)
                ),
            'lower': objects.Button(
                    x=settings.SCREEN_WIDTH//2 + 50, 
                    y=settings.SCREEN_HEIGHT//2, 
                    width=50, 
                    height=50, 
                    text="Lower", 
                    font=pygame.font.Font(None, 16),
                    color=(255,255,255), 
                    hover_color=(0,0,0), 
                    bg_color=(0,0,0), 
                    bg_hover_color=(255,255,255)
                ),
            'transfer': objects.Button(
                    x=settings.SCREEN_WIDTH//2-150, 
                    y=settings.SCREEN_HEIGHT-50, 
                    width=100, 
                    height=50, 
                    text="Transfer", 
                    font=pygame.font.Font(None, 16),
                    color=(255,255,255), 
                    hover_color=(0,0,0), 
                    bg_color=(0,0,0), 
                    bg_hover_color=(255,255,255)
                ),
            'pay_off': objects.Button(
                    x=settings.SCREEN_WIDTH//2+50, 
                    y=settings.SCREEN_HEIGHT-50, 
                    width=100, 
                    height=50, 
                    text="Pay", 
                    font=pygame.font.Font(None, 16),
                    color=(255,255,255), 
                    hover_color=(0,0,0), 
                    bg_color=(0,0,0), 
                    bg_hover_color=(255,255,255)
                )
        }


    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons['start'].is_clicked(mouse_pos, event):
                self.buttons['start'].set_enabled(False)
                self._generate_numbers()
            elif self.buttons['greater'].is_clicked(mouse_pos, event):
                self._guess_greater()
            elif self.buttons['lower'].is_clicked(mouse_pos, event):
                self._guess_lower()
            elif self.buttons['transfer'].is_clicked(mouse_pos, event):
                self._transfer()
            elif self.buttons['pay_off'].is_clicked(mouse_pos, event):
                self._pay()
        return GameState.PLAY
    
    def draw(self, screen, mouse_pos):
        screen.fill(settings.BLACK)

        for text in self.texts.values():
            text.draw(screen)

        for button in self.buttons.values():
            button.check_hover(mouse_pos)
            button.draw(screen)

        self.table.draw(screen)

        self.texts['announcement'].draw(screen)

    def update(self):
        self.timer_manager.update_all()
        self.announcement_flash.update()


        if self.playing != True:
            self.playing = True
            return GameState.MAIN_MENU
        
        return GameState.PLAY


    # GAME FUNCTIONS
    def _generate_numbers(self):
        self.actual = random.randint(1,20)
        self.clue = random.randint(1,20)
        while self.actual == self.clue:
            self.clue = random.randint(1,20)
        self.texts['clue'].set_text(str(self.clue))
        self.texts['clue'].set_visibility(True)

        self.buttons['transfer'].set_enabled(False)
        self.buttons['pay_off'].set_enabled(False)

    def _guess_greater(self):
        if self.clue is not None and self.actual is not None:
            if self.clue < self.actual:
                self._win()
            else:
                self._lose()


    def _guess_lower(self):
        if self.clue is not None and self.actual is not None:
            if self.clue > self.actual:
                self._win()
            else:
                self._lose()

    def _win(self):
        self.texts['clue'].set_color((0,255,0))
        self.timer_manager.start_timer("win_flash")
        self.temporary_storage += 1
        self.score += 1
        self.actual = None
        self.texts['temporary_storage'].set_text(str(self.temporary_storage))

    def _lose(self):
        self.texts['clue'].set_color((255,0,0))
        self.timer_manager.start_timer("lose_flash")
        self.temporary_storage = 0
        self.actual = None
        self.texts['temporary_storage'].set_text(str(self.temporary_storage))

    def _reset(self):
        self.texts['clue'].set_color((255, 255, 255))
        self.texts['clue'].set_text("ROLL")
        self.buttons['start'].set_enabled(True)
        self.buttons['transfer'].set_enabled(True)
        self.buttons['pay_off'].set_enabled(True)



    def _transfer(self):
        [button.set_enabled(False) for button in self.buttons.values()]
        if self.temporary_storage != 0:
            self.timer_manager.add_timer("transfer_timer", 1000, self._transfer)
            self.timer_manager.start_timer("transfer_timer")
            self.permanent_storage += 1
            self.temporary_storage -= 1
            self.texts['permanent_storage'].set_text(str(self.permanent_storage))
            self.texts['temporary_storage'].set_text(str(self.temporary_storage))
        else:
            [button.set_enabled(True) for button in self.buttons.values()]

    def _pay(self):
        [button.set_enabled(False) for button in self.buttons.values()]
        if self.current_debt != 0 and self.permanent_storage != 0:
            self.current_debt -= 1
            self.permanent_storage -= 1
            self.timer_manager.add_timer("pay_timer", 1000, self._pay)
            self.timer_manager.start_timer("pay_timer")
            self.texts['debt'].set_text(str(self.current_debt))
            self.texts['permanent_storage'].set_text(str(self.permanent_storage))
        elif self.current_debt == 0:
            [button.set_enabled(True) for button in self.buttons.values()]
            self._advance_level()
        else:
            [button.set_enabled(True) for button in self.buttons.values()]

        
            


    def _advance_level(self):
        self.timer_manager.delay(0, lambda: self.texts['announcement'].set_visibility(True))
        self.timer_manager.delay(0, lambda: self.texts['announcement'].set_text("DEBT RAISED"))
        self.current_debt = int(self.last_debt * 1.5)
        self.last_debt = self.current_debt
        self.texts['debt'].set_text(str(self.current_debt))
        self.timer_manager.delay(2000, lambda: self.texts['announcement'].set_text(str(self.current_debt)))
        self.timer_manager.delay(2000, lambda: self.announcement_flash.start())
        self.time_remaining +=  100


    def _stop_playing(self):
        self.playing = False

    def _end_round(self):
        for button in self.buttons.values():
            button.set_enabled(False)
        self.timer_manager.delay(0, lambda: self.texts['announcement'].set_text(""))
        self.timer_manager.delay(0, lambda: self.texts['announcement'].set_visibility(True))
        self.timer_manager.delay(2000, lambda: self.texts['announcement'].set_text("GAME"))
        self.timer_manager.delay(4000, lambda: self.texts['announcement'].set_text("GAME OVER"))
        self.table.set_data([{
                    "User": settings.load_settings()['username'],
                    "Level": self.level,
                    "Score": self.score,
                    "Date": self.started_at
                }])
        db_handling.insert_row(db_handling.GameSessionModel, {
                'user_id': db_handling.query_rows(db_handling.UserModel, {"username": settings.load_settings()["username"]})[0].id,
                'started_at': self.started_at,
                'score': self.score,
                'level_reached': self.level
            })
        self.timer_manager.delay(6000, lambda: self.table.set_visibility(True))
        self.timer_manager.delay(10000, lambda: self._stop_playing())
        

    def _timer(self):
        if self.time_remaining <= 0:
            self._end_round()
        else:
            self.time_remaining -= 1
            self.texts['timer'].set_text(str(self.time_remaining))
            self.timer_manager.delay(1000, self._timer)














#
#   LEADERBOARDS STATE
#
class LeaderboardScreen:
    """Handles the leaderboard screen"""
    def __init__(self):
        self.back_button = objects.Button(50, settings.SCREEN_HEIGHT - 80, 150, 50, "BACK", color=(255,255,255), hover_color=(0,0,0))
        self.table = objects.LeaderboardTable(x=settings.SCREEN_WIDTH//2, y=settings.SCREEN_HEIGHT//2, width=int(settings.SCREEN_WIDTH*0.8), height=400, columns=["Rank", "User", "Level", "Score", "Date"], center_x=True, center_y=True)
        unsorted_data = db_handling.query_rows(db_handling.GameSessionModel, include=['user'])
        sorted_data = sorted(unsorted_data, key=lambda x: (-x['level_reached'], -x['score']))
        leaderboard_data = []
        i = 1
        for row in sorted_data:
            leaderboard_data.append(
                {
                    "Rank": i,
                    "User": row['user']['username'],
                    "Level": row['level_reached'],
                    "Score": row['score'],
                    "Date": row['started_at']
                }
            )
            i += 1

        self.table.set_data(leaderboard_data)

        self.texts = {
            'title': objects.Text(
                text="LEADERBOARD",
                font=pygame.font.Font(None, 74),
                x=settings.SCREEN_WIDTH // 2,
                y=100,
                color=(255,255,255),
                align="center"
            )
        }

    
    def handle_event(self, event, mouse_pos):
        self.table.handle_event(event, mouse_pos)
        if self.back_button.is_clicked(mouse_pos, event):
            return GameState.MAIN_MENU
        return GameState.LEADERBOARD
    
    def draw(self, screen, mouse_pos):
        screen.fill(settings.BLACK)
                
        self.table.check_hover(mouse_pos)
        self.table.draw(screen)
        
        # Back button
        self.back_button.check_hover(mouse_pos)
        self.back_button.draw(screen)

        for text in self.texts.values():
            text.draw(screen)


















#
#   MAIN GAME CLASS
#
class Game:
    """Main game class that manages all screens and game loop"""
    def __init__(self):
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize screens
        self.intro = IntroScreen()
        self.main_menu = MainMenuScreen()
        self.settings = SettingsScreen()
        self.play = PlayScreen()
        self.leaderboard = LeaderboardScreen()
        
        # Start with intro
        self.state = GameState.INTRO
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            
            
            if self.state == GameState.INTRO and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
                self.state = GameState.MAIN_MENU
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.PLAY and (event.key == pygame.K_ESCAPE):
                    self.state = GameState.MAIN_MENU
            
            # Handle events based on current state
            elif self.state == GameState.MAIN_MENU:
                new_state = self.main_menu.handle_event(event, mouse_pos)
                # Create a fresh PlayScreen when transitioning to PLAY

                if new_state == GameState.PLAY:
                    self.play = PlayScreen()
                if new_state == GameState.LEADERBOARD:
                    self.leaderboard = LeaderboardScreen()
                self.state = new_state
            elif self.state == GameState.SETTINGS:
                self.state = self.settings.handle_event(event, mouse_pos)
            elif self.state == GameState.PLAY:
                self.state = self.play.handle_event(event, mouse_pos)
            elif self.state == GameState.LEADERBOARD:
                self.state = self.leaderboard.handle_event(event, mouse_pos)
            
            # QUIT STATE
            if self.state == GameState.QUIT:
                self.running = False
    
    def update(self):
        if self.state == GameState.INTRO:
            self.state = self.intro.update()
        elif self.state == GameState.PLAY:
            self.state = self.play.update()
    
    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        
        if self.state == GameState.INTRO:
            self.intro.draw(self.screen)
        elif self.state == GameState.MAIN_MENU:
            self.main_menu.draw(self.screen, mouse_pos)
        elif self.state == GameState.SETTINGS:
            self.settings.draw(self.screen, mouse_pos)
        elif self.state == GameState.PLAY:
            self.play.draw(self.screen, mouse_pos)
        elif self.state == GameState.LEADERBOARD:
            self.leaderboard.draw(self.screen, mouse_pos)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(settings.FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()