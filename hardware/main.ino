#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

# define WIDTH 128
# define LENGTH 64

#define OLED_RESET     -1 
#define SCREEN_ADDRESS 0x3C

# define PUSH 7
# define vrX 0
# define vrY 1
int xval;
int yval;

const int buzzer_pin = 11;

int allX[] = {512, 512};
int allY[] = {512, 512};

Adafruit_SSD1306 display(WIDTH, LENGTH, &Wire, OLED_RESET);

void create_display_box(){
    for(int i=12; i<112; ++i){
        display.drawPixel(i, 7, SSD1306_WHITE);
    }
    for(int i=7; i<57; ++i){
        display.drawPixel(12, i, SSD1306_WHITE);
    }
    for(int i=7; i<57; ++i){
        display.drawPixel(112, i, SSD1306_WHITE);
    }
    for(int i=12; i<112; ++i){
        display.drawPixel(i, 57, SSD1306_WHITE);
    }
    display.display();
}

void setup() {
    Serial.begin(9600);

    pinMode(vrX, INPUT);
    pinMode(vrY, INPUT);
    pinMode(buzzer_pin, OUTPUT);

    if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
        Serial.println(("SSD1306 allocation failed"));
        for(;;); // Don't proceed, loop forever
    }

    display.clearDisplay();
    display.display();

    create_display_box();

    // display.display();
}

void loop() {
    // 1. Read joysticks FIRST so controls stay highly responsive
    xval = analogRead(vrX);
    yval = analogRead(vrY);
    Serial.print(xval);
    Serial.print(", ");
    Serial.println(yval);

    allX[0] = allX[1];
    allY[0] = allY[1];
    allX[1] = xval;
    allY[1] = yval;

    bool xExt = false, yExt = false;
    if(allX[0] > 575 || allX[0] < 450){
        if(allX[1] < 575 && allX[1] > 450){
            xExt = true;
        }
    }
    if(allY[0] > 575 || allY[0] < 450){
        if(allY[1] < 575 && allY[1] > 450){
            yExt = true;
        }
    }

    if(xExt || yExt){
        tone (buzzer_pin, 800, 50);
        digitalWrite(8, HIGH);
        digitalWrite(12, LOW);
        delay(50);
    }

    digitalWrite(8, LOW);
    digitalWrite(12, HIGH);

    // 2. Process serial data only when a full line arrives
    if(Serial.available() > 0){
        String info = Serial.readStringUntil('\n');
        info.trim();

        int comma_loc = info.indexOf(',');

        String fuel_amount = info.substring(0, comma_loc);
        String gameOver = info.substring(comma_loc+1);

        if (info.length() > 0) {
            int fuelVal = fuel_amount.toInt();
            int barWidth = map(fuelVal, 0, 200, 0, 100); 
            barWidth = constrain(barWidth, 0, 100);

            display.clearDisplay();
            create_display_box();

            if (barWidth > 0) {
                display.fillRect(112-barWidth, 7, barWidth, 50, SSD1306_WHITE);
            }
            display.display();
        }

        if(gameOver == "1"){
            for(int i=0; i<5; ++i){
                digitalWrite(8, LOW);
                digitalWrite(12, HIGH);
                delay(50);
                digitalWrite(8, HIGH);
                digitalWrite(12, LOW);
                delay(50);
                for (int freq = 1000; freq >= 800; freq -= 50) {
                    tone (buzzer_pin, freq, 10);
                    delay(10);
                }
            }
        }
    }
}