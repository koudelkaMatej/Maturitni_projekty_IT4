import unittest

import game
import objects






class TestGame(unittest.TestCase):

    def test_play_sound_1(self):
        self.assertTrue(game.play_sound("success-sfx"))

    def test_play_sound_2(self):
        # NO FILE
        self.assertEqual(game.play_sound("null"), "failure")




    def test_play_music_1(self):
        self.assertTrue(game.play_music("play"))

    def test_play_music_2(self):
        # NO FILE
        self.assertEqual(game.play_music("null"), "failure")

    def test_play_music_3(self):
        # INT overflow
        self.assertEqual(game.play_music("play", 9999999999), "failure")
    
    def test_play_music_4(self):
        # INT overflow
        self.assertEqual(game.play_music("play", 0, 9999999999), "failure")

    
    def test_play_1(self):
        game_obj = game.Game()
        play_obj = game.PlayScreen(game_obj._set_state)
        self.assertEqual(play_obj.multiplier(), 1)

    def test_play_2(self):
        game_obj = game.Game()
        play_obj = game.PlayScreen(game_obj._set_state)
        play_obj.permanent_storage = 5
        self.assertEqual(play_obj.multiplier(), 2)

    def test_play_3(self):
        game_obj = game.Game()
        play_obj = game.PlayScreen(game_obj._set_state)
        play_obj.effectors['another_chance']['level'] = 5
        self.assertEqual(play_obj.salvage_chance(), 0.5)

    def test_play_4(self):
        game_obj = game.Game()
        play_obj = game.PlayScreen(game_obj._set_state)
        play_obj._advance_level()
        self.assertEqual(play_obj.current_debt, 15)


class TestTimer(unittest.TestCase):

    def test_timer_starts_inactive(self):
        t = objects.Timer(1000)
        self.assertFalse(t.is_active)

    def test_timer_active_after_start(self):
        t = objects.Timer(1000)
        t.start()
        self.assertTrue(t.is_active)

    def test_timer_stops(self):
        t = objects.Timer(1000)
        t.start()
        t.stop()
        self.assertFalse(t.is_active)

    def test_callback_fires(self):
        fired = []
        t = objects.Timer(0, callback=lambda: fired.append(True))
        t.start()
        t.update()
        self.assertTrue(len(fired) > 0)

class TestTimerManager(unittest.TestCase):

    def test_add_and_retrieve_timer(self):
        tm = objects.TimerManager()
        tm.add_timer("test", 1000)
        self.assertIn("test", tm.timers)

    def test_delay_creates_timer(self):
        tm = objects.TimerManager()
        tm.delay(0, lambda: None)
        self.assertTrue(len(tm.timers) > 0)


if __name__ == '__main__':
    unittest.main()