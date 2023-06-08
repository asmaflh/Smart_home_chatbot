import mysql.connector

# Set up database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="icosnet"
)

# Create cursor object
mycursor = mydb.cursor()
ip_adress = ""
port = ""
currentId=0

def getIdUser():
    idFacebook = []
    idTelegram = []
    # Execute SQL query
    mycursor.execute("SELECT idFacebook,idTelegram FROM client")

    # Fetch all rows
    rows = mycursor.fetchall()
    # Print rows
    for row in rows:
        idFacebook.append(row[0])
        idTelegram.append(row[1])
        print('idFacebookUser : ', row[0])
        print('idTelegramUser : ', row[1])
    return idFacebook, idTelegram


def getIpAdress(id):
    # Execute SQL query
    mycursor.execute("SELECT Ip,Port FROM client WHERE idTelegram='%s'" % id)
    # Fetch all rows
    row = mycursor.fetchone()
    return row[0], row[1]


if __name__ == "__main__":
    getIdUser()
    getIpAdress(1668424135)
#     allowed, tel = getIdUser()
#     if 1668424135 in tel:
#         print("true")
