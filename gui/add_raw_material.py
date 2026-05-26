# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import center_window
from gui.manage_categories import ManageCategoriesWindow
from gui.manage_items import ManageItemsWindow
import json
import jdatetime

class AddRawMaterialWindow(tk.Toplevel):
    def __init__(self, master, callback, db_conn):
        super().__init__(master)
        self.master = master
        self.callback = callback
        self.db_conn = db_conn
        self.current_lang = self.load_language()
        self.texts = self.get_texts(self.current_lang)
        
        self.title(self.texts['title'])
        self.geometry("650x700")
        center_window(self, 650, 700)
        self.resizable(False, False)
        
        self.setup_ui()
    
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
                'title': 'افزودن مواد اولیه',
                'category': 'دسته:',
                'item_name': 'نام کالا:',
                'quantity': 'مقدار وارده:',
                'unit_type': 'نوع واحد:',
                'consumption_unit': 'واحد مصرف:',
                'consumable_quantity': 'مقدار قابل مصرف:',
                'purchase_date': 'تاریخ خرید:',
                'entry_date': 'تاریخ ورود به انبار:',
                'price': 'قیمت هر واحد (ریال):',
                'supplier': 'تامین کننده:',
                'description': 'توضیحات:',
                'submit': 'ثبت',
                'manage_cat': 'مدیریت دسته',
                'manage_item': 'مدیریت کالا',
                'select': 'انتخاب',
                'success': 'مواد اولیه با موفقیت ثبت شد.',
                'error': 'خطا در ثبت مواد اولیه:',
                'all_fields': 'لطفاً تمام فیلدها را پر کنید!',
                'invalid_qty': 'مقدار نامعتبر است!'
            }
        else:
            return {
                'title': 'Add Raw Material',
                'category': 'Category:',
                'item_name': 'Item Name:',
                'quantity': 'Quantity:',
                'unit_type': 'Unit Type:',
                'consumption_unit': 'Consumption Unit:',
                'consumable_quantity': 'Consumable Quantity:',
                'purchase_date': 'Purchase Date:',
                'entry_date': 'Entry Date:',
                'price': 'Price per Unit (IRR):',
                'supplier': 'Supplier:',
                'description': 'Description:',
                'submit': 'Submit',
                'manage_cat': 'Manage Categories',
                'manage_item': 'Manage Items',
                'select': 'Select',
                'success': 'Raw material added successfully!',
                'error': 'Error adding raw material:',
                'all_fields': 'Please fill all required fields!',
                'invalid_qty': 'Invalid quantity!'
            }
    
    def setup_ui(self):
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Category selection with manage button
        row = 0
        tk.Label(main_frame, text=self.texts['category'], font=('Arial', 10)).grid(row=row, column=0, sticky="e", pady=8)
        
        cat_frame = tk.Frame(main_frame)
        cat_frame.grid(row=row, column=1, sticky="w", pady=8)
        
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.category_var, width=30, font=('Arial', 10))
        self.category_combo.pack(side="left", padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', self.load_items)
        
        tk.Button(cat_frame, text=self.texts['manage_cat'], command=self.open_manage_categories,
                 bg='#3498db', fg='white', font=('Arial', 8), padx=10).pack(side="left", padx=2)
        
        # Item selection with manage button
        row += 1
        tk.Label(main_frame, text=self.texts['item_name'], font=('Arial', 10)).grid(row=row, column=0, sticky="e", pady=8)
        
        item_frame = tk.Frame(main_frame)
        item_frame.grid(row=row, column=1, sticky="w", pady=8)
        
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(item_frame, textvariable=self.item_var, width=30, font=('Arial', 10))
        self.item_combo.pack(side="left", padx=5)
        self.item_combo.bind('<<ComboboxSelected>>', self.load_unit_type)
        
        tk.Button(item_frame, text=self.texts['manage_item'], command=self.open_manage_items,
                 bg='#3498db', fg='white', font=('Arial', 8), padx=10).pack(side="left", padx=2)
        
        # Quantity
        row += 1
        tk.Label(main_frame, text=self.texts['quantity'], font=('Arial', 10)).grid(row=row, column=0, sticky="e", pady=8)
        self.quantity_entry = tk.Entry(main_frame, width=35, font=('Arial', 10))
        self.quantity_entry.grid(row=row, column=1, pady=8, padx=5, sticky="w")
        
        # Unit Type (readonly, loaded from item)
        row += 1
        tk.Label(main_frame, text=self.texts['unit_type'], font=('Arial', 10)).grid(row=row, column=0, sticky="e", pady=8)
        self.unit_type_entry = tk.Entry(main_frame, width=35, font=('Arial', 10), state='readonly')
        self.unit_type_entry.grid(row=row, column=1, pady=8, padx=5, sticky="w")
        
        # Consumption Unit
        row += 1
        tk.Label(main_frame, text=self.texts['consumption_unit'], font=('Arial', 10)).grid(row=row, column=0, sticky="e", pady=8)
        self.consumption_combo = ttk.Combobox(main_frame, width=33, font=('Arial', 10))
        self.consumption_combo.grid(row=row, column=1, pady=8, padx=5, sticky="w")
        
        # Consumable Quantity
        row += 1
        tk.Label(main_frame, text=self.texts['consumable_quantity'], font=('Arial', 10)).grid(row=row, column=0, sticky="e", pady=8)
        self.consumable_entry = tk.Entry(main_frame, width=35, font=('Arial', 10), state='readonly')
        self.consumable_entry.grid(row=row, column=1, pady=8, padx=5, sticky="w")
        
        # Bind quantity change to update consumable
        self.quantity_entry.bind('<KeyRelease>', self.calculate_consumable)
        self.consumption_combo.bind('<<ComboboxSelected>>', self.calculate_consumable)
        
        # Purchase Date
        row += 1
        tk.Label(main_frame, text=self.texts['purchase_date'], font=('Arial', 10)).grid(row=row, column=0, sticky="e", pady=8)
        date_frame = tk.Frame(main_frame)
        date_frame.grid(row=row, column=1, sticky="w", pady=8)
        self.purchase_date = tk.Entry(date_frame, width=25, font=('Arial', 10))
        self.purchase_date.pack(side="left")
        today = jdatetime.date.today().strftime("%Y/%m/%d")
        self.purchase_date.insert(0, today)
        
        # Entry Date
        row += 1
        tk.Label(main_frame, text=self.texts['entry_date'], font=('Arial', 10)).grid(row=row, column=0, sticky="e", pady=8)
        entry_frame = tk.Frame(main_frame)
        entry_frame.grid(row=row, column=1, sticky="w", pady=8)
        self.entry_date = tk.Entry(entry_frame, width=25, font=('Arial', 10))
        self.entry_date.pack(side="left")
        self.entry_date.insert(0, today)
        
        # Price
        row += 1
        tk.Label(main_frame, text=self.texts['price'], font=('Arial', 10)).grid(row=row, column=0, sticky="e", pady=8)
        self.price_entry = tk.Entry(main_frame, width=35, font=('Arial', 10))
        self.price_entry.grid(row=row, column=1, pady=8, padx=5, sticky="w")
        
        # Supplier
        row += 1
        tk.Label(main_frame, text=self.texts['supplier'], font=('Arial', 10)).grid(row=row, column=0, sticky="e", pady=8)
        self.supplier_entry = tk.Entry(main_frame, width=35, font=('Arial', 10))
        self.supplier_entry.grid(row=row, column=1, pady=8, padx=5, sticky="w")
        
        # Description
        row += 1
        tk.Label(main_frame, text=self.texts['description'], font=('Arial', 10)).grid(row=row, column=0, sticky="ne", pady=8)
        self.description_text = tk.Text(main_frame, width=30, height=4, font=('Arial', 10))
        self.description_text.grid(row=row, column=1, pady=8, padx=5, sticky="w")
        
        # Submit button
        row += 1
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text=self.texts['submit'], command=self.submit,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), padx=30, pady=8).pack()
        
        # Load initial data
        self.load_categories()
    
    def load_categories(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in cursor.fetchall()]
        self.category_combo['values'] = categories
        if categories:
            self.category_combo.set(categories[0])
            self.load_items()
    
    def load_items(self, event=None):
        category = self.category_var.get()
        if category:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT item_name FROM items WHERE category_name = ? ORDER BY item_name", (category,))
            items = [row[0] for row in cursor.fetchall()]
            self.item_combo['values'] = items
            if items:
                self.item_combo.set(items[0])
                self.load_unit_type()
    
    def load_unit_type(self, event=None):
        item = self.item_var.get()
        if item:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT unit_type FROM items WHERE item_name = ?", (item,))
            result = cursor.fetchone()
            if result:
                self.unit_type_entry.config(state='normal')
                self.unit_type_entry.delete(0, tk.END)
                self.unit_type_entry.insert(0, result[0])
                self.unit_type_entry.config(state='readonly')
                
                # Set consumption units (include the original unit and common conversions)
                units = [result[0], 'gram', 'kilogram', 'liter', 'milliliter', 'piece']
                self.consumption_combo['values'] = list(dict.fromkeys(units))  # Remove duplicates
                self.consumption_combo.set(result[0])
                self.calculate_consumable()
    
    def calculate_consumable(self, event=None):
        try:
            quantity = float(self.quantity_entry.get()) if self.quantity_entry.get() else 0
            self.consumable_entry.config(state='normal')
            self.consumable_entry.delete(0, tk.END)
            self.consumable_entry.insert(0, str(quantity))
            self.consumable_entry.config(state='readonly')
        except ValueError:
            self.consumable_entry.config(state='normal')
            self.consumable_entry.delete(0, tk.END)
            self.consumable_entry.config(state='readonly')
    
    def open_manage_categories(self):
        win = ManageCategoriesWindow(self.master, self.db_conn, self.load_categories)
        win.transient(self)
        win.grab_set()
    
    def open_manage_items(self):
        win = ManageItemsWindow(self.master, self.db_conn, self.load_items)
        win.transient(self)
        win.grab_set()
    
    def submit(self):
        try:
            quantity = float(self.quantity_entry.get()) if self.quantity_entry.get() else 0
        except ValueError:
            messagebox.showerror("Error", self.texts['invalid_qty'])
            return
        
        data = {
            'category': self.category_var.get(),
            'item': self.item_var.get(),
            'original_quantity': quantity,
            'original_unit': self.unit_type_entry.get(),
            'quantity': self.consumable_entry.get(),
            'type': 'entry',
            'purchase_date': self.purchase_date.get(),
            'entry_date': self.entry_date.get(),
            'price': float(self.price_entry.get()) if self.price_entry.get() else 0,
            'supplier': self.supplier_entry.get(),
            'description': self.description_text.get("1.0", tk.END).strip(),
            'user': 'System'
        }
        
        if not all([data['category'], data['item'], data['original_quantity'] > 0]):
            messagebox.showwarning("Warning", self.texts['all_fields'])
            return
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO inventory_log 
                (category, item, original_quantity, original_unit, quantity, type, 
                 purchase_date, entry_date, price, supplier, description, user)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data['category'], data['item'], data['original_quantity'], data['original_unit'],
                  data['quantity'], data['type'], data['purchase_date'], data['entry_date'],
                  data['price'], data['supplier'], data['description'], data['user']))
            self.db_conn.commit()
            
            messagebox.showinfo("Success", self.texts['success'])
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"{self.texts['error']}\n{str(e)}")