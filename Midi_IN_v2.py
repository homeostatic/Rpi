#!/usr/bin/env python 
import serial
import mido
from mido import Message

# Configure the serial port
SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 38400

# Configure Midi port name
MIDI_OUT  = 'M8 MIDI 1'

# Open the serial port
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"Listening to {SERIAL_PORT} at {BAUD_RATE} baud...")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit(1)

# Open a mido output port
try:
    midi_out = mido.open_output(MIDI_OUT)  # Opens the default MIDI output port
    print(f"Opened MIDI output: {midi_out.name}")
except Exception as e:
    print(f"Error opening MIDI output: {e}")
    ser.close()
    exit(1)

def parse_midi_message(serial_data):
    """
    Parses raw MIDI bytes into a mido Message object.
    Handles 1-, 2-, or 3-byte MIDI messages.
    """
    try:
        # Mido automatically handles MIDI Running Status if used properly
        return Message.from_bytes(serial_data)
    except Exception as e:
        print(f"Error parsing MIDI message: {e}")
        return None

# Read and forward MIDI messages
try:
    buffer = bytearray()  # Buffer to store incoming bytes
    while True:
        if ser.in_waiting > 0:
            byte = ser.read(1)  # Read one byte from the serial port
            buffer.append(ord(byte))  # Append the byte to the buffer
            
            # Try to parse the MIDI message
            if len(buffer) >= 3:  # Most MIDI messages are 3 bytes
                message = parse_midi_message(buffer[:3])
                if message:
                    print(f"Received MIDI: {message}")
                    midi_out.send(message)
                    buffer.clear()  # Clear the buffer for the next message
                elif len(buffer) > 3:  # Avoid buffer overflows
                    buffer.pop(0)
except KeyboardInterrupt:
    print("\nExiting...")

# Cleanup
finally:
    ser.close()
    midi_out.close()
    print("Serial port and MIDI output closed.")
