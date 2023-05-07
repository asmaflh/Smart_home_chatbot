import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import threading
import websocket
import time


def on_message(ws, message):
    print("Received: ", message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("WebSocket closed")


def on_open(ws):
    def run(*args):
        while True:
            msg = ""

            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

            with open('intents.json', 'r') as json_data:
                intents = json.load(json_data)

            FILE = "data.pth"
            data = torch.load(FILE)

            input_size = data["input_size"]
            hidden_size = data["hidden_size"]
            output_size = data["output_size"]
            all_words = data['all_words']
            tags = data['tags']
            model_state = data["model_state"]

            model = NeuralNet(input_size, hidden_size, output_size).to(device)
            model.load_state_dict(model_state)
            model.eval()

            bot_name = "Home"
            print("Let's chat! (type 'quit' to exit)")
            while True:

                sentence = input("You: ")
                if sentence == "quit":
                    break

                sentence = tokenize(sentence)
                X = bag_of_words(sentence, all_words)
                X = X.reshape(1, X.shape[0])
                X = torch.from_numpy(X).to(device)

                output = model(X)
                _, predicted = torch.max(output, dim=1)

                tag = tags[predicted.item()]

                probs = torch.softmax(output, dim=1)
                prob = probs[0][predicted.item()]
                if prob.item() > 0.7:
                    for intent in intents['intents']:
                        if tag == intent["tag"]:
                            print(f"{bot_name}: {random.choice(intent['responses'])}")
                            # dispaly date and time
                            if tag == 'datetime':
                                print(time.strftime("%A"))
                                print(time.strftime("%D %B %Y"))
                                print(time.strftime("%H:%M:%S"))
                            msg = tag
                            ws.send(msg)
                            time.sleep(1)

                else:
                    print(f"{bot_name}: I do not understand...")

            if msg == "quit":
                break

    # start a new thread to keep the WebSocket connection alive
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()


websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://192.168.0.164:81/",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open
ws.run_forever()
