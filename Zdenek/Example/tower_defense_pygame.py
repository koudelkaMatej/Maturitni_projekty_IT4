"""
Desktop Tower Defense version with login and database integration.
The gameplay mirrors the current web version from static/js/game.js.
"""

import math
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import pygame
from mysql.connector import Error

try:
    from Example.db import get_db
except ModuleNotFoundError:
    from db import get_db

SCREEN_WIDTH = 1180
SCREEN_HEIGHT = 760
MIN_SCREEN_WIDTH = 980
MIN_SCREEN_HEIGHT = 680
FPS = 60

GRID = 10
TOTAL_WAVES = 10
MAX_TOWER_LEVEL = 3

PATH = [(x, 5) for x in range(10)]

TOWER_CATALOG: Dict[str, dict] = {
    "basic": {
        "name": "Basic",
        "description": "Balanced defense for any lane.",
        "cost": 0,
        "unlock_cost": 0,
        "range": 120,
        "damage": 10,
        "cooldown": 34,
        "color": (14, 143, 136),
    },
    "sniper": {
        "name": "Sniper",
        "description": "Huge range, slower fire rate.",
        "cost": 90,
        "unlock_cost": 120,
        "range": 210,
        "damage": 26,
        "cooldown": 78,
        "color": (61, 107, 145),
    },
    "splash": {
        "name": "Splash",
        "description": "Damages groups around the target.",
        "cost": 110,
        "unlock_cost": 160,
        "range": 132,
        "damage": 14,
        "cooldown": 48,
        "splash_radius": 58,
        "color": (232, 111, 81),
    },
    "frost": {
        "name": "Frost",
        "description": "Slows enemies and stabilizes the lane.",
        "cost": 100,
        "unlock_cost": 150,
        "range": 145,
        "damage": 8,
        "cooldown": 42,
        "slow_factor": 0.55,
        "slow_duration": 105,
        "color": (105, 205, 187),
    },
}

DIFFICULTIES = {
    "easy": {
        "name": "Easy",
        "enemy_speed": 0.9,
        "enemy_hp": 0.85,
        "enemies_per_wave": 0,
        "starting_lives": 6,
        "starting_gold": 260,
        "reward_bonus": 0.9,
    },
    "normal": {
        "name": "Normal",
        "enemy_speed": 1.0,
        "enemy_hp": 1.0,
        "enemies_per_wave": 1,
        "starting_lives": 5,
        "starting_gold": 220,
        "reward_bonus": 1.0,
    },
    "hard": {
        "name": "Hard",
        "enemy_speed": 1.18,
        "enemy_hp": 1.3,
        "enemies_per_wave": 2,
        "starting_lives": 4,
        "starting_gold": 180,
        "reward_bonus": 1.2,
    },
}

GAME_LENGTHS = {
    "short": {"name": "Short", "waves": 5},
    "normal": {"name": "Normal", "waves": 10},
    "long": {"name": "Long", "waves": 15},
}

ENEMY_TYPES = {
    "grunt": {"name": "Grunt", "hp": 34, "speed": 0.62, "reward": 14, "color": (209, 72, 95), "radius": 10},
    "fast": {"name": "Fast", "hp": 20, "speed": 1.05, "reward": 12, "color": (246, 186, 74), "radius": 8},
    "tank": {"name": "Tank", "hp": 72, "speed": 0.42, "reward": 20, "color": (94, 123, 173), "radius": 12},
    "boss": {"name": "Boss", "hp": 260, "speed": 0.36, "reward": 90, "color": (14, 31, 40), "radius": 16},
}

COLOR_BG = (237, 247, 245)
COLOR_PANEL = (251, 255, 254)
COLOR_PANEL_ALT = (228, 242, 239)
COLOR_LINE = (180, 203, 208)
COLOR_TEXT = (23, 49, 58)
COLOR_MUTED = (93, 119, 128)
COLOR_ACCENT = (14, 143, 136)
COLOR_GREEN = (232, 111, 81)
COLOR_RED = (209, 72, 95)
COLOR_PATH = (225, 170, 131)
COLOR_GRID = (193, 212, 216)
COLOR_HP = (84, 195, 136)
COLOR_HP_BOSS = (232, 111, 81)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (14, 31, 40)


class GameState(Enum):
    MENU = 1
    LOGIN = 2
    STATS = 3
    PLAYING = 4


@dataclass
class Enemy:
    enemy_type: str
    hp: int
    max_hp: int
    base_speed: float
    reward: int
    color: Tuple[int, int, int]
    radius: int
    path_index: int
    progress: float
    x: float
    y: float
    slow_ticks: int = 0
    slow_factor: float = 1.0
    hit_flash_ticks: int = 0
    animation_phase: float = 0.0


@dataclass
class Tower:
    gx: int
    gy: int
    tower_type: str
    level: int = 1
    cooldown: int = 0


@dataclass
class Particle:
    x: float
    y: float
    dx: float
    dy: float
    radius: float
    color: Tuple[int, int, int]
    life: int


def get_db_connection():
    try:
        return get_db()
    except Error as exc:
        print(f"Database connection error: {exc}")
        return None


def authenticate_user(username: str, password: str) -> Optional[int]:
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        user_id, stored_password = row
        return user_id if stored_password == password else None
    except Error as exc:
        print(f"Authentication error: {exc}")
        return None
    finally:
        conn.close()


def get_user_stats(user_id: int) -> dict:
    conn = get_db_connection()
    if not conn:
        return {"wins": 0, "losses": 0, "total_kills": 0, "best_wave": 0, "total_games": 0, "coins": 0}
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*),
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END),
                SUM(CASE WHEN result = 'LOSE' THEN 1 ELSE 0 END),
                SUM(kills),
                MAX(waves_reached)
            FROM matches
            WHERE user_id = %s
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        cursor.execute("SELECT coins FROM users WHERE id = %s", (user_id,))
        coin_row = cursor.fetchone()
        cursor.close()
        return {
            "total_games": row[0] or 0,
            "wins": row[1] or 0,
            "losses": row[2] or 0,
            "total_kills": row[3] or 0,
            "best_wave": row[4] or 0,
            "coins": coin_row[0] if coin_row else 0,
        }
    except Error as exc:
        print(f"Stats error: {exc}")
        return {"wins": 0, "losses": 0, "total_kills": 0, "best_wave": 0, "total_games": 0, "coins": 0}
    finally:
        conn.close()


def ensure_default_tower_unlock(cursor, user_id: int):
    cursor.execute(
        """
        INSERT INTO towers_unlocked (user_id, tower_name)
        SELECT %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM towers_unlocked WHERE user_id = %s AND tower_name = %s
        )
        """,
        (user_id, "basic", user_id, "basic"),
    )


def get_user_profile_state(user_id: int) -> Tuple[int, List[str]]:
    conn = get_db_connection()
    if not conn:
        return 0, ["basic"]
    try:
        cursor = conn.cursor()
        ensure_default_tower_unlock(cursor, user_id)
        cursor.execute("SELECT coins FROM users WHERE id = %s", (user_id,))
        coin_row = cursor.fetchone()
        cursor.execute(
            """
            SELECT tower_name
            FROM towers_unlocked
            WHERE user_id = %s
            ORDER BY unlocked_at ASC, id ASC
            """,
            (user_id,),
        )
        unlocked = [row[0] for row in cursor.fetchall()]
        conn.commit()
        cursor.close()
        return (coin_row[0] if coin_row else 0, unlocked or ["basic"])
    except Error as exc:
        print(f"Profile load error: {exc}")
        return 0, ["basic"]
    finally:
        conn.close()


def unlock_tower_for_user(user_id: int, tower_id: str) -> Tuple[bool, str, int, List[str]]:
    if tower_id not in TOWER_CATALOG:
        return False, "Unknown tower.", 0, ["basic"]
    if tower_id == "basic":
        coins, unlocked = get_user_profile_state(user_id)
        return False, "Basic tower is already available.", coins, unlocked

    conn = get_db_connection()
    if not conn:
        return False, "Database is unavailable.", 0, ["basic"]
    try:
        cursor = conn.cursor()
        ensure_default_tower_unlock(cursor, user_id)
        cursor.execute("SELECT coins FROM users WHERE id = %s", (user_id,))
        coins = cursor.fetchone()[0]
        cursor.execute(
            "SELECT 1 FROM towers_unlocked WHERE user_id = %s AND tower_name = %s",
            (user_id, tower_id),
        )
        if cursor.fetchone():
            cursor.close()
            updated_coins, unlocked = get_user_profile_state(user_id)
            return False, "Tower is already unlocked.", updated_coins, unlocked

        cost = TOWER_CATALOG[tower_id]["unlock_cost"]
        if coins < cost:
            cursor.close()
            updated_coins, unlocked = get_user_profile_state(user_id)
            return False, "Not enough profile coins.", updated_coins, unlocked

        cursor.execute("UPDATE users SET coins = coins - %s WHERE id = %s", (cost, user_id))
        cursor.execute(
            "INSERT INTO towers_unlocked (user_id, tower_name) VALUES (%s, %s)",
            (user_id, tower_id),
        )
        cursor.execute(
            "INSERT INTO purchases (user_id, item_name, price) VALUES (%s, %s, %s)",
            (user_id, TOWER_CATALOG[tower_id]["name"], cost),
        )
        conn.commit()
        cursor.close()
        updated_coins, unlocked = get_user_profile_state(user_id)
        return True, f"{TOWER_CATALOG[tower_id]['name']} unlocked.", updated_coins, unlocked
    except Error as exc:
        print(f"Unlock error: {exc}")
        conn.rollback()
        return False, "Unlock failed.", 0, ["basic"]
    finally:
        conn.close()


def grant_profile_coins_for_user(user_id: int, amount: int = 500) -> Tuple[bool, str, int, List[str]]:
    conn = get_db_connection()
    if not conn:
        return False, "Database is unavailable.", 0, ["basic"]
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET coins = coins + %s WHERE id = %s", (amount, user_id))
        conn.commit()
        cursor.close()
        updated_coins, unlocked = get_user_profile_state(user_id)
        return True, f"Cheat applied: +{amount} profile coins.", updated_coins, unlocked
    except Error as exc:
        print(f"Cheat coins error: {exc}")
        conn.rollback()
        return False, "Cheat failed.", 0, ["basic"]
    finally:
        conn.close()


def unlock_all_towers_for_user(user_id: int) -> Tuple[bool, str, int, List[str]]:
    conn = get_db_connection()
    if not conn:
        return False, "Database is unavailable.", 0, ["basic"]
    try:
        cursor = conn.cursor()
        ensure_default_tower_unlock(cursor, user_id)
        cursor.execute("SELECT tower_name FROM towers_unlocked WHERE user_id = %s", (user_id,))
        unlocked_names = {row[0] for row in cursor.fetchall()}
        new_unlocks = 0
        for tower_id, tower in TOWER_CATALOG.items():
            if tower_id in unlocked_names:
                continue
            cursor.execute(
                "INSERT INTO towers_unlocked (user_id, tower_name) VALUES (%s, %s)",
                (user_id, tower_id),
            )
            cursor.execute(
                "INSERT INTO purchases (user_id, item_name, price) VALUES (%s, %s, %s)",
                (user_id, f"{tower['name']} [CHEAT]", 0),
            )
            new_unlocks += 1
        conn.commit()
        cursor.close()
        updated_coins, unlocked = get_user_profile_state(user_id)
        if new_unlocks == 0:
            return True, "All towers were already unlocked.", updated_coins, unlocked
        return True, "Cheat applied: all towers unlocked.", updated_coins, unlocked
    except Error as exc:
        print(f"Cheat unlock error: {exc}")
        conn.rollback()
        return False, "Cheat failed.", 0, ["basic"]
    finally:
        conn.close()


def calculate_match_reward(result: str, kills: int, waves: int, difficulty_id: str) -> int:
    reward = 20 + (kills * 2) + (waves * 10)
    if result == "WIN":
        reward += 100
    return int(round(reward * DIFFICULTIES[difficulty_id]["reward_bonus"]))


def save_match_result(user_id: int, result: str, waves: int, kills: int, difficulty_id: str) -> bool:
    conn = get_db_connection()
    if not conn:
        print("Database unavailable while saving match.")
        return False
    try:
        reward = calculate_match_reward(result, kills, waves, difficulty_id)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO matches (user_id, result, waves_reached, kills, reward_coins, difficulty)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, result, waves, kills, reward, difficulty_id),
        )
        cursor.execute("UPDATE users SET coins = coins + %s WHERE id = %s", (reward, user_id))
        conn.commit()
        cursor.close()
        return True
    except Error as exc:
        print(f"Match save error: {exc}")
        conn.rollback()
        return False
    finally:
        conn.close()


class TowerDefenseGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Tower Defense Lite - Desktop")
        self.clock = pygame.time.Clock()

        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 20)

        self.state = GameState.MENU
        self.current_user_id: Optional[int] = None
        self.current_username = ""

        self.username_input = ""
        self.password_input = ""
        self.selected_input = "username"
        self.login_error = False

        self.selected_difficulty_id = "normal"
        self.selected_game_length_id = "normal"
        self.selected_tower_id = "basic"
        self.unlocked_towers = {"basic"}
        self.profile_coins = 0
        self.cheat_menu_open = False

        self.status_message = "Place towers and press Start."
        self.game_started = False
        self.paused = False
        self.game_over = False
        self.game_result: Optional[str] = None
        self.selected_tower_coords: Optional[Tuple[int, int]] = None

        self.base_lives = 0
        self.kills = 0
        self.gold = 0
        self.waves_reached = 0
        self.wave_spawn_timer = 0
        self.wave_enemies_to_spawn = 0
        self.current_wave_plan: List[str] = []

        self.enemies: List[Enemy] = []
        self.towers: List[Tower] = []
        self.particles: List[Particle] = []

    def get_window_size(self) -> Tuple[int, int]:
        return self.screen.get_size()

    def get_layout_metrics(self) -> dict:
        window_width, window_height = self.get_window_size()
        outer_margin = max(18, min(30, window_width // 48))
        panel_gap = max(18, min(28, window_width // 42))
        title_height = max(72, min(104, window_height // 8))
        bottom_hud_height = max(108, min(150, window_height // 5))
        sidebar_width = max(390, min(520, int(window_width * 0.42)))
        sidebar_height = window_height - (outer_margin * 2)
        sidebar_x = window_width - outer_margin - sidebar_width
        board_area_width = sidebar_x - outer_margin - panel_gap
        board_area_height = window_height - title_height - bottom_hud_height - (outer_margin * 2)
        board_size = max(320, min(board_area_width, board_area_height))
        board_size = max(GRID * 24, (board_size // GRID) * GRID)
        board_x = outer_margin + max(0, (board_area_width - board_size) // 2)
        board_y = title_height + outer_margin
        board_rect = pygame.Rect(board_x, board_y, board_size, board_size)
        hud_rect = pygame.Rect(board_rect.x, board_rect.bottom + 12, board_rect.width, max(88, window_height - board_rect.bottom - outer_margin - 6))
        sidebar_rect = pygame.Rect(sidebar_x, outer_margin, sidebar_width, sidebar_height)
        return {
            "window_width": window_width,
            "window_height": window_height,
            "outer_margin": outer_margin,
            "panel_gap": panel_gap,
            "title_height": title_height,
            "bottom_hud_height": bottom_hud_height,
            "board_rect": board_rect,
            "hud_rect": hud_rect,
            "sidebar_rect": sidebar_rect,
            "cell_size": board_rect.width // GRID,
        }

    def load_user_profile(self):
        if not self.current_user_id:
            self.profile_coins = 0
            self.unlocked_towers = {"basic"}
            self.cheat_menu_open = False
            return
        coins, unlocked = get_user_profile_state(self.current_user_id)
        self.profile_coins = coins
        self.unlocked_towers = set(unlocked)
        if self.selected_tower_id not in self.unlocked_towers:
            self.selected_tower_id = "basic"
        if not self.is_cheat_user():
            self.cheat_menu_open = False

    def get_difficulty(self) -> dict:
        return DIFFICULTIES[self.selected_difficulty_id]

    def get_game_length(self) -> dict:
        return GAME_LENGTHS[self.selected_game_length_id]

    def get_total_waves(self) -> int:
        return self.get_game_length()["waves"]

    def is_cheat_user(self) -> bool:
        return self.current_username == "sa"

    def get_tower_stats(self, tower: Tower) -> dict:
        base = TOWER_CATALOG[tower.tower_type]
        level_factor = 1 + ((tower.level - 1) * 0.32)
        return {
            "range": round(base["range"] * (1 + ((tower.level - 1) * 0.12))),
            "damage": round(base["damage"] * level_factor),
            "cooldown": max(12, round(base["cooldown"] * (1 - ((tower.level - 1) * 0.08)))),
            "splash_radius": round(base.get("splash_radius", 0) * (1 + ((tower.level - 1) * 0.08))),
            "slow_factor": base.get("slow_factor", 1.0),
            "slow_duration": base.get("slow_duration", 0) + ((tower.level - 1) * 20 if base.get("slow_duration") else 0),
        }

    def get_upgrade_cost(self, level: int) -> int:
        return 45 + ((level - 1) * 35)

    def set_status(self, message: str):
        self.status_message = message

    def reset_game(self):
        difficulty = self.get_difficulty()
        self.base_lives = difficulty["starting_lives"]
        self.kills = 0
        self.gold = difficulty["starting_gold"]
        self.waves_reached = 0
        self.wave_spawn_timer = 0
        self.wave_enemies_to_spawn = 0
        self.current_wave_plan = []
        self.enemies = []
        self.towers = []
        self.particles = []
        self.game_started = False
        self.paused = False
        self.game_over = False
        self.game_result = None
        self.selected_tower_coords = None
        self.set_status("Place towers and press Start.")

    def grid_to_pixel(self, gx: int, gy: int) -> Tuple[float, float]:
        board_rect = self.get_board_rect()
        cell = self.get_cell_size()
        return (board_rect.x + gx * cell + (cell / 2), board_rect.y + gy * cell + (cell / 2))

    def build_wave_plan(self, wave_number: int) -> List[str]:
        difficulty = self.get_difficulty()
        base_count = 5 + wave_number + difficulty["enemies_per_wave"]
        plan: List[str] = []
        boss_interval = 5
        if wave_number % boss_interval == 0 or wave_number == self.get_total_waves():
            plan.append("boss")
        for index in range(base_count):
            if wave_number >= 3 and index % 4 == 0:
                plan.append("fast")
            elif wave_number >= 6 and index % 3 == 0:
                plan.append("tank")
            else:
                plan.append("grunt")
        return plan

    def spawn_enemy(self, enemy_type: str):
        template = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["grunt"])
        difficulty = self.get_difficulty()
        start_x, start_y = self.grid_to_pixel(PATH[0][0], PATH[0][1])
        hp = round((template["hp"] + (self.waves_reached * 4)) * difficulty["enemy_hp"])
        speed = template["speed"] * difficulty["enemy_speed"]
        self.enemies.append(
            Enemy(
                enemy_type=enemy_type,
                hp=hp,
                max_hp=hp,
                base_speed=speed,
                reward=template["reward"],
                color=template["color"],
                radius=template["radius"],
                path_index=0,
                progress=0.0,
                x=start_x,
                y=start_y,
            )
        )

    def update_enemies(self):
        for index in range(len(self.enemies) - 1, -1, -1):
            enemy = self.enemies[index]
            current = PATH[enemy.path_index]
            next_pos = PATH[enemy.path_index + 1] if enemy.path_index + 1 < len(PATH) else None
            if next_pos is None:
                self.enemies.pop(index)
                self.base_lives -= 2 if enemy.enemy_type == "boss" else 1
                continue

            if enemy.slow_ticks > 0:
                enemy.slow_ticks -= 1
            else:
                enemy.slow_factor = 1.0
            if enemy.hit_flash_ticks > 0:
                enemy.hit_flash_ticks -= 1

            enemy.progress += enemy.base_speed * enemy.slow_factor * 0.02
            enemy.animation_phase += 0.14
            if enemy.progress >= 1:
                enemy.path_index += 1
                enemy.progress = 0
                current = PATH[enemy.path_index]
                next_pos = PATH[enemy.path_index + 1] if enemy.path_index + 1 < len(PATH) else None
                if next_pos is None:
                    continue

            ax, ay = self.grid_to_pixel(current[0], current[1])
            bx, by = self.grid_to_pixel(next_pos[0], next_pos[1])
            enemy.x = ax + ((bx - ax) * enemy.progress)
            bob = math.sin(enemy.animation_phase) * 2.5
            enemy.y = ay + ((by - ay) * enemy.progress) + bob

    def enemy_distance_to_goal(self, enemy: Enemy) -> float:
        return enemy.path_index + enemy.progress

    def update_towers(self):
        for tower in self.towers:
            stats = self.get_tower_stats(tower)
            if tower.cooldown > 0:
                tower.cooldown -= 1
                continue

            tx, ty = self.grid_to_pixel(tower.gx, tower.gy)
            candidates = []
            for enemy in self.enemies:
                if math.hypot(enemy.x - tx, enemy.y - ty) <= stats["range"]:
                    candidates.append(enemy)
            candidates.sort(key=self.enemy_distance_to_goal, reverse=True)
            if not candidates:
                continue

            target = candidates[0]
            if tower.tower_type == "splash":
                for enemy in self.enemies:
                    if math.hypot(enemy.x - target.x, enemy.y - target.y) <= stats["splash_radius"]:
                        enemy.hp -= stats["damage"]
                        enemy.hit_flash_ticks = 5
            else:
                target.hp -= stats["damage"]
                target.hit_flash_ticks = 5
                if tower.tower_type == "frost":
                    target.slow_factor = stats["slow_factor"]
                    target.slow_ticks = stats["slow_duration"]

            tower.cooldown = stats["cooldown"]

        for index in range(len(self.enemies) - 1, -1, -1):
            enemy = self.enemies[index]
            if enemy.hp <= 0:
                self.gold += enemy.reward
                self.kills += 1
                self.spawn_particles(enemy.x, enemy.y, enemy.color)
                self.enemies.pop(index)

    def spawn_particles(self, x: float, y: float, color: Tuple[int, int, int]):
        for particle_index in range(6):
            angle = (math.pi * 2 * particle_index) / 6
            speed = 1.2 + (particle_index * 0.18)
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    dx=math.cos(angle) * speed,
                    dy=math.sin(angle) * speed,
                    radius=4 + (particle_index % 2),
                    color=color,
                    life=18,
                )
            )

    def update_particles(self):
        for index in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[index]
            particle.x += particle.dx
            particle.y += particle.dy
            particle.life -= 1
            particle.radius = max(0, particle.radius - 0.08)
            if particle.life <= 0:
                self.particles.pop(index)

    def start_next_wave(self):
        self.waves_reached += 1
        self.current_wave_plan = self.build_wave_plan(self.waves_reached)
        self.wave_enemies_to_spawn = len(self.current_wave_plan)
        self.wave_spawn_timer = 0
        self.set_status(f"Wave {self.waves_reached} started.")

    def update_waves(self):
        if self.waves_reached == 0 and self.game_started:
            self.start_next_wave()
        if self.wave_enemies_to_spawn > 0:
            self.wave_spawn_timer += 1
            if self.wave_spawn_timer >= 38:
                enemy_type = self.current_wave_plan.pop(0)
                self.spawn_enemy(enemy_type)
                self.wave_enemies_to_spawn -= 1
                self.wave_spawn_timer = 0
        elif self.game_started and self.enemies == [] and self.waves_reached > 0:
            if self.waves_reached >= self.get_total_waves():
                self.end_game("WIN")
            else:
                self.start_next_wave()
        if self.base_lives <= 0:
            self.end_game("LOSE")

    def update_game(self):
        if self.game_started and not self.paused and not self.game_over:
            self.update_waves()
            self.update_enemies()
            self.update_towers()
        self.update_particles()

    def add_tower(self, gx: int, gy: int):
        if self.selected_tower_id not in self.unlocked_towers:
            self.set_status("That tower is still locked.")
            return
        if (gx, gy) in PATH:
            self.set_status("You cannot place a tower on the path.")
            return
        if any(t.gx == gx and t.gy == gy for t in self.towers):
            self.set_status("A tower already stands there.")
            return
        blueprint = TOWER_CATALOG[self.selected_tower_id]
        if self.gold < blueprint["cost"]:
            self.set_status("Not enough gold.")
            return
        self.gold -= blueprint["cost"]
        self.towers.append(Tower(gx=gx, gy=gy, tower_type=self.selected_tower_id))
        self.selected_tower_coords = (gx, gy)
        self.set_status(f"{blueprint['name']} tower placed.")

    def upgrade_tower_at(self, gx: int, gy: int):
        tower = next((item for item in self.towers if item.gx == gx and item.gy == gy), None)
        if tower is None:
            self.set_status("No tower to upgrade on this tile.")
            return
        if tower.level >= MAX_TOWER_LEVEL:
            self.set_status("Tower is already at max level.")
            return
        cost = self.get_upgrade_cost(tower.level)
        if self.gold < cost:
            self.set_status("Not enough gold for upgrade.")
            return
        self.gold -= cost
        tower.level += 1
        self.selected_tower_coords = (gx, gy)
        self.set_status(f"{TOWER_CATALOG[tower.tower_type]['name']} upgraded to level {tower.level}.")

    def get_selected_tower(self) -> Optional[Tower]:
        if self.selected_tower_coords is None:
            return None
        gx, gy = self.selected_tower_coords
        return next((item for item in self.towers if item.gx == gx and item.gy == gy), None)

    def start_or_resume(self):
        if self.game_over:
            self.reset_game()
            self.game_started = True
            self.set_status("New run started.")
        elif not self.game_started:
            self.game_started = True
            self.set_status("Defense is live.")
        elif self.paused:
            self.paused = False
            self.set_status("Game resumed.")

    def toggle_pause(self):
        if not self.game_started or self.game_over:
            self.set_status("There is nothing to pause.")
            return
        self.paused = not self.paused
        self.set_status("Game paused." if self.paused else "Game resumed.")

    def toggle_cheat_menu(self):
        if not self.is_cheat_user():
            return
        self.cheat_menu_open = not self.cheat_menu_open
        self.set_status("Cheat menu opened." if self.cheat_menu_open else "Cheat menu closed.")

    def skip_wave_cheat(self):
        if not self.game_started or self.game_over:
            self.set_status("Start the run before skipping a wave.")
            return
        if self.waves_reached == 0:
            self.start_next_wave()
            self.set_status("Cheat applied: the first wave has been launched.")
            return
        self.enemies = []
        self.current_wave_plan = []
        self.wave_enemies_to_spawn = 0
        self.wave_spawn_timer = 0
        if self.waves_reached >= self.get_total_waves():
            self.end_game("WIN")
        else:
            self.set_status(f"Cheat applied: wave {self.waves_reached} skipped.")

    def apply_cheat_action(self, action: str):
        if not self.is_cheat_user():
            return
        if action == "gold":
            self.gold += 200
            self.set_status("Cheat applied: +200 gold.")
        elif action == "lives":
            self.base_lives += 3
            self.set_status("Cheat applied: +3 lives.")
        elif action == "coins" and self.current_user_id:
            success, message, coins, unlocked = grant_profile_coins_for_user(self.current_user_id)
            self.profile_coins = coins
            self.unlocked_towers = set(unlocked)
            self.set_status(message if success else "Cheat failed.")
        elif action == "wave":
            self.skip_wave_cheat()
        elif action == "unlock" and self.current_user_id:
            success, message, coins, unlocked = unlock_all_towers_for_user(self.current_user_id)
            self.profile_coins = coins
            self.unlocked_towers = set(unlocked)
            self.set_status(message if success else "Cheat failed.")
        elif action == "close":
            self.cheat_menu_open = False
            self.set_status("Cheat menu closed.")

    def end_game(self, result: str):
        if self.game_over:
            return
        self.game_over = True
        self.paused = False
        self.game_result = result
        self.set_status("Victory. The final wave is down." if result == "WIN" else "Defeat. The line has been breached.")
        if self.current_user_id:
            save_match_result(
                self.current_user_id,
                result,
                self.waves_reached,
                self.kills,
                self.selected_difficulty_id,
            )
            self.load_user_profile()

    def get_board_rect(self) -> pygame.Rect:
        return self.get_layout_metrics()["board_rect"]

    def get_board_outer_rect(self) -> pygame.Rect:
        board_rect = self.get_board_rect()
        pad = max(10, self.get_cell_size() // 5)
        return board_rect.inflate(pad * 2, pad * 2)

    def get_sidebar_rect(self) -> pygame.Rect:
        return self.get_layout_metrics()["sidebar_rect"]

    def get_sidebar_content_rect(self) -> pygame.Rect:
        sidebar = self.get_sidebar_rect()
        pad_x = max(20, min(30, sidebar.width // 16))
        pad_y = max(18, min(28, sidebar.height // 24))
        return pygame.Rect(sidebar.x + pad_x, sidebar.y + pad_y, sidebar.width - (pad_x * 2), sidebar.height - (pad_y * 2))

    def get_cell_size(self) -> int:
        return self.get_layout_metrics()["cell_size"]

    def tower_button_rect(self, order_index: int) -> pygame.Rect:
        content = self.get_sidebar_content_rect()
        tower_start_y = self.tower_section_y() + 42
        gap = 6
        status_top = self.status_rect().top
        available_height = max(168, status_top - tower_start_y - 12)
        button_height = max(36, min(56, (available_height - (gap * (len(TOWER_CATALOG) - 1))) // len(TOWER_CATALOG)))
        return pygame.Rect(content.x, tower_start_y + (order_index * (button_height + gap)), content.width, button_height)

    def difficulty_button_rect(self, order_index: int) -> pygame.Rect:
        content = self.get_sidebar_content_rect()
        button_height = max(34, min(40, content.height // 15))
        button_width = max(132, min(160, content.width // 3))
        return pygame.Rect(content.x, content.y + 46 + (order_index * (button_height + 8)), button_width, button_height)

    def game_length_button_rect(self, order_index: int) -> pygame.Rect:
        content = self.get_sidebar_content_rect()
        top = self.length_section_y() + 44
        gap = 12
        width = (content.width - (gap * 2)) // 3
        return pygame.Rect(content.x + (order_index * (width + gap)), top, width, max(34, min(40, content.height // 15)))

    def status_rect(self) -> pygame.Rect:
        content = self.get_sidebar_content_rect()
        controls_top = self.control_button_rects()["start"].top
        height = max(52, min(78, content.height // 7))
        top = controls_top - height - 12
        return pygame.Rect(content.x, top, content.width, height)

    def control_button_rects(self) -> dict:
        content = self.get_sidebar_content_rect()
        button_height = max(40, min(48, content.height // 12))
        gap = 14
        width = (content.width - (gap * 2)) // 3
        top = content.bottom - button_height
        return {
            "start": pygame.Rect(content.x, top, width, button_height),
            "pause": pygame.Rect(content.x + width + gap, top, width, button_height),
            "restart": pygame.Rect(content.x + ((width + gap) * 2), top, width, button_height),
        }

    def selected_tower_panel_rect(self) -> pygame.Rect:
        status = self.status_rect()
        return pygame.Rect(status.x, status.y - 84, status.width, 72)

    def selected_tower_upgrade_rect(self) -> pygame.Rect:
        panel = self.selected_tower_panel_rect()
        return pygame.Rect(panel.right - 140, panel.y + 18, 120, 36)

    def pause_button_rects(self) -> dict:
        board_rect = self.get_board_rect()
        width = 170
        height = 48
        center_x = board_rect.centerx - (width // 2)
        resume_top = board_rect.centery - 6
        exit_top = resume_top + height + 16
        return {
            "resume": pygame.Rect(center_x, resume_top, width, height),
            "exit": pygame.Rect(center_x, exit_top, width, height),
        }

    def cheat_toggle_rect(self) -> pygame.Rect:
        sidebar = self.get_sidebar_rect()
        width = max(132, min(150, sidebar.width // 3))
        return pygame.Rect(sidebar.right - width - 28, sidebar.y + 8, width, 36)

    def cheat_panel_rect(self) -> pygame.Rect:
        window_width, window_height = self.get_window_size()
        width = min(760, window_width - 120)
        height = min(280, window_height - 160)
        return pygame.Rect((window_width - width) // 2, (window_height - height) // 2, width, height)

    def cheat_action_rects(self) -> dict:
        panel = self.cheat_panel_rect()
        left = panel.x + 26
        top = panel.y + 82
        gap = 24
        width = (panel.width - 52 - (gap * 2)) // 3
        height = 46
        return {
            "gold": pygame.Rect(left, top, width, height),
            "lives": pygame.Rect(left + width + gap, top, width, height),
            "coins": pygame.Rect(left + ((width + gap) * 2), top, width, height),
            "wave": pygame.Rect(left, top + 66, width, height),
            "unlock": pygame.Rect(left + width + gap, top + 66, width, height),
            "close": pygame.Rect(left + ((width + gap) * 2), top + 66, width, height),
        }

    def length_section_y(self) -> int:
        content = self.get_sidebar_content_rect()
        last_diff_button = self.difficulty_button_rect(len(DIFFICULTIES) - 1)
        return last_diff_button.bottom + max(16, content.height // 40)

    def tower_section_y(self) -> int:
        content = self.get_sidebar_content_rect()
        last_length_button = self.game_length_button_rect(len(GAME_LENGTHS) - 1)
        return last_length_button.bottom + max(18, content.height // 34)

    def draw_button(self, rect: pygame.Rect, label: str, active: bool = False, danger: bool = False):
        color = COLOR_RED if danger else COLOR_GREEN if active else COLOR_ACCENT
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_BLACK, rect, 2, border_radius=12)
        text = self.font_small.render(label, True, COLOR_WHITE)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_panel(self, rect: pygame.Rect, alt: bool = False):
        color = COLOR_PANEL_ALT if alt else COLOR_PANEL
        pygame.draw.rect(self.screen, color, rect, border_radius=22)
        pygame.draw.rect(self.screen, COLOR_LINE, rect, 2, border_radius=22)

    def draw_overlay(self, title: str):
        board_rect = self.get_board_rect()
        overlay = pygame.Surface(board_rect.size, pygame.SRCALPHA)
        overlay.fill((14, 31, 40, 150))
        self.screen.blit(overlay, board_rect.topleft)
        text = self.font_large.render(title, True, COLOR_WHITE)
        center = board_rect.center
        self.screen.blit(text, text.get_rect(center=(center[0], center[1] - 60)))
        if title == "PAUSED":
            buttons = self.pause_button_rects()
            self.draw_button(buttons["resume"], "Resume", active=True)
            self.draw_button(buttons["exit"], "Exit", danger=True)

    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        words = text.split()
        if not words:
            return [""]
        lines = [words[0]]
        for word in words[1:]:
            candidate = f"{lines[-1]} {word}"
            if font.size(candidate)[0] <= max_width:
                lines[-1] = candidate
            else:
                lines.append(word)
        return lines

    def draw_wrapped_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        topleft: Tuple[int, int],
        max_width: int,
        line_spacing: int = 2,
        max_lines: Optional[int] = None,
    ) -> int:
        lines = self.wrap_text(text, font, max_width)
        if max_lines is not None:
            lines = lines[:max_lines]
        y = topleft[1]
        line_height = font.get_linesize()
        for line in lines:
            surf = font.render(line, True, color)
            self.screen.blit(surf, (topleft[0], y))
            y += line_height + line_spacing
        return y

    def draw_cheat_panel(self):
        panel = self.cheat_panel_rect()
        shade = pygame.Surface(self.get_window_size(), pygame.SRCALPHA)
        shade.fill((14, 31, 40, 120))
        self.screen.blit(shade, (0, 0))
        self.draw_panel(panel, alt=True)
        self.screen.blit(self.font_large.render("Cheat Menu", True, COLOR_TEXT), (panel.x + 26, panel.y + 22))
        hint = self.font_tiny.render("Enabled only for user sa.", True, COLOR_MUTED)
        self.screen.blit(hint, (panel.x + 28, panel.y + 56))

        labels = {
            "gold": "Gold +200",
            "lives": "Lives +3",
            "coins": "Profile +500",
            "wave": "Skip wave",
            "unlock": "Unlock all towers",
            "close": "Close",
        }
        for action, rect in self.cheat_action_rects().items():
            self.draw_button(rect, labels[action], active=(action != "close"), danger=(action == "close"))

    def draw_game(self):
        self.screen.fill(COLOR_BG)
        metrics = self.get_layout_metrics()
        board_rect = self.get_board_rect()
        board_outer_rect = self.get_board_outer_rect()
        hud_rect = metrics["hud_rect"]
        sidebar_rect = self.get_sidebar_rect()
        sidebar_content = self.get_sidebar_content_rect()
        cell = self.get_cell_size()
        self.draw_panel(board_outer_rect)
        self.draw_panel(sidebar_rect, alt=True)

        pygame.draw.rect(self.screen, (241, 250, 248), board_rect, border_radius=18)
        for px, py in PATH:
            pygame.draw.rect(
                self.screen,
                COLOR_PATH,
                pygame.Rect(board_rect.x + px * cell, board_rect.y + py * cell, cell, cell),
            )

        for index in range(GRID + 1):
            pygame.draw.line(self.screen, COLOR_GRID, (board_rect.x + index * cell, board_rect.y), (board_rect.x + index * cell, board_rect.bottom), 1)
            pygame.draw.line(self.screen, COLOR_GRID, (board_rect.x, board_rect.y + index * cell), (board_rect.right, board_rect.y + index * cell), 1)

        title = self.font_large.render("Tower Defense Lite", True, COLOR_TEXT)
        self.screen.blit(title, (board_outer_rect.x, metrics["outer_margin"] + 8))
        subtitle = self.font_tiny.render("Desktop version of the web game", True, COLOR_MUTED)
        self.screen.blit(subtitle, (board_outer_rect.x + 2, metrics["outer_margin"] + 52))

        hud_lines = [
            f"Profile coins: {self.profile_coins}",
            f"Gold: {self.gold}",
            f"Lives: {self.base_lives}",
            f"Wave: {self.waves_reached}/{self.get_total_waves()}",
            f"Kills: {self.kills}",
            f"Game length: {self.get_game_length()['name']} ({self.get_total_waves()} waves)",
            f"Selected tower: {TOWER_CATALOG[self.selected_tower_id]['name']}",
        ]
        pygame.draw.rect(self.screen, COLOR_BG, hud_rect)
        for index, line in enumerate(hud_lines):
            surf = self.font_small.render(line, True, COLOR_TEXT)
            self.screen.blit(surf, (hud_rect.x, hud_rect.y + (index * self.font_small.get_linesize()) + 2))

        diff_title = self.font_medium.render("Difficulty", True, COLOR_TEXT)
        self.screen.blit(diff_title, (sidebar_content.x, sidebar_content.y))
        for index, diff_id in enumerate(DIFFICULTIES):
            self.draw_button(self.difficulty_button_rect(index), DIFFICULTIES[diff_id]["name"], active=(diff_id == self.selected_difficulty_id))

        length_title = self.font_medium.render("Game Length", True, COLOR_TEXT)
        self.screen.blit(length_title, (sidebar_content.x, self.length_section_y()))
        for index, length_id in enumerate(GAME_LENGTHS):
            rect = self.game_length_button_rect(index)
            waves = GAME_LENGTHS[length_id]["waves"]
            label = f"{GAME_LENGTHS[length_id]['name']} {waves}"
            self.draw_button(rect, label, active=(length_id == self.selected_game_length_id))

        tower_title = self.font_medium.render("Tower Hangar", True, COLOR_TEXT)
        self.screen.blit(tower_title, (sidebar_content.x, self.tower_section_y()))
        for index, tower_id in enumerate(TOWER_CATALOG):
            tower = TOWER_CATALOG[tower_id]
            rect = self.tower_button_rect(index)
            is_selected = tower_id == self.selected_tower_id
            is_unlocked = tower_id in self.unlocked_towers
            bg = tower["color"] if is_unlocked else (145, 159, 165)
            pygame.draw.rect(self.screen, bg, rect, border_radius=16)
            pygame.draw.rect(self.screen, COLOR_GREEN if is_selected else COLOR_BLACK, rect, 3, border_radius=16)
            title_surf = self.font_small.render(f"{tower['name']} {'(Locked)' if not is_unlocked else ''}", True, COLOR_WHITE)
            self.screen.blit(title_surf, (rect.x + 14, rect.y + 6))
            if rect.height >= 48:
                desc_surf = self.font_tiny.render(tower["description"], True, COLOR_WHITE)
                self.screen.blit(desc_surf, (rect.x + 14, rect.y + 22))
            if rect.height >= 56:
                meta_surf = self.font_tiny.render(f"Build {tower['cost']} | Range {tower['range']} | Unlock {tower['unlock_cost']}", True, COLOR_WHITE)
                self.screen.blit(meta_surf, (rect.x + 14, rect.y + 38))

        status_rect = self.status_rect()
        selected_tower = self.get_selected_tower()
        if selected_tower:
            panel = self.selected_tower_panel_rect()
            pygame.draw.rect(self.screen, COLOR_PANEL, panel, border_radius=12)
            pygame.draw.rect(self.screen, COLOR_LINE, panel, 2, border_radius=12)
            tower_stats = self.get_tower_stats(selected_tower)
            upgrade_cost = self.get_upgrade_cost(selected_tower.level) if selected_tower.level < MAX_TOWER_LEVEL else None
            title_line = f"{TOWER_CATALOG[selected_tower.tower_type]['name']} L{selected_tower.level}"
            meta_line = f"DMG {tower_stats['damage']} | Range {tower_stats['range']} | Rate {tower_stats['cooldown']}"
            self.screen.blit(self.font_small.render(title_line, True, COLOR_TEXT), (panel.x + 12, panel.y + 10))
            self.screen.blit(self.font_tiny.render(meta_line, True, COLOR_MUTED), (panel.x + 12, panel.y + 38))
            if upgrade_cost is None:
                self.draw_button(self.selected_tower_upgrade_rect(), "MAX", active=True)
            else:
                self.draw_button(
                    self.selected_tower_upgrade_rect(),
                    f"Upgrade {upgrade_cost}",
                    active=(self.gold >= upgrade_cost),
                )

        pygame.draw.rect(self.screen, COLOR_PANEL, status_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_LINE, status_rect, 2, border_radius=12)
        inner_x = status_rect.x + 12
        inner_y = status_rect.y + 8
        inner_width = status_rect.width - 24
        text_bottom = self.draw_wrapped_text(self.status_message, self.font_tiny, COLOR_TEXT, (inner_x, inner_y), inner_width, line_spacing=1, max_lines=2)
        help_text = "Left click: select/place | Right click: quick upgrade | ESC pause | 1/2/3 diff | 7/8/9 length | Q/W/E/R tower | U unlock"
        self.draw_wrapped_text(help_text, self.font_tiny, COLOR_MUTED, (inner_x, text_bottom + 4), inner_width, line_spacing=1, max_lines=3)

        controls = self.control_button_rects()
        self.draw_button(controls["start"], "Start", active=self.game_started and not self.paused and not self.game_over)
        self.draw_button(controls["pause"], "Pause", active=self.paused)
        self.draw_button(controls["restart"], "Restart", danger=self.game_over)

        if self.is_cheat_user():
            self.draw_button(self.cheat_toggle_rect(), "Cheats", active=self.cheat_menu_open)

        for tower in self.towers:
            tower_info = TOWER_CATALOG[tower.tower_type]
            inset = max(6, cell // 6)
            tx = board_rect.x + tower.gx * cell + inset
            ty = board_rect.y + tower.gy * cell + inset
            size = max(10, cell - (inset * 2))
            if self.selected_tower_coords == (tower.gx, tower.gy):
                selected_stats = self.get_tower_stats(tower)
                range_surface = pygame.Surface(self.get_window_size(), pygame.SRCALPHA)
                pygame.draw.circle(
                    range_surface,
                    (*tower_info["color"], 50),
                    (int(board_rect.x + tower.gx * cell + (cell / 2)), int(board_rect.y + tower.gy * cell + (cell / 2))),
                    selected_stats["range"],
                    2,
                )
                self.screen.blit(range_surface, (0, 0))
            pygame.draw.rect(self.screen, tower_info["color"], (tx, ty, size, size), border_radius=min(10, size // 3))
            self.screen.blit(self.font_tiny.render(str(tower.level), True, COLOR_WHITE), (tx + max(6, size // 4), ty + max(4, size // 5)))

        for enemy in self.enemies:
            enemy_color = COLOR_WHITE if enemy.hit_flash_ticks > 0 else enemy.color
            pygame.draw.circle(self.screen, enemy_color, (int(enemy.x), int(enemy.y)), enemy.radius)
            pygame.draw.rect(self.screen, COLOR_BLACK, (int(enemy.x - 16), int(enemy.y - enemy.radius - 12), 32, 5), border_radius=3)
            hp_width = int(max(0, (enemy.hp / enemy.max_hp) * 32))
            hp_color = COLOR_HP_BOSS if enemy.enemy_type == "boss" else COLOR_HP
            pygame.draw.rect(self.screen, hp_color, (int(enemy.x - 16), int(enemy.y - enemy.radius - 12), hp_width, 5), border_radius=3)

        for particle in self.particles:
            pygame.draw.circle(self.screen, particle.color, (int(particle.x), int(particle.y)), max(1, int(particle.radius)))

        if self.paused and not self.game_over:
            self.draw_overlay("PAUSED")
        if self.game_over:
            self.draw_overlay("VICTORY" if self.game_result == "WIN" else "DEFEAT")
        if self.cheat_menu_open and self.is_cheat_user():
            self.draw_cheat_panel()

    def draw_menu(self):
        self.screen.fill(COLOR_BG)
        window_width, window_height = self.get_window_size()
        title = self.font_large.render("Tower Defense Lite", True, COLOR_TEXT)
        self.screen.blit(title, title.get_rect(center=(window_width // 2, max(120, window_height // 5))))
        subtitle = self.font_small.render("Desktop build with account sync", True, COLOR_MUTED)
        self.screen.blit(subtitle, subtitle.get_rect(center=(window_width // 2, max(160, window_height // 5 + 45))))
        login_rect = pygame.Rect((window_width // 2) - 120, max(240, window_height // 2 - 40), 240, 56)
        quit_rect = pygame.Rect((window_width // 2) - 120, login_rect.bottom + 24, 240, 56)
        self.draw_button(login_rect, "Login")
        self.draw_button(quit_rect, "Quit", danger=True)
        return login_rect, quit_rect

    def draw_login(self):
        self.screen.fill(COLOR_BG)
        window_width, window_height = self.get_window_size()
        panel_width = min(680, window_width - 120)
        panel_height = min(420, window_height - 140)
        panel = pygame.Rect((window_width - panel_width) // 2, (window_height - panel_height) // 2, panel_width, panel_height)
        self.draw_panel(panel)
        self.screen.blit(self.font_large.render("Login", True, COLOR_TEXT), (panel.x + 40, panel.y + 30))

        field_width = panel.width - 80
        username_rect = pygame.Rect(panel.x + 40, panel.y + 120, field_width, 42)
        password_rect = pygame.Rect(panel.x + 40, panel.y + 210, field_width, 42)
        login_rect = pygame.Rect(panel.x + 40, panel.y + 300, 220, 48)
        back_rect = pygame.Rect(panel.x + 280, panel.y + 300, 140, 48)

        for label, rect in [("Username", username_rect), ("Password", password_rect)]:
            self.screen.blit(self.font_small.render(label, True, COLOR_TEXT), (rect.x, rect.y - 28))

        for rect, selected in [(username_rect, self.selected_input == "username"), (password_rect, self.selected_input == "password")]:
            pygame.draw.rect(self.screen, COLOR_PANEL_ALT if selected else COLOR_WHITE, rect, border_radius=10)
            pygame.draw.rect(self.screen, COLOR_BLACK, rect, 2, border_radius=10)

        self.screen.blit(self.font_small.render(self.username_input, True, COLOR_TEXT), (username_rect.x + 10, username_rect.y + 10))
        hidden = "*" * len(self.password_input)
        self.screen.blit(self.font_small.render(hidden, True, COLOR_TEXT), (password_rect.x + 10, password_rect.y + 10))
        self.draw_button(login_rect, "Login")
        self.draw_button(back_rect, "Back")

        if self.login_error:
            self.screen.blit(self.font_small.render("Invalid credentials.", True, COLOR_RED), (panel.x + 40, panel.y + 270))

        hint = self.font_tiny.render("Use web registration first if you do not have an account.", True, COLOR_MUTED)
        self.screen.blit(hint, (panel.x + 40, panel.y + 370))
        return login_rect, back_rect, username_rect, password_rect

    def draw_stats(self):
        self.screen.fill(COLOR_BG)
        window_width, window_height = self.get_window_size()
        panel_width = min(880, window_width - 120)
        panel_height = min(620, window_height - 100)
        panel = pygame.Rect((window_width - panel_width) // 2, (window_height - panel_height) // 2, panel_width, panel_height)
        self.draw_panel(panel)
        self.screen.blit(self.font_large.render(f"{self.current_username} profile", True, COLOR_TEXT), (panel.x + 40, panel.y + 30))

        stats = get_user_stats(self.current_user_id) if self.current_user_id else {"wins": 0, "losses": 0, "total_kills": 0, "best_wave": 0, "total_games": 0, "coins": 0}
        self.load_user_profile()
        lines = [
            f"Games played: {stats['total_games']}",
            f"Profile coins: {self.profile_coins}",
            f"Database coins: {stats['coins']}",
            f"Wins: {stats['wins']}",
            f"Losses: {stats['losses']}",
            f"Total kills: {stats['total_kills']}",
            f"Best wave: {stats['best_wave']}",
            "Unlocked towers: " + ", ".join(TOWER_CATALOG[t]["name"] for t in TOWER_CATALOG if t in self.unlocked_towers),
        ]
        content_x = panel.x + 40
        content_width = panel.width - 80
        y = panel.y + 120
        line_gap = 14
        for line in lines[:-1]:
            surf = self.font_medium.render(line, True, COLOR_TEXT)
            self.screen.blit(surf, (content_x, y))
            y += self.font_medium.get_linesize() + line_gap

        y += 4
        y = self.draw_wrapped_text(
            lines[-1],
            self.font_medium,
            COLOR_TEXT,
            (content_x, y),
            content_width,
            line_spacing=6,
        )

        button_top = min(panel.bottom - 92, y + 28)
        play_rect = pygame.Rect(panel.x + 40, button_top, 220, 52)
        logout_rect = pygame.Rect(panel.x + 280, button_top, 180, 52)
        self.draw_button(play_rect, "Play")
        self.draw_button(logout_rect, "Logout", danger=True)
        return play_rect, logout_rect

    def handle_board_click(self, pos: Tuple[int, int], button: int):
        if self.game_over or self.paused:
            return
        board_rect = self.get_board_rect()
        cell = self.get_cell_size()
        if not board_rect.collidepoint(pos):
            self.selected_tower_coords = None
            return
        gx = (pos[0] - board_rect.x) // cell
        gy = (pos[1] - board_rect.y) // cell
        if not (0 <= gx < GRID and 0 <= gy < GRID):
            self.selected_tower_coords = None
            return
        existing_tower = next((item for item in self.towers if item.gx == gx and item.gy == gy), None)
        if button == 1:
            if existing_tower:
                self.selected_tower_coords = (gx, gy)
                self.set_status(f"{TOWER_CATALOG[existing_tower.tower_type]['name']} selected.")
            else:
                self.add_tower(gx, gy)
        elif button == 3:
            self.upgrade_tower_at(gx, gy)

    def handle_game_click(self, pos: Tuple[int, int], button: int):
        if self.is_cheat_user() and self.cheat_toggle_rect().collidepoint(pos):
            self.toggle_cheat_menu()
            return

        if self.cheat_menu_open and self.is_cheat_user():
            for action, rect in self.cheat_action_rects().items():
                if rect.collidepoint(pos):
                    self.apply_cheat_action(action)
                    return
            if self.cheat_panel_rect().collidepoint(pos):
                return
            self.cheat_menu_open = False
            return

        controls = self.control_button_rects()
        if self.paused and not self.game_over:
            for action, rect in self.pause_button_rects().items():
                if rect.collidepoint(pos):
                    if action == "resume":
                        self.paused = False
                        self.set_status("Game resumed.")
                    else:
                        self.reset_game()
                        self.state = GameState.STATS if self.current_user_id else GameState.MENU
                        self.set_status("Run exited from pause menu.")
                    return

        if controls["start"].collidepoint(pos):
            self.start_or_resume()
            return
        if controls["pause"].collidepoint(pos):
            self.toggle_pause()
            return
        if controls["restart"].collidepoint(pos):
            self.reset_game()
            return

        selected_tower = self.get_selected_tower()
        if selected_tower and self.selected_tower_upgrade_rect().collidepoint(pos):
            self.upgrade_tower_at(selected_tower.gx, selected_tower.gy)
            return

        for index, diff_id in enumerate(DIFFICULTIES):
            rect = self.difficulty_button_rect(index)
            if rect.collidepoint(pos):
                if self.game_started and not self.game_over:
                    self.set_status("Difficulty can only be changed before the run starts.")
                else:
                    self.selected_difficulty_id = diff_id
                    self.reset_game()
                return

        for index, length_id in enumerate(GAME_LENGTHS):
            rect = self.game_length_button_rect(index)
            if rect.collidepoint(pos):
                if self.game_started and not self.game_over:
                    self.set_status("Game length can only be changed before the run starts.")
                else:
                    self.selected_game_length_id = length_id
                    self.reset_game()
                return

        for index, tower_id in enumerate(TOWER_CATALOG):
            rect = self.tower_button_rect(index)
            if rect.collidepoint(pos):
                self.selected_tower_id = tower_id
                self.selected_tower_coords = None
                if tower_id in self.unlocked_towers:
                    self.set_status(f"{TOWER_CATALOG[tower_id]['name']} selected.")
                else:
                    unlock_cost = TOWER_CATALOG[tower_id]["unlock_cost"]
                    self.set_status(f"{TOWER_CATALOG[tower_id]['name']} is locked. Press U to unlock for {unlock_cost} coins.")
                return

        self.selected_tower_coords = None
        self.handle_board_click(pos, button)

    def try_login(self):
        user_id = authenticate_user(self.username_input, self.password_input)
        if user_id:
            self.current_user_id = user_id
            self.current_username = self.username_input
            self.load_user_profile()
            self.reset_game()
            self.state = GameState.STATS
            self.login_error = False
        else:
            self.login_error = True
            self.password_input = ""

    def handle_keydown(self, event: pygame.event.Event):
        if self.state == GameState.LOGIN:
            if event.key == pygame.K_TAB:
                self.selected_input = "password" if self.selected_input == "username" else "username"
            elif event.key == pygame.K_BACKSPACE:
                if self.selected_input == "username":
                    self.username_input = self.username_input[:-1]
                else:
                    self.password_input = self.password_input[:-1]
            elif event.key == pygame.K_RETURN:
                self.try_login()
            elif event.unicode.isprintable():
                if self.selected_input == "username":
                    self.username_input += event.unicode
                else:
                    self.password_input += event.unicode
            return

        if self.state != GameState.PLAYING:
            return

        if event.key == pygame.K_ESCAPE:
            self.toggle_pause()
        elif event.key == pygame.K_SPACE:
            self.start_or_resume()
        elif event.key == pygame.K_p:
            self.toggle_pause()
        elif event.key == pygame.K_n:
            self.reset_game()
        elif event.key == pygame.K_1 and not self.game_started:
            self.selected_difficulty_id = "easy"
            self.reset_game()
        elif event.key == pygame.K_2 and not self.game_started:
            self.selected_difficulty_id = "normal"
            self.reset_game()
        elif event.key == pygame.K_3 and not self.game_started:
            self.selected_difficulty_id = "hard"
            self.reset_game()
        elif event.key == pygame.K_7 and not self.game_started:
            self.selected_game_length_id = "short"
            self.reset_game()
        elif event.key == pygame.K_8 and not self.game_started:
            self.selected_game_length_id = "normal"
            self.reset_game()
        elif event.key == pygame.K_9 and not self.game_started:
            self.selected_game_length_id = "long"
            self.reset_game()
        elif event.key == pygame.K_q:
            self.selected_tower_id = "basic"
            self.set_status("Basic tower selected.")
        elif event.key == pygame.K_w:
            self.selected_tower_id = "sniper"
            self.set_status("Sniper tower selected." if "sniper" in self.unlocked_towers else "Sniper is locked.")
        elif event.key == pygame.K_e:
            self.selected_tower_id = "splash"
            self.set_status("Splash tower selected." if "splash" in self.unlocked_towers else "Splash is locked.")
        elif event.key == pygame.K_r:
            self.selected_tower_id = "frost"
            self.set_status("Frost tower selected." if "frost" in self.unlocked_towers else "Frost is locked.")
        elif event.key == pygame.K_u and self.current_user_id:
            success, message, coins, unlocked = unlock_tower_for_user(self.current_user_id, self.selected_tower_id)
            self.profile_coins = coins
            self.unlocked_towers = set(unlocked)
            self.set_status(message)
            if not success and self.selected_tower_id not in self.unlocked_towers:
                self.selected_tower_id = "basic"
        elif event.key == pygame.K_F1 and self.is_cheat_user():
            self.toggle_cheat_menu()
        elif event.key == pygame.K_g and self.is_cheat_user():
            self.apply_cheat_action("gold")
        elif event.key == pygame.K_h and self.is_cheat_user():
            self.apply_cheat_action("lives")
        elif event.key == pygame.K_j and self.is_cheat_user():
            self.apply_cheat_action("coins")
        elif event.key == pygame.K_k and self.is_cheat_user():
            self.apply_cheat_action("wave")
        elif event.key == pygame.K_l and self.is_cheat_user():
            self.apply_cheat_action("unlock")
        elif event.key == pygame.K_RETURN and self.game_over:
            self.state = GameState.STATS

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    width = max(MIN_SCREEN_WIDTH, event.w)
                    height = max(MIN_SCREEN_HEIGHT, event.h)
                    self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.state == GameState.MENU:
                        login_rect, quit_rect = self.draw_menu()
                        if login_rect.collidepoint(pos):
                            self.state = GameState.LOGIN
                            self.username_input = ""
                            self.password_input = ""
                            self.selected_input = "username"
                            self.login_error = False
                        elif quit_rect.collidepoint(pos):
                            running = False
                    elif self.state == GameState.LOGIN:
                        login_rect, back_rect, username_rect, password_rect = self.draw_login()
                        if username_rect.collidepoint(pos):
                            self.selected_input = "username"
                            self.login_error = False
                        elif password_rect.collidepoint(pos):
                            self.selected_input = "password"
                            self.login_error = False
                        elif login_rect.collidepoint(pos):
                            self.try_login()
                        elif back_rect.collidepoint(pos):
                            self.state = GameState.MENU
                    elif self.state == GameState.STATS:
                        play_rect, logout_rect = self.draw_stats()
                        if play_rect.collidepoint(pos):
                            self.reset_game()
                            self.state = GameState.PLAYING
                        elif logout_rect.collidepoint(pos):
                            self.current_user_id = None
                            self.current_username = ""
                            self.state = GameState.MENU
                    elif self.state == GameState.PLAYING:
                        self.handle_game_click(pos, event.button)
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)

            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.LOGIN:
                self.draw_login()
            elif self.state == GameState.STATS:
                self.draw_stats()
            elif self.state == GameState.PLAYING:
                self.update_game()
                self.draw_game()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = TowerDefenseGame()
    game.run()
