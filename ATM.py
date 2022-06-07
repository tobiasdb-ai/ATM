import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from pad4pi import rpi_gpio
import time
import mysql.connector
import os

GPIO.setwarnings(False)

hideKeys = 0
iban = ''

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
        print("*", end="")
    elif (hideKeys == 2):
        print(key[-1], end="")
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
    print("Welcome to El Banco Del Los Hermanos")
    print("Scan your card to begin")
    global iban 
    iban = readCard()
    loginPage()

def loginPage():
    global hideKeys
    db.execute("SELECT pin FROM bank_account WHERE iban = \"" + iban[:16] + "\"")
    result = db.fetchone()
    print(result[0])
    hideKeys = 1              # 0-->No chars   1--> * 2--> chars
    print("Succesfully scanned card of account: " + iban)
    print("Type your pin to continue: ")
    password = getPassword()
    if (password == str(result[0])):
        print("Succesfully logged in to bank account")
        hideKeys = 2
        firstMenu()
    else:
        print("Password is wrong")


def getPassword():
    while (len(keys) < 4):
        time.sleep(0.1)
    return keys[-4:]


def getKey():
    while (len(keys) < 1):
        time.sleep(0.1)
    return keys[-1:]


def firstMenu():
    for i in range(10):
        print("\n")
    print("Select what you want to do:")
    print("(A)  Withdraw money")
    print("(B)  Check account balance")
    print("(*)  STOP")
    global keys
    keys = ""
    menuChoice = getKey()
    if (menuChoice == "A"):
        print("money withdrawal page")
    if (menuChoice == "B"):
        print("account balance page")
    if (menuChoice == "*"):
        return



startPage()
