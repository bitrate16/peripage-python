# print-server

Simple utility for creating standalone print server for peripage A6/A6+ thermal printer

# Configure

Edit config in `__main__.py`
```python
# Config
PRINTER_MODEL = ppa6.PrinterType.A6p
PRINTER_MAC   = '00:15:83:15:bc:5f'
SERVER_PORT   = 11001
BREAK_SIZE    = 100
TIMEZONE      = 'Europe/Moscow'
SECRET_KEY    = '1234567890'
```

Edit server properties in `scripts/print_ascii_clipboard.py`
```python
SERVER_ADDR   = '192.168.1.101:11001'
BREAK         = 1 # Enable/disable
CONCENTRATION = 2 # Value (0-2)
SECRET_KEY    = '1234567890'
```

Edit server properties in `scripts/print_image_drag_and_drop.py`
```python
SERVER_ADDR   = '192.168.1.101:11001'
BREAK         = 1 # Enable/disable
CONCENTRATION = 2 # Value (0-2)
SECRET_KEY    = '1234567890'
```

Edit server properties in `scripts/print_image_clipboard.py`
```python
SERVER_ADDR   = '192.168.1.101:11001'
BREAK         = 1 # Enable/disable
CONCENTRATION = 2 # Value (0-2)
SECRET_KEY    = '1234567890'
```

# Requirements

Libraries:
```bash
$ sudo apt install bluetooth bluez libbluetooth-dev libopenjp2-7
```

Packages:
```
$ pip3 install Pillow aiohttp aiohttp_middlewares ppa6 python-dateutil
```

# Usage

### ASCII text print

Tabs automatically converted to 4 spaces

1. Copy text to clipboard
2. Run `print_ascii_clipboard.py` or `print_ascii_clipboard.bat`

Endpoint:
```
Set print_date to 1 to enable print leading date
Set print_break to 1 to enable print trailing break
Set request body to ASCII text to print

POST /print_ascii?print_date=1&print_break=1
body: "Hello World!"
```

### Image print

Supported: jpeg, png

1. Drag and drop image file on `print_image_drag_and_drop.bat.py` or `print_image_drag_and_drop.bat`

Endpoint:
```
Set print_date to 1 to enable print leading date
Set print_break to 1 to enable print trailing break
Set request body to image file, supported png and jpg

POST /print_image?print_break=1
body: { image: binary image file }
```

### Image print from clipboard

Supported: jpeg, png

1. Copy image from browser/editor/etc and run `print_image_clipboard.py` or `print_image_clipboard.bat`
Endpoint: Same as above

# Run

Run with:
```
python3 -m print-server
```
