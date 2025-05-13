from pythonosc import udp_client
import time
import random

client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

# 8x40, cache_size=20, cache_amount=16
class Terminal():
    def __init__(self,
                 IP = "127.0.0.1",
                 sending_port = 9000,
                 waiting_time = 0.25):
        self.client = udp_client.SimpleUDPClient(IP, sending_port)
        self.waiting_time = waiting_time
        self.buffer = [[' ' for j in range(40)] for i in range(8)]
        self.content = [[' ' for j in range(40)] for i in range(8)]

        self.cursor_row = 0
        self.cursor_col = 0
    
    def write_cache(self, string='abcdefghij', region=0):
        string = string[:20].ljust(20)
        client.send_message(f"/avatar/parameters/TaSTT_Select", region)
        for i in range(20):
            self.client.send_message(f"/avatar/parameters/TaSTT_L{i:02}B0_Blend", (-127.5 + ord(string[i])) / 127.5)
        time.sleep(self.waiting_time)

    def enable(self,):
        self.client.send_message(f"/avatar/parameters/TaSTT_Enable", True)

    def disable(self,):
        self.client.send_message(f"/avatar/parameters/TaSTT_Enable", False)

    def refresh(self,):
        for index,line in enumerate(self.buffer):
            if line[:20] != self.content[index][:20]:
                self.write_cache(string=''.join(line[:20]), region=index*2)
                self.content[index] = line[:20] + self.content[index][20:]
            if line[20:] != self.content[index][20:]:
                self.write_cache(string=''.join(line[20:]), region=index*2+1)
                self.content[index] = self.content[index][:20] + line[20:]

    def print_buffer(self, string=""):
        for s in string:
            self.buffer[self.cursor_row][self.cursor_col] = s
            self.cursor_col = (self.cursor_col+1)%40

    def print(self, string="", refresh=True, force=False):
        string += ' ' * ((40 - (len(string) % 40)) % 40)

        for s in string:
            self.buffer[self.cursor_row][self.cursor_col] = s
            if force:
                self.content[self.cursor_row][self.cursor_col] = '\r'
            self.cursor_col += 1
            if self.cursor_col >= 40:
                self.cursor_col = 0
                self.cursor_row = (self.cursor_row+1)%8
        
        if refresh:
            self.refresh()

    def clear(self, refresh=True, force=False, cursor_init=True):
        self.buffer = [[' ' for j in range(40)] for i in range(8)]
        if force:
            self.content = [['A' for j in range(40)] for i in range(8)]
        if refresh:
            self.refresh()
        if cursor_init:
            self.cursor_col = 0
            self.cursor_row = 0

    def cursor_to(self, row=0, col=0):
        self.cursor_row = row
        self.cursor_col = col

    def resync(self):
        self.content = [[' ' for j in range(40)] for i in range(8)]
        self.refresh()

    def chatbox(self, msg, waiting_time=3):
        self.client.send_message(f"/chatbox/input", (msg, True, False))
        time.sleep(waiting_time)
        pass


if __name__ == "__main__":
    terminal = Terminal()

    terminal.enable()

    terminal.clear(force=True)

    c = 0

    while 1:
        terminal.cursor_to(0)
        terminal.print('<Tuantuanmiaomiao> This is a showcase of "VIOS (Virtual IO System)", displaying some real-time data. FPS:0.25Hz', force=True)
        terminal.cursor_to(3)
        terminal.print(f"Timestamp: {time.time()}".center(40,'-'), force=True)
        terminal.cursor_to(4)
        terminal.print(f"Random: {random.random():.5f}".center(40,'='), force=True)
        terminal.cursor_to(5)
        terminal.print(" "*c+">>>", force=True)
        c = (c+1)%37
        terminal.cursor_to(6)
        terminal.print(f"(Test) (Keyboard input not available currently) (Ready for interaction shortly)", force=True)

    terminal.disable()
