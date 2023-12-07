#!/usr/bin/env python
"""
================================================
Applent AT826 LCR Meter
Remote Control
================================================
Version:    0.1
Author:     Sinan Güngör
License:    GPL v2
"""

import platform
import libusb_package
import usb.core
import usb.util
import struct
if platform.system() == 'Windows':
    import usb.backend.libusb1

class Command():
    def __init__(self):
        self.size=60
        self.command=""
        self.parameter=""
        self.signature=0x88805550
        self.checksum=0
        self.commandPack=bytearray(64)
    def set_command_pack(self,command,parameter=None):

        if len(command) > 24 :
            self.command=command[:24].upper()
        else :
            self.command=command.upper()
        
        if parameter :
            if len(parameter) > 28 :
                self.parameter=parameter[:28].upper()
            else :
                self.parameter=parameter.upper()
            
        self.commandPack = [0x0 for i in range(len(self.commandPack))]
        pack=bytearray(struct.pack('<I',self.size))
        for i in range(len(pack)):
            self.commandPack[i]=pack[i]
        
        pack=bytearray(self.command,encoding='utf-8')
        for i in range(len(pack)):
            self.commandPack[4+i]=pack[i]
        
        if self.parameter :
            pack=bytearray(self.parameter,encoding='utf-8')
            for i in range(len(pack)):
                self.commandPack[28+i]=pack[i]
                
        pack=bytearray(struct.pack('<I',self.signature))
        for i in range(len(pack)):
            self.commandPack[56+i]=pack[i]
                
        self.checksum=self.calc_checksum(self.commandPack,self.size)
        pack=bytearray(struct.pack('<I',self.checksum))
        for i in range(len(pack)):
            self.commandPack[60+i]=pack[i]
                  
    def calc_checksum(self,buf,length):
        checksum=0
        for i in range(length):
            checksum+=buf[i]
        return checksum 
    def print(self):
        print("")
        print(" Size:         0x{s:08x}".format(s=self.size))
        print(" Command:      {}".format(self.command))
        print(" Parameter:    {}".format(self.parameter))
        print(" Signature:    0x{s:08x}".format(s=self.signature))
        print(" Checksum:     0x{c:08x}".format(c=self.checksum))
        print(" Command pack:","[ "+"0x{:02x},".format(self.commandPack[0])+ "".join(" 0x{:02x},".format(b) for b in self.commandPack[1:16])) 
        print("                "+"".join(" 0x{:02x},".format(b) for b in self.commandPack[16:32])) 
        print("                "+"".join(" 0x{:02x},".format(b) for b in self.commandPack[32:48])) 
        print("                "+"".join(" 0x{:02x},".format(b) for b in self.commandPack[48:63])+" 0x{:02x} ]".format(self.commandPack[63])) 
        print("")
        
class AT826():
    def __init__(self,vid,pid):
        self.VID=vid
        self.PID=pid
        self.dev=None
        self.command=Command()
        self.response=None
    def find(self):
        if platform.system() == 'Linux':
            self.dev = usb.core.find(idVendor=self.VID, idProduct=self.PID)
        elif platform.system() == 'Windows':
            backend = usb.backend.libusb1.get_backend(find_library=libusb_package.find_library)
            self.dev = usb.core.find(backend=backend,idVendor=self.VID, idProduct=self.PID)
        else :
            self.dev = usb.core.find(idVendor=self.VID, idProduct=self.PID)
    def claim(self):
        interface=0
        if platform.system() == 'Linux':
            if self.dev.is_kernel_driver_active(interface) is True:
                self.dev.detach_kernel_driver(interface)
        usb.util.claim_interface(self.dev, interface)
    def release(self):
        interface=0
        usb.util.release_interface(self.dev, interface)
        if platform.system() == 'Linux':
            self.dev.attach_kernel_driver(interface)
    
    def send_command(self,command,parameter=None):
        self.command.set_command_pack(command,parameter)
        endpointOut = self.dev[0][(0,0)][1]
        self.dev.write(endpointOut.bEndpointAddress,self.command.commandPack)

    def get_response(self):
        endpointIn = self.dev[0][(0,0)][0]
        try:
            data = self.dev.read(endpointIn.bEndpointAddress,endpointIn.wMaxPacketSize, timeout=500)
            self.responsePack=data
            databytes=data.tobytes()
            if 0x00 in databytes:
                end = databytes.index(0x00)
                return(databytes[0:end].decode())
            else :
                return (databytes.decode().append(b'\x00'))
        except usb.core.USBError as e:
            if str(e).find("timed out") >= 0:
                pass
            else:
                raise IOError("USB Error: {}".format(str(e)))
        return("")
    
