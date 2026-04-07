from flask import Flask, abort, jsonify, redirect, render_template, request, session

from config import SECRET_KEY
from db import get_db

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

TOWER_CATALOG = {
    "basic": {
        "name": "Zakladni vez",
        "description": "Vyvazena obrana pro kazdou situaci.",
        "cost": 0,
        "unlock_cost": 0,
        "range": 120,
        "damage": 10,
        "cooldown": 34,
        "color": "#2c7be5",
    },
    "sniper": {
        "name": "Odstrelovaci vez",
        "description": "Velky dostrel, ale pomalejsi strelba.",
        "cost": 90,
        "unlock_cost": 120,
        "range": 210,
        "damage": 26,
        "cooldown": 78,
        "color": "#7d5cff",
    },
    "splash": {
        "name": "Explozivni vez",
        "description": "Zasahne vice nepretele najednou.",
        "cost": 110,
        "unlock_cost": 160,
        "range": 132,
        "damage": 14,
        "cooldown": 48,
        "splash_radius": 58,
        "color": "#ff8c42",
    },
    "frost": {
        "name": "Mraziva vez",
        "description": "Zpomaluje nepretele a drzi linii.",
        "cost": 100,
        "unlock_cost": 150,
        "range": 145,
        "damage": 8,
        "cooldown": 42,
        "slow_factor": 0.55,
        "slow_duration": 105,
        "color": "#1fb8b2",
    },
}

DIFFICULTIES = {
    "easy": {"name": "Easy", "reward_bonus": 0.9},
    "normal": {"name": "Normal", "reward_bonus": 1.0},
    "hard": {"name": "Hard", "reward_bonus": 1.2},
}

MATCH_RESULTS = {"WIN", "LOSE"}
MAX_TOWER_LEVEL = 3

LEADERBOARD_BASE_QUERY = """
SELECT username, best_wave, total_kills, total_coins
FROM (
    SELECT
        u.username AS username,
        COALESCE(MAX(m.waves_reached), 0) AS best_wave,
        COALESCE(SUM(m.kills), 0) AS total_kills,
        COALESCE(SUM(m.reward_coins), 0) AS total_coins
    FROM users u
    LEFT JOIN matches m ON m.user_id = u.id
    GROUP BY u.id, u.username
) summary
"""


# Zakladni pomocne funkce
def logged_in():
    return "user_id" in session


def is_admin():
    if not logged_in():
        return False
    return session.get("username") == "sa"


def ensure_logged_in():
    if logged_in():
        return None
    return redirect("/login")


def ensure_admin():
    if not is_admin():
        abort(403)


def read_int(payload, key):
    try:
        return int(payload.get(key, 0))
    except (TypeError, ValueError):
        raise ValueError(f"{key} musi byt cele cislo")


def calculate_upgrade_cost(level):
    if level < 1:
        raise ValueError("level must be >= 1")
    return 45 + (level - 1) * 35


def calculate_reward(result, kills, waves, difficulty="normal"):
    if difficulty not in DIFFICULTIES:
        raise ValueError("Neplatna obtiznost.")

    reward = 20
    reward += kills * 2
    reward += waves * 10

    if result == "WIN":
        reward += 100

    reward = reward * DIFFICULTIES[difficulty]["reward_bonus"]
    reward = int(round(reward))
    return max(0, reward)


def validate_match_payload(payload):
    result = payload.get("result", "")
    waves = read_int(payload, "waves_reached")
    kills = read_int(payload, "kills")
    difficulty = payload.get("difficulty", "normal")

    if result not in MATCH_RESULTS:
        raise ValueError("result muze byt jen WIN nebo LOSE")
    if waves < 0:
        raise ValueError("waves_reached musi byt >= 0")
    if kills < 0:
        raise ValueError("kills musi byt >= 0")
    if difficulty not in DIFFICULTIES:
        raise ValueError("Neplatna obtiznost.")

    return result, waves, kills, difficulty


# Data pro profil a statistiky
def ensure_default_tower_unlock(cursor, user_id):
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


def get_unlocked_towers(cursor, user_id):
    ensure_default_tower_unlock(cursor, user_id)
    cursor.execute(
        """
        SELECT tower_name
        FROM towers_unlocked
        WHERE user_id = %s
        ORDER BY unlocked_at ASC, id ASC
        """,
        (user_id,),
    )

    tower_names = []
    for row in cursor.fetchall():
        tower_names.append(row[0])

    if tower_names:
        return tower_names
    return ["basic"]


def build_tower_payload(unlocked_names):
    payload = []
    unlocked_set = set(unlocked_names)

    for tower_id, tower_info in TOWER_CATALOG.items():
        tower_data = {}

        for key, value in tower_info.items():
            tower_data[key] = value

        tower_data["id"] = tower_id
        if tower_id in unlocked_set:
            tower_data["unlocked"] = True
            tower_data["card_class"] = "is-unlocked"
            tower_data["status_label"] = "Odemceno"
        else:
            tower_data["unlocked"] = False
            tower_data["card_class"] = "is-locked"
            tower_data["status_label"] = "Zamceno"

        payload.append(tower_data)

    return payload


def get_player_stats(cursor, user_id):
    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN result = 'LOSE' THEN 1 ELSE 0 END), 0),
            COALESCE(MAX(waves_reached), 0),
            COALESCE(SUM(kills), 0),
            COALESCE(SUM(reward_coins), 0)
        FROM matches
        WHERE user_id = %s
        """,
        (user_id,),
    )

    row = cursor.fetchone()
    if row is None:
        row = (0, 0, 0, 0, 0, 0)

    total_games = row[0]
    wins = row[1]
    losses = row[2]
    best_wave = row[3]
    total_kills = row[4]
    total_reward = row[5]

    if total_games == 0:
        win_rate = 0
    else:
        win_rate = round((wins / total_games) * 100, 1)

    return {
        "total_games": total_games,
        "wins": wins,
        "losses": losses,
        "best_wave": best_wave,
        "total_kills": total_kills,
        "total_reward": total_reward,
        "win_rate": win_rate,
    }


def get_recent_matches(cursor, user_id, limit=5):
    cursor.execute(
        """
        SELECT result, waves_reached, kills, reward_coins, difficulty, played_at
        FROM matches
        WHERE user_id = %s
        ORDER BY played_at DESC
        LIMIT %s
        """,
        (user_id, limit),
    )
    return cursor.fetchall()


def get_player_profile_data(user_id):
    mydb = get_db()
    mycursor = mydb.cursor()

    try:
        ensure_default_tower_unlock(mycursor, user_id)

        mycursor.execute(
            "SELECT username, coins, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        user_row = mycursor.fetchone()

        stats = get_player_stats(mycursor, user_id)
        last_matches = get_recent_matches(mycursor, user_id)
        unlocked_towers = get_unlocked_towers(mycursor, user_id)

        mydb.commit()
    finally:
        mycursor.close()
        mydb.close()

    return {
        "username": user_row[0],
        "coins": user_row[1],
        "created_at": user_row[2],
        "stats": stats,
        "last_matches": last_matches,
        "unlocked_towers": build_tower_payload(unlocked_towers),
    }


def get_player_stats_for_page(user_id):
    mydb = get_db()
    mycursor = mydb.cursor()

    try:
        stats = get_player_stats(mycursor, user_id)
    finally:
        mycursor.close()
        mydb.close()

    return stats


def get_history_rows(user_id):
    mydb = get_db()
    mycursor = mydb.cursor()

    try:
        mycursor.execute(
            """
            SELECT played_at, result, waves_reached, kills, reward_coins, difficulty
            FROM matches
            WHERE user_id = %s
            ORDER BY played_at DESC
            """,
            (user_id,),
        )
        rows = mycursor.fetchall()
    finally:
        mycursor.close()
        mydb.close()

    return rows


def get_leaderboard_rows(cursor, order_clause):
    query = LEADERBOARD_BASE_QUERY + f" ORDER BY {order_clause} LIMIT 10"
    cursor.execute(query)
    return cursor.fetchall()


def get_leaderboards():
    mydb = get_db()
    mycursor = mydb.cursor()

    try:
        boards = {
            "best_wave": get_leaderboard_rows(
                mycursor,
                "best_wave DESC, total_kills DESC, total_coins DESC, username ASC",
            ),
            "total_kills": get_leaderboard_rows(
                mycursor,
                "total_kills DESC, best_wave DESC, total_coins DESC, username ASC",
            ),
            "total_coins": get_leaderboard_rows(
                mycursor,
                "total_coins DESC, best_wave DESC, total_kills DESC, username ASC",
            ),
        }
    finally:
        mycursor.close()
        mydb.close()

    return boards


def get_admin_users():
    mydb = get_db()
    mycursor = mydb.cursor()

    try:
        mycursor.execute(
            """
            SELECT
                u.id,
                u.username,
                u.coins,
                COALESCE(COUNT(m.id), 0) AS total_games,
                COALESCE(MAX(m.waves_reached), 0) AS best_wave,
                COALESCE(SUM(m.kills), 0) AS total_kills
            FROM users u
            LEFT JOIN matches m ON m.user_id = u.id
            GROUP BY u.id, u.username, u.coins
            ORDER BY u.username ASC
            """
        )
        rows = mycursor.fetchall()
    finally:
        mycursor.close()
        mydb.close()

    return rows


# Zapis do databaze
def delete_user_data(cursor, user_id):
    cursor.execute("DELETE FROM purchases WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM towers_unlocked WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM matches WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))


def reset_user_data(cursor, user_id):
    cursor.execute("DELETE FROM matches WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM purchases WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM towers_unlocked WHERE user_id = %s", (user_id,))
    cursor.execute("UPDATE users SET coins = 0 WHERE id = %s", (user_id,))


def save_match_result(user_id, payload):
    result, waves, kills, difficulty = validate_match_payload(payload)
    reward = calculate_reward(result, kills, waves, difficulty)

    if reward < 0:
        raise ValueError("reward musi byt >= 0")

    mydb = get_db()
    mycursor = mydb.cursor()

    try:
        mycursor.execute(
            """
            INSERT INTO matches (user_id, result, waves_reached, kills, reward_coins, difficulty)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, result, waves, kills, reward, difficulty),
        )
        mycursor.execute(
            "UPDATE users SET coins = coins + %s WHERE id = %s",
            (reward, user_id),
        )
        mydb.commit()
        return reward
    except Exception:
        mydb.rollback()
        raise
    finally:
        mycursor.close()
        mydb.close()


# Routy
@app.route("/")
def home():
    if logged_in():
        return redirect("/profile")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if username == "" or password == "":
        return render_template("register.html", error="Vypln username a heslo.")

    mydb = get_db()
    mycursor = mydb.cursor()

    try:
        mycursor.execute(
            "INSERT INTO users (username, password, coins) VALUES (%s, %s, %s)",
            (username, password, 0),
        )
        mydb.commit()
    except Exception:
        mydb.rollback()
        return render_template("register.html", error="Uzivatel uz existuje nebo DB chyba.")
    finally:
        mycursor.close()
        mydb.close()

    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    mydb = get_db()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        row = mycursor.fetchone()
    finally:
        mycursor.close()
        mydb.close()

    if row is None:
        return render_template("login.html", error="Spatne jmeno nebo heslo.")

    user_id = row[0]
    stored_password = row[1]

    if stored_password != password:
        return render_template("login.html", error="Spatne jmeno nebo heslo.")

    session["user_id"] = user_id
    session["username"] = username
    return redirect("/profile")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/profile")
def profile():
    redirect_response = ensure_logged_in()
    if redirect_response:
        return redirect_response

    profile_data = get_player_profile_data(session["user_id"])
    return render_template(
        "profile.html",
        username=profile_data["username"],
        coins=profile_data["coins"],
        created_at=profile_data["created_at"],
        stats=profile_data["stats"],
        last_matches=profile_data["last_matches"],
        unlocked_towers=profile_data["unlocked_towers"],
        is_admin_user=is_admin(),
    )


@app.route("/stats")
def stats():
    redirect_response = ensure_logged_in()
    if redirect_response:
        return redirect_response

    player_stats = get_player_stats_for_page(session["user_id"])
    return render_template("stats.html", **player_stats, is_admin_user=is_admin())


@app.route("/history")
def history():
    redirect_response = ensure_logged_in()
    if redirect_response:
        return redirect_response

    history_rows = get_history_rows(session["user_id"])
    return render_template(
        "history.html",
        history_rows=history_rows,
        is_admin_user=is_admin(),
    )


@app.route("/leaderboard")
def leaderboard():
    redirect_response = ensure_logged_in()
    if redirect_response:
        return redirect_response

    leaderboards = get_leaderboards()
    return render_template(
        "leaderboard.html",
        leaderboards=leaderboards,
        is_admin_user=is_admin(),
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():
    redirect_response = ensure_logged_in()
    if redirect_response:
        return redirect_response

    ensure_admin()
    action_message = None

    if request.method == "POST":
        target_user_id = int(request.form.get("user_id", 0))
        action = request.form.get("action", "")

        if target_user_id == session["user_id"]:
            action_message = "Admin ucet nelze menit timto formularem."
        else:
            mydb = get_db()
            mycursor = mydb.cursor()

            try:
                if action == "delete":
                    delete_user_data(mycursor, target_user_id)
                    action_message = "Uzivatel byl smazan."
                elif action == "reset":
                    reset_user_data(mycursor, target_user_id)
                    action_message = "Statistiky uzivatele byly resetovany."

                mydb.commit()
            finally:
                mycursor.close()
                mydb.close()

    return render_template(
        "admin.html",
        users=get_admin_users(),
        action_message=action_message,
        is_admin_user=True,
    )


@app.route("/api/match", methods=["POST"])
def create_match():
    redirect_response = ensure_logged_in()
    if redirect_response:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True)
    if payload is None:
        payload = request.form.to_dict()

    try:
        reward = save_match_result(session["user_id"], payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"ok": True, "reward": reward})


if __name__ == "__main__":
    app.run(debug=True)
