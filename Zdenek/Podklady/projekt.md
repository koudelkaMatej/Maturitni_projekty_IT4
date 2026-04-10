# Tahak k upravam projektu

Tenhle soubor je schvalne psany jako rychly maturitni tahak.
Neni to detailni vyuka Pythonu nebo Flasku.
Cil je vedet:

- co se da menit
- kde to najdes
- co s cim souvisi

## 1. Rychla mapa projektu

- `app.py` = hlavni Flask web aplikace
- `db.py` = pripojeni do MySQL databaze
- `config.py` = tajny klic Flasku
- `databaze.py` = vytvareni, mazani a zakladni sprava DB
- `tower_defense_pygame.py` = desktop verze hry v Pygame
- `templates/*.html` = vzhled jednotlivych stranek
- `static/css/style.css` = barvy, layout, tlacitka, tabulky, responzivita
- `tests/test_app.py` = testy backendu

## 2. Kde najdu jednotlive stranky

- registrace: `templates/register.html`
- prihlaseni: `templates/login.html`
- profil: `templates/profile.html`
- statistiky: `templates/stats.html`
- historie her: `templates/history.html`
- leaderboard: `templates/leaderboard.html`
- admin stranka: `templates/admin.html`

Napojeni stranek je v `app.py` pres `@app.route(...)` a `render_template(...)`.

## 3. Co se nejcasteji upravuje a kde

- Nazev aplikace, texty na strankach:
  hledej hlavne v `templates/*.html`

- Odkazy mezi strankami:
  hledej v HTML sablonach a v routach v `app.py`

- Prihlaseni / registrace:
  `app.py`
  Funkce `register()`, `login()`, `logout()`

- Kontrola admina:
  `app.py`
  Funkce `is_admin()`
  Ted je admin podle username `sa`

- Tajny Flask klic:
  `config.py`

- Pripojeni do databaze:
  `db.py`
  Tam je `DB_CONFIG`

- Vytvoreni tabulek:
  `databaze.py`
  Tam jsou SQL prikazy `CREATE TABLE`

- Vychozi admin ucet:
  `databaze.py`
  Vklada se uzivatel `sa`

- Ukladani vysledku hry:
  `app.py`
  Funkce `save_match_result()`
  API route: `/api/match`

- Validace dat z hry:
  `app.py`
  Funkce `validate_match_payload()`

- Vypocet odmeny:
  `app.py`
  Funkce `calculate_reward()`

- Statistiky hrace:
  `app.py`
  Funkce `get_player_stats()`

- Leaderboard:
  `app.py`
  Konstanta `LEADERBOARD_BASE_QUERY` a route `leaderboard()`

- Mazani nebo reset uzivatele:
  `app.py`
  Funkce `delete_user_data()`, `reset_user_data()`

- Odemceni vezi:
  `app.py`
  `ensure_default_tower_unlock()`, `get_unlocked_towers()`, `build_tower_payload()`

## 4. Kdyz chces menit herni hodnoty

Nejdulesitejsi misto je `TOWER_CATALOG` v `app.py`.
Tam menis napriklad:

- jmeno veze
- popis veze
- cenu
- cenu za odemceni
- dostrel
- damage
- cooldown
- barvu
- splash radius
- slow efekt

Pozor:
podobna data jsou i v `tower_defense_pygame.py`.
Kdyz chces, aby web a desktop verze odpovidaly stejne logice, uprav casto oba soubory.

## 5. Kdyz chces menit obtiznost hry

V `app.py` je slovnik `DIFFICULTIES`.
Tam najdes:

- easy
- normal
- hard
- reward bonus

V `tower_defense_pygame.py` je obtiznost rozsirena jeste o:

- enemy speed
- enemy hp
- enemies per wave
- starting lives
- starting gold

Takze:
pro webovou logiku staci casto `app.py`,
pro realny gameplay musis casto i `tower_defense_pygame.py`.

## 6. Kdyz chces menit vzhled webu

Vsechno hlavni je v `static/css/style.css`.
Tam najdes:

- barvy v `:root`
- styl tlacitek
- styl formularu
- kontejnery a panely
- tabulky leaderboardu
- responzivni cast pro mobil

Kdyz menis konkretni rozlozeni jedne stranky, tak:

- HTML struktura je v `templates/...`
- vzhled trid je v `static/css/style.css`

## 7. Kdyz chces menit databazi

Hlavni pravidlo:
kdyz menis strukturu DB, nekoukej jen do jednoho souboru.

Obvykle musis zkontrolovat:

- `databaze.py` = struktura tabulek
- `app.py` = SQL dotazy, ktere tabulky pouzivaji
- `templates/*.html` = jestli se nove hodnoty nekde vypisuji
- `tests/test_app.py` = jestli se kvuli tomu nerozbiji testy

Priklady:

- pridas sloupec do `users`:
  uprav `CREATE TABLE users` a potom i `SELECT`/`INSERT`/`UPDATE` v `app.py`

- pridas sloupec do `matches`:
  uprav tabulku a pak i ukladani vysledku, statistiky, historii a leaderboard

## 8. Kdyz chces menit admin funkce

Admin cast je v `app.py` pod route `/admin`.
Najdes tam:

- kontrolu, jestli je uzivatel prihlaseny
- kontrolu, jestli je admin
- mazani uzivatele
- reset statistik uzivatele
- nacitani seznamu uzivatelu

Vzhled admin stranky je v `templates/admin.html`.

## 9. Kdyz chces menit poradi nebo obsah leaderboardu

Jdi do `app.py`:

- `LEADERBOARD_BASE_QUERY`
- route `leaderboard()`

Tam zmenis napr.:

- podle ceho se radi
- kolik zaznamu se vypise
- jake sloupce se budou zobrazovat

Kdyz menis sloupce v tabulce na webu, zkontroluj i `templates/leaderboard.html`.

## 10. Kdyz chces menit profil a statistiky

Profil je hlavne:

- route `profile()` v `app.py`
- sablona `templates/profile.html`

Statistiky jsou hlavne:

- route `stats()` v `app.py`
- funkce `get_player_stats()`
- sablona `templates/stats.html`

Historie her:

- route `history()` v `app.py`
- sablona `templates/history.html`

## 11. Kdyz chces menit prihlasovaci logiku

Najdes v `app.py`:

- `logged_in()`
- `login()`
- `logout()`
- `register()`

Kdybys napr. chtel:

- jine overeni admina
- vice poli pri registraci
- kontrolu delky hesla
- hash hesel

tak hlavni misto je `app.py`,
ale u novych DB poli i `databaze.py`.

## 12. Kdyz chces menit desktop verzi hry

Pouzij `tower_defense_pygame.py`.
Tam najdes:

- prihlaseni do hry
- profile coins
- unlock vezi
- difficulty
- enemy typy
- vlny
- vykreslovani UI
- klavesove zkratky

Tohle je uz samostatna cast projektu.
Web a desktop spolu sdileji databazi, ale ne vsechnu logiku uplne stejne.

## 13. Co je dobre si ohlidat u maturity

- Kdyz menis data v DB, mysli i na SQL dotazy.
- Kdyz menis backend data, mysli i na template.
- Kdyz menis herni hodnoty, zkontroluj web i Pygame verzi.
- Kdyz menis admina, zkontroluj `is_admin()` i vytvoreni admin uctu.
- Kdyz menis vzhled, nejdriv najdi HTML tridu a pak ji v CSS uprav.

## 14. Doporuceny rychly postup pri uprave

1. Najdi, jestli jde o backend, databazi, vzhled, nebo hru.
2. Otevri hlavni soubor podle mapy vyse.
3. Uprav jen konkretni cast, ne vsechno najednou.
4. Zkontroluj, jestli na to nenavazuje template nebo SQL.
5. Kdyz menis DB, mysli i na `databaze.py`.
6. Kdyz menis gameplay, mysli i na `tower_defense_pygame.py`.

## 15. Nejkratsi orientace

Kdyz nebudes vedet:

- web logika = `app.py`
- databaze = `db.py` a `databaze.py`
- vzhled = `templates/` + `static/css/style.css`
- hra = `tower_defense_pygame.py`
- testy = `tests/test_app.py`

