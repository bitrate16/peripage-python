import pyperclip
import requests
import sys

SERVER_ADDR   = '192.168.1.101:11001'
BREAK         = 1 # Enable/disable
CONCENTRATION = 2 # Value (0-2)

s = pyperclip.paste().strip().replace('\t', '    ')
s = ''.join([i for i in s if (31 < ord(i) or ord(i) == 10) and ord(i) < 127])
print(s)

r = requests.post(
	url=f'http://{SERVER_ADDR}/print_ascii?print_break={BREAK}&print_concentration={CONCENTRATION}', 
	data=s
)

print(r.status_code, r.text)
