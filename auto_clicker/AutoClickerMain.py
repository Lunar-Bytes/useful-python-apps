import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from PIL import Image, ImageTk
import threading, time, sys, os, tempfile, shutil, json
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Listener

mouse = MouseController()

# ---- Helpers ----
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_theme():
    path = resource_path("theme.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_theme(themes):
    path = resource_path("theme.json")
    with open(path, "w") as f:
        json.dump(themes, f, indent=4)

# ---- AutoClicker class ----
class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto clicker - Joar edition")
        self.root.geometry("520x500")
        root.resizable(False, False)

        # ---- Icon ----
        temp_icon_path = os.path.join(tempfile.gettempdir(), "taskbar.ico")
        shutil.copy(resource_path("assets/images/taskbar.ico"), temp_icon_path)
        self.root.iconbitmap(temp_icon_path)

        # ---- State ----
        self.is_running = False
        self.click_delay = 1.0
        self.hotkey = "f2"

        self.themes = load_theme()
        if "default" not in self.themes:
            self.themes["default"] = {
                "background": "#ffffff",
                "foreground": "#000000",
                "button_bg": "#e0e0e0",
                "button_fg": "#000000",
                "status_fg": "#000000",
                "controls_background": "#d0d0d0",
                "controls_foreground": "#000000",
                "controls_wallpaper": "#ffffff"
            }
        if "dark_mode" not in self.themes:
            self.themes["dark_mode"] = {
                "background": "#1e1e1e",
                "foreground": "#f0f0f0",
                "button_bg": "#333333",
                "button_fg": "#f0f0f0",
                "status_fg": "#f0f0f0",
                "controls_background": "#2a2a2a",
                "controls_foreground": "#f0f0f0",
                "controls_wallpaper": "#2a2a2a"
            }

        self.theme_name = "default"
        self.theme = self.themes[self.theme_name]

        # ---- Speed chooser ----
        tk.Label(root, text="Speed:", bg=self.theme["background"], fg=self.theme["foreground"]).pack()
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_dropdown = ttk.Combobox(root, textvariable=self.speed_var)
        self.speed_dropdown['values'] = [1, 0.75, 0.5, 0.25, 0.1, 0.05, 0.025, 0.005, 0.0005, 0.0001]
        self.speed_dropdown.pack()

        # ---- Hotkey chooser ----
        tk.Label(root, text="hotkey: ", bg=self.theme["background"], fg=self.theme["foreground"]).pack()
        self.key_var = tk.StringVar(value="f2")
        self.key_dropdown = ttk.Combobox(root, textvariable=self.key_var)
        self.key_dropdown['values'] = ["f8", "f6", "f4", "f2", "§"]
        self.key_dropdown.pack()

        # ---- Button frame ----
        self.button_frame = tk.Frame(root, bg=self.theme["controls_wallpaper"])
        self.button_frame.pack(pady=10, fill="x")

        # ---- Buttons ----
        self.start_button = tk.Button(self.button_frame, text="Start autoclicker", command=self.start_clicking,
                                      bg=self.theme["button_bg"], fg=self.theme["button_fg"])
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        # Middle image
        img = Image.open(resource_path("assets/images/mouse.jpg"))
        img = img.rotate(-90, expand=True)
        img.thumbnail((220, 220))
        self.logo = ImageTk.PhotoImage(img)
        self.logo_label = tk.Label(self.button_frame, image=self.logo, bg=self.theme["controls_wallpaper"])
        self.logo_label.grid(row=0, column=1, padx=10)

        self.stop_button = tk.Button(self.button_frame, text="Stop autoclicker", command=self.stop_clicking,
                                     bg=self.theme["button_bg"], fg=self.theme["button_fg"])
        self.stop_button.grid(row=0, column=2, padx=5, pady=5)

        # Cursor vibration toggle
        self.vibrate_button = tk.Button(root, text="Cursor vibration", command=self.toggle_vibration,
                                        bg=self.theme["button_bg"], fg=self.theme["button_fg"])
        self.vibrate_button.pack(pady=5)

        # Theme switch button
        self.theme_button = tk.Button(root, text="Dark Mode", command=self.switch_dark_mode,
                                      bg=self.theme["button_bg"], fg=self.theme["button_fg"])
        self.theme_button.pack(pady=5)

        # Status label
        self.status_label = tk.Label(root, text="OFF", bg=self.theme["background"], fg=self.theme["status_fg"])
        self.status_label.pack(pady=5)

        # ---- Menu bar ----
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        info_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Info", menu=info_menu)
        info_menu.add_command(label="About", command=self.show_about)
        info_menu.add_command(label="Customization", command=self.open_customization)

        # ---- Hotkey listener ----
        listener = Listener(on_press=self.on_key_press)
        listener.daemon = True
        listener.start()

        # ---- Cursor vibration ----
        self.vibrate_on = False
        self.vibration_thread = None

    # ---- Click loop ----
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
            if self.vibrate_on and self.vibration_thread is None:
                self.vibration_thread = threading.Thread(target=self.cursor_vibration, daemon=True)
                self.vibration_thread.start()

    def stop_clicking(self):
        self.is_running = False
        self.status_label.config(text="OFF")
        self.vibration_thread = None

    # ---- Hotkey toggle ----
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

    # ---- About ----
    def show_about(self):
        messagebox.showinfo("About", "Autoclicker - Joar edition\nVersion 1.0")

    # ---- Cursor vibration ----
    def toggle_vibration(self):
        self.vibrate_on = not self.vibrate_on
        if self.vibrate_on and self.is_running:
            self.vibration_thread = threading.Thread(target=self.cursor_vibration, daemon=True)
            self.vibration_thread.start()

    def cursor_vibration(self):
        direction = 1
        while self.is_running and self.vibrate_on:
            x, y = mouse.position
            dx = 5 if direction == 1 else -5
            dy = 5 if direction == 1 else -5
            mouse.position = (x + dx, y + dy)
            direction *= -1
            time.sleep(0.1)

    # ---- Dark Mode ----
    def switch_dark_mode(self):
        self.theme_name = "dark_mode" if self.theme_name != "dark_mode" else "default"
        self.theme = self.themes[self.theme_name]
        self.apply_theme()

    # ---- Apply theme to UI ----
    def apply_theme(self):
        self.root.configure(bg=self.theme["background"])
        self.status_label.configure(bg=self.theme["background"], fg=self.theme["status_fg"])
        self.button_frame.configure(bg=self.theme["controls_wallpaper"])
        self.logo_label.configure(bg=self.theme["controls_wallpaper"])
        self.start_button.configure(bg=self.theme["button_bg"], fg=self.theme["button_fg"])
        self.stop_button.configure(bg=self.theme["button_bg"], fg=self.theme["button_fg"])
        self.vibrate_button.configure(bg=self.theme["button_bg"], fg=self.theme["button_fg"])
        self.theme_button.configure(bg=self.theme["button_bg"], fg=self.theme["button_fg"])

    # ---- Customization GUI ----
    def open_customization(self):
        win = tk.Toplevel(self.root)
        win.title("Customization")
        win.geometry("400x400")
        win.configure(bg=self.theme["background"])

        colors = [
            ("Background", "background"),
            ("Foreground", "foreground"),
            ("Button BG", "button_bg"),
            ("Button FG", "button_fg"),
            ("Status FG", "status_fg"),
            ("Controls BG", "controls_background"),
            ("Controls FG", "controls_foreground"),
            ("Controls Wallpaper", "controls_wallpaper")
        ]

        entries = {}

        def pick_color(key):
            color = colorchooser.askcolor(title=f"Choose {key}")[1]
            if color:
                self.theme[key] = color
                apply_preview()

        def apply_preview():
            self.apply_theme()

        row = 0
        for label, key in colors:
            tk.Label(win, text=label, bg=self.theme["background"], fg=self.theme["foreground"]).grid(row=row, column=0, padx=5, pady=5, sticky="w")
            btn = tk.Button(win, text="Pick", bg=self.theme["button_bg"], fg=self.theme["button_fg"], command=lambda k=key: pick_color(k))
            btn.grid(row=row, column=1, padx=5, pady=5)
            entries[key] = btn
            row += 1

        def apply_changes():
            self.themes[self.theme_name] = self.theme
            save_theme(self.themes)
            win.destroy()

        def reset_default():
            self.theme_name = "default"
            self.theme = self.themes[self.theme_name]
            self.apply_theme()

        def rak_mode():
            self.theme_name = "dark_mode"
            self.theme = self.themes[self.theme_name]
            self.apply_theme()

        tk.Button(win, text="Apply", bg=self.theme["button_bg"], fg=self.theme["button_fg"], command=apply_changes).grid(row=row, column=0, pady=10)
        tk.Button(win, text="Default", bg=self.theme["button_bg"], fg=self.theme["button_fg"], command=reset_default).grid(row=row, column=1, pady=10)
        tk.Button(win, text="Dark Mode", bg=self.theme["button_bg"], fg=self.theme["button_fg"], command=rak_mode).grid(row=row+1, column=0, columnspan=2, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()
