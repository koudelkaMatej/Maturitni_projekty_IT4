# GradProj
Samostatný maturitní projekt - Michal Schenk

# Specifikace
Téma: Hra založená na faktorech náhody (Inspirace hrou FLATHEAD od Tima Oxtona)

# Myšlenka
Hráčova postava stojí před strojem který po "započatí tahu" vyberou se dvě zcela náhodná čísla od 1 do 20*.
1. náhodné číslo je pouze rozdělovač dvou rozsahů (př. 1. číslo 10: 1. rozsah = <1-9>, 2. rozsah = <11-20>)
2. náhodné číslo je tedy členem jednoho ze dvou rozsahů
Hráč dostane k dispozici pouze 1. náhodné číslo, 2. je mu zcela neznámé, a jeho úlohou je zjistit v jakém rozsahu se právě to druhé číslo nachází.

Hráč tedy vlastně hádá pouze dvě varianty: číslo je větší, číslo je menší**.
Hráčova postava je vlastně dlužník nějáké smyšlené enitě/společnosti/... (Příběh není v plánu) a každým správným odhadem získá "body", kterými splácí svůj dluh.

Po splacení "úrovně" dluhu hráč postupuje na další úroveň. Pokud se hráčovi nepodaří "úrovňový" dluh splatit, končí***.

- \*Horní hranice může být dynamická na více faktorech (úroveň, obtížnost, efekty, atp.).
- \*\*Jeden z mých nápadů je, že hráč bude moct pokusit se odhadnout přesné číslo pro získání vyšší odměny.
- \*\*\*V plánu jsou nějaké hrozby, které by mohly body krást, nebo hru rovnou ukončit.

# Plány
- [x] Postoupení na další úroveň
- [x] Nekonečno úrovní
- [ ] Multipliery podle Temporary bodů (více Temporary bodů = vyšší odměny)
- [ ] Efekty/Efektory (zvýšení rozsahu, dvojnásobná odměna, pomoc při odhadu, atd.)
- [ ] Pokusy o přesný odhad pro vyšší odměnu
- [ ] Hrozby (časovač, nepřátelé, atd.)
