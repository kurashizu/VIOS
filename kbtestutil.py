# Keyboard Test Utility
# by Kurashizu

from terminal import Terminal
from vkey import Keyboard
import time
from threading import Thread
import json

# Load config
print("Loading config.json...")
with open('config.json', 'r', encoding="utf-8") as config:
    cfg = json.load(config)

IP=cfg["kbtestutil_config"]["IP"]
sending_port=cfg["kbtestutil_config"]["sending_port"]
listening_port=cfg["kbtestutil_config"]["listening_port"]
terminal_waiting_time=cfg["kbtestutil_config"]["terminal"]["waiting_time"]
is_banner_enabled = cfg["kbtestutil_config"]["is_banner_enabled"]
print("Config.json loaded.")

# Initialise
terminal = Terminal(IP=IP, sending_port=sending_port, waiting_time=terminal_waiting_time)
print("Terminal initialised.")
keyboard = Keyboard(IP=IP, listening_port=listening_port, sending_port=sending_port)
print("Keyboard initialised.")

keyboard.clear()
keyboard.serve()
print("Waiting for VIOS connection...")
while not keyboard.connected:
    time.sleep(0.5)
print("VIOS connected.")
print("Keyboard listening...")

terminal.cursor_to(7,20)
terminal.print("VIOS Initialising...".rjust(20))
terminal.clear(force=True)
terminal.enable()

def banner():
    msg = "VIOS (Virtual IO System)\n"
    msg += "Keyboard Test Utility Running\n"
    msg += 'Press "Sync" (the red button on the keyboard) to start'
    while 1:
        terminal.chatbox(msg)
    pass
if is_banner_enabled:
    Thread(target=banner, daemon=True).start()

_status = keyboard.getStatus()
while keyboard.connected:
    status = keyboard.getStatus()

    for i in status:
        if status[i] != _status[i]:
            print(f"Key change - {i}: {status[i]}")

    if status['scancode'] == 53: # Sync
        terminal.cursor_to(7,20)
        print("Resyncing...")
        terminal.print("Resyncing...".rjust(20))
        terminal.resync()
        print("Synced.")

    terminal.cursor_to(0)
    terminal.print("Keyboard Test Utility".center(40))
    terminal.cursor_to(2)
    terminal.print("Key Status:".center(40,'='))
    terminal.cursor_to(3)
    terminal.print(f"scancode: {status['scancode']} | keyname: {status['keyname']}".center(40))
    terminal.cursor_to(4)
    terminal.print(f"shift: {status['shift']} | ctrl: {status['ctrl']}".center(40))
    terminal.cursor_to(5)
    terminal.print(f"capslk: {status['capslk']} | fn: {status['fn']}".center(40))
    terminal.cursor_to(6)
    terminal.print(f"alt: {status['alt']}".center(40))
    terminal.cursor_to(7)
    terminal.print(f"".center(40,"="))
    time.sleep(0.1)

    _status = status.copy()

print("VIOS disconnected.")
terminal.disable()
