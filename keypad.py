from pad4pi import rpi_gpio

KEYPAD = [
    [1,2,3,"A"],
    [4,5,6,"B"],
    [7,8,9,"C"],
    ["*",0,"#","D"]
]

ROW_PINS = [5,6,13,19]
COL_PINS = [12,16,20,21]

factory = rpi_gpio.KeypadFactory()

keypad = factory.create_keypad(keypad=KEYPAD, row_pins = ROW_PINS, col_pins=COL_PINS)
def printKey(key):
    print(key, end='')
    
keypad.registerKeyPressHandler(printKey)