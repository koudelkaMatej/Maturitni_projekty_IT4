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


# ──────────────────────────────────────────────
# POMOCNÉ RENDEROVACÍ FUNKCE
# ──────────────────────────────────────────────

def _render_scores_rows():
    data = databaze.ziskej_data()
    if not data:
        return "<tr><td colspan='4'>Zatím nejsou uložené žádné výsledky.</td></tr>"
    rows = []
    for i, hrac in enumerate(data, start=1):
        rows.append(
            f"<tr><td>{i}.</td><td>{hrac[0]}</td><td>{hrac[1]}</td><td>{hrac[2]}</td></tr>"
        )
    return "".join(rows)


def _render_users_rows():
    users = databaze.ziskej_uzivatele()
    if not users:
        return "<tr><td colspan='2'>Nejsou dostupné žádné účty.</td></tr>"
    rows = []
    for jmeno in users:
        actions = (
            "<form method='POST' class='inline-form'>"
            "<input type='hidden' name='action' value='delete_user'>"
            f"<input type='hidden' name='target_user' value='{jmeno}'>"
            "<button type='submit' class='btn danger'>Smazat účet</button>"
            "</form>"
        )
        rows.append(f"<tr><td>{jmeno}</td><td>{actions}</td></tr>")
    return "".join(rows)


# ──────────────────────────────────────────────
# STYLY (společné pro všechny stránky)
# ──────────────────────────────────────────────

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
            position: sticky; top: 0; z-index: 20;
            border-bottom: 1px solid #12405f;
            background: linear-gradient(90deg, #0c4a6e, #0f766e);
        }
        .topbar nav {
            max-width: 1150px; margin: 0 auto;
            display: flex; gap: 8px; flex-wrap: wrap; padding: 12px 14px;
        }
        .topbar a {
            color: #fff; text-decoration: none; font-weight: 700;
            font-size: 14px; padding: 8px 10px; border-radius: 9px; transition: background .2s;
        }
        .topbar a:hover { background: rgba(255,255,255,0.18); }

        .wrap { max-width: 1150px; margin: 20px auto 40px; padding: 0 14px; }

        .hero {
            background: linear-gradient(135deg, #fff 0%, #f2fbff 55%, #fff5dc 100%);
            border: 1px solid var(--line); border-radius: 16px; padding: 22px;
            box-shadow: 0 10px 30px rgba(15,23,42,0.08); position: relative;
        }

        h1, h2, h3 { margin-top: 0; }

        .user-chip {
            position: absolute; top: 16px; right: 16px;
            background: #e8fff4; border: 1px solid #85d1a9;
            border-radius: 999px; padding: 7px 12px;
            font-size: 13px; font-weight: 700;
        }

        .grid { margin-top: 16px; display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }

        .card {
            background: var(--card); border: 1px solid var(--line);
            border-radius: 14px; padding: 16px;
            box-shadow: 0 6px 20px rgba(2,6,23,0.05);
        }

        .msg { min-height: 22px; font-weight: 700; color: var(--warn); margin-bottom: 10px; }

        .form input {
            width: 100%; border: 1px solid #b9c4d6; border-radius: 8px;
            padding: 10px 12px; margin-bottom: 8px; font-size: 14px;
        }

        .btn {
            border: none; border-radius: 8px; padding: 10px 14px;
            font-weight: 700; color: white; background: var(--brand-2); cursor: pointer;
        }
        .btn:hover { filter: brightness(0.92); }
        .btn.alt    { background: var(--brand); }
        .btn.warn   { background: var(--warn); }
        .btn.danger { background: var(--danger); }

        .inline-form { display: inline; }

        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { text-align: left; border-bottom: 1px solid var(--line); padding: 10px 8px; vertical-align: top; }
        th { background: #f7fbff; }

        ul, ol { margin: 0 0 8px 0; padding-left: 20px; }
        li { margin-bottom: 6px; line-height: 1.5; }

        /* ── NÁVOD SPECIFICKÉ STYLY ── */
        .navod-krok {
            display: flex; gap: 14px; align-items: flex-start;
            padding: 14px 0; border-bottom: 1px solid var(--line);
        }
        .navod-krok:last-child { border-bottom: none; }
        .navod-cislo {
            min-width: 38px; height: 38px; border-radius: 50%;
            background: var(--brand-2); color: #fff; font-weight: 700;
            font-size: 18px; display: grid; place-items: center; flex-shrink: 0;
        }
        .navod-text h3 { margin: 0 0 4px 0; font-size: 16px; }
        .navod-text p  { margin: 0; font-size: 14px; line-height: 1.6; color: #334155; }

        .soubor-tabulka td:first-child {
            font-family: monospace; font-weight: 700;
            color: var(--brand); white-space: nowrap;
        }

        .badge {
            display: inline-block; font-size: 11px; font-weight: 700;
            padding: 2px 8px; border-radius: 999px; margin-right: 4px;
        }
        .badge-python { background: #dbeafe; color: #1e40af; }
        .badge-flask  { background: #dcfce7; color: #166534; }
        .badge-sqlite { background: #fef9c3; color: #854d0e; }
        .badge-pygame { background: #fce7f3; color: #9d174d; }

        .tip-box {
            background: #f0fdf4; border-left: 4px solid #16a34a;
            border-radius: 0 8px 8px 0; padding: 10px 14px;
            margin-top: 10px; font-size: 14px; color: #166534;
        }
        .warn-box {
            background: #fffbeb; border-left: 4px solid #d97706;
            border-radius: 0 8px 8px 0; padding: 10px 14px;
            margin-top: 10px; font-size: 14px; color: #92400e;
        }

        /* ── ER DIAGRAM ── */
        .diagram-wrap { overflow-x: auto; padding: 8px 0; }
        .diagram-svg {
            min-width: 720px; width: 100%; height: auto; display: block;
            background: #fff; border: 1px solid #c8d4e5; border-radius: 12px;
        }
        .diagram-note { margin-top: 12px; color: #475569; font-size: 14px; line-height: 1.5; }

        @media (max-width: 640px) {
            .topbar a { font-size: 13px; }
            .btn { width: 100%; }
            .user-chip { position: static; display: inline-block; margin-top: 10px; }
        }
    </style>
    """


# ──────────────────────────────────────────────
# NÁVOD (velká sekce vložená do hlavní stránky)
# ──────────────────────────────────────────────

def _render_navod():
    return """
    <section class="card" id="navod" style="margin-top:16px;">
        <h2>📖 Kompletní návod k projektu</h2>

        <!-- 1. Co je projekt -->
        <h3 style="color:#0c4a6e; margin-top:12px;">1. O projektu</h3>
        <p style="font-size:14px; line-height:1.7;">
            Tento projekt je maturitní práce – klon klasické hry <b>Flappy Bird</b>.
            Hra je napsaná v Pythonu pomocí knihovny <b>Pygame</b> a webový server je postaven
            na <b>Flask</b>. Výsledky a účty hráčů se ukládají do lehké databáze <b>SQLite</b>.
            Tato webová stránka slouží k registraci, přihlášení a zobrazení žebříčku.
        </p>

        <!-- 2. Soubory projektu -->
        <h3 style="color:#0c4a6e; margin-top:18px;">2. Struktura projektu – přehled souborů</h3>
        <table>
            <tr><th>Soubor</th><th>Co dělá</th><th>Technologie</th></tr>
            <tr>
                <td>menu.py</td>
                <td>Hlavní vstupní bod. Spouští Pygame okno s menu, přihlášením a tlačítky.</td>
                <td><span class="badge badge-pygame">Pygame</span></td>
            </tr>
            <tr>
                <td>hra.py</td>
                <td>Samotná herní logika – pták, trubky, kolize, skóre, zvuky.</td>
                <td><span class="badge badge-pygame">Pygame</span></td>
            </tr>
            <tr>
                <td>databaze.py</td>
                <td>Veškerá práce s databází – registrace, přihlášení, ukládání skóre.</td>
                <td><span class="badge badge-sqlite">SQLite</span></td>
            </tr>
            <tr>
                <td>web.py</td>
                <td>Webový server – tato stránka. Registrace, přihlášení přes prohlížeč, žebříček.</td>
                <td><span class="badge badge-flask">Flask</span></td>
            </tr>
            <tr>
                <td>skore.db</td>
                <td>Databázový soubor. Vytvoří se automaticky při prvním spuštění.</td>
                <td><span class="badge badge-sqlite">SQLite</span></td>
            </tr>
            <tr>
                <td>Obrazky/</td>
                <td>Složka s obrázky ptáčka, pozadí, trubek a zvukem flap.mp3.</td>
                <td>–</td>
            </tr>
        </table>

        <!-- 3. Jak spustit -->
        <h3 style="color:#0c4a6e; margin-top:18px;">3. Jak projekt spustit</h3>
        <p style="font-size:14px;">
            Projekt vyžaduje nainstalovaný <b>Python 3</b> a knihovny
            <code>pygame</code> a <code>flask</code>.<br>
            Nainstalovat je lze příkazem:
        </p>
        <pre style="background:#1e293b; color:#e2e8f0; padding:12px 16px; border-radius:10px; font-size:13px; overflow-x:auto;">pip install pygame flask</pre>

        <div style="margin-top:12px;">
            <div class="navod-krok">
                <div class="navod-cislo">1</div>
                <div class="navod-text">
                    <h3>Spusť webový server</h3>
                    <p>Otevři terminál ve složce projektu a zadej: <code>python web.py</code><br>
                    Terminál nech otevřený – server musí běžet celou dobu.</p>
                </div>
            </div>
            <div class="navod-krok">
                <div class="navod-cislo">2</div>
                <div class="navod-text">
                    <h3>Zaregistruj se přes web</h3>
                    <p>V prohlížeči přejdi na <b>http://127.0.0.1:5000</b>, vyplň jméno a heslo
                    v sekci <i>Registrace</i> a klikni na <i>Vytvořit účet</i>.<br>
                    Zapamatuj si přesně jméno i heslo – budou potřeba v herním menu.</p>
                </div>
            </div>
            <div class="navod-krok">
                <div class="navod-cislo">3</div>
                <div class="navod-text">
                    <h3>Spusť herní menu</h3>
                    <p>V novém terminálu zadej: <code>python menu.py</code><br>
                    Otevře se Pygame okno s hlavním menu hry.</p>
                </div>
            </div>
            <div class="navod-krok">
                <div class="navod-cislo">4</div>
                <div class="navod-text">
                    <h3>Přihlas se v herním menu</h3>
                    <p>Klikni na <b>PŘIHLÁSIT SE</b>, zadej stejné jméno a heslo jako při registraci.
                    Po úspěšném přihlášení se odemkne tlačítko <b>HRÁT</b>.</p>
                </div>
            </div>
            <div class="navod-krok">
                <div class="navod-cislo">5</div>
                <div class="navod-text">
                    <h3>Hraj a sleduj výsledky</h3>
                    <p>Po každé hře se tvoje skóre automaticky uloží do databáze.
                    Žebříček s nejlepšími výsledky vidíš níže na této stránce nebo kliknutím na
                    <b>WEB A VÝSLEDKY</b> v herním menu.</p>
                </div>
            </div>
        </div>

        <div class="tip-box">
            💡 <b>Tip:</b> Webový server (<code>python web.py</code>) a herní menu (<code>python menu.py</code>)
            musí běžet ve <b>dvou oddělených terminálech</b> najednou.
        </div>

        <!-- 4. Jak se zaregistrovat / přihlásit -->
        <h3 style="color:#0c4a6e; margin-top:18px;">4. Registrace a přihlášení – podrobně</h3>
        <div class="grid" style="margin-top:8px;">
            <div>
                <h4 style="margin:0 0 8px 0;">🌐 Přes web (doporučeno)</h4>
                <ol style="font-size:14px;">
                    <li>Jdi na <b>http://127.0.0.1:5000</b></li>
                    <li>Vyplň libovolné uživatelské jméno (bez mezer)</li>
                    <li>Vyplň heslo (min. 1 znak)</li>
                    <li>Klikni <b>Vytvořit účet</b></li>
                    <li>Pokud jméno ještě neexistuje, registrace proběhne a budeš přihlášen/a</li>
                    <li>Příště se přihlas přes sekci <i>Přihlášení hráče</i></li>
                </ol>
            </div>
            <div>
                <h4 style="margin:0 0 8px 0;">🎮 V herním menu</h4>
                <ol style="font-size:14px;">
                    <li>Klikni na <b>PŘIHLÁSIT SE</b></li>
                    <li>Do políčka napiš jméno a stiskni <kbd>Enter</kbd></li>
                    <li>Do políčka napiš heslo a stiskni <kbd>Enter</kbd></li>
                    <li>Pokud jsou údaje správné, přihlásíš se a odemkne se hra</li>
                    <li>Registrace v menu <b>není možná</b> – musí proběhnout přes web</li>
                </ol>
                <div class="warn-box">
                    ⚠️ Heslo se zadává do Pygame okna – znaky nejsou skryté hvězdičkami.
                </div>
            </div>
        </div>

        <!-- 5. Jak hrát -->
        <h3 style="color:#0c4a6e; margin-top:18px;">5. Jak se hraje</h3>
        <div class="grid" style="margin-top:8px;">
            <div>
                <h4 style="margin:0 0 8px 0;">🕹️ Ovládání</h4>
                <ul style="font-size:14px;">
                    <li><kbd>SPACE</kbd> – pták vyskočí nahoru (odrazí se od vzduchu)</li>
                    <li>Bez stisku pták padá dolů kvůli gravitaci</li>
                    <li>Po smrti stiskni <kbd>SPACE</kbd> pro návrat do menu</li>
                </ul>
            </div>
            <div>
                <h4 style="margin:0 0 8px 0;">🏆 Skórování a pravidla</h4>
                <ul style="font-size:14px;">
                    <li>+1 bod za každou úspěšně přeleténou dvojici trubek</li>
                    <li>Kolize s trubkou nebo s krajem obrazovky = konec hry</li>
                    <li>Mezera mezi trubkami je <b>náhodná</b> (140–240 px)</li>
                    <li>Čas mezi trubkami je <b>náhodný</b> (1,2–2,2 sekundy)</li>
                    <li>Do databáze se uloží <b>nejlepší skóre</b> z celé tvé herní history</li>
                </ul>
            </div>
        </div>
        <div class="tip-box">
            💡 <b>Tip pro vyšší skóre:</b> Neklikej moc rychle za sebou – pták pak nekontrolovaně stoupá.
            Snaž se držet ptáčka uprostřed mezery krátkými a přesnými stisky.
        </div>

        <!-- 6. Jak funguje databáze -->
        <h3 style="color:#0c4a6e; margin-top:18px;">6. Jak funguje databáze</h3>
        <p style="font-size:14px; line-height:1.7;">
            Databáze <b>skore.db</b> je soubor SQLite ve složce projektu. Obsahuje dvě tabulky:
        </p>
        <table style="margin-top:8px;">
            <tr><th>Tabulka</th><th>Sloupce</th><th>Účel</th></tr>
            <tr>
                <td><b>uzivatele</b></td>
                <td>id, jmeno, heslo_hash</td>
                <td>Ukládá přihlašovací údaje. Heslo se ukládá jako SHA-256 hash – nikdy jako prostý text.</td>
            </tr>
            <tr>
                <td><b>vysledky</b></td>
                <td>id, jmeno, body, datum</td>
                <td>Každá odehraná hra se zapíše jako nový řádek. V žebříčku se zobrazuje jen nejlepší výsledek každého hráče.</td>
            </tr>
        </table>
        <div class="warn-box">
            ⚠️ <b>Pozor:</b> Tabulky nejsou propojeny cizím klíčem – vazba mezi hráčem a výsledky se řeší
            shodou hodnoty <code>jmeno</code>. Pokud admin smaže účet, smažou se i všechny jeho výsledky.
        </div>

        <!-- 7. Admin panel -->
        <h3 style="color:#0c4a6e; margin-top:18px;">7. Admin panel</h3>
        <p style="font-size:14px; line-height:1.7;">
            Admin panel je dostupný na adrese <b>http://127.0.0.1:5000/admin</b>.<br>
            Výchozí přihlašovací údaje jsou: jméno <code>admin</code>, heslo <code>admin123</code>.<br>
            V admin panelu lze smazat jakýkoli hráčský účet včetně jeho výsledků.
        </p>
        <div class="warn-box">
            ⚠️ V produkčním prostředí je nutné změnit výchozí admin heslo – ideálně přes proměnnou prostředí
            <code>ADMIN_PASSWORD</code>.
        </div>

        <!-- 8. Časté problémy -->
        <h3 style="color:#0c4a6e; margin-top:18px;">8. Časté problémy a jejich řešení</h3>
        <table>
            <tr><th>Problém</th><th>Možná příčina</th><th>Řešení</th></tr>
            <tr>
                <td>Web se nespustí</td>
                <td>Flask není nainstalovaný nebo port 5000 je obsazený</td>
                <td>Spusť <code>pip install flask</code> nebo v web.py změň <code>port=5000</code> na jiné číslo</td>
            </tr>
            <tr>
                <td>Hra se nespustí / chybí obrázky</td>
                <td>Chybí složka Obrazky nebo soubory uvnitř</td>
                <td>Hra funguje i bez obrázků – zobrazí barevné obdélníky jako náhradu</td>
            </tr>
            <tr>
                <td>Špatné jméno nebo heslo v menu</td>
                <td>Hráč ještě není registrován nebo se překlepl</td>
                <td>Nejdřív se zaregistruj přes web na http://127.0.0.1:5000</td>
            </tr>
            <tr>
                <td>Skóre se neuloží</td>
                <td>Hráč není přihlášen nebo skóre je 0</td>
                <td>Musíš být přihlášen v menu. Skóre 0 se neukládá záměrně.</td>
            </tr>
            <tr>
                <td>Není slyšet zvuk</td>
                <td>Chybí soubor flap.mp3 nebo je zvuk vypnutý v menu</td>
                <td>Zkontroluj složku Obrazky a tlačítko ZVUK v menu</td>
            </tr>
        </table>
    </section>
    """


# ──────────────────────────────────────────────
# HLAVNÍ STRÁNKA
# ──────────────────────────────────────────────

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
                user_msg = f"Registrace úspěšná. Jsi přihlášen/a jako {jmeno}."
            else:
                user_msg = "Registrace selhala. Jméno už existuje nebo je neplatné."

        elif action == "login":
            jmeno = request.form.get("jmeno", "").strip()
            heslo = request.form.get("heslo", "").strip()
            if databaze.prihlaseni(jmeno, heslo):
                session["player"] = jmeno
                user_msg = f"Přihlášení úspěšné. Vítej, {jmeno}."
            else:
                user_msg = "Špatné jméno nebo heslo."

        elif action == "logout":
            session.pop("player", None)
            user_msg = "Byl/a jsi odhlášen/a."

    logged_player = session.get("player")
    user_chip = (
        f"<div class='user-chip'>Přihlášen: {logged_player}</div>" if logged_player else ""
    )
    scores_rows = _render_scores_rows()

    if logged_player:
        auth_section = f"""
        <section class="card" id="auth" style="margin-top:16px;">
            <h2>Účet</h2>
            <p class="msg">{user_msg}</p>
            <p>Jsi přihlášen/a jako <b>{logged_player}</b>. Formuláře jsou skryté.</p>
            <form method="POST">
                <input type="hidden" name="action" value="logout">
                <button type="submit" class="btn warn">Odhlásit</button>
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
                    <input type="text" name="jmeno" placeholder="Uživatelské jméno" required>
                    <input type="password" name="heslo" placeholder="Heslo" required>
                    <button type="submit" class="btn alt">Vytvořit účet</button>
                </form>
            </article>
            <article class="card">
                <h2>Přihlášení hráče</h2>
                <p style="font-size:14px;">Po přihlášení se stejnými údaji se přihlásíš i v Pygame menu.</p>
                <form method="POST" class="form">
                    <input type="hidden" name="action" value="login">
                    <input type="text" name="jmeno" placeholder="Uživatelské jméno" required>
                    <input type="password" name="heslo" placeholder="Heslo" required>
                    <button type="submit" class="btn">Přihlásit</button>
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
    <title>Flappy Bird – Web projektu</title>
    {_base_styles()}
</head>
<body>
    <header class="topbar">
        <nav>
            <a href="#home">Domů</a>
            <a href="#auth">Účty</a>
            <a href="#navod">Návod</a>
            <a href="#ovladani">Ovládání</a>
            <a href="#diagramy">ER diagram</a>
            <a href="#vysledky">Výsledky</a>
        </nav>
    </header>

    <main class="wrap" id="home">
        <section class="hero">
            {user_chip}
            <h1>🐦 Flappy Bird – web projektu</h1>
            <p>Tato stránka slouží pro registraci, přihlášení a zobrazení výsledků.
               Nový hráč se musí nejdříve zaregistrovat zde a pak se přihlásit v Pygame menu.</p>
        </section>

        {auth_section}

        <section class="grid" style="margin-top:16px;">
            <article class="card" id="ovladani">
                <h2>🕹️ Jak se hra ovládá</h2>
                <ul>
                    <li><b>SPACE</b> – pták vyskočí nahoru</li>
                    <li>Cílem je proletět mezi trubkami bez kolize</li>
                    <li>Po konci hry stiskni <b>SPACE</b> pro návrat do menu</li>
                    <li>Mezera i čas mezi trubkami jsou náhodné – každá hra je jiná</li>
                </ul>
            </article>
            <article class="card">
                <h2>📊 O výsledcích</h2>
                <ul>
                    <li>Skóre = počet přeletěných dvojic trubek</li>
                    <li>Ukládá se pouze <b>nejlepší skóre</b> každého hráče</li>
                    <li>Výsledky se neuloží, pokud hráč není přihlášen</li>
                    <li>Skóre 0 se do tabulky nepřidá</li>
                </ul>
            </article>
        </section>

        {_render_navod()}

        <section class="card" id="diagramy" style="margin-top:16px;">
            <h2>🗄️ ER diagram databáze</h2>
            <div class="diagram-wrap">
                <svg viewBox="0 0 980 320" class="diagram-svg" xmlns="http://www.w3.org/2000/svg"
                     role="img" aria-label="ER diagram databaze">
                    <defs>
                        <marker id="arrow-end" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
                            <path d="M0,0 L12,6 L0,12 z" fill="#0f766e"/>
                        </marker>
                    </defs>
                    <rect x="60"  y="40" width="320" height="200" rx="16" fill="#f8fbff" stroke="#0c4a6e" stroke-width="2"/>
                    <rect x="60"  y="40" width="320" height="44"  rx="16" fill="#0c4a6e"/>
                    <text x="220" y="68" text-anchor="middle" font-size="24" font-weight="700" fill="#fff">UZIVATELE</text>
                    <text x="86"  y="112" font-size="19" font-weight="700" fill="#0f172a">PK id : INTEGER</text>
                    <text x="86"  y="145" font-size="19" fill="#0f172a">jmeno : TEXT (UNIQUE)</text>
                    <text x="86"  y="178" font-size="19" fill="#0f172a">heslo_hash : TEXT</text>

                    <rect x="600" y="40" width="320" height="200" rx="16" fill="#fffdf7" stroke="#b45309" stroke-width="2"/>
                    <rect x="600" y="40" width="320" height="44"  rx="16" fill="#b45309"/>
                    <text x="760" y="68" text-anchor="middle" font-size="24" font-weight="700" fill="#fff">VYSLEDKY</text>
                    <text x="626" y="112" font-size="19" font-weight="700" fill="#0f172a">PK id : INTEGER</text>
                    <text x="626" y="145" font-size="19" fill="#0f172a">jmeno : TEXT</text>
                    <text x="626" y="178" font-size="19" fill="#0f172a">body : INTEGER</text>
                    <text x="626" y="211" font-size="19" fill="#0f172a">datum : TEXT</text>

                    <line x1="380" y1="140" x2="600" y2="140" stroke="#0f766e" stroke-width="4" marker-end="url(#arrow-end)"/>
                    <text x="490" y="126" text-anchor="middle" font-size="18" font-weight="700" fill="#0f766e">1 : N</text>
                    <text x="490" y="164" text-anchor="middle" font-size="16" fill="#334155">vazba přes jmeno</text>
                </svg>
            </div>
            <p class="diagram-note">
                Diagram odpovídá databázi <b>skore.db</b>. Vazba mezi tabulkami je řešena
                logicky přes pole <b>jmeno</b>. V SQLite momentálně není nastaven cizí klíč –
                mazání účtu zajišťuje aplikační logika v <code>databaze.py</code>.
            </p>
        </section>

        <section class="card" id="vysledky" style="margin-top:16px;">
            <h2>🏆 TOP výsledky</h2>
            <table>
                <tr><th>Pořadí</th><th>Jméno</th><th>Skóre</th><th>Datum</th></tr>
                {scores_rows}
            </table>
        </section>
    </main>
</body>
</html>
"""


# ──────────────────────────────────────────────
# ADMIN PANEL
# ──────────────────────────────────────────────

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
                admin_msg = "Admin přihlášení úspěšné."
            else:
                admin_msg = "Špatné admin jméno nebo heslo."
        elif action == "admin_logout":
            session.pop("admin", None)
            admin_msg = "Admin byl odhlášen."
        elif action == "delete_user":
            if not session.get("admin"):
                admin_msg = "Pro tuto akci musíš být přihlášen jako admin."
            else:
                target_user = request.form.get("target_user", "").strip()
                if target_user == ADMIN_USERNAME:
                    admin_msg = "Admin účet nelze smazat tímto formulářem."
                elif databaze.smazat_ucet(target_user):
                    if session.get("player") == target_user:
                        session.pop("player", None)
                    admin_msg = f"Účet {target_user} byl smazán."
                else:
                    admin_msg = "Účet se nepodařilo smazat (neexistuje?)."

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
    <main class="wrap" style="max-width:520px;">
        <section class="card" style="margin-top:28px;">
            <h2>Admin přihlášení</h2>
            <p class="msg">{admin_msg}</p>
            <form method="POST" class="form">
                <input type="hidden" name="action" value="admin_login">
                <input type="text"     name="admin_name" placeholder="Admin jméno" required>
                <input type="password" name="admin_pass" placeholder="Admin heslo" required>
                <button type="submit" class="btn">Přihlásit admina</button>
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
                <button type="submit" class="btn warn">Odhlásit admina</button>
            </form>
            <table>
                <tr><th>Uživatel</th><th>Akce</th></tr>
                {users_rows}
            </table>
        </section>
    </main>
</body>
</html>
"""


if __name__ == "__main__":
    databaze.vytvorit_tabulku()
    print("Zapínám webový server. Nech toto okno otevřené.")
    print("Hráčský web : http://127.0.0.1:5000")
    print("Admin panel : http://127.0.0.1:5000/admin")
    app.run(port=5000, use_reloader=False)