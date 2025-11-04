import json
import time


def init_general_room(redis_client):
    """Initialize the General room with default messages"""
    # Set the General room name
    redis_client.set("room:0:name", "General")

    # Add welcome messages to General room
    welcome_messages = [
        {
            "from": "1",
            "date": int(time.time() * 1000),
            "message": "Welcome to the General room!",
            "roomId": "0",
        },
        {
            "from": "2",
            "date": int(time.time() * 1000) + 1000,
            "message": "Feel free to chat with everyone here!",
            "roomId": "0",
        },
    ]

    for msg in welcome_messages:
        redis_client.zadd("room:0", {json.dumps(msg): int(msg["date"])})


def init_private_rooms(redis_client):
    """Initialize private rooms between demo users"""
    # Create private room pairs (1-2, 2-3, 3-4)
    room_pairs = [(1, 2), (2, 3), (3, 4)]

    for user1, user2 in room_pairs:
        room_id = f"{user1}:{user2}"

        # Add room to both users
        redis_client.sadd(f"user:{user1}:rooms", room_id)
        redis_client.sadd(f"user:{user2}:rooms", room_id)

        # Add initial message
        message = {
            "from": str(user1),
            "date": int(time.time() * 1000),
            "message": "Hey! Let's chat!",
            "roomId": room_id,
        }
        redis_client.zadd(
            f"room:{room_id}", {json.dumps(message): int(message["date"])}
        )


def ensure_general_room_membership(redis_client):
    """Ensure all users are members of the General room"""
    total_users = int(redis_client.get("total_users") or 0)
    for user_id in range(1, total_users + 1):
        redis_client.sadd(f"user:{user_id}:rooms", "0")


def initialize_redis(redis_client):
    """Main initialization function"""
    try:
        # Check if initialization is needed
        if redis_client.exists("room:0:name"):
            print("Redis already initialized, skipping...")
            return True

        print("Starting Redis initialization...")

        # Initialize General room
        init_general_room(redis_client)
        print("General room initialized")

        # Wait for demo users to be created (they should be created by demo_data.py)
        max_retries = 5
        for i in range(max_retries):
            if redis_client.exists("total_users"):
                break
            print(f"Waiting for users to be created (attempt {i + 1}/{max_retries})...")
            time.sleep(1)

        # Initialize private rooms
        init_private_rooms(redis_client)
        print("Private rooms initialized")

        # Ensure all users are in General room
        ensure_general_room_membership(redis_client)
        print("User room membership configured")

        print("Redis initialization completed successfully")
        return True

    except Exception as e:
        print(f"Error during Redis initialization: {str(e)}")
        return False
