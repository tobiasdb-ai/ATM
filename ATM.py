from colorama import Fore
from colorama import Style
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from pad4pi import rpi_gpio
from smbus import SMBus
import time
import datetime
import mysql.connector
import sys
import os

address = 0x8
bus = SMBus(1)

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
    print(Style.BRIGHT + "\nWelcome to El Banco Del Los Hermanos")
    print("Scan your card to begin")
    global iban 
    iban = readCard()[:16]
    loginPage()

def loginPage():
    global hideKeys
    global accID
    global keys
    tries = 0
    os.system('clear')
    db.execute("SELECT * FROM card WHERE iban = \"" + iban[:16] + "\"")
    result = db.fetchone()
    accID = result[3]
    ibanhalf = iban[:16]
    tries = result[2]
    print(f"you have {3 - tries} tries.")
    if (tries >= 3):
        maxTries()    
    hideKeys = 1              # 0-->No chars   1--> * 2--> chars
    print("Succesfully scanned card of account: " + ibanhalf[0:10] + "******")
    print("Type your pin to continue: ")
    keys = ""
    password = getPassword()
    if (password == str(result[1])):
        hideKeys = 0
        firstMenu()
    else:
        hideKeys = 2
        wrongPass(tries)

def wrongPass(tries):
    global keys
    os.system('clear')
    newTries = tries + 1
    db.execute("UPDATE `pinautomaat_elba`.`card` SET `tries` = '" + str(newTries) + "' WHERE(`iban` = '" + str(iban[:16]) + "');")
    mydb.commit()
    if (newTries >= 3):
        maxTries()
    print("\nIncorrect password. What do you want to do:")
    print(Fore.YELLOW + "\n(A)  Retry" + Fore.RESET)
    print(Fore.RED + "\n(*)  STOP" + Fore.RESET)
    keys = ""
    menuChoice = getKey()
    if (menuChoice == "A"):
        loginPage()
    if (menuChoice == "*"):
        startPage()
        
def maxTries():
    global keys
    os.system('clear')
    print(Fore.RED + "Exceeded maximum amount of tries." + Fore.RESET)
    print(Fore.RED + "Call 0900 0899 to recover your account." + Fore.RESET)
    print(Fore.RED + "\n\nPress any key to continue." + Fore.RESET)
    keys = ""
    menuChoice = getKey()
    startPage()
    


def getPassword():
    while (len(keys) < 4):
        time.sleep(0.1)
    return keys[-4:]

def getAmount():
    global hideKeys
    hideKeys = 2
    while (len(keys) < 3):
        time.sleep(0.1)
    return keys[-3:]


def getKey():
    while (len(keys) < 1):
        time.sleep(0.1)
    return keys[-1:]


def firstMenu():
    os.system('clear')
    db.execute("UPDATE `pinautomaat_elba`.`card` SET `tries` = '" + str(0) + "' WHERE(`iban` = '" + str(iban[:16]) + "');")
    mydb.commit()
    print("Succesfully logged in to bank account\n")
    print("Select what you want to do:")
    print("(A)  Withdraw money")
    print("(B)  Check account balance\n")
    print(Fore.RED + "\n(*)  STOP" + Fore.RESET)
    global keys
    keys = ""
    menuChoice = getKey()
    if (menuChoice == "A"):
        withdrawPage()
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
    print(Fore.RED + "\n(*)  STOP" + Fore.RESET)
    keys = ""
    menuChoice = getKey()
    if (menuChoice == "A"):
        withdrawPage()
    if (menuChoice == "*"):
        startPage()

def withdrawPage():
    os.system('clear')
    print("\nMoney withdrawal page\n")
    print("Select the amount of money you wish to withdraw: \n")
    print("(A)  € 20")
    print("(B)  € 50")
    print("(C)  € 70")
    print("(D)  € 100")
    print("(#)  Custom amount")
    print(Fore.RED + "\n(*)  STOP" + Fore.RESET)
    global keys
    keys = ""
    menuChoice = getKey()
    if (menuChoice == "A"):
        dbWithdraw(2000)
    if (menuChoice == "B"):
        dbWithdraw(5000)
    if (menuChoice == "C"):
        dbWithdraw(7000)
    if (menuChoice == "D"):
        dbWithdraw(10000)
    if (menuChoice == "#"):
        customAmountPage()
    if (menuChoice == "*"):
        startPage()

def customAmountPage():
    print("\nEnter your custom amount (max €300): €", end='')
    global keys
    keys = ""
    amount = int(getAmount())
    if (amount <= 300):
        dbWithdraw(amount*100)
    else:
        print("\nUnvalid withdrawal amount")
        time.sleep(2)
        withdrawPage()
    

def dbWithdraw(amount):
    os.system('clear')
    db.execute("SELECT balance FROM bank_account WHERE id = \"" + str(accID) + "\"")
    result = db.fetchone()
    balance = result[0]
    if (balance >= amount):
        newBalance = balance - amount
        db.execute("UPDATE `pinautomaat_elba`.`bank_account` SET `balance` = '" + str(newBalance) + "' WHERE(`id` = '" + str(accID) + "');")
        mydb.commit()
        withdrawSucces(amount)
    else:
        os.system('clear')
        print("\nMoney withdrawal unsuccesful: Not enough balance.")
        time.sleep(2)
        startPage()
        
def withdrawSucces(amount):
    os.system('clear')
    print("\nMoney withdrawal succesful\n")
    print("Would you like a receipt?: \n")
    print(Fore.GREEN + "(A)  YES" + Fore.RESET)
    print(Fore.RED + "\n(*)  STOP" + Fore.RESET)
    global keys
    keys = ""
    menuChoice = getKey()
    global iban
    if (menuChoice == "A"):
        printReceipt("1",iban,iban[-2:],str(amount))
        finalPage()
    if (menuChoice == "B"):
        finalPage()
        
    
def finalPage():
    os.system('clear')
    print('Thanks for using El Banco Del Los Hermanos')
    print('\n We hope to see you again in the near future!')
    time.sleep(3)
    startPage()

def writeData(value):
    byteValue = StringToBytes(value)
    bus.write_i2c_block_data(address,0x00,byteValue)
    return -1

def StringToBytes(val):
    retVal = []
    for c in val:
        retVal.append(ord(c))
    return retVal

def printReceipt(rctranID, rcIBAN, rcpasnr, rcamount):
    dateTimeStamp = datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')
    writeData(dateTimeStamp)
    time.sleep(0.2)
    writeData(rctranID)
    time.sleep(0.2)
    writeData(rcIBAN)
    time.sleep(0.2)
    writeData(rcpasnr)
    time.sleep(0.2)
    writeData(rcamount)
    time.sleep(0.2)
    
startPage()
