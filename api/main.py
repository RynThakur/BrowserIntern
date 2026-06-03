import json
import threading
import queue
import sys
import os
import asyncio

from dotenv import load_dotenv

# Load .env BEFORE importing agent
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from agent import run_agent


app = FastAPI(title="Browsing Intern")


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.websocket("/ws/run")
async def ws_run(websocket: WebSocket):

    await websocket.accept()

    try:

        data = await websocket.receive_json()

        task = data.get("task", "").strip()
        headless = data.get("headless", True)

        if not task:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "result": "No Task Provided."
                    }
                )
            )
            await websocket.close()
            return

        q: queue.Queue = queue.Queue()

        def run_in_thread():

            try:

                for event in run_agent(
                    task,
                    headless=headless
                ):

                    q.put(event)

            except Exception as e:

                q.put(
                    {
                        "type": "error",
                        "result": str(e)
                    }
                )

            finally:

                q.put(None)

        thread = threading.Thread(
            target=run_in_thread,
            daemon=True
        )

        thread.start()

        loop = asyncio.get_running_loop()

        while True:

            event = await loop.run_in_executor(
                None,
                q.get
            )

            if event is None:
                break

            await websocket.send_text(
                json.dumps(event)
            )

            if event.get("type") in (
                "done",
                "error"
            ):
                break

    except WebSocketDisconnect:

        pass

    finally:

        try:
            await websocket.close()
        except:
            pass