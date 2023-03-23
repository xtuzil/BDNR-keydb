from datetime import datetime
import redis

from generate_data import generate_data


class App:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def get_all_messages_for_room(self, room_code, page=1, page_size=10):
        """Get all messages for a room"""
        start = (page - 1) * 10
        end = start + page_size - 1
        message_ids = self.redis_client.zrevrange(
            f"room:{room_code}:messages", start, end
        )
        return [self.get_message(message_id) for message_id in message_ids]

    def get_message(self, message_id):
        """Get a message by id"""
        return self.redis_client.hgetall(f"messages:{message_id}")

    def get_all_user_rooms(self, user_id):
        """Get all rooms for a user"""
        return self.redis_client.smembers(f"user:{user_id}:rooms")

    def get_room_members(self, room_code):
        """Get all members for a room"""
        return self.redis_client.smembers(f"room:{room_code}:users")

    def add_message_to_room(self, room_code, sender_id, text):
        """Add a message to a room"""
        message_id = self.redis_client.incr("next_message_id")
        message = {
            "id": message_id,
            "sender_id": sender_id,
            "timestamp": datetime.timestamp(datetime.now()),
            "text": text,
        }
        # store message itself
        self.redis_client.hset(f"messages:{message_id}", mapping=message)

        # store message in room
        self.redis_client.zadd(
            f"room:{room_code}:messages", {message_id: message["timestamp"]}
        )

        self.index_message_text(room_code, message_id, text)
        return message

    def search_in_messages(self, room_code, text):
        """Search for a text in messages of a room
        Only basic with case sensitivity"""
        message_ids = self.redis_client.zrevrange(f"room:{room_code}:messages", 0, -1)
        messages = [self.get_message(message_id) for message_id in message_ids]
        return [message for message in messages if text in message["text"]]

    def index_search_in_room(self, room_code, word):
        """Search for a word in messages of a room"""
        message_ids = self.redis_client.smembers(f"{room_code}:word_index:{word}")
        messages = [self.get_message(message_id) for message_id in message_ids]
        return [message for message in messages]

    def global_index_search(self, user_id, word):
        """Search for a word in all messages"""

        # get all rooms for user
        rooms = self.get_all_user_rooms(user_id)

        # get all messages for all rooms
        message_ids = []
        for room in rooms:
            print(room)
            message_ids.extend(self.redis_client.smembers(f"{room}:word_index:{word}"))

        # get all messages
        messages = [self.get_message(message_id) for message_id in message_ids]
        return [message for message in messages]

    def index_message_text(self, room_code, message_id, message_text):
        """Index message text for search"""
        for token in message_text.split(" "):
            self.redis_client.sadd(f"{room_code}:word_index:{token}", message_id)

    def add_user_to_room(self, room_code, user_id):
        """Add a user to a room"""
        self.redis_client.sadd(f"room:{room_code}:users", user_id)
        self.redis_client.sadd(f"user:{user_id}:rooms", room_code)


def test_search(redis_client):
    app = App(redis_client)
    app.add_message_to_room("room1", 1, "Nesmysl to je s vice slovy")
    app.add_message_to_room("room1", 2, "Some different text")
    app.add_message_to_room("room1", 3, "Tottally different message")
    app.add_message_to_room("room2", 1, "Nesmysl to je s vice slovy")

    app.add_user_to_room("room2", 1)

    print(app.get_room_members("room2"))

    print("1:", app.index_search_in_room("room1", "je"))
    print("2:", app.global_index_search(1, "je"))


if __name__ == "__main__":
    redis_client = redis.Redis(
        host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True
    )
    # redis_client.flushall()
    # generate_data(redis_client, 10, 2, 5000)

    app = App(redis_client)
    test_search(redis_client)
    # print(app.get_all_messages_for_room("room1", 1, 10))
    # app.add_message_to_room("room1", 1, "Nesmysl")
    # print(app.get_all_messages_for_room("room1", 1, 10))

    # search_in_messages = app.search_in_messages("room1", "nesmysl")

    # print(search_in_messages)
