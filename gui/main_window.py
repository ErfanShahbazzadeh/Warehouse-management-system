# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import center_window
import jdatetime
import os
import sys
import json
import hashlib

class MainWindow:
    """Main application window"""
    
    def __init__(self, root, db_conn, user_data):
        self.root = root
        self.db_conn = db_conn
        self.user_data = user_data
        self.log_data = []
        self.filtered_data = []
        self.current_view = "transactions"
        
        # Load language
        self.load_language()
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.refresh_log_display()
        
        # Start time update
        self.update_time()
    
    def load_language(self):
        """Load language from config"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.current_lang = config.get('language', 'en')
        except:
            self.current_lang = 'en'
        
        self.texts = self.get_texts(self.current_lang)
    
    def get_texts(self, lang):
        """Get UI texts"""
        if lang == 'fa':
            return {
                'file': 'فایل',
                'exit': 'خروج',
                'raw_materials': 'مواد اولیه',
                'add_raw': 'افزودن مواد اولیه',
                'view_inventory': 'مشاهده موجودی',
                'production': 'تولیدات',
                'add_production': 'افزودن تولید',
                'manage_products': 'مدیریت محصولات',
                'warehouse': 'انبار',
                'exports': 'صادرات از انبار',
                'export_report': 'گزارش صادرات',
                'reports': 'گزارشات',
                'inventory_report': 'گزارش موجودی',
                'help_menu': 'راهنما',
                'about': 'درباره',
                'settings': 'تنظیمات',
                'language': 'زبان',
                'english': 'انگلیسی',
                'persian': 'فارسی',
                'manage_users': 'مدیریت کاربران',
                'add_user': 'افزودن کاربر',
                'change_password': 'تغییر رمز عبور',
                'dashboard': 'داشبورد',
                'total_items': 'کل اقلام',
                'total_products': 'کل محصولات',
                'total_productions': 'تولیدات',
                'total_exports': 'صادرات',
                'recent_activity': 'فعالیت‌های اخیر',
                'recent_transactions': 'تراکنش‌های اخیر',
                'welcome': 'خوش آمدید',
                'start_date': 'تاریخ شروع',
                'end_date': 'تاریخ پایان',
                'apply_filter': 'اعمال فیلتر',
                'refresh': 'تازه‌سازی',
                'ready': 'آماده',
                'row': 'ردیف',
                'item': 'کالا',
                'quantity': 'مقدار',
                'type': 'نوع',
                'date': 'تاریخ',
                'user': 'کاربر',
                'username': 'نام کاربری',
                'password': 'رمز عبور',
                'confirm_password': 'تکرار رمز عبور',
                'full_name': 'نام کامل',
                'role': 'نقش',
                'cancel': 'انصراف',
                'save': 'ذخیره',
                'delete': 'حذف',
                'items_detail': 'جزئیات اقلام',
                'products_detail': 'جزئیات محصولات',
                'productions_detail': 'جزئیات تولیدات',
                'exports_detail': 'جزئیات صادرات',
                'item_name': 'نام کالا',
                'total_quantity': 'مقدار کل',
                'unit': 'واحد',
                'product_name': 'نام محصول',
                'back_to_transactions': 'بازگشت به تراکنش‌ها',
                'total': 'مجموع',
                'records': 'رکورد',
                'recipient': 'تحویل گیرنده',
                'reason': 'دلیل',
                'production_date': 'تاریخ تولید'
            }
        else:
            return {
                'file': 'File',
                'exit': 'Exit',
                'raw_materials': 'Raw Materials',
                'add_raw': 'Add Raw Material',
                'view_inventory': 'View Inventory',
                'production': 'Production',
                'add_production': 'Add Production',
                'manage_products': 'Manage Products',
                'warehouse': 'Warehouse',
                'exports': 'Exports from Warehouse',
                'export_report': 'Export Report',
                'reports': 'Reports',
                'inventory_report': 'Inventory Report',
                'help_menu': 'Help',
                'about': 'About',
                'settings': 'Settings',
                'language': 'Language',
                'english': 'English',
                'persian': 'Persian',
                'manage_users': 'Manage Users',
                'add_user': 'Add User',
                'change_password': 'Change Password',
                'dashboard': 'DASHBOARD',
                'total_items': 'Total Items',
                'total_products': 'Total Products',
                'total_productions': 'Productions',
                'total_exports': 'Exports',
                'recent_activity': 'RECENT ACTIVITY',
                'recent_transactions': 'RECENT TRANSACTIONS',
                'welcome': 'Welcome',
                'start_date': 'Start Date',
                'end_date': 'End Date',
                'apply_filter': 'Apply Filter',
                'refresh': 'Refresh',
                'ready': 'Ready',
                'row': 'Row',
                'item': 'Item',
                'quantity': 'Qty',
                'type': 'Type',
                'date': 'Date',
                'user': 'User',
                'username': 'Username',
                'password': 'Password',
                'confirm_password': 'Confirm Password',
                'full_name': 'Full Name',
                'role': 'Role',
                'cancel': 'Cancel',
                'save': 'Save',
                'delete': 'Delete',
                'items_detail': 'Items Detail',
                'products_detail': 'Products Detail',
                'productions_detail': 'Productions Detail',
                'exports_detail': 'Exports Detail',
                'item_name': 'Item Name',
                'total_quantity': 'Total Quantity',
                'unit': 'Unit',
                'product_name': 'Product Name',
                'back_to_transactions': 'Back to Transactions',
                'total': 'Total',
                'records': 'Records',
                'recipient': 'Recipient',
                'reason': 'Reason',
                'production_date': 'Production Date'
            }
    
    def change_language(self, lang_code):
        """Change language"""
        self.current_lang = lang_code
        self.texts = self.get_texts(lang_code)
        
        # Save to config
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            config['language'] = lang_code
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
        except:
            with open('config.json', 'w') as f:
                json.dump({'language': lang_code}, f, indent=4)
        
        # Refresh UI
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh all UI texts"""
        self.setup_menubar()
        # Refresh current view
        if self.current_view == "transactions":
            self.refresh_log_display()
        elif self.current_view == "items":
            self.show_items_detail()
        elif self.current_view == "products":
            self.show_products_detail()
        elif self.current_view == "productions":
            self.show_productions_detail()
        elif self.current_view == "exports":
            self.show_exports_detail()
    
    def setup_ui(self):
        """Setup main UI layout"""
        self.setup_menubar()
        self.setup_toolbar()
        
        # Main content area
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left panel - Dashboard summary
        self.setup_summary_panel(main_frame)
        
        # Right panel - Dynamic content
        self.setup_content_panel(main_frame)
        
        # Status bar
        self.setup_statusbar()
    
    def setup_menubar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu - Only Exit
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.texts['exit'], command=self.root.quit)
        menubar.add_cascade(label=self.texts['file'], menu=file_menu)
        
        # Raw Materials menu
        raw_menu = tk.Menu(menubar, tearoff=0)
        raw_menu.add_command(label=self.texts['add_raw'], command=self.open_add_raw_material)
        raw_menu.add_command(label=self.texts['view_inventory'], command=self.open_raw_inventory)
        menubar.add_cascade(label=self.texts['raw_materials'], menu=raw_menu)
        
        # Production menu
        prod_menu = tk.Menu(menubar, tearoff=0)
        prod_menu.add_command(label=self.texts['add_production'], command=self.open_add_production)
        prod_menu.add_command(label=self.texts['manage_products'], command=self.open_manage_products)
        menubar.add_cascade(label=self.texts['production'], menu=prod_menu)
        
        # Warehouse menu - Exports
        warehouse_menu = tk.Menu(menubar, tearoff=0)
        warehouse_menu.add_command(label=self.texts['exports'], command=self.open_exit_warehouse)
        menubar.add_cascade(label=self.texts['warehouse'], menu=warehouse_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        
        # Language submenu
        lang_submenu = tk.Menu(settings_menu, tearoff=0)
        lang_submenu.add_command(label=self.texts['english'], command=lambda: self.change_language('en'))
        lang_submenu.add_command(label=self.texts['persian'], command=lambda: self.change_language('fa'))
        settings_menu.add_cascade(label=self.texts['language'], menu=lang_submenu)
        
        settings_menu.add_separator()
        settings_menu.add_command(label=self.texts['manage_users'], command=self.manage_users)
        settings_menu.add_command(label=self.texts['add_user'], command=self.add_user_dialog)
        settings_menu.add_command(label=self.texts['change_password'], command=self.change_password_dialog)
        
        menubar.add_cascade(label=self.texts['settings'], menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=self.texts['about'], command=self.show_about)
        menubar.add_cascade(label=self.texts['help_menu'], menu=help_menu)
    
    def setup_toolbar(self):
        """Create toolbar with quick actions"""
        toolbar = tk.Frame(self.root, bg='#34495e', height=40)
        toolbar.pack(fill="x", pady=(0, 5))
        toolbar.pack_propagate(False)
        
        buttons = [
            (f"➕ {self.texts['add_raw']}", self.open_add_raw_material),
            (f"🏭 {self.texts['add_production']}", self.open_add_production),
            (f"📤 {self.texts['exports']}", self.open_exit_warehouse),
            (f"🔄 {self.texts['refresh']}", self.refresh_current_view)
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(toolbar, text=text, command=cmd,
                          bg='#34495e', fg='white', font=('Arial', 9),
                          padx=10, pady=5, relief=tk.FLAT)
            btn.pack(side="left", padx=2)
    
    def setup_summary_panel(self, parent):
        """Create summary panel on the left with clickable cards"""
        summary_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        summary_frame.pack(side="left", fill="both", expand=False, padx=(0, 5))
        summary_frame.config(width=280)
        summary_frame.pack_propagate(False)
        
        # Title
        title = tk.Label(summary_frame, text=self.texts['dashboard'], 
                        font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        title.pack(pady=10)
        
        # Summary cards
        cards = [
            ("📦", self.texts['total_items'], "0", self.show_items_detail),
            ("📝", self.texts['total_products'], "0", self.show_products_detail),
            ("🏭", self.texts['total_productions'], "0", self.show_productions_detail),
            ("📤", self.texts['total_exports'], "0", self.show_exports_detail)
        ]
        
        self.summary_labels = []
        for icon, label, value, command in cards:
            card = tk.Frame(summary_frame, bg='#f8f9fa', relief=tk.RAISED, bd=1)
            card.pack(fill="x", padx=10, pady=5)
            
            # Make the entire card clickable
            card.bind('<Button-1>', lambda e, cmd=command: cmd())
            
            # Icon
            icon_label = tk.Label(card, text=icon, font=('Arial', 24), bg='#f8f9fa', cursor='hand2')
            icon_label.pack(side="left", padx=10, pady=10)
            icon_label.bind('<Button-1>', lambda e, cmd=command: cmd())
            
            # Right frame for text
            right_frame = tk.Frame(card, bg='#f8f9fa')
            right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
            right_frame.bind('<Button-1>', lambda e, cmd=command: cmd())
            
            # Label
            lbl = tk.Label(right_frame, text=label, font=('Arial', 9), bg='#f8f9fa', fg='#7f8c8d', cursor='hand2')
            lbl.pack(anchor="e")
            lbl.bind('<Button-1>', lambda e, cmd=command: cmd())
            
            # Value
            value_label = tk.Label(right_frame, text=value, font=('Arial', 20, 'bold'),
                                  bg='#f8f9fa', fg='#3498db', cursor='hand2')
            value_label.pack(anchor="e")
            value_label.bind('<Button-1>', lambda e, cmd=command: cmd())
            self.summary_labels.append(value_label)
        
        # Recent activity
        tk.Label(summary_frame, text=self.texts['recent_activity'], font=('Arial', 10, 'bold'),
                bg='white', fg='#2c3e50').pack(pady=10)
        
        self.recent_listbox = tk.Listbox(summary_frame, height=8, bg='white', font=('Arial', 8))
        self.recent_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.load_summary()
    
    def setup_content_panel(self, parent):
        """Create dynamic content panel on the right"""
        self.content_frame = tk.Frame(parent, bg='#f8f9fa')
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # This frame will be dynamically updated
        self.dynamic_frame = None
        self.show_transactions_view()
    
    def show_transactions_view(self):
        """Show the default transactions view"""
        self.current_view = "transactions"
        
        # Clear existing content
        if self.dynamic_frame:
            self.dynamic_frame.destroy()
        
        self.dynamic_frame = tk.Frame(self.content_frame, bg='#f8f9fa')
        self.dynamic_frame.pack(fill="both", expand=True)
        
        # Welcome message
        welcome_text = f"{self.texts['welcome']}, {self.user_data.get('full_name', self.user_data.get('username'))}!"
        welcome_label = tk.Label(self.dynamic_frame, text=welcome_text,
                                font=('Arial', 14, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        welcome_label.pack(pady=10)
        
        # Filter frame
        filter_frame = tk.Frame(self.dynamic_frame, bg='white', relief=tk.RAISED, bd=1)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        # Date filters
        row = 0
        tk.Label(filter_frame, text=f"{self.texts['start_date']}:", font=('Arial', 9),
                bg='white').grid(row=row, column=0, padx=5, pady=10)
        self.start_date_entry = tk.Entry(filter_frame, width=12, font=('Arial', 9))
        self.start_date_entry.grid(row=row, column=1, padx=5, pady=10)
        
        tk.Label(filter_frame, text=f"{self.texts['end_date']}:", font=('Arial', 9),
                bg='white').grid(row=row, column=2, padx=5, pady=10)
        self.end_date_entry = tk.Entry(filter_frame, width=12, font=('Arial', 9))
        self.end_date_entry.grid(row=row, column=3, padx=5, pady=10)
        
        # Buttons
        apply_btn = tk.Button(filter_frame, text=self.texts['apply_filter'], command=self.apply_filter,
                             bg='#3498db', fg='white', font=('Arial', 9), padx=15, pady=5)
        apply_btn.grid(row=row, column=4, padx=5, pady=10)
        
        # Log display
        log_frame = tk.Frame(self.dynamic_frame, bg='white', relief=tk.RAISED, bd=1)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(log_frame, text=self.texts['recent_transactions'], font=('Arial', 10, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor="w", padx=10, pady=5)
        
        # Treeview
        tree_frame = tk.Frame(log_frame, bg='white')
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        columns = ("row", "item", "quantity", "type", "date", "user")
        self.log_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        headings = [self.texts['row'], self.texts['item'], self.texts['quantity'], 
                   self.texts['type'], self.texts['date'], self.texts['user']]
        widths = [50, 200, 80, 100, 120, 120]
        
        for col, heading, width in zip(columns, headings, widths):
            self.log_tree.heading(col, text=heading)
            self.log_tree.column(col, width=width, anchor="center")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        
        self.log_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_items_detail(self):
        """Show detailed list of all items in the right panel"""
        self.current_view = "items"
        
        # Clear existing content
        if self.dynamic_frame:
            self.dynamic_frame.destroy()
        
        self.dynamic_frame = tk.Frame(self.content_frame, bg='#f8f9fa')
        self.dynamic_frame.pack(fill="both", expand=True)
        
        # Header with back button
        header_frame = tk.Frame(self.dynamic_frame, bg='#f8f9fa')
        header_frame.pack(fill="x", padx=10, pady=10)
        
        back_btn = tk.Button(header_frame, text="← " + self.texts['back_to_transactions'], 
                            command=self.show_transactions_view,
                            bg='#3498db', fg='white', font=('Arial', 9), padx=15, pady=5)
        back_btn.pack(side="left")
        
        title = tk.Label(header_frame, text=self.texts['items_detail'], 
                        font=('Arial', 14, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        title.pack(side="left", padx=20)
        
        # Treeview for items
        tree_frame = tk.Frame(self.dynamic_frame, bg='white', relief=tk.RAISED, bd=1)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=('item', 'quantity', 'unit'), show='headings', height=20)
        tree.heading('item', text=self.texts['item_name'])
        tree.heading('quantity', text=self.texts['total_quantity'])
        tree.heading('unit', text=self.texts['unit'])
        
        tree.column('item', width=250, anchor='center')
        tree.column('quantity', width=150, anchor='center')
        tree.column('unit', width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Load data
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT item, SUM(original_quantity) as total, original_unit
            FROM inventory_log
            WHERE type = 'entry'
            GROUP BY item, original_unit
            HAVING total > 0
            ORDER BY item
        """)
        
        total_qty = 0
        for row in cursor.fetchall():
            tree.insert('', 'end', values=(row[0], row[1], row[2]))
            total_qty += row[1]
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Summary label
        items_count = len(tree.get_children())
        summary_label = tk.Label(self.dynamic_frame, 
                                 text=f"{self.texts['total']}: {items_count} {self.texts['records']} | {self.texts['total_quantity']}: {total_qty}",
                                 font=('Arial', 10, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        summary_label.pack(pady=5)
    
    def show_products_detail(self):
        """Show detailed list of all products in the right panel"""
        self.current_view = "products"
        
        # Clear existing content
        if self.dynamic_frame:
            self.dynamic_frame.destroy()
        
        self.dynamic_frame = tk.Frame(self.content_frame, bg='#f8f9fa')
        self.dynamic_frame.pack(fill="both", expand=True)
        
        # Header with back button
        header_frame = tk.Frame(self.dynamic_frame, bg='#f8f9fa')
        header_frame.pack(fill="x", padx=10, pady=10)
        
        back_btn = tk.Button(header_frame, text="← " + self.texts['back_to_transactions'], 
                            command=self.show_transactions_view,
                            bg='#3498db', fg='white', font=('Arial', 9), padx=15, pady=5)
        back_btn.pack(side="left")
        
        title = tk.Label(header_frame, text=self.texts['products_detail'], 
                        font=('Arial', 14, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        title.pack(side="left", padx=20)
        
        # Treeview for products
        tree_frame = tk.Frame(self.dynamic_frame, bg='white', relief=tk.RAISED, bd=1)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=('product', 'unit'), show='headings', height=20)
        tree.heading('product', text=self.texts['product_name'])
        tree.heading('unit', text=self.texts['unit'])
        
        tree.column('product', width=350, anchor='center')
        tree.column('unit', width=150, anchor='center')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Load data
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT DISTINCT product_name, unit
            FROM products
            ORDER BY product_name
        """)
        
        for row in cursor.fetchall():
            tree.insert('', 'end', values=(row[0], row[1]))
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Summary label
        products_count = len(tree.get_children())
        summary_label = tk.Label(self.dynamic_frame, 
                                 text=f"{self.texts['total']}: {products_count} {self.texts['records']}",
                                 font=('Arial', 10, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        summary_label.pack(pady=5)
    
    def show_productions_detail(self):
        """Show detailed list of all production records in the right panel"""
        self.current_view = "productions"
        
        # Clear existing content
        if self.dynamic_frame:
            self.dynamic_frame.destroy()
        
        self.dynamic_frame = tk.Frame(self.content_frame, bg='#f8f9fa')
        self.dynamic_frame.pack(fill="both", expand=True)
        
        # Header with back button
        header_frame = tk.Frame(self.dynamic_frame, bg='#f8f9fa')
        header_frame.pack(fill="x", padx=10, pady=10)
        
        back_btn = tk.Button(header_frame, text="← " + self.texts['back_to_transactions'], 
                            command=self.show_transactions_view,
                            bg='#3498db', fg='white', font=('Arial', 9), padx=15, pady=5)
        back_btn.pack(side="left")
        
        title = tk.Label(header_frame, text=self.texts['productions_detail'], 
                        font=('Arial', 14, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        title.pack(side="left", padx=20)
        
        # Treeview for productions
        tree_frame = tk.Frame(self.dynamic_frame, bg='white', relief=tk.RAISED, bd=1)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=('product', 'quantity', 'unit', 'date'), show='headings', height=20)
        tree.heading('product', text=self.texts['product_name'])
        tree.heading('quantity', text=self.texts['quantity'])
        tree.heading('unit', text=self.texts['unit'])
        tree.heading('date', text=self.texts['production_date'])
        
        tree.column('product', width=200, anchor='center')
        tree.column('quantity', width=100, anchor='center')
        tree.column('unit', width=80, anchor='center')
        tree.column('date', width=120, anchor='center')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Load data
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT product_name, quantity, unit, production_date
            FROM production_log
            ORDER BY production_date DESC
        """)
        
        total_qty = 0
        for row in cursor.fetchall():
            tree.insert('', 'end', values=(row[0], row[1], row[2], row[3]))
            total_qty += row[1]
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Summary label
        productions_count = len(tree.get_children())
        summary_label = tk.Label(self.dynamic_frame, 
                                 text=f"{self.texts['total']}: {productions_count} {self.texts['records']} | {self.texts['total_quantity']}: {total_qty}",
                                 font=('Arial', 10, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        summary_label.pack(pady=5)
    
    def show_exports_detail(self):
        """Show detailed list of all export records in the right panel"""
        self.current_view = "exports"
        
        # Clear existing content
        if self.dynamic_frame:
            self.dynamic_frame.destroy()
        
        self.dynamic_frame = tk.Frame(self.content_frame, bg='#f8f9fa')
        self.dynamic_frame.pack(fill="both", expand=True)
        
        # Header with back button
        header_frame = tk.Frame(self.dynamic_frame, bg='#f8f9fa')
        header_frame.pack(fill="x", padx=10, pady=10)
        
        back_btn = tk.Button(header_frame, text="← " + self.texts['back_to_transactions'], 
                            command=self.show_transactions_view,
                            bg='#3498db', fg='white', font=('Arial', 9), padx=15, pady=5)
        back_btn.pack(side="left")
        
        title = tk.Label(header_frame, text=self.texts['exports_detail'], 
                        font=('Arial', 14, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        title.pack(side="left", padx=20)
        
        # Treeview for exports
        tree_frame = tk.Frame(self.dynamic_frame, bg='white', relief=tk.RAISED, bd=1)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=('item', 'quantity', 'unit', 'recipient', 'reason', 'date'), show='headings', height=20)
        tree.heading('item', text=self.texts['item_name'])
        tree.heading('quantity', text=self.texts['quantity'])
        tree.heading('unit', text=self.texts['unit'])
        tree.heading('recipient', text=self.texts['recipient'])
        tree.heading('reason', text=self.texts['reason'])
        tree.heading('date', text=self.texts['date'])
        
        tree.column('item', width=150, anchor='center')
        tree.column('quantity', width=80, anchor='center')
        tree.column('unit', width=60, anchor='center')
        tree.column('recipient', width=120, anchor='center')
        tree.column('reason', width=150, anchor='center')
        tree.column('date', width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Load data
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT item, original_quantity, original_unit, supplier, description, entry_date
            FROM inventory_log
            WHERE type = 'exit'
            ORDER BY entry_date DESC
        """)
        
        total_qty = 0
        for row in cursor.fetchall():
            tree.insert('', 'end', values=(row[0], abs(row[1]), row[2], row[3], row[4], row[5]))
            total_qty += abs(row[1])
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Summary label
        exports_count = len(tree.get_children())
        summary_label = tk.Label(self.dynamic_frame, 
                                 text=f"{self.texts['total']}: {exports_count} {self.texts['records']} | {self.texts['total_quantity']}: {total_qty}",
                                 font=('Arial', 10, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        summary_label.pack(pady=5)
    
    def refresh_current_view(self):
        """Refresh the currently displayed view"""
        if self.current_view == "transactions":
            self.refresh_log_display()
        elif self.current_view == "items":
            self.show_items_detail()
        elif self.current_view == "products":
            self.show_products_detail()
        elif self.current_view == "productions":
            self.show_productions_detail()
        elif self.current_view == "exports":
            self.show_exports_detail()
    
    def setup_statusbar(self):
        """Create status bar at bottom"""
        status_bar = tk.Frame(self.root, bg='#34495e', height=25)
        status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(status_bar, text=self.texts['ready'], bg='#34495e', fg='white', font=('Arial', 8))
        self.status_label.pack(side="left", padx=10)
        
        self.time_label = tk.Label(status_bar, text="", bg='#34495e', fg='white', font=('Arial', 8))
        self.time_label.pack(side="right", padx=10)
    
    def load_summary(self):
        """Load dashboard summary"""
        try:
            cursor = self.db_conn.cursor()
            
            cursor.execute("SELECT COUNT(DISTINCT item) FROM inventory_log WHERE type = 'entry'")
            total_items = cursor.fetchone()[0] or 0
            self.summary_labels[0].config(text=str(total_items))
            
            cursor.execute("SELECT COUNT(DISTINCT product_name) FROM products")
            total_products = cursor.fetchone()[0] or 0
            self.summary_labels[1].config(text=str(total_products))
            
            cursor.execute("SELECT COUNT(*) FROM production_log")
            total_productions = cursor.fetchone()[0] or 0
            self.summary_labels[2].config(text=str(total_productions))
            
            cursor.execute("SELECT COUNT(*) FROM inventory_log WHERE type = 'exit'")
            total_exports = cursor.fetchone()[0] or 0
            self.summary_labels[3].config(text=str(total_exports))
            
            # Load recent activity
            self.recent_listbox.delete(0, tk.END)
            cursor.execute("SELECT entry_date, item, type FROM inventory_log ORDER BY id DESC LIMIT 5")
            for row in cursor.fetchall():
                type_text = "Entry" if row[2] == 'entry' else "Export"
                self.recent_listbox.insert(tk.END, f"{row[0]} - {row[1]} ({type_text})")
                
        except Exception as e:
            print(f"Error loading summary: {e}")
    
    def refresh_log_display(self):
        """Refresh the log display"""
        try:
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)
            
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT item, quantity, type, entry_date, user 
                FROM inventory_log 
                ORDER BY id DESC LIMIT 100
            """)
            
            for i, row in enumerate(cursor.fetchall(), 1):
                type_text = "Entry" if row[2] == 'entry' else "Export"
                self.log_tree.insert("", "end", values=(i, row[0], row[1], type_text, row[3], row[4] or "System"))
            
            self.status_label.config(text=self.texts['ready'])
            self.load_summary()
            
        except Exception as e:
            print(f"Error refreshing log: {e}")
    
    def apply_filter(self):
        """Apply date filter"""
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        
        if not start_date and not end_date:
            messagebox.showwarning("Warning", "Please enter at least one date")
            return
        
        try:
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)
            
            cursor = self.db_conn.cursor()
            query = "SELECT item, quantity, type, entry_date, user FROM inventory_log WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND entry_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND entry_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY id DESC"
            cursor.execute(query, params)
            
            for i, row in enumerate(cursor.fetchall(), 1):
                type_text = "Entry" if row[2] == 'entry' else "Export"
                self.log_tree.insert("", "end", values=(i, row[0], row[1], type_text, row[3], row[4] or "System"))
            
            self.status_label.config(text="Filter applied")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {str(e)}")
    
    def update_time(self):
        """Update time display"""
        now = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Warehouse Manager v2.0\n\nComplete Warehouse Management System")
    
    def manage_users(self):
        """Open user management window"""
        win = tk.Toplevel(self.root)
        win.title(self.texts['manage_users'])
        win.geometry("800x500")
        center_window(win, 800, 500)
        
        columns = ("id", "username", "full_name", "role", "status")
        tree = ttk.Treeview(win, columns=columns, show="headings", height=15)
        tree.heading("id", text="ID")
        tree.heading("username", text=self.texts['username'])
        tree.heading("full_name", text=self.texts['full_name'])
        tree.heading("role", text=self.texts['role'])
        tree.heading("status", text="Status")
        
        tree.column("id", width=50)
        tree.column("username", width=150)
        tree.column("full_name", width=200)
        tree.column("role", width=100)
        tree.column("status", width=100)
        
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.full_name, r.role_name, u.is_active
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
        """)
        
        for row in cursor.fetchall():
            status = "Active" if row[4] == 1 else "Inactive"
            tree.insert("", "end", values=(row[0], row[1], row[2] or "", row[3] or "user", status))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_frame = tk.Frame(win)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        def delete_user():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a user")
                return
            
            values = tree.item(selected[0])['values']
            if values[1] == 'admin':
                messagebox.showwarning("Warning", "Cannot delete admin user")
                return
            
            if messagebox.askyesno("Confirm", f"Delete user '{values[1]}'?"):
                cursor.execute("DELETE FROM users WHERE id = ?", (values[0],))
                self.db_conn.commit()
                tree.delete(selected[0])
                messagebox.showinfo("Success", "User deleted")
        
        def toggle_status():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a user")
                return
            
            values = tree.item(selected[0])['values']
            if values[1] == 'admin':
                messagebox.showwarning("Warning", "Cannot modify admin user")
                return
            
            new_status = 0 if values[4] == "Active" else 1
            cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, values[0]))
            self.db_conn.commit()
            
            status_text = "Active" if new_status == 1 else "Inactive"
            tree.item(selected[0], values=(values[0], values[1], values[2], values[3], status_text))
        
        tk.Button(btn_frame, text=self.texts['delete'], command=delete_user,
                 bg='#e74c3c', fg='white', padx=20, pady=5).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Toggle Status", command=toggle_status,
                 bg='#f39c12', fg='white', padx=20, pady=5).pack(side="left", padx=5)
        tk.Button(btn_frame, text=self.texts['cancel'], command=win.destroy,
                 bg='#95a5a6', fg='white', padx=20, pady=5).pack(side="right", padx=5)
    
    def add_user_dialog(self):
        """Add new user dialog"""
        win = tk.Toplevel(self.root)
        win.title(self.texts['add_user'])
        win.geometry("400x450")
        center_window(win, 400, 450)
        win.resizable(False, False)
        
        frame = tk.Frame(win, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text=self.texts['username'] + ":", font=('Arial', 10)).pack(anchor="w", pady=5)
        username_entry = tk.Entry(frame, font=('Arial', 11), width=30)
        username_entry.pack(fill="x", pady=5)
        
        tk.Label(frame, text=self.texts['full_name'] + ":", font=('Arial', 10)).pack(anchor="w", pady=5)
        fullname_entry = tk.Entry(frame, font=('Arial', 11), width=30)
        fullname_entry.pack(fill="x", pady=5)
        
        tk.Label(frame, text=self.texts['password'] + ":", font=('Arial', 10)).pack(anchor="w", pady=5)
        password_entry = tk.Entry(frame, font=('Arial', 11), width=30, show="•")
        password_entry.pack(fill="x", pady=5)
        
        tk.Label(frame, text=self.texts['confirm_password'] + ":", font=('Arial', 10)).pack(anchor="w", pady=5)
        confirm_entry = tk.Entry(frame, font=('Arial', 11), width=30, show="•")
        confirm_entry.pack(fill="x", pady=5)
        
        tk.Label(frame, text=self.texts['role'] + ":", font=('Arial', 10)).pack(anchor="w", pady=5)
        role_var = tk.StringVar(value="user")
        role_frame = tk.Frame(frame)
        role_frame.pack(fill="x", pady=5)
        tk.Radiobutton(role_frame, text="Admin", variable=role_var, value="admin").pack(side="left", padx=10)
        tk.Radiobutton(role_frame, text="User", variable=role_var, value="user").pack(side="left", padx=10)
        
        def save_user():
            username = username_entry.get().strip()
            fullname = fullname_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            role = role_var.get()
            
            if not username or not password:
                messagebox.showwarning("Warning", "Username and password are required")
                return
            
            if password != confirm:
                messagebox.showwarning("Warning", "Passwords do not match")
                return
            
            if len(password) < 4:
                messagebox.showwarning("Warning", "Password must be at least 4 characters")
                return
            
            try:
                cursor = self.db_conn.cursor()
                
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    messagebox.showwarning("Warning", "Username already exists")
                    return
                
                cursor.execute("SELECT id FROM roles WHERE role_name = ?", (role,))
                role_result = cursor.fetchone()
                role_id = role_result[0] if role_result else None
                
                hashed = hashlib.sha256(password.encode()).hexdigest()
                
                cursor.execute("""
                    INSERT INTO users (username, password, role_id, full_name, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """, (username, hashed, role_id, fullname))
                
                self.db_conn.commit()
                messagebox.showinfo("Success", f"User '{username}' added successfully")
                win.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add user: {str(e)}")
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=20)
        
        tk.Button(btn_frame, text=self.texts['save'], command=save_user,
                 bg='#27ae60', fg='white', padx=20, pady=5).pack(side="left", padx=5)
        tk.Button(btn_frame, text=self.texts['cancel'], command=win.destroy,
                 bg='#95a5a6', fg='white', padx=20, pady=5).pack(side="right", padx=5)
    
    def change_password_dialog(self):
        """Change password dialog"""
        win = tk.Toplevel(self.root)
        win.title(self.texts['change_password'])
        win.geometry("400x350")
        center_window(win, 400, 350)
        win.resizable(False, False)
        
        frame = tk.Frame(win, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="Current Password:", font=('Arial', 10)).pack(anchor="w", pady=5)
        current_entry = tk.Entry(frame, font=('Arial', 11), width=30, show="•")
        current_entry.pack(fill="x", pady=5)
        
        tk.Label(frame, text="New Password:", font=('Arial', 10)).pack(anchor="w", pady=5)
        new_entry = tk.Entry(frame, font=('Arial', 11), width=30, show="•")
        new_entry.pack(fill="x", pady=5)
        
        tk.Label(frame, text="Confirm New Password:", font=('Arial', 10)).pack(anchor="w", pady=5)
        confirm_entry = tk.Entry(frame, font=('Arial', 11), width=30, show="•")
        confirm_entry.pack(fill="x", pady=5)
        
        def change():
            current = current_entry.get()
            new_pass = new_entry.get()
            confirm = confirm_entry.get()
            
            if not current or not new_pass:
                messagebox.showwarning("Warning", "Please fill all fields")
                return
            
            if new_pass != confirm:
                messagebox.showwarning("Warning", "New passwords do not match")
                return
            
            if len(new_pass) < 4:
                messagebox.showwarning("Warning", "Password must be at least 4 characters")
                return
            
            hashed_current = hashlib.sha256(current.encode()).hexdigest()
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT password FROM users WHERE id = ?", (self.user_data['id'],))
            stored = cursor.fetchone()
            
            if not stored or stored[0] != hashed_current:
                messagebox.showwarning("Warning", "Current password is incorrect")
                return
            
            hashed_new = hashlib.sha256(new_pass.encode()).hexdigest()
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_new, self.user_data['id']))
            self.db_conn.commit()
            
            messagebox.showinfo("Success", "Password changed successfully")
            win.destroy()
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=20)
        
        tk.Button(btn_frame, text="Change", command=change,
                 bg='#27ae60', fg='white', padx=20, pady=5).pack(side="left", padx=5)
        tk.Button(btn_frame, text=self.texts['cancel'], command=win.destroy,
                 bg='#95a5a6', fg='white', padx=20, pady=5).pack(side="right", padx=5)
    
    # Window methods
    def open_add_raw_material(self):
        from gui.add_raw_material import AddRawMaterialWindow
        AddRawMaterialWindow(self.root, self.refresh_log_display, self.db_conn)
    
    def open_raw_inventory(self):
        from gui.view_raw_inventory import RawInventoryWindow
        RawInventoryWindow(self.root, self.db_conn)
    
    def open_add_production(self):
        from gui.add_production import AddProductionWindow
        AddProductionWindow(self.root, self.db_conn)
    
    def open_manage_products(self):
        from gui.manage_products import ManageProductsWindow
        ManageProductsWindow(self.root, self.db_conn)
    
    def open_exit_warehouse(self):
        from gui.exit_warehouse import ExitWarehouseWindow
        ExitWarehouseWindow(self.root, self.db_conn, self.refresh_log_display)