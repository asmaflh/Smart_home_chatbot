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

currentId = 0
ip_adress = ""
port = ""


def getIdUser():
    idFacebook = []
    idTelegram = []
    # Execute SQL query
    mycursor.execute("SELECT * FROM client")

    # Fetch all rows
    rows = mycursor.fetchall()
    # Print rows
    for row in rows:
        idFacebook.append(row[1])
        idTelegram.append(row[2])
        print('idFacebookUser : ', row[1])
        print('idTelegramUser : ', row[2])
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
