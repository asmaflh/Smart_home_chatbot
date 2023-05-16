from flask import Flask
from flask import request
from flask import Response
import requests
import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import threading
import websocket
import time
from translate import Translator
from lingua import Language, LanguageDetectorBuilder
import speech_recognition as sr


def on_message(ws, message):
    print("Received from Wemos:", message)
    tel_send_message(1668424135,message)
    return message
    # Process the received message from the Wemos device and send a response to Telegram


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("WebSocket closed")


def on_open(ws):
    print("WebSocket connection established")


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

TOKEN = "6114189098:AAEpUkeH4t7ZONXzgnty6WBlr7EonrkUn1M"
app = Flask(__name__)


def parse_message(message):
    print("message-->", message)
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id, txt


def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    r = requests.post(url, json=payload)
    return r
ws = websocket.WebSocketApp("ws://192.168.0.164:81/",
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
ws.on_open = on_open

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, txt = parse_message(msg)
        """
           # Initialize recognizer class (for recognizing the speech)
           r = sr.Recognizer()
           # Reading Microphone as source
           # listening the speech and store in audio_text variable
           with sr.Microphone() as source:
               print("Talk")
               audio_text = r.listen(source)
               print("Time over, thanks")
               # recoginize_() method will throw a request error if the API is unreachable, hence using exception handling
               try:
                   # using google speech recognition
                   sentence = r.recognize_google(audio_text)
                   print("Text: " + r.recognize_google(audio_text))
               except:
                   print("Sorry, I did not get that")

       """

        sentence = txt

        # detect language
        languages = [Language.ENGLISH, Language.FRENCH, Language.ARABIC]
        detector = LanguageDetectorBuilder.from_languages(*languages).build()
        lang = detector.detect_language_of(sentence)

        if lang == Language.FRENCH:

            translator = Translator(from_lang="fr", to_lang="en")
            sentence = translator.translate(sentence)
        elif lang == Language.ARABIC:
            translator = Translator(from_lang="ar", to_lang="en")
            sentence = translator.translate(sentence)

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
                    response = random.choice(intent['responses'])
                    if lang == Language.FRENCH:
                        translator = Translator(from_lang="en", to_lang="fr")
                        response = translator.translate(response)

                    elif lang == Language.ARABIC:
                        translator = Translator(from_lang="en", to_lang="ar")
                        response = translator.translate(response)

                    # dispaly date and time
                    if tag == 'datetime':
                        print(time.strftime("%A"))
                        print(time.strftime("%D %B %Y"))
                        print(time.strftime("%H:%M:%S"))
                    tagg = tag
                    ws.send(tagg)
                    time.sleep(1)


        else:
            response = "I do not understand..."


        tel_send_message(chat_id, response)

        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"


def wemos_connection_thread():
    websocket.enableTrace(True)
    ws.run_forever()




wemos_thread = threading.Thread(target=wemos_connection_thread)
wemos_thread.daemon = True
wemos_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
