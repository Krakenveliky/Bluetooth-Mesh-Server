from datetime import datetime
import os
from fastapi import FastAPI, APIRouter, Request
import uvicorn
import asyncio
import threading


class WebServer:

    def __init__(self, server):

        self.server = server
        self.app = FastAPI()
        self.router = APIRouter()

        self.router.add_api_route("/send", self.accept_message, methods=["GET"])

        self.app.include_router(self.router)

        self.shutdown_event = threading.Event()
        self.LOG_FILE = "log.txt"


    def log_event(self, event):

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(self.LOG_FILE, "a") as f:
            f.write(f"{timestamp} - {event}\n")


    def accept_message(self, request: Request):

        mac = request.query_params.get("mac")
        button = request.query_params.get("button")

        self.log_event(f"HTTP {mac} {button}")

        if mac and button:
            try:
                # call existing BLE server function
                self.server.send(button)

            except Exception as e:
                self.log_event(f"HTTP send error {e}")

        return {"status": "ok"}


    def run(self, host="0.0.0.0", port=8000):

        self.log_event(f"Starting server on {host}:{port}")

        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(server.serve())


    def start_in_thread(self, host="0.0.0.0", port=8000):

        self.server_thread = threading.Thread(
            target=self.run,
            args=(host, port)
        )

        self.server_thread.start()

        self.log_event("Server started in thread")


    def stop(self):

        self.shutdown_event.set()
        self.server_thread.join()

        self.log_event("Server stopped")