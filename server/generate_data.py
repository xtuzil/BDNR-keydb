from datetime import datetime
import random
import uuid
from faker import Faker


def generate_data(redis_client, num_users=10, num_rooms=2, num_messages_per_room=100):
    """Generate data for chat app - uses redis to store data
    generate num_users users with faker
    generate num_rooms rooms with faker
    generate num_messages_per_room messages with faker
    """
    fake = Faker()

    # Generate users
    users = {}
    for _ in range(num_users):
        username = fake.user_name()
        print(username)
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        user = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }
        users[username] = user

        # Save user to Redis
        redis_client.hset(f"user:{username}", mapping=user)

    # Generate rooms
    room_names = ["room" + str(i) for i in range(1, num_rooms + 1)]
    rooms = {}
    for i in range(num_rooms):
        room_name = room_names[i]
        room_code = uuid.uuid4().hex[:6].upper()
        room_users = random.choices(
            list(users.keys()), k=4
        )  # select 4 random users for this room
        room = {"code": room_code, "users": room_users}
        rooms[room_code] = room

        # Save room to Redis
        redis_client.hset(f"room:{room_code}", "name", room_name)
        redis_client.sadd(f"room:{room_code}:users", *room_users)

        # Add room to each user's list of rooms
        for username in room_users:
            redis_client.sadd(f"user:{username}:rooms", room_code)

    # Generate messages for each room
    for room_code, room in rooms.items():
        for i in range(num_messages_per_room):
            author = random.choice(room["users"])
            message_id = redis_client.incr("next_message_id")
            message = {
                "author": author,
                "text": fake.text(),
                "timestamp": datetime.timestamp(datetime.now()),
                "id": message_id,
            }

            redis_client.zadd(
                f"room:{room_code}:messages", {message_id: message["timestamp"]}
            )
            redis_client.hset(f"message:{message['id']}", mapping=message)

            """Index message text for search"""
            for token in message["text"].split(" "):
                redis_client.sadd(f"{room_code}:word_index:{token}", message_id)

    # Close Redis connection
    redis_client.close()
