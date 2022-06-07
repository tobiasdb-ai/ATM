import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

rd = SimpleMFRC522()

try:
	id, text = rd.read()
	print(id)
	print(text)
finally:
	GPIO.cleanup()
