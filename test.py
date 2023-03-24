import datetime
import unittest
import redis

from server.app import App
from server.generate_data import generate_data

# test redis client
class TestRedisClient(unittest.TestCase):
    """Test the redis client."""
    def setUp(self):
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
        )
        self.redis_client.flushall()

    def test_redis_client(self):
        self.redis_client.set("test", "test")
        self.assertEqual(self.redis_client.get("test"), "test")

class TestAppRooms(unittest.TestCase):
    """Test the App class room methods."""
    @classmethod
    def setUpClass(self):
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
        )

    def setUp(self):
        self.redis_client.flushall()
        self.app = App(self.redis_client)

    def test_add_user_to_room(self):
        self.app.add_user_to_room("room1", 1)

        # check if user is added to the room
        self.assertEqual(self.redis_client.scard(f"room:room1:users"), 1)
        self.assertEqual(self.redis_client.sismember(f"room:room1:users", 1), 1)
        # check if room is added to the user
        self.assertEqual(self.redis_client.scard(f"user:1:rooms"), 1)
        self.assertEqual(self.redis_client.sismember(f"user:1:rooms", "room1"), 1)


    def test_create_room(self):
        self.app.create_room(1, "room1", "room1")

        self.assertEqual(self.redis_client.hget(f"room:room1", "name"), "room1")

    def test_get_room_members(self):
        self.app.add_user_to_room("room1", 1)
        self.app.add_user_to_room("room1", 2)

        self.assertEqual(self.app.get_room_members("room1"), {'1', '2'})

    def test_get_user_rooms(self):
        self.app.add_user_to_room("room1", 1)
        self.app.add_user_to_room("room2", 1)

        self.assertEqual(self.app.get_user_rooms(1), {'room1', 'room2'})

 
class TestAppSearch(unittest.TestCase):
    """Test the App class search methods."""
    @classmethod
    def setUpClass(self):
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
        )

    def setUp(self):
        self.redis_client.flushall()
        self.app = App(self.redis_client)

    def test_basic_search_in_messages(self):
        self.app.add_message_to_room("room1", 1, "Some message")
        self.app.add_message_to_room("room1", 2, "Some different message")
        self.app.add_message_to_room("room1", 3, "Totally different message")

        self.assertEqual(len(self.app.basic_search_in_messages("room1", "message")), 3)
        self.assertEqual(len(self.app.basic_search_in_messages("room1", "different")), 2)
        # self.assertEqual(len(self.app.basic_search_in_messages("room1", "totally")), 1)

    def test_search_word_in_room(self):
        self.app.add_message_to_room("room1", 1, "Some message")
        self.app.add_message_to_room("room1", 2, "Some different message")
        self.app.add_message_to_room("room1", 3, "Totally different message")

        self.assertEqual(len(self.app.search_word_in_room("room1", "message")), 3)
        self.assertEqual(len(self.app.search_word_in_room("room1", "different")), 2)
        # self.assertEqual(len(self.app.search_word_in_room("room1", "totally")), 1)

    def test_search_word_globally(self):
        self.app.add_user_to_room("room1", 1)
        self.app.add_user_to_room("room2", 1)

        self.app.add_message_to_room("room1", 1, "some message in room1")
        self.app.add_message_to_room("room2", 1, "some message in room2")
        self.app.add_message_to_room("room1", 1, "different message")
        

        self.assertEqual(len(self.app.search_word_globally(1, "message")), 3)
        self.assertEqual(len(self.app.search_word_globally(1, "different")), 1)
        self.assertEqual(len(self.app.search_word_globally(1, "some")), 2)


if __name__ == '__main__': 
    unittest.main()
