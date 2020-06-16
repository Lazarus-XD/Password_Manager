import sqlite3
from cryptography.fernet import Fernet
import cryptography
import random
import string

conn = sqlite3.connect("info.db")
cur = conn.cursor()
key = None

def storeUser_MasterPass(username):
    cur.execute(f"INSERT INTO info (username) VALUES ('{username}');")
    conn.commit()

def addServiceAndPass(username):
    """Store the randomly generated password in the selected service column"""
    service = input("Enter the service name: ")
    columns = [i[1] for i in cur.execute("PRAGMA table_info(info)")]
    print(columns)

    if service not in columns:
        cur.execute(f"ALTER TABLE info ADD COLUMN '{service}' TEXT;")
    conn.commit()

    cur.execute(f"SELECT COUNT({service}) FROM info WHERE username = '{username}';")
    record = cur.fetchone()[0]

    if record == 0:
        cur.execute(f"UPDATE info SET '{service}' = '{generatePass()}' WHERE username = '{username}';")
    conn.commit()

def generatePass():
    """
    Generate a random 25 char password containing lowercase, uppercase, numbers and special chars
    :return: str
    """
    global key
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
    f = Fernet(key)
    token = f.encrypt(password.encode("utf-8"))
    return token.decode("utf-8")

def createTable():
    cur.execute("""CREATE TABLE IF NOT EXISTS info
                    (username TEXT PRIMARY KEY NOT NULL);""")
    conn.commit()

def generateKey(username):
    global key
    key = Fernet.generate_key()
    with open(username + "(key).txt", "w") as f:
        f.write("*********************************************************************\n")
        f.write("                 STORE THIS KEY IN A SECURE PLACE!\n")
        f.write("*********************************************************************\n")
        f.write("\n")
        f.write(key.decode("utf-8"))
        f.close()

def fetchData(username):
    global key
    cur.execute(f"SELECT * FROM info WHERE username = '{username}';")
    record = cur.fetchall()
    f = Fernet(key)
    for row in record:
        print("username:", row[0], "facebook:", row[1], "youtube:", row[2])
        print(f.decrypt(row[1].encode("utf-8")).decode("utf-8"))
        # print(f.decrypt(row[2].encode("utf-8")).decode("utf-8"))


def main():
    global key
    createUser = "n"
    username = input("Enter yout username: ")
    cur.execute(f"SELECT COUNT(username) FROM info WHERE username = '{username}';")
    record = cur.fetchone()[0]
    if record == 0:
        while True:
            createUser = input("Username does not exist. Do you want to create a new? Enter y or n: ")
            if createUser == "y" or createUser == "n":
                break

        if createUser == "y":
            storeUser_MasterPass(username)
            generateKey(username)
            print("Your info has been stored in the database.")

    while True:
        if createUser == "n" or record != 0:
            key = input("Enter your master key: ").encode("utf-8")
        answer = input("Do you want to add a new service? Enter y or n: ")
        if answer == "y" or answer == "n":
            break

    if answer == "y":
        print("key:", key)
        addServiceAndPass(username)

createTable()
# print(user1.userKey)
# print(checkPassword())
# user1.addGeneratedPass()
# print(generatePass())
main()
# fetchData("Abbu")
conn.close()

# try:
#     key = Fernet.generate_key()
#     f = Fernet(key)
#     token = f.encrypt(b"my deep dark secret")
#     key = Fernet.generate_key()
#     f = Fernet(key)
#     print(f.decrypt(token))
# except (cryptography.fernet.InvalidToken):
#     print("Invalid key")