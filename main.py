import sqlite3
import bcrypt
from cryptography.fernet import Fernet
import random
import string

conn = sqlite3.connect("info.db")
cur = conn.cursor()

class Database():
    def __init__(self, username, master_password):
        self.username = username
        self.master_password = master_password

    def storeUser_MasterPass(self):
        hashedMasterPass = bcrypt.hashpw(self.master_password.encode("utf-8"), bcrypt.gensalt())
        insertQuery = "INSERT INTO info (username, master_password) VALUES (?, ?);"
        cur.execute(insertQuery, (self.username, hashedMasterPass))
        conn.commit()

    def addGeneratedPass(self):
        """Store the randomly generated password in the selected service column"""
        service = input("Enter the service name: ")
        columns = [i[1] for i in cur.execute("PRAGMA table_info(info)")]

        if service not in columns:
            cur.execute("ALTER TABLE info ADD COLUMN '{}' TEXT;".format(service))

        cur.execute(f"SELECT COUNT({service}) FROM info WHERE username = '{self.username}';")
        record = cur.fetchone()[0]

        if record == 0:
            cur.execute(f"UPDATE info SET '{service}' = '{self.generatePass()}' WHERE username = '{self.username}';")
        conn.commit()

    def generatePass(self):
        """
        Generate a random 25 char password containing lowercase, uppercase, numbers and special chars
        :return: str
        """
        password = ""
        randomSource = string.ascii_letters + string.digits + string.punctuation

        for i in range(3):
            password += random.choice(string.ascii_lowercase)
            password += random.choice(string.ascii_uppercase)
            password += random.choice(string.digits)
            password += random.choice(string.punctuation)
            password += random.choice(string.digits)

        for i in range(10):
            password += random.choice(randomSource)

        passwordList = list(password)
        random.shuffle(passwordList)
        random.shuffle(passwordList)
        password = ''.join(passwordList)
        return password

def createTable():
    cur.execute("""CREATE TABLE IF NOT EXISTS info
                    (username TEXT PRIMARY KEY NOT NULL,
                    master_password BLOB);""")
    conn.commit()

def addUser():
    while True:
        username = input("Set your username: ")
        cur.execute(f"SELECT COUNT(username) FROM info WHERE username = '{username}';")
        record = cur.fetchone()[0]
        if record == 0:
            break
        print("There is already a similar username. Enter a different username.")

    MasterPass = input("Set your master password: ")
    newUser = Database(username, MasterPass)
    newUser.storeUser_MasterPass()

    print("Your info has been stored in the database.")

def fetchData():
    cur.execute("SELECT * FROM info;")
    record = cur.fetchall()
    print(record)
    for row in record:
        print("username:", row[0], "password:", row[1], "facebook:", row[2], "youtube:", row[3])

def checkPassword():
    username = input("Enter yout username: ")
    cur.execute(f"SELECT master_password FROM info WHERE username = '{username}';")
    record = cur.fetchall()
    password = input("Enter your master password: ")
    return bcrypt.checkpw(password.encode("utf-8"), record[0][0])

user1 = Database("Rizwan", "hello")
user2 = Database("Omar", "12345")
createTable()
# user1.storeUser_MasterPass()
# user2.storeUser_MasterPass()
# print(user1.userKey)
# addUser()
# print(checkPassword())
# user2.addGeneratedPass()
fetchData()
conn.close()