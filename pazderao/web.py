from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import webbrowser
from settings import host, username, password, database, povolené_znaky
from flask import request

app = Flask(__name__)
# nutnost pro fungování loginu
app.secret_key = "HESLO1234567890"
def get_db():
    return mysql.connector.connect(host=host, user=username, password=password, database=database)

@app.route('/')
def index():
    # zjištění jestli je někdo přihlášen
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/tab')
def tabulka():
    user = session.get('user')
    # Získání levelu z URL, pokud není zadán, default je 2 (střední)
    level = request.args.get('level', default=2, type=int)
    
    try:
        conn = mysql.connector.connect(host=host, user=username, password=password, database=database)
        cursor = conn.cursor(dictionary=True)

        # SQL dotaz pro tvoji tabulku
        query = "SELECT username, time_str FROM pazderao_casy WHERE level = %s ORDER BY time_ms ASC LIMIT 10"
        cursor.execute(query, (level,))
        leaderboard = cursor.fetchall()

        cursor.close()
        conn.close()
        
        # Tady posíláme data do tvého tab.html
        return render_template('tab.html', leaderboard=leaderboard, level=level, user=user)
    
    except Exception as e:
        print(f"Chyba DB: {e}")
        return f"Chyba při načítání žebříčku: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form.get('username', '')
        # kontrola znaků kvůli bezpečnosti
        if all(c in povolené_znaky for c in user_input) and user_input.strip() != "":
            # uložení jména do paměti prohlížeče
            session['user'] = user_input.capitalize()
            return redirect(url_for('profile'))
            
    return render_template('login.html', user=session.get('user'))

@app.route('/logout')
def logout():
    # vymaže data a odhlásí
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/about')
def about():
    # Pokud v navigaci zobrazuješ jméno uživatele, musíme ho vytáhnout ze session
    user = session.get('user') 
    return render_template('about.html', user=user)
    

@app.route('/profile')
def profile():
    # když není přihlášen, vyhodí ho to na login
    if 'user' not in session:
        return redirect(url_for('login'))
        
    user_name = session['user']
    stats = []
    
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        # ukáže jen časy daného hráče
        query = "SELECT level, time_str FROM pazderao_casy WHERE username = %s ORDER BY level ASC, time_ms ASC"
        cursor.execute(query, (user_name,))
        stats = cursor.fetchall()
    except Exception as e:
        print(f"chyba profilu: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            
    return render_template('profile.html', user=user_name, stats=stats)

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=False)