#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021 bitrate16

def main():
    import argparse
    import sys
    import peripage
    import PIL.Image

    parser = argparse.ArgumentParser(description='Print on a Peripage printer via bluetooth')
    parser.add_argument(
        '-m', '--mac',
        help='Bluetooth MAC address of the printer',
        required=True,
        type=str
    )
    parser.add_argument(
        '-c', '--concentration',
        help='Concentration value for printing (temperature)',
        choices=[0, 1, 2],
        metavar='[0-2]',
        type=int,
        default=0
    )
    parser.add_argument(
        '-b', '--break',
        dest='break_size',
        help='Size of the break inserted after printed image or text',
        choices=range(256),
        metavar='[0-255]',
        type=int,
        default=0
    )
    parser.add_argument(
        '-p', '--printer',
        help='Printer model selection',
        choices=peripage.PrinterType.names(),
        type=str,
        required=True
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-t', '--text',
        help='ASCII text to print. Text must be ASCII-safe and will be filtered for invalid characters',
        type=str
    )
    group.add_argument(
        '-s', '--stream',
        help='Print text received from STDIN, line by line. Text must be ASCII-safe and will be filtered for invalid characters',
        action='store_true'
    )
    group.add_argument(
        '-i', '--image',
        help='Path to the image for printing',
        type=str
    )
    group.add_argument(
        '-q', '--qr',
        help='String to convert into a QR code for printing',
        type=str
    )
    group.add_argument(
        '-e', '--introduce',
        help='Ask the printer to introduce itself',
        action='store_true'
    )

    args = parser.parse_args()

    # Open connection
    printer = peripage.Printer(args.mac, peripage.PrinterType[args.printer])
    printer.connect()
    printer.reset()

    # Act based on args
    if 'introduce' in args and args.introduce:

        # print('Hello, my name is Harold..')
        print(printer.getDeviceFull().decode('ascii'))
        printer.disconnect()
        sys.exit(0)

    elif 'stream' in args and args.stream:

        printer.setConcentration(args.concentration)

        while True:
            try:
                line = input().rstrip()

                printer.printlnASCII(line)

            except EOFError:
                # Input closed ^d^d
                break

        if args.break_size > 0:
            printer.printBreak(args.break_size)

        printer.disconnect()

        sys.exit(0)

    elif 'text' in args and args.text is not None:

        printer.setConcentration(args.concentration)

        text = args.text.rstrip()

        if len(text) > 0:
            printer.printASCII(text)
            printer.flushASCII()

        if args.break_size > 0:
            printer.printBreak(args.break_size)

        printer.disconnect()

        sys.exit(0)

    elif 'image' in args and args.image is not None:

        printer.setConcentration(args.concentration)

        try:
            img = PIL.Image.open(args.image)
        except:
            print(f'Failed to open image { args.image }')

        printer.printImage(img)

        if args.break_size > 0:
            printer.printBreak(args.break_size)

        printer.disconnect()

        sys.exit(0)

    elif 'qr' in args and args.qr is not None:

        printer.setConcentration(args.concentration)

        printer.printQR(args.qr)

        if args.break_size > 0:
            printer.printBreak(args.break_size)

        printer.disconnect()

        sys.exit(0)

    else:

        print('How did you get there?')

if __name__ == '__main__':
    main()
