import unittest
import keydb

from api import App


# test redis client
class TestRedisClient(unittest.TestCase):
    """Test the redis client."""

    def setUp(self):
        self.db_client = keydb.KeyDB(
            host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
        )
        self.db_client.flushall()

    def test_db_client(self):
        self.db_client.set("test", "test")
        self.assertEqual(self.db_client.get("test"), "test")


class TestAppRooms(unittest.TestCase):
    """Test the App class room methods."""

    @classmethod
    def setUpClass(self):
        self.db_client = keydb.KeyDB(
            host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
        )

    def setUp(self):
        self.db_client.flushall()
        self.app = App(self.db_client)

    def test_add_user_to_room(self):
        self.app.add_user_to_room("room1", 1)

        created_room_code = self.app.create_room("1", "room1")

        # check if user is added to the room
        self.assertEqual(self.db_client.scard(f"room:{created_room_code}:users"), 1)
        self.assertEqual(
            self.db_client.sismember(f"room:{created_room_code}:users", 1), 1
        )
        # check if room is added to the user
        self.assertEqual(self.db_client.scard(f"user:1:rooms"), 1)
        self.assertEqual(
            self.db_client.sismember(f"user:1:rooms", f"{created_room_code}"), 1
        )

    def test_create_room(self):
        created_room_code = self.app.create_room("user1", "room1")

        self.assertEqual(
            self.db_client.hget(f"room:{created_room_code}", "name"), "room1"
        )

    def test_get_room_members(self):
        created_room_code = self.app.create_room("1", "room1")
        self.app.add_user_to_room(created_room_code, 1)
        self.app.add_user_to_room(created_room_code, 2)

        self.assertEqual(self.app.get_room_members(created_room_code), {"1", "2"})

    def test_get_user_rooms(self):
        created_room1_code = self.app.create_room("X", "room1")
        created_room2_code = self.app.create_room("X", "room2")

        self.app.add_user_to_room(created_room1_code, 1)
        self.app.add_user_to_room(created_room2_code, 1)

        self.assertEqual(
            self.app.get_user_rooms(1),
            [
                {"code": created_room1_code, "name": "room1", "last_message": None},
                {"code": created_room2_code, "name": "room2", "last_message": None},
            ],
        )


class TestAppSearch(unittest.TestCase):
    """Test the App class search methods."""

    @classmethod
    def setUpClass(self):
        self.db_client = keydb.KeyDB(
            host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
        )

    def setUp(self):
        self.db_client.flushall()
        self.app = App(self.db_client)

    def test_basic_search_in_messages(self):
        self.app.add_message_to_room("room1", 1, "Some message")
        self.app.add_message_to_room("room1", 2, "Some different message")
        self.app.add_message_to_room("room1", 3, "Totally different message")

        self.assertEqual(len(self.app.search_prefix_in_room("room1", "message")), 3)
        self.assertEqual(len(self.app.search_prefix_in_room("room1", "different")), 2)

    def test_search_word_in_room(self):
        self.app.add_message_to_room("room1", 1, "Some message")
        self.app.add_message_to_room("room1", 2, "Some different message")
        self.app.add_message_to_room("room1", 3, "Totally different message")

        self.assertEqual(len(self.app.search_word_in_room("room1", "message")), 3)
        self.assertEqual(len(self.app.search_word_in_room("room1", "different")), 2)

    def test_search_word_globally(self):
        created_room1_code = self.app.create_room(1, "room1")
        created_room2_code = self.app.create_room(1, "room2")

        self.app.add_message_to_room(created_room1_code, 1, "some message in room1")
        self.app.add_message_to_room(created_room2_code, 1, "some message in room2")
        self.app.add_message_to_room(created_room1_code, 1, "different message")

        self.assertEqual(len(self.app.search_word_globally(1, "message")), 3)
        self.assertEqual(len(self.app.search_word_globally(1, "different")), 1)
        self.assertEqual(len(self.app.search_word_globally(1, "some")), 2)


if __name__ == "__main__":
    unittest.main()
