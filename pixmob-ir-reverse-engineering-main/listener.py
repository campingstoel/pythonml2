import serial
import subprocess

ser = serial.Serial('COM3', 115200)  # Change 'COM3' to the port your Circuit Playground is connected to

while True:
    if (ser.in_waiting > 0):
        print("Waiting for data...")
        line = ser.readline().decode('utf-8').rstrip()
        print(f"Received: {line}")  # This will print the received line
        if line == "Button A pressed":
            subprocess.run(["python", "path/to/demo_multiple_effects.py"])