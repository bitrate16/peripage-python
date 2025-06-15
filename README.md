# peripage-python
### Python module for printing on Peripage printers

**This project is a continued development of the [original project](https://github.com/eliasweingaertner/peripage-A6-bluetooth) made by [Elias Weingärtner](https://github.com/eliasweingaertner). This module combined all results of reverse engineering of the Peripage A6/A6+ protocol in a python utility providing interface and CLI tool for printing on this thermal printer.**

## [The original introduction](https://github.com/eliasweingaertner/peripage-A6-bluetooth#introduction)

The Peripage A6 F622 is an inexpensive portable thermal printer. It provides both Bluetooth and USB connectivity. Unlike most other thermo printers it **does not** seem to support ESC/POS or any other standardized printer control language.

So far, the Peripage A6 F622 can be only controlled using a proprietary app (iOS / Anndroid). There is also a driver for Windows with many limitations, most notably the need of defining a page size before printing; this is a huge limitation, as the Peripage prints on continuous form paper.

The script provided here was built based on an analysis of captured Bluetooth traffic between the printer and an Android device. The Peripage A6 uses the serial profile (BTSPP) and RFCOMM.

Essentially, the script takes an input images, scales it to the printers native X resolution of 384 pixels, and then sends it to the printer.

## Deprecation Warning

**The latest version ot `ppa6-python` module is deprecated due the major update with new models support and better module naming**

## Denial of responsibility

The author and people associated with him are not responsible for the inoperability, breakdown, disruption and failure of software and hardware, as well as loss and damage to physical and software property as a result of the use of this software and related projects. Everything you do is at your own risk and responsibility.

## Features

* Printing text of any length encoded in ASCII
* Printing Images using PIL library
* Printing Images row-by row using binary row representation
* Printing page breaks using paper feed
* Printing using generator/iterator that return bytes for each row, chunks of bytes for each row, images
* Requesting printer details (Serial Number, Name, Battery Level, Hardware Info and an option the meaning of which i don't know)
* Configuring print concentration (temperature)
* Changing printer serial number
* Configuring printer poweroff timeout
* Supported printers:
  * Peripage A6
  * Peripage A6+
  * Peripage A40
  * Peripage A40+

## Prerequisites

* Peripage A6/A6+/A40/A40+/e.t.c printer
* Python 3

## Installation

**Install from git clone**

```
pip install -r requirements.txt
pip install . --user
```

**Install from pypi using pip**

```
pip install peripage
```

## Dependencies

* `PyBluez>=0.30`
* `Pillow>=8.1.2`
* `argparse>=1.1`

Install dependencies with
`pip install -r requirements.txt`

## Identify printer Bluetooth MAC address

**On linux:**

```
user@name:~$ hcitool scan
Scanning ..
00:15:83:15:bc:5f    PeriPage+BC5F
```

**On windows:**

You may use [BluetoothCL](https://www.nirsoft.net/utils/bluetoothcl.html)

```
PS E:\E\E> .\BluetoothCL.exe
BluetoothCL v1.07
Copyright (c) 2009 - 2014 Nir Sofer
Web Site: http://www.nirsoft.net

syntax:
BluetoothCL -timeout [seconds]

-timeout is optional parameter. The default value is 15 seconds.


Scanning bluetooth devices... please wait.

00:15:83:15:bc:5f    Imaging                         PeriPage+BC5F
```

## Troubleshooting

> Windows installation requires installing PyBluez from master branch as pypi module is not updated

```
pip install git+https://github.com/pybluez/pybluez@master#egg=pybluez --user
```

> Raspberry PI installation requires additional libraries

```
sudo apt install libbluetooth-dev libopenjp2-7 libtiff5
```

> Some cases may require restarting bluetooth adapter

```
sudo systemctl restart bluetooth
sudo hciconfig hci0 reset
```

## CLI usage

**On linux**

Install module and run
`peripage <args>`

**On windows**

Install module and run
`python -m peripage <args>`

### Options

```
$ python -m peripage -h
usage: __main__.py [-h] -m MAC [-c [0-2]] [-b [0-255]] -p {A6,A6p,A40,A40p} (-t TEXT | -s | -i IMAGE | -q QR | -e)

Print on a Peripage printer via bluetooth

optional arguments:
  -h, --help            show this help message and exit
  -m MAC, --mac MAC     Bluetooth MAC address of the printer
  -c [0-2], --concentration [0-2]
                        Concentration value for printing (temperature)
  -b [0-255], --break [0-255]
                        Size of the break inserted after printed image or text
  -p {A6,A6p,A40,A40p}, --printer {A6,A6p,A40,A40p}
                        Printer model selection
  -t TEXT, --text TEXT  ASCII text to print. Text must be ASCII-safe and will be filtered for invalid characters
  -s, --stream          Print text received from STDIN, line by line. Text must be ASCII-safe and will be filtered for invalid characters
  -i IMAGE, --image IMAGE
                        Path to the image for printing
  -q QR, --qr QR        String to convert into a QR code for printing
  -e, --introduce       Ask the printer to introduce itself
```

### Print image example

**Print image from [file](https://github.com/bitrate16/peripage-python/blob/main/honk.png) with following break for 100px and concentration set to 2 (HIGH) on A6+**
```
peripage -m 00:15:83:15:bc:5f -p A6p -b 100 -c 2 -i honk.png
```

### Print text example

**Print some random text followed by newline and break for 100px on A6+**
```
peripage -m 00:15:83:15:bc:5f -p A6p -b 100 -t "HONK" -n
```
Newline is required to fush the internal printer buffer and force it to print all text without cutting

### Create ruler example

This will generate an image of ruler, approximately matching real centimeters (measured with unpreciese real ruler) on Periapge A6+

```python

WIDTH = 576
WIDTH_MM = 48.5
MM2PX = WIDTH / WIDTH_MM
CM2PX = 10 * MM2PX
TICKS = 100
TICK_HEIGHT = 4
TICK_WIDTH = 50


import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont


image = PIL.Image.new('RGB', (WIDTH, int(MM2PX * 10 * (TICKS + 2))), (255, 255, 255))
draw = PIL.ImageDraw.Draw(image)
# font = PIL.ImageFont.truetype('/usr/share/fonts/gnu-free/FreeSans.ttf', 18)
font = PIL.ImageFont.truetype('/usr/share/fonts/open-sans/OpenSans-Regular.ttf', 40)

for tick in range(1, TICKS + 2):
    for ty in range(TICK_HEIGHT):
        for tx in range(TICK_WIDTH):
            image.putpixel(
                (
                    int(tx),
                    int(tick * CM2PX + ty),
                ),
                (0, 0, 0),
            )

        draw.text(
            (
                int(TICK_WIDTH * 2),
                int(tick * CM2PX - 0.25 * CM2PX + ty),
            ),
            text=str(tick - 1),
            font=font,
            fill='black',
        )


image.save('ruler.png')

```

## Print Service

**Print 50 text tasks on A6+**
```python
import peripage
import print_service

# Ping battery every 60 seconds
# Send task every 5 seconds
# Try to reconnect after waiting 5 seconds
# Wait 1 second before send after connecting/reconnecting to printer
# Print only after pinging printer and waiting for 1 second
service = print_service.PrintService(60, 5, 5, 1, 1)
service.start('00:15:83:15:bc:5f', peripage.PrinterType.A6p)
for i in range(50):
	service.add_print_ascii(f'number {i}', flush=True)
```
Newline is required to fush the internal printer buffer and force it to print all text without cutting

## Recommendations

* Don't forget about concentration, this can make print brighter and better visible.
* Split long images into multiple print requests with cooldown time for printer (printer may overheat during a long print and will stop printing for a while. This will result in partial print loss because the internal buffer is about 250px height). For example, when you print [looooooooooooooooooooooooooooooongcat.jpg](http://lurkmore.so/images/9/91/Loooooooooooooooooooooooooooooooooooooooooongcat.JPG), split it into at least 20 pieces with 1-2 minutes delay because you will definetly loose something without cooling. Printer gets hot very fast. Yes, it was the first that i've printed.
* Be carefull when printing lots of black or using max concentration, as i said, printer heats up very fast.
* The picture printed at maximum concentration has the longest shelf life.
* Turn printer off then long press the power button till it becomes orange. Release the button and look at the another useless feature.
* Be aware of cats, they have paws 🐾

## Code example

View this [python notebook](https://github.com/bitrate16/peripage-python/blob/main/notebooks/peripage-tutorial.ipynb) for tutorial

View this [python notebook](https://github.com/bitrate16/peripage-python/blob/main/notebooks/Test-notebook.ipynb) for test

## Printer disassembly

[Disassembly for A6+](https://imgur.com/a/6LLwuaD)

## TODO

* Fix page sometimes get cutted off for some rows
* Fix delays
* ~~Python 2.7 support~~ (Don't need)
* Implement overheat protection
* Implement cover open handler
* Tweak wait timings to precisely match printing speed
* Implement printer renaming
* Implement printing stop operation
* Reverse-engineer USB driver and add support for it
* Print randomly gets cropped (some images getting cropped)
* 1 type conversion is low quality

## Contribution

> Q: How to contribute?
>
> A: Implement some features and make a pull request in this repo. For example, you could add info about USB communication, write a any-font printing using PIL text drawing, make an additional research in protocol and other cool things.

> Q: How to get my printer supported?
>
> A: If you own a peripage printer that is currently unsupported, you can reverse-engineer the bluetooth packets captured from the oficial printing app and find out the specs of your printer (the main and the only spec is bytes per row). Another way is to find how many letters can fit in a row when using `printASCII()`.
>
> If you would like to participate, please make an issue and I will guide you on how to obtain required parameters.

## Credits

* [Elias Weingärtner](https://github.com/eliasweingaertner) for initial work in reverse-engineering bluetooth protocol
* [bitrate16](https://github.com/bitrate16) for additional research and python module
* [henryleonard](https://github.com/henryleonard) for specs of A40 printer
* [anthony-foulfoin](https://github.com/anthony-foulfoin) for specs of A40+ printer

## License

[GPLv3 License](https://github.com/bitrate16/peripage-python/blob/main/LICENSE)
