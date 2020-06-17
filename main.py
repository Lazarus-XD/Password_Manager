import sqlite3
from cryptography.fernet import Fernet
import cryptography
import random
import string

key = None

def storeUser(username):
    cur.execute("INSERT INTO info (username) VALUES (?)", (username,))
    conn.commit()

def addServiceAndPass(username):
    """Store the randomly generated password in the selected service column"""
    global key
    service = input("Enter the service name: ")
    while True:
        print("\n1. Manually enter password")
        print("2. Generate random password")
        passInfo = input("Enter your choice (1/2): ")
        if passInfo == "1" or passInfo == "2":
            break
    columns = [i[1] for i in cur.execute("PRAGMA table_info(info)")]

    if service not in columns:
        cur.execute("ALTER TABLE info ADD COLUMN '{}' TEXT".format(service))
        conn.commit()

    cur.execute("SELECT COUNT({}) FROM info WHERE username = ?".format(service), (username,))
    record = cur.fetchone()[0]

    if record == 0 and passInfo == "2":
        cur.execute("UPDATE info SET {} = '{}' WHERE username = ?".format(service, generatePass()), (username,))
        conn.commit()

    if record == 0 and passInfo == "1":
        password = input("Enter your password: ")
        f = Fernet(key)
        token = f.encrypt(password.encode("utf-8")).decode("utf-8")
        cur.execute("UPDATE info SET {} = '{}' WHERE username = ?".format(service, token), (username,))
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
    """Generate the encryption key and store it in a seperate txt file"""
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
    passStored = printed = False
    cur.execute("SELECT * FROM info WHERE username = ?", (username,))
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
                continue
            except cryptography.fernet.InvalidToken:
                print("Invalid Token")
                break
            if not passStored and not printed:
                print("You have no stored passwords!")
                printed = True

def createTable():
    cur.execute("""CREATE TABLE IF NOT EXISTS info
                    (username TEXT PRIMARY KEY NOT NULL)""")
    conn.commit()

def main():
    global key
    createUser = "n"
    while True:
        username = input("Enter your username: ")
        cur.execute("SELECT COUNT(username) FROM info WHERE username = ?", (username,))
        record = cur.fetchone()[0]
        if record == 0:
            while True:
                createUser = input("Username does not exist. Do you want to create a new? Enter y or n: ")
                if createUser == "y" or createUser == "n":
                    break

            if createUser == "y":
                storeUser(username)
                generateKey(username)
                print("Your info has been stored in the database.")
                break

        if createUser == "n" and record != 0:
            key = input("Enter your master key: ").encode("utf-8")
            break

    while True:
        while True:
            print("\n1. Add a new service")
            print("2. Access your stored passwords")
            print("3. Exit password manager")
            answer = input("Enter your choice (1/2/3): ")
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
