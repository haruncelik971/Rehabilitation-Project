#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>

// --- Wİ-Fİ VE BİLGİSAYAR AYARLARI ---
const char* ssid = "WIFI_ADIN";           // Bağlanacağın Wi-Fi adı
const char* password = "WIFI_SIFREN";     // Wi-Fi şifresi
const char* pc_ip = "192.168.1.100";      // Bilgisayarının yerel IP adresi
const int udpPort = 5005;

WiFiUDP udp;

// --- DONANIM PİNLERİ VE ADRESLER ---
const int MPU_ADDR = 0x68;  // MPU6050 standart I2C adresi
const int FSR_PIN = 34;     // FSR basınç sensörü analog pini (ESP32 ADC1)

// --- FİLTRE DEĞİŞKENLERİ ---
float pitch = 0.0, roll = 0.0;
unsigned long lastTime = 0;

void setup() {
  Serial.begin(115200);
  
  // I2C ve MPU6050 Başlatma (ESP32 Varsayılan: SDA=21, SCL=22)
  Wire.begin(21, 22);
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);  // Güç yönetimi register'ı
  Wire.write(0);     // MPU6050'yi uyandır
  Wire.endTransmission(true);

  // Wi-Fi Bağlantısı
  WiFi.begin(ssid, password);
  Serial.print("Wi-Fi baglaniyor");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nBaglandi! ESP32 IP: " + WiFi.localIP().toString());
  
  lastTime = millis();
}

void loop() {
  unsigned long currentTime = millis();
  float dt = (currentTime - lastTime) / 1000.0;
  lastTime = currentTime;

  // --- 1. MPU6050 VERİLERİNİ OKU ---
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 14, true);

  int16_t ax = Wire.read() << 8 | Wire.read();
  int16_t ay = Wire.read() << 8 | Wire.read();
  int16_t az = Wire.read() << 8 | Wire.read();
  Wire.read(); Wire.read(); // Sıcaklık verisini atla
  int16_t gx = Wire.read() << 8 | Wire.read();
  int16_t gy = Wire.read() << 8 | Wire.read();
  int16_t gz = Wire.read() << 8 | Wire.read();

  float accPitch = atan2(ay, sqrt(ax * ax + az * az)) * 180.0 / PI;
  float accRoll  = atan2(-ax, az) * 180.0 / PI;

  float gyroXrate = gx / 131.0;
  float gyroYrate = gy / 131.0;

  // Tamamlayıcı Filtre (%96 Jiroskop + %4 İvmeölçer)
  pitch = 0.96 * (pitch + gyroXrate * dt) + 0.04 * accPitch;
  roll  = 0.96 * (roll  + gyroYrate * dt) + 0.04 * accRoll;

  // --- 2. FSR BASINÇ SENSÖRÜNÜ OKU ---
  int rawForce = analogRead(FSR_PIN);
  int force = map(rawForce, 0, 4095, 0, 1023);

  // --- 3. JSON PAKETİ OLUŞTUR VE UDP İLE GÖNDER ---
  String jsonPayload = "{\"timestamp\":" + String(millis() / 1000.0, 2) +
                       ",\"pitch\":" + String(pitch, 2) +
                       ",\"roll\":" + String(roll, 2) +
                       ",\"force\":" + String(force) + "}";

  udp.beginPacket(pc_ip, udpPort);
  udp.print(jsonPayload);
  udp.endPacket();

  delay(33); // ~30 Hz
}