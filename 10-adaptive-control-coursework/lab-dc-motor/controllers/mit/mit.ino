// Motor control pins
const int M1 = 6;  // Motor terminal 1 //for us 6
const int M2 = 7;  // Motor terminal 2 //for us 7

// Speed feedback pins
const int S1 = 2;  // Speed sensor (forward)//for us 2
const int S2 = 3;  // Speed sensor (reverse)//for us 3


volatile unsigned long pos_i = 0;
volatile unsigned long prevT = 0;
volatile unsigned long prevT_i = 0;
volatile unsigned long velocity_i = 0;
volatile unsigned long posPrev = 0;
volatile unsigned long v1Filt = 0;
volatile unsigned long v1Prev = 0;

int targetPWM = 208; // 0=stop, 255=full speed

float a = 1.203;     // Plant parameter
float b = 0.1514;
float am = 2.0;      // Model parameter
float bm = 0.2;
float gammaVal = 0.02;  // Adaptation gain
float u = 0.0;

// Variables
float yp = 0.0;   // Plant output
float ym = 0.0;   // Reference model output
float theta1 = 0.0, theta2 = 0.0; // Adaptive parameters
float e0 = 0.0;   // Tracking error
float thres=0.9;

// Sampling
float dt = 0.001;       // Sampling period (s)
unsigned long lastTime = 0;

void setup() {
  pinMode(M1, OUTPUT);
  pinMode(M2, OUTPUT);

  pinMode(S1, INPUT_PULLUP);
  pinMode(S2, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(S1), readEncoder, RISING);
  //attachInterrupt(digitalPinToInterrupt(S2), readEncoder, RISING);
  //attachInterrupt(digitalPinToInterrupt(S2), readEncoder, RISING);
  //attachInterrupt(digitalPinToInterrupt(S2), countReversePulse, RISING);

  Serial.begin(9600);
}
float reference(float t) {
  // Choose your input signal:
  return 168;               // Step
  // return 0.5 * t;        // Ramp
  // return sin(1.0 * t);   // Sine
  //return 12+2*(sin(0.2 * PI * t) > 0 ? 1 : -1); // Square wave
}
void loop() {
  // Spin forward
  int pos = 0;
  float velocity2 = 0;
  noInterrupts(); // disable interrupts temporarily while reading
  pos = pos_i;
  velocity2 = velocity_i;
  interrupts(); 
  unsigned long previousMillis = 0;   // Stores last time event ran
  const unsigned long interval = 10;  // 10 ms = 0.01 seconds

  long currT = micros();
  float deltaT = ((float) (currT-prevT))/1.0e6;
  float velocity1 = (pos - posPrev)/deltaT;
  float V_ref = 15.0;
  posPrev = pos;
  prevT = currT;

  velocity1 = velocity1/2086.0*60.0;
  v1Filt = (float)0.854*v1Filt + 0.0728*velocity1 + 0.0728*v1Prev;
  v1Prev = velocity1;
  
  
  // if(currT/1e6==1){
  //   Serial.println(v1Filt);
  //   Serial.println(targetPWM);
  // }

  unsigned long now = millis();
  float t = now / 1000.0;  // time in seconds

  if (t - lastTime * 0.001 >= dt) {
    lastTime = now;

    // Reference input
    float r = reference(t);

    // Control input (adaptive law)
    u = theta1 * r - theta2 * v1Filt;

    // Plant dynamics (Euler integration)
    float dyp = -a * yp + b * u;
    yp += dyp * dt;

    // Reference model dynamics
    float dym = -am * ym + bm * r;
    ym += dym * dt;

    // Tracking error
    e0 = v1Filt - ym;

    // MIT adaptation laws
    float dtheta1 = -gammaVal * e0 * r;
    float dtheta2 =  gammaVal * e0 * v1Filt;

    theta1 = max(min(theta1+dtheta1 * dt,thres),-thres);
    theta2 = max(min(theta2+dtheta2 * dt,thres),-thres);
    Serial.println(theta1);
    Serial.println(theta2);
    

    targetPWM=min(u,250);
    Serial.println(v1Filt);
  }

  //unsigned long currentMillis = millis();  // current time in ms

  // if (currentMillis - previousMillis >= interval) {
  //   previousMillis = currentMillis;  // save last trigger time
  //   //Serial.println(v1Filt);
  //   //Serial.println(128+u);
    
  // }
  //targetPWM=0;
  //40*(V_ref-v1Filt)


  analogWrite(M1, targetPWM); //forward
  digitalWrite(M2,LOW);
  
  // digitalWrite(M2, HIGH);
  // analogWrite(M1, targetPWM);

  // digitalWrite(M2, HIGH); 
  // analogWrite(M1, 255- targetPWM);
  //digitalWrite(M1,HIGH);
  //digitalWrite(M2,LOW);
    
  
  //delay(2000);  // run 2 sec
  /*

  
  //Stop
  digitalWrite(M1, LOW);
  digitalWrite(M2, LOW);
  delay(1000);

  
  // Spin backward
  digitalWrite(M1, LOW);
  digitalWrite(M2, HIGH);
  delay(2000);  // run 2 sec

  // Stop
  digitalWrite(M1, LOW);
  digitalWrite(M2, LOW);
  delay(1000);*/

  // Print speed info
  
  //Serial.println(pos);
  //Serial.println(currT);
  //Serial.println(posPrev);
  
  delay(100); // 0.1 s sampling
  //delay(5000);
}



void readEncoder() {
  // Read encoder B when ENCA rises
  int b = digitalRead(S1);
  //int b1 = digitalRead(S1);
  int increment = 0;
  if (b > 0) {
    // If B is high, increment forward
    increment = 1;
  } else {
    // Otherwise, increment backward
    increment = -1;
  }
  pos_i = pos_i + increment;

  // Compute velocity with method 2
  long currT = micros();
  float deltaT = ((float)(currT - prevT_i)) / 1.0e6;
  velocity_i = increment / deltaT;
  prevT_i = currT;
  //Serial.println(pos_i);
  //Serial.println(b);
  //Serial.println(b1);
}

