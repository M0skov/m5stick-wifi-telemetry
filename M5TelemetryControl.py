#######################################################
##Jan Gomez
##Lab 3 - WiFi Telemetry (corrections)
##Instructor Kyle Jonhsen
#######################################################
import paho.mqtt.client as mqtt
import time
import struct
from datetime import datetime
import csv
import tkinter as tk
from tkinter import ttk

MOVEMENT_TOPIC ="elee2045/jan_gomez_FINAL/movement";
BATTERY_TOPIC = "elee2045sp25/jan_gomez_FINAL/battery";
SOUND_TOPIC ="elee2045/jan_gomez_FINAL/sound";
RATE_TOPIC = "elee2045sp25/jan_gomez_FINAL/rate";
VELOCITY_TOPIC ="elee2045/jan_gomez_FINAL/velocity";

CSV_Movement1 = "Movement topic1.csv"
CSV_Battery1 = "Battery_topic1.csv"
CSV_Sound1 = "Sound_Topic1.csv"
CSV_Velocity1 = "Velocity_topic1.csv"

class MQTTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MQQT DATA Battery, Movement and Sound")

        self.accel_data = ttk.Label(root, text="Accelerometer: ")
        self.accel_data.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.gyro_data = ttk.Label(root, text="Gyro: ")
        self.gyro_data.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.velocity_data = ttk.Label(root, text="Velocity: ")
        self.velocity_data.grid(row=2, column=0, columnspan=2, sticky="nsew")

        self.battery_data = ttk.Label(root, text="Battery: ")
        self.battery_data.grid(row=3, column=0, columnspan=2, sticky="nsew")

        self.sound_data = ttk.Label(root, text="Sound: ")
        self.sound_data.grid(row=4, column=0, sticky="nsew")

        self.sound_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate", maximum=1.0)
        self.sound_bar.grid(row=4, column=1, sticky="nsew")

        self.last_received = ttk.Label(root, text="Last Received : ")
        self.last_received.grid(row=5, column=0, columnspan=2, sticky="nsew")

        self.rate_input_label = ttk.Label(root, text="Update Rate in seconds :")
        self.rate_input_label.grid(row=6, column=0, sticky="nsew")

        self.rate_input = ttk.Entry(root)
        self.rate_input.grid(row=6, column=1, sticky="nsew")
        self.rate_input.insert(0, "60.0")

        self.send_rate_btn = ttk.Button(root, text="Set Rate", command=self.send_rate)
        self.send_rate_btn.grid(row=7, column=0, columnspan=2, pady=5)

        self.client = mqtt.Client()
        self.client.username_pw_set("giiuser", "giipassword")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.vx = self.vy = self.vz = None

        print("Connecting to broker...")
        self.client.connect("eduoracle.ugavel.com", 1883)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            client.subscribe(MOVEMENT_TOPIC)
            client.subscribe(BATTERY_TOPIC)
            client.subscribe(SOUND_TOPIC)
            client.subscribe(VELOCITY_TOPIC)
        else:
            print("Connection failed")

    def on_message(self, client, userdata, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_received.config(text=f"Last data obtained at {timestamp}")
        try:
            if msg.topic == MOVEMENT_TOPIC:
                ax, ay, az, gx, gy, gz = struct.unpack("<ffffff", msg.payload)
                self.accel_data.config(text=f"Accel: {ax:.2f}, {ay:.2f}, {az:.2f}")
                self.gyro_data.config(text=f"Gyro: {gx:.2f}, {gy:.2f}, {gz:.2f}")
                self.save_to_csv(timestamp, ax, ay, az, gx, gy, gz)
            elif msg.topic == VELOCITY_TOPIC:
                 self.vx, self.vy, self.vz = struct.unpack("<fff", msg.payload)
                 self.velocity_data.config(text=f"Velocity: {self.vx:.2f}, {self.vy:.2f}, {self.vz:.2f}")
                 self.save_to_csv3(timestamp, self.vx, self.vy, self.vz)
            elif msg.topic == BATTERY_TOPIC:
                 voltage = struct.unpack("<h", msg.payload)[0]
                 self.battery_data.config(text=f"Battery: {voltage} mV")
                 self.save_to_csv1(timestamp, voltage)
            elif msg.topic == SOUND_TOPIC:
                 sound_level = struct.unpack("<f", msg.payload)[0]
                 self.sound_data.config(text=f"{sound_level:.2f}")
                 self.sound_bar["value"] = sound_level
                 self.save_to_csv2(timestamp, sound_level)
        except Exception as e:
            print("Error unpacking message:", e)

    def send_rate(self):
        try:
            seconds = float(self.rate_input.get())
            milliseconds = int(seconds * 1000)
            packed = struct.pack("<I", milliseconds)
            self.client.publish(RATE_TOPIC, packed, retain=True)
            print(f"Sent rate: {seconds} seconds")
        except ValueError:
            print("Invalid number entered.")

    def save_to_csv(self, time_str, ax, ay, az, gx, gy, gz):
        with open(CSV_Movement1, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time_str, ax, ay, az, gx, gy, gz])

    def save_to_csv1(self, time_str, battery):
        with open(CSV_Battery1, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time_str, battery])

    def save_to_csv2(self, time_str, sound):
        with open(CSV_Sound1, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time_str, sound])

    def save_to_csv3(self, time_str, vx, vy, vz):
        with open(CSV_Velocity1, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time_str, vx, vy, vz])

if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTApp(root)
    root.mainloop()
