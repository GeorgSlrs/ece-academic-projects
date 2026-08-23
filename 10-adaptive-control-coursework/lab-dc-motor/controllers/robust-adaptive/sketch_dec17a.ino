/* ===================== PIN DEFINITIONS =====================
   You said “don’t change the ports” — so keep these as you already use them.
   NOTE: M1 must be a PWM-capable pin if you really want PWM output.
*/
const int M1 = 7;   // Motor terminal 1  (PWM pin recommended)
const int M2 = 5;   // Motor terminal 2  (direction or second terminal)

// Encoder / speed feedback (quadrature A/B)
const int S1 = 2;   // Encoder channel A (interrupt)
const int S2 = 3;   // Encoder channel B (read inside ISR)

// ===================== YOUR ORIGINAL VARIABLES (kept) =====================

// Encoder state
volatile long pos_i = 0;          // MUST be signed for direction
volatile unsigned long prevT_i = 0;
volatile float velocity_i = 0.0f; // use float, not unsigned long

unsigned long prevT = 0;
long posPrev = 0;

// Filtered speed
float v1Filt = 0.0f;
float v1Prev = 0.0f;

int targetPWM = 208; // 0=stop, 255=full speed (as in your code)

// Plant/model parameters (kept)
float a = 1.203;     // Plant parameter (used only for internal model yp)
float b = 0.1514;
float am = 2.0;      // Reference model parameter
float bm = 0.2;

float gammaVal = 0.02;   // Adaptation gain
float u = 0.0;

// Internal model vars (kept)
float yp = 0.0;      // internal plant model output (optional)
float ym = 0.0;      // reference model output

// ADI adaptive parameters (kept)
float theta1 = 0.0;  // ~ a_hat
float theta2 = 0.0;  // ~ b_hat

float e0 = 0.0;
float thres = 0.9;   // projection bound (kept)

// Sampling (kept)
float dt = 0.001;                 // [s]
unsigned long lastControlUs = 0;   // scheduler in micros

// ===================== NEW: MODE SWITCHES =====================
enum CtrlMode { CTRL_ADI = 0, CTRL_MRAC = 1 };
const CtrlMode CTRL_MODE = CTRL_ADI;   // <-- set CTRL_ADI or CTRL_MRAC

enum RefMode { REF_STEP = 0, REF_SINE = 1, REF_STEP_LONG = 2 };
const RefMode REF_MODE = REF_STEP;     // <-- choose STEP / SINE / STEP_LONG

// ===================== NEW: ROBUSTIFYING OPTIONS =====================

// deadzone threshold (rad/s or rpm depending on your v1Filt units)
const float deadzone_eps = 0.9f;  // start near your noise level

// sigma / e-mod leakage
const float sigma0 = 0.02f;
const float sigmaE = 0.00f;       // set >0 for e-mod: sigma = sigma0 + sigmaE*|e|

// normalization offset
const float norm0 = 1.0f;

// avoid division by tiny b_hat
const float b_hat_min_abs = 0.01f;

// MRAC parameters (NEW): u = th_r*r + th_y*(-y) + th_b*1
float th_r = 0.0f;
float th_y = 0.0f;
float th_b = 0.0f;

// for logging
unsigned long lastPrintMs = 0;
const unsigned long printEveryMs = 20; // 50 Hz printing

// ===================== REFERENCE FUNCTION =====================
float reference(float t_sec) {
  switch (REF_MODE) {
    case REF_STEP:
      // multi-step schedule (edit levels)
      if (t_sec < 1.0f) return 168;
      if (t_sec < 4.0f) return 188;
      if (t_sec < 7.0f) return 148;
      return 208;

    case REF_STEP_LONG:
      // hold constant for a long time (exercise requirement)
      if (t_sec < 1.0f) return 168;
      return 208; // hold

    case REF_SINE:
      // slow sinusoid (edit amplitude/freq)
      // IMPORTANT: choose slow enough not to saturate, but rich enough for PE
      return 168.0f + 40.0f * sinf(0.1f * t_sec); // your original example

    default:
      return 168;
  }
}

// ===================== UTILITIES =====================
static inline float clampf(float x, float lo, float hi) {
  if (x < lo) return lo;
  if (x > hi) return hi;
  return x;
}

static inline float sigmaEff(float e) {
  return sigma0 + sigmaE * fabsf(e);
}

// ===================== ENCODER ISR =====================
// Use S1 as channel A interrupt, read S2 as channel B for direction
void readEncoder() {
  int b = digitalRead(S2);          // direction from channel B
  int increment = (b > 0) ? +1 : -1;

  pos_i += increment;

  unsigned long currT = micros();
  float deltaT = (currT - prevT_i) * 1e-6f;
  if (deltaT > 1e-6f) {
    velocity_i = (float)increment / deltaT; // counts/sec (signed)
  }
  prevT_i = currT;
}

// ===================== SETUP =====================
void setup() {
  pinMode(M1, OUTPUT);
  pinMode(M2, OUTPUT);

  pinMode(S1, INPUT_PULLUP);
  pinMode(S2, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(S1), readEncoder, RISING);

  Serial.begin(115200);
  // CSV header
  //Serial.println("t,r,ym,y,u,mode,e,a_hat,b_hat,th_r,th_y,th_b,phi1,phi2,phi3");
}

// ===================== MAIN LOOP =====================
void loop() {
  // ---------- 1) Speed estimation (your style) ----------
  long pos = 0;
  noInterrupts();
  pos = pos_i;
  interrupts();

  unsigned long currT = micros();
  float deltaT = (currT - prevT) * 1e-6f;
  if (deltaT <= 1e-6f) deltaT = 1e-6f;

  float velocity1 = (pos - posPrev) / deltaT; // counts/sec (signed)
  posPrev = pos;
  prevT = currT;

  // your conversion (kept): counts/sec -> rpm (you used 2086 counts/rev)
  velocity1 = velocity1 / 2086.0f * 60.0f;

  // your IIR filter (kept), but using float
  v1Filt = 0.854f * v1Filt + 0.0728f * velocity1 + 0.0728f * v1Prev;
  v1Prev = velocity1;

  // ---------- 2) Controller scheduler (dt seconds) ----------
  unsigned long nowUs = micros();
  unsigned long controlPeriodUs = (unsigned long)(dt * 1e6f);

  if (nowUs - lastControlUs >= controlPeriodUs) {
    lastControlUs = nowUs;

    float t = millis() / 1000.0f;   // seconds (ok for reference timing)

    // (a) Reference input
    float r = reference(t);

    // (b) Reference model update: ym_dot = -am*ym + bm*r
    float dym = -am * ym + bm * r;
    ym += dym * dt;

    // (c) Tracking error (measured output is v1Filt)
    e0 = v1Filt - ym;

    // (d) Robust adaptation gating
    bool adapt_on = (fabsf(e0) >= deadzone_eps);
    float sig = sigmaEff(e0);

    // (e) Choose controller
    if (CTRL_MODE == CTRL_ADI) {
      // ================= ADI CONTROL =================
      // u = ((am - a_hat)*y + bm*r) / b_hat
      float b_hat_safe = theta2;
      if (fabsf(b_hat_safe) < b_hat_min_abs) {
        b_hat_safe = (b_hat_safe >= 0.0f) ? b_hat_min_abs : -b_hat_min_abs;
      }

      u = ((am - theta1) * v1Filt + bm * r) / b_hat_safe;

      // ---- (optional) internal plant model yp update (kept) ----
      float dyp = -a * yp + b * u;
      yp += dyp * dt;

      // ---- ADI adaptation laws (robustified + normalized) ----
      // basic (your version): theta1_dot = gamma*y*e , theta2_dot = gamma*u*e
      // add normalization + sigma leakage:
      float denom = norm0 + v1Filt * v1Filt + u * u;

      float dtheta1 = 0.0f;
      float dtheta2 = 0.0f;

      if (adapt_on) {
        dtheta1 = (gammaVal / denom) * (v1Filt * e0) - sig * theta1;
        dtheta2 = (gammaVal / denom) * (u      * e0) - sig * theta2;
      } else {
        // even when not adapting, you can still apply leakage (optional)
        dtheta1 = -sig * theta1 * 0.0f; // set to 1.0f if you want leakage always on
        dtheta2 = -sig * theta2 * 0.0f;
      }

      theta1 = clampf(theta1 + dtheta1 * dt, -thres, thres); // projection
      theta2 = clampf(theta2 + dtheta2 * dt, -thres, thres); // projection

    } else {
      // ================= MRAC (DIRECT) =================
      // u = th_r * r + th_y * (-y) + th_b * 1
      float phi1 = r;
      float phi2 = -v1Filt;
      float phi3 = 1.0f;

      u = th_r * phi1 + th_y * phi2 + th_b * phi3;

      // robust normalized gradient update:
      // th_dot = -(gamma/denom) * phi * e - sigma*th
      float denom = norm0 + phi1*phi1 + phi2*phi2 + phi3*phi3;

      float dthr = 0.0f, dthy = 0.0f, dthb = 0.0f;
      if (adapt_on) {
        float g = -(gammaVal / denom) * e0;
        dthr = g * phi1 - sig * th_r;
        dthy = g * phi2 - sig * th_y;
        dthb = g * phi3 - sig * th_b;
      }

      th_r = clampf(th_r + dthr * dt, -thres, thres);
      th_y = clampf(th_y + dthy * dt, -thres, thres);
      th_b = clampf(th_b + dthb * dt, -thres, thres);

      // keep theta1/theta2 as-is (they belong to ADI)
    }

    // (f) Convert u -> PWM command (your style)
    // targetPWM = min(128+u, 250);  (also clamp low)
    float pwm_cmd = 128.0f + u;
    pwm_cmd = clampf(pwm_cmd, 0.0f, 250.0f);
    targetPWM = (int)(pwm_cmd);

    // (g) Logging at ~50 Hz
    unsigned long nowMs = millis();
    if (nowMs - lastPrintMs >= printEveryMs) {
      lastPrintMs = nowMs;

      // MRAC regressor (for PE checks offline)
      float phi1 = r;
      float phi2 = -v1Filt;
      float phi3 = 1.0f;

      
      Serial.print(-v1Filt);
      Serial.print("\n");
    }
  }

  // ---------- 3) Apply motor command (your wiring style) ----------
  // Forward-only style (kept):
  analogWrite(M1, targetPWM);
  digitalWrite(M2, LOW);

  // IMPORTANT: remove big delays if you want dt=0.001 to actually happen.
  // Your old delay(100) makes the controller run ~10 Hz no matter what dt is.
  // So we do NOT delay here.
}
