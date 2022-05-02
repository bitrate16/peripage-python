# Utility for tracking printing tasks
#
# MIT License
# 
# Copyright (c) 2022 bitrate16

import time
import threading

import ppa6


class Repeat():
	"""
	Interval-based code execution
	"""
	
	def __init__(self, interval: float, handler):
		self.interval = interval
		self.running = False
		self.should_stop = True
		self.thread = None
		self.handler = handler
	
	def start(self):
		if self.running:
			return False
		else:
			def handler():
				self.running = True
				
				while not self.should_stop:
					try:
						self.handler()
					except:
						# XXX: Important: we are ignoring this exception
						pass
					time.sleep(self.interval)
				
				self.running = False
				
			self.should_stop = False
			self.thread = threading.Thread(target=handler).start()
			return True
	
	def stop(self):
		if not self.running:
			return False
		else:
			self.should_stop = True
	
	def set_handler(self, handler):
		self.handler = handler
	
	def is_running(self):
		return self.running


class PrintService:
	"""
	This printer task autimatically handler print tasks from internal queue and 
	maintains printer connected state.
	
	Printer processes events in another thread by proocessing single event per 
	event_interval.
	
	If printer disconnects, this service will automatically reconnect it after 
	event_interval and print in the same time slot. If reconenct attempts fail, 
	it will wait given offline_interval until next connection attempt.
	
	If ping interval is over, printer will be pinged to return battery level and 
	keep connection alive (prevent sleep).
	"""
	
	def __init__(self, ping_interval: float = 60, event_interval: float = 1, offline_interval: float = 1, startup_interval: float = 1, guard_ping_interval: float = 1):
		# Printer keep-alive check interval, seconds
		self.ping_interval = ping_interval

		# Printer event check interval, seconds
		self.event_interval = event_interval

		# Last printer ping timestamp, seconds
		self.last_ping_timestamp = 0
		
		# Interval to wait after printer cconenction established
		self.startup_interval = startup_interval
		
		# Time between reconnect attempts
		self.offline_interval = offline_interval
		
		# interval between ping and data sending
		self.guard_ping_interval = guard_ping_interval

		# Serive task loop
		self.service: Repeat = None

		# Instance of printer
		self.printer: ppa6.Printer = None

		# Event queue
		self.events = []
		
		# Indicate service failture
		self.service_failture = True
		
	def start(self, printer_mac: str, printer_type: ppa6.PrinterType, timeout: float = 1.0):
		"""
		Perform startup oof the service without check for previous instance running.
		"""

		def service_handler():
			"""
			Internal event processing handler.
			"""
			
			initial_failture = True
			while self.service.is_running():
				try:
					if not self.printer.isConnected():
						raise RuntimeError('not connected')
					
					# Windows workaround
					try:
						self.printer.sock.listen()
					except:
						pass
				
					if not self.printer.isConnected():
						raise RuntimeError('not connected')
					
					# If time is over, perform keep-alive procedure
					if time.time() > (self.last_ping_timestamp + self.ping_interval):
						str(self.printer.getDeviceBattery())
						self.last_ping_timestamp = time.time()
						
					# Execute task handler
					# Task will be deleted only after correct execution without exceptions
					if len(self.events):
						
						str(self.printer.getDeviceBattery())
						self.last_ping_timestamp = time.time()
						
						time.sleep(self.guard_ping_interval)
						
						self.events[-1](self.printer)
						self.events.pop(0)
					
					# Return on success
					return
					
				except:
					# Connection error, reinitialize conenction
					self.service_failture = True
					
					# Wait for offline_interval before reconencts
					if not initial_failture:
						time.sleep(self.offline_interval)
					initial_failture = False
					
					# Disconnect
					try:
						if self.printer.isConnected():
							self.printer.disconnect()
					except:
						pass
					
					# Connect
					try:
						self.printer.connect()
						self.printer.reset()
						
						time.sleep(self.startup_interval)
						
						self.last_ping_timestamp = time.time()
						self.service_failture = False
					except:
						pass
		
		self.printer = ppa6.Printer(printer_mac, printer_type, timeout)
		self.last_ping_timestamp = time.time()
		self.events = []
		self.service = Repeat(self.event_interval, service_handler)
		self.service.start()
	
	def stop(self):
		try:
			self.service.stop()
			self.printer.disconnect()
		except:
			pass
			
	def is_service_failture(self):
		return self.service_failture
			
	def add_print_handler(self, print_handler):
		"""
		Adds event handler to the queue. THis handler will be executed with single 
		arguemnt - printer instance.
		
		Example:
		```
		printer_task.add_print_handler(lambda printer: printer.printASCII('hello'))
		```
		"""
		
		try:
			self.events.append(print_handler)
			return True
		except:
			return False

	def add_print_ascii(self, ascii_text: str, flush: bool = False):
		"""
		Adds simple print event to queue, additionally flushes output buffer.
		
		Example:
		```
		printer_task.add_print_ascii('hello', True)
		```
		"""
		
		def wrap_print(printer: ppa6.Printer):
			printer.printASCII(ascii_text)
			if flush:
				printer.flushASCII()
		
		
		try:
			self.events.append(wrap_print)
			return True
		except:
			return False
