import mysql.connector

mydb = mysql.connector.connect(
    host='145.24.222.168',
    user='tobias',
    password='Password123_',
    db='pinautomaat_elba',
    port=8001
)

iban = "VEELBA0000123401"
iban = input("DOE HET: ")

db = mydb.cursor()
db.execute("SELECT pin FROM bank_account WHERE iban = \"" + iban + "\"")
result = db.fetchone()
print(result)
print(iban.type)
