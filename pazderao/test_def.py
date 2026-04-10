import unittest
import pygame
from breakout import paddle, boost
from settings import *

class TestBreakout(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init() # zapnutí pygame pro potřeby testů
        pygame.display.set_mode((1, 1)) # okno, co není vidět (jen pro testování)

    def test_paddle_reset(self):
        test_paddle = paddle()
        test_paddle.rect.x = 0 # nastavení pálky na blbou pozici
        test_paddle.reset() # zkouška funkce pro vrácení na střed
        
        expected_x = int((SCREEN_WIDTH / 2) - (test_paddle.width / 2)) # výpočet, kde by měla správně být
        self.assertEqual(test_paddle.rect.x, expected_x) # ověření, jestli se pozice rovná výpočtu

    def test_boost_movement(self):
        test_boost = boost(300, 100, 'plus') # bonus na pozici 100
        test_boost.move() # posun o jeden krok dolů
        self.assertEqual(test_boost.rect.y, 103) # kontrola, jestli se y změnilo o 3 pixely

    def test_boost_out_of_bounds(self):
        test_boost = boost(300, SCREEN_HEIGHT + 10, 'plus') # bonus mimo obrazovku
        result = test_boost.move()
        self.assertFalse(result) # potvrzení, že funkce vrátila false (bonus zmizel)

if __name__ == "__main__":
    unittest.main() # spuštění testování