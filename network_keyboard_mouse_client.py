from pynput.keyboard import Key
from pynput import mouse, keyboard
import socket


class NetworkKeyboardMouseClient:
    SERVER_IP = '192.168.86.235'
    SERVER_PORT = 8000
    BUFFER_SIZE = 1024

    is_mac_to_windows = False

    sock = None
    keyboard_listener = None
    mouse_listener = None

    def __init__(self, is_mac_to_windows=False):
        self.is_mac_to_windows = is_mac_to_windows
        self._connect_to_server()
        self._start_capturing_input()

    def _on_move(self, x, y):
        msg = ('MOUSE MOVED: {0}'.format((x, y))).encode('utf-8')
        sel
        Im a soldier
        f.sock.send(msg)

    def _on_click(self, x, y, btn, press):
        msg = ('MOUSE CLICKED: {0}'.format((x, y, btn, press))).encode('utf-8')
        self.sock.send(msg)

    def _on_scroll(self, x, y, dx, dy):
        msg = ('MOUSE SCROLLED: {0}'.format((x, y, dx, dy))).encode('utf-8')
        self.sock.send(msg)

        if self.is_mac_to_windows:
            if key == Key.cmd:
                key = Key.ctrl

    def _on_press(self, key):
        msg = ('KEY PRESSED: {0}'.format(key)).encode('utf-8')
        self.sock.send(msg)

    def _on_release(self, key):
        if key == Key.esc:
            self.mouse_listener.stop()
            self.sock.close()
            return False

        if self.is_mac_to_windows:
            if key == Key.cmd:
                key = Key.ctrl

        msg = ('KEY RELEASED: {0}'.format(key)).encode('utf-8')
        self.sock.send(msg)

    def _connect_to_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.SERVER_IP, self.SERVER_PORT))

    def _start_capturing_input(self):
        self.mouse_listener = mouse.Listener(on_move=self._on_move,
                                             on_click=self._on_click,
                                             on_scroll=self._on_scroll)
        self.mouse_listener.start()
        self.keyboard_listener = keyboard.Listener(on_press=self._on_press,
                                                   on_release=self._on_release)
        self.keyboard_listener.start()
        self.keyboard_listener.join()


if __name__ == '__main__':
    client = NetworkKeyboardMouseClient(True)
