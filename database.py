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

def getIdFacebook():
  # Execute SQL query
  mycursor.execute("SELECT idFacebook FROM client")
  # Fetch all rows
  rows = mycursor.fetchone()
  # Print rows
  for row in rows:
    print('idFacebookUser : ', row)
  return rows

if __name__ == "__main__":
  getIdFacebook()

