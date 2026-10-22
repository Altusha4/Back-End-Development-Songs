"""Songs API backed by MongoDB; seed records are inserted only when absent."""
import os
import json
from pathlib import Path
from urllib.parse import quote_plus
from flask import request
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import json_util
from . import app

host = os.getenv("MONGODB_SERVICE", "127.0.0.1")
port = os.getenv("MONGODB_PORT", "27017")
username = os.getenv("MONGODB_USERNAME")
password = os.getenv("MONGODB_PASSWORD")
auth = f"{quote_plus(username)}:{quote_plus(password)}@" if username and password else ""
client = MongoClient(os.getenv("MONGODB_URI", f"mongodb://{auth}{host}:{port}"), serverSelectionTimeoutMS=5000)
db = client[os.getenv("MONGODB_DATABASE", "songs")]
db.songs.create_index("id", unique=True)
if db.songs.count_documents({}) == 0:
    for song in json.loads((Path(__file__).parent / "data/songs.json").read_text()):
        db.songs.update_one({"id": song["id"]}, {"$setOnInsert": song}, upsert=True)

def parse_json(value):
    return json.loads(json_util.dumps(value))

@app.get("/health")
def health():
    client.admin.command("ping")
    return {"status": "OK"}, 200

@app.get("/count")
def count():
    return {"count": db.songs.count_documents({})}, 200

@app.get("/song")
def songs():
    return {"songs": parse_json(list(db.songs.find({}).sort("id", 1)))}, 200

@app.get("/song/<int:id>")
def get_song_by_id(id):
    song = db.songs.find_one({"id": id})
    return (parse_json(song), 200) if song else ({"message": f"song with id {id} not found"}, 404)

@app.post("/song")
def create_song():
    song = request.get_json(silent=True)
    if not isinstance(song, dict) or type(song.get("id")) is not int or not all(isinstance(song.get(k),str) for k in ("title","lyrics")):
        return {"message": "integer id, title and lyrics required"}, 400
    song = {k: song[k] for k in ("id", "title", "lyrics")}
    try:
        result = db.songs.insert_one(song)
    except DuplicateKeyError:
        return {"Message": f"song with id {song['id']} already present"}, 302
    return {"inserted id": parse_json(result.inserted_id)}, 201

@app.put("/song/<int:id>")
def update_song(id):
    if db.songs.find_one({"id": id}) is None:
        return {"message": "song not found"}, 404
    song = request.get_json(silent=True)
    if not isinstance(song, dict) or song.get("id", id) != id:
        return {"message": "JSON object with matching id required"}, 400
    changes = {k: song[k] for k in ("title", "lyrics") if k in song}
    if not changes or not all(isinstance(v,str) for v in changes.values()):
        return {"message": "title or lyrics must be text"}, 400
    result = db.songs.update_one({"id":id}, {"$set":changes})
    if not result.modified_count:
        return {"message":"song found, but nothing updated"}, 200
    return parse_json(db.songs.find_one({"id":id})), 201

@app.delete("/song/<int:id>")
def delete_song(id):
    if not db.songs.delete_one({"id": id}).deleted_count:
        return {"message": "song not found"}, 404
    return "", 204
