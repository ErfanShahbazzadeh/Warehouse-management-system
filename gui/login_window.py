
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import center_window
import hashlib
import os
import json

class LoginWindow(tk.Frame):  # Changed from Toplevel to Frame
    def __init__(self, parent, db_conn, login_callback):
        super().__init__(parent)
        self.parent = parent
        self.db_conn = db_conn
        self.login_callback = login_callback
        
        # Load language settings
        self.load_language_settings()
        
        self.setup_ui()
        
        # Bind Enter key
        self.bind('<Return>', lambda e: self.login())
        
    def load_language_settings(self):
        """Load saved language preference"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                lang_code = config.get('language', 'en')
        except:
            lang_code = 'en'
        
        self.language = lang_code
        self.texts = self.get_texts(lang_code)
    
    def get_texts(self, lang):
        """Get UI texts based on language"""
        if lang == 'fa':
            return {
                'title': 'مدیریت انبار',
                'username': 'نام کاربری',
                'password': 'رمز عبور',
                'remember': 'مرا به خاطر بسپار',
                'login': 'ورود',
                'cancel': 'انصراف',
                'warning': 'هشدار',
                'error': 'خطا',
                'empty_fields': 'لطفاً نام کاربری و رمز عبور را وارد کنید!',
                'invalid': 'نام کاربری یا رمز عبور اشتباه است!'
            }
        else:
            return {
                'title': 'WAREHOUSE MANAGER',
                'username': 'USERNAME',
                'password': 'PASSWORD',
                'remember': 'Remember Me',
                'login': 'LOGIN',
                'cancel': 'CANCEL',
                'warning': 'Warning',
                'error': 'Error',
                'empty_fields': 'Please enter username and password!',
                'invalid': 'Invalid username or password!'
            }
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self, bg='#f0f0f0')
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(main_frame, text=self.texts['title'], 
                              font=('Arial', 18, 'bold'),
                              bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(20, 30))
        
        # Form frame
        form_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        form_frame.pack(fill="both", expand=True, pady=10)
        
        # Username
        tk.Label(form_frame, text=self.texts['username'], font=('Arial', 10, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor="w", pady=(20, 5), padx=20)
        self.username_entry = tk.Entry(form_frame, font=('Arial', 11), 
                                       bg='#dddddd', relief=tk.FLAT, bd=1)
        self.username_entry.pack(pady=(0, 15), padx=20, fill='x', ipady=8)
        
        # Password with show/hide button
        tk.Label(form_frame, text=self.texts['password'], font=('Arial', 10, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor="w", pady=(0, 5), padx=20)
        
        password_frame = tk.Frame(form_frame, bg='#dddddd')
        password_frame.pack(pady=(0, 15), padx=20, fill='x')
        
        self.password_entry = tk.Entry(password_frame, font=('Arial', 11), 
                                       bg='#dddddd', relief=tk.FLAT, bd=1, show="•")
        self.password_entry.pack(side="left", fill='x', expand=True, ipady=8)
        
        # Show/Hide password button (shows only while pressed)
        self.show_btn = tk.Button(password_frame, text="👁", 
                         bg='#dddddd', relief=tk.FLAT, font=('Segoe UI Emoji', 11),  # Better emoji font
                         activebackground='#e0e0e0',
                         padx=4, pady=1)
        self.show_btn.pack(side="right", padx=(5, 0))
        
        # Bind mouse events
        self.show_btn.bind('<ButtonPress-1>', self.start_show_password)
        self.show_btn.bind('<ButtonRelease-1>', self.stop_show_password)
        
        # Remember me
        self.remember_var = tk.BooleanVar()
        remember_cb = tk.Checkbutton(form_frame, text=self.texts['remember'], 
                                     variable=self.remember_var,
                                     bg='white', font=('Arial', 9))
        remember_cb.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Buttons frame
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.pack(pady=10, padx=20, fill='x')
        
        # Login button
        login_btn = tk.Button(button_frame, text=self.texts['login'], command=self.login,
                             font=('Arial', 11, 'bold'), bg='#3498db', 
                             fg='white', relief=tk.FLAT, padx=20, pady=8)
        login_btn.pack(side="left", expand=True, fill='x', padx=(0, 5))
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text=self.texts['cancel'], command=self.quit_app,
                              font=('Arial', 11), bg='#95a5a6', 
                              fg='white', relief=tk.FLAT, padx=20, pady=8)
        cancel_btn.pack(side="left", expand=True, fill='x', padx=(5, 0))
        
        # Load saved credentials
        self.load_saved_credentials()
    
    def quit_app(self):
        """Quit the application"""
        self.parent.quit()
    
    def start_show_password(self, event):
        """Show password while button is pressed"""
        self.password_entry.config(show='')
    
    def stop_show_password(self, event):
        """Hide password when button is released"""
        self.password_entry.config(show='•')
    
    def load_saved_credentials(self):
        """Load saved username"""
        try:
            with open('.credentials', 'r') as f:
                username = f.read().strip()
                if username:
                    self.username_entry.insert(0, username)
                    self.remember_var.set(True)
        except:
            pass
    
    def save_credentials(self):
        """Save username if remember me is checked"""
        if self.remember_var.get():
            with open('.credentials', 'w') as f:
                f.write(self.username_entry.get().strip())
        else:
            try:
                os.remove('.credentials')
            except:
                pass
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning(self.texts['warning'], self.texts['empty_fields'])
            return
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT u.id, u.username, r.role_name, u.full_name
                FROM users u 
                LEFT JOIN roles r ON u.role_id = r.id 
                WHERE u.username = ? AND u.password = ? AND u.is_active = 1
            """, (username, hashed_password))
            
            user = cursor.fetchone()
            
            if user:
                user_data = {
                    'id': user[0],
                    'username': user[1],
                    'role': user[2] if user[2] else 'user',
                    'full_name': user[3] or user[1]
                }
                self.save_credentials()
                self.login_callback(user_data)
            else:
                messagebox.showerror(self.texts['error'], self.texts['invalid'])
                
        except Exception as e:
            messagebox.showerror(self.texts['error'], f"Login error: {str(e)}")