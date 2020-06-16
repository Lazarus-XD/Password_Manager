import sqlite3
from cryptography.fernet import Fernet
import cryptography
import random
import string

key = None

def storeUser_MasterPass(username):
    cur.execute(f"INSERT INTO info (username) VALUES ('{username}');")
    conn.commit()

def addServiceAndPass(username):
    """Store the randomly generated password in the selected service column"""
    service = input("Enter the service name: ")
    columns = [i[1] for i in cur.execute("PRAGMA table_info(info)")]

    if service not in columns:
        cur.execute(f"ALTER TABLE info ADD COLUMN '{service}' TEXT;")
    conn.commit()

    cur.execute(f"SELECT COUNT({service}) FROM info WHERE username = '{username}';")
    record = cur.fetchone()[0]

    if record == 0:
        cur.execute(f"UPDATE info SET '{service}' = '{generatePass()}' WHERE username = '{username}';")
    conn.commit()

def generatePass():
    """Generate a random 25 char password containing lowercase, uppercase, numbers and special chars"""
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
    try:
        print("\nGenerated password:", password)
        f = Fernet(key)
        token = f.encrypt(password.encode("utf-8"))
        return token.decode("utf-8")
    except:
        print("Invalid key")

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
    passStored = False
    cur.execute(f"SELECT * FROM info WHERE username = '{username}';")
    record = cur.fetchall()
    columns = [i[1] for i in cur.execute("PRAGMA table_info(info)")]
    f = Fernet(key)
    print()
    for row in record:
        if len(row) == 1:
            print("You have no stored passwords!")
        for data in range(len(row)-1):
            try:
                if type(f.decrypt(row[data+1].encode("utf-8")).decode("utf-8")) == str:
                    print(columns[data+1], end=": ")
                    print(f.decrypt(row[data+1].encode("utf-8")).decode("utf-8"))
                    passStored = True
            except AttributeError:
                if not passStored:
                    print("You have no stored passwords!")
                continue
            except cryptography.fernet.InvalidToken:
                print("Invalid Token")
                break

def createTable():
    cur.execute("""CREATE TABLE IF NOT EXISTS info
                    (username TEXT PRIMARY KEY NOT NULL);""")
    conn.commit()

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

    if createUser == "n" or record != 0:
        key = input("Enter your master key: ").encode("utf-8")

    while True:
        while True:
            answer = input("""\n1. Do you want to add a new service
2. Do you want to access your stored passwords
3. Exit password manager
Enter your choice (1/2/3): """)
            if answer == "1" or answer == "2" or answer == "3":
                break

        if answer == "1":
            addServiceAndPass(username)

        if answer == "2":
            fetchData(username)

        if answer == "3":
            break


if __name__ == "__main__":
    conn = sqlite3.connect("info.db")
    cur = conn.cursor()
    createTable()
    main()
    conn.close()