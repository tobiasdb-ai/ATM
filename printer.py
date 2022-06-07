from smbus import SMBus
import time
import datetime

address = 0x8
bus = SMBus(1)

def writeData(value):
    byteValue = StringToBytes(value)
    bus.write_i2c_block_data(address,0x00,byteValue)
    return -1

def StringToBytes(val):
    retVal = []
    for c in val:
        retVal.append(ord(c))
    return retVal

def printReceipt(tranID, IBAN, pasnr, amount):
    dateTimeStamp = datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')
    writeData(dateTimeStamp)
    time.sleep(0.2)
    writeData(tranID)
    time.sleep(0.2)
    writeData(IBAN)
    time.sleep(0.2)
    writeData(pasnr)
    time.sleep(0.2)
    writeData(amount)
    time.sleep(0.2)
    
    
    

while True:
    tranID = input("Please input the transaction id: ")
    IBAN = input("Please input the IBAN: ")
    pasnr = input("Please input the pasnr: ")
    amount = input("Please input the amount: ")
    printReceipt(tranID, IBAN, pasnr, amount)
    time.sleep(5)
    input("Press return to print another receipt")
