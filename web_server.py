import datetime
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
        """
        Logs events with timestamps to a log file.
        :param event: The event description to log.
        """
        try:
            with open(self.LOG_FILE, "a") as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} - {event}\n")
        except FileNotFoundError:
            os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
            with open(self.LOG_FILE, "a") as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} - {event}\n")

    async def accept_message(self, request: Request):
        mac_adress = request.query_params.get("mac") # mac adresa zarizeni
        self.log_event(mac_adress)
        btn = request.query_params.get("button") # cislo buttonu ktery zmackl
        await self.server.connect_and_send_message(mac_adress, btn)
        self.log_event(btn)
        
        return {"message": "Zprava odeslana uspesne"}

    def run(self, host="0.0.0.0", port=8000):
        self.log_event(f"Starting server on {host}:{port}")
        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server.serve())
        while not self.shutdown_event.is_set():
            loop.run_until_complete(asyncio.sleep(1))

    def start_in_thread(self, host="0.0.0.0", port=8000):
        self.server_thread = threading.Thread(target=self.run, args=(host, port))
        self.server_thread.start()
        self.log_event("Server started in thread")

    def stop(self):
        self.shutdown_event.set()
        self.server_thread.join()
        self.log_event("Server stopped")