import json

with open("icosnetdb.json", "r") as f:
    data = json.load(f)
ip_adress = ""
port = ""
currentId = 0


def getIdUser():
    idFacebook = []
    idTelegram = []
    for x in data["clients"]:
        idFacebook.append(x["idFacebook"])
        idTelegram.append(x["idTelegram"])
    return idFacebook, idTelegram


def getIpAdress(id):
    for x in data["clients"]:
        if x["idTelegram"] == id:
            return x["Ip"], x["Port"]
        else:
            return 0,0

