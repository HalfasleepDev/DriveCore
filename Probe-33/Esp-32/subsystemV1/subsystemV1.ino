/*
 * Probe-33 Subsystem Controller for FireBeetle ESP32
 * 
 * WIRING CONFIGURATION:
 * 
 * N-Channel MOSFETs (Fan Control):
 * - Fan positive terminals connect to +12V power supply
 * - Fan negative terminals connect to MOSFET drain pins
 * - MOSFET source pins connect to ground
 * - MOSFET gate pins connect to ESP32 PWM pins (3,5,6,9)
 * - This allows PWM control of fan speed via ground switching
 * 
 * ESP32 to Raspberry Pi Communication:
 * - Physical connection: Default UART (GPIO1/TX, GPIO3/RX)
 * - ESP32 TX (GPIO1) connects to RPi RX (GPIO15)  
 * - ESP32 RX (GPIO3) connects to RPi TX (GPIO14)
 * - Common ground connection required
 * - Baud rate: 115200
 * - Protocol: JSON status messages every 100ms
 * 
 * RPi Python code should use: serial.Serial('/dev/ttyS0', 115200)
 * Enable UART on RPi: sudo raspi-config -> Interface Options -> Serial
 * Note: USB programming will be unavailable when connected to RPi
 */
#include <Arduino.h>
#include <Wire.h>
#include <U8g2lib.h>
#include <SPI.h>

// OLED Display Setup (I2C)
#if defined ARDUINO_SAM_ZERO
#define OLED_DC  7
#define OLED_CS  5
#define OLED_RST 6
/*ESP32 */
#elif defined(ESP32)
#define OLED_DC  D2
#define OLED_CS  D6
#define OLED_RST D3
/*ESP8266*/
#elif defined(ESP8266)
#define OLED_DC  D4
#define OLED_CS  D6
#define OLED_RST D5
/*AVR series board*/
#else
#define OLED_DC  2
#define OLED_CS  3
#define OLED_RST 4
#endif
U8G2_SSD1309_128X64_NONAME2_1_4W_HW_SPI display(/* rotation=*/U8G2_R0, /* cs=*/ OLED_CS, /* dc=*/ OLED_DC,/* reset=*/OLED_RST);

// Pin Definitions
// Battery Box 1 - N-MOSFETs control fan ground switching
#define TEMP1_BOX1_PIN A0
#define TEMP2_BOX1_PIN A1
#define FAN1_BOX1_MOSFET_PIN D10  // Controls ground switching for Fan 1
#define FAN2_BOX1_MOSFET_PIN D11  // Controls ground switching for Fan 2

// Battery Box 2 - N-MOSFETs control fan ground switching  
#define TEMP1_BOX2_PIN A2
#define TEMP2_BOX2_PIN A3
#define FAN1_BOX2_MOSFET_PIN D12  // Controls ground switching for Fan 1
#define FAN2_BOX2_MOSFET_PIN D13  // Controls ground switching for Fan 2

// Water Detection
#define WATER_SENSOR_PIN A4

// Wiper Motor (L9110s H-Bridge)
#define WIPER_PIN1 D9
#define WIPER_PIN2 D7

// Wiper End Switch
#define WIPER_END_SWITCH_PIN D5

// Communication with Raspberry Pi via default UART
#define SERIAL_BAUD 115200
#define RPI_RX_PIN RX       // ESP32 RX pin connected to RPi TX
#define RPI_TX_PIN TX       // ESP32 TX pin connected to RPi RX

// Temperature thresholds (Celsius)
#define TEMP_THRESHOLD_LOW 20.0
#define TEMP_THRESHOLD_HIGH 45.0
#define TEMP_CRITICAL 55.0

// Water detection threshold
#define WATER_THRESHOLD 2000

// Display page switching
#define PAGE_STATUS 0
#define PAGE_MESSAGES 1
#define PAGE_SWITCH_INTERVAL 10000  // Switch pages every 10 seconds

// Timing variables
unsigned long lastTempCheck = 0;
unsigned long lastWaterCheck = 0;
unsigned long lastDisplayUpdate = 0;
unsigned long lastCommUpdate = 0;
unsigned long lastWiperCheck = 0;
unsigned long lastPageSwitch = 0;
bool wiperEndSwitchPrev = false;    // Previous state of end switch
int wiperCycleCount = 0;            // Number of home crossings (sweeps)
int wiperTargetCycles = 1;          // Sweeps per activation (change as needed)
bool wiperParking = false;          // True when parking at home
unsigned long wiperDebounceTime = 0;
const unsigned long WIPER_DEBOUNCE_MS = 50;  // Debounce for end switch

// Intervals (milliseconds)
const unsigned long TEMP_INTERVAL = 1000;
const unsigned long WATER_INTERVAL = 500;
const unsigned long DISPLAY_INTERVAL = 250;
const unsigned long COMM_INTERVAL = 100;
const unsigned long WIPER_INTERVAL = 50;

// System state variables
struct BatteryBox {
  float temp1;
  float temp2;
  int fan1Speed;
  int fan2Speed;
  bool overheating;
};

BatteryBox box1, box2;
bool waterDetected = false;
bool wiperActive = false;
bool wiperMoved = false;
String displayMessage = "System Ready";
String commBuffer = "";

// Display page management
int currentPage = PAGE_STATUS;
String systemMessages[5] = {"", "", "", "", ""};  // Circular buffer for messages
int messageIndex = 0;
int messageCount = 0;

void setup() {
  Serial.begin(SERIAL_BAUD, SERIAL_8N1, RPI_RX_PIN, RPI_TX_PIN);        // Default Serial for RPi communication

  // Initialize display
  display.begin();
  //display.setFontPosTop();

  display.firstPage();
  do {
    display.clearBuffer();
    display.setFont(u8g2_font_haxrcorp4089_tr);
    display.drawStr(12, 11, "DriveCore Subsystem OS");
    display.drawStr(12, 23, "Ver   1.0.0");
    display.drawStr(41, 41, "Initializing...");
    display.sendBuffer();
  } while (display.nextPage());
  
  // Initialize N-MOSFET control pins (LOW = fan off, HIGH = fan on)
  pinMode(FAN1_BOX1_MOSFET_PIN, OUTPUT);
  pinMode(FAN2_BOX1_MOSFET_PIN, OUTPUT);
  pinMode(FAN1_BOX2_MOSFET_PIN, OUTPUT);
  pinMode(FAN2_BOX2_MOSFET_PIN, OUTPUT);
  
  // Ensure all fans start OFF
  digitalWrite(FAN1_BOX1_MOSFET_PIN, LOW);
  digitalWrite(FAN2_BOX1_MOSFET_PIN, LOW);
  digitalWrite(FAN1_BOX2_MOSFET_PIN, LOW);
  digitalWrite(FAN2_BOX2_MOSFET_PIN, LOW);
  
  pinMode(WIPER_PIN1, OUTPUT);
  pinMode(WIPER_PIN2, OUTPUT);

  pinMode(WIPER_END_SWITCH_PIN, INPUT_PULLUP);

  
  // Initialize system state
  box1 = {0, 0, 0, 0, false};
  box2 = {0, 0, 0, 0, false};
  
  // Add initial system message
  addSystemMessage("System Online");
  
  delay(5000);
  displayMessage = "System Online";
}

void loop() {
  unsigned long currentTime = millis();
  
  // Temperature monitoring and fan control
  if (currentTime - lastTempCheck >= TEMP_INTERVAL) {
    checkTemperatures();
    controlFans();
    lastTempCheck = currentTime;
  }
  
  // Water detection
  if (currentTime - lastWaterCheck >= WATER_INTERVAL) {
    checkWaterSensor();
    lastWaterCheck = currentTime;
  }
  
  // Wiper control
  if (currentTime - lastWiperCheck >= WIPER_INTERVAL) {
    controlWiper();
    lastWiperCheck = currentTime;
  }
  
  // Page switching for burn-in prevention
  if (currentTime - lastPageSwitch >= PAGE_SWITCH_INTERVAL) {
    currentPage = (currentPage == PAGE_STATUS) ? PAGE_MESSAGES : PAGE_STATUS;
    lastPageSwitch = currentTime;
  }
  
  // Display update
  if (currentTime - lastDisplayUpdate >= DISPLAY_INTERVAL) {
    updateDisplay();
    lastDisplayUpdate = currentTime;
  }
  
  // Communication with Raspberry Pi
  if (currentTime - lastCommUpdate >= COMM_INTERVAL) {
    handleCommunication();
    lastCommUpdate = currentTime;
  }
}

void checkTemperatures() {
  // Read LM35 sensors (10mV per degree Celsius)
  box1.temp1 = (analogRead(TEMP1_BOX1_PIN) * 3.3 / 4095.0) * 100.0;
  box1.temp2 = (analogRead(TEMP2_BOX1_PIN) * 3.3 / 4095.0) * 100.0;
  box2.temp1 = (analogRead(TEMP1_BOX2_PIN) * 3.3 / 4095.0) * 100.0;
  box2.temp2 = (analogRead(TEMP2_BOX2_PIN) * 3.3 / 4095.0) * 100.0;
  
  // Check for overheating
  box1.overheating = (box1.temp1 > TEMP_CRITICAL || box1.temp2 > TEMP_CRITICAL);
  box2.overheating = (box2.temp1 > TEMP_CRITICAL || box2.temp2 > TEMP_CRITICAL);
  
  // Log temperature warnings
  if (box1.overheating) {
    addSystemMessage("WARNING: Box 1 Overheating!");
  }
  if (box2.overheating) {
    addSystemMessage("WARNING: Box 2 Overheating!");
  }
}

void controlFans() {
  // Box 1 Fan Control - N-MOSFETs switch ground connection
  box1.fan1Speed = calculateFanSpeed(box1.temp1);
  box1.fan2Speed = calculateFanSpeed(box1.temp2);
  
  // For N-MOSFETs controlling ground: PWM controls switching frequency
  // Higher PWM = more on-time = higher effective fan speed
  analogWrite(FAN1_BOX1_MOSFET_PIN, box1.fan1Speed);
  analogWrite(FAN2_BOX1_MOSFET_PIN, box1.fan2Speed);
  
  // Box 2 Fan Control
  box2.fan1Speed = calculateFanSpeed(box2.temp1);
  box2.fan2Speed = calculateFanSpeed(box2.temp2);
  analogWrite(FAN1_BOX2_MOSFET_PIN, box2.fan1Speed);
  analogWrite(FAN2_BOX2_MOSFET_PIN, box2.fan2Speed);
}

int calculateFanSpeed(float temperature) {
  static int lastState = 0; // 0 = off, 255 = on

  if (temperature < TEMP_THRESHOLD_LOW - 1) {
    lastState = 0;    // Fan off
  } else if (temperature > TEMP_THRESHOLD_LOW + 1) {
    lastState = 255;  // Fan on
  }
  return lastState;
}

void checkWaterSensor() {
  int sensorValue = analogRead(WATER_SENSOR_PIN);
  bool previousWaterState = waterDetected;
  waterDetected = (sensorValue > WATER_THRESHOLD);
  
  // Activate wiper if water is detected
  if (waterDetected && !previousWaterState) {
    // Water just detected: start wiper normally
    wiperActive = true;
    wiperCycleCount = 0;
    wiperParking = false;
    displayMessage = "Water Detected!";
    addSystemMessage("Water Detected - Wiper Active");
  } else if (!waterDetected && previousWaterState) {
    // Water just cleared: park the wiper
    wiperParking = true;
    wiperActive = true; // Ensures parking logic will run in controlWiper
    displayMessage = "Water Cleared - Parking";
    addSystemMessage("Water Cleared - Wiper Parking");
  }
}

void controlWiper() {
    bool endSwitchPressed = digitalRead(WIPER_END_SWITCH_PIN) == LOW;  // LOW = home
    unsigned long now = millis();

    // Debounced rising edge detection (only count once per crossing)
    bool endSwitchEdge = false;
    if (endSwitchPressed && !wiperEndSwitchPrev && (now - wiperDebounceTime > WIPER_DEBOUNCE_MS)) {
        wiperDebounceTime = now;
        endSwitchEdge = true;
    }
    wiperEndSwitchPrev = endSwitchPressed;

    // If a sweep is starting, reset counters
    if (wiperActive && wiperCycleCount == 0 && !wiperParking && endSwitchPressed) {
        // Starting from home, don't count as a cycle yet, wait until it leaves and returns
        // Optional: You can display "Wiper starting from home" here
    }

    if (wiperActive) {
        if (!wiperParking) {
            // If in the middle of sweeping
            if (endSwitchEdge) {
                wiperCycleCount++;
                addSystemMessage("Wiper: Home position detected");
                // Check if done with target sweeps
                if (wiperCycleCount >= wiperTargetCycles) {
                    wiperParking = true;
                }
            }
            // Run motor (edit for your H-bridge logic!)
            analogWrite(WIPER_PIN1, 180); // PWM for speed (adjust value if needed)
            digitalWrite(WIPER_PIN2, LOW);
            wiperMoved = true;
        } else {
            // Parking at home after all sweeps complete
            if (endSwitchPressed) {
                // Home reached: stop and park
                analogWrite(WIPER_PIN1, 0);   // Stop motor
                digitalWrite(WIPER_PIN2, LOW);
                wiperActive = false;
                wiperParking = false;
                wiperMoved = false;
                wiperCycleCount = 0;
                displayMessage = "Wiper Parked";
                addSystemMessage("Wiper parked at home");
            } else {
                // Still not home: keep moving!
                analogWrite(WIPER_PIN1, 180);
                digitalWrite(WIPER_PIN2, LOW);
            }
        }
    } else {
        // Wiper inactive: make sure it's stopped
        analogWrite(WIPER_PIN1, 0);
        digitalWrite(WIPER_PIN2, LOW);

        if (wiperMoved) {
            wiperMoved = false;
            displayMessage = "System Normal";
            addSystemMessage("Wiper Deactivated");
        }
        wiperParking = false;
        wiperCycleCount = 0;
    }
}

void addSystemMessage(String message) {
  systemMessages[messageIndex] = message;
  messageIndex = (messageIndex + 1) % 5;
  if (messageCount < 5) {
    messageCount++;
  }
}

void updateDisplay() {
  display.firstPage();
  do {
    display.clearBuffer();
    display.setFont(u8g2_font_haxrcorp4089_tr);
    
    if (currentPage == PAGE_STATUS) {
      drawStatusPage();
    } else {
      drawMessagesPage();
    }
    
    display.sendBuffer();
  } while (display.nextPage());
}

void drawStatusPage() {
  // Title with page indicator
  display.drawStr(14, 9, "Probe-33 Status [1/2]");
  display.drawLine(0, 12, 127, 12);
  
  // Temperature info
  char tempStr[32];
  sprintf(tempStr, "B1: %.1f %.1f C", box1.temp1, box1.temp2);
  display.drawStr(4, 22, tempStr);
  sprintf(tempStr, "B2: %.1f %.1f C", box2.temp1, box2.temp2);
  display.drawStr(4, 31, tempStr);
  
  // Fan speeds
  sprintf(tempStr, "F1: %d %d", box1.fan1Speed, box1.fan2Speed);
  display.drawStr(73, 22, tempStr);
  sprintf(tempStr, "F2: %d %d", box2.fan1Speed, box2.fan2Speed);
  display.drawStr(73, 31, tempStr);
  
  // Water and wiper status
  display.drawStr(43, 41, waterDetected ? "Water: YES" : "Water: NO");
  display.drawStr(43, 51, wiperActive ? "Wiper: ON" : "Wiper: OFF");
  
  // Warning indicators
  if (box1.overheating || box2.overheating) {
    display.drawStr(6, 45, "HOT!");
  }
}

void drawMessagesPage() {
  // Title with page indicator
  display.drawStr(12, 9, "System Messages [2/2]");
  display.drawLine(0, 12, 127, 12);
  
  // Display recent messages (up to 5)
  int yPos = 22;
  int displayCount = min(messageCount, 3);  // Show max 4 messages to fit screen
  
  for (int i = 0; i < displayCount; i++) {
    int msgIdx = (messageIndex - displayCount + i + 5) % 5;
    if (systemMessages[msgIdx].length() > 0) {
      // Truncate long messages to fit screen
      String msg = systemMessages[msgIdx];
      if (msg.length() > 23) {
        msg = msg.substring(0, 17) + "...";
      }
      display.drawStr(1, yPos, msg.c_str());
      yPos += 10;
    }
  }
  
  // Show current status at bottom
  display.drawStr(0, 53, displayMessage.c_str());
}

void handleCommunication() {
  // Send status to Raspberry Pi via default Serial
  sendStatusToRPi();
  
  // Check for incoming commands from Raspberry Pi
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
}

void sendStatusToRPi() {
  // Create JSON-like status message and send to Raspberry Pi
  Serial.print("{");
  Serial.print("\"box1_temp1\":");
  Serial.print(box1.temp1);
  Serial.print(",\"box1_temp2\":");
  Serial.print(box1.temp2);
  Serial.print(",\"box2_temp1\":");
  Serial.print(box2.temp1);
  Serial.print(",\"box2_temp2\":");
  Serial.print(box2.temp2);
  Serial.print(",\"box1_fan1\":");
  Serial.print(box1.fan1Speed);
  Serial.print(",\"box1_fan2\":");
  Serial.print(box1.fan2Speed);
  Serial.print(",\"box2_fan1\":");
  Serial.print(box2.fan1Speed);
  Serial.print(",\"box2_fan2\":");
  Serial.print(box2.fan2Speed);
  Serial.print(",\"water_detected\":");
  Serial.print(waterDetected ? "true" : "false");
  Serial.print(",\"wiper_active\":");
  Serial.print(wiperActive ? "true" : "false");
  Serial.print(",\"box1_overheating\":");
  Serial.print(box1.overheating ? "true" : "false");
  Serial.print(",\"box2_overheating\":");
  Serial.print(box2.overheating ? "true" : "false");
  Serial.print(",\"current_page\":");
  Serial.print(currentPage);
  Serial.println("}");
}

void processCommand(String command) {
  if (command.startsWith("MSG:")) {
    // Update display message and add to system messages
    displayMessage = command.substring(4);
    addSystemMessage(displayMessage);
  } else if (command == "WIPER_ON") {
    wiperActive = true;
    wiperCycleCount = 0;
    wiperParking = false;
    // Optionally set wiperTargetCycles = N; // For N sweeps per trigger
    addSystemMessage("Wiper Manual ON");
  } else if (command == "WIPER_OFF") {
    wiperParking = true;
    wiperActive = true; // Ensure the parking logic runs in controlWiper
    addSystemMessage("Wiper Manual OFF - Parking");
  } else if (command == "STATUS") {
    // Force immediate status send
    sendStatusToRPi();
  } else if (command == "PAGE_STATUS") {
    // Force switch to status page
    currentPage = PAGE_STATUS;
    lastPageSwitch = millis();
  } else if (command == "PAGE_MESSAGES") {
    // Force switch to messages page
    currentPage = PAGE_MESSAGES;
    lastPageSwitch = millis();
  } else if (command.startsWith("TEMP_THRESH:")) {
    // Allow dynamic temperature threshold adjustment
    float newThresh = command.substring(12).toFloat();
    addSystemMessage("Temp threshold updated");
    // Implement threshold updates here
  }
}