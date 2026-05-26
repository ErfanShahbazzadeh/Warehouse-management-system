# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import center_window
import hashlib

class AddUserWindow(tk.Toplevel):
    def __init__(self, parent, db_conn):
        super().__init__(parent)
        self.parent = parent
        self.db_conn = db_conn
        self.title("افزودن کاربر جدید")
        
        window_width = 400
        window_height = 300
        center_window(self, window_width, window_height)
        self.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="افزودن کاربر جدید", font=("B Nazanin", 14, "bold")).pack(pady=10)
        
        form_frame = tk.Frame(main_frame)
        form_frame.pack(pady=10)
        
        # نام کاربری
        tk.Label(form_frame, text="نام کاربری:", font=("B Nazanin", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(form_frame, font=("B Nazanin", 12), width=25)
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # رمز عبور
        tk.Label(form_frame, text="رمز عبور:", font=("B Nazanin", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(form_frame, font=("B Nazanin", 12), width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # تکرار رمز عبور
        tk.Label(form_frame, text="تکرار رمز عبور:", font=("B Nazanin", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_password_entry = tk.Entry(form_frame, font=("B Nazanin", 12), width=25, show="*")
        self.confirm_password_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # سطح دسترسی
        tk.Label(form_frame, text="سطح دسترسی:", font=("B Nazanin", 12)).grid(row=3, column=0, sticky="w", pady=5)
        self.role_combobox = ttk.Combobox(form_frame, font=("B Nazanin", 12), width=23, state="readonly")
        self.role_combobox.grid(row=3, column=1, pady=5, padx=5)
        self.load_roles()
        
        # دکمه‌ها
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="ثبت کاربر", command=self.add_user,
                 font=("B Nazanin", 12), bg="#4CAF50", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(button_frame, text="انصراف", command=self.destroy,
                 font=("B Nazanin", 12), bg="#f44336", fg="white", width=12).pack(side="left", padx=5)
        
    def load_roles(self):
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT role_name FROM roles ORDER BY id")
            roles = [row[0] for row in cursor.fetchall()]
            self.role_combobox['values'] = roles
            if roles:
                self.role_combobox.set(roles[0])
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگیری سطوح دسترسی: {str(e)}")
            
    def add_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        role_name = self.role_combobox.get()
        
        if not all([username, password, confirm_password, role_name]):
            messagebox.showwarning("خطا", "لطفاً تمام فیلدها را پر کنید.")
            return
            
        if password != confirm_password:
            messagebox.showwarning("خطا", "رمز عبور و تکرار آن مطابقت ندارند.")
            return
            
        if len(password) < 6:
            messagebox.showwarning("خطا", "رمز عبور باید حداقل ۶ کاراکتر باشد.")
            return
            
        try:
            cursor = self.db_conn.cursor()
            
            # بررسی وجود کاربر
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                messagebox.showwarning("خطا", "این نام کاربری قبلاً ثبت شده است.")
                return
                
            # دریافت شناسه نقش
            cursor.execute("SELECT id FROM roles WHERE role_name = ?", (role_name,))
            role_result = cursor.fetchone()
            if not role_result:
                messagebox.showwarning("خطا", "سطح دسترسی انتخاب شده معتبر نیست.")
                return
            role_id = role_result[0]
            
            # هش کردن رمز عبور
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # ثبت کاربر
            cursor.execute("""
                INSERT INTO users (username, password, role_id) 
                VALUES (?, ?, ?)
            """, (username, hashed_password, role_id))
            
            self.db_conn.commit()
            messagebox.showinfo("موفقیت", "کاربر با موفقیت اضافه شد.")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ثبت کاربر: {str(e)}")