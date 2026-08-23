#include <math.h>

// ================= PIN DEFINITIONS =================
const int M1 = 5;   // PWM Pin (Speed) - Must be PWM capable!
const int M2 = 7;   // Direction Pin
const int S1 = 2;   // Encoder A
const int S2 = 3;   // Encoder B

// ================= SYSTEM CONSTANTS =================
// UPDATE THIS: (Encoder CPR) * (Gear Ratio) / (2 * PI)
// Example: 12 CPR * 50:1 Ratio = 600 counts per rev
const float COUNTS_PER_RAD = 600.0 / 6.2831853; 

const float VOLT_LIMIT = 12.0;  // Max voltage of your power supply
const float DT = 0.005;         // Sample time 5ms (200Hz)

// ================= STATE VARIABLES =================
volatile long pos_i = 0; 
float theta = 0.0;      // Plant Position [rad]
float omega = 0.0;      // Plant Speed [rad/s]
float theta_prev = 0.0;

// Reference Model States (2nd Order)
float thm = 0.0;        // Model Position
float wm = 0.0;         // Model Speed

// Model Parameters (From MATLAB)
const float wn_m = 3.0;     
const float zeta_m = 1.8;   
const float a_m = -(wn_m * wn_m); // Simplified coeffs for update
const float b_m = -(2.0 * zeta_m * wn_m);

// ================= ADAPTIVE PARAMETERS =================
// Theta_mrac = [k_theta; k_omega; k_ref; bias; fric]
// We use individual variables for clarity
float k_theta = 0.0;
float k_omega = 0.0;
float k_ref   = 0.0; // Init near ideal if possible (e.g. 1.0)
float w_bias  = 0.0;
float w_fric  = 0.0;

// Tuning (Matches MATLAB)
const float GAMMA = 20.0;    // Adaptation Gain
const float SIGMA = 0.001;   // Leakage
const float DEADZONE = 0.001; 
const float THETA_MAX = 50.0;

// Timing
unsigned long lastTimeUs = 0;

void setup() {
  // Pin Setup
  pinMode(M1, OUTPUT);
  pinMode(M2, OUTPUT);
  pinMode(S1, INPUT_PULLUP);
  pinMode(S2, INPUT_PULLUP);
  
  // Interrupt for Encoder
  attachInterrupt(digitalPinToInterrupt(S1), readEncoder, RISING);
  
  // Initialization
  // Initialize k_ref to a small positive value to help startup
  k_ref = 0.5; 
  
  Serial.begin(115200);
  //Serial.println("Time,Ref,Model,Theta,PWM,Error");
}

// ================= REFERENCE GENERATOR =================
// ================= REFERENCE GENERATOR =================
float getReference(float t) {
  // Define step duration (how long to wait before moving next)
  float step_duration = 5.0; // e.g., move every 5 seconds
  float step_size = 1.0;     // Move +1.0 rad each time
  
  // Calculate which step we are on (0, 1, 2, 3...)
  // "floor" rounds down to the nearest integer
  int step_number = (int)floor(t / step_duration);
  
  // Target = Step Number * Step Size
  return (float)step_number * step_size;
}

// ================= MAIN LOOP =================
void loop() {
  unsigned long nowUs = micros();
  
  if (nowUs - lastTimeUs >= (unsigned long)(DT * 1000000.0)) {
    lastTimeUs = nowUs;
    float t = millis() / 1000.0;
    
    // --- 1. READ PLANT STATE ---
    noInterrupts();
    long currPos = pos_i;
    interrupts();
    
    theta = (float)currPos / COUNTS_PER_RAD;
    
    // Calculate Omega (Derivative + Low Pass Filter)
    float raw_omega = (theta - theta_prev) / DT;
    omega = 0.85 * omega + 0.15 * raw_omega; // Simple LPF
    theta_prev = theta;
    
    // --- 2. UPDATE REFERENCE MODEL ---
    float r = getReference(t);
    
    // MATLAB Eq: wm_dot = wn^2*r - 2*z*wn*wm - wn^2*thm
    float wm_dot = (wn_m*wn_m)*r - (2.0*zeta_m*wn_m)*wm - (wn_m*wn_m)*thm;
    
    // Euler Integration
    thm += wm * DT;
    wm  += wm_dot * DT;
    
    // --- 3. CALCULATE ERROR ---
    float e_pos = theta - thm;
    float e_vel = omega - wm;
    // Mixed Error Surface (matches MATLAB "e_mix")
    float e_mix = e_pos + 1.0 * e_vel;
    
    // --- 4. CONTROL LAW (Vector MRAC) ---
    // Regressors
    float phi_th = theta;
    float phi_w  = omega;
    float phi_r  = r;
    float phi_bias = -1.0;       // Negative sign per standard cancellation logic
    float phi_fric = -tanh(omega); // Hyperbolic tangent for friction
    
    // u = K*x + Wh*Phi
    float u = (k_theta * phi_th) + 
              (k_omega * phi_w) + 
              (k_ref   * phi_r) + 
              (w_bias  * phi_bias) + 
              (w_fric  * phi_fric);
              
    // --- 5. ROBUST ADAPTATION ---
    // Normalization Factor: 1 + phi^T * phi
    float norm = 1.0 + (phi_th*phi_th) + (phi_w*phi_w) + (phi_r*phi_r) + 
                 (phi_bias*phi_bias) + (phi_fric*phi_fric);
                 
    if (abs(e_mix) > DEADZONE) {
       // Common Learning Rate Term: -(Gamma / Norm) * Error
       // NOTE: We assume sign(b_p) is Positive. If motor reversed, flip sign.
       float rate = -(GAMMA / norm) * e_mix;
       
       // Parameter Updates (Euler + Sigma Mod)
       k_theta += (rate * phi_th - SIGMA * k_theta) * DT;
       k_omega += (rate * phi_w  - SIGMA * k_omega) * DT;
       k_ref   += (rate * phi_r  - SIGMA * k_ref)   * DT;
       w_bias  += (rate * phi_bias - SIGMA * w_bias)* DT;
       w_fric  += (rate * phi_fric - SIGMA * w_fric)* DT;
       
       // Projection (Clamping)
       k_theta = constrain(k_theta, -THETA_MAX, THETA_MAX);
       k_omega = constrain(k_omega, -THETA_MAX, THETA_MAX);
       k_ref   = constrain(k_ref,   -THETA_MAX, THETA_MAX);
       w_bias  = constrain(w_bias,  -THETA_MAX, THETA_MAX);
       w_fric  = constrain(w_fric,  -THETA_MAX, THETA_MAX);
    }
    
    // --- 6. ACTUATION ---
    // Clamp Voltage
    float u_clamped = constrain(u, -VOLT_LIMIT, VOLT_LIMIT);
    
    // Convert Voltage to PWM (0-255)
    // Map: 0V -> 0, VOLT_LIMIT -> 255
    int pwm_out = (int)(abs(u_clamped) / VOLT_LIMIT * 255.0);
    pwm_out = constrain(pwm_out, 0, 255);
    
    // Direction Logic
    if (u_clamped > 0) {
      digitalWrite(M2, LOW);      // Forward
      analogWrite(M1, pwm_out);
    } else {
      digitalWrite(M2, HIGH);     // Reverse
      analogWrite(M1, pwm_out);
    }
    
    // --- 7. LOGGING ---
    //Serial.print(t); Serial.print(",");
    //Serial.print(r); Serial.print(",");
    Serial.print(thm); 
    Serial.print("\n");
    Serial.print(theta); 
    Serial.print("\n");
    //Serial.print(u_clamped); Serial.print(",");
    //Serial.println(e_pos);
  }
}

// ================= ENCODER ISR =================
void readEncoder() {
  int b = digitalRead(S2);
  if (b > 0) {
    pos_i++;
  } else {
    pos_i--;
  }
}