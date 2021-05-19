from rflib import *
import sys
import time
import argparse
import textwrap
import bitstring
import configparser
import datetime
import os


parser = argparse.ArgumentParser(description='Yard Attack.')

#path for catures
capture_path = "./captures"
if not os.path.exists(capture_path):
    os.makedirs(capture_path)

#default file name (timestamp)
def filename():
    now = datetime.datetime.now()
    ts = now.strftime("%Y-%m-%d-%H-%M-%S")
    return ts

#creates bytecode from payload  that can be send with RFxmit
def createBytesFromPayload(payload):
    binary = bin(int(payload,16))[2:]
    formatedPayload = bitstring.BitArray(bin=(binary)).tobytes()
    return formatedPayload

#creates printable hexcode in RFxmit syntax "\x8e\x9f\x90\x00"
#return value can NOT be used in RFxmit function
def createFormatedHexFromPayload(payload):

    formatedPayload = ""
    iterator = iter(payload)
    for i in iterator:
        try:
            formatedPayload += ('\\x' + i + next(iterator))
        except StopIteration:
            pass

    return formatedPayload

def capturePayload(d, split):
    capture = ""
    try:
        for i in range(72):
            y, z = d.RFrecv() #capture input
            capture += y.encode('hex') #and append it on the whole
        print("Received raw input:")
        print(capture) #print raw output
        print("")
    except ChipconUsbTimeoutException:
        print("DEBUG: ChipconUsbTimeoutException")
    else:
        pass
        #raise

    #parsing captured code
    if split == True:
         #remove empty code "ffffff*" to split or rather extract the payload from whole capture
        items = re.split('ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff*', capture) #0000*|ffff*
    else:
        #capture as one payload (for noisy enviroment)
        items = [capture]
    payloads = [] #array of all useable captured payloads
    for item in items:
        if len(item) >= 6: #if length of one item after split is <6 it will be ignored
            if (len(item) % 2 != 0): #adjust length of payload
                item += item + '0' #if length is odd then add a 0 to the end
            payloads.append(item) #append to array of useable payloads
    
    return payloads

def writeConfig(frequency, modulation, baudrate, payloads, name):
    #write configuration file for captured payloads
    config = configparser.ConfigParser()
    config.add_section("radioconfig")
    config.add_section("replaymessage")
    config.set("radioconfig", "frequency", str(frequency))
    config.set("radioconfig", "modulation", modulation)
    config.set("radioconfig", "baudrate", str(baudrate))
    for index, value in enumerate(payloads): #for each useable payload in array payloads
        config.set("replaymessage", str(index), str(value)) #create a seperate entry for the payload
        print("{} = {}".format(index, createFormatedHexFromPayload(value))) #print the payload with index in file
    with open("{}/{}.cfg".format(capture_path, name), 'wb') as configfile:
        config.write(configfile) #write configfile

#argument help
parser = argparse.ArgumentParser(add_help=True, formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent('''\
       _  _   __    ____  ____       
      ( \/ ) /__\  (  _ \(  _ \      
       \  / /(__)\  )   / )(_) )     
       (__)(__)(__)(_)\_)(____/      
   __   ____  ____   __    ___  _  _ 
  /__\ (_  _)(_  _) /__\  / __)( )/ )
 /(__)\  )(    )(  /(__)\( (__  )  ( 
(__)(__)(__)  (__)(__)(__)\___)(_)\_)

Capture and Replay signals...

       '''))
#other arguments
parser.add_argument("-c", "--capture", help="Capture received code in file")
parser.add_argument("-r", "--replay", help="Replay code from file")
parser.add_argument("-f", "--frequency", default="433000000", help="Frequency for capture. Default: 433000000", type=int)
parser.add_argument("-m", "--modulation", default="MOD_ASK_OOK", help="Modulation for capture. Default: MOD_ASK_OOK")
parser.add_argument("-b", "--baudrate", default="9600", help="Baudrate for capture. Default: 9600", type=int)
parser.add_argument("-s", "--rssi", default="-110", help="Threshold value for capture to be triggered. Default: -110", type=int)
parser.add_argument("-e", "--extract", default="false", help="Extract signal from noise. Default: True")

args = parser.parse_args()

try:
    if (281000000 > args.frequency > 361000000) or (378000000 > args.frequency > 481000000) or (749000000 > args.frequency > 962000000):
        print("Frequency not in range")
        raise
    
    d = RfCat()
    
    #if capture argument is given
    if not args.capture == None:
        
        #set device to given or default settings
        d.setMaxPower()
        d.setFreq(args.frequency)
        d.setMdmModulation(eval(args.modulation))
        d.setMdmDRate(args.baudrate)
        d.lowball(1)
        
        while True:
            try:
                signal_strength = 0 - ord(str(d.getRSSI())) #get signal strength

            except ChipconUsbTimeoutException: #when usb timeout
                pass
            
            except UnicodeDecodeError: #when signal is to weak
                pass
            
            else: #if no errors occure
                if signal_strength >= args.rssi: #if signal is stronger than given or default value
                    try:
                        print("")
                        print("Signal Strength RSSI: {}".format(signal_strength))
                        if args.extract == "true":
                            split = True
                        else:
                            split = False
                        payloads = capturePayload(d, split)
                        writeConfig(args.frequency, args.modulation, args.baudrate, payloads, args.capture)
                        break
                    except:
                        break

        
    #if replay argument is given
    if not args.replay == None:
        try:
            config = configparser.ConfigParser()
            config.read("{}/{}.cfg".format(capture_path, args.replay)) #open given configfile
            freq = config.getint("radioconfig", "frequency") #get frequency from file
            mod  = config.get("radioconfig", "modulation") #get modulation from file
            baud = config.getint("radioconfig", "baudrate") #get baudrate from file
            
            #print parameters from file
            print("Frequency: {}".format(freq))
            print("Modulation: {}".format(mod))
            print("Baudrate: {}".format(baud))
            print("")
            
            d.setMaxPower()
            d.setFreq(freq) #set device frequency
            d.setMdmModulation(eval(mod)) #set device modulation as object [eval()]
            d.setMdmDRate(baud) #set device baudrate
            
            payloads = config.items("replaymessage")
            for packet, payload in payloads: #for each payload in section [replaymessage]
                print(" Sending Payload {}:".format(packet)) #print payload number
                print(createFormatedHexFromPayload(payload)) #print formated payload
                send = createBytesFromPayload(payload) #create sendable bytecode from payload
                d.RFxmit(send)
                if len(payloads) != int(packet)+1: #if end of payload list is not reached
                    print("Press CTRL+C if the payload worked. Otherwise the next one will be sent in 8 seconds.")
                    print("")
                    time.sleep(8) #wait for the user to have a chance to cancel operation
            
        except configparser.NoSectionError:
            print("File not Found") #if file can not be read, file does probably not exists
        
finally: #finally do not forget to set device back to idle mode
    d.setModeIDLE()
