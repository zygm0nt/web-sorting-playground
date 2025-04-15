from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get():
    with open("static/index.html") as f:
        return HTMLResponse(f.read())

async def bubble_sort(data, websocket: WebSocket):
    n = len(data)
    for i in range(n):
        for j in range(0, n - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                await websocket.send_json(data)
                await asyncio.sleep(0.05)
    return data

async def quick_sort(data, websocket: WebSocket, low=0, high=None):
    if high is None:
        high = len(data) - 1

    async def partition(low, high):
        pivot = data[high]
        i = low - 1
        for j in range(low, high):
            if data[j] < pivot:
                i += 1
                data[i], data[j] = data[j], data[i]
                await websocket.send_json(data)
                await asyncio.sleep(0.05)
        data[i + 1], data[high] = data[high], data[i + 1]
        await websocket.send_json(data)
        await asyncio.sleep(0.05)
        return i + 1

    if low < high:
        pi = await partition(low, high)
        await quick_sort(data, websocket, low, pi - 1)
        await quick_sort(data, websocket, pi + 1, high)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        message = await websocket.receive_json()
        algorithm = message.get("algorithm", "bubble")
        data = [random.randint(5, 100) for _ in range(50)]
        await websocket.send_json(data)
        if algorithm == "bubble":
            await bubble_sort(data, websocket)
        elif algorithm == "quick":
            await quick_sort(data, websocket)
        await websocket.send_json({"done": True})
    except WebSocketDisconnect:
        print("Client disconnected")
