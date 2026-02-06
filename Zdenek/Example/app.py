# app.py
from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from config import SECRET_KEY
from db import get_db

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


# ---------------------------
# Pomocné funkce (testovatelné)
# ---------------------------

def calculate_reward(result: str, kills: int, waves: int) -> int:
    base = 20 + (kills * 2) + (waves * 10)
    if result == "WIN":
        base += 100
    return base


def validate_match_payload(data: dict):

    if not isinstance(data, dict):
        raise ValueError("Data must be object")

    result = data.get("result")
    waves = data.get("waves_reached")
    kills = data.get("kills")

    if result not in ["WIN", "LOSE"]:
        raise ValueError("Invalid result")
    if not isinstance(waves, int) or not isinstance(kills, int):
        raise ValueError("Invalid waves/kills")
    if waves < 0 or kills < 0:
        raise ValueError("Negative values")

    return result, waves, kills


def logged_in():
    return "user_id" in session


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
        return render_template("register.html", error="Vyplň username a heslo.")

    mydb = get_db()
    mycursor = mydb.cursor()

    try:
        hashed = generate_password_hash(password)
        mycursor.execute(
            "INSERT INTO users (username, password, coins) VALUES (%s, %s, %s)",
            (username, hashed, 0)
        )
        mydb.commit()
    except Exception:
        return render_template("register.html", error="Uživatel už existuje nebo DB chyba.")
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

    mycursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    row = mycursor.fetchone()

    mycursor.close()
    mydb.close()

    if row is None:
        return render_template("login.html", error="Špatné jméno nebo heslo.")

    user_id, stored_hash = row
    if not check_password_hash(stored_hash, password):
        return render_template("login.html", error="Špatné jméno nebo heslo.")

    session["user_id"] = user_id
    session["username"] = username
    return redirect("/profile")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/profile")
def profile():
    if not logged_in():
        return redirect("/login")

    user_id = session["user_id"]

    mydb = get_db()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT coins, created_at FROM users WHERE id = %s", (user_id,))
    user_row = mycursor.fetchone()

    mycursor.execute("""
        SELECT result, waves_reached, kills, reward_coins, played_at
        FROM matches
        WHERE user_id = %s
        ORDER BY played_at DESC
        LIMIT 5
    """, (user_id,))
    last_matches = mycursor.fetchall()

    mycursor.close()
    mydb.close()

    coins, created_at = user_row
    return render_template(
        "profile.html",
        username=session["username"],
        coins=coins,
        created_at=created_at,
        last_matches=last_matches
    )


@app.route("/stats")
def stats():
    if not logged_in():
        return redirect("/login")

    user_id = session["user_id"]

    mydb = get_db()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT COUNT(*) FROM matches WHERE user_id = %s", (user_id,))
    total_games = mycursor.fetchone()[0]

    mycursor.execute("SELECT COUNT(*) FROM matches WHERE user_id = %s AND result='WIN'", (user_id,))
    wins = mycursor.fetchone()[0]

    mycursor.execute("SELECT COALESCE(MAX(waves_reached), 0) FROM matches WHERE user_id = %s", (user_id,))
    best_wave = mycursor.fetchone()[0]

    mycursor.execute("SELECT COALESCE(SUM(kills), 0) FROM matches WHERE user_id = %s", (user_id,))
    total_kills = mycursor.fetchone()[0]

    mycursor.close()
    mydb.close()

    return render_template(
        "stats.html",
        total_games=total_games,
        wins=wins,
        best_wave=best_wave,
        total_kills=total_kills
    )


@app.route("/game")
def game():
    if not logged_in():
        return redirect("/login")
    return render_template("game.html")



@app.route("/api/match_end", methods=["POST"])
def match_end():
    if not logged_in():
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}

    try:
        result, waves, kills = validate_match_payload(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    reward = calculate_reward(result, kills, waves)
    user_id = session["user_id"]

    mydb = get_db()
    mycursor = mydb.cursor()

    mycursor.execute("""
        INSERT INTO matches (user_id, result, waves_reached, kills, reward_coins)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, result, waves, kills, reward))

    mycursor.execute("UPDATE users SET coins = coins + %s WHERE id = %s", (reward, user_id))

    mydb.commit()

    mycursor.execute("SELECT coins FROM users WHERE id = %s", (user_id,))
    total_coins = mycursor.fetchone()[0]

    mycursor.close()
    mydb.close()

    return jsonify({
        "reward_coins": reward,
        "total_coins": total_coins
    })


if __name__ == "__main__":
    app.run(debug=True)
