import tkinter as tk
from tkinter import messagebox
import csv
import os
import random
import threading
from time import time, sleep
from datetime import datetime

# ── Try to import hardware; fall back to simulation ──────────────────────────
try:
    from gpiozero import LED, Buzzer
    _led    = LED(17)
    _buzzer = Buzzer(18)
    HARDWARE = True
except Exception:
    HARDWARE = False
    _led    = None
    _buzzer = None

MORSE = {
    'A': '.-',   'B': '-...', 'C': '-.-.',
    'D': '-..',  'E': '.',    'F': '..-.',
    'G': '--.',  'H': '....', 'I': '..',
    'J': '.---', 'K': '-.-',  'L': '.-..',
    'M': '--',   'N': '-.',   'O': '---',
}

DOT_TIME = 0.2   # seconds


def hw_cleanup():
    try:
        if _led:    _led.off()
        if _buzzer: _buzzer.off()
    except Exception:
        pass


# ── Colour / font palette ─────────────────────────────────────────────────────
BG       = "#0d0f14"
PANEL    = "#13161e"
ACCENT   = "#e8c84a"
ACCENT2  = "#4ae8b0"
DANGER   = "#e84a4a"
TEXT     = "#e8e4d8"
SUBTEXT  = "#7a7a6a"

FT       = ("Courier New", 11)
FT_BOLD  = ("Courier New", 11, "bold")
FT_TITLE = ("Courier New", 22, "bold")
FT_SMALL = ("Courier New",  9)
FT_MONO  = ("Courier New", 12)


# ── CSV helpers ───────────────────────────────────────────────────────────────
CSV_HEADERS = [
    "participant_id", "session", "gender", "mode",
    "round_type", "letter", "guess", "correct",
    "reaction_time_s", "timestamp"
]

def csv_path(pid: str, session: str) -> str:
    return f"session_{pid}_{session}.csv"

def append_csv(path: str, row: dict):
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if new_file:
            w.writeheader()
        w.writerow(row)


# ═══════════════════════════════════════════════════════════════════════════════
#  SETUP WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
class SetupWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Morse Trainer - Session Setup")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._build()
        self.eval('tk::PlaceWindow . center')

    def _entry(self, parent, var, width=22):
        return tk.Entry(parent, textvariable=var,
                        bg="#1e2230", fg=ACCENT, insertbackground=ACCENT,
                        font=FT_MONO, relief="flat", width=width,
                        highlightthickness=1,
                        highlightcolor=ACCENT, highlightbackground=SUBTEXT)

    def _build(self):
        hdr = tk.Frame(self, bg=BG, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="... --- ...",
                 bg=BG, fg=ACCENT, font=("Courier New", 13)).pack()
        tk.Label(hdr, text="MORSE TRAINER",
                 bg=BG, fg=ACCENT, font=FT_TITLE).pack()
        tk.Label(hdr, text="session configuration",
                 bg=BG, fg=SUBTEXT, font=FT_SMALL).pack(pady=(0, 6))

        card = tk.Frame(self, bg=PANEL, padx=32, pady=24,
                        highlightthickness=1, highlightbackground=SUBTEXT)
        card.pack(padx=28, pady=(0, 24))

        def field(label, widget_fn):
            r = tk.Frame(card, bg=PANEL)
            r.pack(fill="x", pady=7)
            tk.Label(r, text=label, bg=PANEL, fg=SUBTEXT,
                     font=FT_SMALL, width=18, anchor="w").pack(side="left")
            widget_fn(r).pack(side="left")

        def radios(parent, var, options):
            f = tk.Frame(parent, bg=PANEL)
            for txt, val in options:
                tk.Radiobutton(f, text=txt, variable=var, value=val,
                               bg=PANEL, fg=TEXT, selectcolor=BG,
                               activebackground=PANEL, activeforeground=ACCENT,
                               font=FT_SMALL, cursor="hand2").pack(side="left", padx=5)
            return f

        self.v_pid = tk.StringVar()
        field("Participant ID", lambda p: self._entry(p, self.v_pid))

        self.v_session = tk.StringVar(value="1")
        field("Session #", lambda p: self._entry(p, self.v_session, width=8))

        self.v_gender = tk.StringVar(value="prefer_not")
        field("Gender", lambda p: radios(p, self.v_gender,
              [("Male","male"), ("Female","female"),
               ("Non-binary","nonbinary"), ("Prefer not","prefer_not")]))

        self.v_mode = tk.StringVar(value="audio_visual")
        field("Mode", lambda p: radios(p, self.v_mode,
              [("Audio only","audio"),
               ("Visual only","visual"),
               ("Audio + Visual","audio_visual")]))

        self.v_round = tk.StringVar(value="practice")
        field("Round type", lambda p: radios(p, self.v_round,
              [("Practice","practice"), ("Test","test")]))

        tk.Frame(card, bg=SUBTEXT, height=1).pack(fill="x", pady=(14, 0))
        tk.Button(card, text="START SESSION  >",
                  bg=ACCENT, fg=BG, font=("Courier New", 12, "bold"),
                  relief="flat", padx=20, pady=10, cursor="hand2",
                  activebackground="#f0d060", activeforeground=BG,
                  command=self._start).pack(pady=(14, 0))

        if not HARDWARE:
            tk.Label(card,
                     text="  Hardware not found - running in simulation mode",
                     bg=PANEL, fg="#e8944a", font=FT_SMALL).pack(pady=(8, 0))

    def _start(self):
        pid     = self.v_pid.get().strip()
        session = self.v_session.get().strip()
        if not pid:
            messagebox.showerror("Missing", "Please enter a Participant ID.")
            return
        if not session:
            messagebox.showerror("Missing", "Please enter a Session number.")
            return
        config = {
            "participant_id": pid,
            "session":        session,
            "gender":         self.v_gender.get(),
            "mode":           self.v_mode.get(),
            "round_type":     self.v_round.get(),
        }
        self.destroy()
        TrainerWindow(config).mainloop()


# ═══════════════════════════════════════════════════════════════════════════════
#  TRAINER WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
class TrainerWindow(tk.Tk):
    def __init__(self, config: dict):
        super().__init__()
        self.cfg            = config
        self.csv            = csv_path(config["participant_id"], config["session"])
        self.score          = 0
        self.total          = 0
        self.current_letter = None
        self.t_start        = None
        self.sending        = False

        self.title(
            f"Morse Trainer  |  {config['participant_id']}"
            f"  |  Session {config['session']}"
        )
        self.configure(bg=BG)
        self.resizable(False, False)
        self._build()
        self.eval('tk::PlaceWindow . center')
        self.after(400, self._next_round)

    def _build(self):
        top = tk.Frame(self, bg=BG, padx=20, pady=12)
        top.pack(fill="x")
        tk.Label(top, text="MORSE TRAINER",
                 bg=BG, fg=ACCENT, font=("Courier New", 16, "bold")).pack(side="left")

        info = tk.Frame(top, bg=BG)
        info.pack(side="right")
        tk.Label(info,
                 text=(f"ID: {self.cfg['participant_id']}   "
                       f"Session: {self.cfg['session']}   "
                       f"Mode: {self.cfg['mode'].replace('_',' ').title()}"),
                 bg=BG, fg=SUBTEXT, font=FT_SMALL).pack(anchor="e")

        self.lbl_badge = tk.Label(info,
                                  text=self._badge_text(),
                                  bg=self._badge_bg(), fg=self._badge_fg(),
                                  font=("Courier New", 10, "bold"),
                                  padx=8, pady=2)
        self.lbl_badge.pack(anchor="e", pady=(3, 0))

        tk.Frame(self, bg=SUBTEXT, height=1).pack(fill="x")

        main = tk.Frame(self, bg=BG, padx=30, pady=24)
        main.pack(fill="both", expand=True)

        # Signal indicator - only an on/off dot, never shows pattern or letter
        sig_card = tk.Frame(main, bg=PANEL,
                            highlightthickness=1, highlightbackground=SUBTEXT,
                            padx=24, pady=20)
        sig_card.pack(fill="x", pady=(0, 20))

        tk.Label(sig_card, text="SIGNAL",
                 bg=PANEL, fg=SUBTEXT, font=FT_SMALL).pack(anchor="w")

        self.lbl_indicator = tk.Label(sig_card, text="●",
                                      bg=PANEL, fg=SUBTEXT,
                                      font=("Courier New", 52, "bold"))
        self.lbl_indicator.pack()

        self.lbl_status = tk.Label(sig_card, text="Preparing...",
                                   bg=PANEL, fg=SUBTEXT, font=FT)
        self.lbl_status.pack(pady=(6, 0))

        input_row = tk.Frame(main, bg=BG)
        input_row.pack(fill="x", pady=(0, 14))

        tk.Label(input_row, text="YOUR GUESS:",
                 bg=BG, fg=SUBTEXT, font=FT_SMALL).pack(side="left", padx=(0, 10))

        self.v_guess = tk.StringVar()
        self.entry_guess = tk.Entry(
            input_row, textvariable=self.v_guess,
            bg="#1e2230", fg=ACCENT, insertbackground=ACCENT,
            font=("Courier New", 20, "bold"), relief="flat",
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=SUBTEXT,
            width=4, justify="center"
        )
        self.entry_guess.pack(side="left")
        self.entry_guess.bind("<Return>", lambda e: self._submit())

        self.btn_submit = tk.Button(
            input_row, text="SUBMIT",
            bg=ACCENT, fg=BG, font=FT_BOLD,
            relief="flat", padx=16, pady=6, cursor="hand2",
            activebackground="#f0d060", activeforeground=BG,
            command=self._submit
        )
        self.btn_submit.pack(side="left", padx=(10, 0))

        self.btn_replay = tk.Button(
            input_row, text="REPLAY",
            bg="#1e2230", fg=TEXT, font=FT,
            relief="flat", padx=12, pady=6, cursor="hand2",
            activebackground="#2a2e3e", activeforeground=ACCENT,
            command=self._replay
        )
        self.btn_replay.pack(side="left", padx=(8, 0))

        self.lbl_feedback = tk.Label(main, text="",
                                     bg=BG, fg=ACCENT2,
                                     font=("Courier New", 14, "bold"))
        self.lbl_feedback.pack()

        bot = tk.Frame(self, bg=PANEL, padx=20, pady=10,
                       highlightthickness=1, highlightbackground=SUBTEXT)
        bot.pack(fill="x", side="bottom")

        self.lbl_score = tk.Label(bot, text="Score: 0/0  (---%)",
                                  bg=PANEL, fg=TEXT, font=FT)
        self.lbl_score.pack(side="left")

        self.btn_switch = tk.Button(
            bot, text=self._switch_text(),
            bg=self._switch_bg(), fg=ACCENT, font=FT_SMALL,
            relief="flat", padx=10, pady=4, cursor="hand2",
            command=self._switch_round
        )
        self.btn_switch.pack(side="right", padx=(0, 6))

        tk.Button(bot, text="QUIT",
                  bg="#2a1a1a", fg=DANGER, font=FT_SMALL,
                  relief="flat", padx=10, pady=4, cursor="hand2",
                  command=self._quit).pack(side="right")

    def _badge_text(self):
        return f"  {self.cfg['round_type'].upper()} ROUND  "

    def _badge_bg(self):
        return ACCENT if self.cfg["round_type"] == "test" else "#2a4a6a"

    def _badge_fg(self):
        return BG if self.cfg["round_type"] == "test" else ACCENT

    def _switch_text(self):
        return ("-> Switch to TEST round"
                if self.cfg["round_type"] == "practice"
                else "-> Switch to PRACTICE round")

    def _switch_bg(self):
        return "#4a2a2a" if self.cfg["round_type"] == "test" else "#2a4a6a"

    def _refresh_round_ui(self):
        self.lbl_badge.config(text=self._badge_text(),
                              bg=self._badge_bg(), fg=self._badge_fg())
        self.btn_switch.config(text=self._switch_text(), bg=self._switch_bg())

    def _switch_round(self):
        if self.sending:
            return
        self.cfg["round_type"] = (
            "test" if self.cfg["round_type"] == "practice" else "practice"
        )
        self._refresh_round_ui()
        self.lbl_feedback.config(
            text=f"Switched to {self.cfg['round_type'].upper()} round.",
            fg=ACCENT
        )
        self.after(1200, lambda: self.lbl_feedback.config(text=""))
        self.after(1400, self._next_round)

    def _indicator_on(self):
        self.lbl_indicator.config(fg=ACCENT)

    def _indicator_off(self):
        self.lbl_indicator.config(fg=SUBTEXT)

    def _next_round(self):
        self.current_letter = random.choice(list(MORSE.keys()))
        self.v_guess.set("")
        self.lbl_feedback.config(text="")
        self.lbl_status.config(text="Sending...", fg=SUBTEXT)
        self._indicator_off()
        self.entry_guess.config(state="disabled")
        self.btn_submit.config(state="disabled")
        self.btn_replay.config(state="disabled")
        self.sending = True
        threading.Thread(target=self._transmit_thread, daemon=True).start()

    def _transmit_thread(self):
        """
        Drives hardware directly:
          audio        -> buzzer only  (LED stays off)
          visual       -> LED only     (buzzer stays silent)
          audio_visual -> LED + buzzer together

        The on-screen dot mirrors the LED/buzzer state but never
        reveals the morse pattern or the letter to the participant.
        """
        mode       = self.cfg["mode"]
        use_led    = mode in ("visual", "audio_visual")
        use_buzzer = mode in ("audio",  "audio_visual")
        code       = MORSE[self.current_letter]

        for sym in code:
            dur = DOT_TIME if sym == '.' else 3 * DOT_TIME

            # ON
            self.after(0, self._indicator_on)
            if use_led    and _led:    _led.on()
            if use_buzzer and _buzzer: _buzzer.on()

            sleep(dur)

            # OFF
            self.after(0, self._indicator_off)
            if use_led    and _led:    _led.off()
            if use_buzzer and _buzzer: _buzzer.off()

            sleep(DOT_TIME)   # inter-symbol gap

        sleep(2 * DOT_TIME)   # inter-letter gap
        self.after(0, self._ready_for_input)

    def _ready_for_input(self):
        self.sending = False
        self.lbl_status.config(text="What letter was that?", fg=TEXT)
        self.entry_guess.config(state="normal")
        self.btn_submit.config(state="normal")
        self.btn_replay.config(state="normal")
        self.entry_guess.focus_set()
        self.t_start = time()

    def _replay(self):
        if self.sending or self.current_letter is None:
            return
        self.entry_guess.config(state="disabled")
        self.btn_submit.config(state="disabled")
        self.btn_replay.config(state="disabled")
        self.lbl_status.config(text="Replaying...", fg=SUBTEXT)
        self.sending = True
        threading.Thread(target=self._transmit_thread, daemon=True).start()

    def _submit(self):
        if self.sending or self.current_letter is None:
            return
        guess = self.v_guess.get().strip().upper()
        if not guess:
            return

        rt      = round(time() - self.t_start, 3)
        correct = (guess == self.current_letter)
        self.total += 1
        if correct:
            self.score += 1

        if correct:
            self.lbl_feedback.config(
                text=f"  Correct!  ({self.current_letter})", fg=ACCENT2)
        else:
            self.lbl_feedback.config(
                text=f"  Wrong - it was '{self.current_letter}'", fg=DANGER)

        pct = self.score / self.total * 100
        self.lbl_score.config(
            text=f"Score: {self.score}/{self.total}  ({pct:.1f}%)")

        append_csv(self.csv, {
            "participant_id":  self.cfg["participant_id"],
            "session":         self.cfg["session"],
            "gender":          self.cfg["gender"],
            "mode":            self.cfg["mode"],
            "round_type":      self.cfg["round_type"],
            "letter":          self.current_letter,
            "guess":           guess,
            "correct":         int(correct),
            "reaction_time_s": rt,
            "timestamp":       datetime.now().isoformat(timespec="seconds"),
        })

        self.after(1200, self._next_round)

    def _quit(self):
        hw_cleanup()
        pct = (self.score / self.total * 100) if self.total else 0
        messagebox.showinfo(
            "Session Complete",
            f"Final score: {self.score}/{self.total}  ({pct:.1f}%)\n"
            f"Log saved to:  {self.csv}"
        )
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    SetupWindow().mainloop()
