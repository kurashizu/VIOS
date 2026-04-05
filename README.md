# VIOS — Virtual IO System for VRChat

VIOS is a Python-based bridge that gives your VRChat avatar a functional keyboard and text display. It communicates with VRChat over OSC (Open Sound Control), reading key presses from avatar parameters and writing text to a TaSTT-compatible in-game display.

---

## Features

- **Terminal** — drive an 8×40 character in-game display via VRChat avatar parameters (TaSTT-compatible).
- **Keyboard** — receive key events (scancode, Shift, Ctrl, Alt, Fn, Caps Lock) from VRChat avatar parameters over OSC.
- **Simple Input Method** — a cursor-based text-entry canvas that combines the keyboard and terminal.
- **Keyboard Test Utility** (`kbtestutil`) — shows live key-status on the in-game display; useful for verifying your avatar setup.
- **AI Chatbot Utility** (`chatutil`) — type a message via the in-game keyboard, get an AI reply displayed on the terminal. Supports **Google Gemini** and local **Ollama** models.
- **Simulator** (`simulate.py`) — a local tkinter window that emulates the VRChat environment so you can develop and test without launching VRChat.

---

## Requirements

- Python 3.x
- [`python-osc`](https://pypi.org/project/python-osc/)
- [`requests`](https://pypi.org/project/requests/)
- `tkinter` (included with most Python distributions; required by the simulator only)
- A VRChat avatar with the **TaSTT** text display and keyboard parameter setup, **or** the included simulator

For the AI chatbot:
- A [Google Gemini API key](https://aistudio.google.com/), **or**
- A running [Ollama](https://ollama.com/) instance with your chosen model (e.g. `gemma3:4b`)

Install Python dependencies:

```bash
pip install python-osc requests
```

---

## Configuration

All settings live in `config.json`.

### `kbtestutil_config`

| Key | Default | Description |
|-----|---------|-------------|
| `IP` | `"127.0.0.1"` | IP address where VRChat is running |
| `sending_port` | `9000` | OSC port VIOS sends to (VRChat's OSC receive port) |
| `listening_port` | `9001` | OSC port VIOS listens on (VRChat's OSC send port) |
| `terminal.waiting_time` | `0.25` | Seconds to wait between terminal cache writes |
| `is_banner_enabled` | `false` | Show a chatbox banner message on startup |

### `chatutil_config`

| Key | Default | Description |
|-----|---------|-------------|
| `model_type` | `"ollama"` | AI backend: `"ollama"` or `"gemini"` |
| `gemini_api_key` | `""` | Gemini API key (required when `model_type` is `"gemini"`) |
| `ollama_model_name` | `"gemma3:4b"` | Ollama model to use |
| `ollama_IP` | `"127.0.0.1"` | IP where Ollama is running |
| `ollama_port` | `11434` | Ollama API port |
| `ollama_context_length` | `1` | Number of previous turns kept in context |
| `prompt` | *(see file)* | Prompt template; use `{user_input}` as the placeholder |
| `VIOS_IP` | `"127.0.0.1"` | VRChat OSC IP |
| `VIOS_sending_port` | `9000` | OSC send port |
| `VIOS_listening_port` | `9001` | OSC listen port |
| `VIOS_Terminal.waiting_time` | `0.25` | Terminal write delay |
| `is_banner_enabled` | `false` | Show chatbox banner |
| `banner_message` | *(see file)* | Chatbox banner text |

---

## Usage

### Simulator (no VRChat needed)

Run the simulator to open a local window that acts as the VRChat environment:

```bash
python simulate.py
```

The simulator listens on port `9000` and sends key events to port `9001`, matching the default config. Your physical keyboard is mapped to VRChat scancodes. Modifier keys (Shift, Alt, Win/Super → Fn, Caps Lock, Ctrl) toggle on each press.

### Keyboard Test Utility

```bash
python kbtestutil.py
```

Connects to VRChat (or the simulator), then continuously displays the current key status on the in-game terminal. Press the **Sync** key (`` ` `` / grave in the simulator) at any time to force a full terminal refresh.

### AI Chatbot Utility

1. Edit `config.json` to select your AI model and set any required API keys.
2. Run:

   ```bash
   python chatutil.py
   ```

3. Once connected, type your message using the in-game keyboard and press **Enter** to send. The AI response is displayed on the terminal.
4. Press **Esc** at the input prompt to cancel.
5. Type `/h` and press **Enter** to display the help screen.

---

## In-game Keyboard Controls

| Key / Combo | Action |
|-------------|--------|
| Any printable key | Type the character at the cursor |
| **Shift** + key | Type the shifted character |
| **Caps Lock** | Toggle uppercase for letter keys |
| **Fn + W / A / S / D** | Move cursor up / left / down / right |
| **Backspace** | Delete the character before the cursor |
| **Enter** | Confirm / submit input |
| **Esc** | Cancel / exit input |
| **Sync** (`` ` ``) | Force a full terminal refresh |

---

## Building Standalone Executables

PyInstaller spec files are provided for `kbtestutil` and `chatutil`:

```bash
pyinstaller kbtestutil.spec
pyinstaller chatutil.spec
```

The resulting executables are placed in the `dist/` directory. Copy `config.json` to the same folder as the executable before running.

---

## Project Structure

```
VIOS/
├── config.json        # Configuration for all utilities
├── vkey.py            # Keyboard class — OSC-based key event receiver
├── terminal.py        # Terminal class — OSC-based TaSTT display driver
├── simpleim.py        # Simple Input Method using Keyboard + Terminal
├── kbtestutil.py      # Keyboard Test Utility (entry point)
├── chatutil.py        # AI Chatbot Utility (entry point)
├── simulate.py        # Local VRChat environment simulator (tkinter)
├── kbtestutil.spec    # PyInstaller spec for kbtestutil
└── chatutil.spec      # PyInstaller spec for chatutil
```

---

## OSC Communication

VIOS uses the [VRChat OSC API](https://docs.vrchat.com/docs/osc-overview).

| Direction | Address pattern | Purpose |
|-----------|----------------|---------|
| VRChat → VIOS | `/avatar/parameters/Key/Output/Int` | Current key scancode |
| VRChat → VIOS | `/avatar/parameters/Key/Output/Shift` | Shift state |
| VRChat → VIOS | `/avatar/parameters/Key/Output/Ctrl` | Ctrl state |
| VRChat → VIOS | `/avatar/parameters/Key/Output/Alt` | Alt state |
| VRChat → VIOS | `/avatar/parameters/Key/Output/Caps` | Caps Lock state |
| VRChat → VIOS | `/avatar/parameters/Key/Output/Fn` | Fn state |
| VRChat → VIOS | `/avatar/parameters/Heartbeat` | Connection heartbeat |
| VIOS → VRChat | `/avatar/parameters/TaSTT_Select` | Display cache region |
| VIOS → VRChat | `/avatar/parameters/TaSTT_L##B0_Blend` | Character blend value |
| VIOS → VRChat | `/avatar/parameters/TaSTT_Enable` | Enable/disable display |
| VIOS → VRChat | `/chatbox/input` | VRChat chatbox message |
