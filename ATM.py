import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from pad4pi import rpi_gpio
import time
import mysql.connector
import sys
import os

GPIO.setwarnings(False)

hideKeys = 0
iban = ''
accID = ''

mydb = mysql.connector.connect(
    host='145.24.222.168',
    user='tobias',
    password='Password123_',
    db='pinautomaat_elba',
    port=8001
)
db = mydb.cursor()


def printKey(key):
    global keys
    if (hideKeys == 1):
        sys.stdout.write("*")
        sys.stdout.flush()
    elif (hideKeys == 2):
        sys.stdout.write(key[-1])
        sys.stdout.flush()
    keys += key


KEYPAD = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

ROW_PINS = [5, 6, 13, 19]
COL_PINS = [12, 16, 20, 21]

global keys
keys = ""

factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(
    keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

keypad.registerKeyPressHandler(printKey)

reader = SimpleMFRC522()


def readCard():
    id, text = reader.read()
    return text


def startPage():
    os.system('clear')
    print("\nWelcome to El Banco Del Los Hermanos")
    print("Scan your card to begin")
    global iban 
    iban = readCard()
    loginPage()

def loginPage():
    global hideKeys
    global accID
    global keys
    os.system('clear')
    db.execute("SELECT * FROM card WHERE iban = \"" + iban[:16] + "\"")
    result = db.fetchone()
    accID = result[3]
    hideKeys = 1              # 0-->No chars   1--> * 2--> chars
    print("Succesfully scanned card of account: " + iban)
    print("Type your pin to continue: ")
    keys = ""
    password = getPassword()
    if (password == str(result[1])):
        hideKeys = 0
        firstMenu()
    else:
        hideKeys = 2
        wrongPass()

def wrongPass():
    global keys
    os.system('clear')
    print("\nIncorrect password. What do you want to do:")
    print("\n(A) Retry")
    print("\n(*) STOP")
    keys = ""
    menuChoice = getKey()
    if (menuChoice == "A"):
        loginPage()
    if (menuChoice == "*"):
        startPage()


def getPassword():
    while (len(keys) < 4):
        time.sleep(0.1)
    return keys[-4:]


def getKey():
    while (len(keys) < 1):
        time.sleep(0.1)
    return keys[-1:]


def firstMenu():
    os.system('clear')
    print("Succesfully logged in to bank account\n")
    print("Select what you want to do:")
    print("(A)  Withdraw money")
    print("(B)  Check account balance\n")
    print("(*)  STOP")
    global keys
    keys = ""
    menuChoice = getKey()
    if (menuChoice == "A"):
        print("money withdrawal page")
    if (menuChoice == "B"):
        balancePage()
    if (menuChoice == "*"):
        startPage()

def balancePage():
    global keys
    os.system('clear')
    print("\nAccount Balance Page:\n")
    db.execute("SELECT balance FROM bank_account WHERE id = \"" + str(accID) + "\"")
    result = db.fetchone()
    balance = "{:.2f}".format(result[0]/100)
    print(f"Your current account balance is: {str(balance)} EURO")
    print("\nSelect what you want to do:")
    print("(A)  Withdraw money")
    print("\n(*)  STOP")
    keys = ""
    menuChoice = getKey()
    if (menuChoice == "A"):
        print("money withdrawal page")
    if (menuChoice == "*"):
        startPage()
    

startPage()
