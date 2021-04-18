
#include <WiFi.h>
#include <HTTPClient.h>
#include "DHTesp.h"
#include "Ticker.h"

#ifndef ESP32
#pragma message(THIS EXAMPLE IS FOR ESP32 ONLY!)
#error Select ESP32 board.
#endif

// Uncomment one of the lines below for whatever DHT sensor type you're using!
#define DHTTYPE DHT11   // DHT 11
//#define DHTTYPE DHT21   // DHT 21 (AM2301)
//#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321

int dhtPin = 4;
int sensor_pin = 35;

DHTesp dht;

const char* ssid = "MAJOR PROJECT 3";
const char* password = "Prachi123";


// const char* ssid = "SD5 1";
// const char* password = "sathya@sinu5";

//Your Domain name with URL path or IP address with path
String serverName = "http://192.168.43.190:5000/input_pipe";
//String serverName = "http://192.168.0.107:5000/input_pipe";

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastTime = 0;
// Timer set to 10 minutes (600000)
//unsigned long timerDelay = 600000;
// Set timer to 5 seconds (5000)
unsigned long timerDelay = 5000;

void setup() {
  Serial.begin(115200); 

  dht.setup(dhtPin, DHTesp::DHT11);
  Serial.println("DHT initiated");
  
  
  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
 
  Serial.println("Timer set to 5 seconds (timerDelay variable), it will take 5 seconds before publishing the first reading.");
}

float temperature = 0;
float humidity = 0;
float soil_moisture = 0;

void loop() {
  TempAndHumidity newValues = dht.getTempAndHumidity();
  
  float temp_temp = newValues.temperature;
  float temp_hum = newValues.humidity;
  if((String(temp_temp)!="nan")&&(String(temp_hum)!="nan")){
    temperature = temp_temp;
    humidity = temp_hum;
   }
   int output_value= analogRead(sensor_pin);
   output_value = map(output_value,0,4095,0,100);
   soil_moisture = 100 - output_value;
   Serial.print("Mositure : ");
   Serial.print(soil_moisture);
   Serial.println("%");
   Serial.print("Temperature measured is ");
   Serial.print(temperature);
   Serial.println(" C");
   Serial.print("humidity measured is ");
   Serial.print(humidity);
   Serial.println("%");

    //Check WiFi connection status
    if(WiFi.status()== WL_CONNECTED){
      HTTPClient http;
      
      String serverPath = serverName + "?temperature="+String(temperature)+"&humidity="+String(humidity)+"&soil_moisture="+String(soil_moisture);
      Serial.print("The url is : ");
      Serial.println(serverPath);
      // Your Domain name with URL path or IP address with path
      http.begin(serverPath.c_str());
      
      // Send HTTP GET request
      int httpResponseCode = http.GET();
      
      if (httpResponseCode>0) {
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        String payload = http.getString();
        Serial.println(payload);
      }
      else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
      }
      // Free resources
      http.end();
    }
    else {
      Serial.println("WiFi Disconnected");
    }
    
}
