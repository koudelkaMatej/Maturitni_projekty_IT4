import secrets
from flask import Flask, request, session, render_template, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_conn, init_db

app = Flask(__name__)
app.secret_key = "change-me-in-school-project"

init_db()

# ---------- helpers ----------
def current_user():
    return session.get("user")

def require_web_login():
    if not current_user():
        return jsonify({"error": "Not logged in"}), 401
    return None

def user_from_token(auth_header: str):
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None

    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.username
            FROM api_tokens t
            JOIN users u ON u.id = t.user_id
            WHERE t.token = ?
            """,
            (token,),
        ).fetchone()
    return dict(row) if row else None

# ---------- pages ----------
@app.get("/")
def index():
    return render_template("index.html", user=current_user())

@app.get("/about")
def about_page():
    return render_template("about.html", user=current_user())

@app.get("/login")
def login_page():
    return render_template("login.html", user=current_user())

@app.get("/register")
def register_page():
    return render_template("register.html", user=current_user())

@app.get("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html", user=current_user())

@app.get("/profile")
def profile_page():
    return render_template("profile.html", user=current_user())

# ---------- web auth API (pro web) ----------
@app.post("/api/register")
def api_register():
    data = request.get_json(force=True)
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if len(username) < 3:
        return jsonify({"error": "Username min 3 chars"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password min 6 chars"}), 400

    pw_hash = generate_password_hash(password)

    try:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, pw_hash),
            )
            user_id = cur.lastrowid
    except Exception:
        return jsonify({"error": "Username already exists"}), 409

    session["user"] = {"id": user_id, "username": username}
    return jsonify({"ok": True, "user": session["user"]})

@app.post("/api/login")
def api_login():
    data = request.get_json(force=True)
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user"] = {"id": row["id"], "username": row["username"]}
    return jsonify({"ok": True, "user": session["user"]})

@app.post("/api/logout")
def api_logout():
    session.pop("user", None)
    return jsonify({"ok": True})

@app.get("/api/me")
def api_me():
    return jsonify({"user": current_user()})

# ---------- desktop app API ----------
@app.post("/api/app-login")
def api_app_login():
    """
    Desktop app login:
    - když účet neexistuje → 404 "No such user"
    - když heslo špatně → 401
    - když ok → vrátí token
    """
    data = request.get_json(force=True)
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if not row:
        return jsonify({"error": "No such user"}), 404

    if not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = secrets.token_urlsafe(32)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO api_tokens (token, user_id) VALUES (?, ?)",
            (token, row["id"]),
        )

    return jsonify({"ok": True, "token": token, "username": row["username"]})

@app.post("/api/score")
def api_score():
    user = user_from_token(request.headers.get("Authorization", ""))
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    score = int(data.get("score", 0))
    apples = int(data.get("apples", 0))
    duration_ms = int(data.get("duration_ms", 0))

    if score < 0:
        return jsonify({"error": "Bad score"}), 400

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO scores (user_id, score, apples, duration_ms) VALUES (?, ?, ?, ?)",
            (user["id"], score, apples, duration_ms),
        )
    return jsonify({"ok": True})

@app.get("/api/leaderboard")
def api_leaderboard():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT s.score, s.apples, s.duration_ms, s.played_at, u.username
            FROM scores s
            JOIN users u ON u.id = s.user_id
            ORDER BY s.score DESC, s.played_at DESC
            LIMIT 20
            """
        ).fetchall()
    return jsonify({"rows": [dict(r) for r in rows]})

@app.get("/api/my-stats")
def api_my_stats():
    guard = require_web_login()
    if guard:
        return guard

    u = current_user()
    with get_conn() as conn:
        best = conn.execute(
            "SELECT COALESCE(MAX(score), 0) AS best FROM scores WHERE user_id = ?",
            (u["id"],),
        ).fetchone()
        games = conn.execute(
            "SELECT COUNT(*) AS games FROM scores WHERE user_id = ?",
            (u["id"],),
        ).fetchone()
        avg = conn.execute(
            "SELECT COALESCE(ROUND(AVG(score), 1), 0) AS avg FROM scores WHERE user_id = ?",
            (u["id"],),
        ).fetchone()
        last10 = conn.execute(
            """
            SELECT score, apples, duration_ms, played_at
            FROM scores
            WHERE user_id = ?
            ORDER BY played_at DESC
            LIMIT 10
            """,
            (u["id"],),
        ).fetchall()

    return jsonify(
        {
            "user": u,
            "best_score": best["best"],
            "games": games["games"],
            "avg_score": avg["avg"],
            "last10": [dict(r) for r in last10],
        }
    )

if __name__ == "__main__":
    app.run(debug=True)