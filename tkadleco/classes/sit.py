import requests
import threading

class SpravceSite:
    def __init__(self):
        # POZOR: Zde musí být ta adresa s vlnovkou!
        self.url = "https://xeon.spskladno.cz/~tkadleco/index.php"

    def odesli_skore(self, jmeno, body):
        """ Spustí odesílání ve vedlejším vlákně, aby se hra nezasekla """
        vlakno = threading.Thread(target=self._odesli_task, args=(jmeno, body))
        vlakno.start()

    def _odesli_task(self, jmeno, body):
        try:
            data = {'hrac': jmeno, 'body': body}
            response = requests.post(self.url, data=data, timeout=5)
            if response.text.strip() == "ULOZENO":
                print(f"Skóre uloženo: {jmeno} - {body}")
            else:
                print(f"Chyba serveru: {response.text}")
        except Exception as e:
            print(f"Chyba připojení: {e}")