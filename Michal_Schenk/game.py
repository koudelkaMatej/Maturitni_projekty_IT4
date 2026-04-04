import pygame
import sys
from enum import Enum
import random
import datetime

import settings
import objects

import db_handling
from db_handling import UserModel as User

# Initialize Logger
import logger
log = logger.get_logger("game")



# Initialize Pygame
pygame.init()
pygame.mixer.init()



def play_sound(sound:str):
    """Play a specified SFX.mp3 from assets/sfx/

    Args:
        sound (str): name of the .mp3 file to play
    """    
    try:
        sfx = pygame.mixer.Sound(f"assets/sfx/{sound}.mp3")
        sfx.set_volume(settings.load_settings()['volume-sfx'])
        sfx.play()
        return True
    except FileNotFoundError:
        log.warning(f"FILE {sound}.mp3 NOT FOUND")
        return "failure"
    except Exception as e:
        log.warning(e)
        return "failure"


def play_music(music:str, loops:int=-1, fade_ms:int=0):
    """Play a specified MUSIC.mp3 from assets/sfx/

    Args:
        music (str): music filename to play
        loops (int, optional): Number of loops to play. Defaults to -1 (inf).
        fade_ms (int, optional): !!!. Defaults to 0 (ms).
    """
    try:
        if music:
            pygame.mixer.music.load(f"assets/music/{music}.mp3")
            pygame.mixer.music.set_volume(settings.load_settings()['volume-music'])
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            return True
    except FileNotFoundError:
        log.warning(f"FILE {music}.mp3 NOT FOUND")
        return "failure"
    except Exception as e:
        log.warning(e)
        return "failure"

def change_volume(group:str, volume:float):
    """Change the current volume and save it to user_settings.json

    Args:
        group (str): volume group, must be one of the following: sfx, music
        volume (float): the volume, must be between 0.0 and 1.0
    """    
    if group == "music":
        pygame.mixer.music.set_volume(volume)
    settings.save_setting(f"volume-{group}", volume)



class GameState(Enum):
    """Represents the different high-level states of the game. This enum is used to control which screen or mode is currently active.

    The values indicate transitions such as intro, main menu, gameplay, settings, leaderboard display, or quitting the game.
    """
    INTRO = 1
    MAIN_MENU = 2
    SETTINGS = 3
    PLAY = 4
    LEADERBOARD = 5
    QUIT = 6




class IntroScreen:
    """INTRO STATE"""
    def __init__(self, set_state):    
        self.set_state = set_state

        self.alpha = 0
        self.fade_speed = 3
        self.display_time = 0
        self.max_display_time = settings.FPS * 3.6

        self.texts = {
            'title': objects.Text(
                text=settings.GAME_TITLE,
                font=pygame.font.Font(None, 74),
                x=settings.SCREEN_WIDTH // 2,
                y=settings.SCREEN_HEIGHT // 2,
            ),
            'subtitle': objects.Text(
                text="Press any key to skip",
                x=settings.SCREEN_WIDTH // 2,
                y=settings.SCREEN_HEIGHT // 2 + 30,
                color=(128,128,128),
            ),
            'inspiration_credit': objects.Text(
                text="Inspired by FLATHEAD @ Tim Oxton",
                x=settings.SCREEN_WIDTH // 2,
                y=settings.SCREEN_HEIGHT - 20,
            )
        }
        log.info("INTRO SCREEN created")
        
    def update(self):
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed)
        self.display_time += 1
        
        if self.display_time >= self.max_display_time:
            self.set_state(GameState.MAIN_MENU)
    
    def draw(self, screen):
        screen.fill(settings.BLACK)

        for text in self.texts.values():
            text.set_alpha(self.alpha)
            text.draw(screen)
























class MainMenuScreen():
    """MAIN MENU STATE"""
    def __init__(self, set_state):
        # THE ESSENTIALS
        self.set_state = set_state
        self.timer_manager = objects.TimerManager()

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
                    text="PLAY"
                ),
            'settings': objects.Button(
                    x=button_x, 
                    y=start_y + spacing, 
                    width=button_width, 
                    height=button_height, 
                    text="SETTINGS"
                ),
            'leaderboard': objects.Button(
                    x=button_x, 
                    y=start_y + spacing * 2, 
                    width=button_width, 
                    height=button_height, 
                    text="LEADERBOARD"
                ),
            'quit': objects.Button(
                    x=button_x, 
                    y=start_y + spacing * 3, 
                    width=button_width, 
                    height=button_height, 
                    text="QUIT"
                )
        }
    
        self.texts = {
            'title': objects.Text(
                text=settings.GAME_TITLE,
                font=pygame.font.Font(None, 74),
                x=settings.SCREEN_WIDTH // 2,
                y=100
            ),
            'copyright': objects.Text(
                text="Copyright © 2026 Michal Schenk",
                x=settings.SCREEN_WIDTH-10,
                y=settings.SCREEN_HEIGHT-10,
                align="bottomright"
            ),
            'user': objects.Text(
                text=self.check_login_status(),
                prefix="Logged in as: ",
                x=settings.SCREEN_WIDTH//2,
                y=settings.SCREEN_HEIGHT-10,
                align="bottom"
            )
        }
        log.info("MAIN MENU SCREEN created")

    def check_login_status(self):
        if settings.load_settings()["logged_in"]:
            return settings.load_settings()["username"]
        else:
            return "Anonymous"

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons['play'].is_clicked(mouse_pos, event):
                play_music("play")
                self.set_state(GameState.PLAY)

            elif self.buttons['settings'].is_clicked(mouse_pos, event):
                self.set_state(GameState.SETTINGS)

            elif self.buttons['leaderboard'].is_clicked(mouse_pos, event):
                self.set_state(GameState.LEADERBOARD)

            elif self.buttons['quit'].is_clicked(mouse_pos, event):
                self.timer_manager.delay(250, lambda: self.set_state(GameState.QUIT))
    
    def draw(self, screen, mouse_pos):
        screen.fill(settings.BLACK)
        
        for button in self.buttons.values():
            button.check_hover(mouse_pos)
            button.draw(screen)

        for text in self.texts.values():
            text.draw(screen)

    def update(self):
        self.timer_manager.update_all()

    




















class SettingsScreen:
    """SETTINGS STATE"""
    def __init__(self, set_state):
        # THE ESSENTIALS
        self.set_state = set_state
        self.timer_manager = objects.TimerManager()

        self.buttons = {
            "back": objects.Button(50, settings.SCREEN_HEIGHT - 80, 150, 50, "BACK"),
            "login": objects.Button(settings.SCREEN_WIDTH//2+300, settings.SCREEN_HEIGHT-40, 150, 40, "Login", silenced=True),
            "logout": objects.Button(settings.SCREEN_WIDTH//2-75, settings.SCREEN_HEIGHT-40, 150, 40, "Logout", enabled=False, visible=False)
        }

        self.username_input = objects.InputField(
            x=settings.SCREEN_WIDTH//2-300, 
            y=settings.SCREEN_HEIGHT-40, 
            width=300, 
            placeholder="Username",
            max_length=128,
            border_radius=0
        )
        self.password_input = objects.InputField(
            x=settings.SCREEN_WIDTH//2, 
            y=settings.SCREEN_HEIGHT-40, 
            width=300, 
            placeholder="Password",
            max_length=128,
            password=True,
            border_radius=0
        )

        self.check_login_status()




        self.texts = {
            'title': objects.Text(
                text="SETTINGS",
                font=pygame.font.Font(None, 74),
                x=settings.SCREEN_WIDTH // 2,
                y=100
            ),
            'announcement': objects.Text(
                text="",
                x=settings.SCREEN_WIDTH//2,
                y=settings.SCREEN_HEIGHT//2,
                font=pygame.font.Font(None, 36),
                bg_color=(0,0,0, 196),
                padding=settings.SCREEN_WIDTH,
                visible=False
            )
        }

        
        initial_settings = settings.load_settings()


        self.sliders = {
            "volume_music_slider": objects.Slider(
                x=settings.SCREEN_WIDTH // 2 - 150,
                y=250,
                width=300,
                height=10,
                min_val=0,
                max_val=100,
                initial_val=initial_settings['volume-music']*100,
                label="Music Volume",
                suffix=" %"
            ),
            "volume_sfx_slider": objects.Slider(
                x=settings.SCREEN_WIDTH // 2 - 150,
                y=300,
                width=300,
                height=10,
                min_val=0,
                max_val=100,
                initial_val=initial_settings['volume-sfx']*100,
                label="Sound Effects Volume",
                suffix=" %"
            )
        }
        log.info("SETTINGS SCREEN created")
    

    def check_login_status(self):
            # Check login status on init
            if settings.load_settings()["logged_in"]:
                self.buttons['logout'].set_visibility(True, True)
                self.buttons['login'].set_visibility(False, False)
                self.username_input.set_visibility(False)
                self.password_input.set_visibility(False)
            else:
                self.buttons['login'].set_visibility(True, True)
                self.buttons['logout'].set_visibility(False, False)
                self.username_input.set_visibility(True)
                self.password_input.set_visibility(True)
            
        
    
    def handle_event(self, event, mouse_pos):
        for slider in self.sliders.values():
            slider.handle_event(event, mouse_pos)

        if self.buttons['back'].is_clicked(mouse_pos, event):
            self.set_state(GameState.MAIN_MENU)
        
        if self.sliders['volume_music_slider'].dragging:
            change_volume(group="music", volume=self.sliders['volume_music_slider'].get_value()/100)
        elif self.sliders['volume_sfx_slider'].dragging:
            change_volume(group="sfx", volume=self.sliders['volume_sfx_slider'].get_value()/100)

        username = self.username_input.handle_event(event)
        password = self.password_input.handle_event(event)
        if username == "submit" or password == "submit" or self.buttons['login'].is_clicked(mouse_pos, event):
            user = db_handling.query_rows(db_handling.UserModel, {'username': self.username_input.get_text()})
            user = user[0] if user else None
            if user and user.check_password(self.password_input.get_text()):
                settings.save_setting("username", self.username_input.get_text())
                settings.save_setting("password", self.password_input.get_text())
                settings.save_setting("logged_in", True)
                play_sound("success-sfx")
                self.username_input.clear()
                self.password_input.clear()
                self.timer_manager.delay(0, lambda: self.texts['announcement'].set_visibility(True))
                self.timer_manager.delay(0, lambda: self.texts['announcement'].set_text("Successfully logged in, please restart the game"))
                self.timer_manager.delay(2500, lambda: self.texts['announcement'].set_visibility(False))
                self.check_login_status()
                log.info("USER LOGGED IN")
            else:
                log.info("INCORRECT LOG IN")
                play_sound("failure-sfx")
                # Maybe a message

        if self.buttons['logout'].is_clicked(mouse_pos, event):
            settings.save_setting("username", "Anonymous")
            settings.save_setting("password", "")
            settings.save_setting("logged_in", False)
            play_sound("success-sfx")
            self.timer_manager.delay(0, lambda: self.texts['announcement'].set_visibility(True))
            self.timer_manager.delay(0, lambda: self.texts['announcement'].set_text("Successfully logged out, please restart the game"))
            self.timer_manager.delay(2500, lambda: self.texts['announcement'].set_visibility(False))
            self.check_login_status()
            log.info("USER LOGGED OUT")
            
            
    
    def draw(self, screen, mouse_pos):
        screen.fill(settings.BLACK)
        
        for slider in self.sliders.values():
            slider.check_hover(mouse_pos)
            slider.draw(screen)

        for button in self.buttons.values():
            button.check_hover(mouse_pos)
            button.draw(screen)
        
        for text in self.texts.values():
            text.draw(screen)

        self.username_input.draw(screen)
        self.password_input.draw(screen)

    def update(self):
        self.timer_manager.update_all()
        self.username_input.update()
        self.password_input.update()











class PlayScreen:
    """PLAY STATE"""
    def __init__(self, set_state):
        # THE ESSENTIALS
        self.set_state = set_state
        self.timer_manager = objects.TimerManager()
        


        self.clue = None
        self.actual = None
        self.last_debt = 10
        self.current_debt = 10

        self.temporary_storage = 0
        self.permanent_storage = 0

        self.level = 1
        self.score = 0
        self.strikes = 0
        self.multiplier = lambda: (self.permanent_storage // 5) + 1
        
        self.effectors = {
                "insta_pay": {
                    "name": "Insta Pay",
                    "description": "Instantly pays the debt, no waiting.",
                    "level": 0
                },
                "insta_transfer": {
                    "name": "Insta Transfer",
                    "description": "Instantly transfers the points, no waiting.",
                    "level": 0
                },
                "another_chance": {
                    "name": "I Don't Think So",
                    "description": "A small chance to turn a loss into a win.",
                    "level": 0
                },
                "no_locks": {
                    "name": "I'm Free!",
                    "description": "Allows to do transfer while rolling.",
                    "level": 0
                }
            }
        self.salvage_chance = lambda: self.effectors['another_chance'].get('level', 0)/(self.effectors['another_chance'].get('level', 0)+5)
        
        
        

        



        self.started_at = datetime.datetime.now()

        self.timer_manager.add_timer("win_flash", 2000, self._reset)
        self.timer_manager.add_timer("lose_flash", 2000, self._reset)

        self.announcement_flash = objects.TimerSequence()
        for i in range(4):
            self.announcement_flash.add_step(250, lambda: self.texts['announcement'].set_alpha(0))
            self.announcement_flash.add_step(250, lambda: self.texts['announcement'].set_alpha(255))
            i += 1
        self.announcement_flash.add_step(500, lambda: self.texts['announcement'].set_visibility(False))

        self.time_remaining = 200
        self.advance_timer = True
        self.timer_manager.add_timer("timer", 1000, self._timer)
        self.timer_manager.start_timer("timer")

        
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
            'multiplier': objects.Text(
                text=str(self.multiplier()),
                x=10,
                y=70,
                font=pygame.font.Font(None, 36),
                align="topleft",
                prefix="MULTIPLIER: "
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
            ),
            'strikes': objects.Text(
                text=str(self.strikes),
                prefix="Strikes: ",
                x=settings.SCREEN_WIDTH,
                y=24,
                font=pygame.font.Font(None, 24),
                align="topright",
                suffix="/5"
            ),
            'skill_descriptor': objects.Text(
                text="",
                x=settings.SCREEN_WIDTH // 2,
                y=settings.SCREEN_HEIGHT//2+50,
                font=pygame.font.Font(None, 24),
                align="center"
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
        log.info("PLAY SCREEN created")


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
    
    def draw(self, screen, mouse_pos):
        screen.fill(settings.BLACK)

        for text in self.texts.values():
            text.draw(screen)

        for button in self.buttons.values():
            button.check_hover(mouse_pos)
            button.draw(screen)

        self.texts['announcement'].draw(screen)
        self.texts['skill_descriptor'].draw(screen)
        self.table.draw(screen)

    def update(self):
        self.timer_manager.update_all()
        self.announcement_flash.update()


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
        log.info("GENERATED NUMBERS")
        log.debug(f"GENERATED NUMBERS  [{self.clue}, {self.actual}]")

    def _guess_greater(self):
        log.debug("GUESSED GREATER")
        if self.clue is not None and self.actual is not None:
            if self.clue < self.actual:
                self._win()
                play_sound("success-sfx")
            else:
                self._lose()
                play_sound("failure-sfx")


    def _guess_lower(self):
        log.debug("GUESSED LOWER")
        if self.clue is not None and self.actual is not None:
            if self.clue > self.actual:
                self._win()
                play_sound("success-sfx")
            else:
                self._lose()
                play_sound("failure-sfx")

    def _win(self, chance_override=False):
        self.texts['clue'].set_color((255,255,0) if chance_override else (0,255,0))
        self.timer_manager.start_timer("win_flash")
        self.temporary_storage += self.multiplier()
        self.score += self.multiplier()
        self.actual = None
        self.texts['temporary_storage'].set_text(str(self.temporary_storage))
        self.strikes = max(0, self.strikes-1)
        self.texts['strikes'].set_text(str(self.strikes))
        log.info("CORRECT GUESS")

    def _lose(self):
        log.info("INCORRECT GUESS")
        if self.effectors['another_chance'].get('level', 0) > 0:
            if random.random() < self.salvage_chance():
                log.info("USED SKILL - OVERRIDE LOSS TO WIN")
                self._win(True)
            else:
                self.texts['clue'].set_color((255,0,0))
                self.timer_manager.start_timer("lose_flash")
                self.temporary_storage = 0
                self.actual = None
                self.texts['temporary_storage'].set_text(str(self.temporary_storage))
                self.strikes += 1
                self.texts['strikes'].set_text(str(self.strikes))
        else:    
            self.texts['clue'].set_color((255,0,0))
            self.timer_manager.start_timer("lose_flash")
            self.temporary_storage = 0
            self.actual = None
            self.texts['temporary_storage'].set_text(str(self.temporary_storage))
            self.strikes += 1
            self.texts['strikes'].set_text(str(self.strikes))

        if self.strikes == 5:
            self._end_round("TOO MANY STRIKES")

    def _reset(self):
        self.texts['clue'].set_color((255, 255, 255))
        self.texts['clue'].set_text("ROLL")
        self.buttons['start'].set_enabled(True)
        self.buttons['transfer'].set_enabled(True)
        self.buttons['pay_off'].set_enabled(True)



    def _transfer(self):
        log.debug("TRANSFERING")
        if self.effectors['no_locks']['level'] != 1:
            [button.set_enabled(False) for button in self.buttons.values()]
        self.buttons['transfer'].set_enabled(False)
        if self.temporary_storage != 0:
            if self.effectors['insta_transfer']['level'] >= 1:
                while self.temporary_storage > 0:
                    self.permanent_storage += 1
                    self.temporary_storage -= 1
                    self.texts['permanent_storage'].set_text(str(self.permanent_storage))
                    self.texts['temporary_storage'].set_text(str(self.temporary_storage))
                [button.set_enabled(True) for button in self.buttons.values()]
            else:
                self.timer_manager.add_timer("transfer_timer", 1000, self._transfer)
                self.timer_manager.start_timer("transfer_timer")
                self.permanent_storage += 1
                self.temporary_storage -= 1
                self.texts['permanent_storage'].set_text(str(self.permanent_storage))
                self.texts['temporary_storage'].set_text(str(self.temporary_storage))           
        else:
            [button.set_enabled(True) for button in self.buttons.values()]
        self.texts['multiplier'].set_text(str(self.multiplier()))

    def _pay(self):
        log.debug("PAYING")
        if self.effectors['no_locks']['level'] != 1:
            [button.set_enabled(False) for button in self.buttons.values()]
        self.buttons['pay_off'].set_enabled(False)
        if self.current_debt != 0 and self.permanent_storage != 0:

            if self.effectors['insta_pay']['level'] >= 1:
                while self.current_debt > 0 and self.permanent_storage > 0:
                    self.current_debt -= 1
                    self.permanent_storage -= 1
                    self.texts['debt'].set_text(str(self.current_debt))
                    self.texts['permanent_storage'].set_text(str(self.permanent_storage))
                self._pay()
            else:
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
        self.texts['multiplier'].set_text(str(self.multiplier()))

        
            


    def _advance_level(self):
        log.info("ADVANCED LEVEL")
        self._stop_time()
        
        self.texts['announcement'].set_visibility(True)
        self.texts['announcement'].set_text("DEBT RAISED")
        self.current_debt = int(self.last_debt * 1.5)
        log.debug(f"NEW DEBT: {self.current_debt}")
        self.last_debt = self.current_debt
        self.texts['debt'].set_text(str(self.current_debt))
        self.timer_manager.delay(2000, lambda: self.texts['announcement'].set_text(str(self.current_debt)))
        self.timer_manager.delay(2000, lambda: self.announcement_flash.start())
        self.time_remaining +=  100
        self.level += 1

        # A chance to get a skill/effector
        picked_skill = self.effectors[list(self.effectors.keys())[random.randrange(0, len(self.effectors.values()))]]
        picked_skill['level'] += 1
        log.debug(f"ACQUIRED SKILL: {picked_skill}")
        self.timer_manager.delay(5000, lambda: self.texts['announcement'].set_visibility(True))
        self.timer_manager.delay(5000, lambda: self.texts['announcement'].set_text("NEW SKILL"))

        self.timer_manager.delay(6000, lambda: self.texts['announcement'].set_text(f"{picked_skill['name']} [LVL: {picked_skill['level']}]"))
        self.timer_manager.delay(6500, lambda: self.texts['skill_descriptor'].set_text(picked_skill['description']))

        self.timer_manager.delay(9500, lambda: self.texts['announcement'].set_visibility(False))
        self.timer_manager.delay(9500, lambda: self.texts['skill_descriptor'].set_visibility(False))
        
        self.timer_manager.delay(9500, lambda: self._resume_time())
        log.debug("CONTINUING")


    def _stop_playing(self):
        self.set_state(GameState.MAIN_MENU)
        play_music("main_menu")

    def _end_round(self, reason:str):
        play_music("endgame", loops=0)
        for button in self.buttons.values():
            button.set_enabled(False)
        self.timer_manager.delay(0, lambda: self.texts['announcement'].set_text(""))
        self.timer_manager.delay(0, lambda: self.texts['announcement'].set_visibility(True))
        self.timer_manager.delay(2000, lambda: self.texts['announcement'].set_text("GAME"))
        self.timer_manager.delay(4000, lambda: self.texts['announcement'].set_text("GAME OVER"))

        for i in range(len(reason)):
            self.timer_manager.delay(6000+((3000//len(reason))*i), lambda i=i: self.texts['announcement'].set_text(reason[:i+1]))

        self.table.set_data([{
                    "User": settings.load_settings()['username'],
                    "Level": self.level,
                    "Score": self.score,
                    "Date": self.started_at
                }])
        try:
            db_handling.insert_row(db_handling.GameSessionModel, {
                    'user_id': db_handling.query_rows(db_handling.UserModel, {"username": settings.load_settings()["username"]})[0].id,
                    'started_at': self.started_at,
                    'score': self.score,
                    'level_reached': self.level
                })
        except Exception as e:
            print(f"Error: {e}")
        self.timer_manager.delay(10000, lambda: self.table.set_visibility(True))
        self.timer_manager.delay(15000, lambda: self._stop_playing())
        log.info("ENDED ROUND")
        log.debug(f"ENDED ROUND - REASON: {reason}")
        

    def _timer(self):
        if self.time_remaining <= 0:
            self._end_round("TIME RAN OUT")
        elif self.advance_timer:
            self.time_remaining -= 1
            self.texts['timer'].set_text(str(self.time_remaining))
            self.timer_manager.delay(1000, self._timer)
        else:
            self.timer_manager.delay(1000, self._timer)

    def _stop_time(self):
        self.advance_timer = False
    def _resume_time(self):
        self.advance_timer = True














#
#   LEADERBOARDS STATE
#
class LeaderboardScreen:
    """Handles the leaderboard screen"""
    def __init__(self, set_state):
        self.set_state = set_state



        self.back_button = objects.Button(50, settings.SCREEN_HEIGHT - 80, 150, 50, "BACK", color=(255,255,255), hover_color=(0,0,0))
        self.table = objects.LeaderboardTable(x=settings.SCREEN_WIDTH//2, y=settings.SCREEN_HEIGHT//2, width=int(settings.SCREEN_WIDTH*0.8), height=400, columns=["Rank", "User", "Level", "Score", "Date"], center_x=True, center_y=True)
        unsorted_data = db_handling.query_rows(db_handling.GameSessionModel, include=['user'])
        sorted_data = sorted(unsorted_data, key=lambda x: (-x['level_reached'], -x['score']))
        leaderboard_data = [
            {
                "Rank": i,
                "User": row['user']['username'],
                "Level": row['level_reached'],
                "Score": row['score'],
                "Date": row['started_at'],
            }
            for i, row in enumerate(sorted_data, start=1)
        ]

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
        log.info("LEADERBOARDS SCREEN created")

    def update(self):
        pass

    
    def handle_event(self, event, mouse_pos):
        self.table.handle_event(event, mouse_pos)
        if self.back_button.is_clicked(mouse_pos, event):
            self.set_state(GameState.MAIN_MENU)
    
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

        play_music(music="main_menu", fade_ms=1000)
        
        # Initialize screens
        self.intro = IntroScreen(set_state=self._set_state)
        self.main_menu = MainMenuScreen(set_state=self._set_state)
        self.settings = SettingsScreen(set_state=self._set_state)
        self.play = PlayScreen(set_state=self._set_state)
        self.leaderboard = LeaderboardScreen(set_state=self._set_state)

        # Start with Intro
        self.state = GameState.INTRO
        log.info("GAME INSTANCE created")
        
        
    def _set_state(self, new_state: GameState):
        if new_state == GameState.PLAY:
            self.play = PlayScreen(set_state=self._set_state)
        elif new_state == GameState.LEADERBOARD:
            self.leaderboard = LeaderboardScreen(set_state=self._set_state)
        self.state = new_state

        
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            
            if self.state == GameState.INTRO and event.type in [pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN]:
                self.state = GameState.MAIN_MENU
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.PLAY and (event.key == pygame.K_ESCAPE):
                    play_music("main_menu", -1)
                    self.state = GameState.MAIN_MENU
            
            elif self.state == GameState.MAIN_MENU:
                self.main_menu.handle_event(event, mouse_pos)

            elif self.state == GameState.SETTINGS:
                self.settings.handle_event(event, mouse_pos)

            elif self.state == GameState.PLAY:
                self.play.handle_event(event, mouse_pos)

            elif self.state == GameState.LEADERBOARD:
                self.leaderboard.handle_event(event, mouse_pos)
            
            elif self.state == GameState.QUIT:
                self.running = False
    
    def update(self):
        match self.state:
            case GameState.INTRO:
                self.intro.update()
            case GameState.MAIN_MENU:
                self.main_menu.update()
            case GameState.PLAY:
                self.play.update()
            case GameState.SETTINGS:
                self.settings.update()
            case GameState.LEADERBOARD:
                self.leaderboard.update()
            case GameState.QUIT | _:
                self.running = False
            
    
    def draw(self):
        mouse_pos = pygame.mouse.get_pos()

        match self.state:
            case GameState.INTRO:
                self.intro.draw(self.screen)
            case GameState.MAIN_MENU:
                self.main_menu.draw(self.screen, mouse_pos)
            case GameState.PLAY:
                self.play.draw(self.screen, mouse_pos)
            case GameState.SETTINGS:
                self.settings.draw(self.screen, mouse_pos)
            case GameState.LEADERBOARD:
                self.leaderboard.draw(self.screen, mouse_pos)
            case GameState.QUIT | _:
                self.running = False
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(settings.FPS)
        log.info("ENDING GAME")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()