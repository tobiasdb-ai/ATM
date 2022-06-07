import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()
def readCard():
    try:
        id, text = reader.read()
        return text
    finally:
        GPIO.cleanup()
print("SCAN YOUR CARD")
print(readCard())