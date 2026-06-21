# define PUSH 7
# define vrX 0
# define vrY 1
int xval;
int yval;

const int buzzer_pin = 11;

int allX[] = {512, 512};
int allY[] = {512, 512};

void setup() {
    Serial.begin(9600);
    pinMode(vrX, INPUT);
    pinMode(vrY, INPUT);
    pinMode(buzzer_pin, OUTPUT);
}

void loop() {
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
    digitalWrite(12, HIGHT);
    
}