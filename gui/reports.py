# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import center_window
from database.db import get_final_inventory, get_production_report, get_exit_reports, get_raw_inventory
from utils.pdf_generator import export_to_pdf
import jdatetime

class ReportsWindow(tk.Toplevel):
    def __init__(self, parent, db_conn):
        super().__init__(parent)
        self.parent = parent
        self.db_conn = db_conn
        self.title("گزارشات جامع")
        
        window_width = 900
        window_height = 600
        center_window(self, window_width, window_height)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Notebook برای تب‌های مختلف
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # تب موجودی مواد اولیه
        raw_inventory_frame = ttk.Frame(notebook)
        self.setup_raw_inventory_tab(raw_inventory_frame)
        notebook.add(raw_inventory_frame, text="موجودی مواد اولیه")
        
        # تب تولیدات
        production_frame = ttk.Frame(notebook)
        self.setup_production_tab(production_frame)
        notebook.add(production_frame, text="تولیدات")
        
        # تب خروج از انبار
        exit_frame = ttk.Frame(notebook)
        self.setup_exit_tab(exit_frame)
        notebook.add(exit_frame, text="خروج از انبار")
        
        # تب موجودی نهایی
        final_inventory_frame = ttk.Frame(notebook)
        self.setup_final_inventory_tab(final_inventory_frame)
        notebook.add(final_inventory_frame, text="موجودی نهایی")
        
    def setup_raw_inventory_tab(self, parent):
        # Treeview برای نمایش موجودی
        columns = ("item", "quantity", "unit", "category")
        self.raw_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        self.raw_tree.heading("item", text="نام کالا")
        self.raw_tree.heading("quantity", text="مقدار")
        self.raw_tree.heading("unit", text="واحد")
        self.raw_tree.heading("category", text="دسته‌بندی")
        
        self.raw_tree.column("item", width=200)
        self.raw_tree.column("quantity", width=100, anchor="center")
        self.raw_tree.column("unit", width=80, anchor="center")
        self.raw_tree.column("category", width=150)
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.raw_tree.yview)
        self.raw_tree.configure(yscrollcommand=scrollbar.set)
        
        self.raw_tree.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # دکمه بارگذاری
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="بارگذاری داده‌ها", 
                  command=self.load_raw_inventory).pack(side="left", padx=5)
        ttk.Button(button_frame, text="خروجی PDF", 
                  command=self.export_raw_to_pdf).pack(side="left", padx=5)
                  
        # بارگذاری اولیه
        self.load_raw_inventory()
        
    def load_raw_inventory(self):
        for item in self.raw_tree.get_children():
            self.raw_tree.delete(item)
            
        data = get_raw_inventory(self.db_conn)
        for row in data:
            self.raw_tree.insert("", "end", values=row[1:])
            
    def export_raw_to_pdf(self):
        data = get_raw_inventory(self.db_conn)
        if not data:
            messagebox.showwarning("خطا", "هیچ داده‌ای برای خروجی وجود ندارد.")
            return
            
        # فرمت داده برای PDF
        formatted_data = []
        for row in data:
            formatted_data.append((
                row[1],  # نام کالا
                row[2],  # مقدار
                row[3],  # واحد
                row[0],  # دسته‌بندی
                "",      # تامین کننده
                ""       # قیمت
            ))
            
        export_to_pdf(formatted_data, self)
        
    def setup_production_tab(self, parent):
        columns = ("product", "quantity", "unit", "date", "materials")
        self.production_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        self.production_tree.heading("product", text="نام محصول")
        self.production_tree.heading("quantity", text="مقدار")
        self.production_tree.heading("unit", text="واحد")
        self.production_tree.heading("date", text="تاریخ تولید")
        self.production_tree.heading("materials", text="مواد مصرفی")
        
        for col in columns:
            self.production_tree.column(col, width=150)
            
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.production_tree.yview)
        self.production_tree.configure(yscrollcommand=scrollbar.set)
        
        self.production_tree.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="بارگذاری داده‌ها", 
                  command=self.load_production).pack(side="left", padx=5)
                  
        self.load_production()
        
    def load_production(self):
        for item in self.production_tree.get_children():
            self.production_tree.delete(item)
            
        data = get_production_report(self.db_conn)
        for row in data:
            self.production_tree.insert("", "end", values=row)
            
    def setup_exit_tab(self, parent):
        columns = ("item", "quantity", "recipient", "reason", "date")
        self.exit_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        self.exit_tree.heading("item", text="نام کالا")
        self.exit_tree.heading("quantity", text="مقدار")
        self.exit_tree.heading("recipient", text="تحویل‌گیرنده")
        self.exit_tree.heading("reason", text="دلیل")
        self.exit_tree.heading("date", text="تاریخ")
        
        for col in columns:
            self.exit_tree.column(col, width=140)
            
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.exit_tree.yview)
        self.exit_tree.configure(yscrollcommand=scrollbar.set)
        
        self.exit_tree.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="بارگذاری داده‌ها", 
                  command=self.load_exit_reports).pack(side="left", padx=5)
                  
        self.load_exit_reports()
        
    def load_exit_reports(self):
        for item in self.exit_tree.get_children():
            self.exit_tree.delete(item)
            
        data = get_exit_reports(self.db_conn)
        for row in data:
            self.exit_tree.insert("", "end", values=row)
            
    def setup_final_inventory_tab(self, parent):
        columns = ("item", "quantity", "unit", "type")
        self.final_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        self.final_tree.heading("item", text="نام کالا")
        self.final_tree.heading("quantity", text="مقدار")
        self.final_tree.heading("unit", text="واحد")
        self.final_tree.heading("type", text="نوع")
        
        for col in columns:
            self.final_tree.column(col, width=200)
            
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.final_tree.yview)
        self.final_tree.configure(yscrollcommand=scrollbar.set)
        
        self.final_tree.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="بارگذاری داده‌ها", 
                  command=self.load_final_inventory).pack(side="left", padx=5)
                  
        self.load_final_inventory()
        
    def load_final_inventory(self):
        for item in self.final_tree.get_children():
            self.final_tree.delete(item)
            
        data = get_final_inventory(self.db_conn)
        for row in data:
            self.final_tree.insert("", "end", values=row)