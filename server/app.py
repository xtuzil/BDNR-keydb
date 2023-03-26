import argparse
from datetime import datetime
import redis

class App:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.pub_sub = self.redis_client.pubsub()

    def get_room_messages(self, room_code, page=1, page_size=10):
        """Get all messages for a room"""
        start = (page - 1) * 10
        end = start + page_size - 1
        message_ids = self.redis_client.zrevrange(
            f"room:{room_code}:messages", start, end
        )
        return [self.get_message(message_id) for message_id in message_ids]

    def get_message(self, message_id):
        """Get a message by id"""
        return self.redis_client.hgetall(f"message:{message_id}")

    # TODO: get also last message in room
    def get_user_rooms(self, user_id):
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
        self.redis_client.hset(f"message:{message_id}", mapping=message)

        # store message in room
        self.redis_client.zadd(
            f"room:{room_code}:messages", {message_id: message["timestamp"]}
        )

        self.index_message_text(room_code, message_id, text)
        return message

    def basic_search_in_messages(self, room_code, word):
        """Search for a word in messages of a room
        Only basic with case sensitivity"""
        message_ids = self.redis_client.zrevrange(f"room:{room_code}:messages", 0, -1)
        messages = [self.get_message(message_id) for message_id in message_ids]
        return [message for message in messages if word in message["text"]]

    def search_word_in_room(self, room_code, word):
        """Search for a word in messages of a room"""
        message_ids = self.redis_client.smembers(f"{room_code}:word_index:{word}")
        messages = [self.get_message(message_id) for message_id in message_ids]
        return [message for message in messages]

    def search_word_globally(self, user_id, word):
        """Search for a word in all messages"""

        # get all rooms for user
        rooms = self.get_user_rooms(user_id)

        # get all messages for all rooms
        message_ids = []
        for room in rooms:
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
    
    def remove_user_from_room(self, room_code, user_id):
        """Remove a user from a room"""
        self.redis_client.srem(f"room:{room_code}:users", user_id)
        self.redis_client.srem(f"user:{user_id}:rooms", room_code)

    # TODO: check for existing code
    # (we can generate code and get only name)
    def create_room(self, user_id, room_name, room_code):
        """Create a room with user"""
        self.redis_client.hset(f"room:{room_code}", "name", room_name)
        self.add_user_to_room(room_code, user_id)

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
        self.redis_client.publish(room_code, message)
        


if __name__ == "__main__":
    redis_client = redis.Redis(
        host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
    )
    # redis_client.flushall()
    # generate_data(redis_client, 10, 2, 5000)

    app = App(redis_client)

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sub", help="subscribe to room")
    parser.add_argument("-p", "--pub", help="publish to room")

    args = parser.parse_args()
    if args.sub:
        app.subscribe_to_room(args.sub)
    elif args.pub:
        while True:
            message = input("Enter message: ")
            app.publish_to_room(args.pub, message)
