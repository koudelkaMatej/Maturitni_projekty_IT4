import unittest
from app import calculate_reward, validate_match_payload

class TestProject(unittest.TestCase):

    def test_calculate_reward_win(self):
        # WIN: 20 + (kills*2) + (waves*10) + 100
        self.assertEqual(calculate_reward("WIN", 10, 2), 20 + 20 + 20 + 100)

    def test_validate_payload_ok(self):
        data = {"result": "LOSE", "waves_reached": 3, "kills": 5}
        result, waves, kills = validate_match_payload(data)
        self.assertEqual(result, "LOSE")
        self.assertEqual(waves, 3)
        self.assertEqual(kills, 5)

if __name__ == "__main__":
    unittest.main()
