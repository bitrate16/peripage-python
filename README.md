# peripage-python
### Python module for printing on Peripage printers

**This project is a continued development of the [original project](https://github.com/eliasweingaertner/peripage-A6-bluetooth) made by [Elias Weingärtner](https://github.com/eliasweingaertner). This module combined all results of reverse engineering of the Peripage A6/A6+ protocol in a python utility providing interface and CLI tool for printing on this thermal printer.**

## [The original introduction](https://github.com/eliasweingaertner/peripage-A6-bluetooth#introduction)

The Peripage A6 F622 is an inexpensive portable thermal printer. It provides both Bluetooth and USB connectivity. Unlike most other thermo printers it **does not** seem to support ESC/POS or any other standardized printer control language.

So far, the Peripage A6 F622 can be only controlled using a proprietary app (iOS / Anndroid). There is also a driver for Windows with many limitations, most notably the need of defining a page size before printing; this is a huge limitation, as the Peripage prints on continuous form paper.

The script provided here was built based on an analysis of captured Bluetooth traffic between the printer and an Android device. The Peripage A6 uses the serial profile (BTSPP) and RFCOMM.

Essentially, the script takes an input images, scales it to the printers native X resolution of 384 pixels, and then sends it to the printer.

## Current abilities

* Printing text of any length encoded in ASCII
* Printing Images using PIL library
* Printing raw bytes representing image in binary (black/white) form
* Printing a page break of desired size (in pixels)
* Printing using generator/iterator which returns image row by row in form of bytes or PIL Images
* Requesting printer details (Serial Number, Name, Battery Level, Hardware Info and an option the meaning of which i don't know)
* Configuring print concentration (light, gray, black)
* Configuring printer poweroff timeout

## Prerequirements
* Peripage A6/A6+ printer
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
* `PyBluez==0.30`
* `Pillow==8.1.2`
* `argparse==1.1` (for CLI)

Install dependencies with
`pip install -r requirements.txt`

On windows you may need to install PyBluez 0.3
```
git clone https://github.com/pybluez/pybluez
cd pybluez
pip install . --user
```

On raspberry pi it may require to install additional libraries
```
sudo apt install libbluetooth-dev libopenjp2-7 libtiff5
```

And in some cases you will have to restart the bluetooth adapter and service on raspberry pi when it fails to connect or device is busy
```
sudo systemctl restart bluetooth
sudo hciconfig hci0 reset
```

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
usage: __main__.py [-h] -m MAC [-c [0-2]] [-b [0-255]] -p {A6,A6p,A40} (-t TEXT | -s | -i IMAGE | -q QR | -e)

Print on a Peripage printer via bluetooth

optional arguments:
  -h, --help            show this help message and exit
  -m MAC, --mac MAC     Bluetooth MAC address of the printer
  -c [0-2], --concentration [0-2]
                        Concentration value for printing (temperature)
  -b [0-255], --break [0-255]
                        Size of the break inserted after printed image or text
  -p {A6,A6p,A40}, --printer {A6,A6p,A40}
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

### Print Service example

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

### Suggestions
* Don't forget about concentration, this can make print brighter and better visible.
* Split long images into multiple print requests with cooldown time for printer (printer may overheat during a long print and will stop printing for a while. This will result in partial print loss because the internal buffer is about 250px height). For example, when you print [looooooooooooooooooooooooooooooongcat.jpg](http://lurkmore.so/images/9/91/Loooooooooooooooooooooooooooooooooooooooooongcat.JPG), split it into at least 20 pieces with 1-2 minutes delay because you will definetly loose something without cooling. Printer gets hot very fast. Yes, it was the first that i've printed.
* Be carefull when printing lots of black or using max concentration, as i said, printer heats up very fast.
* The picture printed at maximum concentration has the longest shelf life.
* Turn printer off then long press the power button till it becomes orange. Release the button and look at the another useless feature.
* Be aware of cats, they have paws 🐾

## Code example

View this [python notebook](https://github.com/bitrate16/peripage-python/blob/main/notebooks/peripage-tutorial.ipynb) for tutorial

## Printer disassembly

[Disassembly for A6+](https://imgur.com/a/6LLwuaD)

## TODO

* Fix page sometimes get cutted off for some rows
* Fix delays
* Python 2.7 support
* Implement overheat protection
* Implement cover open handler
* Tweak wait timings to precisely match the printing speed
* Implement printer renaming
* Implement printing stop operation
* Reverse-engineer USB driver and add support for it
* **FIX:** Print randomly gets cropped (some images getting cropped)
* **FIX:** 1 type conversion is low quality

## Credits

* [Elias Weingärtner](https://github.com/eliasweingaertner) for initial work in reverse-engineering bluetooth protocol
* [bitrate16](https://github.com/bitrate16) for additional research and python module

## Disclaimer

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.**

## License

[MIT License](https://github.com/bitrate16/peripage-python/blob/main/LICENSE)
