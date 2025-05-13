# AI Chatbot Utility
# In the working directory, you shold have a 'gemini_api_key.txt' where your gemini api key is.

from terminal import Terminal
from vkey import Keyboard
from simpleim import SimpleIM
import time

with open('gemini_api_key.txt', 'r', encoding="utf-8") as gemini_api_key:
    API_KEY = gemini_api_key.read()

