from flask import Flask, request, Response
import requests
import random
import json
import torch
from database import getIdUser, getIpAdress
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
from translate import Translator
from lingua import Language, LanguageDetectorBuilder
from speech_recognition import UnknownValueError
import speech_recognition as sr
import soundfile
import time
import database
import threading
import websocket




def Websocket(tag):
    def on_message(ws, message):
        print("Received from Wemos:", message)
        time.sleep(2)
        tel_send_message(database.currentId, message)
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
    time.sleep(2)
    ws.close()




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
    print("chat_id-->", chat_id)
    return chat_id


def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    r = requests.post(url, json=payload)
    return r


@app.route('/', methods=['GET', 'POST'])
def index():
    global wemos_msg
    if request.method == 'POST':
        msg = request.get_json()
        chat_id = parse_message(msg)
        txt = ""
        response = ""
        a, b = getIdUser()
        if chat_id in b:
            database.currentId = chat_id
            database.ip_adress, database.port = getIpAdress(chat_id)

            if 'voice' in msg['message']:
                file_id = msg['message']['voice']['file_id']
                audio_url = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}'
                response = requests.get(audio_url)
                audio_file_path = response.json()['result']['file_path']
                audio_content_url = f'https://api.telegram.org/file/bot{TOKEN}/{audio_file_path}'
                audio_response = requests.get(audio_content_url)

                with open('audio.ogg', 'wb') as f:
                    f.write(audio_response.content)

                data, samplerate = soundfile.read('audio.ogg')
                soundfile.write('new.wav', data, samplerate, subtype='PCM_16')
                audio_file = "new.wav"
                r = sr.Recognizer()
                try:
                    with sr.AudioFile(audio_file) as source:
                        audio = r.record(source)  # Read the entire audio file

                        # Perform speech recognition
                        txt = r.recognize_google(audio)
                        print("Recognized Text:")
                        print(txt)
                except UnknownValueError:
                    tel_send_message(chat_id, "can't determine audio please speak again!")
            elif 'text' in msg['message']:
                txt = msg['message']['text']
            else:
                tel_send_message(chat_id, "can't process this type of data please enter your commande as text or voice")

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
                        Websocket(tagg)




            else:
                response = "I do not understand..."

            tel_send_message(chat_id, response)

        else:
            tel_send_message(chat_id, "you're not allowed to use this chat")

        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"


if __name__ == '__main__':
    app.run(debug=True)
