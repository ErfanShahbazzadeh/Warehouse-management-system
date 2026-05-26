# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import center_window
import json

class RawInventoryWindow(tk.Toplevel):
    def __init__(self, master, db_conn):
        super().__init__(master)
        self.db_conn = db_conn
        self.current_lang = self.load_language()
        self.texts = self.get_texts(self.current_lang)
        
        self.title(self.texts['title'])
        self.geometry("900x500")
        center_window(self, 900, 500)
        
        self.setup_ui()
        self.load_inventory()
    
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
                'title': 'موجودی مواد اولیه',
                'row': 'ردیف',
                'category': 'دسته',
                'item': 'نام کالا',
                'quantity': 'مقدار',
                'unit': 'واحد',
                'refresh': 'تازه سازی',
                'export': 'خروجی PDF'
            }
        else:
            return {
                'title': 'Raw Material Inventory',
                'row': 'Row',
                'category': 'Category',
                'item': 'Item Name',
                'quantity': 'Quantity',
                'unit': 'Unit',
                'refresh': 'Refresh',
                'export': 'Export PDF'
            }
    
    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg='#34495e', height=40)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)
        
        tk.Button(toolbar, text=self.texts['refresh'], command=self.load_inventory,
                 bg='#3498db', fg='white', padx=15, pady=5).pack(side="left", padx=10, pady=5)
        tk.Button(toolbar, text=self.texts['export'], command=self.export_pdf,
                 bg='#27ae60', fg='white', padx=15, pady=5).pack(side="left", padx=5, pady=5)
        
        # Treeview
        self.tree = ttk.Treeview(self, columns=('row', 'category', 'item', 'quantity', 'unit'), show='headings')
        self.tree.heading('row', text=self.texts['row'])
        self.tree.heading('category', text=self.texts['category'])
        self.tree.heading('item', text=self.texts['item'])
        self.tree.heading('quantity', text=self.texts['quantity'])
        self.tree.heading('unit', text=self.texts['unit'])
        
        self.tree.column('row', width=50, anchor='center')
        self.tree.column('category', width=150, anchor='center')
        self.tree.column('item', width=200, anchor='center')
        self.tree.column('quantity', width=100, anchor='center')
        self.tree.column('unit', width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
    
    def load_inventory(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT category, item, SUM(original_quantity) as total, original_unit
            FROM inventory_log
            WHERE type = 'entry'
            GROUP BY item, original_unit, category
            HAVING total > 0
            ORDER BY category, item
        """)
        
        for i, row in enumerate(cursor.fetchall(), 1):
            self.tree.insert('', 'end', values=(i, row[0] or '-', row[1], row[2], row[3]))
    
    def export_pdf(self):
        messagebox.showinfo("Info", "PDF export feature coming soon!")