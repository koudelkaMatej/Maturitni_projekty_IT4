## Maturitní projekt  
**Flappy Turtle**  

Hra inspirovaná klasickou hrou Flappy Bird s rozšířenými funkcemi:  
- 3 obtížnosti (easy, medium, hard), které ovlivňují rychlost pohybu i velikost mezer mezi trubkami.  
- Náhodné generování překážek (různá mezera, různý časový odstup).  
- Systém přihlašování uživatelů (registrace / login) – bez přihlášení se skóre a achievementy neukládají.  
- Achievementy (první skóre, skóre 20, skóre 100, vítězství na každé obtížnosti).  
- Webové rozhraní (Flask) – žebříček, profily uživatelů, správa uživatelů (admin).  
- Ukládání skóre a achievementů do SQLite databáze.

## Spuštění

- **Hra:** `python hra.py` → menu → obtížnost → přihlášení → hraní.
- **Web:** `python app.py` → otevři `http://127.0.0.1:5000`. Pro žebříček je nutné přihlášení.
- **Admin:**  `admin` / `tvoje_heslo` – získá přístup ke správě leaderboard, uživatelů a statistikám.

 
### Struktura projektu  
- `main.py` – kompletně celá hra
- `add_achievements.py` – přidání achievemenů  
- `app.py` – webová stránka
- `static/style.css` – styl webového rozhraní.  
- `flappy.db` – obsahují herní data.   
- `databaze.py` – SQLite databáze (vytvoří se při prvním spuštění).
- `init_db.py` – inicializace databáze pro webovku
