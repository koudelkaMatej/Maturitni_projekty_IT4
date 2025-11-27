
## Úvod
* Jedná se o snake hru naprogramovanou pomocí knihovny Pygame v jazyce Python, za účelem školního projektu.
* Hra je rozdělena do vícero souborů pro snažší čitelnost
* Hra obsahuje možnost zvolení obtížnosti(více k obtížnostem níže), obsahuje možnost nápovědy, zobrazení a vynulování hodnot skóre dosažených uživatelem a žebříček nejlepšího hráče pro individuální obtížnost
* Hra ukládá hodnoty skóre pro jednotlivé uživatele do Vámi specifikované remote db 
* Volba nickname při každém spuštění programu je samozřejmostí
* Projekt umožňuje WEB interface pro detailnější zobrazení žebříčků a profilů jednotlivých hráčů
* Program obsahuje prevenci vůči SQLi

---

## Stažení

[![Download](https://img.shields.io/badge/Klikni%20zde-green?style=for-the-badge)](https://downgit.github.io/#/home?url=https://github.com/koudelkaMatej/Maturitni_projekty_IT4/tree/main/kroufekj)



---
## ▶️ Jak spustit

1. Bude potřeba Python 3.8+.
2. Nainstalujte knihovny:

```
pip install -r requirements.txt
```

3. Nakonfigurujte připojení k MySQL v souboru `settings.py`:

```
host = "<Váš_host>"
username = "<Vaše_uživatelské_jméno>"
password = "<Vaše_heslo>"
database = "<název_databáze>"
```

4. Spusťte hru:

```
python snake-game.py
```

---

<div style="display: flex; gap: 10px;">
    <img src="https://github.com/koudelkaMatej/Maturitni_projekty_IT4/blob/main/kroufekj/img/1.png" width="30%" height="40%">
    <img src="https://github.com/koudelkaMatej/Maturitni_projekty_IT4/blob/main/kroufekj/img/2.png" width="30%" height="40%">
</div>
<div style="display: flex; gap: 10px;">
    <img src="https://github.com/koudelkaMatej/Maturitni_projekty_IT4/blob/main/kroufekj/img/3.png" width="30%" height="40%">
    <img src="https://github.com/koudelkaMatej/Maturitni_projekty_IT4/blob/main/kroufekj/img/4.png" width="30%" height="40%">
</div>


---


## Žebříčky

<div style="display: flex; gap: 10px;">
    <img src="https://github.com/koudelkaMatej/Maturitni_projekty_IT4/blob/main/kroufekj/img/6.png" width="30%" height="40%">
    <img src="https://github.com/koudelkaMatej/Maturitni_projekty_IT4/blob/main/kroufekj/img/5.png" width="30%" height="40%">
</div>

---

## Volba nickname

<div style="display: flex; gap: 10px;">
    <img src="https://github.com/koudelkaMatej/Maturitni_projekty_IT4/blob/main/kroufekj/img/7.png" width="30%" height="40%">
    <img src="https://github.com/koudelkaMatej/Maturitni_projekty_IT4/blob/main/kroufekj/img/8.png" width="30%" height="40%">
</div>

---

## WEB interface

<div style="display: flex; gap: 10px;">
    <img src="https://github.com/koudelkaMatej/Maturitni_projekty_IT4/blob/main/kroufekj/img/9.png" width="30%" height="40%">
    <img src="https://github.com/koudelkaMatej/Maturitni_projekty_IT4/blob/main/kroufekj/img/10.png" width="30%" height="40%">
</div>

---

## 📁 Struktura

```
.    
├── requirements.txt
├── .gitignore
├── settings.py    
├── snake-game.py                   
├── packages/
│   ├── block.py
│   ├── nickname.py
│   ├── funkce.py
│   ├── snake.py
│   └── okno_volby.py
├── web.py  
├── static/
│   └── style.css
├── templates/
│   ├── index.html
│   └── profile.html
├── img/
│   ├── 1.jpg
│   ├── 2.jpg
│   ├── 3.jpg
│   ├── 4.jpg
│   ├── 5.jpg
│   ├── 6.jpg
│   ├── 7.jpg
│   ├── 8.jpg
│   ├── 9.jpg
│   └── 10.jpg
└── readme.md
```

## Obtížnosti

| Obtížnost | Easy  | Medium  | Hard |
| ------- | --- | --- | --- |
| Popis | jídlo nebude nikdy na okraji obrazovky | jídlo může, ale nemusí být na okraji obrazovky (50%) | jídlo je vždy na okraji obrazovky |



