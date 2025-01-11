# Rpi
# disclaimer: I have no idea what I am doing and it's frankly a miracle that any of this worked
Files for use on my custom Rpi4 - m8 tracker interface.

Trying to document this now the project is in a functional state.
This has been a long process with frequent and extended breaks. so I have probably forgotten some steps.

The hardware setup is:

teensy4.0                              -  M8 tracker Headless hardware

adafruit ItsyBitsy 5v                  - Custom USB HID (keypad),
this arduino board has a chip on it which lets it act as a plug and play "keyboard" which is maybe not really needed but makes it very simple to integrate into the setup.
      
USB Audio IO  (cheap junk from amazon)

5-PIN DIN MIDI IO board                - with 6n138 optocoupler

Momentary pushbutton                   - power switch

Raspberry Pi 4


Broadly speaking I followed the excellent guide by RowdyVoyeur: 
  https://github.com/RowdyVoyeur/m8c-rpi4

  notes:
  patchbox does seem be pretty good in terms of audio and midi latency.
    however I don't really understand the 'modules' and the one made by RowdyVoyeur to auto-start M8c on boot doesn't work for me.

  I have edited the launch script to also start my midi_IN.py script as well as disabled a number of things that were specific to Rowdy's system.  
  
  audio config that works reasonably well for me:
    I get occasonal crackle on my audio but I find it mostly pretty good.
    I suspect the crackle is linked to the delay which is printed by m8c and might be linked to general load on the system (it seems worse when the m8 is playing many tracks?)
          (it is also more obvious when MIDI in is receiving lots of data)
          possibly could be improved by reducing script load on rpi4 or maybe overclocking slightly?

   m8c audio enabled
   
   44100 hz
   
   2 jack period
   
   64 chunk size
   

   audio input doesn't always connect properly, recently the hacky workaround is to make sure the input is active when starting m8c?? 

   another issue is that (since upgrading to M8 firmware 4.0?) the tracker doesn't seem to be exiting gracefully. State is not saved between power cycles.

   the shutdown command is also apparently not working properly in m8c. It gets stuck on "closing audio devices"
   

for MIDI over GPIO BLitz city DIY has made a very good tutorial on how to free the RX and TX pins and set them up to be the serial IO as well as some info about MIDI hardware:
  https://www.youtube.com/watch?v=RbdNczYovHQ

for the serial to MIDI python scripts (maybe python is not the best solution but it seems to work) I use the py-serial Library and MIDO (which is based on the rt-midi backend)

config of the power button:
  in /boot/config.txt
  ...
  



