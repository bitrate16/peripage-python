import secrets
import requests
import sys
import PIL.ImageGrab
import secrets
import traceback
import os

SERVER_ADDR   = 'http://192.168.1.101:11001'
BREAK         = 1 # Enable/disable
CONCENTRATION = 2 # Value (0-2)
SECRET_KEY    = '1234567890'

# Detect type: list[str] or image

im = PIL.ImageGrab.grabclipboard()

if isinstance(im, list):
	im = im[0]
	
	if not (im.endswith('.png') or im.endswith('.jpg') or im.endswith('.jpeg')):
		raise RuntimeError('Invalid file type')
	
	try:
		r = requests.post(
			url=f'{SERVER_ADDR}/print_image?print_break={BREAK}&print_concentration={CONCENTRATION}&secret={SECRET_KEY}', 
			files={
				'image': open(im, 'rb')
			}
		)
		
		print(r.status_code, r.text)
	except:
		traceback.print_exc()

else:
	temp_name = f'{secrets.token_bytes(16).hex()}-temp.png'
	im.save(temp_name, 'PNG')
	
	try:
		r = requests.post(
			url=f'{SERVER_ADDR}/print_image?print_break={BREAK}&print_concentration={CONCENTRATION}&secret={SECRET_KEY}', 
			files={
				'image': open(temp_name, 'rb')
			}
		)
		
		print(r.status_code, r.text)
	except:
		traceback.print_exc()

	os.remove(temp_name)

