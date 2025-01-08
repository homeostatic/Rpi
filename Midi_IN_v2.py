import serial
import mido
from mido import Message

# Configure the serial port
SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 38400


# Open the serial port
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"Listening to {SERIAL_PORT} at {BAUD_RATE} baud...")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit(1)

# Open a mido output port
try:
    midi_out = mido.open_output('M8 MIDI 1')  # Opens the default MIDI output port
    print(f"Opened MIDI output: {midi_out.name}")
except Exception as e:
    print(f"Error opening MIDI output: {e}")
    ser.close()
    exit(1)

# Initialize Running Status
last_status_byte = None

def parse_midi_message(byte_stream):
    """
    Parses raw MIDI bytes into a mido Message object.
    Handles 1-, 2-, or 3-byte MIDI messages and Running Status.
    """
    global last_status_byte
    try:
        # Check if the first byte is a status byte
        if byte_stream[0] & 0x80:
            last_status_byte = byte_stream[0]  # Update Running Status
            return Message.from_bytes(byte_stream)
        else:
            # If no status byte, prepend the last known status byte
            if last_status_byte is not None:
                return Message.from_bytes([last_status_byte] + byte_stream)
            else:
                print("Error: Missing status byte and no Running Status available.")
                return None
    except Exception as e:
        print(f"Error parsing MIDI message: {e}")
        return None

# Read and forward MIDI messages
try:
    buffer = bytearray()  # Buffer to store incoming bytes
    while True:
        if ser.in_waiting > 0:
            byte = ser.read(1)[0]  # Read one byte from the serial port
            
            # Add byte to buffer and handle Running Status
            if byte & 0x80:  # If it's a status byte
                if buffer:  # Process any incomplete message
                    message = parse_midi_message(buffer)
                    if message:
                        print(f"Received MIDI: {message}")
                        midi_out.send(message)
                    buffer.clear()  # Clear the buffer
                buffer.append(byte)  # Start a new message
            else:
                buffer.append(byte)  # Add data byte to the buffer
            
            # Try to parse the message when we have enough bytes
            if len(buffer) >= 3:  # Most MIDI messages are 3 bytes
                message = parse_midi_message(buffer)
                if message:
                    print(f"Received MIDI: {message}")
                    midi_out.send(message)
                    buffer.clear()  # Clear the buffer for the next message
except KeyboardInterrupt:
    print("\nExiting...")

# Cleanup
finally:
    ser.close()
    midi_out.close()
    print("Serial port and MIDI output closed.")
