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
    return PlainTextResponse("pong", status_code=200)

async def send_ping():
    while True:
        if os.path.exists(pause_file):
            print(f"{instance_id} is paused.")
            await asyncio.sleep(1)  # Sleep briefly to avoid busy-waiting
            continue
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(target_url)
                if response.status_code == 200 and response.text == "pong":
                    print(f"{instance_id} received pong from {target_url}")
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")

        await asyncio.sleep(pong_time_ms / 1000.0)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_ping())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
