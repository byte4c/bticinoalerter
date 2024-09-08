#include "WiFi.h"

const int batMon = A2;
const int led = D3;
const char* ssid = "Lima1R-IoT";
const char* password = "JfbtCHy77Pv3aYQicNmdC3CfPpFxxiYJ";
const char* host = "192.168.20.10";
const int httpPort = 80;

void print_wakeup_reason() {
  esp_sleep_wakeup_cause_t wakeup_reason;

  wakeup_reason = esp_sleep_get_wakeup_cause();

  switch(wakeup_reason)
  {
    case ESP_SLEEP_WAKEUP_UNDEFINED : Serial.println("Wakeup reason undefined"); break;
    case ESP_SLEEP_WAKEUP_EXT0 : Serial.println("Wakeup caused by external signal using RTC_IO"); break;
    case ESP_SLEEP_WAKEUP_EXT1 : Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case ESP_SLEEP_WAKEUP_TIMER : Serial.println("Wakeup caused by timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD : Serial.println("Wakeup caused by touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP : Serial.println("Wakeup caused by ULP program"); break;
    case ESP_SLEEP_WAKEUP_GPIO : Serial.println("Wakeup caused by GPOI"); break;
    default : Serial.printf("Wakeup was not caused by deep sleep: %d\n",wakeup_reason); break;
  }
}

float readBattery() {
  uint32_t Vbatt = 0;
  for(int i = 0; i < 16; i++) {
    Vbatt = Vbatt + analogReadMilliVolts(batMon); // ADC with correction   
  }
  float battery = 2 * Vbatt / 16 / 1000.0;     // attenuation ratio 1/2, mV --> V
  Serial.println(battery, 3);
  return battery;
}

int readResponse(NetworkClient *client) {
  unsigned long timeout = millis();
  while (client->available() == 0) {
    if (millis() - timeout > 5000) {
      Serial.println(">>> Client Timeout !");
      client->stop();
      return 0;
    }
  }

  // Read all the lines of the reply from server and print them to Serial
  while (client->available()) {
    String line = client->readStringUntil('\r');
    Serial.print(line);
  }

  Serial.printf("\nClosing connection\n\n");
  return 1;
}
void alert(float battery) {
  for (int i = 0; i < 5; i++) {
    NetworkClient client;
    if (!client.connect(host, httpPort)) {
      continue;
    }

    client.println("GET /alert?battery=" + String(battery) + " HTTP/1.1");
    client.println("Host: " + String(host));
    client.println("Connection: close");
    client.println();  // end HTTP header
    
    int success = readResponse(&client);
    if (success == 1) {
      delay(1000);
      break;
    }
  }
}

void setup() {
  pinMode(batMon, INPUT);
  pinMode(led, OUTPUT);
  digitalWrite(led, HIGH);
  Serial.begin(115200);
  delay(1000); //Take some time to open up the Serial Monitor
  print_wakeup_reason();
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\nConnected\n\n");
  
  float battery = readBattery();
  alert(battery);

  esp_deep_sleep_enable_gpio_wakeup((BIT(D0)|BIT(D1)), ESP_GPIO_WAKEUP_GPIO_HIGH);

  //Go to sleep now
  Serial.println("Going to sleep now");
  digitalWrite(led, LOW);
  delay(2000);
  esp_deep_sleep_start();
  Serial.println("This will never be printed");
}
void loop() {
  //This is not going to be called
}