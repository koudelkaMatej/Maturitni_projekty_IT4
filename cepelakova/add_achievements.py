import sqlite3

conn = sqlite3.connect("flappy.db")
c = conn.cursor()

seznam = [
    ("První krůček", "Získej první skóre"),
    ("Skokan", "Dosáhni skóre 20"),
    ("Veterán", "Dosáhni skóre 100"),
    ("Obtížnost Easy", "Vyhraj na easy dosáhnutím skóre 50"),
    ("Obtížnost Medium", "Vyhraj na medium dosáhnutím skóre 50"),
    ("Obtížnost Hard", "Vyhraj na hard dosáhnutím skóre 50"),
]

for name, desc in seznam:
    try:
        c.execute("INSERT INTO achievements (name, description) VALUES (?, ?)", (name, desc))
    except:
        pass

conn.commit()
conn.close()
print("Hotovo, achievements jsou v databázi.")