#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Preferences.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <cmath>

// ==========================================
// 1. WIFI CONFIGURATION
// ==========================================

const char* WIFI_SSID = "An";
const char* WIFI_PASSWORD = "13062005";

// ==========================================
// 2. SENSOR CONFIGURATION
// ==========================================

// Hai MPU-6050 cùng địa chỉ, mỗi module trên một bus I2C riêng.
const uint8_t MPU_ADDRESS = 0x68;
const unsigned long SAMPLE_INTERVAL_MS = 50UL;
const unsigned long MPU_RETRY_MS = 500UL;
const uint8_t MPU_MISSES_TO_DISCONNECT = 3;
// Node 1: each test GPIO connects through 47 kOhm to its ESP-side signal row.
const int SOIL_TEST_PIN = 23;
const int VIBRATION_TEST_PIN = 25;
const unsigned long RELAY_HOLD_MS = 2000UL;
const bool VIBRATION_ACTIVE_LOW = false;
const unsigned long VIBRATION_HOLD_MS = 3000UL;
const float SOIL_FILTER_ALPHA = 0.12f;
const unsigned long SOIL_TREND_INTERVAL_MS = 10000UL;
const uint8_t SOIL_TREND_HISTORY_SIZE = 7; // 7 mốc cách nhau 10 giây ~= 60 giây
const unsigned long CALIBRATION_DURATION_MS = 8000UL;
const float TILT_DEADBAND_DEG = 2.0f;
const float MOISTURE_HIGH_THRESHOLD = 90.0f;
const float MOISTURE_RESET_THRESHOLD = 88.0f; // hysteresis chống nhấp nháy
const unsigned long MOISTURE_CONFIRM_MS = 5000UL;
const float MOISTURE_WEIGHT = 0.60f;
const float TILT_WEIGHT = 0.30f;
const float VIBRATION_WEIGHT = 0.10f;
const float SENSOR_FILTER_ALPHA = 0.18f;
const float TILT_FILTER_ALPHA = 0.20f;

WebServer server(80);

struct TiltBaseline {
    float gravityX, gravityY, gravityZ;
    float roll, pitch;
};

struct SensorNode {
    const char* id;
    const char* name;
    const char* baselineNamespace;
    int soilPin, vibrationPin, sdaPin, sclPin;
    TwoWire& wire;
    int soilDryRaw, soilWetRaw;

    Adafruit_MPU6050 mpu;
    Preferences preferences;
    bool mpuOK = false;
    bool signalsOK = false;
    bool online() const { return mpuOK && signalsOK; }

    int soilRaw = 0;
    float soilPercent = 0.0f; // phần trăm quy đổi đã làm mịn
    bool soilFilterInitialized = false;
    float soilTrendHistory[SOIL_TREND_HISTORY_SIZE] = {0};
    unsigned long soilTrendTimes[SOIL_TREND_HISTORY_SIZE] = {0};
    uint8_t soilTrendIndex = 0;
    unsigned long lastSoilTrendSample = 0;
    float soilTrendPerMinute = 0.0f;
    float soilTrendScore = 0.0f;

    bool vibrationDetected = false;
    volatile uint32_t vibrationPulseCounter = 0;
    uint32_t lastHandledVibrationPulse = 0;
    unsigned long lastVibrationTime = 0;
    bool vibrationEverDetected = false;

    // Dữ liệu cảm biến sau lọc EMA.
    float ax = 0, ay = 0, az = 0;
    float gx = 0, gy = 0, gz = 0;
    float filteredAx = 0, filteredAy = 0, filteredAz = 0;
    float filteredGx = 0, filteredGy = 0, filteredGz = 0;
    bool sensorFilterInitialized = false;

    float roll = 0.0f;
    float pitch = 0.0f;
    bool angleInitialized = false;
    unsigned long lastMPUTime = 0;

    // Góc gốc lưu trong NVS của chính ESP32 này.
    bool baselineValid = false;
    float baselineGX = 0.0f, baselineGY = 0.0f, baselineGZ = 1.0f;
    float baselineRoll = 0.0f, baselinePitch = 0.0f;
    float tiltDelta3D = 0.0f;
    float tiltScore = 0.0f;
    bool tiltDeltaInitialized = false;
    bool tiltConfirmed = false;
    unsigned long tiltAboveSince = 0;

    // Hiệu chuẩn không chặn loop: 0=chưa, 1=đang chạy, 2=thành công, 3=thất bại.
    uint8_t calibrationState = 0;
    float calibrationProgress = 0.0f;
    unsigned long calibrationStartMs = 0;
    double calibrationSumX = 0, calibrationSumY = 0, calibrationSumZ = 0;
    double calibrationSumSqX = 0, calibrationSumSqY = 0, calibrationSumSqZ = 0;
    uint32_t calibrationSamples = 0;
    uint32_t calibrationRejectedSamples = 0;
    char calibrationMessage[96] = "Chua hieu chuan";

    // Theo dõi độ ẩm nguy cơ cao và điểm rủi ro tổng hợp.
    unsigned long moistureHighSince = 0;
    bool moistureDanger = false;
    float moistureConfirmProgress = 0.0f;
    float soilScore = 0.0f;
    float vibrationScore = 0.0f;
    float seismicScore = 0.0f; // Giữ tên field để tương thích dashboard cũ.

    SensorNode(const char* id, const char* name, const char* baselineNamespace,
               int soilPin, int vibrationPin, int sdaPin, int sclPin, TwoWire& wire,
               int soilDryRaw, int soilWetRaw)
        : id(id), name(name), baselineNamespace(baselineNamespace),
          soilPin(soilPin), vibrationPin(vibrationPin), sdaPin(sdaPin), sclPin(sclPin),
          wire(wire), soilDryRaw(soilDryRaw), soilWetRaw(soilWetRaw) {}

    void begin();
    void updateVibrationStatus(unsigned long now);
    bool sample(unsigned long now);
    void startCalibration();
    void setCalibrationMessage(const char* message);
    void formatData(char* json, size_t size, const char* ip) const;

private:
    bool wireReady = false;
    uint8_t mpuMisses = 0;
    uint8_t signalMisses = 0;
    uint8_t signalPasses = 0;
    unsigned long lastMpuRetry = 0;

    static void onVibrationPulse(void* context);
    bool probeMpu();
    bool checkSignalWires();
    bool connectMpu();
    void readSensors(unsigned long now);
    void loadTiltBaseline();
    void updateCalibration(unsigned long now, float sampleX, float sampleY, float sampleZ, float gyroMagnitude);
    void updateSoilTrend(unsigned long now);
    void updateMoistureState(unsigned long now);
    void updateTiltScore(unsigned long now);
    void calculateLandslideRisk();
};

// Node 1 tiếp tục đọc mốc góc cũ từ "tiltbase".
// Chỉnh hai mốc ADC khô/ướt riêng cho từng đầu dò khi cần.
SensorNode sensorNodes[] = {
    {"node-1", "Node 1", "tiltbase", 34, 27, 21, 22, Wire,  3000, 1000},
    {"node-2", "Node 2", "tiltbase2", 35, 26, 32, 33, Wire1, 3000, 1000},
};

unsigned long lastSample = 0;

struct RelayPacket {
    unsigned long sequence = 0;
    unsigned long sampledAt = 0;
    int soilRaw = 0;
    float soilPercent = 0;
    float roll = 0;
    float pitch = 0;
    bool vibration = false;
    float riskScore = 0;
};

RelayPacket relayBuffer;
RelayPacket lastRelayPacket;
unsigned long relaySequence = 0;
unsigned long sourceLostAt = 0;
unsigned long relayForwardedAt = 0;
bool sourceWasOnline = false;
bool relayPending = false;

void updateRelayDemo(unsigned long now, bool sourceSampled) {
    const SensorNode& source = sensorNodes[0];
    const bool relayOnline = sensorNodes[1].online();

    if (sourceSampled && relayOnline) {
        relayBuffer.sequence = ++relaySequence;
        relayBuffer.sampledAt = now;
        relayBuffer.soilRaw = source.soilRaw;
        relayBuffer.soilPercent = source.soilPercent;
        relayBuffer.roll = source.roll;
        relayBuffer.pitch = source.pitch;
        relayBuffer.vibration = source.vibrationDetected;
        relayBuffer.riskScore = source.seismicScore;
    }

    if (sourceWasOnline && !source.online()) {
        if (!relayPending) {
            lastRelayPacket = relayBuffer;
            sourceLostAt = now;
            relayForwardedAt = 0;
            relayPending = lastRelayPacket.sequence != 0;
        }
        relayBuffer = {};
    }
    sourceWasOnline = source.online();

    // Giữ gói đủ lâu để dashboard thấy trạng thái chờ sau khi rút dây.
    if (relayPending && relayOnline && now - sourceLostAt >= RELAY_HOLD_MS) {
        relayPending = false;
        relayForwardedAt = now;
    }
}

// Ngắt GPIO bắt cả xung rung ngắn; không đặt delay() trong ISR.
void IRAM_ATTR SensorNode::onVibrationPulse(void* context) {
    static_cast<SensorNode*>(context)->vibrationPulseCounter++;
}

void SensorNode::updateVibrationStatus(unsigned long now) {
    noInterrupts();
    uint32_t currentPulseCount = vibrationPulseCounter;
    interrupts();

    if (currentPulseCount != lastHandledVibrationPulse) {
        lastHandledVibrationPulse = currentPulseCount;
        lastVibrationTime = now;
        vibrationEverDetected = true;
    }

    vibrationDetected = vibrationEverDetected &&
        (now - lastVibrationTime < VIBRATION_HOLD_MS);
}

float clampFloat(float value, float low, float high) {
    if (value < low) return low;
    if (value > high) return high;
    return value;
}

bool normalizeVector(float &x, float &y, float &z) {
    float magnitude = sqrtf(x * x + y * y + z * z);
    if (!std::isfinite(magnitude) || magnitude < 0.001f) return false;
    x /= magnitude;
    y /= magnitude;
    z /= magnitude;
    return true;
}

void SensorNode::setCalibrationMessage(const char* message) {
    strncpy(calibrationMessage, message, sizeof(calibrationMessage) - 1);
    calibrationMessage[sizeof(calibrationMessage) - 1] = '\0';
}

void SensorNode::loadTiltBaseline() {
    TiltBaseline saved{};
    baselineValid = false;
    if (preferences.getBytesLength("baseline") == sizeof(saved)) {
        baselineValid = preferences.getBytes("baseline", &saved, sizeof(saved)) == sizeof(saved);
    } else if (preferences.getBool("valid", false)) {
        saved = {
            preferences.getFloat("gx0", 0.0f), preferences.getFloat("gy0", 0.0f), preferences.getFloat("gz0", 1.0f),
            preferences.getFloat("roll0", 0.0f), preferences.getFloat("pitch0", 0.0f)
        };
        baselineValid = true;
    }

    if (!baselineValid) return;
    if (!normalizeVector(saved.gravityX, saved.gravityY, saved.gravityZ)) {
        baselineValid = false;
        setCalibrationMessage("Moc goc trong bo nho khong hop le; can hieu chuan lai");
        return;
    }

    baselineGX = saved.gravityX;
    baselineGY = saved.gravityY;
    baselineGZ = saved.gravityZ;
    baselineRoll = saved.roll;
    baselinePitch = saved.pitch;
    calibrationState = 2;
    calibrationProgress = 100.0f;
    setCalibrationMessage("Da hieu chuan");
}

void SensorNode::startCalibration() {
    calibrationState = 1;
    calibrationProgress = 0.0f;
    calibrationStartMs = millis();
    calibrationSumX = calibrationSumY = calibrationSumZ = 0.0;
    calibrationSumSqX = calibrationSumSqY = calibrationSumSqZ = 0.0;
    calibrationSamples = 0;
    calibrationRejectedSamples = 0;
    setCalibrationMessage("Dang lay mau goc trong 8 giay");
}

void SensorNode::updateCalibration(unsigned long now, float sampleX, float sampleY, float sampleZ, float gyroMagnitude) {
    if (calibrationState != 1) return;

    float accMagnitude = sqrtf(sampleX * sampleX + sampleY * sampleY + sampleZ * sampleZ);
    bool stableSample = !vibrationDetected &&
                        accMagnitude >= 7.5f && accMagnitude <= 12.0f &&
                        gyroMagnitude <= 8.0f;

    if (stableSample) {
        calibrationSumX += sampleX;
        calibrationSumY += sampleY;
        calibrationSumZ += sampleZ;
        calibrationSumSqX += sampleX * sampleX;
        calibrationSumSqY += sampleY * sampleY;
        calibrationSumSqZ += sampleZ * sampleZ;
        calibrationSamples++;
    } else {
        calibrationRejectedSamples++;
    }

    unsigned long elapsed = now - calibrationStartMs;
    calibrationProgress = clampFloat(100.0f * (float)elapsed / (float)CALIBRATION_DURATION_MS, 0.0f, 100.0f);
    if (elapsed < CALIBRATION_DURATION_MS) return;

    bool accepted = calibrationSamples >= 120; // xấp xỉ >=75% mẫu ở chu kỳ 50ms
    float meanX = 0, meanY = 0, meanZ = 0;
    float stdX = 999, stdY = 999, stdZ = 999;

    if (calibrationSamples > 0) {
        double n = (double)calibrationSamples;
        meanX = (float)(calibrationSumX / n);
        meanY = (float)(calibrationSumY / n);
        meanZ = (float)(calibrationSumZ / n);
        double varX = calibrationSumSqX / n - (double)meanX * meanX;
        double varY = calibrationSumSqY / n - (double)meanY * meanY;
        double varZ = calibrationSumSqZ / n - (double)meanZ * meanZ;
        stdX = sqrtf((float)(varX > 0.0 ? varX : 0.0));
        stdY = sqrtf((float)(varY > 0.0 ? varY : 0.0));
        stdZ = sqrtf((float)(varZ > 0.0 ? varZ : 0.0));
    }

    float meanMagnitude = sqrtf(meanX * meanX + meanY * meanY + meanZ * meanZ);
    if (stdX > 0.65f || stdY > 0.65f || stdZ > 0.65f || meanMagnitude < 8.0f || meanMagnitude > 11.5f) {
        accepted = false;
    }

    if (!accepted) {
        calibrationState = 3;
        calibrationProgress = 100.0f;
        setCalibrationMessage("Hieu chuan that bai: node chua on dinh, hay thu lai");
        return; // Không ghi đè mốc gốc cũ nếu lần hiệu chuẩn mới thất bại.
    }

    TiltBaseline baseline = {
        meanX, meanY, meanZ,
        atan2f(meanY, meanZ) * (180.0f / static_cast<float>(PI)),
        atan2f(-meanX, sqrtf(meanY * meanY + meanZ * meanZ)) * (180.0f / static_cast<float>(PI))
    };
    if (!normalizeVector(baseline.gravityX, baseline.gravityY, baseline.gravityZ)) {
        calibrationState = 3;
        setCalibrationMessage("Hieu chuan that bai: vector gia toc khong hop le");
        return;
    }
    if (preferences.putBytes("baseline", &baseline, sizeof(baseline)) != sizeof(baseline)) {
        calibrationState = 3;
        setCalibrationMessage("Khong luu duoc moc goc hieu chuan");
        return;
    }

    baselineGX = baseline.gravityX;
    baselineGY = baseline.gravityY;
    baselineGZ = baseline.gravityZ;
    baselineRoll = baseline.roll;
    baselinePitch = baseline.pitch;
    baselineValid = true;

    tiltDelta3D = 0.0f;
    tiltScore = 0.0f;
    tiltDeltaInitialized = true;
    tiltConfirmed = false;
    tiltAboveSince = 0;
    calibrationState = 2;
    calibrationProgress = 100.0f;
    setCalibrationMessage("Hieu chuan thanh cong");
}

void SensorNode::updateSoilTrend(unsigned long now) {
    if (lastSoilTrendSample == 0) {
        for (uint8_t i = 0; i < SOIL_TREND_HISTORY_SIZE; i++) {
            soilTrendHistory[i] = soilPercent;
            soilTrendTimes[i] = now;
        }
        soilTrendIndex = 0;
        lastSoilTrendSample = now;
        soilTrendPerMinute = 0.0f;
        soilTrendScore = 0.0f;
        return;
    }

    if (now - lastSoilTrendSample < SOIL_TREND_INTERVAL_MS) return;

    lastSoilTrendSample = now;
    soilTrendIndex = (soilTrendIndex + 1) % SOIL_TREND_HISTORY_SIZE;
    soilTrendHistory[soilTrendIndex] = soilPercent;
    soilTrendTimes[soilTrendIndex] = now;

    uint8_t oldestIndex = (soilTrendIndex + 1) % SOIL_TREND_HISTORY_SIZE;
    unsigned long windowMs = now - soilTrendTimes[oldestIndex];
    if (windowMs >= 60000UL) {
        float increase = soilPercent - soilTrendHistory[oldestIndex];
        soilTrendPerMinute = increase * 60000.0f / (float)windowMs;
        // Tăng <=2 điểm %/phút: không cộng điểm xu hướng; >=10 điểm/phút: tối đa.
        soilTrendScore = clampFloat((soilTrendPerMinute - 2.0f) / 8.0f * 100.0f, 0.0f, 100.0f);
    } else {
        soilTrendPerMinute = 0.0f;
        soilTrendScore = 0.0f;
    }
}

void SensorNode::updateMoistureState(unsigned long now) {
    if (soilPercent >= MOISTURE_HIGH_THRESHOLD) {
        if (moistureHighSince == 0) moistureHighSince = now;
        unsigned long elapsed = now - moistureHighSince;
        moistureConfirmProgress = clampFloat(100.0f * (float)elapsed / (float)MOISTURE_CONFIRM_MS, 0.0f, 100.0f);
        moistureDanger = elapsed >= MOISTURE_CONFIRM_MS;
    } else if (soilPercent < MOISTURE_RESET_THRESHOLD) {
        moistureHighSince = 0;
        moistureConfirmProgress = 0.0f;
        moistureDanger = false;
    }
}

void SensorNode::updateTiltScore(unsigned long now) {
    if (!baselineValid) {
        tiltScore = 0.0f;
        tiltConfirmed = false;
        tiltAboveSince = 0;
        return;
    }

    if (tiltDelta3D > TILT_DEADBAND_DEG) {
        if (tiltAboveSince == 0) tiltAboveSince = now;
        unsigned long requiredMs = (tiltDelta3D >= 10.0f) ? 1000UL :
                                   (tiltDelta3D >= 5.0f) ? 2000UL : 3000UL;
        tiltConfirmed = (now - tiltAboveSince) >= requiredMs;
    } else {
        tiltAboveSince = 0;
        tiltConfirmed = false;
    }

    if (!tiltConfirmed) {
        tiltScore = 0.0f;
        return;
    }

    // Quy đổi theo từng đoạn: 2°=0, 5°=30, 10°=70, >=15°=100.
    if (tiltDelta3D < 5.0f) {
        tiltScore = (tiltDelta3D - 2.0f) * 10.0f;
    } else if (tiltDelta3D < 10.0f) {
        tiltScore = 30.0f + (tiltDelta3D - 5.0f) * 8.0f;
    } else {
        tiltScore = 70.0f + (tiltDelta3D - 10.0f) * 6.0f;
    }
    tiltScore = clampFloat(tiltScore, 0.0f, 100.0f);
}

void SensorNode::calculateLandslideRisk() {
    float moistureLevelScore = clampFloat(soilPercent, 0.0f, 100.0f);
    float moistureTrendScore = clampFloat(soilTrendScore, 0.0f, 100.0f);
    soilScore = 0.80f * moistureLevelScore + 0.20f * moistureTrendScore;
    vibrationScore = vibrationDetected ? 100.0f : 0.0f;

    float risk = MOISTURE_WEIGHT * soilScore +
                 TILT_WEIGHT * tiltScore +
                 VIBRATION_WEIGHT * vibrationScore;

    // Quy tắc độc lập: độ ẩm >=90% liên tục 5 giây không cần có rung.
    if (moistureDanger && risk < 80.0f) risk = 80.0f;

    // Quy tắc độc lập cho độ nghiêng đã xác nhận kéo dài.
    if (tiltConfirmed) {
        if (tiltDelta3D >= 10.0f && risk < 75.0f) risk = 75.0f;
        else if (tiltDelta3D >= 5.0f && risk < 50.0f) risk = 50.0f;
        else if (tiltDelta3D > TILT_DEADBAND_DEG && risk < 25.0f) risk = 25.0f;
    }

    seismicScore = clampFloat(risk, 0.0f, 100.0f);
}

// ==========================================
// 4. HTML DASHBOARD (EXPANDED TOPOLOGY & TELEMETRY INSPECTOR)
// ==========================================

const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hệ Thống Giám Sát & Cảnh Báo Sạt Lở Đất</title>
<style>
:root {
    --bg-dark: #0b1120;
    --card-bg: #1e293b;
    --card-border: #334155;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --primary: #3b82f6;
    --primary-hover: #2563eb;
    --safe: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

body {
    background: var(--bg-dark);
    color: var(--text-main);
    min-height: 100vh;
    padding: 24px;
    padding-bottom: 100px;
}

.container {
    max-width: 1360px;
    margin: 0 auto;
}

/* Header */
header {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    padding: 24px 30px;
    margin-bottom: 24px;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45);
}

header h1 {
    font-size: 26px;
    font-weight: 800;
    color: #60a5fa;
    display: flex;
    align-items: center;
    gap: 12px;
}

header p {
    color: var(--text-muted);
    font-size: 14px;
    margin-top: 4px;
}

.header-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.badge {
    padding: 8px 16px;
    border-radius: 30px;
    font-size: 13px;
    font-weight: 600;
    background: #1e293b;
    border: 1px solid var(--card-border);
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.badge.online {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border-color: rgba(16, 185, 129, 0.3);
}

.dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: currentColor;
    display: inline-block;
}

/* Tabs Navigation */
.tabs-nav {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--card-border);
    padding-bottom: 14px;
}

.tab-btn {
    background: transparent;
    border: none;
    outline: none;
    color: var(--text-muted);
    font-size: 16px;
    font-weight: 600;
    padding: 12px 24px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 10px;
}

.tab-btn:hover {
    color: var(--text-main);
    background: rgba(255, 255, 255, 0.05);
}

.tab-btn.active {
    color: #fff;
    background: var(--primary);
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

/* Tab Content */
.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ==========================================
   TAB 1: EXPANDED TOPOLOGY
   ========================================== */
.topo-wrapper {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 32px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    position: relative;
}

.topo-instructions {
    margin-bottom: 28px;
    padding: 16px 20px;
    background: rgba(59, 130, 246, 0.12);
    border-left: 5px solid var(--primary);
    border-radius: 10px;
    font-size: 14px;
    color: #93c5fd;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
}

.demo-controls {
    display: flex;
    gap: 10px;
}

.demo-btn {
    background: #334155;
    border: 1px solid #475569;
    color: #f1f5f9;
    font-size: 13px;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.demo-btn:hover {
    background: #475569;
}

.demo-btn.active-quake {
    background: #dc2626;
    border-color: #ef4444;
    color: white;
    animation: pulseRed 0.8s infinite alternate;
}

/* Network Chain Graph */
.topology-chain {
    display: flex;
    align-items: flex-start;
    justify-content: space-around;
    padding: 30px 10px 45px;
    width: 100%;
    gap: 12px;
    position: relative;
    overflow-x: auto;
}

.node-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    user-select: none;
    z-index: 2;
    transition: transform 0.25s ease;
    min-width: 200px;
    max-width: 250px;
    margin-bottom: 10px;
}

.node-item:hover, .node-item.selected-node {
    transform: translateY(-8px);
}

.node-circle-wrap {
    position: relative;
    margin-bottom: 16px;
}

.node-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: #0f172a;
    border: 5px solid var(--safe);
    box-shadow: 0 0 25px rgba(16, 185, 129, 0.35);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}

.node-item.selected-node .node-circle {
    outline: 3px dashed #60a5fa;
    outline-offset: 6px;
}

.node-icon {
    font-size: 38px;
}

.node-pct {
    font-size: 14px;
    font-weight: 800;
    margin-top: 4px;
}

/* Quick stats card directly below each node */
.node-quick-card {
    background: #0f172a;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 12px 14px;
    width: 100%;
    text-align: center;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
    transition: all 0.2s;
}

.node-item:hover .node-quick-card, .node-item.selected-node .node-quick-card {
    border-color: #60a5fa;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.25);
}

.node-quick-name {
    font-size: 15px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 4px;
}

.node-quick-ip {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 10px;
    font-family: monospace;
}

.node-quick-metrics {
    display: flex;
    flex-direction: column;
    gap: 6px;
    text-align: left;
    font-size: 12px;
}

.metric-pill {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 8px;
    background: #1e293b;
    border-radius: 6px;
}

.metric-pill span {
    color: var(--text-muted);
}

/* Demo chuyển tiếp trên một ESP32 */
.relay-demo {
    margin: 0 0 16px;
    padding: 14px 16px;
    background: #0f172a;
    border: 1px solid var(--card-border);
    border-radius: 10px;
    line-height: 1.5;
}
.relay-demo p { margin-top: 5px; }
#relayPacketView { color: #cbd5e1; overflow-wrap: anywhere; }

/* Connecting link */
.node-link {
    flex-grow: 1;
    min-width: 28px;
    max-width: 120px;
    height: 6px;
    background: linear-gradient(90deg, #334155 0%, #64748b 50%, #334155 100%);
    position: relative;
    margin-top: 57px;
    z-index: 1;
    border-radius: 3px;
}

.node-link::after {
    content: "";
    position: absolute;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #60a5fa;
    top: -5px;
    left: 0;
    animation: flowData 2s infinite linear;
    box-shadow: 0 0 12px #60a5fa;
}

@keyframes flowData {
    0% { left: 5%; opacity: 0; }
    20% { opacity: 1; }
    80% { opacity: 1; }
    100% { left: 95%; opacity: 0; }
}

@keyframes pulseRed {
    0% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.5); }
    100% { box-shadow: 0 0 45px rgba(239, 68, 68, 1); }
}

/* ==========================================
   LIVE TELEMETRY INSPECTOR PANEL (TAB 1)
   ========================================== */
.inspector-panel {
    margin-top: 35px;
    background: #0f172a;
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
}

.inspector-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    border-bottom: 1px solid var(--card-border);
    padding-bottom: 16px;
    margin-bottom: 20px;
}

.inspector-title {
    display: flex;
    align-items: center;
    gap: 10px;
}

.inspector-title h3 {
    font-size: 18px;
    color: #60a5fa;
    font-weight: 700;
}

.inspector-title span {
    font-size: 13px;
    color: var(--text-muted);
}

.inspector-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 18px;
}

.telemetry-card {
    background: #1e293b;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 18px;
    transition: transform 0.2s;
}

.telemetry-card h4 {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: flex;
    align-items: center;
    gap: 6px;
}

.telemetry-val {
    font-size: 28px;
    font-weight: 800;
    color: #38bdf8;
    margin-bottom: 8px;
}

.telemetry-val .unit {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-muted);
}

.telemetry-sub {
    font-size: 12px;
    color: #cbd5e1;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.telemetry-sub-row {
    display: flex;
    justify-content: space-between;
}

.risk-bar-container {
    width: 100%;
    height: 10px;
    background: #334155;
    border-radius: 5px;
    overflow: hidden;
    margin-top: 10px;
}

.risk-bar-fill {
    height: 100%;
    width: 0%;
    transition: width 0.3s ease, background-color 0.3s ease;
}

/* ==========================================
   TAB 2: NODE LIST TABLE
   ========================================== */
.table-container {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    overflow-x: auto;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}

table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    min-width: 1280px;
}

th, td {
    padding: 18px 22px;
    border-bottom: 1px solid var(--card-border);
}

th {
    background: #172554;
    color: #93c5fd;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

tr:last-child td {
    border-bottom: none;
}

tr:hover td {
    background: rgba(255, 255, 255, 0.03);
}

.node-name-cell {
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 600;
}

.node-tag {
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 600;
}

.tag-master {
    background: #1e3a8a;
    color: #93c5fd;
}

.tag-child {
    background: #334155;
    color: #cbd5e1;
}

.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
}

.btn-action {
    background: transparent;
    border: 1px solid var(--card-border);
    color: #ef4444;
    padding: 6px 14px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s;
}

.btn-action:hover {
    background: rgba(239, 68, 68, 0.2);
}

.calibration-cell { min-width: 230px; }
.calibration-status { font-size: 12px; line-height: 1.5; margin-bottom: 8px; color: #cbd5e1; }
.btn-calibrate {
    background: #1d4ed8; border: 1px solid #3b82f6; color: #fff;
    padding: 7px 10px; border-radius: 8px; cursor: pointer;
    font-size: 12px; font-weight: 600; white-space: nowrap;
}
.btn-calibrate:hover { background: #2563eb; }
.btn-calibrate:disabled { opacity: .45; cursor: not-allowed; }

/* Floating Action Button (+) */
.fab-btn {
    position: fixed;
    bottom: 28px;
    left: 28px;
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    border: none;
    outline: none;
    font-size: 34px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    box-shadow: 0 6px 25px rgba(37, 99, 235, 0.55);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 999;
}

.fab-btn:hover {
    transform: scale(1.1) rotate(90deg);
    box-shadow: 0 8px 30px rgba(37, 99, 235, 0.75);
}

/* Modal Add Node */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.75);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    opacity: 0;
    visibility: hidden;
    transition: all 0.25s ease;
    backdrop-filter: blur(5px);
}

.modal-overlay.active {
    opacity: 1;
    visibility: visible;
}

.modal-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    width: 90%;
    max-width: 500px;
    padding: 28px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
    transform: scale(0.95);
    transition: transform 0.25s ease;
}

.modal-overlay.active .modal-card {
    transform: scale(1);
}

.modal-card h3 {
    font-size: 20px;
    margin-bottom: 8px;
    color: #60a5fa;
    display: flex;
    align-items: center;
    gap: 10px;
}

.modal-card p {
    color: var(--text-muted);
    font-size: 14px;
    margin-bottom: 22px;
}

.form-group {
    margin-bottom: 18px;
}

.form-group label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #cbd5e1;
}

.form-group input {
    width: 100%;
    padding: 12px 16px;
    border-radius: 10px;
    background: #0f172a;
    border: 1px solid var(--card-border);
    color: #fff;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
}

.form-group input:focus {
    border-color: var(--primary);
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 26px;
}

.btn-secondary {
    background: #334155;
    border: none;
    color: #cbd5e1;
    padding: 11px 20px;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
}

.btn-primary {
    background: var(--primary);
    border: none;
    color: #fff;
    padding: 11px 22px;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    transition: background-color 0.2s;
}

.btn-primary:hover {
    background: var(--primary-hover);
}

@media (max-width: 1080px) {
    .topology-chain { flex-direction: column; align-items: center; }
    .node-link {
        flex: none;
        width: 6px;
        min-width: 0;
        height: 24px;
        margin-top: 0;
        background: #64748b;
    }
    .node-link::after { display: none; }
}
</style>
</head>
<body>

<div class="container">

    <!-- Header -->
    <header>
        <div>
            <h1>📡 MẠNG NODE GIÁM SÁT SẠT LỞ ĐẤT</h1>
            <p>Hệ thống giám sát đa cảm biến & cảnh báo sớm nguy cơ sạt lở đất</p>
        </div>
        <div class="header-badges">
            <div class="badge online">
                <span class="dot"></span>
                <span id="headerStatus">ESP32 Đang Hoạt Động</span>
            </div>
            <div class="badge">
                <span>WiFi:</span>
                <strong id="headerSSID">--</strong>
            </div>
            <div class="badge">
                <span>IP:</span>
                <strong id="headerIP">--</strong>
            </div>
        </div>
    </header>

    <!-- Navigation Tabs -->
    <div class="tabs-nav">
        <button class="tab-btn active" onclick="switchTab('tab-topology')">
            🕸️ Tab 1: Sơ đồ mạng Topology
        </button>
        <button class="tab-btn" onclick="switchTab('tab-nodes')">
            📋 Tab 2: Danh sách & Hiệu chuẩn Node
        </button>
    </div>

    <!-- TAB 1: TOPOLOGY -->
    <div id="tab-topology" class="tab-content active">
        <div class="topo-wrapper">
            <div class="topo-instructions">
                <div>
                    💡 <strong>Hướng dẫn:</strong> Rê chuột hoặc bấm vào từng Node để xem đầy đủ thông số tức thời ở bảng bên dưới. Màu sắc thể hiện <strong>điểm nguy cơ sạt lở tổng hợp</strong> từ độ ẩm, độ nghiêng và rung động.
                    Node 1 và 2 lấy số đo qua cùng ESP32. Các đường nối minh họa sơ đồ mạng.
                </div>
                <div class="demo-controls">
                    <button class="demo-btn" id="btnSim3" onclick="toggleDemoQuake(2)">Thử rung Node 3</button>
                    <button class="demo-btn" id="btnSim4" onclick="toggleDemoQuake(3)">Thử rung Node 4</button>
                </div>
            </div>

            <section class="relay-demo" aria-label="Demo chuyển tiếp khi Node 1 mất kết nối">
                <h3>Node 1 → Node 2 → Gateway (trình duyệt)</h3>
                <p>Khi Node 2 đã giữ mẫu, rút dây tín hiệu AO (GPIO34), DO (GPIO27) hoặc SDA (GPIO21) của Node 1. Giữ hai điện trở kiểm tra ở phía ESP32. Cắm lại để tiếp tục đo.</p>
                <p id="relayBufferView">Đang chờ mẫu đầu tiên từ Node 1…</p>
                <p id="relayStateView" role="status">Chưa có sự kiện mất kết nối.</p>
                <p id="relayPacketView" hidden></p>
            </section>

            <!-- Dynamic Node Chain -->
            <div class="topology-chain" id="topologyContainer">
                <!-- Javascript will render nodes and links here -->
            </div>

            <!-- Prominent Live Telemetry Panel for the selected / hovered node -->
            <div class="inspector-panel" id="inspectorPanel">
                <div class="inspector-header">
                    <div class="inspector-title">
                        <h3>📊 BẢNG THEO DÕI THÔNG SỐ TỨC THỜI</h3>
                        <span id="inspNodeLabel">Node 1 (ESP32 Thật)</span>
                    </div>
                    <div class="badge" id="inspStatusBadge" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border-color: rgba(16, 185, 129, 0.3);">
                        <span class="dot"></span>
                        <span id="inspStatusText">Bình thường</span>
                    </div>
                </div>

                <div class="inspector-grid">
                    <!-- Độ ẩm đất -->
                    <div class="telemetry-card">
                        <h4>🌱 Độ ẩm đất</h4>
                        <div class="telemetry-val">
                            <span id="inspSoilPct">--</span>
                            <span class="unit">%</span>
                        </div>
                        <div class="telemetry-sub">
                            <div class="telemetry-sub-row">
                                <span>Giá trị ADC:</span>
                                <strong id="inspSoilRaw">--</strong>
                            </div>
                            <div class="telemetry-sub-row">
                                <span>Đánh giá:</span>
                                <strong id="inspSoilStatus">--</strong>
                            </div>
                            <div class="telemetry-sub-row">
                                <span>Xu hướng (điểm %/phút):</span>
                                <strong id="inspSoilTrend">--</strong>
                            </div>
                        </div>
                    </div>

                    <!-- Cảm biến rung SW-420 -->
                    <div class="telemetry-card">
                        <h4>📳 Rung SW-420</h4>
                        <div class="telemetry-val" id="inspVibVal" style="font-size:22px; color:#34d399;">
                            ỔN ĐỊNH
                        </div>
                        <div class="telemetry-sub">
                            <div class="telemetry-sub-row">
                                <span>Xung rung:</span>
                                <strong id="inspVibStatus">Không phát hiện</strong>
                            </div>
                            <div class="telemetry-sub-row">
                                <span>Giữ cảnh báo:</span>
                                <strong>3 giây sau xung cuối</strong>
                            </div>
                        </div>
                    </div>

                    <!-- MPU-6050 Gia tốc -->
                    <div class="telemetry-card">
                        <h4>📐 Gia tốc MPU-6050</h4>
                        <div class="telemetry-val" id="inspAccMagnitude" style="font-size:24px;">
                            9.8 <span class="unit">m/s²</span>
                        </div>
                        <div class="telemetry-sub">
                            <div class="telemetry-sub-row">
                                <span>Trục X:</span>
                                <strong id="inspAx">0.00</strong>
                            </div>
                            <div class="telemetry-sub-row">
                                <span>Trục Y:</span>
                                <strong id="inspAy">0.00</strong>
                            </div>
                            <div class="telemetry-sub-row">
                                <span>Trục Z:</span>
                                <strong id="inspAz">9.80</strong>
                            </div>
                        </div>
                    </div>

                    <!-- MPU-6050 Góc & Con quay -->
                    <div class="telemetry-card">
                        <h4>🔄 Góc nghiêng & Vận tốc góc</h4>
                        <div class="telemetry-val" style="font-size:20px;">
                            <span id="inspRoll">0.0</span>° / <span id="inspPitch">0.0</span>°
                        </div>
                        <div class="telemetry-sub">
                            <div class="telemetry-sub-row">
                                <span>Roll (Xoay X):</span>
                                <strong id="inspRollSub">0.0°</strong>
                            </div>
                            <div class="telemetry-sub-row">
                                <span>Pitch (Nghiêng Y):</span>
                                <strong id="inspPitchSub">0.0°</strong>
                            </div>
                            <div class="telemetry-sub-row">
                                <span>Con quay (gx, gy, gz):</span>
                                <strong id="inspGyro">0, 0, 0</strong>
                            </div>
                        </div>
                    </div>

                    <!-- Mức độ nguy cơ sạt lở đất -->
                    <div class="telemetry-card">
                        <h4>🚨 Nguy cơ sạt lở đất</h4>
                        <div class="telemetry-val" id="inspSeismicPct" style="color: #10b981;">
                            0 <span class="unit">%</span>
                        </div>
                        <div class="telemetry-sub">
                            <div class="telemetry-sub-row">
                                <span>Trạng thái:</span>
                                <strong id="inspSeismicText" style="color: #10b981;">Bình thường</strong>
                            </div>
                            <div class="telemetry-sub-row">
                                <span>Độ lệch so với góc gốc:</span>
                                <strong id="inspTiltDelta">Chưa hiệu chuẩn</strong>
                            </div>
                            <div class="telemetry-sub-row">
                                <span>Độ ẩm nguy cơ cao:</span>
                                <strong id="inspMoistureDanger">Chưa kích hoạt</strong>
                            </div>
                            <div class="risk-bar-container">
                                <div class="risk-bar-fill" id="inspSeismicBar" style="width: 0%; background-color: #10b981;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <!-- TAB 2: NODE LIST -->
    <div id="tab-nodes" class="tab-content">
        <div class="topo-instructions" style="margin-bottom:16px;">
            <strong>Quy trình góc gốc:</strong> Nạp firmware này cho từng ESP32, kết nối tất cả vào cùng Wi-Fi, thêm IP Node tại nút +. Sau khi cắm và cố định Node vào đất, để cảm biến đứng yên rồi nhấn <strong>Chốt góc gốc (8 giây)</strong>. Không di chuyển Node trong lúc lấy mẫu.
        </div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Node</th>
                        <th>IP / Endpoint</th>
                        <th>WiFi SSID</th>
                        <th>Độ ẩm đất</th>
                        <th>Rung (SW-420)</th>
                        <th>Gia tốc / Góc</th>
                        <th>Hiệu chuẩn góc gốc</th>
                        <th>Nguy cơ sạt lở</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody id="nodeTableBody">
                    <!-- Javascript will render rows here -->
                </tbody>
            </table>
        </div>
    </div>

</div>

<!-- Floating Action Button (+) bottom left -->
<button class="fab-btn" onclick="openAddNodeModal()" title="Thêm Node Mới">+</button>

<!-- Modal Add Node -->
<div class="modal-overlay" id="addNodeModal">
    <div class="modal-card">
        <h3>➕ Thêm Node Mới</h3>
        <p>Nhập IP của ESP32 phụ đã nạp cùng firmware và kết nối vào cùng mạng Wi-Fi. Sau khi cố định node xuống đất, bạn sẽ chốt góc gốc trong bảng Tab 2.</p>

        <form id="addNodeForm" onsubmit="saveNewNode(event)">
            <div class="form-group">
                <label>Tên / Mã Node (*)</label>
                <input type="text" id="newNodeName" placeholder="Ví dụ: Node 4 - Cảm biến khu vực D" required>
            </div>
            <div class="form-group">
                <label>Địa chỉ IP hoặc Hostname (*)</label>
                <input type="text" id="newNodeIP" placeholder="Ví dụ: 192.168.1.104" required>
            </div>
            <div class="form-group">
                <label>SSID (tham chiếu, không cấu hình Wi-Fi từ trình duyệt)</label>
                <input type="text" id="newNodeSSID" value="" placeholder="Ví dụ: iPhone hoặc Wi-Fi hiện tại">
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" onclick="closeAddNodeModal()">Hủy</button>
                <button type="submit" class="btn-primary">Thêm Node & Kết nối</button>
            </div>
        </form>
    </div>
</div>

<script>
// ==========================================
// CLIENT STATE & NODE MANAGEMENT
// ==========================================

const EMPTY_NODE_DATA = {
    soilPercent: 0, soilRaw: 0, soilTrendPerMinute: 0, soilTrendScore: 0, vibration: false, mpuOK: false,
    ax: 0, ay: 0, az: 9.8, gx: 0, gy: 0, gz: 0,
    roll: 0, pitch: 0, tiltDelta: 0, tiltScore: 0,
    calibrated: false, calibrationState: 0, calibrationProgress: 0,
    baselineRoll: 0, baselinePitch: 0, moistureDanger: false,
    moistureConfirmProgress: 0, seismicScore: 0
};

const DEFAULT_NODES = [
    {
        id: "node-1", name: "Node 1 (Miếng A)", isLocal: true,
        isSimulated: false, isOnline: false,
        ip: window.location.hostname, ssid: "", data: { ...EMPTY_NODE_DATA }
    },
    {
        id: "node-2", name: "Node 2 (Miếng B)", isLocal: true,
        isSimulated: false, isOnline: false,
        ip: window.location.hostname, ssid: "", data: { ...EMPTY_NODE_DATA }
    },
    {
        id: "node-3", name: "Node 3",
        isSimulated: true, isOnline: true, ip: "", ssid: "",
        demoQuake: false,
        data: {
            soilPercent: 42.5, soilRaw: 2150, soilTrendPerMinute: 0, soilTrendScore: 0, vibration: false, mpuOK: true,
            ax: 0.05, ay: 0.12, az: 9.81, gx: 0.1, gy: -0.2, gz: 0,
            roll: 0.7, pitch: -0.3, tiltDelta: 0, tiltScore: 0,
            calibrated: false, calibrationState: 0, calibrationProgress: 0,
            baselineRoll: 0, baselinePitch: 0, moistureDanger: false,
            moistureConfirmProgress: 0, seismicScore: 26
        }
    },
    {
        id: "node-4", name: "Node 4",
        isSimulated: true, isOnline: true, ip: "", ssid: "",
        demoQuake: false,
        data: {
            soilPercent: 68, soilRaw: 1640, soilTrendPerMinute: 0, soilTrendScore: 0, vibration: false, mpuOK: true,
            ax: -0.08, ay: 0.02, az: 9.79, gx: 0, gy: 0.1, gz: -0.1,
            roll: -0.5, pitch: 0.4, tiltDelta: 0, tiltScore: 0,
            calibrated: false, calibrationState: 0, calibrationProgress: 0,
            baselineRoll: 0, baselinePitch: 0, moistureDanger: false,
            moistureConfirmProgress: 0, seismicScore: 41
        }
    }
];

const EXTRA_NODES_STORAGE_KEY = 'esp32_iot_extra_nodes_v2';

let nodesList = [];
let activeNodeIndex = 0;
let nodePollBusy = false;

function loadNodes() {
    nodesList = JSON.parse(JSON.stringify(DEFAULT_NODES));
    try {
        const saved = JSON.parse(localStorage.getItem(EXTRA_NODES_STORAGE_KEY));
        if (Array.isArray(saved)) {
            for (const { id, name, ip, ssid } of saved) {
                nodesList.push({
                    id, name, ip, ssid, isLocal: false, isSimulated: false,
                    isOnline: false, data: { ...EMPTY_NODE_DATA }
                });
            }
        }
    } catch (err) {
        console.warn('Không đọc được danh sách node bổ sung:', err);
    }
}

function persistNodes() {
    const extraNodes = nodesList.slice(DEFAULT_NODES.length);
    localStorage.setItem(EXTRA_NODES_STORAGE_KEY, JSON.stringify(
        extraNodes.map(({ id, name, ip, ssid }) => ({ id, name, ip, ssid }))
    ));
}

function nodeSourceLabel(node) {
    if (node.isSimulated) return 'Mô phỏng';
    return node.isLocal ? 'Cảm biến thật' : 'Node phụ';
}

function getRiskColor(score) {
    if (score < 25) return "#10b981";
    if (score < 50) return "#eab308";
    if (score < 75) return "#f97316";
    return "#ef4444";
}

function getRiskStatusText(score) {
    if (score < 25) return "Bình thường";
    if (score < 50) return "Theo dõi";
    if (score < 75) return "Cảnh báo";
    return "NGUY CƠ CAO";
}

function nodeBaseUrl(node) {
    if (node.isLocal) return '';
    let host = (node.ip || '').trim();
    if (!/^https?:\/\//i.test(host)) host = 'http://' + host;
    return host.replace(/\/$/, '');
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn')[tabId === 'tab-topology' ? 0 : 1].classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

function selectNode(index) {
    activeNodeIndex = index;
    document.querySelectorAll('.node-item').forEach((el, idx) => {
        el.classList.toggle('selected-node', idx === index);
    });
    renderInspector();
}

function renderTopology() {
    const container = document.getElementById('topologyContainer');
    container.innerHTML = '';

    nodesList.forEach((node, index) => {
        const score = Number(node.data.seismicScore || 0);
        const color = node.isOnline ? getRiskColor(score) : '#64748b';
        const isAlert = node.isOnline && score >= 75;
        const isSelected = index === activeNodeIndex;
        const nodeItem = document.createElement('div');
        nodeItem.className = 'node-item' + (isSelected ? ' selected-node' : '');
        nodeItem.onmouseenter = () => selectNode(index);
        nodeItem.onclick = () => selectNode(index);
        nodeItem.innerHTML = `
            <div class="node-circle-wrap">
                <div class="node-circle" style="border-color:${color};box-shadow:0 0 ${isAlert ? '35px' : '20px'} ${color};${isAlert ? 'animation:pulseRed 0.8s infinite alternate;' : ''}">
                    <div class="node-icon">${isAlert ? '🚨' : '📡'}</div>
                    <div class="node-pct" style="color:${color};">${node.isOnline ? score.toFixed(0) + '%' : 'OFFLINE'}</div>
                </div>
            </div>
            <div class="node-quick-card">
                <div class="node-quick-name">${node.name}</div>
                <div class="node-quick-ip">${nodeSourceLabel(node)}${node.isOnline ? '' : ' · Mất kết nối'}</div>
                <div class="node-quick-metrics">
                    <div class="metric-pill"><span>Độ ẩm đất:</span><strong>${Number(node.data.soilPercent).toFixed(1)}%</strong></div>
                    <div class="metric-pill"><span>Rung SW-420:</span><strong style="color:${node.data.vibration ? '#ef4444' : '#34d399'};">${node.data.vibration ? 'CÓ RUNG' : 'ỔN ĐỊNH'}</strong></div>
                    <div class="metric-pill"><span>Nguy cơ sạt lở:</span><strong style="color:${color};font-weight:700;">${score.toFixed(0)}%</strong></div>
                    <div class="metric-pill"><span>Kết nối:</span><strong style="color:${node.isOnline ? '#34d399' : '#ef4444'};">${node.isOnline ? 'ONLINE' : 'OFFLINE'}</strong></div>
                </div>
            </div>`;
        container.appendChild(nodeItem);

        if (index < nodesList.length - 1) {
            const link = document.createElement('div');
            link.className = 'node-link';
            container.appendChild(link);
        }
    });
    renderInspector();
}

function renderInspector() {
    if (!nodesList[activeNodeIndex]) activeNodeIndex = 0;
    const node = nodesList[activeNodeIndex];
    if (!node) return;
    const d = node.data;
    const score = Number(d.seismicScore || 0);
    const color = getRiskColor(score);
    const statusText = getRiskStatusText(score);

    document.getElementById('inspNodeLabel').textContent = `${node.name} · ${nodeSourceLabel(node)}`;
    const badge = document.getElementById('inspStatusBadge');
    badge.style.background = `rgba(${score >= 75 ? '239,68,68' : score >= 50 ? '249,115,22' : score >= 25 ? '234,179,8' : '16,185,129'},0.2)`;
    badge.style.color = color;
    badge.style.borderColor = color;
    document.getElementById('inspStatusText').textContent = node.isOnline ? statusText : 'Mất kết nối · số đo chưa cập nhật';

    document.getElementById('inspSoilPct').textContent = Number(d.soilPercent).toFixed(1);
    document.getElementById('inspSoilRaw').textContent = d.soilRaw;
    document.getElementById('inspSoilStatus').textContent = d.moistureDanger ? 'Nguy cơ cao – ≥90% trong 5 giây' : (d.soilPercent >= 60 ? 'Đất ẩm' : (d.soilPercent >= 30 ? 'Trung bình' : 'Đất khô'));
    document.getElementById('inspSoilTrend').textContent = `${Number(d.soilTrendPerMinute || 0).toFixed(2)} điểm %/phút`;

    const vibVal = document.getElementById('inspVibVal');
    if (d.vibration) {
        vibVal.textContent = 'PHÁT HIỆN RUNG!';
        vibVal.style.color = '#ef4444';
        document.getElementById('inspVibStatus').textContent = 'Có xung trong 3 giây gần nhất';
    } else {
        vibVal.textContent = 'ỔN ĐỊNH';
        vibVal.style.color = '#34d399';
        document.getElementById('inspVibStatus').textContent = 'Không phát hiện';
    }

    const accMag = Math.sqrt(d.ax * d.ax + d.ay * d.ay + d.az * d.az);
    document.getElementById('inspAccMagnitude').innerHTML = `${accMag.toFixed(2)} <span class="unit">m/s²</span>`;
    document.getElementById('inspAx').textContent = Number(d.ax).toFixed(2);
    document.getElementById('inspAy').textContent = Number(d.ay).toFixed(2);
    document.getElementById('inspAz').textContent = Number(d.az).toFixed(2);
    document.getElementById('inspRoll').textContent = Number(d.roll).toFixed(1);
    document.getElementById('inspPitch').textContent = Number(d.pitch).toFixed(1);
    document.getElementById('inspRollSub').textContent = Number(d.roll).toFixed(1) + '°';
    document.getElementById('inspPitchSub').textContent = Number(d.pitch).toFixed(1) + '°';
    document.getElementById('inspGyro').textContent = `${Number(d.gx).toFixed(1)}, ${Number(d.gy).toFixed(1)}, ${Number(d.gz).toFixed(1)}`;

    document.getElementById('inspTiltDelta').textContent = d.calibrated ? `${Number(d.tiltDelta).toFixed(2)}° (gốc ${Number(d.baselineRoll).toFixed(1)}° / ${Number(d.baselinePitch).toFixed(1)}°)` : 'Chưa hiệu chuẩn';
    document.getElementById('inspMoistureDanger').textContent = d.moistureDanger ? 'ĐÃ KÍCH HOẠT' : `${Number(d.moistureConfirmProgress || 0).toFixed(0)}% thời gian xác nhận`;

    const sPct = document.getElementById('inspSeismicPct');
    sPct.innerHTML = `${score.toFixed(0)} <span class="unit">%</span>`;
    sPct.style.color = color;
    document.getElementById('inspSeismicText').textContent = statusText;
    document.getElementById('inspSeismicText').style.color = color;
    const sBar = document.getElementById('inspSeismicBar');
    sBar.style.width = `${Math.min(100, Math.max(2, score))}%`;
    sBar.style.backgroundColor = color;
}

function calibrationCell(node, index) {
    if (node.isSimulated) return '<span style="color:#94a3b8;">Node mô phỏng</span>';
    const d = node.data;
    let status = 'Chưa hiệu chuẩn';
    if (!node.isOnline) status = 'Node offline';
    else if (!d.mpuOK) status = 'Không nhận MPU-6050';
    else if (Number(d.calibrationState) === 1) status = `Đang hiệu chuẩn: ${Number(d.calibrationProgress || 0).toFixed(0)}%`;
    else if (Number(d.calibrationState) === 3 && d.calibrated) status = `Lần mới thất bại – giữ mốc cũ (${Number(d.baselineRoll).toFixed(1)}° / ${Number(d.baselinePitch).toFixed(1)}°)`;
    else if (d.calibrated) status = `Đã chốt: Roll₀ ${Number(d.baselineRoll).toFixed(1)}° · Pitch₀ ${Number(d.baselinePitch).toFixed(1)}°<br>Độ lệch hiện tại: ${Number(d.tiltDelta).toFixed(2)}°`;
    else if (Number(d.calibrationState) === 3) status = d.calibrationMessage || 'Hiệu chuẩn thất bại – thử lại';

    const disabled = !node.isOnline || !d.mpuOK || Number(d.calibrationState) === 1;
    const buttonLabel = Number(d.calibrationState) === 1 ? 'Đang lấy mẫu 8 giây…' : (d.calibrated ? 'Hiệu chuẩn lại' : 'Chốt góc gốc (8 giây)');
    return `<div class="calibration-cell"><div class="calibration-status">${status}</div><button class="btn-calibrate" onclick="calibrateNode(${index})" ${disabled ? 'disabled' : ''}>${buttonLabel}</button></div>`;
}

function renderNodeTable() {
    const tbody = document.getElementById('nodeTableBody');
    tbody.innerHTML = '';
    nodesList.forEach((node, index) => {
        const d = node.data;
        const score = Number(d.seismicScore || 0);
        const color = getRiskColor(score);
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><div class="node-name-cell"><span>📡</span><div><div>${node.name}</div><span class="node-tag ${node.isLocal ? 'tag-master' : 'tag-child'}">${nodeSourceLabel(node)}</span></div></div></td>
            <td><code>${node.ip || '—'}</code><br><small style="color:${node.isOnline ? '#34d399' : '#ef4444'}">${node.isOnline ? 'ONLINE' : 'OFFLINE'}</small></td>
            <td>${node.ssid || '—'}</td>
            <td><strong>${Number(d.soilPercent).toFixed(1)}%</strong><br><small>Xu hướng: ${Number(d.soilTrendPerMinute || 0).toFixed(1)} điểm %/phút</small>${d.moistureDanger ? '<br><small style="color:#ef4444">Nguy cơ cao</small>' : ''}</td>
            <td><span class="status-indicator" style="color:${d.vibration ? '#ef4444' : '#10b981'};font-weight:600;"><span class="dot" style="background:currentColor;"></span>${d.vibration ? 'PHÁT HIỆN RUNG' : 'Ổn định'}</span></td>
            <td><small>a: [${Number(d.ax).toFixed(2)}, ${Number(d.ay).toFixed(2)}, ${Number(d.az).toFixed(2)}]</small><br><small>Roll/Pitch: ${Number(d.roll).toFixed(1)}° / ${Number(d.pitch).toFixed(1)}°</small><br><small>Δθ: ${d.calibrated ? Number(d.tiltDelta).toFixed(2) + '°' : '—'}</small></td>
            <td>${calibrationCell(node, index)}</td>
            <td><div style="font-weight:700;color:${color};">${score.toFixed(0)}%</div><small style="color:${color};">${getRiskStatusText(score)}</small></td>
            <td>${index < DEFAULT_NODES.length ? '—' : `<button class="btn-action" onclick="deleteNode(${index})">Xóa</button>`}</td>`;
        tbody.appendChild(tr);
    });
}

function openAddNodeModal() { document.getElementById('addNodeModal').classList.add('active'); }
function closeAddNodeModal() { document.getElementById('addNodeModal').classList.remove('active'); }

function saveNewNode(e) {
    e.preventDefault();
    const name = document.getElementById('newNodeName').value.trim();
    const ip = document.getElementById('newNodeIP').value.trim();
    const ssid = document.getElementById('newNodeSSID').value.trim();
    if (!name || !ip) return;

    const duplicate = nodesList.some(n => !n.isSimulated && String(n.ip).toLowerCase() === ip.toLowerCase());
    if (duplicate) { alert('IP/hostname này đã có trong danh sách Node.'); return; }

    const newNode = {
        id: 'node-' + Date.now(), name, isLocal: false, isSimulated: false,
        isOnline: false, ip, ssid: ssid || '', data: { ...EMPTY_NODE_DATA }
    };
    nodesList.push(newNode);
    persistNodes();
    activeNodeIndex = nodesList.length - 1;
    renderTopology();
    renderNodeTable();
    closeAddNodeModal();
    document.getElementById('addNodeForm').reset();
    document.getElementById('newNodeSSID').value = '';
    fetchNodeData(newNode).then(() => { renderTopology(); renderNodeTable(); });
}

function deleteNode(index) {
    if (!nodesList[index] || index < DEFAULT_NODES.length) return;
    if (confirm(`Bạn có chắc muốn xóa "${nodesList[index].name}" khỏi danh sách theo dõi?`)) {
        nodesList.splice(index, 1);
        if (activeNodeIndex >= nodesList.length) activeNodeIndex = 0;
        persistNodes(); renderTopology(); renderNodeTable();
    }
}

async function calibrateNode(index) {
    const node = nodesList[index];
    if (!node || node.isSimulated || !node.isOnline || !node.data.mpuOK) return;
    try {
        const target = node.isLocal ? '?node=' + encodeURIComponent(node.id) : '';
        const response = await fetch(nodeBaseUrl(node) + '/calibrate' + target, {
            method: 'POST', cache: 'no-store'
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || 'Không thể bắt đầu hiệu chuẩn');
        node.data.calibrationState = 1;
        node.data.calibrationProgress = 0;
        renderNodeTable();
        renderInspector();
    } catch (err) {
        alert('Không gửi được lệnh hiệu chuẩn tới ' + node.ip + '. Kiểm tra node, cùng mạng Wi-Fi và quyền truy cập mạng nội bộ/CORS. Chi tiết: ' + err.message);
    }
}

function toggleDemoQuake(nodeIndex) {
    if (!nodesList[nodeIndex] || !nodesList[nodeIndex].isSimulated) return;
    const node = nodesList[nodeIndex];
    node.demoQuake = !node.demoQuake;
    const btn = document.getElementById('btnSim' + (nodeIndex + 1));
    if (node.demoQuake) {
        btn.classList.add('active-quake');
        btn.textContent = `Dừng rung Node ${nodeIndex + 1}`;
        node.data.vibration = true; node.data.seismicScore = 94;
        node.data.ax = 5.2; node.data.ay = 3.6; node.data.az = 14.8;
        node.data.roll = 21.5; node.data.pitch = -14.2;
    } else {
        btn.classList.remove('active-quake');
        btn.textContent = `Thử rung Node ${nodeIndex + 1}`;
        node.data = { ...DEFAULT_NODES[nodeIndex].data };
    }
    selectNode(nodeIndex); renderTopology(); renderNodeTable();
}

function applyNodeData(node, d) {
    node.isOnline = d.online !== false;
    node.data = {
        ...node.data,
        soilPercent: Number(d.soilPercent || 0), soilRaw: Number(d.soilRaw || 0),
        soilTrendPerMinute: Number(d.soilTrendPerMinute || 0), soilTrendScore: Number(d.soilTrendScore || 0),
        vibration: !!d.vibration, mpuOK: !!d.mpuOK,
        ax: Number(d.ax || 0), ay: Number(d.ay || 0), az: Number(d.az || 0),
        gx: Number(d.gx || 0), gy: Number(d.gy || 0), gz: Number(d.gz || 0),
        roll: Number(d.roll || 0), pitch: Number(d.pitch || 0),
        tiltDelta: Number(d.tiltDelta || 0), tiltScore: Number(d.tiltScore || 0),
        calibrated: !!d.calibrated, calibrationState: Number(d.calibrationState || 0),
        calibrationProgress: Number(d.calibrationProgress || 0),
        calibrationMessage: d.calibrationMessage || '',
        baselineRoll: Number(d.baselineRoll || 0), baselinePitch: Number(d.baselinePitch || 0),
        moistureDanger: !!d.moistureDanger,
        moistureConfirmProgress: Number(d.moistureConfirmProgress || 0),
        seismicScore: Number(d.riskScore ?? d.seismicScore ?? 0)
    };
    if (d.ip) node.ip = d.ip;
    if (d.ssid) node.ssid = d.ssid;
}

function renderRelayDemo(relay, relayOnline) {
    const buffer = document.getElementById('relayBufferView');
    const state = document.getElementById('relayStateView');
    const packet = document.getElementById('relayPacketView');
    buffer.textContent = relay?.bufferedSeq
        ? 'Node 2 đang giữ mẫu mới nhất: SRC=1 · SEQ=' + relay.bufferedSeq
        : 'Chưa có mẫu mới trong bộ đệm Node 2.';
    packet.hidden = !relay?.seq;
    if (!relay) {
        state.textContent = 'Đang chờ dữ liệu từ ESP32.';
        return;
    }
    if (relay.phase === 'waiting') {
        state.textContent = relayOnline
            ? 'Node 1 đã mất kết nối. Node 2 đang chờ chuyển tiếp gói cuối…'
            : 'Node 2 đang offline. Gói cuối vẫn chờ chuyển tiếp.';
    } else if (relay.phase === 'forwarded') {
        state.textContent = 'Gateway đã nhận gói cuối từ Node 2 sau khi Node 1 mất kết nối.';
    } else if (relay.phase === 'empty') {
        state.textContent = 'Node 1 mất kết nối trước khi có mẫu để chuyển tiếp.';
    } else {
        state.textContent = 'Chưa có sự kiện mất kết nối.';
    }
    if (relay.seq) {
        packet.textContent = 'SRC=1 · SEQ=' + relay.seq;
        if (relay.phase !== 'forwarded') return;
        const relayDelay = ((relay.forwardedAt - relay.lostAt) >>> 0) / 1000;
        packet.textContent += ' · Chuyển tiếp sau ' + relayDelay.toFixed(1) + ' giây'
            + ' · Độ ẩm: ' + relay.soilPercent + '% (ADC ' + relay.soilRaw + ')'
            + ' · Roll/Pitch: ' + relay.roll + '° / ' + relay.pitch + '°'
            + ' · Rung: ' + (relay.vibration ? 'Có' : 'Không')
            + ' · Điểm nguy cơ: ' + relay.riskScore + '%';
    }
}

async function fetchLocalNodes(localNodes) {
    try {
        const response = await fetch('/data/all', { cache: 'no-store' });
        if (!response.ok) throw new Error('HTTP ' + response.status);
        const { nodes, relay } = await response.json();
        for (const node of localNodes) {
            const data = nodes.find(item => item.nodeId === node.id);
            if (data) applyNodeData(node, data);
            else node.isOnline = false;
        }
        renderRelayDemo(relay, nodes.some(node => node.nodeId === 'node-2' && node.online !== false));
        return true;
    } catch (err) {
        for (const node of localNodes) node.isOnline = false;
        renderRelayDemo(null, false);
        return false;
    }
}

async function fetchNodeData(node) {
    if (!node || node.isSimulated) return;
    try {
        const response = await fetch(nodeBaseUrl(node) + '/data?t=' + Date.now(), { cache: 'no-store' });
        if (!response.ok) throw new Error('HTTP ' + response.status);
        const d = await response.json();
        applyNodeData(node, d);
    } catch (err) {
        node.isOnline = false;
    }
}

async function fetchAllNodeData() {
    if (nodePollBusy) return;
    nodePollBusy = true;
    try {
        const localNodes = nodesList.filter(node => node.isLocal);
        const extraNodes = nodesList.slice(DEFAULT_NODES.length);
        const [connected] = await Promise.all([fetchLocalNodes(localNodes), ...extraNodes.map(fetchNodeData)]);
        const master = localNodes[0];
        if (connected) {
            document.getElementById('headerIP').textContent = master.ip;
            document.getElementById('headerStatus').textContent = 'ESP32 Đang Hoạt Động';
            document.getElementById('headerSSID').textContent = master.ssid || 'Đã kết nối';
        } else {
            document.getElementById('headerStatus').textContent = 'Mất kết nối ESP32';
        }
        renderTopology();
        renderNodeTable();
    } finally {
        nodePollBusy = false;
    }
}

loadNodes();
renderTopology();
renderNodeTable();
fetchAllNodeData();
setInterval(fetchAllNodeData, 1000);
</script>

</body>
</html>
)rawliteral";

// ==========================================
// 5. SENSOR PROCESSING & LANDSLIDE RISK
// ==========================================

bool SensorNode::checkSignalWires() {
    // Only Node 1 has diagnostic resistors. A connected output resists the
    // weak bias. A disconnected ESP-side signal follows it in both directions.
    if (this != &sensorNodes[0]) return signalsOK = true;
    pinMode(SOIL_TEST_PIN, OUTPUT);
    pinMode(VIBRATION_TEST_PIN, OUTPUT);
    digitalWrite(SOIL_TEST_PIN, LOW);
    digitalWrite(VIBRATION_TEST_PIN, LOW);
    delayMicroseconds(500);
    analogRead(soilPin); // discard the first ADC conversion after switching
    const int soilLow = analogRead(soilPin);
    const int vibrationLow = digitalRead(vibrationPin);
    digitalWrite(SOIL_TEST_PIN, HIGH);
    digitalWrite(VIBRATION_TEST_PIN, HIGH);
    delayMicroseconds(500);
    analogRead(soilPin);
    const int soilHigh = analogRead(soilPin);
    const int vibrationHigh = digitalRead(vibrationPin);
    pinMode(SOIL_TEST_PIN, INPUT);
    pinMode(VIBRATION_TEST_PIN, INPUT);
    delayMicroseconds(500);
    const bool soilOpen = soilLow < 800 && soilHigh > 3200;
    const bool vibrationOpen = vibrationLow == LOW && vibrationHigh == HIGH;
    if (soilOpen || vibrationOpen) {
        signalPasses = 0;
        if (signalMisses < 3) ++signalMisses;
        if (signalMisses == 3) signalsOK = false;
        return false; // never put a suspect reading into the relay buffer
    }
    signalMisses = 0;
    if (signalPasses < 3) ++signalPasses;
    if (!signalsOK && signalPasses == 3) {
        signalsOK = true;
        lastHandledVibrationPulse = vibrationPulseCounter;
        vibrationEverDetected = false;
        soilFilterInitialized = false;
        lastSoilTrendSample = 0;
        moistureHighSince = 0;
        moistureDanger = false;
        angleInitialized = sensorFilterInitialized = tiltDeltaInitialized = false;
        lastMPUTime = tiltAboveSince = 0;
        tiltConfirmed = false;
    }
    return signalsOK;
}

bool SensorNode::sample(unsigned long now) {
    if (!mpuOK) {
        if (now - lastMpuRetry < MPU_RETRY_MS) return false;
        lastMpuRetry = now;
        if (!connectMpu()) return false;
    }
    if (!probeMpu()) {
        if (++mpuMisses >= MPU_MISSES_TO_DISCONNECT) {
            mpuOK = false;
            lastMpuRetry = now;
            if (calibrationState == 1) {
                calibrationState = 3;
                calibrationProgress = 100.0f;
                setCalibrationMessage("Mat ket noi MPU-6050 khi hieu chuan");
            }
        }
        return false;
    }
    mpuMisses = 0;
    if (!checkSignalWires()) {
        if (!signalsOK && calibrationState == 1) {
            calibrationState = 3;
            calibrationProgress = 100.0f;
            setCalibrationMessage("Mat day tin hieu cam bien khi hieu chuan");
        }
        return false;
    }
    updateVibrationStatus(now);
    readSensors(now);
    return true;
}

void SensorNode::readSensors(unsigned long now) {
    // 1. SOIL MOISTURE
    long total = 0;
    for (int i = 0; i < 10; i++) {
        total += analogRead(soilPin);
        delayMicroseconds(200);
    }
    soilRaw = total / 10;

    if (soilDryRaw != soilWetRaw) {
        float mappedSoilPercent = 100.0f * (soilDryRaw - soilRaw) / (float)(soilDryRaw - soilWetRaw);
        mappedSoilPercent = clampFloat(mappedSoilPercent, 0.0f, 100.0f);
        if (!soilFilterInitialized) {
            soilPercent = mappedSoilPercent;
            soilFilterInitialized = true;
        } else {
            soilPercent += SOIL_FILTER_ALPHA * (mappedSoilPercent - soilPercent);
        }
    }
    updateSoilTrend(now);
    updateMoistureState(now);

    // 2. MPU-6050: low-pass filtering + complementary Roll/Pitch.
    if (mpuOK) {
        sensors_event_t accel;
        sensors_event_t gyro;
        sensors_event_t temp;
        mpu.getEvent(&accel, &gyro, &temp);

        float rawAx = accel.acceleration.x;
        float rawAy = accel.acceleration.y;
        float rawAz = accel.acceleration.z;
        float rawGx = gyro.gyro.x * 180.0f / PI;
        float rawGy = gyro.gyro.y * 180.0f / PI;
        float rawGz = gyro.gyro.z * 180.0f / PI;

        if (!sensorFilterInitialized) {
            filteredAx = rawAx; filteredAy = rawAy; filteredAz = rawAz;
            filteredGx = rawGx; filteredGy = rawGy; filteredGz = rawGz;
            sensorFilterInitialized = true;
        } else {
            filteredAx += SENSOR_FILTER_ALPHA * (rawAx - filteredAx);
            filteredAy += SENSOR_FILTER_ALPHA * (rawAy - filteredAy);
            filteredAz += SENSOR_FILTER_ALPHA * (rawAz - filteredAz);
            filteredGx += SENSOR_FILTER_ALPHA * (rawGx - filteredGx);
            filteredGy += SENSOR_FILTER_ALPHA * (rawGy - filteredGy);
            filteredGz += SENSOR_FILTER_ALPHA * (rawGz - filteredGz);
        }

        // Dashboard nhận giá trị đã làm mịn để tránh nhảy 1-2 đơn vị liên tục.
        ax = filteredAx; ay = filteredAy; az = filteredAz;
        gx = filteredGx; gy = filteredGy; gz = filteredGz;

        float accMagnitude = sqrtf(ax * ax + ay * ay + az * az);
        float gyroMagnitude = sqrtf(gx * gx + gy * gy + gz * gz);

        float rollAcc = atan2f(ay, az) * 180.0f / PI;
        float pitchAcc = atan2f(-ax, sqrtf(ay * ay + az * az)) * 180.0f / PI;

        float dt = 0.05f;
        if (lastMPUTime != 0) {
            dt = (now - lastMPUTime) / 1000.0f;
            dt = clampFloat(dt, 0.001f, 0.20f);
        }
        lastMPUTime = now;

        if (!angleInitialized) {
            roll = rollAcc;
            pitch = pitchAcc;
            angleInitialized = true;
        } else {
            roll = 0.98f * (roll + gx * dt) + 0.02f * rollAcc;
            pitch = 0.98f * (pitch + gy * dt) + 0.02f * pitchAcc;
        }

        // 3. Hiệu chuẩn gốc 8 giây, chỉ nhận mẫu ổn định.
        updateCalibration(now, ax, ay, az, gyroMagnitude);

        // 4. Độ lệch vector trọng lực 3D so với tư thế gốc.
        // Chỉ cập nhật khi không có rung và độ lớn gia tốc gần trọng lực.
        if (baselineValid && !vibrationDetected && accMagnitude >= 7.5f && accMagnitude <= 12.0f) {
            // Tái tạo vector trọng lực 3D từ Roll/Pitch đã lọc (kết hợp gyro + accelerometer).
            // Yaw không thể xác định ổn định chỉ bằng MPU-6050 nếu không có từ kế.
            float rollRad = roll * PI / 180.0f;
            float pitchRad = pitch * PI / 180.0f;
            float currentGX = -sinf(pitchRad);
            float currentGY = sinf(rollRad) * cosf(pitchRad);
            float currentGZ = cosf(rollRad) * cosf(pitchRad);
            if (normalizeVector(currentGX, currentGY, currentGZ)) {
                float dot = baselineGX * currentGX + baselineGY * currentGY + baselineGZ * currentGZ;
                dot = clampFloat(dot, -1.0f, 1.0f);
                float measuredDelta = acosf(dot) * 180.0f / PI;
                if (!tiltDeltaInitialized) {
                    tiltDelta3D = measuredDelta;
                    tiltDeltaInitialized = true;
                } else {
                    tiltDelta3D += TILT_FILTER_ALPHA * (measuredDelta - tiltDelta3D);
                }
            }
        }
        updateTiltScore(now);
    } else {
        tiltScore = 0.0f;
        tiltConfirmed = false;
    }

    // 5. RISK FUSION: độ ẩm 60%, độ nghiêng 30%, rung 10%.
    calculateLandslideRisk();
}

// ==========================================
// 6. HTTP API: DATA / CALIBRATION / STATUS
// ==========================================

void addCorsHeaders() {
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
    server.sendHeader("Access-Control-Allow-Private-Network", "true");
    server.sendHeader("Cache-Control", "no-store");
}

String currentIp() {
    return (WiFi.getMode() == WIFI_AP ? WiFi.softAPIP() : WiFi.localIP()).toString();
}

void SensorNode::formatData(char* json, size_t size, const char* ip) const {
    snprintf(json, size,
        "{\"nodeId\":\"%s\",\"name\":\"%s\",\"ip\":\"%s\",\"ssid\":\"%s\",\"online\":%s,\"soilRaw\":%d,\"soilPercent\":%.1f,\"soilTrendPerMinute\":%.2f,\"soilTrendScore\":%.1f,\"vibration\":%s,\"mpuOK\":%s,\"ax\":%.2f,\"ay\":%.2f,\"az\":%.2f,\"gx\":%.2f,\"gy\":%.2f,\"gz\":%.2f,\"roll\":%.2f,\"pitch\":%.2f,\"calibrated\":%s,\"calibrationState\":%u,\"calibrationProgress\":%.1f,\"calibrationMessage\":\"%s\",\"baselineRoll\":%.2f,\"baselinePitch\":%.2f,\"tiltDelta\":%.2f,\"tiltScore\":%.1f,\"moistureDanger\":%s,\"moistureConfirmProgress\":%.1f,\"soilScore\":%.1f,\"vibrationScore\":%.1f,\"riskScore\":%.1f,\"seismicScore\":%.1f}",
        id, name, ip, WIFI_SSID, online() ? "true" : "false", soilRaw, soilPercent, soilTrendPerMinute, soilTrendScore,
        vibrationDetected ? "true" : "false", mpuOK ? "true" : "false",
        ax, ay, az, gx, gy, gz, roll, pitch,
        baselineValid ? "true" : "false", static_cast<unsigned>(calibrationState), calibrationProgress, calibrationMessage,
        baselineRoll, baselinePitch, tiltDelta3D, tiltScore,
        moistureDanger ? "true" : "false", moistureConfirmProgress,
        soilScore, vibrationScore, seismicScore, seismicScore);
}

// Khi không có tham số node, các URL cũ tiếp tục trả về Node 1.
SensorNode* requestedNode();
SensorNode* requestedNode() {
    if (!server.hasArg("node")) return &sensorNodes[0];

    const String id = server.arg("node");
    for (SensorNode& node : sensorNodes) {
        if (id == node.id) return &node;
    }

    addCorsHeaders();
    server.send(404, "application/json; charset=utf-8", "{\"message\":\"Khong tim thay node\"}");
    return nullptr;
}

void sendCalibrationResponse(int statusCode, const SensorNode& node);
void sendCalibrationResponse(int statusCode, const SensorNode& node) {
    char json[512];
    snprintf(json, sizeof(json),
        "{\"nodeId\":\"%s\",\"calibrated\":%s,\"calibrationState\":%u,\"calibrationProgress\":%.1f,\"baselineRoll\":%.2f,\"baselinePitch\":%.2f,\"tiltDelta\":%.2f,\"message\":\"%s\"}",
        node.id, node.baselineValid ? "true" : "false", static_cast<unsigned>(node.calibrationState), node.calibrationProgress,
        node.baselineRoll, node.baselinePitch, node.tiltDelta3D, node.calibrationMessage);
    addCorsHeaders();
    server.send(statusCode, "application/json; charset=utf-8", json);
}

void handleData() {
    const SensorNode* node = requestedNode();
    if (!node) return;

    const String ip = currentIp();
    char json[1200];
    node->formatData(json, sizeof(json), ip.c_str());
    addCorsHeaders();
    server.send(200, "application/json; charset=utf-8", json);
}

void handleAllData() {
    const String ip = currentIp();
    char nodeJson[1200];
    String json;
    json.reserve(2 * sizeof(nodeJson) + 430);
    json += "{\"nodes\":[";
    for (const SensorNode& node : sensorNodes) {
        if (&node != &sensorNodes[0]) json += ',';
        node.formatData(nodeJson, sizeof(nodeJson), ip.c_str());
        json += nodeJson;
    }
    char relayJson[420];
    const RelayPacket& packet = lastRelayPacket;
    const char* phase = relayPending ? "waiting" :
                        packet.sequence ? "forwarded" :
                        sourceLostAt ? "empty" : "ready";
    snprintf(relayJson, sizeof(relayJson),
        "],\"relay\":{\"phase\":\"%s\",\"bufferedSeq\":%lu,\"seq\":%lu,\"sampledAt\":%lu,\"lostAt\":%lu,\"forwardedAt\":%lu",
        phase, relayBuffer.sequence, packet.sequence, packet.sampledAt, sourceLostAt,
        relayForwardedAt);
    json += relayJson;
    if (packet.sequence && !relayPending) {
        snprintf(relayJson, sizeof(relayJson),
            ",\"soilRaw\":%d,\"soilPercent\":%.1f,\"roll\":%.2f,\"pitch\":%.2f,\"vibration\":%s,\"riskScore\":%.1f",
            packet.soilRaw, packet.soilPercent, packet.roll, packet.pitch,
            packet.vibration ? "true" : "false", packet.riskScore);
        json += relayJson;
    }
    json += "}}";
    addCorsHeaders();
    server.send(200, "application/json; charset=utf-8", json);
}

void handleCalibration() {
    const SensorNode* node = requestedNode();
    if (node) sendCalibrationResponse(200, *node);
}

void handleStartCalibration() {
    SensorNode* node = requestedNode();
    if (!node) return;
    if (!node->online()) {
        node->setCalibrationMessage("Node mat ket noi cam bien");
        sendCalibrationResponse(503, *node);
        return;
    }
    if (node->calibrationState == 1) {
        sendCalibrationResponse(409, *node);
        return;
    }
    node->startCalibration();
    sendCalibrationResponse(202, *node);
}

void handleStatus() {
    const SensorNode* node = requestedNode();
    if (!node) return;

    char json[256];
    snprintf(json, sizeof(json), "{\"nodeId\":\"%s\",\"online\":%s,\"mpuOK\":%s,\"calibrated\":%s}",
             node->id, node->online() ? "true" : "false", node->mpuOK ? "true" : "false",
             node->baselineValid ? "true" : "false");
    addCorsHeaders();
    server.send(200, "application/json; charset=utf-8", json);
}

void handleOptions() {
    addCorsHeaders();
    server.send(204, "text/plain", "");
}

// ==========================================
// 7. WIFI CONNECTION
// ==========================================

void connectWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    Serial.print("Connecting WiFi");

    unsigned long startTime = millis();
    while (
        WiFi.status() != WL_CONNECTED &&
        millis() - startTime < 20000
    ) {
        delay(500);
        Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
        Serial.print("Open browser: http://");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nWiFi connection failed! Starting AP fallback...");
        WiFi.mode(WIFI_AP);
        WiFi.softAP("ESP32_Landslide_Monitor", "12345678");
        Serial.print("AP IP: ");
        Serial.println(WiFi.softAPIP());
    }
}

// ==========================================
// 8. SETUP
// ==========================================

void SensorNode::begin() {
    if (preferences.begin(baselineNamespace, false)) loadTiltBaseline();

    analogSetPinAttenuation(soilPin, ADC_11db);
    pinMode(vibrationPin, INPUT);
    attachInterruptArg(vibrationPin, onVibrationPulse, this, VIBRATION_ACTIVE_LOW ? FALLING : RISING);

    connectMpu();
    Serial.print(id);
    Serial.println(mpuOK ? ": MPU6050 CONNECTED" : ": MPU6050 NOT FOUND");
}

bool SensorNode::probeMpu() {
    wire.beginTransmission(MPU_ADDRESS);
    return wire.endTransmission() == 0;
}

bool SensorNode::connectMpu() {
    if (!wireReady) {
        wireReady = wire.begin(sdaPin, sclPin);
        if (!wireReady) return false;
        wire.setTimeOut(15);
    }
    if (!probeMpu() || !mpu.begin(MPU_ADDRESS, &wire)) return false;

    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_5_HZ);
    mpuMisses = 0;
    soilFilterInitialized = false;
    lastSoilTrendSample = 0;
    moistureHighSince = 0;
    moistureDanger = false;
    moistureConfirmProgress = 0;
    sensorFilterInitialized = false;
    angleInitialized = false;
    lastMPUTime = 0;
    tiltDeltaInitialized = false;
    tiltDelta3D = 0;
    tiltAboveSince = 0;
    tiltConfirmed = false;
    mpuOK = true;
    return true;
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n=============================================");
    Serial.println("       LANDSLIDE MONITORING SYSTEM           ");
    Serial.println("=============================================");

    analogReadResolution(12);
    for (SensorNode& node : sensorNodes) node.begin();

    // Connect WiFi
    connectWiFi();

    // Configure Web Server
    server.on("/", HTTP_GET, []() {
        server.send_P(
            200,
            "text/html; charset=utf-8",
            INDEX_HTML
        );
    });

    server.on("/data/all", HTTP_GET, handleAllData);
    server.on("/data/all", HTTP_OPTIONS, handleOptions);
    server.on("/data", HTTP_GET, handleData);
    server.on("/data", HTTP_OPTIONS, handleOptions);
    server.on("/calibration", HTTP_GET, handleCalibration);
    server.on("/calibration", HTTP_OPTIONS, handleOptions);
    server.on("/calibrate", HTTP_POST, handleStartCalibration);
    server.on("/calibrate", HTTP_OPTIONS, handleOptions);
    server.on("/status", HTTP_GET, handleStatus);
    server.on("/status", HTTP_OPTIONS, handleOptions);

    server.begin();
    Serial.println("Web Server Started successfully!");
    for (const SensorNode& node : sensorNodes) {
        Serial.print(node.id);
        Serial.print(" tilt baseline: ");
        Serial.println(node.baselineValid ? "LOADED" : "NOT CALIBRATED");
    }
    Serial.println("Risk weights: Soil 60%, Tilt 30%, Vibration 10%");
    Serial.println("=============================================");
}

// ==========================================
// 9. MAIN LOOP
// ==========================================

void loop() {
    // Xử lý request trước, sau đó mới lấy millis() để tránh now cũ hơn
    // thời điểm bắt đầu hiệu chuẩn trong HTTP handler.
    server.handleClient();

    unsigned long now = millis();

    if (now - lastSample >= SAMPLE_INTERVAL_MS) {
        lastSample = now;
        const bool sourceSampled = sensorNodes[0].sample(now);
        sensorNodes[1].sample(now);
        updateRelayDemo(now, sourceSampled);
    }

    delay(1);
}
