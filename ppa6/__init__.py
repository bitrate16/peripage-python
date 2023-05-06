#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021-2023 bitrate16

__title__ = 'Peripage buetooth printing utility'
__version__ = '1.1'
__author__ = 'bitrate16'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2021-2023 bitrate16'

import time
import math
import qrcode
import typing
import socket
import bluetooth

import PIL.Image
import PIL.ImageOps
from enum import Enum

class PrinterTypeSpecs:
    """
    Specification parameters for each printer model. required for unifying the
    printing interface and easy adding new printe models.

    Defines:
    * `row_bytes` - bytes per row encoding
    * `row_width` - width of single row in pixels
    * `row_characters` - width of row in ASCII-mode characters
    """

    def __init__(self, row_bytes: int, row_width: int, row_characters: int):
        self.row_bytes = row_bytes
        self.row_width = row_width
        self.row_characters = row_characters

class PrinterType(Enum):
    """
    Defines names for supported printer types.
    Currently supported printers are: Peripage A6, A6+, A40
    """

    A6 = PrinterTypeSpecs(
        row_bytes=48,
        row_width=384,
        row_characters=32
    )

    A6p = PrinterTypeSpecs(
        row_bytes=72,
        row_width=576,
        row_characters=48
    )

    A40 = PrinterTypeSpecs(
        row_bytes=216,
        row_width=1728,
        row_characters=144
    )

    @classmethod
    def names(cls) -> typing.List[str]:
        """List available keys from Enum"""
        return [ e.name for e in cls ]

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, spec: PrinterTypeSpecs):
        self.spec = spec

class Printer:
    """
    This class defines the Peripage interface utility.
    It contains methods wrapping requests with special control opcodes.
    By default instance of this class is constructed with timeout set
    to 1s and printer type A6.
    Currently there is no thermal overheat protection opcodes found, so
    use printing carefully and avoid overheating of the printer which
    may result in hardware break.
    Currently there is no stop codes found, so you can not stop printing.

    It is required to perform reset() after connection to the printer.
    """

    @staticmethod
    def filter_ascii(text: str) -> str:
        """
        Remove non-safe-ascii letters from the string so it can be safety used
        in most internal calls.
        """

        return ''.join([ i for i in text if (31 < ord(i) or ord(i) == 10) and ord(i) < 127 ])

    @staticmethod
    def is_safe_ascii(text: str) -> bool:
        """
        Check is string does not contain non-safe-ascii letters (like `>0x7f` or `\\0`).
        """

        for i in text:
            if (31 < ord(i) or ord(i) == 10) and ord(i) < 127:
                return False
        return True

    def __init__(self, mac: str, printer_type: PrinterType, timeout: float=1.0):
        """
        Create instance of peripage connector. `mac` and `printer_type` are
        required for bluetooth connection and printer-specific printing
        parameters.

        In order to make printer operate normally, it is required to call
        `reset()` after connecting.

        Arguments:
        * `mac` - mac address of the printer
        * `printer_type` - printer type enum with specification
        * `timeout` - socket connection timeout in seconds
        """

        self.mac = mac
        self.timeout = timeout
        self.printer_type = printer_type

        # buffer used for continuous printing with line wrapping
        self.print_buffer = ''

    def isConnected(self) -> bool:
        """
        Check if printer is connected (socket alive)
        """

        try:
            self.sock.getpeername()
            return True
        except:
            return False

    def connect(self) -> None:
        """
        Open a new connection to the printer without checking for existing
        connection. In case of malfunction and/or twice connecting to the same
        printer, socket descriptor becomes unoperateable.

        In order to make printer operate normally, it is required to call
        `reset()` after connecting.
        """

        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((self.mac, 1))
        self.sock.settimeout(self.timeout)

    def reconnect(self) -> None:
        """
        Reconnect to the printer with existing connection check.

        In order to make printer operate normally, it is required to call
        `reset()` after connecting.
        """

        if self.isConnected():
            # self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            del self.sock

        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((self.mac, 1))
        self.sock.settimeout(self.timeout)

    def disconnect(self) -> None:
        """
        Disconnect from the printer.
        """

        if self.isConnected():
            # self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            del self.sock

    def setTimeout(self, timeout) -> None:
        """
        Set the bluetooth socket connection recv / send timeout.
        """

        self.timeout = timeout
        if self.isConnected():
            self.sock.settimeout(timeout)

    def tellPrinter(self, byteseq: bytes) -> None:
        """
        Send `bytes` to the printer without response.

        Arguments:
        * `byteseq` - `bytes` data
        """

        self.sock.send(byteseq)

    def askPrinter(self, byteseq: bytes, recv_size: int=1024) -> bytes:
        """
        Send `bytes` to the printer with response.

        Arguments:
        * `recv_size` - max size of received chunk
        * `byteseq` - `bytes` data
        """

        self.sock.send(byteseq)
        return self.sock.recv(recv_size)

    def listenPrinter(self, recv_size: int=1024) -> bytes:
        """
        Receive data from printer.

        Arguments:
        * `recv_size` - max size of received chunk
        """

        return self.sock.recv(recv_size)

    def tellPrinterSeq(self, byteseq: typing.Iterable[bytes]) -> None:
        """
        Send list of `bytes` to the printer without response.

        Arguments:
        * `byteseq` - `list` of `bytes`
        """

        for s in byteseq:
            self.sock.send(s)

    def askPrinterSeq(self, byteseq: typing.Iterable[bytes], recv_size: int=1024) -> bytes:
        """
        Send list of `bytes` to the printer with response.

        Arguments:
        * `recv_size` - max size of received chunk
        * `byteseq` - `list` of `bytes`
        """

        for s in byteseq:
            self.sock.send(s)
        return self.sock.recv(recv_size)

    def getDeviceIP(self) -> bytes:
        """
        Query Unknown Property.

        Request: `10ff20f0`.

        Response: `bytes` with unknown property.

        Example: Peripage A6+ returns `IP-300`.
        """

        return self.askPrinter(b'10ff20f0')

    def getDeviceName(self) -> bytes:
        """
        Query device name.

        Request: `10ff3011`.

        Response: `bytes` with `device_name+two_bytes_of_mac`

        Example: Peripage A6+ returns `PeriPage+DF7A`.
        """

        return self.askPrinter(b'10ff3011')

    def getDeviceSerialNumber(self) -> bytes:
        """
        Query serial number.

        Request: `10ff20f2`.

        Response: `bytes` with serial number

        Example: Peripage A6+ returns `A6491571121`.
        """

        return self.askPrinter(b'10ff20f2')

    def getDeviceFirmware(self) -> bytes:
        """
        Query device firmware version.

        Request: `10ff20f1`.

        Response: `bytes` with firmware version

        Example: Peripage A6+ returns `V2.11_304dpi`.
        """

        return self.askPrinter('10ff20f1')

    def getDeviceBattery(self) -> int:
        """
        Query device battery percentage.

        Request: `10ff50f1`.

        Response: `bytes[2]` with percentage. `bytes[2] = { 0, percentage }`

        Example: Peripage A6+ returns `\\x00@` (equals to `bytes[2] = { 0, 64 }`).
        """
        return int(self.askPrinter(b'10ff50f1')[1])

    def getDeviceHardware(self) -> bytes:
        """
        Query device hardware info.

        Request: `10ff3010`.

        Response: `bytes` with hw info.

        Example: Peripage A6+ returns `BR2141e-s(A02)_B9_20190815_r3460`.
        `BR2141e-s` chip with a pile of ascii letters.
        """

        return self.askPrinter(b'10ff3010')

    def getDeviceMAC(self) -> bytes:
        """
        Query device mac from device itself.

        Request: `10ff3012`.

        Response: `bytes` with mac address.

        Example: Peripage A6+ returns `\\x00\\xF5\\x73\\x25\\xAC\\x9F_\\x00\\xF5\\x73\\x25\\xAC\\x9F_`
        (equals to `00:F5:73:25:AC:9F`).
        """

        return self.askPrinter(b'10ff3012')

    def getDeviceFull(self) -> bytes:
        """
        Query full device info.

        Request: `10ff70f100`.

        Response: `bytes` with fill info.

        Example: Peripage A6+ returns `PeriPage+DF7A|00:F5:73:25:AC:9F|C5:12:81:19:2C:51|V2.11_304dpi|A6491571121|84`
        (`name+mac_slice|device_mac|client_mac|firmware|serial_number|battery_percentage`).

        WARNING:

        This command has a side-effect causing the printed images getting
        corrupted by shifting horisontally and adding a █ character to the
        in-printer ASCII buffer.
        """

        return self.askPrinter(b'10ff70f100')

    def getRowBytes(self) -> int:
        """
        Get row_bytes spec for current printer.

        Images are encoded as 1-pixel-per-1-bit, which means that 1 byte can
        encode 8 black-white pixels in a line. This property defines the bytes
        limit per image row, the overflow is truncated.
        """

        return self.printer_type.spec.row_bytes

    def getRowWidth(self) -> int:
        """
        Get row_width spec for current printer.

        Images are encoded as 1-pixel-per-1-bit, which means that 1 byte can
        encode 8 black-white pixels in a line. This property defines the pixel
        limit per image row, the overflow is truncated.
        """

        return self.printer_type.spec.row_width

    def getRowCharacters(self) -> int:
        """
        Get row_characters spec for current printer.

        Internal ASCII printing mode allows printer to output the raw ASCII
        letters up to `0x7f` and below to `0x10`. This property defunes the
        amount of letters that can fit in a single row. in case of wrapped
        printing, the overflow is wrapped using in-class buffer and synchronized
        with the in-printer buffer.
        """

        return self.printer_type.spec.row_characters

    def getHeightLimit(self) -> int:
        """
        Get the limit of single-image printing chunk.

        Printer protocol allows only 16-bit number as the definition for the
        image printing procedire, that requires used to vertically split the
        image into multiple chunks.
        """

        return 0xffff

    def setDeviceSerialNumber(self, serial_number: str, wait: bool=True) -> None:
        """
        Set device serial number.

        Set a new device serial number explicitly. `serial_number` defines the
        new serial number for the device. This serial number must be
        ascii-encodable string that match the requirements of
        `Printer.is_safe_ascii()` filter in order to work. Serial number string
        is additionally filtered with `Printer.filter_ascii` if you haven't read
        the previous sentence.

        Request: `10ff20f4+ascii_str+00`.

        Arguments:
        * `serial_number` - serial number string that passes the
        `Printer.is_safe_ascii()` check.
        """

        request = b'10ff20f4' + Printer.filter_ascii(serial_number).encode('ascii') + b'00'

        if wait:
            return self.askPrinter(request)
        else:
            self.tellPrinter(request)

    def setPowerTimeout(self, timeout: int, wait: bool=True) -> None:
        """
        Set device poweroff timeout.

        Device standby mode is triggered by any action made with the device. It
        can be either a print task, battery lever query and anything else that
        envolves ask-answer communication. Power timeout defines the internal
        auto poweroff timeout of the device in minutes, up to `0xffff` minutes.

        Request: `10ff12+bytes[2]:big_endian`.

        Arguments:
        * `timeout` - new timeout value between `0` and `0xffff`, minutes
        """

        timeout = max(min(0xfff0, timeout), 0x0001)
        request = b'10ff12' + int.to_bytes(timeout, 2, 'big')

        if wait:
            return self.askPrinter(request)
        else:
            self.tellPrinter(request)

    def setConcentration(self, concentration: int, wait: bool=False) -> None:
        """
        Set printing concentration level.

        Printer supports multiple temperature concentration modes that allow to
        print darker or lighter images with the price of overheating. The more
        concentration - the longer lasting image will be.

        Request: `10ff1000+bytes[1]:big_endian`.

        Arguments:
        * `concentration` - concentration value from range `(0, 1, 2)`
        """

        if concentration <= 0:
            request = b'10ff100000'
        elif concentration == 1:
            request = b'10ff100001'
        elif concentration >= 2:
            request = b'10ff100002'

        if wait:
            return self.askPrinter(request)
        else:
            self.tellPrinter(request)

    def reset(self) -> None:
        """
        Send reset request, required for initial printer initialization after
        connect/reconnect. Without this operation, printer will not print nor
        return any data.

        Request: `10fffe01+000000000000000000000000`.
        """

        self.tellPrinter(b'10fffe01000000000000000000000000')

    def printBreak(self, size: int=0x40) -> None:
        """
        Ask printer to print out a break of fixed size.

        Printer allows user to feed out some paper to wipe away tears of this
        module developer.

        Request: `1b4a+bytes[1]:big_endian`.

        Arguments:
        * `size` - break size in range `(0, 0xff)`
        """

        size = min(0xff, max(0x01, size))
        request = f'1b4a' + int.to_bytes(size, 1, 'big')

        self.tellPrinter(request)

    def writeASCII(self, text: str='\n', wait=False) -> None:
        """
        WARNING: THIS API IS UNSAFE

        Write text into printer without internal safety-checks and filtering. If
        you want to print text with internal checks for non-ascii or
        unsafe-ascii characters, use `Printer.printASCII()`. If you need to use
        this function, check you text with `Printer.is_safe_ascii` or filter
        with `Printer.filter_ascii` and do not leave more than one sequential
        `\\n` character.

        Request: `ascii_str`.

        Arguments:
        * `text` - text to be printed, should be checked by user before print or
        may malfunction and/or damage the printer. String must not contain
        repeating `\\n` characters or printer will freeze.
        """

        request = text.encode('ascii')

        if wait:
            return self.askPrinter(request)
        else:
            self.tellPrinter(request)

    def printlnASCII(self, text: str='', delay: float=0.25) -> None:
        """
        Safe to use printing method that relies on in-class buffer for wrapping
        text. The input is filtered with `Printer.filter_ascii` in order to
        exclude all non-safe-ascii characters and later splitted into multiple
        chunks over `\\n` in order to prevent freeze caused by twice-newline in
        printer buffer. This function is equal to  normal `println` in C and
        semi-equal to `print(text + '\\n')`. This method relies on in-class
        buffer to track printed data and keeping sync with in-printer buffer.

        Request: `impl:Printer.printASCII()`.

        Arguments:
        * `text` - text to be printed, automatically filtered with
        `Printer.filter_ascii()` and splitted into newline-chunked data.
        * `delay` - delay between lines submission, seconds
        """

        self.printASCII(text=text + '\n', delay=delay)

    def printASCII(self, text: str='\n', delay: float=0.25) -> None:
        """
        Safe to use printing method that relies on in-class buffer for wrapping
        text. The input is filtered with `Printer.filter_ascii` in order to
        exclude all non-safe-ascii characters and later splitted into multiple
        chunks over `\\n` in order to prevent freeze caused by twice-newline in
        printer buffer. This function is equal to  normal `print` in C. This
        method relies on in-class buffer to track printed data and keeping sync
        with in-printer buffer.

        In case when the input text contains two sequential `\\n`, they are
        replaced with `Printer.printBreak(30)`.

        Request: `impl:Printer.writeASCII()`.

        Arguments:
        * `text` - text to be printed, automatically filtered with
        `Printer.filter_ascii()` and splitted into newline-chunked data.
        * `delay` - delay between lines submission, seconds
        """

        text = Printer.filter_ascii(text)

        # Check for empty and print out newline
        text = self.print_buffer + text
        self.print_buffer = ''
        if len(text) == 0:
            return

        # Special case: \n only, causes duplicating newlines (white-only string)
        if len(text.strip()) == 0:
            for s in text:
                if s == '\n':
                    self.printBreak(30)
                    time.sleep(delay)
            return

        # Iterlines
        lines = text.split('\n')
        for l in lines:

            # Flush previuos incomplete line
            if len(self.print_buffer) != 0:
                self.tellPrinter(self.print_buffer.encode('ascii'))
                self.tellPrinter(b'\n')
                self.print_buffer = ''
                time.sleep(delay)

            # Flush if white-empty, because it is newline
            if len(l.strip()) == 0:

                # Flush in-printer buffer if not empty
                if len(self.print_buffer) != 0:
                    self.tellPrinter(self.print_buffer.encode('ascii'))
                    self.tellPrinter(b'\n')
                    self.print_buffer = ''
                    time.sleep(delay)

                # Trail
                else:
                    self.printBreak(30)
                    time.sleep(delay)

            # Process normal lines
            else:
                # Wrap line
                parts = [ l[i:i+self.getRowCharacters()] for i in range(0, len(l), self.getRowCharacters()) ]

                for p in parts:

                    # Print full line
                    if len(l) == self.getRowCharacters():
                        self.tellPrinter(p.encode('ascii'))
                        self.tellPrinter(b'\n')
                        time.sleep(delay)

                    # Partial, write to buffer
                    else:
                        self.print_buffer = p

    def flushASCII(self, delay: float=0.25) -> None:
        """
        Force=print out buffer if it is not empty. Not equal to
        `Printer.println()` because does not output empty newline if buffer is
        empty.

        Request: `impl:Printer.printASCII()`.

        Arguments:
        * `delay` - delay between lines submission, seconds
        """

        if len(self.print_buffer) != 0:
            self.tellPrinter(self.print_buffer.encode('ascii'))
            self.tellPrinter(b'\n')
            self.print_buffer = ''
            time.sleep(delay)

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
        if self.printer_type == PrinterType.A6:
            self.tellPrinter(bytes.fromhex('1d76300030000100'))
        elif self.printer_type == PrinterType.A6p:
            self.tellPrinter(bytes.fromhex('1d76300048000100'))
        else:
            self.tellPrinter(bytes.fromhex('1d763000d8000100'))

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
            if self.printer_type == PrinterType.A6:
                self.tellPrinter(bytes.fromhex(f'1d7630003000{heightHex}00'))
            elif self.printer_type == PrinterType.A6p:
                self.tellPrinter(bytes.fromhex(f'1d7630004800{heightHex}00'))
            else:
                self.tellPrinter(bytes.fromhex(f'1d763000d800{heightHex}00'))


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
            if self.printer_type == PrinterType.A6:
                self.tellPrinter(bytes.fromhex(f'1d7630003000{heightHex}00'))
            elif self.printer_type == PrinterType.A6p:
                self.tellPrinter(bytes.fromhex(f'1d7630004800{heightHex}00'))
            else:
                self.tellPrinter(bytes.fromhex(f'1d763000d800{heightHex}00'))


            for j in range(height):
                self.tellPrinter(imagebytes[(i*0xff+j)*expectedLen:(i*0xff+(j+1))*expectedLen])

                time.sleep(delay)

    def printImage(self, img, delay=0.01, resample=PIL.Image.NEAREST):
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
        img = PIL.ImageOps.invert(img)
        img = img.resize((self.getRowWidth(), int(self.getRowWidth() / img.size[0] * img.size[1])), resample)
        img = img.convert('1')

        imgbytes = img.tobytes()
        self.printImageBytes(imgbytes)

    def printQR(self, text, delay=0.01, resample=PIL.Image.NEAREST):
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
        if self.printer_type == PrinterType.A6:
            self.tellPrinter(bytes.fromhex(f'1d7630003000{rowcountstr}'))
        elif self.printer_type == PrinterType.A6p:
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
