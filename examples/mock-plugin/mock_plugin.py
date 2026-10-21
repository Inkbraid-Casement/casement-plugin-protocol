# A Casement protocol plugin for tests (docs/plugin-protocol.md), in plain
# Python. It "connects" to mock://<anything>: with ?expect=<word> in the
# address it wants that password first (state auth_failed until it comes).
# Then it draws colour bars into the shared surface, moves a white block
# across them ten times a second, marks the pointer with a square, sends a
# crosshair cursor, and echoes clipboard text back with "echo: " in front.
# Every message from Casement is written to the file named by
# MOCK_PLUGIN_LOG (when set), one JSON object per line.
import ctypes
import json
import os
import struct
import sys
import threading
import time
import urllib.parse
from ctypes import wintypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
kernel32.MapViewOfFile.restype = ctypes.c_void_p
kernel32.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
FILE_MAP_ALL_ACCESS = 0xF001F

stdin = sys.stdin.buffer
stdout = sys.stdout.buffer
out_lock = threading.Lock()
LOG = os.environ.get('MOCK_PLUGIN_LOG')
W, H = 1280, 720


def log(obj):
    if LOG:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(obj) + '\n')


def send(obj):
    data = json.dumps(obj).encode('utf-8')
    with out_lock:
        stdout.write(struct.pack('<I', len(data)) + data)
        stdout.flush()


def receive():
    header = stdin.read(4)
    if len(header) < 4:
        return None
    (n,) = struct.unpack('<I', header)
    return json.loads(stdin.read(n).decode('utf-8'))


class Surface:
    def __init__(self, msg):
        self.id = msg['id']
        self.width, self.height, self.stride = msg['width'], msg['height'], msg['stride']
        self.handle = msg['handle']
        self.size = msg['size']
        self.view = kernel32.MapViewOfFile(self.handle, FILE_MAP_ALL_ACCESS, 0, 0, self.size)
        if not self.view:
            raise OSError('MapViewOfFile failed: %d' % ctypes.get_last_error())

    def close(self):
        kernel32.UnmapViewOfFile(self.view)
        kernel32.CloseHandle(self.handle)

    def row(self, y, x, pixels):
        ctypes.memmove(self.view + y * self.stride + x * 4, pixels, len(pixels))

    def fill(self, x, y, w, h, bgrx):
        x, y = max(0, x), max(0, y)
        w, h = min(w, self.width - x), min(h, self.height - y)
        if w <= 0 or h <= 0:
            return None
        line = bytes(bgrx) * w
        for yy in range(y, y + h):
            self.row(yy, x, line)
        return [x, y, w, h]


BARS = [(255, 255, 255), (0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 255), (0, 0, 255), (255, 0, 0)]  # BGR


def draw_bars(s, x, w):
    # The bars under one column range, so the block leaves no trail.
    bar_w = s.width // len(BARS)
    for i, (b, g, r) in enumerate(BARS):
        left, right = max(x, i * bar_w), min(x + w, (i + 1) * bar_w if i < len(BARS) - 1 else s.width)
        if right > left:
            s.fill(left, 0, right - left, s.height, (b, g, r, 255))


state = {'surface': None, 'acked': True, 'pointer': None, 'block': 0, 'connected': False}
lock = threading.Lock()


def frame(rects):
    s = state['surface']
    send({'type': 'frame', 'surface': s.id, 'rects': [r for r in rects if r]})
    state['acked'] = False


def animate():
    while True:
        time.sleep(0.1)
        with lock:
            s = state['surface']
            if not s or not state['acked'] or not state['connected']:
                continue
            old = state['block']
            new = (old + 16) % (s.width - 64)
            draw_bars(s, old, 64)
            rects = [[old, s.height // 2 - 32, 64, 64]]
            rects.append(s.fill(new, s.height // 2 - 32, 64, 64, (255, 255, 255, 255)))
            state['block'] = new
            p = state['pointer']
            if p:
                rects.append(s.fill(p[0] - 4, p[1] - 4, 9, 9, (0, 0, 0, 255)))
            frame(rects)


def crosshair():
    size = 17
    rgba = bytearray(size * size * 4)
    for i in range(size):
        for (x, y) in ((i, size // 2), (size // 2, i)):
            o = (y * size + x) * 4
            rgba[o:o + 4] = bytes((255, 0, 0, 255))
    import base64
    return {'type': 'cursor', 'width': size, 'height': size, 'hot_x': size // 2, 'hot_y': size // 2,
            'rgba': base64.b64encode(bytes(rgba)).decode()}


def main():
    hello = receive()
    log(hello)
    send({'type': 'hello', 'protocol': 1, 'name': 'Mock plugin', 'version': '1.0',
          'capabilities': ['password', 'clipboard', 'cursor']})
    threading.Thread(target=animate, daemon=True).start()
    while True:
        msg = receive()
        if msg is None:
            break
        log(msg)
        kind = msg.get('type')
        if kind == 'connect':
            query = urllib.parse.parse_qs(urllib.parse.urlparse(msg['address']).query)
            wanted = query.get('expect', [None])[0]
            if wanted is not None and msg.get('password') != wanted:
                send({'type': 'state', 'state': 'auth_failed', 'text': 'That password is wrong.'})
                continue
            send({'type': 'state', 'state': 'connected'})
            send({'type': 'surface_request', 'width': W, 'height': H})
            send(crosshair())
        elif kind == 'surface':
            with lock:
                if state['surface']:
                    state['surface'].close()
                s = state['surface'] = Surface(msg)
                draw_bars(s, 0, s.width)
                state['connected'] = True
                frame([])
        elif kind == 'frame_ack':
            with lock:
                state['acked'] = True
        elif kind == 'pointer':
            with lock:
                state['pointer'] = (msg['x'], msg['y'])
        elif kind == 'clipboard':
            send({'type': 'clipboard', 'text': 'echo: ' + msg.get('text', '')})
        elif kind == 'disconnect':
            break
    print('mock plugin: bye', file=sys.stderr)


main()
