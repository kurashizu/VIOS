# AI Chatbot Utility
# Make sure you have read config.json carefully before run this script

from terminal import Terminal
from vkey import Keyboard
from simpleim import SimpleIM
import time
import requests
from threading import Thread
import os
import json

class Gemini():
    def __init__(self, API_KEY: str):
        self.API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
        self.headers = {"Content-Type": "application/json"}

    def chat(self, prompt: str):
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(self.API_URL, headers=self.headers, json=data)
        if response.status_code == 200:
            reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return reply
        else:
            return f"Error {response.status_code}: {response.text}"

class Ollama():
    def __init__(self,
                 model_name: str,
                 IP='127.0.0.1',
                 port=11434,
                 context_length=1):
        
        self.chat_history = []
        self.context_length = context_length
        self.model = model_name
        self.IP = IP
        self.port = port
        pass

    def chat(self, prompt: str, image=None):
        chat = {
            'role': 'user', 
            'content': prompt,
            }
        if image:
            chat['images'] = [image]
        self.chat_history.append(chat)

        self.chat_history = self.chat_history[-self.context_length:]

        response = requests.post(
            f'http://{self.IP}:{self.port}/api/chat',
            json={
                'model': self.model,
                'messages': self.chat_history,
                'stream': False,
            }
        )

        reply = response.json()['message']['content']
        self.chat_history.append({'role': 'assistant', 'content': reply})

        return reply
    
if __name__ == "__main__":
    
    # load config
    print("Loading config.json ...")
    with open('config.json', 'r', encoding="utf-8") as config:
        cfg = json.load(config)["chatutil_config"]
    
    if cfg["model_type"] == "ollama":
        chatbot = Ollama(model_name=cfg["ollama_model_name"], IP=cfg["ollama_IP"], port=cfg["ollama_port"], context_length=cfg["ollama_context_length"])
        pass
    elif cfg["model_type"] == "gemini":
        chatbot = Gemini(API_KEY=cfg["gemini_api_key"])
        pass
    else:
        print("No valid model_type specified")
        os._exit()
    
    terminal = Terminal(IP=cfg["VIOS_IP"], sending_port=cfg["VIOS_sending_port"], waiting_time=cfg["VIOS_Terminal"]["waiting_time"])
    keyboard = Keyboard(IP=cfg["VIOS_IP"], listening_port=cfg["VIOS_listening_port"], sending_port=cfg["VIOS_sending_port"])
    simpleim = SimpleIM(keyboard, terminal)
    IS_BANNER_ENABLED = cfg["is_banner_enabled"]

    print("config.json loaded.")
    # config loaded

    keyboard.serve()
    keyboard.clear()
    print("Waiting for VIOS connection...")
    while not keyboard.connected:
        time.sleep(0.5)
    print("VIOS connected.")
    print("Keyboard listening...")

    def sync_daemon():
        while keyboard.connected:
            status = keyboard.getStatus()
            if status['scancode'] == 53: # Sync
                print("Resyncing...")
                terminal.resync()
                print("Synced.")
            time.sleep(0.1)
        print("VIOS disconnected.")
        terminal.disable()
        os._exit(0)
    Thread(target=sync_daemon, daemon=True).start()

    def banner():
            msg = "VIOS (Virtual IO System)\n"
            msg += "Chatbot Utility Running\n"
            # msg += 'Press "Sync" (the red button on the keyboard) to start\n'
            msg += '首先点击键盘左上角的Sync键(红色)进行同步，然后在输入框里输入文本，输入完后按Enter键获取AI回复。'
            while 1:
                terminal.chatbox(msg)
            pass
    if IS_BANNER_ENABLED:
        Thread(target=banner, daemon=True).start()

    terminal.enable()
    terminal.cursor_to(7,20)
    terminal.print("VIOS Initialising...".rjust(20))
    terminal.clear(force=True)
    
    while keyboard.connected:
        terminal.cursor_to(0, 0)
        terminal.print("VIOS Chatbot <Type '/h' for help>".center(40,' '))
        terminal.print(" ")
        terminal.print(" ")
        terminal.print(" ")

        user_input = simpleim.input(offset=(4,0), size=(4,40))
        print(f"Got user input: {user_input}")

        if user_input == '/h':
            user_outputs = []
            user_outputs.append("This is a AI chatbot utility. You can type via the keyboard, then press Enter to get response.")
            user_outputs.append("NB: Press Fn+w/a/s/d so you can move the cursor around!")
            user_outputs.append(" ")
            user_outputs.append("https://github.com/kurashizu/VIOS".rjust(40))
            terminal.cursor_to(0, 0)
            for msg in user_outputs:
                terminal.print(msg)
            terminal.cursor_to(7, 0)
            terminal.print("Press Esc to Continue".center(40,'-'))
            keyboard.waitKey(41) # wait for Esc
            continue

        prompt = f'Your name is VIOS standing for Virtual IO System. You are gonna receive message from a user \
            who are talking to you. You should make a short response less than 300 letters in total. \
            And remember you can respond in English with only ASCII characters! \
            But you can understand 拼音 if the user send you. \
            The user is saying : "{user_input}"'
        
        terminal.cursor_to(0, 0)
        terminal.print("VIOS Thinking".center(40,'-'))
        response = chatbot.chat(prompt=prompt)
        user_output = f"VIOS: {response}".ljust(160-6)
        
        print(user_output)
        terminal.cursor_to(0, 0)
        terminal.print(user_output)
        terminal.cursor_to(7, 0)
        terminal.print("Press Enter to Continue...".center(40,'-'))

        keyboard.waitKey(40) # wait for Enter
