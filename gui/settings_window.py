# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils.window_utils import center_window
from utils.language_manager import lang
from styles.theme import AppTheme
from database.db import backup_database, restore_database, export_to_csv
import os
import shutil
from datetime import datetime

class SettingsWindow(tk.Toplevel):
    """Settings window for application configuration"""
    
    def __init__(self, parent, db_conn):
        super().__init__(parent)
        self.parent = parent
        self.db_conn = db_conn
        self.title("Settings")
        
        window_width = 800
        window_height = 600
        center_window(self, window_width, window_height)
        self.resizable(True, True)
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup settings UI with notebook tabs"""
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)
        
        # General settings tab
        general_frame = ttk.Frame(notebook, padding="10")
        notebook.add(general_frame, text="General")
        self.setup_general_tab(general_frame)
        
        # Database tab
        db_frame = ttk.Frame(notebook, padding="10")
        notebook.add(db_frame, text="Database")
        self.setup_database_tab(db_frame)
        
        # Backup tab
        backup_frame = ttk.Frame(notebook, padding="10")
        notebook.add(backup_frame, text="Backup & Restore")
        self.setup_backup_tab(backup_frame)
        
        # User preferences tab
        prefs_frame = ttk.Frame(notebook, padding="10")
        notebook.add(prefs_frame, text="Preferences")
        self.setup_preferences_tab(prefs_frame)
        
        # About tab
        about_frame = ttk.Frame(notebook, padding="10")
        notebook.add(about_frame, text="About")
        self.setup_about_tab(about_frame)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        save_btn = AppTheme.create_button(button_frame, "Save Settings", 
                                         self.save_settings, 'Success.TButton')
        save_btn.pack(side="right", padx=5)
        
        cancel_btn = AppTheme.create_button(button_frame, "Cancel", 
                                           self.destroy, 'TButton')
        cancel_btn.pack(side="right", padx=5)
        
    def setup_general_tab(self, parent):
        """Setup general settings tab"""
        # Language settings
        lang_frame = ttk.LabelFrame(parent, text="Language", padding="10")
        lang_frame.pack(fill="x", pady=5)
        
        self.lang_var = tk.StringVar(value=lang.get_current_language())
        
        ttk.Radiobutton(lang_frame, text="English", variable=self.lang_var, 
                       value="en").pack(anchor="w", pady=2)
        ttk.Radiobutton(lang_frame, text="Persian (فارسی)", variable=self.lang_var, 
                       value="fa").pack(anchor="w", pady=2)
        
        # Theme settings
        theme_frame = ttk.LabelFrame(parent, text="Theme", padding="10")
        theme_frame.pack(fill="x", pady=5)
        
        self.theme_var = tk.StringVar(value="light")
        
        ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var, 
                       value="light").pack(anchor="w", pady=2)
        ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var, 
                       value="dark").pack(anchor="w", pady=2)
        
        # Date format
        date_frame = ttk.LabelFrame(parent, text="Date Format", padding="10")
        date_frame.pack(fill="x", pady=5)
        
        self.date_format_var = tk.StringVar(value="persian")
        
        ttk.Radiobutton(date_frame, text="Persian (Shamsi)", variable=self.date_format_var, 
                       value="persian").pack(anchor="w", pady=2)
        ttk.Radiobutton(date_frame, text="Gregorian", variable=self.date_format_var, 
                       value="gregorian").pack(anchor="w", pady=2)
        
    def setup_database_tab(self, parent):
        """Setup database management tab"""
        # Database info
        info_frame = ttk.LabelFrame(parent, text="Database Information", padding="10")
        info_frame.pack(fill="x", pady=5)
        
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
        db_size = self.get_file_size(db_path)
        
        ttk.Label(info_frame, text=f"Database Path: {db_path}").pack(anchor="w", pady=2)
        ttk.Label(info_frame, text=f"Database Size: {db_size}").pack(anchor="w", pady=2)
        
        # Database actions
        actions_frame = ttk.LabelFrame(parent, text="Database Actions", padding="10")
        actions_frame.pack(fill="x", pady=5)
        
        btn_frame = ttk.Frame(actions_frame)
        btn_frame.pack(fill="x", pady=5)
        
        backup_btn = AppTheme.create_button(btn_frame, "Backup Database", 
                                           self.backup_database, 'Primary.TButton')
        backup_btn.pack(side="left", padx=5)
        
        optimize_btn = AppTheme.create_button(btn_frame, "Optimize Database", 
                                             self.optimize_database, 'TButton')
        optimize_btn.pack(side="left", padx=5)
        
        # Export data
        export_frame = ttk.LabelFrame(parent, text="Export Data", padding="10")
        export_frame.pack(fill="x", pady=5)
        
        tables = ['inventory_log', 'production_log', 'users', 'categories', 'items']
        self.export_table_var = tk.StringVar(value=tables[0])
        
        ttk.Label(export_frame, text="Select table to export:").pack(anchor="w", pady=5)
        table_combo = ttk.Combobox(export_frame, textvariable=self.export_table_var, 
                                   values=tables, state="readonly")
        table_combo.pack(fill="x", pady=5)
        
        export_csv_btn = AppTheme.create_button(export_frame, "Export to CSV", 
                                               self.export_to_csv, 'Success.TButton')
        export_csv_btn.pack(pady=5)
        
    def setup_backup_tab(self, parent):
        """Setup backup and restore tab"""
        # Auto backup settings
        auto_frame = ttk.LabelFrame(parent, text="Auto Backup Settings", padding="10")
        auto_frame.pack(fill="x", pady=5)
        
        self.auto_backup_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(auto_frame, text="Enable automatic backup", 
                       variable=self.auto_backup_var).pack(anchor="w", pady=5)
        
        backup_freq_frame = ttk.Frame(auto_frame)
        backup_freq_frame.pack(fill="x", pady=5)
        
        ttk.Label(backup_freq_frame, text="Backup frequency (days):").pack(side="left", padx=5)
        self.backup_freq_var = tk.StringVar(value="7")
        freq_spinbox = ttk.Spinbox(backup_freq_frame, from_=1, to=30, 
                                   textvariable=self.backup_freq_var, width=10)
        freq_spinbox.pack(side="left", padx=5)
        
        backup_path_frame = ttk.Frame(auto_frame)
        backup_path_frame.pack(fill="x", pady=5)
        
        ttk.Label(backup_path_frame, text="Backup location:").pack(side="left", padx=5)
        self.backup_path_var = tk.StringVar(value=os.path.expanduser("~/Desktop/warehouse_backups"))
        path_entry = ttk.Entry(backup_path_frame, textvariable=self.backup_path_var)
        path_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        browse_btn = AppTheme.create_button(backup_path_frame, "Browse", 
                                           self.browse_backup_path, 'TButton')
        browse_btn.pack(side="left", padx=5)
        
        # Manual backup
        manual_frame = ttk.LabelFrame(parent, text="Manual Backup", padding="10")
        manual_frame.pack(fill="x", pady=5)
        
        backup_now_btn = AppTheme.create_button(manual_frame, "Create Backup Now", 
                                               self.create_manual_backup, 'Success.TButton')
        backup_now_btn.pack(pady=5)
        
        # Restore
        restore_frame = ttk.LabelFrame(parent, text="Restore", padding="10")
        restore_frame.pack(fill="x", pady=5)
        
        restore_btn = AppTheme.create_button(restore_frame, "Restore from Backup", 
                                            self.restore_from_backup, 'Danger.TButton')
        restore_btn.pack(pady=5)
        
        ttk.Label(restore_frame, text="Warning: Restoring will overwrite current data!", 
                 foreground="red").pack(pady=5)
        
    def setup_preferences_tab(self, parent):
        """Setup user preferences tab"""
        # Display preferences
        display_frame = ttk.LabelFrame(parent, text="Display Preferences", padding="10")
        display_frame.pack(fill="x", pady=5)
        
        self.show_tooltips_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="Show tooltips", 
                       variable=self.show_tooltips_var).pack(anchor="w", pady=5)
        
        self.confirm_exit_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="Confirm on exit", 
                       variable=self.confirm_exit_var).pack(anchor="w", pady=5)
        
        self.show_notifications_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="Show notifications", 
                       variable=self.show_notifications_var).pack(anchor="w", pady=5)
        
        # Items per page
        items_frame = ttk.LabelFrame(parent, text="Items per page", padding="10")
        items_frame.pack(fill="x", pady=5)
        
        self.items_per_page_var = tk.StringVar(value="100")
        items_spinbox = ttk.Spinbox(items_frame, from_=10, to=500, step=10,
                                   textvariable=self.items_per_page_var, width=10)
        items_spinbox.pack(anchor="w", pady=5)
        
        # Low stock alert
        alert_frame = ttk.LabelFrame(parent, text="Low Stock Alert", padding="10")
        alert_frame.pack(fill="x", pady=5)
        
        self.low_stock_threshold_var = tk.StringVar(value="10")
        threshold_spinbox = ttk.Spinbox(alert_frame, from_=1, to=100, 
                                       textvariable=self.low_stock_threshold_var, width=10)
        threshold_spinbox.pack(anchor="w", pady=5)
        
        ttk.Label(alert_frame, text="Show alert when stock falls below this threshold").pack(anchor="w")
        
    def setup_about_tab(self, parent):
        """Setup about tab with application information"""
        about_frame = ttk.Frame(parent)
        about_frame.pack(fill="both", expand=True)
        
        # Logo (if available)
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'logo.jpg')
        if os.path.exists(logo_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                logo = ImageTk.PhotoImage(img)
                logo_label = tk.Label(about_frame, image=logo)
                logo_label.image = logo
                logo_label.pack(pady=10)
            except:
                pass
        
        # App info
        info_frame = ttk.Frame(about_frame)
        info_frame.pack(pady=10)
        
        ttk.Label(info_frame, text="Warehouse Management System", 
                 font=('Segoe UI', 14, 'bold')).pack()
        ttk.Label(info_frame, text="Version 2.0", 
                 font=('Segoe UI', 10)).pack(pady=5)
        ttk.Label(info_frame, text="Young Innovators Cooperative of Shahrekord", 
                 font=('Segoe UI', 10)).pack()
        
        ttk.Separator(about_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Credits
        credits_frame = ttk.LabelFrame(about_frame, text="Credits", padding="10")
        credits_frame.pack(fill="x", pady=5)
        
        ttk.Label(credits_frame, text="Developed by: IT Department").pack(anchor="w", pady=2)
        ttk.Label(credits_frame, text="Copyright © 2024").pack(anchor="w", pady=2)
        ttk.Label(credits_frame, text="All Rights Reserved").pack(anchor="w", pady=2)
        
        # License
        license_frame = ttk.LabelFrame(about_frame, text="License", padding="10")
        license_frame.pack(fill="x", pady=5)
        
        ttk.Label(license_frame, text="This software is for internal use only", 
                 wraplength=400).pack(anchor="w", pady=2)
        
    def get_file_size(self, file_path):
        """Get file size in human readable format"""
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"
    
    def browse_backup_path(self):
        """Browse for backup directory"""
        directory = filedialog.askdirectory(title="Select Backup Directory")
        if directory:
            self.backup_path_var.set(directory)
    
    def backup_database(self):
        """Create database backup"""
        backup_dir = self.backup_path_var.get()
        if backup_dir and backup_dir != "Select directory":
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"warehouse_backup_{timestamp}.db")
            
            if backup_database(self.db_conn, backup_file):
                messagebox.showinfo("Success", f"Database backed up successfully!\nLocation: {backup_file}")
            else:
                messagebox.showerror("Error", "Failed to backup database!")
        else:
            messagebox.showwarning("Warning", "Please select a backup directory first!")
    
    def create_manual_backup(self):
        """Create manual backup with custom name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db")],
            initialfile=f"warehouse_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        if file_path:
            if backup_database(self.db_conn, file_path):
                messagebox.showinfo("Success", f"Backup created successfully!\nLocation: {file_path}")
            else:
                messagebox.showerror("Error", "Failed to create backup!")
    
    def restore_from_backup(self):
        """Restore database from backup"""
        file_path = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        if file_path:
            if messagebox.askyesno("Confirm Restore", 
                                  "Warning: This will overwrite current data!\nAre you sure?"):
                if restore_database(file_path):
                    messagebox.showinfo("Success", "Database restored successfully!\nPlease restart the application.")
                else:
                    messagebox.showerror("Error", "Failed to restore database!")
    
    def optimize_database(self):
        """Optimize database (VACUUM)"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("VACUUM")
            self.db_conn.commit()
            messagebox.showinfo("Success", "Database optimized successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to optimize database: {str(e)}")
    
    def export_to_csv(self):
        """Export selected table to CSV"""
        table_name = self.export_table_var.get()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{table_name}_export_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if file_path:
            if export_to_csv(self.db_conn, table_name, file_path):
                messagebox.showinfo("Success", f"Data exported successfully!\nLocation: {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export data!")
    
    def save_settings(self):
        """Save all settings"""
        # Save language setting
        new_lang = self.lang_var.get()
        if new_lang != lang.get_current_language():
            lang.set_language(new_lang)
            messagebox.showinfo("Info", "Language changed. Please restart the application for changes to take effect.")
        
        # Save other settings to config file
        settings = {
            'theme': self.theme_var.get(),
            'date_format': self.date_format_var.get(),
            'show_tooltips': self.show_tooltips_var.get(),
            'confirm_exit': self.confirm_exit_var.get(),
            'show_notifications': self.show_notifications_var.get(),
            'items_per_page': self.items_per_page_var.get(),
            'low_stock_threshold': self.low_stock_threshold_var.get(),
            'auto_backup': self.auto_backup_var.get(),
            'backup_frequency': self.backup_freq_var.get(),
            'backup_path': self.backup_path_var.get()
        }
        
        # Save to file
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        try:
            import json
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")