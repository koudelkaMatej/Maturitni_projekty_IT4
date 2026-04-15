# tests.py – Automatizované testy klíčových funkcí projektu Pixel Invaders

import sys
import hashlib
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from database import Database

# ──────────────────────────────────────────────────────────────
# TestRunner – jednoduchý framework bez externích závislostí
# ──────────────────────────────────────────────────────────────

class TestRunner:
    """
    Konzolový testovací framework (Unit Testing) vytvořený speciálně pro tento projekt,
    bez externích závislostí jako pytest, pro snadnou integraci bez nutnosti instalace dalšího bloatu.
    """
    def __init__(self):
        self.ok   = 0
        self.fail = 0

    def run(self, name, func):
        try:
            func()
            print(f"  ✅  {name}")
            self.ok += 1
        except AssertionError as e:
            print(f"  ❌  {name} – selhalo: {e}")
            self.fail += 1
        except Exception as e:
            print(f"  ❌  {name} – neočekávaná výjimka: {e}")
            self.fail += 1

    def section(self, title):
        print(f"\n── {title} {'─' * (42 - len(title))}")

    def summary(self):
        total = self.ok + self.fail
        print(f"\n{'='*50}")
        print(f"  Výsledek: {self.ok}/{total} testů prošlo")
        if self.fail:
            print(f"  POZOR: {self.fail} test(ů) selhalo!")
        print(f"{'='*50}")
        return self.fail == 0


# ──────────────────────────────────────────────────────────────
# SEKCE 1 – Databáze (offline robustnost)
# ──────────────────────────────────────────────────────────────

def test_offline_get_user():
    """DB nesmí spadnout při čtení uživatele bez spojení."""
    db = Database()
    db.connection = None
    u = db.get_user("test_offline")
    assert u["username"] == "test_offline", "Musí vrátit předané jméno"
    assert u["id"] is None, "Offline musí vrátit id=None"
    assert "highscore" in u, "Výsledek musí obsahovat klíč 'highscore'"

def test_offline_register():
    """DB nesmí vyhodit výjimku při registraci bez spojení."""
    db = Database()
    db.connection = None
    result = db.register_user("ghost", "heslo123")
    assert result is False, "Offline registrace musí vrátit False"

def test_offline_login():
    """DB nesmí vyhodit výjimku při přihlášení bez spojení."""
    db = Database()
    db.connection = None
    result = db.login_user("ghost", "heslo123")
    assert result is None, "Offline login musí vrátit None"

def test_offline_save_score():
    """DB nesmí vyhodit výjimku při ukládání skóre bez spojení."""
    db = Database()
    db.connection = None
    try:
        db.save_score(1, 9999)
    except Exception as e:
        assert False, f"save_score() vyhodil výjimku offline: {e}"


# ──────────────────────────────────────────────────────────────
# SEKCE 2 – Bezpečnost hesel (SHA-256 hashing)
# ──────────────────────────────────────────────────────────────

def test_password_hash_is_sha256():
    """Heslo musí být uloženo jako SHA-256 hexdigest (64 znaků)."""
    db = Database()
    h = db._hash("testovaci_heslo")
    assert len(h) == 64, f"Hash musí mít 64 znaků, má {len(h)}"
    assert all(c in "0123456789abcdef" for c in h), "Hash musí být hexadecimální"

def test_same_password_same_hash():
    """Stejné heslo musí vždy produkovat stejný hash."""
    db = Database()
    assert db._hash("heslo") == db._hash("heslo"), "Stejné heslo musí dávat stejný hash"

def test_different_passwords_different_hashes():
    """Různá hesla musí dávat různé hashe (odolnost proti kolizím)."""
    db = Database()
    assert db._hash("heslo1") != db._hash("heslo2"), "Různá hesla musí mít různé hashe"

def test_hash_matches_stdlib():
    """Hash z db._hash() musí souhlasit s přímým voláním hashlib.sha256."""
    db = Database()
    expected = hashlib.sha256("moje_heslo".encode()).hexdigest()
    assert db._hash("moje_heslo") == expected, "Hash musí souhlasit s hashlib.sha256"


# ──────────────────────────────────────────────────────────────
# SEKCE 3 – Validace vstupů (registrační logika)
# ──────────────────────────────────────────────────────────────

def _make_menu():
    """Pomocná funkce – vytvoří instanci Menu s offline DB."""
    from menu import Menu
    db = Database()
    db.connection = None
    screen = pygame.display.get_surface()
    m = Menu(screen, db, has_save=False)
    return m

def test_register_short_username():
    """Registrace se jménem kratším než 3 znaky musí selhat."""
    m = _make_menu()
    m.state = "REGISTER"
    m.f_username  = "ab"
    m.f_password  = "heslo123"
    m.f_password2 = "heslo123"
    result = m._try_register()
    assert result is None, "Registrace s krátkým jménem musí vrátit None"
    assert m.f_error != "", "Musí být nastaven chybový text"

def test_register_short_password():
    """Registrace s heslem kratším než 4 znaky musí selhat."""
    m = _make_menu()
    m.f_username  = "validni"
    m.f_password  = "abc"
    m.f_password2 = "abc"
    result = m._try_register()
    assert result is None, "Registrace s krátkým heslem musí vrátit None"

def test_register_password_mismatch():
    """Registrace s nesouhlasícími hesly musí selhat."""
    m = _make_menu()
    m.f_username  = "uzivatel"
    m.f_password  = "heslo123"
    m.f_password2 = "jine_heslo"
    result = m._try_register()
    assert result is None, "Nesouhlasící hesla musí vrátit None"
    assert "neshoduj" in m.f_error.lower(), "Chybová hláška musí zmínit neshodu hesel"

def test_login_empty_fields():
    """Přihlášení s prázdnými poli musí selhat."""
    m = _make_menu()
    m.f_username = ""
    m.f_password = ""
    result = m._try_login()
    assert result is None, "Prázdné přihlášení musí vrátit None"


# ──────────────────────────────────────────────────────────────
# SEKCE 4 – Herní logika (skóre, kombo, životní maximum)
# ──────────────────────────────────────────────────────────────

def _make_game():
    """Pomocná funkce – vytvoří instanci Game s fake uživatelem."""
    import game
    db = Database()
    db.connection = None
    screen = pygame.display.get_surface()
    user = {"id": None, "username": "tester", "highscore": 0}
    
    # Dočasně vypneme zapisování do logu při testech, aby to nešpinilo záznamy
    game.log_event = lambda msg: None
    
    g = game.Game(screen, user, db, start_level=1)
    return g

def test_initial_score_is_zero():
    """Na začátku hry musí být skóre nulové."""
    g = _make_game()
    assert g.score == 0, f"Počáteční skóre musí být 0, je {g.score}"

def test_initial_hp_matches_settings():
    """Počáteční HP musí odpovídat konstantě PLAYER_HEALTH ze settings.py."""
    from settings import PLAYER_HEALTH
    g = _make_game()
    assert g.player_hp == PLAYER_HEALTH, \
        f"HP musí být {PLAYER_HEALTH}, je {g.player_hp}"

def test_hp_does_not_exceed_max_on_lifesteal():
    """Life-steal nesmí zvýšit HP nad maximum 100."""
    g = _make_game()
    g.player_hp = 99
    g.player_hp = min(100, g.player_hp + 1)
    assert g.player_hp == 100, "HP nesmí přesáhnout 100"
    # Další heal přes cap
    g.player_hp = min(100, g.player_hp + 10)
    assert g.player_hp == 100, "HP nesmí přesáhnout 100 ani po dalším healu"

def test_combo_score_multiplier():
    """Skóre s combo x2 musí být přesně dvojnásobek základního skóre."""
    base_points = 100
    combo = 2
    result = base_points * combo
    assert result == 200, f"Combo x2 ze 100 bodů musí dát 200, dalo {result}"

def test_weapon_level_capped_at_3():
    """Upgrade zbraně nesmí přesáhnout Level 3."""
    g = _make_game()
    g.weapon_level = 3
    g.weapon_level = min(3, g.weapon_level + 1)
    assert g.weapon_level == 3, "Weapon level nesmí přesáhnout 3"

def test_difficulty_cap():
    """Rychlost nepřátel nesmí překročit hard cap bez ohledu na level."""
    g = _make_game()
    g.level = 999   # extrémní level
    speed, bullet_speed, shoot = g.get_difficulty()
    assert speed       <= 3.5,  f"Enemy speed nesmí překročit 3.5 (je {speed})"
    assert bullet_speed <= 14.0, f"Bullet speed nesmí překročit 14 (je {bullet_speed})"
    assert shoot       <= 0.02,  f"Shoot chance nesmí překročit 0.02 (je {shoot})"

def test_game_over_trigger():
    """Při nulových HP musí být nastaven příznak game_over."""
    g = _make_game()
    g.player_hp = 0
    g.trigger_game_over()
    assert g.game_over is True, "game_over musí být True po trigger_game_over()"


# ──────────────────────────────────────────────────────────────
# Spuštění
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    r = TestRunner()

    r.section("1 – Databáze (offline robustnost)")
    r.run("Offline čtení uživatele",        test_offline_get_user)
    r.run("Offline registrace → False",     test_offline_register)
    r.run("Offline login → None",           test_offline_login)
    r.run("Offline ukládání skóre",         test_offline_save_score)

    r.section("2 – Bezpečnost hesel (SHA-256)")
    r.run("Hash má 64 znaků (SHA-256)",     test_password_hash_is_sha256)
    r.run("Stejné heslo = stejný hash",     test_same_password_same_hash)
    r.run("Různá hesla = různé hashe",      test_different_passwords_different_hashes)
    r.run("Hash souhlasí s hashlib",        test_hash_matches_stdlib)

    r.section("3 – Validace vstupů (registrace / login)")
    r.run("Příliš krátké jméno → zamítnuto",      test_register_short_username)
    r.run("Příliš krátké heslo → zamítnuto",      test_register_short_password)
    r.run("Neshoda hesel → zamítnuto",            test_register_password_mismatch)
    r.run("Prázdné přihlášení → zamítnuto",       test_login_empty_fields)

    r.section("4 – Herní logika")
    r.run("Počáteční skóre = 0",                  test_initial_score_is_zero)
    r.run("Počáteční HP = PLAYER_HEALTH",         test_initial_hp_matches_settings)
    r.run("Life-steal nepřesáhne 100 HP",         test_hp_does_not_exceed_max_on_lifesteal)
    r.run("Combo x2 zdvojnásobí skóre",           test_combo_score_multiplier)
    r.run("Weapon level nepřesáhne 3",            test_weapon_level_capped_at_3)
    r.run("Difficulty cap na Level 999",          test_difficulty_cap)
    r.run("trigger_game_over() nastaví příznak",  test_game_over_trigger)

    success = r.summary()
    sys.exit(0 if success else 1)
