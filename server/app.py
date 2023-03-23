from datetime import datetime
import redis

from generate_data import generate_data

from redisearch import Client, TextField, NumericField, IndexDefinition


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
        return self.redis_client.hgetall(f"message:{message_id}")

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
        self.redis_client.hset(f"message:{message_id}", mapping=message)
        self.redis_client.zadd(
            f"room:{room_code}:messages", {message_id: message["timestamp"]}
        )
        return message


if __name__ == "__main__":
    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    redis_client.flushall()
    generate_data(redis_client, 10, 2, 5000)

    app = App(redis_client)

    # client = Client("messages", conn=redis_client)

    # # IndexDefinition is available for RediSearch 2.0+
    # definition = IndexDefinition(prefix="messages:")

    # # Creating the index definition and schema
    # try:
    #     client.create_index((TextField("text")), definition=definition)
    # except:
    #     pass

    # res = client.search("art")
    # print(res.total)
    # print(res.docs)
