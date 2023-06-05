import time
import database
import threading
import websocket
import chat

def Websocket(tag):
    def on_message(ws, message):
        print("Received from Wemos:", message)
        print("the currentid", database.currentId)
        chat.tel_send_message(database.currentId, message)

        return message

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("WebSocket closed")

    def on_open(ws):
        ws.send(tag)
        time.sleep(1)
        print("WebSocket connection established")

    ws = websocket.WebSocketApp(f'ws://{database.ip_adress}:{database.port}/',
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open

    def wemos_connection_thread():
        websocket.enableTrace(True)
        ws.run_forever()

    wemos_thread = threading.Thread(target=wemos_connection_thread)
    wemos_thread.daemon = True
    wemos_thread.start()
