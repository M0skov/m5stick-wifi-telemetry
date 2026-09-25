# M5Stick WiFi Telemetry

Lab 3 (ELEE 2045): the M5Stick connects over WiFi and streams live sensor telemetry over MQTT, with a Python dashboard that displays and logs the data.

## What it does

- **M5Stick firmware** (`Telemetryc_code_arduino/`) connects to WiFi and publishes telemetry to MQTT topics: accelerometer/gyro movement, battery level, sound, and velocity.
- **Python dashboard** (`M5TelemetryControl.py`) subscribes to the topics with a Tkinter GUI showing live values and logs each stream to its own CSV file.

## Files

- `Telemetryc_code_arduino/Telemetryc_code_arduino.ino` - M5Stick firmware (WiFi + MQTT publishing)
- `Telemetryc_code_arduino/wifi_final_version.h` - WiFi connection helper
- `M5TelemetryControl.py` - Tkinter dashboard and CSV logger
- `Battery_topic1.csv`, `Movement topic1.csv`, `Sound_Topic1.csv`, `Velocity_topic1.csv` - sample logged telemetry

Demo: https://youtube.com/shorts/WL20rkbZPdY

## Setup

```bash
pip install paho-mqtt
```

Flash the `.ino` to the M5Stick with the Arduino IDE (M5StickC board support), enter your WiFi credentials on the device when prompted, then run:

```bash
python M5TelemetryControl.py
```
