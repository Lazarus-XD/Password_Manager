# Password_Manager
A simple password manager that generates random passwords and stores them in a database.

**REQUIRED PACKAGE: cryptography**

To install the package type in command prompt or terminal:
```{r, engine='bash', count_lines}
pip install cryptography
```

## How it works
- Stores all the information in a database file
- Generates random passwords for each service
- Stores the generated password after encrypting it
- The encryption key is stored in a .txt file when a user is created **[Store the key in a secure place]**
