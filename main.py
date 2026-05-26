# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import os
import sys

# Add project path
sys.path.append(os.path.dirname(__file__))

from database.db import setup_database
from gui.login_window import LoginWindow

class WarehouseApplication:
    def __init__(self):
        # Setup database first
        self.db_conn = setup_database()
        
        if not self.db_conn:
            messagebox.showerror("Error", "Failed to connect to database!")
            sys.exit(1)
        
        # Create login window with normal size
        self.login_root = tk.Tk()
        self.login_root.title("Warehouse Manager - Login")
        self.login_root.geometry("400x500")
        
        # Center login window
        screen_width = self.login_root.winfo_screenwidth()
        screen_height = self.login_root.winfo_screenheight()
        x = (screen_width // 2) - (400 // 2)
        y = (screen_height // 2) - (500 // 2)
        self.login_root.geometry(f"400x500+{x}+{y}")
        
        # Create login frame
        self.login_frame = LoginWindow(self.login_root, self.db_conn, self.on_login_success)
        self.login_frame.pack(fill="both", expand=True)
        
        self.login_root.mainloop()
        
    def on_login_success(self, user_data):
        # Close login window
        self.login_root.destroy()
        
        # Create main window with full size
        self.main_root = tk.Tk()
        self.main_root.title("Warehouse Manager")
        
        # Method 2: Try 'zoomed' first, fallback to screen dimensions
        try:
            self.main_root.state('zoomed')  # Windows/Linux maximized state
        except:
            # Fallback for systems that don't support 'zoomed'
            screen_width = self.main_root.winfo_screenwidth()
            screen_height = self.main_root.winfo_screenheight()
            self.main_root.geometry(f"{screen_width}x{screen_height}")
        
        # Create main window
        from gui.main_window import MainWindow
        self.main_window = MainWindow(self.main_root, self.db_conn, user_data)
        self.main_root.mainloop()
        
if __name__ == "__main__":
    app = WarehouseApplication()