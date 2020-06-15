import sqlite3
import os.path
import bcrypt
from cryptography.fernet import Fernet

conn = sqlite3.connect("info.db")
cur = conn.cursor()

class Database():
    def __init__(self, username, master_password):
        self.username = username
        self.master_password = master_password
        self.userKey = Fernet.generate_key()

    def storeUser_MasterPass(self):
        hashedMasterPass = bcrypt.hashpw(self.master_password.encode("utf-8"), bcrypt.gensalt())
        insertQuery = "INSERT INTO info (username, master_password) VALUES (?, ?);"
        cur.execute(insertQuery, (self.username, hashedMasterPass))
        conn.commit()

    def addService(self):
        pass

def createTable():
    cur.execute("""CREATE TABLE IF NOT EXISTS info
                    (username TEXT PRIMARY KEY NOT NULL,
                    master_password BLOB);""")
    conn.commit()

def addUser():
    while True:
        username = input("Set your username: ")
        cur.execute("SELECT COUNT(username) FROM info WHERE username = ?;", (username,))
        record = cur.fetchone()[0]
        if record == 0:
            break
        print("There is already a similar username. Enter a different username.")

    MasterPass = input("Set your master password: ")
    newUser = Database(username, MasterPass)
    newUser.storeUser_MasterPass()

    print("Your info has been stored in the database.")

def fetchData():
    fetchQuery = "SELECT * FROM info;"
    cur.execute(fetchQuery)
    record = cur.fetchall()
    for row in record:
        print("username:", row[0], "password:", row[1])
    # print("username:", record[0][0], "password:", record[0][1])
    # print("username:", record[1][0], "password:", record[1][1])

def checkPassword():
    username = input("Enter yout username: ")
    fetchQuery = "SELECT master_password FROM info WHERE username = ?;"
    cur.execute(fetchQuery, (username,))
    record = cur.fetchall()
    password = input("Enter your master password: ")
    # print("password:", record[0][0])
    # print(type(record[0][0]))
    return bcrypt.checkpw(password.encode("utf-8"), record[0][0])

user1 = Database("Rizwan", "hello")
user2 = Database("Omar", "12345")
createTable()
user1.storeUser_MasterPass()
user2.storeUser_MasterPass()
print(user1.userKey)
fetchData()
# addUser()
# print(checkPassword())
conn.close()