# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import center_window
import json
import jdatetime

class ExitWarehouseWindow(tk.Toplevel):
    def __init__(self, parent, db_conn, refresh_callback):
        super().__init__(parent)
        self.db_conn = db_conn
        self.refresh_callback = refresh_callback
        self.current_lang = self.load_language()
        self.texts = self.get_texts(self.current_lang)
        
        self.title(self.texts['title'])
        self.geometry("500x500")
        center_window(self, 500, 500)
        self.resizable(False, False)
        
        self.setup_ui()
        self.load_items()
    
    def load_language(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                return config.get('language', 'en')
        except:
            return 'en'
    
    def get_texts(self, lang):
        if lang == 'fa':
            return {
                'title': 'ثبت خروج از انبار',
                'item': 'نام کالا:',
                'current_stock': 'موجودی فعلی:',
                'quantity': 'مقدار خروج:',
                'recipient': 'تحویل گیرنده:',
                'reason': 'دلیل خروج:',
                'date': 'تاریخ:',
                'submit': 'ثبت خروج',
                'cancel': 'انصراف',
                'success': 'خروج با موفقیت ثبت شد!',
                'error': 'خطا در ثبت خروج:',
                'insufficient': 'موجودی کافی نیست!',
                'invalid_qty': 'مقدار نامعتبر است!',
                'no_item': 'لطفاً کالا را انتخاب کنید!'
            }
        else:
            return {
                'title': 'Export from Warehouse',
                'item': 'Item Name:',
                'current_stock': 'Current Stock:',
                'quantity': 'Export Quantity:',
                'recipient': 'Recipient:',
                'reason': 'Reason for Export:',
                'date': 'Date:',
                'submit': 'Register Export',
                'cancel': 'Cancel',
                'success': 'Export registered successfully!',
                'error': 'Error registering export:',
                'insufficient': 'Insufficient stock!',
                'invalid_qty': 'Invalid quantity!',
                'no_item': 'Please select an item!'
            }
    
    def setup_ui(self):
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Item
        tk.Label(main_frame, text=self.texts['item'], font=('Arial', 10)).grid(row=0, column=0, sticky="e", pady=5)
        self.item_combo = ttk.Combobox(main_frame, width=35)
        self.item_combo.grid(row=0, column=1, pady=5, padx=5)
        self.item_combo.bind('<<ComboboxSelected>>', self.update_stock)
        
        # Current Stock
        tk.Label(main_frame, text=self.texts['current_stock'], font=('Arial', 10)).grid(row=1, column=0, sticky="e", pady=5)
        self.stock_label = tk.Label(main_frame, text="0", font=('Arial', 10, 'bold'), fg='blue')
        self.stock_label.grid(row=1, column=1, sticky="w", pady=5, padx=5)
        
        # Quantity
        tk.Label(main_frame, text=self.texts['quantity'], font=('Arial', 10)).grid(row=2, column=0, sticky="e", pady=5)
        self.quantity_entry = tk.Entry(main_frame, width=37)
        self.quantity_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Recipient
        tk.Label(main_frame, text=self.texts['recipient'], font=('Arial', 10)).grid(row=3, column=0, sticky="e", pady=5)
        self.recipient_entry = tk.Entry(main_frame, width=37)
        self.recipient_entry.grid(row=3, column=1, pady=5, padx=5)
        
        # Reason
        tk.Label(main_frame, text=self.texts['reason'], font=('Arial', 10)).grid(row=4, column=0, sticky="ne", pady=5)
        self.reason_text = tk.Text(main_frame, width=30, height=4)
        self.reason_text.grid(row=4, column=1, pady=5, padx=5)
        
        # Date
        tk.Label(main_frame, text=self.texts['date'], font=('Arial', 10)).grid(row=5, column=0, sticky="e", pady=5)
        self.date_entry = tk.Entry(main_frame, width=37)
        self.date_entry.grid(row=5, column=1, pady=5, padx=5)
        today = jdatetime.date.today().strftime("%Y/%m/%d")
        self.date_entry.insert(0, today)
        
        # Buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text=self.texts['submit'], command=self.submit,
                 bg='#e74c3c', fg='white', padx=20, pady=5).pack(side="left", padx=5)
        tk.Button(btn_frame, text=self.texts['cancel'], command=self.destroy,
                 bg='#95a5a6', fg='white', padx=20, pady=5).pack(side="left", padx=5)
    
    def load_items(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT DISTINCT item FROM inventory_log")
        items = [row[0] for row in cursor.fetchall()]
        self.item_combo['values'] = items
    
    def update_stock(self, event):
        item = self.item_combo.get()
        if item:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT SUM(CASE WHEN type = 'entry' THEN original_quantity ELSE -original_quantity END)
                FROM inventory_log WHERE item = ?
            """, (item,))
            stock = cursor.fetchone()[0] or 0
            self.stock_label.config(text=str(stock))
    
    def submit(self):
        item = self.item_combo.get()
        try:
            quantity = float(self.quantity_entry.get())
        except ValueError:
            messagebox.showerror("Error", self.texts['invalid_qty'])
            return
        
        recipient = self.recipient_entry.get().strip()
        reason = self.reason_text.get("1.0", tk.END).strip()
        exit_date = self.date_entry.get()
        
        if not item or quantity <= 0 or not recipient:
            messagebox.showwarning("Warning", self.texts['no_item'])
            return
        
        # Check stock
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT SUM(CASE WHEN type = 'entry' THEN original_quantity ELSE -original_quantity END)
            FROM inventory_log WHERE item = ?
        """, (item,))
        stock = cursor.fetchone()[0] or 0
        
        if quantity > stock:
            messagebox.showerror("Error", self.texts['insufficient'])
            return
        
        try:
            cursor.execute("""
                INSERT INTO inventory_log (item, original_quantity, original_unit, quantity, type, supplier, description, entry_date, user)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item, -quantity, 'unit', str(quantity), 'exit', recipient, reason, exit_date, 'System'))
            self.db_conn.commit()
            
            messagebox.showinfo("Success", self.texts['success'])
            if self.refresh_callback:
                self.refresh_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"{self.texts['error']}\n{str(e)}")