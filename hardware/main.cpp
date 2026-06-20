# define PUSH 7
# define vrX 0
# define vrY 1
int xval;
int yval;

void setup() {
  Serial.begin(9600);
  pinMode(vrX, INPUT);
  pinMode(vrY, INPUT);
}

void loop() {
  xval = analogRead(vrX);
  yval = analogRead(vrY);
  Serial.print(xval);
  Serial.print(", ");
  Serial.println(yval);
}