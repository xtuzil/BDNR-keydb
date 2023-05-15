import datetime
import json
from typing import Optional
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import keydb
from sse_starlette.sse import EventSourceResponse

from fastapi.middleware.cors import CORSMiddleware

from api import App

HOST = "keydb"

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


r = keydb.KeyDB(host=HOST, port=6379, db=0, encoding="utf-8", decode_responses=True)

api = App(r)


@app.get("/")
async def root():
    return {"message": "Hello World"}


class Message(BaseModel):
    author: str
    text: str


@app.post("/rooms/{room_code}/messages", status_code=204)
async def publish_message(room_code: str, message: Message):
    """Publish message to a room"""
    api.add_message_to_room(room_code, message.author, message.text)

    now = datetime.datetime.now()
    message_json = json.dumps(
        {
            "author": message.author,
            "text": message.text,
            "time": now.isoformat(),
            "room_code": room_code,
        }
    )
    r.publish("chat", message_json)


class NewRoom(BaseModel):
    author: str
    name: str


@app.post("/rooms", status_code=200)
async def create_room(room: NewRoom):
    """Create a room"""
    room_code = api.create_room(room.author, room.name)
    return {"room_code": room_code}


class JoinRoom(BaseModel):
    user: str
    room_code: str


@app.post("/rooms/register")
async def register_to_room(room: JoinRoom):
    """register to a room"""
    status, message = api.add_user_to_room(room.room_code, room.user)
    if not status:
        raise HTTPException(status_code=404, detail=message)

    return Response(status_code=204)


class LeaveRoom(BaseModel):
    user: str


@app.post("/rooms/{room_code}/leave")
async def leave_from_room(room_code: str, msg: LeaveRoom):
    """register to a room"""
    try:
        api.remove_user_from_room(room_code, msg.user)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    return Response(status_code=204)


@app.get("/rooms/{room_code}/messages")
async def get_room_messages(room_code: str, q: Optional[str] = None):
    if q:
        print("searching", q)
        return api.search_prefix_in_room(room_code, q.lower())
    return api.get_room_messages(room_code)


@app.get("/users/{username}/rooms/messages")
async def search_globally(username: str, q: Optional[str] = None):
    if q:
        print("searching", q)
        return api.search_word_globally(username, q.lower())
    else:
        return []


@app.get("/users/{username}/rooms")
async def get_user_rooms(username: str):
    return api.get_user_rooms(username)


@app.post("/init")
async def init_data():
    return {"created_rooms": api.init_data()}


@app.get("/stream")
async def message_stream():
    def event_stream():
        pubsub = r.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe("chat")
        for message in pubsub.listen():
            print("message")
            yield message["data"]

    return EventSourceResponse(event_stream())
