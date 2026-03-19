import unittest
import pygame
from breakout import paddle, boost
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BOOST_SIZE

class TestBreakoutLogic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Musíme inicializovat pygame, aby fungovaly Rect objekty
        pygame.init()
        pygame.display.set_mode((1, 1)) # Malé neviditelné okno pro testy

    def test_paddle_reset(self):
        # Test 1: Kontrola, jestli se pálka po resetu vrátí doprostřed obrazovky
        test_paddle = paddle()
        # Změníme pozici na nesmyslnou hodnotu
        test_paddle.rect.x = 0
        
        # Zavoláme reset
        test_paddle.reset()
        
        # Vypočítáme, kde by měla být (střed - polovina šířky)
        expected_x = int((SCREEN_WIDTH / 2) - (test_paddle.width / 2))
        self.assertEqual(test_paddle.rect.x, expected_x)

    def test_boost_movement(self):
        # Test 2: Kontrola, jestli boost (věc co padá) správně mění Y souřadnici
        # Vytvoříme boost na pozici Y = 100
        test_boost = boost(300, 100, 'plus')
        
        # V breakout.py má boost speed = 3
        test_boost.move()
        
        # Po jednom pohybu by měl být na Y = 103
        self.assertEqual(test_boost.rect.y, 103)

    def test_boost_out_of_bounds(self):
        # Test 3: Kontrola, jestli move() vrátí False, když boost vyletí z obrazovky
        # Dáme ho těsně nad spodní okraj
        test_boost = boost(300, SCREEN_HEIGHT + 10, 'plus')
        result = test_boost.move()
        
        # Mělo by to vrátit False (protože rect.top už není < SCREEN_HEIGHT)
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()