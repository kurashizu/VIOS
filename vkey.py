from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
from threading import Thread, Lock
import time

class Keyboard():
    def __init__(self,
                 IP='127.0.0.1',
                 listening_port=9001,
                 sending_port=9000):

        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/avatar/parameters/*", self.server_handler)
        self.server = osc_server.ThreadingOSCUDPServer((IP, listening_port), self.dispatcher)
        self.client = udp_client.SimpleUDPClient(IP, sending_port)
        self.lock = Lock()
        self.counter = 0
        self.connected = False

        self.status = {
            'keyname': 'Idle',
            'scancode': 0,
            'shift': False,
            'ctrl': False,
            'capslk': False,
            'fn': False,
            'alt': False,
        }

        self.keymap = {
            53: "Sync",
            30: "1",
            31: "2",
            32: "3",
            33: "4",
            34: "5",
            35: "6",
            36: "7",
            37: "8",
            38: "9",
            39: "0",
            45: "-",
            46: "=",
            76: "Delete",
            43: "Tab",
            20: "Q",
            26: "W",
            8: "E",
            21: "R",
            23: "T",
            28: "Y",
            24: "U",
            12: "I",
            18: "O",
            19: "P",
            47: "[",
            48: "]",
            4: "A",
            22: "S",
            7: "D",
            9: "F",
            10: "G",
            11: "H",
            13: "J",
            14: "K",
            15: "L",
            51: ";",
            52: "'",
            40: "Enter",
            49: "\\",
            29: "Z",
            27: "X",
            6: "C",
            25: "V",
            5: "B",
            17: "N",
            16: "M",
            54: ",",
            55: ".",
            56: "/",
            41: "Esc",
            44: "Space",
            0: "Idle"
            }
        pass

    def server_handler(self, addr, *args):
        if addr == '/avatar/parameters/Key/Output/Int':
            self.lock.acquire()
            self.status['scancode'] = args[0]
            self.status['keyname'] = self.keymap[args[0]]
            self.lock.release()
        elif addr == '/avatar/parameters/Key/Output/Ctrl':
            self.lock.acquire()
            self.status['ctrl'] = args[0]
            self.lock.release()
        elif addr == '/avatar/parameters/Key/Output/Shift':
            self.lock.acquire()
            self.status['shift'] = args[0]
            self.lock.release()
        elif addr == '/avatar/parameters/Key/Output/Alt':
            self.lock.acquire()
            self.status['alt'] = args[0]
            self.lock.release()
        elif addr == '/avatar/parameters/Key/Output/Caps':
            self.lock.acquire()
            self.status['capslk'] = args[0]
            self.lock.release()
        elif addr == '/avatar/parameters/Key/Output/Fn':
            self.lock.acquire()
            self.status['fn'] = args[0]
            self.lock.release()
        elif addr == '/avatar/parameters/Heartbeat':
            self.connected = True
            self.counter = 0

    def heartbeat_daemon(self):
        while 1:
            self.counter += 1
            time.sleep(0.5)
            if self.counter >= 3:
                self.connected = False

    def serve(self):
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.heartbeat = Thread(target=self.heartbeat_daemon, daemon=True)
        self.heartbeat.start()

    def sendKey(self, key='shift', value=False):
        if key == 'scancode':
            addr = '/avatar/parameters/Key/Output/Int'
        elif key == 'ctrl':
            addr = '/avatar/parameters/Key/Output/Ctrl'
        elif key == 'shift':
            addr = '/avatar/parameters/Key/Output/Shift'
        elif key == 'alt':
            addr = '/avatar/parameters/Key/Output/Alt'
        elif key == 'capslk':
            addr = '/avatar/parameters/Key/Output/Caps'
        elif key == 'fn':
            addr = '/avatar/parameters/Key/Output/Fn'
        self.client.send_message(addr, value)

        self.lock.acquire()
        self.status[key] = value
        self.lock.release()
    
    def waitKey(self, scancode=0):
        '''
        wait for key with specified scancode (0 = any scancode)
        '''
        while 1:
            key_status = self.getStatus()
            if scancode:
                if key_status['scancode'] == scancode:
                    break
            elif key_status['scancode']:
                break
            time.sleep(0.05)
        return key_status

    def clear(self):
        self.sendKey('ctrl', False)
        self.sendKey('shift', False)
        self.sendKey('alt', False)
        self.sendKey('fn', False)
        self.sendKey('capslk', False)

    def getStatus(self):
        self.lock.acquire()
        status = self.status.copy()
        self.lock.release()
        return status
    
if __name__ == "__main__":
    keyboard = Keyboard()

    keyboard.serve()
    
    while 1:
        time.sleep(1)
    pass
