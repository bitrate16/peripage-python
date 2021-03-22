import bluetooth
from enum import Enum

class PrinterType(Enum):
    """
    Defines names for supported printer types.
    Currently supported printers are: Peripage A6, Peripage A6+
    """
    A6  = 6
    A6p = 7

class Printer:
    """
    This class defines the Peripage A6 / A6+ interface utility.
    It contains methods wrapping requests with special control opcodes.
    By default instance of this class is constructed with timeout set 
    to 1s and printer type A6.
    """
    
    def __init__(self, mac, printertype=PrinterType.A6, timeout=1.0):
        """
        Creates an instance of this wrapper class and stores passed mac 
        address for future connection (reconnection) to the printer.
        By default printer type is set to A6.
        By default timeout for connection / request is set to 1sec and 
        can be changed later with setTimeout(timeout).
        
        TODO: Autimatically recognize printer type and avoid using 
        explicit definition or leave it for explicit compability bypassing.
        """
        
        self.mac = mac
        self.printerType = printertype
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.settimeout(timeout)
    
    def isConnected(self):
        """
        Checks if printer is connected.
        """
        
        try:
            self.sock.getpeername()
            return True
        except:
            return False
    
    def connect(self):
        """
        Opens a new connection to the printer. Does not perform check if it
        was already connected or socket is in use.
        """
        
        self.sock.connect((self.mac, 1))
    
    def reconnect(self):
        """
        Reconnects to the printer. If connection already exists, socket is 
        being closed first.
        """
        
        if isConnected():
            self.sock.close()
        self.sock.connect((self.mac, 1))
    
    def disconnect(self):
        """
        Disconnects from the printer.
        """
        
        if isConnected():
            self.sock.close()
    
    def setTimeout(self, timeout):
        """
        Used to set a connection / send / recv timeout for bluetooth socket.
        """

        self.sock.settimeout(timeout)
    
    
    def tellPrinter(self, byteseq):
        """
        Send byte sequence to the printer and return, no response is expected
        """
        
        self.sock.send(byteseq)

    def askPrinter(self, byteseq, recv_size=1024):
        """
        Send byte sequence to the printer and receive recv_size bytes as response
        """
        
        self.sock.send(byteseq)
        return self.sock.recv(recv_size)

    def listenPrinter(self, recv_size=1024):
        """
        Receive recv_size bytes from the printer
        """
        
        return self.sock.recv(recv_size)

    def tellPrinterSeq(self, byteseq):
        """
        Send byte sequence list to the printer and return, no response is expected
        """
        
        for s in byteseq:
            self.sock.send(s)

    def askPrinterSeq(self, byteseq, recv_size=1024):
        """
        Send byte sequence list to the printer and receive recv_size bytes as response
        """
        
        for s in byteseq:
            self.sock.send(s)
        return self.sock.recv(recv_size)


    def getDeviceIP(self):
        """
        Returns Unknown Property as response of 0x10ff20f0.
        For example, Peripage A6+ returns 'IP-300'
        """
        
        return askPrinter(bytes.fromhex('10ff20f0'))

    def getDeviceName():
        """
        Returns Device Name as response of 0x10ff3011.
        For example, Peripage A6+ returns 'PeriPage+DF7A'
        """
        
        return askPrinter(bytes.fromhex('10ff3011'))

    def getDeviceSerialNumber():
        """
        Returns Serial Number as response of 0x10ff20f2.
        For example, Peripage A6+ returns 'A6491571121'
        """
        
        return askPrinter(bytes.fromhex('10ff20f2'))

    def getDeviceFirmware():
        """
        Returns Firmware Version as response of 0x10ff20f1.
        For example, Peripage A6+ returns 'V2.11_304dpi'
        """
        
        return askPrinter(bytes.fromhex('10ff20f1'))

    def getDeviceBattery():
        """
        Returns battery value as response of 0x10ff50f1.
        For example, Peripage A6+ returns '\x00@' (sample retult).
        Request returns result of type byte[2] where result[1] is charge 
        lever, result[0] is 0.
        """
        return int(askPrinter(bytes.fromhex('10ff50f1'))[1])

    def getDeviceHardware():
        """
        Returns Hardware Info as response of 0x10ff3010.
        For example, Peripage A6+ returns 'BR2141e-s(A02)_B9_20190815_r3460',
        that means that it has a BR2141e-s chip inside and a small amount of 
        additional ascii characters.
        """
        
        return askPrinter(bytes.fromhex('10ff3010'))

    def getDeviceMAC():
        """
        Returns Device's MAC address as response of 0x10ff3012.
        For example, Peripage A6+ returns 
        '\x00\xF5\x73\x25\xAC\x9F_\x00\xF5\x73\x25\xAC\x9F_', which is equal to
        00:F5:73:25:AC:9F
        """
        
        return askPrinter(bytes.fromhex('10ff3012'))

    def getDeviceFull():
        """
        Returns Full device information as response of 0x10ff70f1.
        For example, Peripage A6+ returns 
        'PeriPage+DF7A|00:F5:73:25:AC:9F|C5:12:81:19:2C:51|V2.11_304dpi|A6491571121|84', 
        which means that it's name is 'PeriPage+DF7A', mac is 00:F5:73:25:AC:9F, 
        connected to mac C5:12:81:19:2C:51, F/W V2.11_304dpi, S/N A6491571121, battery
        level 84%.
        """
        
        return askPrinter(bytes.fromhex('10ff3012'))
    
    def getRowBytes(self):
        """
        Returns an amount of bytes used to encode a single image row. 
        Image is encoded as one bit per pixel. For Peripage A6 a single row contains 48 
        bytes of biary pixel data. Peripage A6+'s single row contains 72 bytes of binary 
        pixel data.
        For example 0b10101010 encodes an image with alternating black and white pixels, 
        total 8 pixels and 1 byte to encode.
        If you want to work with raw bytes printing, you shout fit your images into this 
        bytes limits.
        """
        
        if self.printerType == PrinterType.A6:
            return 48
        elif self.printerType == PrinterType.A6p:
            return 72
        else:
            raise ValueError('Unsupported printer type')
    
    def getRowWidth(self):
        """
        Returns resolution of a single image row that can be printed.
        For Peripage A6 it is 384 pixels, for Peripage A6+ it is 576 pixels.
        If you want to work with raw bytes printing, you shout fit your images into this 
        pixel limits.
        """
        
        if self.printerType == PrinterType.A6:
            return 384
        elif self.printerType == PrinterType.A6p:
            return 576
        else:
            raise ValueError('Unsupported printer type')
        
    def getHeightLimit(self):
        """
        Returns height limit for image in pixels. If image size exceeds this height, it 
        should be splitted into multiple different images
        """
        return 0xffff
    
    
    def setDeviceSerialNumber(self, snstr, wait=True):
        """
        Sets a new Serial Number for the device as snstr using 0x10ff20f4
        Autimatically terminates string with '\0' because '\0' is required to explicitly
        send string in C-style to the printer. Missing '\0' may result in internal memory 
        corruption or S/N read timeouts (which can be fixed by writing a new correct S/N).
        Limitations for S/N string are not currently determined.
        Call to 0x10ff20f4 returns 'OK' as the result of S/N change.
        """
        
        tellPrinter(bytes.fromhex('10ff20f4'))
        if wait:
            return askPrinter(bytes(snstr + '\0', 'ascii'))
        else:
            tellPrinter(bytes(snstr + '\0', 'ascii'))

    def setPowerTimeout(self, timeout, wait=True):
        """
        Sets the device timeout (in minutes) to the value (bound between 0x0001 and 0xfff0) 
        using 0x10ff12.
        Call to 0x10ff12 returns 'OK' as the result of timeout change.
        """
        
        timeout = max(min(0xfff0, timeout), 0x0001)
        strtimeout = '{0:0{1}X}'.format(timeout, 4)
        if wait:
            return askPrinter(bytes.fromhex('10ff12' + strtimeout))
        else:
            tellPrinter(bytes.fromhex('10ff12' + strtimeout))
    
    def setConcentration(self, cons, wait=False):
        """
        Sets the printing concentration using 0x10ff1000 opcode.
        Currently allowed values are 0, 1, 2 which represents light, medium, hard 
        (heating intensivity). Other values are not tested yet.
        """
        
        opcode = ''
        
        if cons <= 0:
            opcode = '10ff100000'
        elif cons == 1:
            opcode = '10ff100001'
        elif cons >= 2:
            opcode = '10ff100002'
        
        if wait:
            return askPrinter(bytes.fromhex(opcode))
        else:
            tellPrinter(bytes.fromhex(opcode))
    
    
    def reset(self):
        """
        Performs reset operation (The initial purpose of it is stoll unknown) 
        required before printing stream of bytes in a binary image.
        Opcode for this operation is 0x10fffe01 followed by 0x000000000000000000000000.
        """
        
        tellPrinter(bytes.fromhex('10fffe01000000000000000000000000'))
    
    def printBreak(self, size=0x40):
        """
        Asks printer to print a line break with specified size (in pixels) using 0x1b4a. 
        Value expected in range (0x01, 0xff).
        """
        
        size = min(0xff, max(0x01, size))
        strsize = '{0:0{1}X}'.format(size, 2)
        tellPrinter(bytes.fromhex('1b4a' + strsize))
    
    def writeASCII(self, text='\n', wait='True'):
        """
        Write raw ASCII string to the printer.
        By default this printer accepts an ascii string for printing it with raw monospace
        font. Printer has internal buffer (48 characters in Peripage A6+) that will 
        accumulate the received characters. Printer will print out the buffer if meets a '\n' 
        character or buffer overflows.
        This function expects only ASCII characters without control codes (0x00-0x20, 0xFF).
        This function is not recommended to use while printer is in byte stream printing mode
        or while it expects arguments for some of it's opcodes.
        """
        
        if wait:
            return askPrinter(bytes(text, 'ascii'))
        else:
            tellPrinter(bytes(text, 'ascii'))
    
    def printRow(self, rowbytes):
        """
        Send array of pixels represented with rowbytes bytes to the printer.
        This operation invokes printer image / byte stream printing mode and prints out a single 
        row.
        rowbytes expected to be bytes type with size matching the printer extected row size for 
        specified printer model (Refer to getRowBytes() for more information).
        If amount of bytes exceeeds or under the required by this printer type, bytes array will 
        be cut or pad with zeros.
        """
        
        expectedLen = getRowBytes()
        if len(rowbytes) < expectedLen:
            rowbytes = rowbytes.ljust(expectedLen, bytes.fromhex('00'))
        elif len(rowbytes) > expectedLen:
            rowbytes = rowbytes[:expectedLen]
        
        reset()
        
        # Notify printer about incomming $expectedLen bytes row
        if self.printerType == PrinterType.A6:
            tellPrinter(bytes.fromhex('1d76300030000100'))
        else:
            tellPrinter(bytes.fromhex('1d76300048000100'))
        
        tellPrinter(rowbytes)
        
        # We're done here
    
    def printImageBytes(self, imagebytes): # Byte array, should be sliced to match size
        pass
    
    def printImage(self, image): # Pil image should be sliced and processed to match size
        pass
    
    def printRowIterator(self, rowiterator): # Print from iterator
        pass

# Entry for cli utility
if __name__ == '__main__':
    pass