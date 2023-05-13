import argparse
from datetime import datetime
import keydb
import uuid
import re

from generate_data import generate_data

get_datetime_from_timestamp = lambda timestamp: datetime.fromtimestamp(
    timestamp
).strftime("%Y-%m-%d %H:%M:%S")


class App:
    def __init__(self, keydb_client):
        self.keydb_client = keydb_client
        # self.pub_sub = self.keydb_client.pubsub()

    def get_room_messages(self, room_code):
        """Get all messages for a room"""
        # start = (page - 1) * 10
        # end = start + page_size - 1
        message_ids = self.keydb_client.zrevrange(f"room:{room_code}:messages", 0, -1)
        return [self.get_message(message_id) for message_id in message_ids]

    def get_message(self, message_id):
        """Get a message by id"""
        message = self.keydb_client.hgetall(f"message:{message_id}")
        return {
            "id": message_id,
            "author": message["author"],
            "timestamp": get_datetime_from_timestamp(float(message["timestamp"])),
            "text": message["text"],
        }

    def get_last_message(self, room_code):
        """Get last message in room"""
        message_id = self.keydb_client.zrevrange(f"room:{room_code}:messages", 0, 0)
        if message_id:
            return self.get_message(message_id[0])
        return None

    def get_user_rooms(self, user_id):
        """Get all rooms for a user"""
        room_codes = self.keydb_client.smembers(f"user:{user_id}:rooms")
        return [self.get_room(room_code) for room_code in room_codes]

    def get_room_members(self, room_code):
        """Get all members for a room"""
        return self.keydb_client.smembers(f"room:{room_code}:users")

    def add_message_to_room(self, room_code, author, text):
        """Add a message to a room"""
        message_id = self.keydb_client.incr("next_message_id")
        message = {
            "id": message_id,
            "author": author,
            "timestamp": datetime.timestamp(datetime.now()),
            "text": text,
        }
        # store message itself
        self.keydb_client.hset(f"message:{message_id}", mapping=message)

        # store message in room
        self.keydb_client.zadd(
            f"room:{room_code}:messages", {message_id: message["timestamp"]}
        )

        self.index_message_text(room_code, message_id, text)
        return message

    # def basic_search_in_messages(self, room_code, word):
    #     """Search for a word in messages of a room
    #     Only basic with case sensitivity"""
    #     message_ids = self.keydb_client.zrevrange(f"room:{room_code}:messages", 0, -1)
    #     messages = [self.get_message(message_id) for message_id in message_ids]
    #     return [message for message in messages if word in message["text"]]

    def search_word_in_room(self, room_code, word):
        """Search for a word in messages of a room"""
        message_ids = self.keydb_client.smembers(f"room:{room_code}:word_index:{word}")
        messages = [self.get_message(message_id) for message_id in message_ids]
        return [message for message in messages]

    def search_prefix_in_room(self, room_code, word):
        """Search for a word in messages of a room"""
        keys = self.keydb_client.keys(f"room:{room_code}:word_index:{word}*")
        message_ids = []
        for key in keys:
            message_ids.extend(self.keydb_client.smembers(key))
        messages = [self.get_message(message_id) for message_id in message_ids]

        return sorted(
            messages,
            key=lambda x: datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S"),
            reverse=True,
        )

    def search_word_globally(self, username, word):
        """Search for a word in all messages"""

        # get all rooms for user
        rooms = self.get_user_rooms(username)

        # get all messages for all rooms
        message_ids = []
        for room in rooms:
            room_code = room["code"]
            message_ids.extend(
                self.keydb_client.smembers(f"room:{room_code}:word_index:{word}")
            )

        # get all messages
        messages = [self.get_message(message_id) for message_id in message_ids]
        return sorted(
            messages,
            key=lambda x: datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S"),
            reverse=True,
        )

    def index_message_text(self, room_code, message_id, message_text):
        """Index message text for search"""
        for token in re.findall(r"[\w']+", message_text):
            self.keydb_client.sadd(
                f"room:{room_code}:word_index:{token.lower()}", message_id
            )

    def add_user_to_room(self, room_code, username) -> tuple[bool, str]:
        """Add a user to a room"""

        # check for room existence
        if not self.keydb_client.exists(f"room:{room_code}"):
            return False, f"Room with code {room_code} does not exist"

        self.keydb_client.sadd(f"room:{room_code}:users", username)
        self.keydb_client.sadd(f"user:{username}:rooms", room_code)

        return True, ""

    # TODO: check for room existence
    def remove_user_from_room(self, room_code, user_id):
        """Remove a user from a room"""
        self.keydb_client.srem(f"room:{room_code}:users", user_id)
        self.keydb_client.srem(f"user:{user_id}:rooms", room_code)

    def get_room(self, room_code):
        """Get a room by code"""
        room = self.keydb_client.hgetall(f"room:{room_code}")
        last_message = self.get_last_message(room_code)
        return {
            "code": room_code,
            "name": room["name"],
            "last_message": last_message,
            # "members": self.get_room_members(room_code),
        }

    def create_room(self, username, room_name) -> str:
        """Create a room with user"""
        room_code = uuid.uuid4().hex[:6].upper()
        self.keydb_client.hset(f"room:{room_code}", "name", room_name)
        self.add_user_to_room(room_code, username)
        return room_code

    def subscribe_to_room(self, room_code):
        """Subscribe to a room"""
        self.pub_sub.subscribe(room_code)
        for message in self.pub_sub.listen():
            print(message)

    def unsubscribe_from_room(self, room_code):
        """Unsubscribe from a room"""
        self.pub_sub.unsubscribe(room_code)

    def publish_to_room(self, room_code, message):
        """Publish a message to a room"""
        self.keydb_client.publish(room_code, message)

    def init_data(self):
        generate_data(self.keydb_client, 6, 2, 1000)

    def get_all_user_keys(self):
        """Get all user keys"""
        return self.keydb_client.keys("user:*")


if __name__ == "__main__":
    keydb_client = keydb.KeyDB(
        host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
    )
    keydb_client.flushall()

    app = App(keydb_client)
    app.init_data()

    # res = app.search_prefix_in_room("D7F0B7", "mess")
    # print(res)

    # parser = argparse.ArgumentParser()
    # parser.add_argument("-s", "--sub", help="subscribe to room")
    # parser.add_argument("-p", "--pub", help="publish to room")

    # args = parser.parse_args()
    # if args.sub:
    #     app.subscribe_to_room(args.sub)
    # elif args.pub:
    #     while True:
    #         message = input("Enter message: ")
    #         app.publish_to_room(args.pub, message)
