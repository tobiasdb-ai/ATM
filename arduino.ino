#include "Adafruit_Thermal.h"
#include "SoftwareSerial.h"
#include <Stepper.h>
#include <Wire.h>

#define TX_PIN 6 // Arduino transmit  YELLOW WIRE  labeled RX on printer
#define RX_PIN 5 // Arduino receive   GREEN WIRE   labeled TX on printer

// Declaring and constructing softwareserial
SoftwareSerial mySerial(RX_PIN, TX_PIN);
Adafruit_Thermal printer(&mySerial); 

#define SLAVE_ADDRESS 0x8

int recCount = 0;
volatile boolean receiveFlag = false;
char temp[100];
String command;
const int stepsPerRevolution = 64;

String dateTime;
String tranID;
String IBAN;
String amount;
String pasnr;
String printbon;

Stepper small_stepper(stepsPerRevolution, 8,10,9,11);

void setup() {
  Serial.begin(9600);
  Serial.println("Initializing");
  mySerial.begin(9600);  // Initialize SoftwareSerial
  printer.begin();
  
  // set stepper motor speed.
  small_stepper.setSpeed(300);
  // initialize i2c as slave
  Wire.begin(SLAVE_ADDRESS);

  // define callbacks for i2c communication
  Wire.onReceive(receiveEvent);
  Serial.println("starting testprint");

  //printReceipt("01-01-1970  00:00:00", 6942, "NL18INGB09090202", 350);
  printer.println("printer is ready");
  printer.feed(1);
  printer.feed(1);
  printer.feed(1);
  Serial.println("Ready!");

}

void loop() {
  if (receiveFlag == true) {
    Serial.println(temp);
    if (recCount == 0){
      dateTime = temp;
    }
    else if (recCount == 1){
      tranID = temp;
    }
    else if (recCount == 2){
      IBAN = temp;
    }
    else if (recCount == 3){
      pasnr = temp;
    }
    else if (recCount == 4){
      amount = temp;
    }
	else if (recCount == 5){
      printbon = temp;
    }
    recCount++;
    receiveFlag = false;
  }
  if (recCount == 6){
	dispenseMoney(amount);
	if (printbon == "yes"){
    	printReceipt(dateTime, tranID, IBAN, amount);
	}
	dispenseMoney(amount);
    recCount = 0;
  }
}

void dispenseMoney(String amount) {
	int x = amount.toInt()
	int y = x/10
	while(x !=0){
    Serial.println(x);
    Serial.println(y);
    for(int m = 0; m < y; m++){
      small_stepper.step(-2048);
      x = x - 10;
      Serial.println(x);
    }
  }
}

void printReceipt(String dateTime, String tranID, String IBAN, String amount) {
  printer.justify('C');
  printer.setSize('M');
  printer.doubleHeightOn();
  printer.println("El Banca Del Hermanos");
  printer.doubleHeightOff();
  printer.boldOff();
  
  printer.setSize('S');
  printer.println("Wijnhaven 99");
  printer.println("3011 WN Rotterdam");

  printer.justify('L');
  printer.print("Datum/Tijd: ");   //"01-01-1970  00:00:00"
  printer.println(dateTime);
  printer.feed(1);

  printer.println("Automaat #: 17");

  printer.print("Transactie #: ");
  printer.println(tranID);

  printer.print("Rekening #: ");
  printer.println(IBAN);

  printer.print("Pas #: ");
  printer.println(pasnr);

  printer.print("Bedrag: ");
  printer.print(amount);
  printer.println(" ,- EURO");

  printer.justify('C');
  printer.boldOn();
  printer.println("---------------------------");
  printer.boldOff();
  printer.justify('L');
  printer.println("Wij bedanken u voor het gebruik");printer.println("van de diensten van El Banco");printer.println("Del Hermanos.");
  printer.feed(3);
}

void receiveEvent(int howMany) {

  for (int i = 0; i < howMany; i++) {
    temp[i] = Wire.read();
    temp[i + 1] = '\0'; // add null after each char
  }

  // Shift everything to the left 1 bit because first bit of RPI is a cmd bit
  for (int i = 0; i < howMany; ++i)
    temp[i] = temp[i + 1];

  receiveFlag = true;
}