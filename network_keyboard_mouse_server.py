from pynput.keyboard import Key
from pynput.mouse import Button
from pynput import mouse, keyboard
import socket
import string

class NetworkKeyboardMouseServer():
	SERVER_IP = '192.168.86.235'
	SERVER_PORT = 8000
	BUFFER_SIZE = 1024

	keyboard_controller = None
	mouse_controller = None

	pressed_keys = None

	string_key_codes = { 'alt': Key.alt, 'alt_l': Key.alt_l,
	                     'alt_r': Key.alt_r, 'alt_gr': Key.alt_gr,
	                     'backspace': Key.backspace, 'caps_lock': Key.caps_lock,
	                     'cmd': Key.cmd, 'cmd_l': Key.cmd_l, 'cmd_r': Key.cmd_r,
	                     'ctrl': Key.ctrl, 'ctrl_l': Key.ctrl_l, 'ctrl_r': Key.ctrl_r, 
	                     'delete': Key.delete, 'down': Key.down, 'end': Key.end,
	                     'enter': Key.enter, 'esc': Key.esc, 'f1': Key.f1, 'f2': Key.f2,
	                     'f3': Key.f3, 'f4': Key.f4, 'f5': Key.f5, 'f6': Key.f6,
	                     'f7': Key.f7, 'f8': Key.f8, 'f9': Key.f9, 'f10': Key.f10, 
	                     'f11': Key.f11, 'f12': Key.f12, 'f13': Key.f13, 'f14': Key.f14,
	                     'f15': Key.f15, 'f16': Key.f16, 'f17': Key.f17, 'f18': Key.f18,
	                     'f19': Key.f19, 'f20': Key.f20, 'home': Key.home, 'left': Key.left,
	                     'page_down': Key.page_down, 'page_up': Key.page_up,
	                     'right': Key.right, 'shift': Key.shift, 'shift_l': Key.shift_l,
	                     'shift_r': Key.shift_r, 'space': Key.space, 'tab': Key.tab,
	                     'up': Key.up, 'media_play_pause': Key.media_play_pause,
	                     'media_volume_mute': Key.media_volume_mute,
	                     'media_volume_down': Key.media_volume_down,
	                     'media_volume_up': Key.media_volume_up,
	                     'media_previous': Key.media_previous,
	                     'media_next': Key.media_next, 'insert': Key.insert,
	                     'menu': Key.menu, 'num_lock': Key.num_lock,
	                     'pause': Key.pause, 'print_screen': Key.print_screen,
	                     'scroll_lock': Key.scroll_lock
	                    }
	event_type_headers = ['MOUSE MOVED: ', 'MOUSE CLICKED: ', 'MOUSE SCROLLED: ',
	                      'KEY PRESSED: ', 'KEY RELEASED: ']

	def __init__(self):
		self.keyboard_controller = keyboard.Controller()
		self.mouse_controller = mouse.Controller()
		self.pressed_keys = set()
		self._start_server()
		self._clean_up()

	def _send_keystroke(self, key, press):
		if 'Key.' in key and key.replace('Key.', '') in self.string_key_codes:
			key = self.string_key_codes[key.replace('Key.', '')]
		elif len(key) == 3 and key[0] == '\'' and key[-1] == '\'':
			key = key[1:-1]
			if key not in string.printable:
				return
		else:
			return
		if press:
			self.keyboard_controller.press(key)
			self.pressed_keys.add(key)
		else:
			self.keyboard_controller.release(key)
			self.pressed_keys.remove(key)

	def _move_mouse(self, x, y):
		self.mouse_controller.position = (x, y)

	def _click_mouse(self, x, y, btn, press):
		self._move_mouse(x, y)
		if press:
			self.mouse_controller.press(btn)
		else:
			self.mouse_controller.release(btn)

	def _scroll_mouse(self, x, y, dx, dy):
		self._move_mouse(x, y)
		self.mouse_controller.scroll(dx, dy)

	def _send_event(self, event):
		try:
			if 'MOUSE MOVED: ' in event:
				event = event.replace('MOUSE MOVED: ', '')[1:-1]
				components = event.split(',')
				x = float(components[0])
				y = float(components[1])
				self._move_mouse(x, y)
			elif 'MOUSE CLICKED: ' in event:
				event = event.replace('MOUSE CLICKED: ', '')[1:-1]
				components = event.split(',')
				x = float(components[0])
				y = float(components[1])
				btn = components[2]
				press = components[-1]
				if 'right' in btn:
					btn = Button.right
				else:
					btn = Button.left
				if press.strip() == 'False':
					press = False
				else:
					press = True
				self._click_mouse(x, y, btn, press)
			elif 'MOUSE SCROLLED: ' in event:
				event = event.replace('MOUSE SCROLLED: ', '')[1:-1]
				components = event.split(',')
				x = float(components[0])
				y = float(components[1])
				dx = int(components[2])
				dy = int(components[3])
				self._scroll_mouse(x, y, dx, dy)
			elif 'KEY PRESSED: ' in event:
				key = event.replace('KEY PRESSED: ', '')
				self._send_keystroke(key, True)
			elif 'KEY RELEASED: ' in event:
				key = event.replace('KEY RELEASED: ', '')
				self._send_keystroke(key, False)
		except Exception:
			pass

	def _parse_events(self, message):
		events = []

		event = ''
		while message:
			eth_present = False
			for eth in self.event_type_headers:
				if eth in message:
					eth_present = True
					if message.index(eth) == 0:
						event += eth
						message = message[len(eth):]
						break
					else:
						event += message[:message.index(eth)]
						events.append(event)
						event = ''
						message = message[message.index(eth):]
						break
			if not eth_present:
				event += message
				events.append(event)
				break
		return events
	
	def _handle_message(self, message):
		message = message.decode('utf-8')
		events = self._parse_events(message)
		for event in events:
			self._send_event(event)

	def _start_server(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((self.SERVER_IP, self.SERVER_PORT))
		s.listen(1)
		conn, addr = s.accept()

		print('Accepting input from: ' + addr[0])

		while 1:
			message = conn.recv(self.BUFFER_SIZE)
			if not message:
				break
			self._handle_message(message)
		conn.close()

	def _clean_up(self):
		for pressed_key in list(self.pressed_keys):
			self.keyboard_controller.release(pressed_key)


if __name__ == '__main__':
	server = NetworkKeyboardMouseServer()