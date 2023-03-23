from datetime import datetime
import random
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
            range(1, num_users + 1), 4
        )  # select 4 random users for this room
        room = {"code": room_code, "users": room_users}
        rooms[room_code] = room

        # Save room to Redis
        redis_client.sadd(f"room:{room_code}:users", *room_users)

        # TODO is this correct?
        # Add room to each user's list of rooms
        for user_id in room_users:
            redis_client.sadd(f"user:{user_id}:rooms", room_code)

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
