import requests
import sys

SERVER_ADDR   = '192.168.1.101:11001'
BREAK         = 1 # Enable/disable
CONCENTRATION = 2 # Value (0-2)
SECRET_KEY    = '1234567890'

r = requests.post(
	url=f'http://{SERVER_ADDR}/print_image?print_break={BREAK}&print_concentration={CONCENTRATION}&secret={SECRET_KEY}', 
	files={
		'image': open(sys.argv[1], 'rb')
	}
)

print(r.status_code, r.text)
