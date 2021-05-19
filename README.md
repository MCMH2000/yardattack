# Yardattack
Convenient tool for the YARD Stick One or HackRF

This Tool is based on Console Cowboys RFCrack tool https://github.com/cclabsInc/RFCrack
```
pi@pitoolbox:~/Desktop/yardattack $ ./yardattack --help
usage: yardattack [-h] [-c CAPTURE] [-r REPLAY] [-f FREQUENCY] [-m MODULATION]
                  [-b BAUDRATE] [-s RSSI] [-e EXTRACT]

       _  _   __    ____  ____
      ( \/ ) /__\  (  _ \(  _ \
       \  / /(__)\  )   / )(_) )
       (__)(__)(__)(_)\_)(____/
   __   ____  ____   __    ___  _  _
  /__\ (_  _)(_  _) /__\  / __)( )/ )
 /(__)\  )(    )(  /(__)\( (__  )  (
(__)(__)(__)  (__)(__)(__)\___)(_)\_)

Capture and Replay signals...

optional arguments:
  -h, --help            show this help message and exit
  -c CAPTURE, --capture CAPTURE
                        Capture received code in file
  -r REPLAY, --replay REPLAY
                        Replay code from file
  -f FREQUENCY, --frequency FREQUENCY
                        Frequency for capture. Default: 433000000
  -m MODULATION, --modulation MODULATION
                        Modulation for capture. Default: MOD_ASK_OOK
  -b BAUDRATE, --baudrate BAUDRATE
                        Baudrate for capture. Default: 9600
  -s RSSI, --rssi RSSI  Threshold value for capture to be triggered. Default:
                        -110
  -e EXTRACT, --extract EXTRACT
                        Extract signal from noise. Default: True
```
