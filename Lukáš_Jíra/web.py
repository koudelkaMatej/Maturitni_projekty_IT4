from flask import Flask, request, session, send_from_directory
import os
import databaze

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "maturitni-projekt-secret")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "Obrazky")


@app.route("/Obrazky/<path:filename>")
def obrazky(filename):
    return send_from_directory(IMAGES_DIR, filename)


def _render_scores_rows():
    data = databaze.ziskej_data()
    if not data:
        return "<tr><td colspan='4'>Zatim nejsou ulozene zadne vysledky.</td></tr>"

    rows = []
    for i, hrac in enumerate(data, start=1):
        rows.append(
            f"<tr><td>{i}.</td><td>{hrac[0]}</td><td>{hrac[1]}</td><td>{hrac[2]}</td></tr>"
        )
    return "".join(rows)


def _render_users_rows():
    users = databaze.ziskej_uzivatele()
    if not users:
        return "<tr><td colspan='2'>Nejsou dostupne zadne ucty.</td></tr>"

    rows = []
    for jmeno in users:
        actions = (
            "<form method='POST' class='inline-form'>"
            "<input type='hidden' name='action' value='delete_user'>"
            f"<input type='hidden' name='target_user' value='{jmeno}'>"
            "<button type='submit' class='btn danger'>Smazat ucet</button>"
            "</form>"
        )
        rows.append(f"<tr><td>{jmeno}</td><td>{actions}</td></tr>")
    return "".join(rows)


def _base_styles():
    return """
    <style>
        :root {
            --bg-1: #fdf6ea;
            --bg-2: #e8f4ff;
            --ink: #1e293b;
            --card: #ffffff;
            --line: #d7dee9;
            --brand: #0f766e;
            --brand-2: #0369a1;
            --warn: #b45309;
            --danger: #b91c1c;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            color: var(--ink);
            background:
                radial-gradient(circle at 15% 20%, #fff7d8 0%, transparent 40%),
                radial-gradient(circle at 85% 0%, #d7ecff 0%, transparent 35%),
                linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 50%, #ffffff 100%);
        }

        .topbar {
            position: sticky;
            top: 0;
            z-index: 20;
            border-bottom: 1px solid #12405f;
            background: linear-gradient(90deg, #0c4a6e, #0f766e);
        }

        .topbar nav {
            max-width: 1150px;
            margin: 0 auto;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            padding: 12px 14px;
        }

        .topbar a {
            color: #ffffff;
            text-decoration: none;
            font-weight: 700;
            font-size: 14px;
            padding: 8px 10px;
            border-radius: 9px;
            transition: background .2s;
        }

        .topbar a:hover { background: rgba(255, 255, 255, 0.18); }

        .wrap {
            max-width: 1150px;
            margin: 20px auto 40px;
            padding: 0 14px;
        }

        .hero {
            background: linear-gradient(135deg, #ffffff 0%, #f2fbff 55%, #fff5dc 100%);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
            position: relative;
        }

        h1, h2, h3 { margin-top: 0; }

        .user-chip {
            position: absolute;
            top: 16px;
            right: 16px;
            background: #e8fff4;
            border: 1px solid #85d1a9;
            border-radius: 999px;
            padding: 7px 12px;
            font-size: 13px;
            font-weight: 700;
        }

        .grid {
            margin-top: 16px;
            display: grid;
            gap: 16px;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }

        .card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0 6px 20px rgba(2, 6, 23, 0.05);
        }

        .msg {
            min-height: 22px;
            font-weight: 700;
            color: var(--warn);
            margin-bottom: 10px;
        }

        .form input {
            width: 100%;
            border: 1px solid #b9c4d6;
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 8px;
            font-size: 14px;
        }

        .btn {
            border: none;
            border-radius: 8px;
            padding: 10px 14px;
            font-weight: 700;
            color: white;
            background: var(--brand-2);
            cursor: pointer;
        }

        .btn:hover { filter: brightness(0.92); }
        .btn.alt { background: var(--brand); }
        .btn.warn { background: var(--warn); }
        .btn.danger { background: var(--danger); }

        .inline-form { display: inline; }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        th, td {
            text-align: left;
            border-bottom: 1px solid var(--line);
            padding: 10px 8px;
            vertical-align: top;
        }

        th { background: #f7fbff; }

        ul { margin: 0; padding-left: 18px; }
        li { margin-bottom: 6px; }

        .diagram-placeholder {
            border: 2px dashed #9aa9bf;
            border-radius: 12px;
            min-height: 220px;
            display: grid;
            place-items: center;
            background: repeating-linear-gradient(
                45deg,
                #f8fafc,
                #f8fafc 10px,
                #eef2f7 10px,
                #eef2f7 20px
            );
            color: #334155;
            font-weight: 700;
            text-align: center;
            padding: 14px;
        }

        .diagram-image {
            width: 100%;
            max-width: 1000px;
            height: auto;
            display: block;
            margin: 0 auto;
            border-radius: 10px;
            border: 1px solid #c8d4e5;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
            background: #fff;
        }

        .diagram-wrap {
            overflow-x: auto;
            padding: 8px 0;
        }

        .diagram-svg {
            min-width: 720px;
            width: 100%;
            height: auto;
            display: block;
            background: #ffffff;
            border: 1px solid #c8d4e5;
            border-radius: 12px;
        }

        .diagram-note {
            margin-top: 12px;
            color: #475569;
            font-size: 14px;
            line-height: 1.5;
        }

        @media (max-width: 640px) {
            .topbar a { font-size: 13px; }
            .btn { width: 100%; }
            .user-chip {
                position: static;
                display: inline-block;
                margin-top: 10px;
            }
        }
    </style>
    """


@app.route("/", methods=["GET", "POST"])
def hlavni_stranka():
    user_msg = ""

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "register":
            jmeno = request.form.get("jmeno", "").strip()
            heslo = request.form.get("heslo", "").strip()
            if databaze.registrace(jmeno, heslo):
                session["player"] = jmeno
                user_msg = f"Registrace uspesna. Jsi prihlaseny jako {jmeno}."
            else:
                user_msg = "Registrace selhala. Jmeno uz existuje nebo je neplatne."

        elif action == "login":
            jmeno = request.form.get("jmeno", "").strip()
            heslo = request.form.get("heslo", "").strip()
            if databaze.prihlaseni(jmeno, heslo):
                session["player"] = jmeno
                user_msg = f"Prihlaseni uspesne. Vitej, {jmeno}."
            else:
                user_msg = "Spatne jmeno nebo heslo."

        elif action == "logout":
            session.pop("player", None)
            user_msg = "Byl jsi odhlasen."

    logged_player = session.get("player")
    user_chip = (
        f"<div class='user-chip'>Prihlasen: {logged_player}</div>" if logged_player else ""
    )
    scores_rows = _render_scores_rows()

    if logged_player:
        auth_section = f"""
        <section class="card" id="auth" style="margin-top:16px;">
            <h2>Ucet</h2>
            <p class="msg">{user_msg}</p>
            <p>Jsi prihlaseny. Formulare jsou schovane.</p>
            <form method="POST">
                <input type="hidden" name="action" value="logout">
                <button type="submit" class="btn warn">Odhlasit</button>
            </form>
        </section>
        """
    else:
        auth_section = f"""
        <section class="grid" id="auth">
            <article class="card">
                <h2>Registrace</h2>
                <p class="msg">{user_msg}</p>
                <form method="POST" class="form">
                    <input type="hidden" name="action" value="register">
                    <input type="text" name="jmeno" placeholder="Uzivatelske jmeno" required>
                    <input type="password" name="heslo" placeholder="Heslo" required>
                    <button type="submit" class="btn alt">Vytvorit ucet</button>
                </form>
            </article>

            <article class="card">
                <h2>Prihlaseni hrace</h2>
                <p>Po prihlaseni se stejnymi udaji se prihlasis i v pygame menu.</p>
                <form method="POST" class="form">
                    <input type="hidden" name="action" value="login">
                    <input type="text" name="jmeno" placeholder="Uzivatelske jmeno" required>
                    <input type="password" name="heslo" placeholder="Heslo" required>
                    <button type="submit" class="btn">Prihlasit</button>
                </form>
            </article>
        </section>
        """

    return f"""
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flappy Bird Web</title>
    {_base_styles()}
</head>
<body>
    <header class="topbar">
        <nav>
            <a href="#home">Domu</a>
            <a href="#auth">Ucty</a>
            <a href="#ovladani">Ovladani</a>
            <a href="#ohre">O hre</a>
            <a href="#diagramy">ER diagram</a>
            <a href="#vysledky">Vysledky</a>
        </nav>
    </header>

    <main class="wrap" id="home">
        <section class="hero">
            {user_chip}
            <h1>Flappy Bird - web projektu</h1>
            <p>Tahle stranka slouzi pro registraci, prihlaseni, orientaci ve hre a zobrazeni vysledku.</p>
        </section>

        {auth_section}

        <section class="grid">
            <article class="card" id="ovladani">
                <h2>Jak se hra ovlada</h2>
                <ul>
                    <li><b>SPACE</b>: ptacek vyskoci nahoru.</li>
                    <li>Cilem je proletet mezi trubkami bez kolize.</li>
                    <li>Po konci hry se vratis do menu a muzes hrat znovu.</li>
                </ul>
            </article>

            <article class="card" id="ohre">
                <h2>Neco o hre</h2>
                <ul>
                    <li>Skore se pripocita za kazdou uspesne preletenou dvojici trubek.</li>
                    <li>Vysledky se ukladaji do SQLite databaze `skore.db`.</li>
                    <li>Bez prihlaseni se vysledky neukladaji ke konkretnimu uzivateli.</li>
                </ul>
            </article>
        </section>

        <section class="card" id="diagramy" style="margin-top:16px;">
            <h2>ER diagram databaze</h2>
            <div class="diagram-wrap">
                <svg viewBox="0 0 980 320" class="diagram-svg" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ER diagram databaze">
                    <defs>
                        <marker id="arrow-end" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
                            <path d="M0,0 L12,6 L0,12 z" fill="#0f766e"/>
                        </marker>
                    </defs>

                    <rect x="60" y="40" width="320" height="200" rx="16" fill="#f8fbff" stroke="#0c4a6e" stroke-width="2"/>
                    <rect x="60" y="40" width="320" height="44" rx="16" fill="#0c4a6e"/>
                    <text x="220" y="68" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff">UZIVATELE</text>
                    <text x="86" y="112" font-size="19" font-weight="700" fill="#0f172a">PK id : INTEGER</text>
                    <text x="86" y="145" font-size="19" fill="#0f172a">jmeno : TEXT (UNIQUE)</text>
                    <text x="86" y="178" font-size="19" fill="#0f172a">heslo_hash : TEXT</text>
                    <text x="86" y="211" font-size="19" fill="#475569">heslo : TEXT (stary sloupec)</text>

                    <rect x="600" y="40" width="320" height="200" rx="16" fill="#fffdf7" stroke="#b45309" stroke-width="2"/>
                    <rect x="600" y="40" width="320" height="44" rx="16" fill="#b45309"/>
                    <text x="760" y="68" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff">VYSLEDKY</text>
                    <text x="626" y="112" font-size="19" font-weight="700" fill="#0f172a">PK id : INTEGER</text>
                    <text x="626" y="145" font-size="19" fill="#0f172a">jmeno : TEXT</text>
                    <text x="626" y="178" font-size="19" fill="#0f172a">body : INTEGER</text>
                    <text x="626" y="211" font-size="19" fill="#0f172a">datum : TEXT</text>

                    <line x1="380" y1="140" x2="600" y2="140" stroke="#0f766e" stroke-width="4" marker-end="url(#arrow-end)"/>
                    <text x="490" y="126" text-anchor="middle" font-size="18" font-weight="700" fill="#0f766e">1 : N</text>
                    <text x="490" y="164" text-anchor="middle" font-size="16" fill="#334155">vazba pres jmeno</text>
                </svg>
            </div>
            <p class="diagram-note">
                Diagram odpovida databazi <b>skore.db</b>. Vazba mezi tabulkami je v aplikaci resena
                logicky pres pole <b>jmeno</b>, ale v SQLite momentalne neni nastavena jako cizi klic.
            </p>
        </section>

        <section class="card" id="vysledky" style="margin-top:16px;">
            <h2>TOP vysledky</h2>
            <table>
                <tr><th>Poradi</th><th>Jmeno</th><th>Skore</th><th>Datum</th></tr>
                {scores_rows}
            </table>
        </section>
    </main>
</body>
</html>
"""


@app.route("/admin", methods=["GET", "POST"])
def admin_stranka():
    admin_msg = ""

    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "admin_login":
            jmeno = request.form.get("admin_name", "").strip()
            heslo = request.form.get("admin_pass", "").strip()
            if jmeno == ADMIN_USERNAME and heslo == ADMIN_PASSWORD:
                session["admin"] = True
                admin_msg = "Admin prihlaseni uspesne."
            else:
                admin_msg = "Spatne admin jmeno nebo heslo."
        elif action == "admin_logout":
            session.pop("admin", None)
            admin_msg = "Admin byl odhlasen."
        elif action == "delete_user":
            if not session.get("admin"):
                admin_msg = "Pro tuto akci musis byt prihlaseny jako admin."
            else:
                target_user = request.form.get("target_user", "").strip()
                if target_user == ADMIN_USERNAME:
                    admin_msg = "Admin ucet nelze smazat timto formularem."
                elif databaze.smazat_ucet(target_user):
                    if session.get("player") == target_user:
                        session.pop("player", None)
                    admin_msg = f"Ucet {target_user} byl smazan."
                else:
                    admin_msg = "Ucet se nepodarilo smazat (neexistuje?)."

    if not session.get("admin"):
        return f"""
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin</title>
    {_base_styles()}
</head>
<body>
    <main class="wrap" style="max-width: 520px;">
        <section class="card" style="margin-top:28px;">
            <h2>Admin prihlaseni</h2>
            <p class="msg">{admin_msg}</p>
            <form method="POST" class="form">
                <input type="hidden" name="action" value="admin_login">
                <input type="text" name="admin_name" placeholder="Admin jmeno" required>
                <input type="password" name="admin_pass" placeholder="Admin heslo" required>
                <button type="submit" class="btn">Prihlasit admina</button>
            </form>
        </section>
    </main>
</body>
</html>
"""

    users_rows = _render_users_rows()
    return f"""
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
    {_base_styles()}
</head>
<body>
    <main class="wrap">
        <section class="card" style="margin-top:20px;">
            <h2>Admin panel</h2>
            <p class="msg">{admin_msg}</p>
            <form method="POST" style="margin-bottom:12px;">
                <input type="hidden" name="action" value="admin_logout">
                <button type="submit" class="btn warn">Odhlasit admina</button>
            </form>
            <table>
                <tr><th>Uzivatel</th><th>Akce</th></tr>
                {users_rows}
            </table>
        </section>
    </main>
</body>
</html>
"""


if __name__ == "__main__":
    databaze.vytvorit_tabulku()
    print("Zapinam webovy server. Nech toto okno otevrene.")
    print("Hracsky web: http://127.0.0.1:5000")
    print("Admin panel: http://127.0.0.1:5000/admin")
    app.run(port=5000, use_reloader=False)
