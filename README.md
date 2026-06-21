# Pay Timer

A Python desktop app for tracking shift time and calculating earnings in real time.

---

## Features

- **Live shift timer** — counts up from the moment you start your shift
- **Earnings counter** — updates every second based on your hourly rate
- **Persistent hourly rate** — saved to the database so it's remembered between sessions
- **Save progress** — snapshot the timer at any point during your shift
- **Manual entry** — calculate earnings for a shift by entering hours and minutes directly
- **Session log** — view all saved sessions with date, start time, duration, rate, and earnings, plus an all-time total

---

## Requirements

- Python 3.8+
- Pillow (`pip install Pillow`)
- Tkinter (usually included with Python; on Linux: `sudo apt install python3-tk`)

---

## Installation

1. Clone or copy the `pay_timer` folder to your machine.
2. Install dependencies:
   ```bash
   pip install Pillow
   ```
3. Run the app:
   ```bash
   python3 pay_timer.py
   ```

### Add to your app launcher (Linux)

1. Open `pay_timer.desktop` and update the two paths to match where you placed the folder:
   ```ini
   Exec=/usr/bin/python3 /path/to/pay_timer/pay_timer.py
   Icon=/path/to/pay_timer/icon.png
   ```
2. Copy it to your local applications folder:
   ```bash
   cp pay_timer.desktop ~/.local/share/applications/
   update-desktop-database ~/.local/share/applications/
   ```

The app will now appear in your launcher as **Pay Timer**.

---

## Usage

### Setting your rate
Enter your hourly rate in the **Hourly Rate** field at the top and click **Set Rate**. Your rate is saved to the database and restored automatically next time you open the app.

### Running the timer
| Button | Action |
|---|---|
| ▶ Start Shift | Starts the timer |
| ■ Stop Shift | Pauses the timer (time is kept) |
| ↺ Reset | Clears the timer back to zero |
| 💾 Save Progress | Saves a snapshot of the current timer to the database |

You can stop and restart the timer without losing accumulated time — useful for pausing during a break while keeping the session open.

### Manual entry
Enter hours and minutes in the **Manual Entry** panel and click **Calculate** to see your earnings for that duration. A **💾 Save** button will appear next to the result — click it to save the entry to the session log.

### Viewing the log
Click **View Log** to open a scrollable table of all saved sessions. Sessions show:
- **Date** — the calendar date of the save
- **Start** — the time the shift timer was started (`manual` for manual entries)
- **Duration** — total time worked
- **Rate** — your hourly rate at the time of the save
- **Earned** — total pay for that session

The bottom of the log shows all-time totals across every session.

---

## Data storage

All data is stored locally in `pay_timer.db` (SQLite) in the same folder as the app. No data is sent anywhere.

| Table | Contents |
|---|---|
| `sessions` | Every saved timer and manual entry |
| `settings` | Hourly rate and any future preferences |

---

## Files

| File | Description |
|---|---|
| `pay_timer.py` | Main application |
| `pay_timer.db` | SQLite database (created on first run) |
| `pay_timer.desktop` | Linux desktop launcher entry |
| `icon.png` | App icon |
