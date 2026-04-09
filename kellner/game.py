import pygame
import sys
import math
import random
import os
import hashlib
import mysql.connector
from pripojeni import *

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
PURPLE = (200, 50, 200)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
CYAN = (0, 255, 255)

DB_FILE = "scores.txt"

class DatabaseManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.ensure_file_exists()
        self.db_config = {
            'user': USER,
            'password': PASSWORD,
            'host': HOST,
            'database': DATABASE
        }
        self.conn = None
        self.table_name = "Ubermosh"
        
        self._init_db()
        self._sync_scores()

    def _get_connection(self):
        try:
            if self.conn is None or not self.conn.is_connected():
                self.conn = mysql.connector.connect(**self.db_config)
            return self.conn
        except mysql.connector.Error as err:
            print(f"DB Connection Error: {err}")
            return None

    def _init_db(self):
        conn = self._get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        nickname VARCHAR(255) PRIMARY KEY,
                        score INT DEFAULT 0,
                        gamemode VARCHAR(50) DEFAULT 'Normal',
                        status VARCHAR(50) DEFAULT 'Registered',
                        password VARCHAR(255) NOT NULL
                    )
                """)
                conn.commit()
                
                # Verify table was created
                cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                count = cursor.fetchone()[0]
                print(f"✓ DB table '{self.table_name}' created/verified. Records: {count}")
                cursor.close()
            except mysql.connector.Error as err:
                print(f"✗ DB Init Error: {err}")
        else:
            print("✗ Warning: Could not connect to database during initialization.")

    def _sync_scores(self):
        """Bidirectional sync: uploads local scores to DB if higher, downloads DB scores to local if higher."""
        local_scores = self._read_scores_local()
        conn = self._get_connection()
        
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # 1. Upload local -> DB (if local score is higher)
                for name, data in local_scores.items():
                    cursor.execute(f"SELECT score, password FROM {self.table_name} WHERE nickname = %s", (name,))
                    result = cursor.fetchone()
                    
                    online_score = result['score'] if result else -1
                    stored_password = result['password'] if result else None
                    
                    if data['score'] >= online_score:
                        cursor.execute(f"""
                            INSERT INTO {self.table_name} (nickname, score, gamemode, status, password)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            score = VALUES(score),
                            gamemode = VALUES(gamemode),
                            status = VALUES(status)
                        """, (name, data['score'], data['mode'], data['status'], stored_password or ''))
                        print(f"Synced local {name} to DB (score: {data['score']})")
                
                # 2. Download DB -> local (if DB score is higher or user doesn't exist locally)
                cursor.execute(f"SELECT nickname, score, gamemode, status FROM {self.table_name}")
                db_records = cursor.fetchall()
                
                for record in db_records:
                    name = record['nickname']
                    db_score = record['score']
                    db_mode = record['gamemode']
                    db_status = record['status']
                    
                    if name not in local_scores or db_score > local_scores[name]['score']:
                        local_scores[name] = {'score': db_score, 'mode': db_mode, 'status': db_status}
                        print(f"Synced DB {name} to local (score: {db_score})")
                
                # Write back merged local scores
                self._write_scores_local(local_scores)
                conn.commit()
                cursor.close()
            except mysql.connector.Error as err:
                print(f"Sync Error: {err}")

    def ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                pass  # Create empty file

    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def user_exists(self, nickname):
        conn = self._get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT 1 FROM {self.table_name} WHERE nickname = %s", (nickname,))
                result = cursor.fetchone()
                cursor.close()
                return bool(result)
            except mysql.connector.Error as err:
                print(f"User Exists Error: {err}")
        return False

    def get_score(self, nickname):
        """Returns the score for the nickname, or 0 if not found."""
        # Prefer online? Or just local? Let's check online first.
        conn = self._get_connection()
        if conn:
             try:
                 cursor = conn.cursor()
                 cursor.execute(f"SELECT score FROM {self.table_name} WHERE nickname = %s", (nickname,))
                 result = cursor.fetchone()
                 cursor.close()
                 if result:
                     return result[0]
             except:
                 pass
                 
        # Fallback
        scores = self._read_scores_local()
        data = scores.get(nickname)
        return data['score'] if data else 0

    def save_score(self, nickname, score, mode, status):
        """Saves score only if it is higher than existing."""
        # 1. Save Local
        scores = self._read_scores_local()
        current_data = scores.get(nickname)
        current_score_local = current_data['score'] if current_data else 0
        
        new_record_local = False
        if score > current_score_local or (score == current_score_local and current_score_local == 0):
             scores[nickname] = {'score': score, 'mode': mode, 'status': status}
             self._write_scores_local(scores)
             new_record_local = True

        # 2. Save Online
        conn = self._get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT score FROM {self.table_name} WHERE nickname = %s", (nickname,))
                result = cursor.fetchone()
                current_score_online = result[0] if result else -1
                
                if score > current_score_online:
                     cursor.execute(f"""
                        INSERT INTO {self.table_name} (nickname, score, gamemode, status) 
                        VALUES (%s, %s, %s, %s) 
                        ON DUPLICATE KEY UPDATE 
                        score = VALUES(score), gamemode = VALUES(gamemode), status = VALUES(status)
                    """, (nickname, score, mode, status))
                     conn.commit()
                     cursor.close()
                     print(f"Uploaded new high score for {nickname}")
                     return True
            except mysql.connector.Error as err:
                print(f"Save Online Error: {err}")
        
        return new_record_local

    def verify_user(self, nickname, password):
        conn = self._get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT password FROM {self.table_name} WHERE nickname = %s", (nickname,))
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    stored_password = result[0]
                    hashed = self.hash_password(password)
                    
                    # Compare hashes
                    if stored_password == hashed:
                        print(f"Login successful for {nickname}")
                        return True
                    else:
                        print(f"Password mismatch for {nickname}. Stored: {stored_password[:20]}..., Hashed input: {hashed[:20]}...")
                else:
                    print(f"User not found: {nickname}")
            except mysql.connector.Error as err:
                print(f"Verify Error: {err}")
        return False

    def register_user(self, nickname, password):
        conn = self._get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                hashed_pwd = self.hash_password(password)
                cursor.execute(f"INSERT INTO {self.table_name} (nickname, score, gamemode, status, password) VALUES (%s, %s, %s, %s, %s)", 
                               (nickname, 0, "Normal", "Registered", hashed_pwd))
                conn.commit()
                cursor.close()
                print(f"Registered user {nickname} with hashed password")
                return True
            except mysql.connector.Error as err:
                print(f"Register Error: {err}")
        return False

    def get_top_scores(self, limit):
        conn = self._get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT nickname, score, gamemode, status FROM {self.table_name} ORDER BY score DESC, status DESC LIMIT %s", (limit,))
                rows = cursor.fetchall()
                cursor.close()
                results = []
                for row in rows:
                    results.append((row[0], {'score': row[1], 'mode': row[2], 'status': row[3]}))
                return results
            except mysql.connector.Error as err:
                print(f"Get Top Scores Error: {err}")

        scores = self._read_scores_local()
        sorted_scores = sorted(scores.items(), key=lambda item: item[1]['score'], reverse=True)
        return sorted_scores[:limit]

    def _read_scores_local(self):
        scores = {}
        try:
            with open(self.filepath, "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) >= 2:
                        name = parts[0]
                        try:
                            s = int(parts[1])
                            mode = parts[2] if len(parts) > 2 else "Unknown"
                            status = parts[3] if len(parts) > 3 else "Unknown"
                            scores[name] = {'score': s, 'mode': mode, 'status': status}
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Error reading DB: {e}")
        return scores

    def _write_scores_local(self, scores):
        try:
            with open(self.filepath, "w") as f:
                for name, data in scores.items():
                    f.write(f"{name}:{data['score']}:{data['mode']}:{data['status']}\n")
        except Exception as e:
            print(f"Error writing DB: {e}")

# --- Camera ---
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def apply_pos(self, pos):
        return (pos[0] + self.camera.x, pos[1] + self.camera.y)

    def update(self, target):
        x = -target.rect.centerx + int(WINDOW_WIDTH / 2)
        y = -target.rect.centery + int(WINDOW_HEIGHT / 2)

        # Smooth camera
        current_x, current_y = self.camera.x, self.camera.y
        lerp_speed = 0.1
        
        new_x = current_x + (x - current_x) * lerp_speed
        new_y = current_y + (y - current_y) * lerp_speed

        self.camera = pygame.Rect(int(new_x), int(new_y), self.width, self.height)

# --- Entities ---
class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, size, color):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 0
        self.color = color

class Player(Entity):
    def __init__(self, x, y, gamemode):
        self.gamemode = gamemode
        
        # Gamemode Props
        hp = 4
        color = GREEN
        self.gun = None
        
        if gamemode == "Reflect":
            hp = 6
            color = CYAN
        elif gamemode == "Gunner":
            hp = 2
            color = YELLOW
            # Gunner gets a random gun type
            self.gun = random.choice(["fast", "dual", "shotgun"])

        super().__init__(x, y, 30, color)
        self.hp = hp
        self.speed = 5
        self.attack_cooldown = 0
        self.sword_active = False
        self.mask_off_timer = 0
        self.max_mask_off_time = 4.0
        
        self.shoot_cooldown = 0

    def update(self, keys):
        # Update Cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        if self.sword_active:
            # Sword active is an int frame counter
            if isinstance(self.sword_active, int):
                self.sword_active -= 1
                if self.sword_active <= 0:
                     self.sword_active = False

        # MOVEMENT
        self.vel = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w]: self.vel.y = -1
        if keys[pygame.K_s]: self.vel.y = 1
        if keys[pygame.K_a]: self.vel.x = -1
        if keys[pygame.K_d]: self.vel.x = 1

        if self.vel.length() > 0:
            self.vel = self.vel.normalize() * self.speed
        
        self.pos += self.vel
        self.rect.center = self.pos

    def slash(self):
        if self.attack_cooldown == 0:
            self.sword_active = 15 # Frames
            self.attack_cooldown = 20 # Fast slashes
            return True
        return False
    
    def shoot(self, target_pos_x, target_pos_y):
        if self.gamemode == "Gunner" and self.shoot_cooldown == 0:
            self.shoot_cooldown = 30 # Fire rate
            return True # Game loop handles creating projectile
        return False

    def get_sword_hitbox(self, camera):
        # Used for SWORD ATTACK (Slashing)
        if not self.sword_active:
            return None
        
        mouse_pos = pygame.mouse.get_pos()
        player_screen = camera.apply(self)
        angle = math.atan2(mouse_pos[1] - player_screen.centery, mouse_pos[0] - player_screen.centerx)
        
        reach = 40
        s_cx = self.pos.x + math.cos(angle) * reach
        s_cy = self.pos.y + math.sin(angle) * reach
        
        return pygame.Rect(s_cx - 25, s_cy - 25, 50, 50)

class Projectile(Entity):
    def __init__(self, x, y, angle, speed, owner_type="enemy"):
        super().__init__(x, y, 10, YELLOW) 
        self.vel = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.owner_type = owner_type 
        if self.owner_type == "player":
            self.color = WHITE
            self.image.fill(WHITE)
            self.speed = speed * 1.5 
        else:
            self.color = RED 
            self.image.fill(RED)

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

class Enemy(Entity):
    def __init__(self, x, y, type_name):
        color_map = {
            "fast": PURPLE,
            "dual": ORANGE,
            "shotgun": BLUE,
            "sword": GRAY
        }
        super().__init__(x, y, 30, color_map.get(type_name, WHITE))
        self.type_name = type_name
        self.fire_cooldown = 120 
        self.speed = 2 if type_name != "sword" else 3.5

    def update(self, player_pos):
        # Movement AI
        # Sword types chase directly
        # Others Kite (Stop at distance)
        
        dist_vec = player_pos - self.pos
        dist = dist_vec.length()
        
        if dist > 0:
            direction = dist_vec.normalize()
            
            if self.type_name == "sword":
                self.vel = direction * self.speed
            else:
                # Shooter AI
                preferred_dist = 250
                if dist > preferred_dist:
                    self.vel = direction * self.speed
                elif dist < preferred_dist - 50:
                    # Too close, back away
                    self.vel = -direction * (self.speed * 0.5)
                else:
                    # Maintain distance (stop)
                    self.vel = pygame.math.Vector2(0, 0)
        
            self.pos += self.vel
            self.rect.center = self.pos

        # Cooldown management for on-screen logic is in Game Loop

# --- Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Ubermosh Rebirth")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.large_font = pygame.font.SysFont("Arial", 48)

        self.db = DatabaseManager(DB_FILE)
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Test database connection
        test_conn = self.db._get_connection()
        if test_conn:
            try:
                cursor = test_conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {self.db.table_name}")
                count = cursor.fetchone()[0]
                cursor.close()
                print(f"✓ Database connection successful. Table has {count} records.")
            except Exception as e:
                print(f"✗ Database test failed: {e}")
            finally:
                test_conn.close()
        else:
            print("✗ Database connection failed!")
        
        self.state = "LOGIN_NAME"
        self.nickname = ""
        self.password = ""
        self.is_host = False
        self.login_error = ""
        self.load_settings()
        
        # Audio
        pygame.mixer.init()
        self.current_music = None
        self.play_music("Aces.mp3")
        pygame.mixer.music.set_volume(self.volume)
        
        # Game Options
        self.gamemode_options = ["Normal", "Reflect", "Gunner"]
        self.current_gamemode_idx = 0
        
        self.reset_game()

    def play_music(self, track_name):
        if self.current_music == track_name:
            return
            
        try:
            pygame.mixer.music.load(track_name)
            pygame.mixer.music.play(-1) # Loop indefinitely
            self.current_music = track_name
        except pygame.error as e:
            print(f"Error loading music {track_name}: {e}")

    def reset_game(self):
        mode = self.gamemode_options[self.current_gamemode_idx]
        self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, mode)
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.score = 0
        self.death_timer = 0
        self.game_over_reason = ""
        self.spawn_timer = 0
        self.damage_flash_timer = 0
        self.game_timer = 60.0

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.state == "LOGIN_NAME":
                self.handle_login_name(events)
            elif self.state == "LOGIN_PASS":
                self.handle_login_pass(events)
            elif self.state == "MENU":
                self.handle_menu(events)
            elif self.state == "LEADERBOARD":
                self.handle_leaderboard(events)
            elif self.state == "HELP":
                self.handle_help(events)
            elif self.state == "OPTIONS":
                self.handle_options(events)
            elif self.state == "PLAYING":
                self.handle_playing(events)
            elif self.state == "PAUSED":
                self.handle_paused(events)
            elif self.state == "GAMEOVER":
                self.handle_gameover(events)

            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_login_name(self, events):
        self.screen.fill(BLACK)
        prompt = self.large_font.render("Enter Nickname:", True, WHITE)
        name_text = self.large_font.render(self.nickname + "_", True, YELLOW)
        self.screen.blit(prompt, (WINDOW_WIDTH//2 - 150, 300))
        self.screen.blit(name_text, (WINDOW_WIDTH//2 - 150, 400))
        
        host_btn_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, 550, 200, 50)
        pygame.draw.rect(self.screen, DARK_GRAY, host_btn_rect)
        host_txt = self.font.render("Host (Guest)", True, WHITE)
        self.screen.blit(host_txt, (host_btn_rect.centerx - host_txt.get_width()//2, host_btn_rect.centery - host_txt.get_height()//2))

        if self.login_error:
            error_surf = self.font.render(self.login_error, True, RED)
            self.screen.blit(error_surf, (WINDOW_WIDTH//2 - error_surf.get_width()//2, 500))

        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if host_btn_rect.collidepoint(mouse_pos):
                    self.nickname = "Host"
                    self.is_host = True
                    self.state = "MENU"
                    self.play_music("Aces.mp3")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(self.nickname) > 0:
                    if self.db.user_exists(self.nickname):
                        self.state = "LOGIN_PASS"
                        self.password = ""
                        self.login_error = ""
                    else:
                        self.login_error = "Unknown username. Use Host or register online."
                elif event.key == pygame.K_BACKSPACE:
                    self.nickname = self.nickname[:-1]
                else:
                    if len(self.nickname) < 12 and event.unicode.isalnum():
                        self.nickname += event.unicode

    def handle_login_pass(self, events):
        self.screen.fill(BLACK)
        prompt = self.large_font.render("Enter Password:", True, WHITE)
        pass_display = "*" * len(self.password)
        pass_text = self.large_font.render(pass_display + "_", True, YELLOW)
        self.screen.blit(prompt, (WINDOW_WIDTH//2 - 150, 300))
        self.screen.blit(pass_text, (WINDOW_WIDTH//2 - 150, 400))
        
        back_txt = self.font.render("Back [ESC]", True, GRAY)
        self.screen.blit(back_txt, (WINDOW_WIDTH//2 - back_txt.get_width()//2, 550))

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.db.verify_user(self.nickname, self.password):
                        self.is_host = False
                        self.state = "MENU"
                        self.play_music("Aces.mp3")
                    else:
                        self.state = "LOGIN_NAME"
                        self.login_error = "Invalid Username or Password"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "LOGIN_NAME"
                elif event.key == pygame.K_BACKSPACE:
                    self.password = self.password[:-1]
                else:
                    if len(self.password) < 20:
                        self.password += event.unicode

    def handle_menu(self, events):
        self.screen.fill(DARK_GRAY)
        
        title = self.large_font.render("UBERMOSH REBIRTH", True, WHITE)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 80))
        
        sub = self.font.render(f"Playing as {self.nickname}", True, YELLOW)
        self.screen.blit(sub, (WINDOW_WIDTH//2 - sub.get_width()//2, 130))
        
        # Buttons
        options = ["Play", "Gamemode: " + self.gamemode_options[self.current_gamemode_idx], "Leaderboard", "Help", "Options", "Exit"]
        
        mouse_pos = pygame.mouse.get_pos()
        clicks = [e for e in events if e.type == pygame.MOUSEBUTTONDOWN]

        for i, opt in enumerate(options):
            txt = self.large_font.render(opt, True, WHITE)
            rect = txt.get_rect(center=(WINDOW_WIDTH//2, 250 + i * 80))
            
            color = WHITE
            if rect.collidepoint(mouse_pos):
                color = GREEN
                if clicks:
                    if "Play" in opt:
                        self.reset_game()
                        self.state = "PLAYING"
                        self.play_music("Blades.mp3")
                    elif "Gamemode" in opt:
                        self.current_gamemode_idx = (self.current_gamemode_idx + 1) % len(self.gamemode_options)
                    elif opt == "Leaderboard":
                         self.state = "LEADERBOARD"
                    elif opt == "Help":
                         self.state = "HELP"
                    elif opt == "Options":
                        self.state = "OPTIONS"
                    elif opt == "Exit":
                        pygame.quit()
                        sys.exit()
            
            txt_colored = self.large_font.render(opt, True, color)
            self.screen.blit(txt_colored, rect)

    def handle_leaderboard(self, events):
        self.screen.fill(BLACK)
        title = self.large_font.render("TOP 3 SCORES", True, YELLOW)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        
        scores = self.db.get_top_scores(3)
        if not scores:
             t = self.font.render("No scores yet.", True, GRAY)
             self.screen.blit(t, (WINDOW_WIDTH//2 - t.get_width()//2, 250))
             
        for i, (name, data) in enumerate(scores):
            # Format: 1. Name: 100 (Normal - Survived)
            # Use smaller font for mode/status if needed, or just append
            entry_str = f"{i+1}. {name}: {data['score']} ({data['mode']} - {data['status']})"
            entry = self.font.render(entry_str, True, WHITE) # Using smaller font to fit
            self.screen.blit(entry, (WINDOW_WIDTH//2 - entry.get_width()//2, 250 + i * 80))
            
        back = self.font.render("Back [ESC]", True, GRAY)
        self.screen.blit(back, (WINDOW_WIDTH//2 - back.get_width()//2, 600))
        
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "MENU"
                self.play_music("Aces.mp3")

    def handle_help(self, events):
        self.screen.fill(BLACK)
        
        # Title
        title = self.large_font.render("HELP & GUIDE", True, YELLOW)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
        
        # Controls
        c_title = self.font.render("CONTROLS", True, WHITE)
        self.screen.blit(c_title, (100, 150))
        
        controls = [
            "WASD : Move",
            "Left Click : Attack / Shoot",
            "Right Click : Attack / Slash",
            "ESC : Pause",
            "Mouse : Aim"
        ]
        
        for i, line in enumerate(controls):
            txt = self.font.render(line, True, GRAY)
            self.screen.blit(txt, (100, 190 + i * 30))
            
        # Enemies
        e_title = self.font.render("ENEMIES", True, WHITE)
        self.screen.blit(e_title, (100, 360))
        
        enemy_data = [
            (PURPLE, "Fast Shooter - Shoots 1 fast bullet"),
            (ORANGE, "Dual Shooter - Shoots 2 side-by-side bullets"),
            (BLUE,   "Shotgun Enemy - Shoots a spread of bullets"),
            (GRAY,   "Sword Enemy - Chases you directly (No gun)")
        ]
        
        y = 400
        for color, desc in enemy_data:
            # Draw sprite icon
            pygame.draw.rect(self.screen, color, (100, y, 30, 30))
            # Draw text
            txt = self.font.render(desc, True, WHITE)
            self.screen.blit(txt, (150, y))
            y += 50

        # Back
        back = self.font.render("Back [ESC]", True, GRAY)
        self.screen.blit(back, (WINDOW_WIDTH//2 - back.get_width()//2, 650))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "MENU"

    def handle_help(self, events):
        self.screen.fill(BLACK)
        
        # Title
        title = self.large_font.render("HELP & GUIDE", True, YELLOW)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
        
        # Controls
        c_title = self.font.render("CONTROLS", True, WHITE)
        self.screen.blit(c_title, (100, 150))
        
        controls = [
            "WASD : Move",
            "Left Click : Attack / Shoot",
            "Right Click : Attack / Slash",
            "ESC : Pause",
            "Mouse : Aim"
        ]
        
        for i, line in enumerate(controls):
            txt = self.font.render(line, True, GRAY)
            self.screen.blit(txt, (100, 190 + i * 30))
            
        # Enemies
        e_title = self.font.render("ENEMIES", True, WHITE)
        self.screen.blit(e_title, (100, 360))
        
        enemy_data = [
            (PURPLE, "Fast Shooter - Shoots 1 fast bullet"),
            (ORANGE, "Dual Shooter - Shoots 2 side-by-side bullets"),
            (BLUE,   "Shotgun Enemy - Shoots a spread of bullets"),
            (GRAY,   "Sword Enemy - Chases you directly (No gun)")
        ]
        
        y = 400
        for color, desc in enemy_data:
            # Draw sprite icon
            pygame.draw.rect(self.screen, color, (100, y, 30, 30))
            # Draw text
            txt = self.font.render(desc, True, WHITE)
            self.screen.blit(txt, (150, y))
            y += 50

        # Back
        back = self.font.render("Back [ESC]", True, GRAY)
        self.screen.blit(back, (WINDOW_WIDTH//2 - back.get_width()//2, 650))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "MENU"
                self.play_music("Aces.mp3")

    def handle_options(self, events):
        self.screen.fill(BLACK)
        title = self.large_font.render("Options - Volume", True, WHITE)
        self.screen.blit(title, (100, 100))

        vol_label = self.font.render(f"{int(self.volume*100)}%", True, WHITE)
        self.screen.blit(vol_label, (100, 200))
        
        slider = pygame.Rect(100, 250, 300, 20)
        knob = pygame.Rect(100 + int(self.volume * 300) - 10, 240, 20, 40)
        pygame.draw.rect(self.screen, GRAY, slider)
        pygame.draw.rect(self.screen, YELLOW, knob)
        
        if pygame.mouse.get_pressed()[0]:
             m_pos = pygame.mouse.get_pos()
             if slider.collidepoint(m_pos) or knob.collidepoint(m_pos):
                 self.volume = max(0.0, min(1.0, (m_pos[0] - 100) / 300))
                 pygame.mixer.music.set_volume(self.volume)
        
        if any(e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE for e in events):
            self.state = "MENU"
            self.save_settings()

    def handle_paused(self, events):
        # Draw game world behind (it's already on screen from last frame? No, we need to redraw it frozen)
        # Actually in Pygame we must redraw everything every frame.
        # So we call a render_world method? Or just copy handle_playing draw logic?
        # A simple hack: Do not fill screen. Just draw overlay.
        # But we need to keep drawing the loop? 
        # Correct way: Separate Draw and Update.
        # For this single file scope, I'll just redraw the game entities without updating them.
        self.draw_game_world()
        
        # Darken Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Paused Text
        txt = self.large_font.render("PAUSED", True, WHITE)
        self.screen.blit(txt, (WINDOW_WIDTH//2 - txt.get_width()//2, WINDOW_HEIGHT//2 - 50))
        
        sub = self.font.render("Press SPACE to Give Up, ESC to Resume", True, YELLOW)
        self.screen.blit(sub, (WINDOW_WIDTH//2 - sub.get_width()//2, WINDOW_HEIGHT//2 + 20))
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "PLAYING"
                elif event.key == pygame.K_SPACE:
                    self.do_game_over("Given Up")

    def draw_game_world(self):
        # Helper to draw world (reused for pause)
        self.screen.fill(BLACK)
        border_rect = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
        pygame.draw.rect(self.screen, RED, self.camera.apply_rect(border_rect), 2)
        
        for s in self.enemies: self.screen.blit(s.image, self.camera.apply(s))
        for s in self.projectiles: self.screen.blit(s.image, self.camera.apply(s))
        self.screen.blit(self.player.image, self.camera.apply(self.player))
        
        if self.player.sword_active:
             hb = self.player.get_sword_hitbox(self.camera)
             if hb: pygame.draw.rect(self.screen, WHITE, self.camera.apply_rect(hb))

        # UI
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        mode_surf = self.font.render(f"Mode: {self.player.gamemode}", True, YELLOW)
        hp_surf = self.font.render(f"HP: {self.player.hp}", True, GREEN)
        
        self.screen.blit(score_surf, (20, 20))
        self.screen.blit(hp_surf, (20, 50))
        self.screen.blit(mode_surf, (20, 80))
        
        # Timer
        timer_color = WHITE
        if self.game_timer < 10: timer_color = RED
        timer_surf = self.large_font.render(f"{int(self.game_timer)}", True, timer_color)
        self.screen.blit(timer_surf, (WINDOW_WIDTH // 2 - timer_surf.get_width() // 2, 20))
        
        if self.player.mask_off_timer > 0:
             warn = self.large_font.render("RETURN TO AREA!", True, RED)
             self.screen.blit(warn, (WINDOW_WIDTH//2 - warn.get_width()//2, 120))

    def handle_playing(self, events):
        # Pause Check
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "PAUSED"
                return

        # Input
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # MOUSE CLICKS
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.player.gamemode == "Gunner":
                    # Left Click Shoot, Right Click Sword
                    if event.button == 1:
                        # Shoot logic
                        mx, my = pygame.mouse.get_pos()
                        player_screen = self.camera.apply(self.player)
                        angle = math.atan2(my - player_screen.centery, mx - player_screen.centerx)
                        
                        if self.player.shoot(mx, my):
                            # Determine gun type spread
                            if self.player.gun == "fast":
                                self.projectiles.add(Projectile(self.player.pos.x, self.player.pos.y, angle, 12, "player"))
                            elif self.player.gun == "dual":
                                self.projectiles.add(Projectile(self.player.pos.x, self.player.pos.y, angle - 0.1, 10, "player"))
                                self.projectiles.add(Projectile(self.player.pos.x, self.player.pos.y, angle + 0.1, 10, "player"))
                            elif self.player.gun == "shotgun":
                                for _ in range(5):
                                    spread = random.uniform(-0.2, 0.2)
                                    self.projectiles.add(Projectile(self.player.pos.x, self.player.pos.y, angle + spread, random.uniform(8, 12), "player"))
                    
                    elif event.button == 3: # RMB
                        self.player.slash()
                        
                else:
                    # Normal / Reflect: Both clicks Slash
                     if event.button == 1 or event.button == 3:
                         self.player.slash()

        # Camera Update
        self.camera.update(self.player)

        # Spawning
        if len(self.enemies) < 15:
            self.spawn_timer += 1
            if self.spawn_timer >= 60 // random.randint(1, 3): 
                self.spawn_timer = 0
                self.spawn_enemy()

        # Update Lists
        self.enemies.update(self.player.pos)
        self.projectiles.update()

        # Enemy Shooting Check
        for enemy in self.enemies:
            enemy_screen_rect = self.camera.apply(enemy)
            on_screen = self.screen.get_rect().colliderect(enemy_screen_rect)
            
            if on_screen:
                if enemy.fire_cooldown > 0:
                    enemy.fire_cooldown -= 1
                else:
                    self.enemy_shoot(enemy)
            else:
                 if enemy.fire_cooldown < 60:
                     enemy.fire_cooldown = 60

        # --- Collisions & Logic ---
        
        # 1. Sword Hitbox (Killing)
        sword_hitbox = self.player.get_sword_hitbox(self.camera)
        if sword_hitbox:
            # In REFLECT mode, sword cannot kill enemies
            can_kill = self.player.gamemode != "Reflect"
            
            # Check Reflecting Bullets (Works in all modes)
            for p in self.projectiles:
                if p.rect.colliderect(sword_hitbox) and p.owner_type == "enemy":
                    p.owner_type = "player"
                    p.color = WHITE
                    p.image.fill(WHITE)
                    p.vel *= -1.5
                    p.speed *= 1.5

            if can_kill:
                 hits = [e for e in self.enemies if e.rect.colliderect(sword_hitbox)]
                 for e in hits:
                     e.kill()
                     self.score += 1
        
        # 3. Projectiles
        for p in list(self.projectiles):
            rect = p.rect
            if rect.left < -500 or rect.right > WORLD_WIDTH+500 or rect.top < -500 or rect.bottom > WORLD_HEIGHT+500:
                p.kill()
                continue
            
            if p.owner_type == "player":
                hits = pygame.sprite.spritecollide(p, self.enemies, True)
                for _ in hits:
                    self.score += 1
                    p.kill()
            elif p.owner_type == "enemy":
                if p.rect.colliderect(self.player.rect):
                    self.player.hp -= 1
                    self.damage_flash_timer = 5
                    p.kill()
                    if self.player.hp <= 0:
                        self.do_game_over("Killed")

        # 4. Collision Damage
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        # Add simple invuln frame or pushback? Or just die fast. 
        # User accepted simple collision damage before.
        if hits:
             # Very punishing without invuln, but requested "Ubermosh" style (fast death)
             # Let's add a small mercy timer? No, stick to raw.
             self.damage_flash_timer = 5
             pass

        # 5. World Border
        in_bounds = (0 <= self.player.pos.x <= WORLD_WIDTH and 0 <= self.player.pos.y <= WORLD_HEIGHT)
        if not in_bounds:
            self.player.mask_off_timer += 1/FPS
            if self.player.mask_off_timer >= self.player.max_mask_off_time:
                self.do_game_over("Left Mission Area")
        else:
            self.player.mask_off_timer = max(0, self.player.mask_off_timer - 2/FPS)

        # 6. Game Timer
        self.game_timer -= 1/FPS
        if self.game_timer <= 0:
            self.do_game_over("Extraction Complete")


        # Draw
        self.draw_game_world()
        
        # Damage Flash
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
            flash = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            flash.set_alpha(100)
            flash.fill(RED)
            self.screen.blit(flash, (0,0))

    def enemy_shoot(self, enemy):
        dx = self.player.pos.x - enemy.pos.x
        dy = self.player.pos.y - enemy.pos.y
        angle = math.atan2(dy, dx)
        
        if enemy.type_name == "fast":
            self.projectiles.add(Projectile(enemy.pos.x, enemy.pos.y, angle, 8))
            enemy.fire_cooldown = 360
        elif enemy.type_name == "dual":
            self.projectiles.add(Projectile(enemy.pos.x, enemy.pos.y, angle - 0.05, 5))
            self.projectiles.add(Projectile(enemy.pos.x, enemy.pos.y, angle + 0.05, 5))
            enemy.fire_cooldown = 360
        elif enemy.type_name == "shotgun":
            for _ in range(5):
                spread = random.uniform(-0.3, 0.3)
                self.projectiles.add(Projectile(enemy.pos.x, enemy.pos.y, angle + spread, random.uniform(3, 5)))
            enemy.fire_cooldown = 360

    def spawn_enemy(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        dist = 100
        if side == 'top': x, y = random.randint(0, WORLD_WIDTH), -dist
        elif side == 'bottom': x, y = random.randint(0, WORLD_WIDTH), WORLD_HEIGHT + dist
        elif side == 'left': x, y = -dist, random.randint(0, WORLD_HEIGHT)
        else: x, y = WORLD_WIDTH + dist, random.randint(0, WORLD_HEIGHT)
            
        choices = ['fast', 'fast', 'dual', 'shotgun', 'sword']
        if self.player.gamemode == "Reflect":
            choices = ['fast', 'fast', 'dual', 'shotgun'] # No swords allowed in Reflect mode
            
        e_type = random.choice(choices)
        self.enemies.add(Enemy(x, y, e_type))

    def do_game_over(self, reason):
        self.game_over_reason = reason
        self.state = "GAMEOVER"
        self.play_music("Aces.mp3")
        
        status = "Survived" if reason == "Extraction Complete" else "Died"
        if not self.is_host:
            self.db.save_score(self.nickname, self.score, self.player.gamemode, status)

    def handle_gameover(self, events):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(10)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0,0))
        
        title_text = "GAME OVER"
        title_color = RED
        if self.game_over_reason == "Extraction Complete":
            title_text = "EXTRACTION COMPLETE"
            title_color = GREEN
            
        txt1 = self.large_font.render(title_text, True, title_color)
        txt2 = self.font.render(f"Reason: {self.game_over_reason}", True, WHITE)
        txt3 = self.large_font.render(f"Final Score: {self.score}", True, YELLOW)
        
        cx = WINDOW_WIDTH // 2
        self.screen.blit(txt1, (cx - txt1.get_width()//2, 300))
        self.screen.blit(txt2, (cx - txt2.get_width()//2, 380))
        self.screen.blit(txt3, (cx - txt3.get_width()//2, 450))
        
        btn_txt = self.font.render("Return to Menu (Click)", True, WHITE)
        btn_rect = btn_txt.get_rect(center=(cx, 600))
        
        mouse_pos = pygame.mouse.get_pos()
        if btn_rect.collidepoint(mouse_pos):
            btn_txt = self.font.render("Return to Menu (Click)", True, GREEN)
            if pygame.mouse.get_pressed()[0]:
                self.state = "MENU"
        
        self.screen.blit(btn_txt, btn_rect)

        self.screen.blit(btn_txt, btn_rect)

    def load_settings(self):
        self.volume = 0.5
        try:
            with open("settings.txt", "r") as f:
                data = f.read().strip()
                self.volume = float(data)
                self.volume = max(0.0, min(1.0, self.volume))
        except FileNotFoundError:
            pass
        except ValueError:
            pass

    def save_settings(self):
        try:
            with open("settings.txt", "w") as f:
                f.write(str(self.volume))
        except Exception as e:
            print(f"Error saving settings: {e}")

if __name__ == "__main__":
    game = Game()
    game.run()
