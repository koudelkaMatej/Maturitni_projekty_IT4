import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as webapp


class FakeCursor:
    def __init__(self, fetchone_values=None, fetchall_values=None, execute_side_effect=None):
        self.fetchone_values = list(fetchone_values or [])
        self.fetchall_values = list(fetchall_values or [])
        self.execute_side_effect = execute_side_effect
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))
        if self.execute_side_effect:
            self.execute_side_effect(query, params)

    def fetchone(self):
        if self.fetchone_values:
            return self.fetchone_values.pop(0)
        return None

    def fetchall(self):
        if self.fetchall_values:
            return self.fetchall_values.pop(0)
        return []

    def close(self):
        return None


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.commit_called = False
        self.rollback_called = False
        self.closed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.commit_called = True

    def rollback(self):
        self.rollback_called = True

    def close(self):
        self.closed = True


class TestProject(unittest.TestCase):
    def setUp(self):
        webapp.app.config["TESTING"] = True
        self.client = webapp.app.test_client()

    def test_calculate_reward_win(self):
        self.assertEqual(webapp.calculate_reward("WIN", 10, 2), 160)

    def test_validate_payload_ok(self):
        data = {
            "result": "LOSE",
            "waves_reached": 3,
            "kills": 5,
            "difficulty": "hard",
        }
        result, waves, kills, difficulty = webapp.validate_match_payload(data)
        self.assertEqual(result, "LOSE")
        self.assertEqual(waves, 3)
        self.assertEqual(kills, 5)
        self.assertEqual(difficulty, "hard")

    def test_validate_payload_uses_default_difficulty(self):
        result, waves, kills, difficulty = webapp.validate_match_payload(
            {"result": "WIN", "waves_reached": 4, "kills": 9}
        )
        self.assertEqual((result, waves, kills, difficulty), ("WIN", 4, 9, "normal"))

    def test_validate_payload_rejects_negative_values(self):
        with self.assertRaises(ValueError):
            webapp.validate_match_payload(
                {"result": "WIN", "waves_reached": -1, "kills": 9, "difficulty": "normal"}
            )

        with self.assertRaises(ValueError):
            webapp.validate_match_payload(
                {"result": "WIN", "waves_reached": 1, "kills": -9, "difficulty": "normal"}
            )

    def test_validate_payload_rejects_invalid_difficulty(self):
        with self.assertRaises(ValueError):
            webapp.validate_match_payload(
                {"result": "WIN", "waves_reached": 4, "kills": 9, "difficulty": "nightmare"}
            )

    def test_upgrade_cost_scales_per_level(self):
        self.assertEqual(webapp.calculate_upgrade_cost(1), 45)
        self.assertEqual(webapp.calculate_upgrade_cost(2), 80)

    def test_register_success(self):
        cursor = FakeCursor()
        connection = FakeConnection(cursor)
        with patch("app.get_db", return_value=connection):
            response = self.client.post(
                "/register",
                data={"username": "new_user", "password": "secret"},
                follow_redirects=False,
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login")
        self.assertTrue(connection.commit_called)
        self.assertIn("INSERT INTO users", cursor.executed[0][0])

    def test_login_success_sets_session(self):
        cursor = FakeCursor(fetchone_values=[(7, "secret")])
        connection = FakeConnection(cursor)

        with patch("app.get_db", return_value=connection):
            response = self.client.post(
                "/login",
                data={"username": "alice", "password": "secret"},
                follow_redirects=False,
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/profile")
        with self.client.session_transaction() as session_state:
            self.assertEqual(session_state["user_id"], 7)
            self.assertEqual(session_state["username"], "alice")

    def test_login_invalid_credentials(self):
        cursor = FakeCursor(fetchone_values=[None])
        connection = FakeConnection(cursor)

        with patch("app.get_db", return_value=connection):
            response = self.client.post(
                "/login",
                data={"username": "alice", "password": "bad"},
                follow_redirects=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Spatne jmeno nebo heslo.", response.data)

    def test_save_match_result_updates_database(self):
        cursor = FakeCursor()
        connection = FakeConnection(cursor)

        with patch("app.get_db", return_value=connection):
            reward = webapp.save_match_result(
                3,
                {"result": "WIN", "waves_reached": 6, "kills": 11, "difficulty": "hard"},
            )

        self.assertEqual(reward, webapp.calculate_reward("WIN", 11, 6, "hard"))
        self.assertTrue(connection.commit_called)
        self.assertEqual(len(cursor.executed), 2)
        self.assertIn("INSERT INTO matches", cursor.executed[0][0])
        self.assertIn("UPDATE users SET coins = coins + %s", cursor.executed[1][0])

    def test_api_match_returns_validation_error(self):
        with self.client.session_transaction() as session_state:
            session_state["user_id"] = 11
            session_state["username"] = "tester"

        response = self.client.post("/api/match", json={"result": "DRAW", "waves_reached": 1, "kills": 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
