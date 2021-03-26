#!/usr/bin/env python3

# MIT License
# 
# Copyright (c) 2021 bitrate16

__title__ = 'Peripage A6/A6+ buetooth printing utility'
__version__ = '0.3'
__author__ = 'bitrate16'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2021 bitrate16'

import time
import math
import qrcode
import socket
import bluetooth

from PIL import Image, ImageOps
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
    Currently there is no thermal overheat protection opcodes found, so
    use printing carefully and avoid overheating of the printer which 
    may result in hardware break.
    Currently there is no stop codes found, so you can not stop printing.
        
    It is required to perform reset() after connection to the printer.
    """
    
    def __init__(self, mac, printertype=PrinterType.A6, timeout=1.0):
        """
        Creates an instance of this wrapper class and stores passed mac 
        address for future connection (reconnection) to the printer.
        By default printer type is set to A6.
        By default timeout for connection / request is set to 1sec and 
        can be changed later with setTimeout(timeout).
        
        It is required to perform reset() after connection to the printer.
        
        TODO: Autimatically recognize printer type and avoid using 
        explicit definition or leave it for explicit compability bypassing.
        
        :param mac: MAC address of the printer
        :type mac: str
        :param printerType: type of the printer
        :type printerType: PrinterType
        :param timeout: timeot for connection
        :type timeout: float
        """
        
        self.mac = mac
        self.timeout = timeout
        self.printerType = printertype
        
        # This buffer is used for continuous printing
        self.printBuffer = ''
    
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
        
        It is required to perform reset() after connection to the printer.
        """
        
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.mac, 1))
    
    def reconnect(self):
        """
        Reconnects to the printer. If connection already exists, socket is 
        being closed first.
        
        It is required to perform reset() after connection to the printer.
        
        TODO: Figure out how to reconnect this bluetooth socket
        """
        
        if self.isConnected():
            # self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            del self.sock
        
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.mac, 1))
    
    def disconnect(self):
        """
        Disconnects from the printer.
        """
        
        if self.isConnected():
            # self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            del self.sock
    
    def setTimeout(self, timeout):
        """
        Used to set a connection / send / recv timeout for bluetooth socket.
        
        :param timeout: new timeout value
        :type timeout: float
        """

        self.timeout = timeout
        self.sock.settimeout(timeout)
    
    
    def tellPrinter(self, byteseq):
        """
        Send byte sequence to the printer and return, no response is expected
        
        :param byteseq: bytes of information to send
        :type byteseq: bytes
        """
        
        self.sock.send(byteseq)

    def askPrinter(self, byteseq, recv_size=1024):
        """
        Send byte sequence to the printer and receive recv_size bytes as response
        
        :param byteseq: bytes of information to send
        :type byteseq: bytes
        :param recv_size: receiver buffer size
        :type recv_size: int
        """
        
        self.sock.send(byteseq)
        return self.sock.recv(recv_size)

    def listenPrinter(self, recv_size=1024):
        """
        Receive recv_size bytes from the printer
        
        :param recv_size: receiver buffer size
        :type recv_size: int
        """
        
        return self.sock.recv(recv_size)

    def tellPrinterSeq(self, byteseq):
        """
        Send byte sequence list to the printer and return, no response is expected
        
        :param byteseq: array or bytes[]
        :type byteseq: list
        """
        
        for s in byteseq:
            self.sock.send(s)

    def askPrinterSeq(self, byteseq, recv_size=1024):
        """
        Send byte sequence list to the printer and receive recv_size bytes as response
        
        :param byteseq: array or bytes[]
        :type byteseq: list
        :param recv_size: receiver buffer size
        :type recv_size: int
        """
        
        for s in byteseq:
            self.sock.send(s)
        return self.sock.recv(recv_size)


    def getDeviceIP(self):
        """
        Returns Unknown Property as response of 0x10ff20f0.
        For example, Peripage A6+ returns 'IP-300'
        """
        
        return self.askPrinter(bytes.fromhex('10ff20f0'))

    def getDeviceName(self):
        """
        Returns Device Name as response of 0x10ff3011.
        For example, Peripage A6+ returns 'PeriPage+DF7A'
        """
        
        return self.askPrinter(bytes.fromhex('10ff3011'))

    def getDeviceSerialNumber(self):
        """
        Returns Serial Number as response of 0x10ff20f2.
        For example, Peripage A6+ returns 'A6491571121'
        """
        
        return self.askPrinter(bytes.fromhex('10ff20f2'))

    def getDeviceFirmware(self):
        """
        Returns Firmware Version as response of 0x10ff20f1.
        For example, Peripage A6+ returns 'V2.11_304dpi'
        """
        
        return self.askPrinter(bytes.fromhex('10ff20f1'))

    def getDeviceBattery(self):
        """
        Returns battery value as response of 0x10ff50f1.
        For example, Peripage A6+ returns '\x00@' (sample retult).
        Request returns result of type byte[2] where result[1] is charge 
        lever, result[0] is 0.
        """
        return int(self.askPrinter(bytes.fromhex('10ff50f1'))[1])

    def getDeviceHardware(self):
        """
        Returns Hardware Info as response of 0x10ff3010.
        For example, Peripage A6+ returns 'BR2141e-s(A02)_B9_20190815_r3460',
        that means that it has a BR2141e-s chip inside and a small amount of 
        additional ascii characters.
        """
        
        return self.askPrinter(bytes.fromhex('10ff3010'))

    def getDeviceMAC(self):
        """
        Returns Device's MAC address as response of 0x10ff3012.
        For example, Peripage A6+ returns 
        '\x00\xF5\x73\x25\xAC\x9F_\x00\xF5\x73\x25\xAC\x9F_', which is equal to
        00:F5:73:25:AC:9F
        """
        
        return self.askPrinter(bytes.fromhex('10ff3012'))

    def getDeviceFull(self):
        """
        Returns Full device information as response of 0x10ff70f1.
        For example, Peripage A6+ returns 
        'PeriPage+DF7A|00:F5:73:25:AC:9F|C5:12:81:19:2C:51|V2.11_304dpi|A6491571121|84', 
        which means that it's name is 'PeriPage+DF7A', mac is 00:F5:73:25:AC:9F, 
        connected to mac C5:12:81:19:2C:51, F/W V2.11_304dpi, S/N A6491571121, battery
        level 84%.
        Use with care. This command has sub effect causing the printed images to corrupt 
        shifting horisontally and adding a █ character to ASCII buffer.
        """
        
        return self.askPrinter(bytes.fromhex('10ff70f100'))
    
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
    
    def getRowCharacters(self):
        """
        Returns amount of characters that may fit in a single row.
        By default A6+ can fit up to 48 characters, A6 can fit up to 32 characters.
        """
        
        if self.printerType == PrinterType.A6:
            # TODO: Measure amount of characters that can fit in the line
            return 32
        elif self.printerType == PrinterType.A6p:
            return 48
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
        
        :param snstr: new serial number
        :type snstr: str
        :param wait: wait for response
        :type wait: bool
        """
        
        self.tellPrinter(bytes.fromhex('10ff20f4'))
        if wait:
            return self.askPrinter(bytes(snstr + '\0', 'ascii'))
        else:
            self.tellPrinter(bytes(snstr + '\0', 'ascii'))

    def setPowerTimeout(self, timeout, wait=True):
        """
        Sets the device timeout (in minutes) to the value (bound between 0x0001 and 0xfff0) 
        using 0x10ff12.
        Call to 0x10ff12 returns 'OK' as the result of timeout change.
        
        :param timeout: power timeout in range (0x0001, 0xfff0)
        :type timeout: int
        :param wait: wait for response
        :type wait: bool
        """
        
        timeout = max(min(0xfff0, timeout), 0x0001)
        strtimeout = '{0:0{1}X}'.format(timeout, 4)
        if wait:
            return self.askPrinter(bytes.fromhex('10ff12' + strtimeout))
        else:
            self.tellPrinter(bytes.fromhex('10ff12' + strtimeout))
    
    def setConcentration(self, cons, wait=False):
        """
        Sets the printing concentration using 0x10ff1000 opcode.
        Currently allowed values are 0, 1, 2 which represents light, medium, hard 
        (heating intensivity). Other values are not tested yet.
        
        :param cons: concentration (0, 1, 2)
        :type cons: int
        :param wait: wait for response
        :type wait: bool
        """
        
        opcode = ''
        
        if cons <= 0:
            opcode = '10ff100000'
        elif cons == 1:
            opcode = '10ff100001'
        elif cons >= 2:
            opcode = '10ff100002'
        
        if wait:
            return self.askPrinter(bytes.fromhex(opcode))
        else:
            self.tellPrinter(bytes.fromhex(opcode))
    
    
    def reset(self):
        """
        Performs reset operation (The initial purpose of it is stoll unknown) 
        required before printing stream of bytes in a binary image.
        Opcode for this operation is 0x10fffe01 followed by 0x000000000000000000000000.
        This operation has to be performed before any other printing operation and after 
        connect to printer.
        """
        
        self.tellPrinter(bytes.fromhex('10fffe01000000000000000000000000'))
    
    def printBreak(self, size=0x40):
        """
        Asks printer to print a line break with specified size (in pixels) using 0x1b4a. 
        Value expected in range (0x01, 0xff).
        
        :param text: size of break in range (0x1, 0xff)
        :type text: int
        """
        
        size = min(0xff, max(0x01, size))
        strsize = '{0:0{1}X}'.format(size, 2)
        self.tellPrinter(bytes.fromhex('1b4a' + strsize))
    
    def writeASCII(self, text='\n', wait=False):
        """
        Deprecated.
        Write raw ASCII string to the printer.
        By default this printer accepts an ascii string for printing it with raw monospace
        font. Printer has internal buffer (getRowCharacters()) that will 
        accumulate the received characters. Printer will print out the buffer if meets a '\n' 
        character or buffer overflows.
        This function expects only ASCII characters without control codes (0x00-0x20, 0xFF).
        This function is not recommended to use while printer is in byte stream printing mode
        or while it expects arguments for some of it's opcodes.
        If string contains sequently repeating '\n' characters, the printer may freeze. So 
        it's recommended to use printASCII() instead.
        
        :param text: string containing ASCII characters
        :type text: str
        :param wait: wait for response
        :type wait: bool
        """
        
        if wait:
            return self.askPrinter(bytes(text, 'ascii'))
        else:
            self.tellPrinter(bytes(text, 'ascii'))
    
    def printlnASCII(self, text='\n', delay=0.25):
        """
        Write raw ASCII string to the printer.
        By default this printer accepts an ascii string for printing it with raw monospace
        font. Printer has internal buffer (getRowCharacters()) that will 
        accumulate the received characters. Printer will print out the buffer if meets a '\n' 
        character or buffer overflows.
        This function expects only ASCII characters without control codes (0x00-0x20, 0xFF).
        This function is not recommended to use while printer is in byte stream printing mode
        or while it expects arguments for some of it's opcodes.
        If string contains sequently repeating '\n' characters, they will be replaced with 
        printBreak(30) which matches the length of the '\n\n'. This function automatically 
        slices string into pieces of size getRowCharacters() and waits till new piece being 
        printed.
        This function acts as println. This function will print out the data stored in the 
        buffer of printASCII().
        
        :param text: string containing ASCII characters
        :type text: str
        :param delay: delay between sending each line
        :type delay: float
        """
        
        # Remove non-ASCII & control (except \n)
        text = ''.join([i for i in text if (31 < ord(i) or ord(i) == 10) and ord(i) < 127])
        
        ## Remove last '\n' to avoid it's duplication
        #if len(text) > 0 and text[-1] == '\n':
        #    text = text[:-1]
        #
        # Check for empty and print out newline
        text = self.printBuffer + text
        if len(text) == 0:
            self.printBreak(30)
            time.sleep(delay)
            return
        
        lines = text.split('\n')
        self.printBuffer = ''
        
        for l in lines:
            # Replace every empty line with break matching newline height
            if len(l) == 0:
                self.printBreak(30)
                time.sleep(delay)
            else:
                # Split to lines
                parts = [l[i:i+self.getRowCharacters()] for i in range(0, len(l), self.getRowCharacters())]
                
                for i, p in enumerate(parts):
                    self.tellPrinter(bytes(p, 'ascii'))
                    if i != 0:
                        time.sleep(delay)
                
                # Push last line from the buffer
                self.tellPrinter(bytes('\n', 'ascii'))
                time.sleep(delay)
    
    def printASCII(self, text='\n', delay=0.25):
        """
        Write raw ASCII string to the printer.
        By default this printer accepts an ascii string for printing it with raw monospace
        font. Printer has internal buffer (getRowCharacters()) that will 
        accumulate the received characters. Printer will print out the buffer if meets a '\n' 
        character or buffer overflows.
        This function expects only ASCII characters without control codes (0x00-0x20, 0xFF).
        This function is not recommended to use while printer is in byte stream printing mode
        or while it expects arguments for some of it's opcodes.
        If string contains sequently repeating '\n' characters, they will be replaced with 
        printBreak(30) which matches the length of the '\n\n'. This function automatically 
        slices string into pieces of size getRowCharacters() and waits till new piece being 
        printed.
        This function uses in class buffer to store tail of the text if text didn't end with 
        '\n'.
        
        :param text: string containing ASCII characters
        :type text: str
        :param delay: delay between sending each line
        :type delay: float
        """
        
        # Remove non-ASCII & control (except \n)
        text = ''.join([i for i in text if (31 < ord(i) or ord(i) == 10) and ord(i) < 127])
        
        # Check for empty and print out newline
        text = self.printBuffer + text
        self.printBuffer = ''
        if len(text) == 0:
            return
        
        endLineBreak = text[-1] == '\n'
        
        # Remove last '\n' to avoid it's duplication
        if len(text) > 0 and text[-1] == '\n':
            if len(text) == 1:
                self.printBreak(30)
                time.sleep(delay)
                return
            
            text = text[:-1]
        
        lines = text.split('\n')
        
        for i, l in enumerate(lines):
            # Replace every empty line with break matching newline height
            if len(l) == 0:
                self.printBreak(30)
                time.sleep(delay)
            else:
                # Split to lines
                parts = [l[i:i+self.getRowCharacters()] for i in range(0, len(l), self.getRowCharacters())]
                
                for j, p in enumerate(parts):
                    # If this is the last part of the text and it ends with '\n', push it
                    if j == len(parts)-1:
                        if i == len(lines)-1:
                            if endLineBreak:
                                self.tellPrinter(bytes(p, 'ascii'))
                                time.sleep(delay)
                                self.tellPrinter(bytes('\n', 'ascii'))
                                time.sleep(delay)
                            else:
                                self.printBuffer = p
                                
                                # Push out the string that is a full row
                                if len(p) == self.getRowCharacters():
                                    self.tellPrinter(bytes(p, 'ascii'))
                                    time.sleep(delay)
                                    self.tellPrinter(bytes('\n', 'ascii'))
                                    time.sleep(delay)
                                    self.printBuffer = ''
                        else:
                            self.tellPrinter(bytes(p, 'ascii'))
                            time.sleep(delay)
                            self.tellPrinter(bytes('\n', 'ascii'))
                            time.sleep(delay)
                    else:
                        self.tellPrinter(bytes(p, 'ascii'))
                        if j != 0:
                            time.sleep(delay)
    
    def flushASCII(self, delay=0.25):
        """
        Prints out the buffer used in printASCII() followed by newline.
        
        :param delay: delay between sending each line
        :type delay: float
        """
        
        if len(self.printBuffer) > 0:
            self.tellPrinter(bytes(self.printBuffer, 'ascii'))
            time.sleep(delay)
            self.tellPrinter(bytes('\n', 'ascii'))
            time.sleep(delay)
            self.printBuffer = ''
    
    def printRow(self, rowbytes):
        """
        Send array of pixels represented with rowbytes bytes to the printer.
        This operation invokes printer image / byte stream printing mode and prints out a single 
        row.
        rowbytes expected to be bytes type with size matching the printer extected row size for 
        specified printer model (Refer to getRowBytes() for more information).
        If amount of bytes exceeeds or under the required by this printer type, bytes array will 
        be cut or pad with zeros.
        
        :param rowbytes: bytes array of size getRowBytes() representing a single row
        :type rowbytes: bytes
        """
        
        expectedLen = self.getRowBytes()
        if len(rowbytes) < expectedLen:
            rowbytes = rowbytes.ljust(expectedLen, bytes.fromhex('00'))
        elif len(rowbytes) > expectedLen:
            rowbytes = rowbytes[:expectedLen]
        
        self.reset()
        
        # Notify printer about incomming $expectedLen bytes row
        if self.printerType == PrinterType.A6:
            self.tellPrinter(bytes.fromhex('1d76300030000100'))
        else:
            self.tellPrinter(bytes.fromhex('1d76300048000100'))
        
        self.tellPrinter(rowbytes)
        
        # We're done here
    
    def printImageRowBytesList(self, imagebytes, delay=0.01): 
        """
        Performs printing of the Image bytes. Image width expected to match getRowBytes(), in other 
        case it will be cut or pad with bytes.
        Input image is being split into multiple pieces if height exceeds 0xff pixels. This should 
        be done because of the limitation in 0xffff pixels in height for single page, but i limit 
        by 0xff.
        imagebytes defines the list with rows. Each row is defined by bytes.
        For example: [0xff000000, 0x00ff0000, 0x0000ff00, 0x000000ff]
        
        :param imagebytes: array of bytes containing rows of the image
        :type imagebytes: list
        :param delay: delay between sending each row of the image
        :type delay: float
        """
        
        imgHeight = len(imagebytes)
        expectedLen = self.getRowBytes()
        nPieces = math.ceil(imgHeight / 0xff)
        restPixels = imgHeight % 0xff
        
        for i in range(nPieces):
            # Size of each print is 0xff, but last print has size restPixels
            height = 0xff if i < nPieces-1 else restPixels
            heightHex = 'ff' if i < nPieces-1 else '{0:0{1}X}'.format(restPixels, 2)
            
            self.reset()
        
            # Notify printer about incomming $expectedLen bytes row
            if self.printerType == PrinterType.A6:
                self.tellPrinter(bytes.fromhex(f'1d7630003000{heightHex}00'))
            else:
                self.tellPrinter(bytes.fromhex(f'1d7630004800{heightHex}00'))
            
            for j in range(height):
                rowbytes = imagebytes[i*0xff+j]
            
                if len(rowbytes) < expectedLen:
                    rowbytes = rowbytes.ljust(expectedLen, bytes.fromhex('00'))
                elif len(rowbytes) > expectedLen:
                    rowbytes = rowbytes[:expectedLen]
                
                self.tellPrinter(rowbytes)
                
                time.sleep(delay)
    
    def printImageBytes(self, imagebytes, delay=0.01): 
        """
        Performs printing of the Image bytes. Image width expected to match getRowBytes(), in other 
        case it will shift while printing and the last for not matching length of getRowBytes() 
        will be cut.
        Input image is being split into multiple pieces if height exceeds 0xff pixels. This should 
        be done because of the limitation in 0xffff pixels in height for single page, but i limit 
        by 0xff.
        imagebytes defines the entime image despite to printImageBytesList argument
        For example: [0xff000000, 0x00ff0000, 0x0000ff00, 0x000000ff] will be defined as
        0xff00000000ff00000000ff00000000ff.
        
        :param imagebytes: bytes containing rows of the image
        :type imagebytes: bytes
        :param delay: delay between sending each row of the image
        :type delay: float
        """
        
        expectedLen = self.getRowBytes()
        imgHeight = math.floor(len(imagebytes) / expectedLen)
        nPieces = math.ceil(imgHeight / 0xff)
        restPixels = imgHeight % 0xff
        
        for i in range(nPieces):            
            self.reset()
            
            # Size of each print is 0xff, because last part is cut off
            height = 0xff if i < nPieces-1 else restPixels
            heightHex = 'ff' if i < nPieces-1 else '{0:0{1}X}'.format(restPixels, 2)
            
            # Notify printer about incomming $expectedLen bytes row
            if self.printerType == PrinterType.A6:
                self.tellPrinter(bytes.fromhex(f'1d7630003000{heightHex}00'))
            else:
                self.tellPrinter(bytes.fromhex(f'1d7630004800{heightHex}00'))
            
            for j in range(height):
                self.tellPrinter(imagebytes[(i*0xff+j)*expectedLen:(i*0xff+(j+1))*expectedLen])
                
                time.sleep(delay)
    
    def printImage(self, img, delay=0.01, resample=Image.NEAREST): 
        """
        Performs printing of PIL image. Image is being rescaled to match width of getRowPixels().
        Result image is converted to '1' binary mode. If image width exceeds limit of 0xff pixels 
        in heigth, it will be split into multiple parts.
        
        :param img: image to print
        :type img: Image
        :param delay: delay between sending each row of the image
        :type delay: float
        :param resample: image resampling mode (Image.NEAREST, Image.BILINEAR, Image.BICUBIC, Image.ANTIALIAS)
        """
        
        img = img.convert('L')
        img = ImageOps.invert(img)
        img = img.resize((self.getRowWidth(), int(self.getRowWidth() / img.size[0] * img.size[1])), resample)
        img = img.convert('1')
        
        imgbytes = img.tobytes()
        self.printImageBytes(imgbytes)
    
    def printQR(self, text, delay=0.01, resample=Image.NEAREST):
        """
        Generates QR code from specified string and prints it out.
        
        :param text: Text for qr code
        :tapy text: str
        :param delay: delay between sending each row of the image
        :type delay: float
        :param resample: image resampling mode (Image.NEAREST, Image.BILINEAR, Image.BICUBIC, Image.ANTIALIAS)
        """
        
        self.printImage(qrcode.make(text, border=0), delay, resample)
    
    def printRowBytesIterator(self, rowiterator, delay=0.25):
        """
        Allows printing image using iterator / generator that should return bytes
        of row as result. If amount of returned bytes do not match getRowBytes(),
        they will be pad or cut.
        
        :param rowiterator: iterator or generator returning bytes describing rows of the image.
        :param delay: delay between sending each row
        :type delay: float
        """
        
        for r in rowiterator:
            self.printRow(r)
            time.sleep(delay)
    
    
    def printRowIterator(self, rowiterator, delay=0.25):
        """
        Allows printing image using iterator / generator that should return image size of 
        (getRowWidth(), 1) as result. Returned image is geing resampled and printed as a row.
        This function does not perform check if this image is really (getRowWidth(), 1) pixels
        size and just passes it to the printImage() repeatly
        
        :param rowiterator: iterator or generator returning image for each row.
        :param delay: delay between sending each row
        :type delay: float
        """
        
        for r in rowiterator:
            self.printImage(r)
            time.sleep(delay)
    
    def printRowBytesIteratorOfSize(self, rowiterator, rowcount, delay=0.01):
        """
        Allows printing image using iterator / generator that should return bytes
        of row as result. If amount of returned bytes do not match getRowBytes(),
        they will be pad or cut.
        Additional parameter for this function is amount of rows that should be 
        reserved for printing. This is usefull for printing long procedural 
        generated pages when printing using single row commit is too slow.
        
        :param rowiterator: iterator or generator returning bytes describing rows of the image.
        :param rowcount: amount of rows to reserve for printing in range (0x1, 0xffff)
        :type rowcount: int
        :param delay: delay between sending each row
        :type delay: float
        """
        
        rowcount = min(0xffff, max(0x1, rowcount))
        rowcountstr = '{0:0{1}X}'.format(rowcount, 4)
        rowcountstr = rowcountstr[2:4] + rowcountstr[0:2]
        
        self.reset()

        # Notify printer about incomming bytes
        if self.printerType == PrinterType.A6:
            self.tellPrinter(bytes.fromhex(f'1d7630003000{rowcountstr}'))
        elif self.printerType == PrinterType.A6p:
            self.tellPrinter(bytes.fromhex(f'1d7630004800{rowcountstr}'))
        else:
            raise ValueError('Unsupported printer type')
        
        expectedLen = self.getRowBytes()
        
        for i, r in enumerate(rowiterator):
            rowbytes = r
            
            if len(rowbytes) < expectedLen:
                rowbytes = rowbytes.ljust(expectedLen, bytes.fromhex('00'))
            elif len(rowbytes) > expectedLen:
                rowbytes = rowbytes[:expectedLen]
            
            self.tellPrinter(rowbytes)
            
            time.sleep(delay)
            
            if i == rowcount - 1:
                break
