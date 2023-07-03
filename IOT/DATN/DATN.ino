#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <Servo.h>
#define sound 
Servo myservo1; // twelve servo objects can be created on most boards


bool gateOpen = true; // to keep track of gate state
int pos = 0;   // variable to store the servo position
const int trigPin1 = D7;
const int echoPin1 = D8;
const int trigPin2 = D4;
const int echoPin2 = D2;
const int coi = D1;

long duration1;
int distance1;
int safetyDistance1;

long duration2;
int distance2;
int safetyDistance2;

// Khai báo các biến 
const int switchPin1 = D5; // Chân kết nối công tắc hành trình
int switchState1 = 0; // Lưu trạng thái công tắc hành trình

// Khai báo đối tượng web server
ESP8266WebServer server(80);

void setup() {
  pinMode(switchPin1, INPUT);
  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);
  myservo1.attach(D6);
  pinMode(coi, OUTPUT);
  
  // Kết nối WiFi
  Serial.begin(115200);
  WiFi.begin("Tien 5G", "0356599038");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  delay(5000);
  // Khởi động server
  server.on("/", handleRoot);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  switchState1 = digitalRead(switchPin1);
  server.handleClient();
  
  Serial.print("GIA TRI NHAN DUOC1: ");
  Serial.println(switchState1);
  
  digitalWrite(trigPin1, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin1, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin1, LOW);
  duration1 = pulseIn(echoPin1, HIGH);
  distance1= duration1*0.034/2;
  safetyDistance1 = distance1;

  digitalWrite(trigPin2, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin2, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin2, LOW);
  duration2 = pulseIn(echoPin2, HIGH);
  distance2= duration2*0.034/2;
  safetyDistance2 = distance2;
  
  digitalWrite(coi,LOW);
  if (safetyDistance1<=5 || safetyDistance2<=4) {
      if (!gateOpen) {
        gateOpen = true;
        myservo1.write(175);
        digitalWrite(coi,HIGH);
        delay(2000);
      } else {
        gateOpen = false;
        myservo1.write(40);
        digitalWrite(coi,HIGH);
        delay(2000);
      }
    }
}

void handleRoot() {
  String html = "<meta charset='utf-8'><html><head><meta http-equiv=\"refresh\" content=\"2\"><style>body {background-color: FloralWhite;}h1   {color: blue;}font    {color: blue;}fontt    {color: red;}fonttt    {color: red;}</style><br><br><br><br><br><br><br><br><br><body><div style='background-color:#f1f1f1;padding:100px;'><font size='+5'><center>RÀO CHẮN ĐÃ: ";
  
  if (switchState1 == HIGH) {
    html += "<fonttt size='+4'>MỞ";
  } else {
    html += "<fonttt size='+4'>ĐÓNG";
  }
  html += "<br><br>";
  html += "<hr width='30%' size='10' color='Goldenrod'>";
  html += "<br>";
  html += "</h1><font size='+4'><center>THÔNG BÁO: ";
  if (safetyDistance1 <= 5) {
    html += "<fontt size='+10'>TINGGG... TÀU HỎA ĐANG ĐẾN!";
  } 

  if (safetyDistance2 <= 4) {
    html += "<fontt size='+5'>TÀU HỎA ĐÃ RỜI ĐI!";
  } 
  html += "</div></body></html>";
  server.send(200, "text/html", html);
}
