#!/usr/bin/env python3

# MIT License
# 
# Copyright (c) 2021 bitrate16

def main():
    import argparse
    import sys
    from ppa6 import Printer, PrinterType
    from PIL import Image

    parser = argparse.ArgumentParser(description='Print on a Peripage A6 / A6+ via bluetooth')
    parser.add_argument('-m', '--mac', help='Bluetooth MAC address of the printer', required=True, type=str)
    parser.add_argument('-c', '--concentration', help='Concentration value for printing (0, 1, 2)', required=False, choices=[0, 1, 2], metavar='[0-2]', type=int, default=0)
    parser.add_argument('-b', '--break', dest='breaksize', help='Size of the break that should be inserted after the print (max 255)', required=False, choices=range(256), metavar='[0-255]', type=int, default=0)
    parser.add_argument('-p', '--printer', help='Printer model name (A6 or A6+/A6p (both allowed))', required=False, choices=['A6', 'A6p', 'A6+'], type=str, default='A6')
    parser.add_argument('-n', '--newline', help='Force printer to add newline at the end of the printed text and flush the buffer', required=False, action='store_true')

    # Selection of the required action:
    # 1. Print text
    # 2. Print stream from stdin
    # 3. Print image from file
    # 4. Requist printer information
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--text', help='ASCII text that should be printed. Add a line break at the end of the string to avoid it being cut. String can be empty, so just page break will be printed', type=str)
    group.add_argument('-s', '--stream', help='Reads an input from stdin and prints as ASCII text', action='store_true')
    group.add_argument('-i', '--image', help='Path to the image that should be printed', type=str)
    group.add_argument('-q', '--qr', help='String for QR code print', type=str)
    group.add_argument('-e', '--introduce', help='Ask the printer to introduce himself', action='store_true')

    args = parser.parse_args()

    # Open connection

    printer = Printer(args.mac, PrinterType.A6 if args.printer == 'A6' else PrinterType.A6p)

    #try:
    printer.connect()
    #except:
    #    print('Failed to open connection')
    #    sys.exit(0)

    if 'introduce' in args and args.introduce:
        
        # print('Hello, my name is Harold..')
        print(printer.getDeviceFull().decode('ascii'))
        printer.disconnect()
        sys.exit(0)
        
    elif 'stream' in args and args.stream:
        
        if 'concentration' in args:
            printer.setConcentration(args.concentration)
        
        printer.reset()
        
        while True:
            try:
                line = input()
                
                printer.printlnASCII(line)
                
            except EOFError:
                # Input closed ^d^d
                break
        
        if 'breaksize' in args and args.breaksize > 0:
            printer.printBreak(args.breaksize)
        
        sys.exit(0)
        
    elif 'text' in args and args.text is not None:
        
        if 'concentration' in args:
            printer.setConcentration(args.concentration)
        
        printer.reset()
        
        line = args.text
        if args.newline:
            line += '\n'
        
        if len(line) > 0:
            printer.printASCII(line)
        
        if 'breaksize' in args and args.breaksize > 0:
            printer.printBreak(args.breaksize)
        
        sys.exit(0)
        
    elif 'image' in args and args.image is not None:
        
        if 'concentration' in args:
            printer.setConcentration(args.concentration)
        
        printer.reset()
        img = None
        
        try:
            img = Image.open(args.image)
        except:
            print(f'Failed to open image {args.image}')
        
        printer.printImage(img, resample=Image.ANTIALIAS)
        
        if 'breaksize' in args and args.breaksize > 0:
            printer.printBreak(args.breaksize)
        
        sys.exit(0)
        
    elif 'qr' in args and args.qr is not None:
        
        if 'concentration' in args:
            printer.setConcentration(args.concentration)
        
        printer.reset()
        
        printer.printQR(args.qr, resample=Image.ANTIALIAS)
        
        if 'breaksize' in args and args.breaksize > 0:
            printer.printBreak(args.breaksize)
        
        sys.exit(0)

    else:
        
        print('How did you get there?')

if __name__ == '__main__':
    main()
