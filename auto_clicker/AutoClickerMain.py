import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading, time
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Listener
import sys, os, tempfile, shutil

mouse = MouseController()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto clicker - Joar edition")
        self.root.geometry("480x380")

        temp_icon_path = os.path.join(tempfile.gettempdir(), "taskbar.ico")
        shutil.copy(resource_path("assets/images/taskbar.ico"), temp_icon_path)
        self.root.iconbitmap(temp_icon_path)

        self.is_running = False
        self.click_delay = 1.0
        self.hotkey = "f2"

        # Speed chooser
        tk.Label(root, text="Speed:").pack()
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_dropdown = ttk.Combobox(root, textvariable=self.speed_var)
        self.speed_dropdown['values'] = [1, 0.75, 0.5, 0.25, 0.1, 0.05, 0.025, 0.005, 0.0005, 0.0001]
        self.speed_dropdown.pack()

        # Hotkey chooser
        tk.Label(root, text="hotkey: ").pack()
        self.key_var = tk.StringVar(value="f2")
        self.key_dropdown = ttk.Combobox(root, textvariable=self.key_var)
        self.key_dropdown['values'] = ["f8", "f6", "f4", "f2", "§"]
        self.key_dropdown.pack()

        # Button frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # Start button
        self.start_button = tk.Button(button_frame, text="Start autoclicker", command=self.start_clicking)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        # Image in middle
        img = Image.open(resource_path("assets/images/mouse.jpg"))
        img = img.rotate(-90, expand=True)
        img.thumbnail((220, 220))
        self.logo = ImageTk.PhotoImage(img)
        self.logo_label = tk.Label(button_frame, image=self.logo)
        self.logo_label.grid(row=0, column=1, padx=10)

        # Stop button
        self.stop_button = tk.Button(button_frame, text="Stop autoclicker", command=self.stop_clicking)
        self.stop_button.grid(row=0, column=2, padx=5, pady=5)

        # Status label
        self.status_label = tk.Label(root, text="OFF")
        self.status_label.pack(pady=5)

        # Menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        info_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Info", menu=info_menu)
        info_menu.add_command(label="About", command=self.show_about)

        # Hotkey listener
        listener = Listener(on_press=self.on_key_press)
        listener.daemon = True
        listener.start()

    def click_loop(self):
        while self.is_running:
            mouse.click(Button.left)
            time.sleep(self.click_delay)

    def start_clicking(self):
        if not self.is_running:
            self.is_running = True
            self.click_delay = float(self.speed_var.get())
            self.hotkey = self.key_var.get().lower()
            self.status_label.config(text="ON")
            threading.Thread(target=self.click_loop, daemon=True).start()

    def stop_clicking(self):
        self.is_running = False
        self.status_label.config(text="OFF")

    def on_key_press(self, key):
        try:
            if key.char == self.hotkey:
                self.toggle()
        except AttributeError:
            if hasattr(key, "name") and key.name == self.hotkey:
                self.toggle()

    def toggle(self):
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def show_about(self):
        messagebox.showinfo("About", "Autoclicker - Joar edition\nVersion 1.0")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()
