import redis
import random
from datetime import datetime
from faker import Faker


redis_client = redis.Redis(host="localhost", port=6379, db=0)


def generate_data(num_users=10, num_rooms=2, num_messages_per_room=100):
    """Generate data for chat app - uses redis to store data
    generate 100 users with faker
    generate 2 rooms with faker
    generate 1000 messages with faker
    """
    fake = Faker()

    # Generate users
    users = {}
    for i in range(num_users):
        user_id = i + 1
        username = fake.user_name()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        user = {
            "id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }
        users[user_id] = user

        # Save user to Redis
        redis_client.hset(f"user:{user_id}", mapping=user)

    # Generate rooms
    room_codes = ["room" + str(i) for i in range(1, num_rooms + 1)]
    rooms = {}
    for i in range(num_rooms):
        room_code = room_codes[i]
        room_users = random.sample(
            range(1, num_users + 1), 10
        )  # select 10 random users for this room
        room = {"code": room_code, "users": room_users}
        rooms[room_code] = room

        # Save room to Redis
        redis_client.sadd(f"room:{room_code}:users", *room_users)

    # Generate messages for each room
    for room_code, room in rooms.items():
        for i in range(num_messages_per_room):
            sender_id = random.choice(room["users"])
            message_id = redis_client.incr("next_message_id")
            message = {
                "sender_id": sender_id,
                "text": fake.text(),
                "timestamp": datetime.timestamp(datetime.now()),
                "id": message_id,
            }

            redis_client.zadd(
                f"room:{room_code}:messages", {message_id: message["timestamp"]}
            )
            redis_client.hset(f"messages:{message['id']}", mapping=message)

    # Close Redis connection
    redis_client.close()


if __name__ == "__main__":
    redis_client.flushall()
    generate_data(100, 2, 5000)
