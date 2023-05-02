import random
import json
import time
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import requests


# Set the IP address of the Wemos board
wemos_ip = "192.168.0.164"

# Set the pin nmr to which the smart led is connected
led_pin = "D1"


# Function to turn on the smart led
def turn_on():
    url = "http://" + wemos_ip + "/digital/" + led_pin + "/1"
    try:
        requests.get(url)
    except requests.exceptions.RequestException as e:
        print(e)


# Function to turn off the smart led
def turn_off():
    url = "http://" + wemos_ip + "/digital/" + led_pin + "/0"
    try:
        requests.get(url)
    except:
        print("An exception occurred")


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
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                print(f"{bot_name}: {random.choice(intent['responses'])}")
                # dispaly date and time
                if tag == 'datetime':
                    print(time.strftime("%A"))
                    print(time.strftime("%D %B %Y"))
                    print(time.strftime("%H:%M:%S"))
                # turn on led
                if tag == 'lights_on':
                    turn_on()
                # turn on led
                if tag == 'lights_off':
                    turn_off()
                #read tempurature
                if tag=='tempurature':
                    pass
                    #temperature=read_tempurature()
                   # print("Humidity: {}%".format(humidity))
                   # print("Temperature: {}°C".format(temperature))
                # read humidity
                if tag == 'humidity':
                    pass
                    #humidity = read_humidity()
                    #print("Humidity: {}%".format(humidity))



    else:
        print(f"{bot_name}: I do not understand...")
