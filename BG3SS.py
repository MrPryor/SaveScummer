import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import time
from tkinter import messagebox

icon_path = 'C:\\Users\\Mr_Pryor\\Desktop\\Save Scummer\\bg3.ico'

class KeySenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BG3: Save Scummer")  # Change the window title here

        # Set the background color to #313338
        self.root.configure(bg='#313338')

        # Calculate the center position of the screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 300) // 2  # 300 is the width of the window
        y = (screen_height - 250) // 2  # 250 is the height of the window

        # Set the window size and position
        self.root.geometry("300x200+{}+{}".format(x, y))

        # Set the window icon
        self.root.iconbitmap(icon_path)

        # Create a custom style to match Discord's color scheme
        self.style = ttk.Style()
        self.style.configure('TLabel', foreground='#949B9A', background='#313338')  # Change label text color to #949B9A and background to #313338
        self.style.configure('TEntry', foreground='black', background='#2B2D31')  # Change text color to black and entry background to #2B2D31
        self.style.configure('TCombobox', foreground='black', background='#2C2F33')  # Change text color to black and combobox background to #2C2F33
        self.style.configure('TButton', foreground='black', background='#B5BAC1')  # Change text color to black and button background to #B5BAC1
        self.style.configure('TFrame', background='#1E1F22')  # Change the frame background color to #1E1F22
        self.style.configure('TNotebook', background='#1E1F22')  # Change the notebook background color to #1E1F22

        self.key_label = ttk.Label(root, text="Key", style='TLabel')
        self.key_label.pack()

        # Set the default key to "F5"
        self.key_entry = ttk.Entry(root, style='TEntry')
        self.key_entry.insert(0, "F5")
        self.key_entry.pack()

        self.key_set = False  # Flag to check if the key is set

        self.delay_label = ttk.Label(root, text="Delay", style='TLabel')
        self.delay_label.pack()

        # Set the default delay to "5"
        self.delay_var = tk.StringVar()
        vcmd = (self.root.register(self.validate_delay_input), "%P")
        self.delay_entry = ttk.Entry(root, style='TEntry', textvariable=self.delay_var, validate="key", validatecommand=vcmd)
        self.delay_entry.insert(0, "5")
        self.delay_entry.pack()

        # Set the default delay units to "Minutes"
        self.delay_units = tk.StringVar()
        self.delay_units.set("Minutes")

        self.delay_units_label = ttk.Label(root, text="Delay Units", style='TLabel')
        self.delay_units_label.pack()

        self.delay_units_combobox = ttk.Combobox(root, textvariable=self.delay_units, values=["Seconds", "Minutes"], state="readonly", style='TCombobox')
        self.delay_units_combobox.pack()

        self.countdown_label = ttk.Label(root, text="Countdown:", style='TLabel')
        self.countdown_label.pack()

        self.countdown_value = tk.StringVar()
        self.countdown_label_value = ttk.Label(root, textvariable=self.countdown_value, style='TLabel')
        self.countdown_label_value.pack()

        # Create a toggle button for start/stop
        self.start_button = ttk.Button(root, text="Start", command=self.toggle_countdown, style='TButton')
        self.start_button.pack()

        self.is_counting_down = False
        self.countdown_thread = None

        # Store the previous delay units
        self.prev_delay_units = "Minutes"

        # Counter for key presses
        self.key_press_count = 0
        self.key_press_label = ttk.Label(root, text="Saves: {}".format(self.key_press_count), style='TLabel')
        self.key_press_label.pack(side="bottom", anchor="se")

        # Bind a key press event to capture the key
        self.root.bind("<KeyPress>", self.capture_key_press)

    def validate_delay_input(self, input_text):
        # This function validates the input in the Delay entry field to allow only numbers and an empty string.
        return input_text == "" or input_text.isdigit()

    def toggle_countdown(self):
        if self.is_counting_down:
            self.stop_countdown()
        else:
            self.start_countdown()

    def start_countdown(self):
        if not self.is_counting_down:
            delay = float(self.delay_var.get())

            if delay <= 1:
                # Display an error message and return without starting the countdown
                messagebox.showerror("Error", "Delay must be greater than 1.")
                return

            self.is_counting_down = True
            self.start_button.config(text="Stop")
            if self.delay_units.get() == "Minutes":
                delay *= 60

            self.stop_countdown_event = threading.Event()

            def countdown(delay):
                original_delay = delay  # Store the original delay
                while not self.stop_countdown_event.is_set():
                    while delay > 0 and not self.stop_countdown_event.is_set():
                        self.countdown_value.set(f"{delay:.1f} seconds")
                        time.sleep(1)
                        delay -= 1
                    if not self.stop_countdown_event.is_set():
                        self.send_key()
                        delay = original_delay  # Reset the delay to the original value

                self.reset_countdown()

            self.countdown_thread = threading.Thread(target=countdown, args=(delay,))
            self.countdown_thread.start()

    def stop_countdown(self):
        if self.is_counting_down:
            self.stop_countdown_event.set()

    def send_key(self):
        key_to_send = self.key_entry.get()
        keyboard.press_and_release(key_to_send)
        self.key_press_count += 1
        self.key_press_label.config(text="Saves: {}".format(self.key_press_count))

    def reset_countdown(self):
        self.is_counting_down = False
        self.start_button.config(text="Start")
        self.countdown_value.set("")

        # Check if the countdown thread is not the current thread before attempting to join it
        if self.countdown_thread and self.countdown_thread != threading.current_thread():
            self.countdown_thread.join()

    def on_delay_units_change(self, *args):
        # Check if delay units have changed
        if self.delay_units.get() != self.prev_delay_units:
            self.prev_delay_units = self.delay_units.get()
            self.reset_countdown()  # Reset the countdown

    def capture_key_press(self, event):
        # This function captures the key press event and sets the key entry field to the pressed key.
        if not self.key_set:
            pressed_key = event.keysym
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, pressed_key)
            self.key_set = True

if __name__ == "__main__":
    root = tk.Tk()
    app = KeySenderApp(root)
    # Bind the delay units change event to the handler
    app.delay_units.trace_add("write", app.on_delay_units_change)
    root.mainloop()
