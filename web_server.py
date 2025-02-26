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

    async def accept_message(self, request: Request):
        mac_adress = request.query_params.get("mac") # mac adresa zarizeni
        print(mac_adress)
        btn = request.query_params.get("button") # cislo buttonu ktery zmackl
        await self.server.connect_and_send_message(mac_adress, btn)
        print(btn)
        
        return {"message": "Zprava odeslana uspesne"}

    def run(self, host="0.0.0.0", port=8000):
        print(f"Starting server on {host}:{port}")
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

    def stop(self):
        self.shutdown_event.set()
        self.server_thread.join()