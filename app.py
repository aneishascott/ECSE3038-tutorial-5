from email import message
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


@app.get("/devices")
def get_devices():
    return list(devices.find({}, {"_id": 0}))

@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0 })
    if device is None:
        raise HTTPException(status_code = 404, detail="Device with name " +name+ " does not exist")
    return device

@app.post("/devices", status_code = 201)
def create_device(device: Device):
    for existing_device in devices.find({}, {"_id": 0}):
        if existing_device["name"] == device.name:
            raise HTTPException(status_code = 409, detail="Device with name " +device.name+ " already exists")
    new_device = device.model_dump()
    devices.insert_one(new_device)
    new_device.pop("_id")
    return new_device

@app.put("/devices/{name}")
def update_device(name: str, device: Device):
    existing_device = devices.find_one({"name": name})
    if existing_device is None:
        new_device = device.model_dump()
        devices.insert_one(new_device)
        new_device.pop("_id", None)
        return JSONResponse(status_code=201, content=new_device)
    updated_device = device.model_dump()
    devices.update_one({"name": name}, {"$set": updated_device})
    updated_device.pop("_id", None)
    return updated_device