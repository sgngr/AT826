from at826 import *
import time

# Ensure the 'libusb' library is found!
print("libusb path:\n\t{}\n".format(libusb_package.get_library_path())) 


at826=AT826(0x0825,0x0826)

at826.find()
if at826.dev == None :
    print ("Applent AT826 not found!") 
    exit()
print ("Applent AT826 found!") 

at826.claim()

#at826.send_command("Rst")  # USB enumaretion changes after a hot reset
#time.sleep(4) # Wait the device to restart   
#at826.find()
#at826.claim()

at826.send_command("IDN?")
print(at826.get_response())

at826.command.print()

at826.send_command("FETC?")
print(at826.get_response())

at826.send_command("disp:line","Test 123")

at826.release()
