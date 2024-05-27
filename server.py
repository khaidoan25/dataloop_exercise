# server.py
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import httpx
import asyncio
import os
import uvicorn
import signal

app = FastAPI()

# Get environment variables
instance_id = os.getenv("INSTANCE_ID", "instance1")
target_url = os.getenv("TARGET_URL", "http://localhost:8001/ping")
pong_time_ms = int(os.getenv("PONG_TIME_MS", "1000"))
pause_file = "pause_signal.txt"

@app.get("/ping")
async def ping():
    asyncio.create_task(wait_and_send_ping())
    return PlainTextResponse("pong", status_code=200)

async def wait_and_send_ping():
    while True:
        if not os.path.exists("pause_signal.txt"):
            break
        with open("pause_signal.txt", "r") as f:
            if f.read() == "paused":
                continue
            else:
                break
            
    await asyncio.sleep(pong_time_ms / 1000.0)            
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(target_url)
            if response.status_code == 200 and response.text == "pong":
                print(f"{instance_id} received pong from {target_url}")
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}: {exc}")

@app.on_event("startup")
async def startup_event():
    if instance_id == "instance1":
        asyncio.create_task(wait_and_send_ping())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
