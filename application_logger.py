# -*- coding: utf-8 -*-

"""
Author: Menny Levinski

Exmple module for application logging.
"""

import io
import sys
import tkinter as tk
from datetime import datetime
import traceback

class AutoLoggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Full TK Logger")

        # --- Tkinter console ---
        self.console_output = tk.Text(root, height=20, width=80, state="normal")
        self.console_output.pack(padx=10, pady=10)
        self.console_output.focus_set()  # ready to type

        # --- Control buttons ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Pause Logging", command=self.stop_wrap_console_logging).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Resume Logging", command=self.resume_wrap_console_logging).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Save Log to File", command=self.save_log_to_file).pack(side="left", padx=5)

        # --- Start logging ---
        self._idle_log_file = self.start_idle_logging()
        self._wrap_console_enabled = True

        # --- Log typing, pastes, and edits ---
        self.console_output.bind("<KeyRelease>", self.log_user_typing)
        self.console_output.bind("<<Paste>>", self.log_paste)

        # --- Automatic startup log ---
        self.console_output.insert("end", f"Application started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print("Typing are logged automatically.\n")

    # --- Capture terminal stdout/stderr ---
    def start_idle_logging(self):
        log_buffer = io.StringIO()
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr

        class TeeStream:
            def __init__(self, *streams):
                self.streams = streams
            def write(self, data):
                for s in self.streams:
                    try:
                        s.write(data)
                        s.flush()
                    except Exception:
                        pass
            def flush(self):
                for s in self.streams:
                    try:
                        s.flush()
                    except Exception:
                        pass

        sys.stdout = TeeStream(orig_stdout, log_buffer)
        sys.stderr = TeeStream(orig_stderr, log_buffer)

        def log_exceptions(exc_type, exc_value, exc_traceback):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=log_buffer)

        sys.excepthook = log_exceptions
        print(f"Program log started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return log_buffer

    # --- Log keypresses ---
    def log_user_typing(self, event):
        if self._wrap_console_enabled and self._idle_log_file:
            char = event.char
            if char == "":
                # Handle special keys
                if event.keysym == "Return":
                    char = "\n"
                elif event.keysym == "Tab":
                    char = "\t"
                elif event.keysym == "BackSpace":
                    char = "<BACKSPACE>"
                else:
                    return
            self._idle_log_file.write(char)
            self._idle_log_file.flush()

    # --- Log paste events ---
    def log_paste(self, event):
        if self._wrap_console_enabled and self._idle_log_file:
            try:
                pasted = self.root.clipboard_get()
                self._idle_log_file.write(pasted)
                self._idle_log_file.flush()
            except Exception:
                pass

    # --- Pause/resume logging ---
    def stop_wrap_console_logging(self):
        self._wrap_console_enabled = False
        print("Console logging paused.")

    def resume_wrap_console_logging(self):
        self._wrap_console_enabled = True
        print("Console logging resumed.")

    # --- Save log to file ---
    def save_log_to_file(self):
        filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self._idle_log_file.getvalue())
        print(f"Log saved to {filename}")

# --- Run the app ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoLoggerApp(root)
    root.mainloop()
