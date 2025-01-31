/*
Serial to MIDI conversion script for use on Rpi4
not yet tested on the rpi4
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <linux/serial.h>
#include <alsa/asoundlib.h>

#define SERIAL_PORT "/dev/serial0"
#define BAUD_RATE B38400
#define MIDI_PORT "hw:1,0,0"

int serial_fd;
snd_rawmidi_t *midi_out;
size_t message_length = 0;

// Function to handle errors and clean up resources
void error_exit(const char *message) {
    perror(message);
    if (serial_fd >= 0) close(serial_fd);
    if (midi_out) snd_rawmidi_close(midi_out);
    exit(EXIT_FAILURE);
}

// Function to configure the serial port
void configure_serial_port() {
    struct termios options;
    serial_fd = open(SERIAL_PORT, O_RDWR | O_NOCTTY | O_NDELAY);
    if (serial_fd == -1) {
        error_exit("Error opening serial port");
    }

     // Clear the O_NONBLOCK flag, making I/O operations blocking
    fcntl(serial_fd, F_SETFL, 0);
    // Get the current options for the port
    tcgetattr(serial_fd, &options);
    // Set the input baud rate
    cfsetispeed(&options, BAUD_RATE);
    // Set the output baud rate
    cfsetospeed(&options, BAUD_RATE);
    // Enable the receiver and set local mode
    options.c_cflag |= (CLOCAL | CREAD);
    // Disable parity bit
    options.c_cflag &= ~PARENB;
    // Use one stop bit
    options.c_cflag &= ~CSTOPB;
    // Clear the current character size mask
    options.c_cflag &= ~CSIZE;
    // Set the character size to 8 bits
    options.c_cflag |= CS8;
    // Disable hardware flow control
    options.c_cflag &= ~CRTSCTS;
    // Set raw input (no canonical mode, no echo, no signal chars)
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    // Disable software flow control
    options.c_iflag &= ~(IXON | IXOFF | IXANY);
    // Set raw output
    options.c_oflag &= ~OPOST;
    // Apply the options immediately
    tcsetattr(serial_fd, TCSANOW, &options);
}

// Function to configure the MIDI port
void configure_midi_port() {
    int status = snd_rawmidi_open(NULL, &midi_out, MIDI_PORT, 0);
    if (status < 0) {
        error_exit("Error opening MIDI output");
    }
}

// Function to send a MIDI message
void send_midi_message(unsigned char *message, size_t length) {
    if (snd_rawmidi_write(midi_out, message, length) < 0) {
        error_exit("Error sending MIDI message");
    }
    snd_rawmidi_drain(midi_out);
}

// Function to determine the length of a MIDI message based on the status byte
size_t get_message_length(unsigned char status_byte) {
    if ((status_byte & 0xF0) == 0xC0 || (status_byte & 0xF0) == 0xD0) {
        return 2;  // Program Change and Channel Pressure messages are 2 bytes long
    } else if ((status_byte & 0xF0) == 0xF0 && status_byte != 0xF0 && status_byte != 0xF7) {
        return 1;  // System Real-Time messages are 1 byte long
    } else {
        return 3;  // Most other MIDI messages are 3 bytes long
    }
}

int main() {
    configure_serial_port();
    configure_midi_port();

    unsigned char buffer[3];
    size_t buffer_index = 0;

    printf("Listening to %s at %d baud...\n", SERIAL_PORT, BAUD_RATE);
    printf("Opened MIDI output: %s\n", MIDI_PORT);

    while (1) {
        unsigned char byte;
        ssize_t bytes_read = read(serial_fd, &byte, 1);
        if (bytes_read > 0) {
            if (byte & 0x80) {  // If it's a status byte
                buffer_index = 0; // Reset buffer index to 0 to start a new message
                buffer[buffer_index++] = byte;
                message_length = get_message_length(byte);
            } else {           // Not a status byte
                buffer[buffer_index++] = byte;
            }

            if (buffer_index >= message_length) {
                send_midi_message(buffer, buffer_index);
                // Reset to 1 to keep the status byte for running-status, will be set to 0 if the next read is a status byte
                buffer_index =  1;  
            }
        } else if (bytes_read < 0) {
            fprintf(stderr, "Error reading from serial port: %s\n", strerror(errno));
            // Optionally, can add a delay here to avoid busy-waiting in case of repeated errors
            usleep(10000);  // Sleep for 10 milliseconds
        }
    }

    close(serial_fd);
    snd_rawmidi_close(midi_out);
    return 0;
}

