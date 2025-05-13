# Simulation of Terminal and Keyboard

# TAB key cannot be caught currently

from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
from threading import Thread, Lock
import time
import tkinter as tk

class VIOS():
    def __init__(self,
                 IP='127.0.0.1',
                 listening_port=9000,
                 sending_port=9001):
        self.client = udp_client.SimpleUDPClient(IP, sending_port)
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/avatar/parameters/*", self.server_handler)
        self.server = osc_server.ThreadingOSCUDPServer((IP, listening_port), self.dispatcher)

        self.content = [[' ' for j in range(40)] for i in range(8)]
        self.parameters = {
            '/avatar/parameters/TaSTT_Select': 0,
        }
        for byte in range(20):
            self.parameters[f"/avatar/parameters/TaSTT_L{byte:02}B0_Blend"] = 0
        
        self.window = tk.Tk()
        self.window.title("VIOS")
        self.window.geometry("800x400")
        self.text_area = tk.Text(self.window, font=("Courier New", 24))
        self.text_area.config(state="normal")
        self.text_area.pack(expand=True, fill=tk.BOTH)
        self.window.bind_all("<KeyPress>", self.key_press)
        self.window.bind_all("<KeyRelease>", self.key_release)

        self.reversed_keymap = {
            "GRAVE": 53,
            "1": 30,
            "2": 31,
            "3": 32,
            "4": 33,
            "5": 34,
            "6": 35,
            "7": 36,
            "8": 37,
            "9": 38,
            "0": 39,
            "MINUS": 45,
            "EQUAL": 46,
            "BACKSPACE": 76,
            "TAB": 43, # cannot be caught
            "Q": 20,
            "W": 26,
            "E": 8,
            "R": 21,
            "T": 23,
            "Y": 28,
            "U": 24,
            "I": 12,
            "O": 18,
            "P": 19,
            "[": 47,
            "]": 48,
            "A": 4,
            "S": 22,
            "D": 7,
            "F": 9,
            "G": 10,
            "H": 11,
            "J": 13,
            "K": 14,
            "L": 15,
            "SEMICOLON": 51,
            "APOSTROPHE": 52,
            "RETURN": 40,
            "BACKSLASH": 49,
            "Z": 29,
            "X": 27,
            "C": 6,
            "V": 25,
            "B": 5,
            "N": 17,
            "M": 16,
            "COMMA": 54,
            "PERIOD": 55,
            "SLASH": 56,
            "ESCAPE": 41,
            "SPACE": 44,
        }
        self.key_state = {
            "Shift": False,
            "Ctrl": False,
            "Fn": False,
            "Caps": False,
            "Alt": False,
        }
        pass

    def key_press(self, event):
        print(f"KeyPressed: Keysym={event.keysym}, Char='{event.char}', Keycode={event.keycode}")
        if "Shift_L" == event.keysym:
            self.key_state['Shift'] = not self.key_state['Shift']
            self.client.send_message('/avatar/parameters/Key/Output/Shift', self.key_state['Shift'])
        elif "Alt_L" == event.keysym:
            self.key_state['Alt'] = not self.key_state['Alt']
            self.client.send_message('/avatar/parameters/Key/Output/Alt', self.key_state['Alt'])
        elif "Super_L" == event.keysym:
            self.key_state['Fn'] = not self.key_state['Fn']
            self.client.send_message('/avatar/parameters/Key/Output/Fn', self.key_state['Fn'])
        elif "Caps_Lock" == event.keysym:
            self.key_state['Caps'] = not self.key_state['Caps']
            self.client.send_message('/avatar/parameters/Key/Output/Caps', self.key_state['Caps'])
        elif "Control_L" == event.keysym:
            self.key_state['Ctrl'] = not self.key_state['Ctrl']
            self.client.send_message('/avatar/parameters/Key/Output/Ctrl', self.key_state['Ctrl'])
        elif event.keysym.upper() in self.reversed_keymap:
            keycode = self.reversed_keymap[event.keysym.upper()]
            self.client.send_message('/avatar/parameters/Key/Output/Int', keycode)
              
    def key_release(self, event):
        print(f"KeyReleased: Keysym={event.keysym}, Char='{event.char}', Keycode={event.keycode}, State={event.state}")
        if event.keysym.upper() in self.reversed_keymap:
            keycode = self.reversed_keymap[event.keysym.upper()]
            self.client.send_message('/avatar/parameters/Key/Output/Int', 0)

    def server_handler(self, addr, *args):
        if "/avatar/parameters/TaSTT" in addr:
            self.parameters[addr] = args[0]
            select = self.parameters['/avatar/parameters/TaSTT_Select']
            row, col = select//2, (select%2)*20
            for i in range(20):
                raw = self.parameters[f"/avatar/parameters/TaSTT_L{i:02}B0_Blend"]
                self.content[row][col+i] = chr(round(raw*127.5 + 127.5))

    def heartbeat_daemon(self):
        bit = False
        while 1:
            self.client.send_message('/avatar/parameters/Heartbeat', bit)
            bit = not bit
            time.sleep(0.5)

    def serve(self):
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.heartbeat = Thread(target=self.heartbeat_daemon, daemon=True)
        self.heartbeat.start()
        self.terminal = Thread(target=self.terminal_daemon, daemon=True)
        self.terminal.start()
        self.window.mainloop()

    def terminal_daemon(self, interval=0.2):
        while 1:
            self.text_area.delete("1.0", tk.END)
            for row in self.content:
                self.text_area.insert(tk.END, "".join(row) + "\n")
            time.sleep(interval)

if __name__ == "__main__":
    vios = VIOS()
    vios.serve()

    pass