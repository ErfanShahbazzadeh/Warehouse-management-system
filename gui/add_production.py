# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import center_window
import json
import jdatetime

class AddProductionWindow(tk.Toplevel):
    def __init__(self, master, db_conn):
        super().__init__(master)
        self.db_conn = db_conn
        self.current_lang = self.load_language()
        self.texts = self.get_texts(self.current_lang)
        
        self.title(self.texts['title'])
        self.geometry("600x600")
        center_window(self, 600, 600)
        self.resizable(False, False)
        
        self.setup_ui()
        self.load_products()
    
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
                'title': 'افزودن تولید جدید',
                'product': 'نام محصول:',
                'quantity': 'مقدار تولید:',
                'unit': 'واحد:',
                'date': 'تاریخ تولید:',
                'materials': 'مواد اولیه مورد نیاز:',
                'material': 'نام کالا',
                'required': 'مقدار مورد نیاز',
                'submit': 'ثبت تولید',
                'success': 'تولید با موفقیت ثبت شد!',
                'error': 'خطا در ثبت تولید:'
            }
        else:
            return {
                'title': 'Add New Production',
                'product': 'Product Name:',
                'quantity': 'Production Quantity:',
                'unit': 'Unit:',
                'date': 'Production Date:',
                'materials': 'Required Materials:',
                'material': 'Material Name',
                'required': 'Required Quantity',
                'submit': 'Submit Production',
                'success': 'Production recorded successfully!',
                'error': 'Error recording production:'
            }
    
    def setup_ui(self):
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Product
        tk.Label(main_frame, text=self.texts['product'], font=('Arial', 10)).grid(row=0, column=0, sticky="e", pady=5)
        self.product_combo = ttk.Combobox(main_frame, width=35)
        self.product_combo.grid(row=0, column=1, pady=5, padx=5)
        
        # Quantity
        tk.Label(main_frame, text=self.texts['quantity'], font=('Arial', 10)).grid(row=1, column=0, sticky="e", pady=5)
        self.quantity_entry = tk.Entry(main_frame, width=37)
        self.quantity_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Unit
        tk.Label(main_frame, text=self.texts['unit'], font=('Arial', 10)).grid(row=2, column=0, sticky="e", pady=5)
        self.unit_entry = tk.Entry(main_frame, width=37, state='readonly')
        self.unit_entry.grid(row=2, column=1, pady=5, padx=5)
        self.product_combo.bind('<<ComboboxSelected>>', self.load_product_unit)
        
        # Date
        tk.Label(main_frame, text=self.texts['date'], font=('Arial', 10)).grid(row=3, column=0, sticky="e", pady=5)
        self.date_entry = tk.Entry(main_frame, width=37)
        self.date_entry.grid(row=3, column=1, pady=5, padx=5)
        today = jdatetime.date.today().strftime("%Y/%m/%d")
        self.date_entry.insert(0, today)
        
        # Materials Treeview
        tk.Label(main_frame, text=self.texts['materials'], font=('Arial', 10, 'bold')).grid(row=4, column=0, columnspan=2, pady=10)
        
        self.materials_tree = ttk.Treeview(main_frame, columns=('material', 'required'), show='headings', height=8)
        self.materials_tree.heading('material', text=self.texts['material'])
        self.materials_tree.heading('required', text=self.texts['required'])
        
        self.materials_tree.column('material', width=200, anchor='center')
        self.materials_tree.column('required', width=150, anchor='center')
        
        self.materials_tree.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text=self.texts['submit'], command=self.submit,
                 bg='#27ae60', fg='white', padx=20, pady=5).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy,
                 bg='#95a5a6', fg='white', padx=20, pady=5).pack(side="left", padx=5)
    
    def load_products(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT DISTINCT product_name FROM production_log UNION SELECT product_name FROM products")
        products = [row[0] for row in cursor.fetchall()]
        self.product_combo['values'] = products
    
    def load_product_unit(self, event):
        product = self.product_combo.get()
        if product:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT unit FROM products WHERE product_name = ?", (product,))
            result = cursor.fetchone()
            if result:
                self.unit_entry.config(state='normal')
                self.unit_entry.delete(0, tk.END)
                self.unit_entry.insert(0, result[0])
                self.unit_entry.config(state='readonly')
    
    def submit(self):
        product = self.product_combo.get()
        try:
            quantity = float(self.quantity_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity!")
            return
        
        production_date = self.date_entry.get()
        
        if not product or quantity <= 0:
            messagebox.showwarning("Warning", "Please fill all fields!")
            return
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO production_log (product_name, quantity, unit, production_date, user)
                VALUES (?, ?, ?, ?, ?)
            """, (product, quantity, self.unit_entry.get(), production_date, 'System'))
            self.db_conn.commit()
            
            messagebox.showinfo("Success", self.texts['success'])
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"{self.texts['error']}\n{str(e)}")