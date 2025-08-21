import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
import time
import threading
import winsound
from datetime import datetime
import os
import sys

class PomodoroTimerWithHistory:
    def __init__(self, root):
        # Determine application directory (works in development and when frozen with PyInstaller)
        if getattr(sys, 'frozen', False):
            # If the app is frozen, use the executable directory
            app_dir = os.path.dirname(sys.executable)
        else:
            # Otherwise use this script's directory
            app_dir = os.path.dirname(os.path.abspath(__file__))
        # Ensure the directory exists
        os.makedirs(app_dir, exist_ok=True)

        # Path to history file, stored alongside the app
        self.history_file = os.path.join(app_dir, "pomodoro_history.txt")

        # Root window setup
        self.root = root
        self.root.title("Pomodoro Timer with History")
        self.root.geometry("420x580")
        self.root.resizable(False, False)
        self.bg_color = "#FFFFFF"
        self.text_color = "#111111"
        self.accent_color = "#111111"
        self.root.configure(bg=self.bg_color)

        # Fonts
        self.font_family = "Segoe UI" if "Segoe UI" in tkfont.families() else "Helvetica"

        # Timer settings
        self.work_minutes = 25
        self.short_break_minutes = 5
        self.long_break_minutes = 15
        self.remaining_seconds = self.work_minutes * 60
        self.current_mode = "Work"     # "Work", "Short Break", "Long Break"
        self.timer_running = False
        self._last_tick = None

        # Pomodoro count
        self.pomodoro_count = 0
        self.max_pomodoros = 4

        # Daily history
        self.today_work_seconds = 0
        self.today_break_seconds = 0
        self.daily_goal_minutes = 120

        # Load or initialize history
        self.load_daily_history()

        # Build UI
        self.create_header()
        self.create_stats_and_goal_frame()
        self.create_timer_frame()
        self.create_mode_control_frame()
        self.create_buttons_frame()
        self.create_session_tracker()
        self.create_quote_frame()

        # Update loops
        self.update_clock()
        self.update_stats_and_goal()

        # Save on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    #
    # History persistence
    #
    def load_daily_history(self):
        """Load today's history from file if present, including daily goal."""
        today = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 4:
                        date, work, brk, goal = parts
                    elif len(parts) == 3:
                        date, work, brk = parts
                        goal = None
                    else:
                        continue
                    if date == today:
                        self.today_work_seconds = int(work)
                        self.today_break_seconds = int(brk)
                        if goal is not None:
                            self.daily_goal_minutes = int(goal)
                        return

    def save_daily_history(self):
        """Write today's work/break seconds and daily goal back to history file."""
        today = datetime.now().strftime("%Y-%m-%d")
        lines = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                lines = f.readlines()

        updated = False
        with open(self.history_file, "w") as f:
            for line in lines:
                if line.startswith(today + ","):
                    # Replace today's line with updated values (including goal)
                    f.write(f"{today},{self.today_work_seconds},{self.today_break_seconds},{self.daily_goal_minutes}\n")
                    updated = True
                else:
                    f.write(line)
            if not updated:
                f.write(f"{today},{self.today_work_seconds},{self.today_break_seconds},{self.daily_goal_minutes}\n")

    def view_full_history(self):
        """Show a popup listing all saved history."""
        if not os.path.exists(self.history_file):
            messagebox.showinfo("History", "No history file found.")
            return

        with open(self.history_file, "r") as f:
            entries = [line.strip().split(",") for line in f if line.strip()]

        # Build display text
        header = "Date       | Work (min) | Break (min) | Goal (min)\n"
        divider = "-" * 45 + "\n"
        body = ""
        for parts in entries:
            if len(parts) == 4:
                date, work, brk, goal = parts
            elif len(parts) == 3:
                date, work, brk = parts
                goal = "-"
            else:
                continue
            work_min = int(work) // 60
            break_min = int(brk) // 60
            body += f"{date} | {work_min:>10} | {break_min:>11} | {goal:>9}\n"

        # Show history in a popup window
        win = tk.Toplevel(self.root)
        win.title("Full Pomodoro History")
        txt = tk.Text(win, wrap="none", font=(self.font_family, 10))
        txt.insert("1.0", header + divider + body)
        txt.config(state="disabled")  # Read-only
        txt.pack(fill="both", expand=True, padx=10, pady=10)

    #
    # UI Creation
    #
    def create_header(self):
        frame = tk.Frame(self.root, bg=self.bg_color, pady=15)
        frame.pack(fill="x")
        lbl = tk.Label(frame,
            text="Pomodoro Timer",
            font=(self.font_family, 22, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        lbl.pack()
        self.mode_label = tk.Label(frame,
            text=f"Mode: {self.current_mode}",
            font=(self.font_family, 12),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.mode_label.pack(pady=(5,0))

    def create_stats_and_goal_frame(self):
        frame = tk.Frame(self.root, bg=self.bg_color, pady=5)
        frame.pack(fill="x")
        self.history_label = tk.Label(frame,
            text=self.get_history_text(),
            font=(self.font_family, 10),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.history_label.pack(side="left", padx=10)
        self.goal_label = tk.Label(frame,
            text=self.get_goal_text(),
            font=(self.font_family, 10),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.goal_label.pack(side="right", padx=10)

        btn = tk.Button(frame,
            text="View History",
            font=(self.font_family, 10),
            command=self.view_full_history,
            bg=self.bg_color, fg=self.accent_color
        )
        btn.pack(side="bottom", pady=5)

    def get_history_text(self):
        w = self.today_work_seconds // 60
        b = self.today_break_seconds // 60
        return f"Today: Work {w}m | Break {b}m"

    def get_goal_text(self):
        done = self.today_work_seconds // 60
        return f"Goal: {done}/{self.daily_goal_minutes} min"

    def update_stats_and_goal(self):
        self.history_label.config(text=self.get_history_text())
        self.goal_label.config(text=self.get_goal_text())
        self.root.after(30000, self.update_stats_and_goal)

    def create_timer_frame(self):
        frame = tk.Frame(self.root, bg=self.bg_color, pady=10)
        frame.pack()
        font = (self.font_family, 54, "bold")
        self.time_display = tk.Label(frame,
            text=self.format_time(self.remaining_seconds),
            font=font,
            fg=self.accent_color,
            bg=self.bg_color
        )
        self.time_display.pack()

    def create_mode_control_frame(self):
        frame = tk.Frame(self.root, bg=self.bg_color, pady=5)
        frame.pack(fill="x")
        opts = ["Work", "Short Break", "Long Break"]
        self.mode_var = tk.StringVar(value=self.current_mode)
        om = tk.OptionMenu(frame, self.mode_var, *opts, command=self.on_mode_change)
        om.config(font=(self.font_family, 10))
        om.pack(side="left", padx=10)

        lbl = tk.Label(frame,
            text="Daily Goal:",
            font=(self.font_family, 10),
            bg=self.bg_color, fg=self.text_color
        )
        lbl.pack(side="left", padx=(20,5))
        self.goal_entry = tk.Entry(frame,
            width=4, font=(self.font_family, 10), justify="center"
        )
        self.goal_entry.insert(0, str(self.daily_goal_minutes))
        self.goal_entry.pack(side="left")
        self.goal_entry.bind("<Return>", self.on_goal_change)

    def on_mode_change(self, mode):
        self.current_mode = mode
        self.mode_label.config(text=f"Mode: {mode}")
        if mode == "Work":
            self.remaining_seconds = self.work_minutes * 60
        elif mode == "Short Break":
            self.remaining_seconds = self.short_break_minutes * 60
        else:
            self.remaining_seconds = self.long_break_minutes * 60
        self.update_timer_display()

    def on_goal_change(self, event=None):
        try:
            val = int(self.goal_entry.get())
            if val > 0:
                self.daily_goal_minutes = val
                self.update_stats_and_goal()
                self.save_daily_history()  # Save goal change immediately
        except ValueError:
            pass

    def create_buttons_frame(self):
        frame = tk.Frame(self.root, bg=self.bg_color, pady=10)
        frame.pack()
        self.start_btn = tk.Button(frame,
            text="Start", font=(self.font_family, 12),
            command=self.start_timer,
            bg=self.bg_color, fg=self.accent_color
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        self.pause_btn = tk.Button(frame,
            text="Pause", font=(self.font_family, 12),
            command=self.pause_timer, state="disabled",
            bg=self.bg_color, fg=self.accent_color
        )
        self.pause_btn.grid(row=0, column=1, padx=5)
        self.reset_btn = tk.Button(frame,
            text="Reset", font=(self.font_family, 12),
            command=self.reset_timer,
            bg=self.bg_color, fg=self.accent_color
        )
        self.reset_btn.grid(row=0, column=2, padx=5)

    def create_session_tracker(self):
        frame = tk.Frame(self.root, bg=self.bg_color, pady=5)
        frame.pack()
        self.session_label = tk.Label(frame,
            text="Pomodoros Completed: 0",
            font=(self.font_family, 11),
            fg=self.text_color, bg=self.bg_color
        )
        self.session_label.pack()

    def create_quote_frame(self):
        frame = tk.Frame(self.root, bg=self.bg_color, pady=10)
        frame.pack(fill="x")
        quote = '"The brain is like a muscle. When it is in use, we feel good." - Jim Kwik'
        lbl = tk.Label(frame,
            text=quote, wraplength=350,
            font=(self.font_family, 10, "italic"),
            fg=self.text_color, bg=self.bg_color
        )
        lbl.pack()

    #
    # Timer logic
    #
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self._last_tick = time.time()
            threading.Thread(target=self.run_timer, daemon=True).start()

    def pause_timer(self):
        self.timer_running = False
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")

    def reset_timer(self):
        self.timer_running = False
        self.remaining_seconds = self.work_minutes * 60
        self.update_timer_display()
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")

    def run_timer(self):
        while self.timer_running and self.remaining_seconds > 0:
            now = time.time()
            elapsed = int(now - self._last_tick)
            if elapsed > 0:
                self.remaining_seconds -= elapsed
                self._last_tick = now
                if self.current_mode == "Work":
                    self.today_work_seconds += elapsed
                else:
                    self.today_break_seconds += elapsed
                self.update_stats_and_goal()
            self.update_timer_display()
            time.sleep(1)
        if self.timer_running and self.remaining_seconds <= 0:
            self.complete_session()

    def complete_session(self):
        self.timer_running = False
        winsound.Beep(1000, 200)
        winsound.Beep(1500, 200)
        if self.current_mode == "Work":
            self.pomodoro_count += 1
            self.session_label.config(text=f"Pomodoros Completed: {self.pomodoro_count}")
            nxt = "Long Break" if (self.pomodoro_count % self.max_pomodoros) == 0 else "Short Break"
        else:
            nxt = "Work"
        self.on_mode_change(nxt)
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")

    def update_timer_display(self):
        self.time_display.config(text=self.format_time(self.remaining_seconds))

    def format_time(self, secs):
        m, s = divmod(max(secs, 0), 60)
        return f"{m:02d}:{s:02d}"

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.root.title(f"Pomodoro Timer - {now}")
        self.root.after(1000, self.update_clock)

    def on_close(self):
        self.save_daily_history()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    PomodoroTimerWithHistory(root)
    root.mainloop()