import unittest, pygame, mysql.connector
from packages import funkce, block
from settings import * #Importujeme globální názvy obtížností

    
class TestCalc(unittest.TestCase):
    def test_tvorba_jidla_okraj(self): #Zde testujeme tvorbu blocku na okraji obrazovky pro obtížnost "Hard"
        obtiznost_test = "Hard" #Pro tento test neměnné
        #Vytvářím jídlo samotné, které později porovnám s požadovaným výsledkem. Funkce je na samostatném řádku pro navýšení přehlednosti
        test_jidlo = funkce.vytvoření_jídla(obtiznost_test,sloupce,20,600,600,pygame.display.set_mode((600, 600)))
        self.assertEqual(test_jidlo.get_pos()[0] in [0, 580] or test_jidlo.get_pos()[1] in [0, 580],True) #Proč [0, 580]? Jídlo je na jedné z os buď na souřadnici 0, která značí okraj, nebo je na pozici šířka_okna-velikost_blocku. Tedy 580
        pygame.quit()
    def test_zapis_score(self):
        navyseni_skore = 22
        test_username = "host"
        test_obtiznost = "Medium" #Tato obtížnost MUSÍ být v globální proměnné "sloupce".
        #Napojení na db pomocí globálních proměnných
        mydb = mysql.connector.connect(
            host = host
            ,user = username
            ,password = password
            ,database = database
        )
        mycursor = mydb.cursor(buffered=True)
        funkce.tvorba_db(mycursor,mydb) #Zde použijeme funkci pro vytvoření db a záznamu v případě jejich absence. Další funkce, která proběhne kontrolou
        #Nyní přepíšu skóre v db o požadovanou hodnotu, aby se zajistila podmínka pro přepsání.
        mycursor.execute(f"SELECT * FROM `Score` WHERE username='{test_username}'")
        nove_score = mycursor.fetchall()[0][2+sloupce.index(test_obtiznost)] + navyseni_skore
        #Zapisuji skóre
        funkce.zápis_score(nove_score,sloupce,test_obtiznost,mycursor,mydb,test_username,sloupce)
        #Fetch dat
        mycursor.execute(f"SELECT * FROM `Score` WHERE username='{test_username}'")
        #Nyní kontroluji rovnost hodnoty v db a hodnotu zvoleného skóre, která MUSÍ převyšovat dosavadní skóre v db
        self.assertEqual(
            mycursor.fetchall()[0][2+sloupce.index(test_obtiznost)], #zde přeskočím první dvě hodnoty, protože se jedná o username a password. Poté indexuji podle zvolené testovací obtížnosti
            nove_score #Porovnávám s požadovanou hodnotou
        )
        mydb.close()
if __name__ == '__main__':
    unittest.main()
