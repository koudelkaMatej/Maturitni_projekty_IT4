# Maturitní projekt 


Tento projekt je přizpůsoben na hru Breakout, vytvořenou jako maturitní práci. Hráč ovládá pálku a pomocí odrážejícího se míčku musí zničit všechny cihly na obrazovce v co nejlepším čase. Součástí projektu je též webová stránka, na které se uživatel může dozvědět informace o hře, aktuální stav tabulky a po přihlášení i své časy.


1. Jedná se o hru breakout, naprogramovanou v jazyce Python, použitím knihovny PyGame.
2. Hra je rozdělena do více souborů, aby byla manipulace se souborem rychlejší a projekt celkově přehlednější.
3. Hra umožňuje hráči možnost přihlášení, díky kterému si poté na webové stránce může prohlédnout své výsledky. 
4. Ve hře se nachází možnost zvolení obtížnosti 
5. Součástí je funkční časomíra, která ukládá dosažené výsledky do vzdálené MySQL databáze.
6. Po dohrání nebo výhře se nejlepší časy zobrazují v žebříčku přímo ve hře nebo na webu.
7. U ničení cihel je 20% šance na takzvaných "Boostů", které hráči mohou hru usnadnit, či naopak znevýhodnit.



# Stažení

[!Download]https://downgit.github.io/#/home?url=https://github.com/koudelkaMatej/Maturitni_projekty_IT4/tree/Ondrej-Pazdera/pazderao



# Spuštení hry

1. Je potřeba mít nainstalovaný Python verze 3.8 nebo novější.
2. Nainstalujte potřebné knihovny pomocí terminálu:
    pip install -r requirements.txt¨

3. Nastavte údaje pro připojení k vaší MySQL databázi v souboru settings.py:
    host = "Vas_host"
    username = "Vase_jmeno"
    password = "Vase_heslo"
    database = "Nazev_databaze"

4. Spusťte hru a web.
python web.py
python breakout.py

# Webové rozhraní a žebříčky
# Web běží na lokálním serveru a umožňuje prohlížet nejlepší časy rozdělené podle obtížnosti.


# Struktura projektu
. 
├── requirements.txt      _Seznam knihoven k instalaci_
├── settings.json         _Konfigurační soubor VS Code_
├── .gitignore            _Seznam ignorovaných repozitářů_
├── readme.md             _Základní informace o projektu_
├── settings.py           _Konfigurace barev, rozlišení a databáze_
├── breakout.py           _Hlavní soubor se hrou_
├── Timer.py              _Logika měření času a komunikace s DB_
├── menu.py               _Definice tlačítek a herních menu_
├── web.py                _Backend pro webové stránky_
├── static/
│   └── style.css         _Vzhled webu_
├── templates/
│   ├── about.html        _Stránka o projektu_
│   ├── index.html        _Hlavní stránka webu_
│   ├── tab.html          _Tabulka výsledků_
│   ├── profile.html      _Profil uživatele_
│   └── login.html        _Přihlášení uživatele_
└── images/
    └──font
        ├── lemonmilk.otf
        ├── squeaky.otf
        └── Wan22345.ttf
    ├── background.jpg    _Pozadí hry_
    ├── ball.png          _Booster míček_
    ├── bg.gif            _Alternativní pozadí (nevyužito)_
    ├── minus.png         _Booster velikosti pálky -_
    ├── Er-Diagram.png    _Er-diagram hry_
    └── plus.png          _Booster velikosti pálky +_




# Obtížnosti

## Obtížnost	Šířka pálky	        Rychlost míčku	        Cihly	
   Easy	        Široká pálka	    Pomalý míček	        5 řad, slabá výdrž	
   Medium	    Normální pálka	    Střední rychlost	    6 řad, střední výdrž	
   Hard	        Normální pálka	    Vysoká rychlost	        6 řad, vysoká výdrž	

# Autor
Ondřej Pazdera 
Třída: IT4
Školní rok: 2026/2027

# Důležité informace
* Při odražení míčku hranou pálky se míček bude pohybovat rychleji, hra je přizpůsobena tak, aby se míček dostal na konkrétní úroveň ve stejný čas.