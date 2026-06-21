import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import os
from datetime import datetime

# ── color theme (matches work_hours_calculator) ──────────────────────────────
BG        = "#1a2a4a"
PANEL     = "#243558"
HEADER    = "#1565c0"
HEADER_FG = "#ffffff"
ACCENT    = "#42a5f5"
FG        = "#e3eaf6"
FG_DIM    = "#90aace"
ENTRY_BG  = "#ffffff"
ENTRY_FG  = "#1a2a4a"
BTN_BG    = "#1565c0"
BTN_HOV   = "#1976d2"
BTN_FG    = "#ffffff"
PANEL2    = "#162033"
TOT_FG    = "#a5d6a7"
OT_FG     = "#ffb74d"
SEP       = "#2d4470"

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pay_timer.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            date            TEXT NOT NULL,
            shift_start     TEXT,
            saved_at        TEXT,
            elapsed_seconds INTEGER,
            duration        TEXT,
            rate            REAL,
            earned          REAL,
            entry_type      TEXT DEFAULT 'timer'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()


class PayTimer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pay Timer")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._running = False
        self._elapsed = 0          # seconds accumulated
        self._after_id = None
        self._shift_start = None   # datetime when current run started

        init_db()
        self._set_icon()
        self._build_ui()
        self._load_rate()

    # ── icon ─────────────────────────────────────────────────────────────────

    def _set_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                self._icon = ImageTk.PhotoImage(img)
                self.iconphoto(True, self._icon)
            except Exception:
                pass

    # ── UI ───────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # header
        hdr = tk.Frame(self, bg=HEADER, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Pay Timer", font=("Segoe UI", 16, "bold"),
                 bg=HEADER, fg=HEADER_FG).pack()

        # rate row
        rate_frame = tk.Frame(self, bg=PANEL, pady=10, padx=20)
        rate_frame.pack(fill="x", padx=12, pady=(12, 0))

        tk.Label(rate_frame, text="Hourly Rate  $", font=("Segoe UI", 11),
                 bg=PANEL, fg=FG_DIM).pack(side="left")

        self._rate_var = tk.StringVar(value="0.00")
        rate_entry = tk.Entry(rate_frame, textvariable=self._rate_var, width=8,
                              bg=ENTRY_BG, fg=ENTRY_FG, font=("Segoe UI", 11),
                              justify="center", relief="flat")
        rate_entry.pack(side="left", padx=(0, 8))

        tk.Button(rate_frame, text="Set Rate", command=self._apply_rate,
                  bg=BTN_BG, fg=BTN_FG, font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, cursor="hand2",
                  activebackground=BTN_HOV, activeforeground=BTN_FG).pack(side="left")

        self._rate_label = tk.Label(rate_frame, text="", font=("Segoe UI", 9, "italic"),
                                    bg=PANEL, fg=ACCENT)
        self._rate_label.pack(side="left", padx=(10, 0))

        # big timer display
        disp = tk.Frame(self, bg=PANEL2, pady=18)
        disp.pack(fill="x", padx=12, pady=10)

        self._time_var = tk.StringVar(value="00:00:00")
        tk.Label(disp, textvariable=self._time_var,
                 font=("Segoe UI", 48, "bold"), bg=PANEL2, fg=ACCENT).pack()

        self._earned_var = tk.StringVar(value="$0.00")
        tk.Label(disp, textvariable=self._earned_var,
                 font=("Segoe UI", 28, "bold"), bg=PANEL2, fg=TOT_FG).pack()

        tk.Label(disp, text="earned this shift", font=("Segoe UI", 9, "italic"),
                 bg=PANEL2, fg=FG_DIM).pack()

        # control buttons
        ctrl = tk.Frame(self, bg=BG, pady=8)
        ctrl.pack()

        self._start_btn = tk.Button(ctrl, text="▶  Start Shift",
                                    command=self._start,
                                    bg="#2e7d32", fg=BTN_FG,
                                    font=("Segoe UI", 11, "bold"),
                                    relief="flat", padx=18, pady=6,
                                    cursor="hand2",
                                    activebackground="#388e3c",
                                    activeforeground=BTN_FG)
        self._start_btn.grid(row=0, column=0, padx=6)

        self._stop_btn = tk.Button(ctrl, text="■  Stop Shift",
                                   command=self._stop,
                                   bg="#b71c1c", fg=BTN_FG,
                                   font=("Segoe UI", 11, "bold"),
                                   relief="flat", padx=18, pady=6,
                                   cursor="hand2",
                                   activebackground="#c62828",
                                   activeforeground=BTN_FG,
                                   state="disabled")
        self._stop_btn.grid(row=0, column=1, padx=6)

        tk.Button(ctrl, text="↺  Reset",
                  command=self._reset,
                  bg=PANEL, fg=FG,
                  font=("Segoe UI", 11, "bold"),
                  relief="flat", padx=14, pady=6,
                  cursor="hand2",
                  activebackground=SEP,
                  activeforeground=FG).grid(row=0, column=2, padx=6)

        # save button
        save_frame = tk.Frame(self, bg=BG, pady=4)
        save_frame.pack()
        tk.Button(save_frame, text="💾  Save Progress",
                  command=self._save,
                  bg=BTN_BG, fg=BTN_FG,
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=5,
                  cursor="hand2",
                  activebackground=BTN_HOV,
                  activeforeground=BTN_FG).pack()

        # separator
        tk.Frame(self, bg=SEP, height=1).pack(fill="x", padx=12, pady=(8, 4))

        # manual entry
        manual = tk.Frame(self, bg=PANEL, padx=14, pady=10)
        manual.pack(fill="x", padx=12, pady=(0, 4))

        tk.Label(manual, text="Manual Entry", font=("Segoe UI", 10, "bold"),
                 bg=PANEL, fg=ACCENT).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 6))

        tk.Label(manual, text="Hours", font=("Segoe UI", 9), bg=PANEL, fg=FG_DIM).grid(row=1, column=0, padx=(0, 4))
        self._man_hours = tk.Entry(manual, width=5, bg=ENTRY_BG, fg=ENTRY_FG,
                                   font=("Segoe UI", 10), justify="center", relief="flat")
        self._man_hours.grid(row=1, column=1, padx=(0, 10))

        tk.Label(manual, text="Minutes", font=("Segoe UI", 9), bg=PANEL, fg=FG_DIM).grid(row=1, column=2, padx=(0, 4))
        self._man_minutes = tk.Entry(manual, width=5, bg=ENTRY_BG, fg=ENTRY_FG,
                                     font=("Segoe UI", 10), justify="center", relief="flat")
        self._man_minutes.grid(row=1, column=3, padx=(0, 10))

        tk.Button(manual, text="Calculate", command=self._manual_calc,
                  bg=BTN_BG, fg=BTN_FG, font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, cursor="hand2",
                  activebackground=BTN_HOV, activeforeground=BTN_FG).grid(row=1, column=4)

        self._man_result = tk.Label(manual, text="", font=("Segoe UI", 11, "bold"),
                                    bg=PANEL, fg=TOT_FG)
        self._man_result.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))

        self._man_save_btn = tk.Button(manual, text="💾 Save", command=self._manual_save,
                                       bg=BTN_BG, fg=BTN_FG, font=("Segoe UI", 9, "bold"),
                                       relief="flat", padx=8, cursor="hand2",
                                       activebackground=BTN_HOV, activeforeground=BTN_FG,
                                       state="disabled")
        self._man_save_btn.grid(row=2, column=4, pady=(8, 0))

        # separator
        tk.Frame(self, bg=SEP, height=1).pack(fill="x", padx=12, pady=(4, 0))

        # log panel
        log_hdr = tk.Frame(self, bg=BG, pady=6)
        log_hdr.pack(fill="x", padx=12)
        tk.Label(log_hdr, text="Saved Sessions", font=("Segoe UI", 10, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Button(log_hdr, text="View Log", command=self._view_log,
                  bg=PANEL, fg=FG, font=("Segoe UI", 8),
                  relief="flat", padx=8, cursor="hand2",
                  activebackground=SEP, activeforeground=FG).pack(side="right")

        self._log_preview = tk.Label(self, text=self._last_save_summary(),
                                     font=("Segoe UI", 9), bg=BG, fg=FG_DIM,
                                     justify="left", anchor="w")
        self._log_preview.pack(fill="x", padx=16, pady=(0, 12))

        self._hourly_rate = 0.0

    # ── rate ─────────────────────────────────────────────────────────────────

    def _apply_rate(self):
        try:
            rate = float(self._rate_var.get())
            if rate < 0:
                raise ValueError
            self._hourly_rate = rate
            self._rate_label.config(text=f"✔ ${rate:.2f}/hr set")
            self._save_rate(rate)
            self._update_display()
        except ValueError:
            messagebox.showerror("Invalid Rate", "Please enter a valid number for the hourly rate.")

    def _save_rate(self, rate):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT OR REPLACE INTO settings VALUES ('hourly_rate', ?)", (str(rate),))
        conn.commit()
        conn.close()

    def _load_rate(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT value FROM settings WHERE key='hourly_rate'").fetchone()
            conn.close()
            if row:
                rate = float(row[0])
                self._hourly_rate = rate
                self._rate_var.set(f"{rate:.2f}")
                self._rate_label.config(text=f"✔ ${rate:.2f}/hr set")
        except Exception:
            pass

    # ── timer control ────────────────────────────────────────────────────────

    def _start(self):
        if self._running:
            return
        if self._shift_start is None:
            self._shift_start = datetime.now()
        self._running = True
        self._start_btn.config(state="disabled")
        self._stop_btn.config(state="normal")
        self._tick()

    def _stop(self):
        if not self._running:
            return
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self._start_btn.config(state="normal")
        self._stop_btn.config(state="disabled")

    def _reset(self):
        if self._running:
            self._stop()
        self._elapsed = 0
        self._shift_start = None
        self._update_display()

    def _tick(self):
        self._elapsed += 1
        self._update_display()
        self._after_id = self.after(1000, self._tick)

    def _update_display(self):
        h = self._elapsed // 3600
        m = (self._elapsed % 3600) // 60
        s = self._elapsed % 60
        self._time_var.set(f"{h:02d}:{m:02d}:{s:02d}")
        earned = (self._elapsed / 3600) * self._hourly_rate
        self._earned_var.set(f"${earned:,.2f}")

    # ── manual calculation ───────────────────────────────────────────────────

    def _manual_calc(self):
        try:
            hours   = float(self._man_hours.get()   or 0)
            minutes = float(self._man_minutes.get() or 0)
            if hours < 0 or minutes < 0:
                raise ValueError
            total_hours = hours + minutes / 60
            earned = total_hours * self._hourly_rate
            total_secs = int(total_hours * 3600)
            h = total_secs // 3600
            m = (total_secs % 3600) // 60
            self._man_calc_result = {
                "elapsed_seconds": total_secs,
                "duration": f"{h:02d}:{m:02d}:00",
                "earned": round(earned, 2),
            }
            self._man_result.config(
                text=f"{h}h {m:02d}m  →  ${earned:,.2f} @ ${self._hourly_rate:.2f}/hr"
            )
            self._man_save_btn.config(state="normal")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid non-negative numbers for hours and minutes.")

    def _manual_save(self):
        result = getattr(self, "_man_calc_result", None)
        if not result:
            return
        now = datetime.now()
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO sessions (date, shift_start, saved_at, elapsed_seconds, duration, rate, earned, entry_type) VALUES (?,?,?,?,?,?,?,?)",
            (now.strftime("%Y-%m-%d"),
             "manual",
             now.strftime("%H:%M:%S"),
             result["elapsed_seconds"],
             result["duration"],
             self._hourly_rate,
             result["earned"],
             "manual")
        )
        conn.commit()
        conn.close()
        self._log_preview.config(text=self._last_save_summary())
        self._man_save_btn.config(state="disabled")
        self._man_calc_result = None
        messagebox.showinfo("Saved", f"Manual entry saved!\n\nDate: {now.strftime('%Y-%m-%d')}\nDuration: {result['duration']}\nEarned: ${result['earned']:,.2f}")

    # ── save / log ───────────────────────────────────────────────────────────

    def _save(self):
        if self._elapsed == 0:
            messagebox.showinfo("Nothing to Save", "Start a shift before saving.")
            return

        earned = round((self._elapsed / 3600) * self._hourly_rate, 2)
        now = datetime.now()
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO sessions (date, shift_start, saved_at, elapsed_seconds, duration, rate, earned, entry_type) VALUES (?,?,?,?,?,?,?,?)",
            (now.strftime("%Y-%m-%d"),
             self._shift_start.strftime("%H:%M:%S") if self._shift_start else "—",
             now.strftime("%H:%M:%S"),
             self._elapsed,
             self._time_var.get(),
             self._hourly_rate,
             earned,
             "timer")
        )
        conn.commit()
        conn.close()
        self._log_preview.config(text=self._last_save_summary())
        messagebox.showinfo("Saved", f"Progress saved!\n\nDate: {now.strftime('%Y-%m-%d')}\nDuration: {self._time_var.get()}\nEarned: ${earned:,.2f}")

    def _last_save_summary(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute(
                "SELECT date, duration, earned, rate FROM sessions ORDER BY id DESC LIMIT 1"
            ).fetchone()
            conn.close()
            if not row:
                return "No saves yet."
            return f"Last save — {row[0]}  |  {row[1]}  |  ${row[2]:,.2f} @ ${row[3]:.2f}/hr"
        except Exception:
            return "No saves yet."

    def _view_log(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            rows = conn.execute(
                "SELECT date, shift_start, duration, rate, earned, entry_type FROM sessions ORDER BY id DESC"
            ).fetchall()
            totals = conn.execute(
                "SELECT COUNT(*), SUM(elapsed_seconds), SUM(earned) FROM sessions"
            ).fetchone()
            conn.close()
        except Exception:
            messagebox.showerror("Error", "Could not read the database.")
            return

        if not rows:
            messagebox.showinfo("Log", "No saved sessions yet.")
            return

        log = [{"date": r[0], "shift_start": r[1], "duration": r[2],
                "rate": r[3], "earned": r[4], "entry_type": r[5]} for r in rows]

        win = tk.Toplevel(self)
        win.title("Saved Sessions")
        win.configure(bg=BG)
        win.resizable(True, True)

        tk.Label(win, text="Saved Sessions", font=("Segoe UI", 13, "bold"),
                 bg=HEADER, fg=HEADER_FG, pady=8).pack(fill="x")

        # scrollable list
        frame = tk.Frame(win, bg=BG)
        frame.pack(fill="both", expand=True, padx=12, pady=10)

        cols = ("Date", "Start", "Duration", "Rate", "Earned")
        widths = (100, 80, 90, 80, 90)

        header_row = tk.Frame(frame, bg=PANEL)
        header_row.pack(fill="x")
        for col, w in zip(cols, widths):
            tk.Label(header_row, text=col, font=("Segoe UI", 9, "bold"),
                     bg=PANEL, fg=ACCENT, width=w//7, anchor="center").pack(side="left", padx=4, pady=4)

        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, entry in enumerate(reversed(log)):
            bg = PANEL if i % 2 == 0 else "#1e3054"
            row = tk.Frame(inner, bg=bg)
            row.pack(fill="x")
            values = (
                entry.get("date", "—"),
                entry.get("shift_start", "—"),
                entry.get("duration", "—"),
                f"${entry.get('rate', 0):.2f}/hr",
                f"${entry.get('earned', 0):,.2f}",
            )
            colors = [FG, FG_DIM, ACCENT, FG_DIM, TOT_FG]
            for val, w, c in zip(values, widths, colors):
                tk.Label(row, text=val, font=("Segoe UI", 9),
                         bg=bg, fg=c, width=w//7, anchor="center").pack(side="left", padx=4, pady=5)

        # totals
        count        = totals[0] or 0
        total_secs   = totals[1] or 0
        total_earned = totals[2] or 0.0
        th = total_secs // 3600
        tm = (total_secs % 3600) // 60

        bot = tk.Frame(win, bg=PANEL2, pady=8, padx=16)
        bot.pack(fill="x")
        tk.Label(bot, text=f"All-time total: {th}h {tm}m   |   ${total_earned:,.2f} earned across {count} session(s)",
                 font=("Segoe UI", 10, "bold"), bg=PANEL2, fg=TOT_FG).pack()

        win.geometry("520x400")


if __name__ == "__main__":
    app = PayTimer()
    app.mainloop()
