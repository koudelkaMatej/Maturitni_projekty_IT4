"""
sit.py - Síťová komunikace pro odesílání skóre
Autor: [tvoje jméno]

Odesílá výsledky hráče na školní server (žebříček).
Komunikace probíhá v samostatném vlákně, aby se hra nezasekla
při pomalém připojení nebo nedostupném serveru.
"""

import requests
import urllib3
import threading

# Potlač varování o nedůvěryhodném SSL certifikátu (školní server)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SpravceSite:
    """
    Zajišťuje odesílání skóre na server žebříčku.

    Odesílání probíhá asynchronně (vedlejší vlákno),
    takže hra pokračuje bez čekání na odpověď serveru.
    """

    def __init__(self):
        # URL skriptu na školním serveru (POZOR: vlnovka v cestě je nutná!)
        self.url = "http://xeon.spskladno.cz/~tkadleco/zebricek.php"

    def odesli_skore(self, jmeno, body):
        """
        Spustí odesílání skóre ve vedlejším vlákně.

        Díky daemon=True vlákno automaticky skončí při ukončení hry.

        Args:
            jmeno (str): Jméno hráče (max 12 znaků, alfanumerické)
            body (int):  Dosažené skóre
        """
        vlakno = threading.Thread(
            target=self._odesli_task,
            args=(jmeno, body),
            daemon=True
        )
        vlakno.start()

    def _odesli_task(self, jmeno, body):
        """
        Interní metoda — provede HTTP POST požadavek na server.

        Běží v samostatném vlákně. Server odpoví textem 'ULOZENO'
        při úspěchu nebo chybovou zprávou při selhání.

        Args:
            jmeno (str): Jméno hráče
            body (int):  Skóre
        """
        try:
            data     = {"hrac": jmeno, "body": body}
            response = requests.post(self.url, data=data, timeout=5, verify=False)
            if response.text.strip() == "ULOZENO":
                print(f"Skóre uloženo: {jmeno} — {body} bodů")
            else:
                print(f"Chyba serveru: {response.text}")
        except Exception as e:
            print(f"Chyba připojení: {e}")
