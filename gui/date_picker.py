# gui/date_picker.py
import tkinter as tk
from tkinter import ttk, messagebox
import jdatetime
from utils.window_utils import center_window

class ShamsiDatePicker(tk.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("انتخاب تاریخ شمسی")
        self.callback = callback
        # تنظیم اندازه و موقعیت پنجره در مرکز
        window_width = 250
        window_height = 150
        center_window(self, window_width, window_height)
        self.resizable(False, False)

        years = [str(y) for y in range(1400, 1451)]
        self.year_var = tk.StringVar(value=jdatetime.datetime.now().strftime("%Y"))
        tk.Label(self, text="سال:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(self, values=years, textvariable=self.year_var, width=10).grid(row=0, column=1)

        months = [str(m) for m in range(1, 13)]
        self.month_var = tk.StringVar(value=jdatetime.datetime.now().strftime("%m"))
        tk.Label(self, text="ماه:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Combobox(self, values=months, textvariable=self.month_var, width=10).grid(row=1, column=1)

        days = [str(d) for d in range(1, 32)]
        self.day_var = tk.StringVar(value=jdatetime.datetime.now().strftime("%d"))
        tk.Label(self, text="روز:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Combobox(self, values=days, textvariable=self.day_var, width=10).grid(row=2, column=1)

        tk.Button(self, text="انتخاب", command=self.on_select).grid(row=3, column=0, columnspan=2, pady=10)

    def on_select(self):
        try:
            y = int(self.year_var.get())
            m = int(self.month_var.get())
            d = int(self.day_var.get())
            jdatetime.date(y, m, d)
            date_str = f"{y:04d}/{m:02d}/{d:02d}"
            self.callback(date_str)
            self.destroy()
        except ValueError:
            messagebox.showerror("خطا", "تاریخ وارد شده معتبر نیست.")