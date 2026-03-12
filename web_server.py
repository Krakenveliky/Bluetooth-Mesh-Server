from fastapi import FastAPI, WebSocket
import uvicorn
import threading


class WebServer:

    def __init__(self, ble_server):

        self.ble = ble_server
        self.app = FastAPI()

        self.app.get("/on")(self.power_on)
        self.app.get("/off")(self.power_off)

        self.app.websocket("/ws")(self.websocket)

    def power_on(self):

        self.ble.send("|O@")
        return {"status": "on"}

    def power_off(self):

        self.ble.send("|F@")
        return {"status": "off"}

    async def websocket(self, ws: WebSocket):

        await ws.accept()

        while True:

            cmd = await ws.receive_text()
            self.ble.send(cmd)

    def run(self):

        uvicorn.run(self.app, host="0.0.0.0", port=8000)

    def start_in_thread(self):

        thread = threading.Thread(target=self.run)
        thread.start()