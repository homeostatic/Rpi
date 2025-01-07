#!/usr/bin/env python 
"""
Goals:
    open GPIO midi connection
    open internal midi port
    parse incomming midi signals
    echo them to the virtual port
"""
from midi import MidiConnector
import mido



conn = MidiConnector('/dev/serial0', 38400)

port_name = 'GPOI_Midi_In'
port = mido.open_outport(port_name)

while True:
    msg = conn.read()
    port.send(msg)
