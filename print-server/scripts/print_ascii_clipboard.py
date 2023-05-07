import pyperclip
import requests
import sys

SERVER_ADDR   = 'http://127.0.0.1:11001'
BREAK         = 1 # Enable/disable
CONCENTRATION = 2 # Value (0-2)
SECRET_KEY    = '1234567890'

s = pyperclip.paste().strip().replace('\t', '    ')
s = ''.join([i for i in s if (31 < ord(i) or ord(i) == 10) and ord(i) < 127])
print(s)

r = requests.post(
	url=f'{SERVER_ADDR}/print_ascii?print_break={BREAK}&print_concentration={CONCENTRATION}&secret={SECRET_KEY}',
	data=s
)

print(r.status_code, r.text)
