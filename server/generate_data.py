from datetime import datetime
import random
import uuid
from faker import Faker
import re


def generate_data(keydb_client, num_users=10, num_rooms=2, num_messages_per_room=100):
    """Generate data for chat app - uses keydb to store data
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

        # Save user to KeyDB
        keydb_client.hset(f"user:{username}", mapping=user)

    # Generate rooms
    room_names = ["room" + str(i) for i in range(1, num_rooms + 1)]
    rooms = {}
    response_rooms = []
    for i in range(num_rooms):
        room_name = room_names[i]
        room_code = uuid.uuid4().hex[:6].upper()
        room_users = random.choices(
            list(users.keys()), k=4
        )  # select 4 random users for this room
        room = {"code": room_code, "users": room_users}
        rooms[room_code] = room
        response_rooms.append({room_code: room_users})

        # Save room to KeyDB
        keydb_client.hset(f"room:{room_code}", "name", room_name)
        keydb_client.sadd(f"room:{room_code}:users", *room_users)

        # Add room to each user's list of rooms
        for username in room_users:
            keydb_client.sadd(f"user:{username}:rooms", room_code)

    # Generate messages for each room
    for room_code, room in rooms.items():
        for i in range(num_messages_per_room):
            author = random.choice(room["users"])
            message_id = keydb_client.incr("next_message_id")
            message = {
                "author": author,
                "text": fake.text(max_nb_chars=50),
                "timestamp": datetime.timestamp(fake.date_time_between()),
                "id": message_id,
            }

            keydb_client.zadd(
                f"room:{room_code}:messages", {message_id: message["timestamp"]}
            )
            keydb_client.hset(f"message:{message['id']}", mapping=message)

            """Index message text for search"""
            for token in re.findall(r"[\w']+", message["text"]):
                keydb_client.sadd(
                    f"room:{room_code}:word_index:{token.lower()}", message_id
                )

    # Close KeyDB connection
    keydb_client.close()

    return response_rooms
