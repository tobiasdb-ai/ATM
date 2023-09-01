# ATM Project
This is a project for the second half of the first year of computer science on the University of Applied sciences in Rotterdam. 

## Parts of the project
- Self-designed laser-cut wooden enclosure.
- Old laptop display for showing the UI
- Raspberry Pi for interfacing the touch pad and the RFID reader and the the main program showing the UI
- Arduino Uno connected over I2C to the RasPi for printing receipts.

## Backend requirements
On the raspberry pi, a seperate SQL server had to be setup that hosted a database with data for the ATM. The main ATM.py program would make requests to this database for account balance, password tries, and transactions. The project also contained security features.
