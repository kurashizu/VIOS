# Simple Input Method

from vkey import Keyboard
from terminal import Terminal
import time

class SimpleIM():
    def __init__(self, keyboard: Keyboard, terminal: Terminal):
        self.keyboard = keyboard
        self.terminal = terminal

        self.printable = { # key = scancode, value = printable_char
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
            20: "q",
            26: "w",
            8: "e",
            21: "r",
            23: "t",
            28: "y",
            24: "u",
            12: "i",
            18: "o",
            19: "p",
            47: "[",
            48: "]",
            4: "a",
            22: "s",
            7: "d",
            9: "f",
            10: "g",
            11: "h",
            13: "j",
            14: "k",
            15: "l",
            51: ";",
            52: "'",
            49: "\\",
            29: "z",
            27: "x",
            6: "c",
            25: "v",
            5: "b",
            17: "n",
            16: "m",
            54: ",",
            55: ".",
            56: "/",
            44: " ",
        }
        self.shifted_printable = { # key = scancode, value = printable_char (with Shift)
            30: "!",
            31: "@",
            32: "#",
            33: "$",
            34: "%",
            35: "^",
            36: "&",
            37: "*",
            38: "(",
            39: ")",
            45: "_",
            46: "+",
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
            47: "{",
            48: "}",
            4: "A",
            22: "S",
            7: "D",
            9: "F",
            10: "G",
            11: "H",
            13: "J",
            14: "K",
            15: "L",
            51: ":",
            52: "\"",
            49: "|",
            29: "Z",
            27: "X",
            6: "C",
            25: "V",
            5: "B",
            17: "N",
            16: "M",
            54: "<",
            55: ">",
            56: "?",
            44: " ",
        }
        pass

    def input(self, offset=(0,0), size=(4,40)):
        '''
        IM takes over the keyboard and creates a window of the specified size.
        Return a string that the user has input.

        offset: starting point at the top left corner of the IM window
        size: height and width of the IM window
        '''
        seq = ''
        cursor = [0, 0]
        canvas = [[False for j in range(size[1])] for i in range(size[0])]

        def move_cursor(direction='next'):
            if direction == 'next':
                cursor_next = cursor[1]+1
                cursor[1] = cursor_next%size[1]
                if cursor_next // size[1]:
                    cursor[0] = (cursor[0]+1)%size[0]
            elif direction == 'last':
                cursor_last = cursor[1]-1
                cursor[1] = cursor_last%size[1]
                if cursor_last // size[1]:
                    cursor[0] = (cursor[0]-1)%size[0]
            elif direction == 'up':
                cursor[0] = (cursor[0]-1)%size[0]
            elif direction == 'down':
                cursor[0] = (cursor[0]+1)%size[0]
            pass

        def print_canvas():
            # print_canvas
            for row in range(size[0]):
                self.terminal.cursor_to(row+offset[0], offset[1])
                self.terminal.print_buffer(''.join(map(lambda char: char if char else '~', canvas[row])))
            # print cursor
            self.terminal.cursor_to(cursor[0]+offset[0], cursor[1]+offset[1])
            self.terminal.print_buffer('_')

            self.terminal.refresh()

        def wait_key(key=None):
            # wait for keys that have scancodes
            # except for Ctrl, Alt, Caps, Cmd, Shift
            scancode = 0
            while 1:
                key_status = self.keyboard.getStatus()
                if key:
                    if key == key_status['scancode']:
                        break
                elif key_status['scancode']:
                    break
                time.sleep(0.05)
            return key_status
        
        def wait_key_released():
            scancode = 255
            while scancode:
                scancode = self.keyboard.getStatus()['scancode']
                time.sleep(0.1)

        while 1:
            print_canvas()
            key_status = wait_key()
            # print(f"{key_status}")

            if key_status['scancode'] in self.printable:
                if key_status['fn']: # function
                    if key_status['scancode'] == 26: # fn + w
                        move_cursor('up')
                    elif key_status['scancode'] == 4: # fn + a
                        move_cursor('last')
                    elif key_status['scancode'] == 22: # fn + s
                        move_cursor('down')
                    elif key_status['scancode'] == 7: # fn + d
                        move_cursor('next')

                elif key_status['shift']: # shift pressed
                    char = self.shifted_printable[key_status['scancode']]
                    canvas[cursor[0]][cursor[1]] = char
                    move_cursor('next')
                else: # normal
                    char = self.printable[key_status['scancode']]
                    if key_status['capslk']: # capslk pressed
                        char = char.upper()
                    canvas[cursor[0]][cursor[1]] = char
                    move_cursor('next')

            elif key_status['scancode'] == 53: # sync
                self.terminal.resync()
                pass

            elif key_status['scancode'] == 76: # backspace
                move_cursor('last')
                canvas[cursor[0]][cursor[1]] = False
                pass

            elif key_status['scancode'] == 41: # esc
                wait_key_released()
                return None
                pass

            elif key_status['scancode'] == 40: # enter
                string = ''
                for line in canvas:
                    string += ''.join(map(lambda char: char if char else '', line))
                wait_key_released()
                return string
                pass

            wait_key_released()

        pass

if __name__ == "__main__":
    terminal = Terminal()
    keyboard = Keyboard()
    keyboard.serve()

    terminal.cursor_to(7,20)
    terminal.print("VIOS Initialising...".rjust(20))
    terminal.clear(force=True)
    keyboard.clear()

    simpleim = SimpleIM(keyboard, terminal)

    while 1:
        string = simpleim.input(offset=(3,5), size=(3,10))
        print(f"Got user string: {string}")
    pass
