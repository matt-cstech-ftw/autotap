import time
import threading
import tkinter as tk
from tkinter import ttk
from pynput.keyboard import Key, Controller as KeyboardController, Listener
from pynput.mouse import Button, Controller as MouseController

# --- Defaults ---
DEFAULT_KEY = "l"
DEFAULT_KEY_CPS = 5.0
DEFAULT_MOUSE_CPS = 10.0
TOGGLE_KEY_HOTKEY = Key.f8
TOGGLE_MOUSE_HOTKEY = Key.f9
EXIT_KEY = Key.esc
# ----------------

keyboard = KeyboardController()
mouse = MouseController()

pressing_key = False
clicking_mouse = False
running = True
listener = None

root = tk.Tk()
root.title("Auto Tap")
root.geometry("380x440")
root.resizable(False, False)

key_var = tk.StringVar(value=DEFAULT_KEY)
key_rate_var = tk.StringVar(value=str(DEFAULT_KEY_CPS))
mouse_rate_var = tk.StringVar(value=str(DEFAULT_MOUSE_CPS))
key_status_var = tk.StringVar(value="Key (F8): OFF")
mouse_status_var = tk.StringVar(value="Mouse (F9): OFF")
error_var = tk.StringVar(value="")


def parse_rate(value_str, fallback):
    try:
        rate = float(value_str.strip())
        return rate if rate > 0 else fallback
    except ValueError:
        return fallback


def get_target_key():
    raw = key_var.get().strip().lower()
    if not raw:
        return DEFAULT_KEY
    return raw[0]


def set_key_state(state):
    global pressing_key
    pressing_key = state
    key_status_var.set(f"Key (F8): {'ON' if pressing_key else 'OFF'}")


def set_mouse_state(state):
    global clicking_mouse
    clicking_mouse = state
    mouse_status_var.set(f"Mouse (F9): {'ON' if clicking_mouse else 'OFF'}")


def toggle_key():
    set_key_state(not pressing_key)


def toggle_mouse():
    set_mouse_state(not clicking_mouse)


def stop_all():
    set_key_state(False)
    set_mouse_state(False)


def quit_app():
    global running, listener
    running = False
    set_key_state(False)
    set_mouse_state(False)
    if listener is not None:
        listener.stop()
    root.after(0, root.destroy)


def key_loop():
    while running:
        if pressing_key:
            rate = parse_rate(key_rate_var.get(), DEFAULT_KEY_CPS)
            target = get_target_key()
            try:
                keyboard.press(target)
                keyboard.release(target)
                root.after(0, lambda: error_var.set(""))
            except Exception as exc:
                root.after(0, lambda e=exc: error_var.set(f"Key error: {e}"))
                root.after(0, lambda: set_key_state(False))
            time.sleep(1.0 / rate)
        else:
            time.sleep(0.05)


def mouse_loop():
    while running:
        if clicking_mouse:
            rate = parse_rate(mouse_rate_var.get(), DEFAULT_MOUSE_CPS)
            mouse.click(Button.left, 1)
            time.sleep(1.0 / rate)
        else:
            time.sleep(0.05)


def on_press(key):
    if not running:
        return False
    if key == TOGGLE_KEY_HOTKEY:
        root.after(0, toggle_key)
    elif key == TOGGLE_MOUSE_HOTKEY:
        root.after(0, toggle_mouse)
    elif key == EXIT_KEY:
        root.after(0, quit_app)
        return False


# --- UI Layout ---
frame = ttk.Frame(root, padding=14)
frame.pack(fill="both", expand=True)
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)

ttk.Label(frame, text="Key to press:").grid(row=0, column=0, sticky="w", pady=3)
ttk.Entry(frame, textvariable=key_var, width=10).grid(row=0, column=1, sticky="e", pady=3)

ttk.Label(frame, text="Key presses / sec:").grid(row=1, column=0, sticky="w", pady=3)
ttk.Entry(frame, textvariable=key_rate_var, width=10).grid(row=1, column=1, sticky="e", pady=3)

ttk.Label(frame, text="Left clicks / sec:").grid(row=2, column=0, sticky="w", pady=3)
ttk.Entry(frame, textvariable=mouse_rate_var, width=10).grid(row=2, column=1, sticky="e", pady=3)

btn_row = ttk.Frame(frame)
btn_row.grid(row=3, column=0, columnspan=2, pady=(10, 6), sticky="ew")
ttk.Button(btn_row, text="Toggle Key (F8)", command=toggle_key).pack(side="left", expand=True, fill="x", padx=(0, 4))
ttk.Button(btn_row, text="Toggle Click (F9)", command=toggle_mouse).pack(side="left", expand=True, fill="x", padx=(4, 0))

ttk.Button(frame, text="Stop Both", command=stop_all).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 8))

status_row = ttk.Frame(frame)
status_row.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 6))
ttk.Label(status_row, textvariable=key_status_var).pack(side="left")
ttk.Label(status_row, textvariable=mouse_status_var).pack(side="right")

# --- Instructions Box ---
info_frame = ttk.LabelFrame(frame, text="How to Use (TikTok Live PC)", padding=8)
info_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(4, 6))

instructions_text = (
    "1. Click on your TikTok browser/app window so it is the active window.\n"
    "2. Press F8 to start/stop auto-pressing 'L' to send likes.\n"
    "3. Hover your mouse over the heart icon and press F9 for dual (high-speed) liking.\n"
    "4. Press Esc at any time to quit Auto Tap."
)
ttk.Label(info_frame, text=instructions_text, wraplength=330, justify="left").pack(anchor="w")

# --- Disclaimer ---
disclaimer_text = (
    "Disclaimer: Use at your own risk. We are not responsible if your account "
    "gets restricted or banned from liking lives on TikTok using this tool."
)
ttk.Label(
    frame,
    text=disclaimer_text,
    wraplength=350,
    justify="left",
    foreground="#b00020",
    font=("Segoe UI", 8)
).grid(row=7, column=0, columnspan=2, sticky="w", pady=(2, 4))

ttk.Label(frame, textvariable=error_var, foreground="red").grid(row=8, column=0, columnspan=2, sticky="w")

root.protocol("WM_DELETE_WINDOW", quit_app)

threading.Thread(target=key_loop, daemon=True).start()
threading.Thread(target=mouse_loop, daemon=True).start()

listener = Listener(on_press=on_press)
listener.start()

root.mainloop()