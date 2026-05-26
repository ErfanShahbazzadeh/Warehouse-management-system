# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from utils.window_utils import center_window
import json

class ManageItemsWindow(tk.Toplevel):
    def __init__(self, master, db_conn, refresh_callback=None):
        super().__init__(master)
        self.db_conn = db_conn
        self.refresh_callback = refresh_callback
        self.current_lang = self.load_language()
        self.texts = self.get_texts(self.current_lang)
        
        self.title(self.texts['title'])
        self.geometry("600x500")
        center_window(self, 600, 500)
        self.resizable(False, False)
        
        self.setup_ui()
        self.load_categories()
    
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
                'title': 'مدیریت کالاها',
                'select_category': 'انتخاب دسته:',
                'items_list': 'لیست کالاهای این دسته:',
                'add_item': 'افزودن کالا جدید',
                'item_name': 'نام کالا:',
                'unit_type': 'نوع واحد:',
                'add_btn': 'افزودن',
                'edit': 'ویرایش',
                'delete': 'حذف',
                'close': 'بستن',
                'units': ['کیلوگرم', 'گرم', 'لیتر', 'میلی لیتر', 'متر', 'سانتی متر', 'عدد', 'کارتن', 'بسته'],
                'confirm_delete': 'آیا از حذف این کالا مطمئن هستید؟',
                'enter_name': 'لطفاً نام کالا را وارد کنید!',
                'select_unit': 'لطفاً واحد را انتخاب کنید!',
                'select_category_first': 'لطفاً ابتدا یک دسته انتخاب کنید!',
                'exists': 'این کالا قبلاً در این دسته وجود دارد!',
                'success_add': 'کالا با موفقیت اضافه شد.',
                'success_edit': 'کالا با موفقیت ویرایش شد.',
                'success_delete': 'کالا با موفقیت حذف شد.',
                'error': 'خطا: '
            }
        else:
            return {
                'title': 'Manage Items',
                'select_category': 'Select Category:',
                'items_list': 'Items in this category:',
                'add_item': 'Add New Item',
                'item_name': 'Item Name:',
                'unit_type': 'Unit Type:',
                'add_btn': 'Add',
                'edit': 'Edit',
                'delete': 'Delete',
                'close': 'Close',
                'units': ['kilogram', 'gram', 'liter', 'milliliter', 'meter', 'centimeter', 'piece', 'carton', 'package'],
                'confirm_delete': 'Are you sure you want to delete this item?',
                'enter_name': 'Please enter item name!',
                'select_unit': 'Please select unit type!',
                'select_category_first': 'Please select a category first!',
                'exists': 'This item already exists in this category!',
                'success_add': 'Item added successfully.',
                'success_edit': 'Item edited successfully.',
                'success_delete': 'Item deleted successfully.',
                'error': 'Error: '
            }
    
    def setup_ui(self):
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Category selection
        cat_frame = tk.Frame(main_frame)
        cat_frame.pack(fill="x", pady=5)
        
        tk.Label(cat_frame, text=self.texts['select_category'], font=('Arial', 10)).pack(side="left", padx=5)
        self.category_combo = ttk.Combobox(cat_frame, width=30, font=('Arial', 10), state='readonly')
        self.category_combo.pack(side="left", padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', self.load_items)
        
        # Items list
        tk.Label(main_frame, text=self.texts['items_list'], font=('Arial', 11, 'bold')).pack(anchor="w", pady=10)
        
        self.listbox_frame = tk.Frame(main_frame)
        self.listbox_frame.pack(fill="both", expand=True, pady=5)
        
        self.items_listbox = tk.Listbox(self.listbox_frame, height=8, font=('Arial', 10))
        self.items_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.listbox_frame, orient="vertical", command=self.items_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.items_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons for items
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        tk.Button(btn_frame, text=self.texts['edit'], command=self.edit_item,
                 bg='#f39c12', fg='white', padx=15, pady=5).pack(side="left", padx=5)
        tk.Button(btn_frame, text=self.texts['delete'], command=self.delete_item,
                 bg='#e74c3c', fg='white', padx=15, pady=5).pack(side="left", padx=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Add new item
        tk.Label(main_frame, text=self.texts['add_item'], font=('Arial', 11, 'bold')).pack(anchor="w", pady=5)
        
        add_frame = tk.Frame(main_frame)
        add_frame.pack(fill="x", pady=5)
        
        # Item name
        tk.Label(add_frame, text=self.texts['item_name'], font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.item_name_entry = tk.Entry(add_frame, width=25, font=('Arial', 10))
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Unit type
        tk.Label(add_frame, text=self.texts['unit_type'], font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.unit_combo = ttk.Combobox(add_frame, values=self.texts['units'], width=23, font=('Arial', 10), state='readonly')
        self.unit_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Add button
        tk.Button(add_frame, text=self.texts['add_btn'], command=self.add_item,
                 bg='#27ae60', fg='white', padx=15, pady=5).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Close button
        tk.Button(main_frame, text=self.texts['close'], command=self.destroy,
                 bg='#95a5a6', fg='white', padx=20, pady=5).pack(pady=10)
    
    def load_categories(self):
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name")
            categories = [row[0] for row in cursor.fetchall()]
            self.category_combo['values'] = categories
            if categories:
                self.category_combo.set(categories[0])
                self.load_items()
        except Exception as e:
            messagebox.showerror("Error", f"{self.texts['error']}{str(e)}")
    
    def load_items(self, event=None):
        self.items_listbox.delete(0, tk.END)
        category = self.category_combo.get()
        if not category:
            return
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT item_name, unit_type FROM items WHERE category_name = ? ORDER BY item_name", (category,))
            for row in cursor.fetchall():
                self.items_listbox.insert(tk.END, f"{row[0]} ({row[1]})")
        except Exception as e:
            messagebox.showerror("Error", f"{self.texts['error']}{str(e)}")
    
    def add_item(self):
        category = self.category_combo.get()
        if not category:
            messagebox.showwarning("Warning", self.texts['select_category_first'])
            return
        
        item_name = self.item_name_entry.get().strip()
        unit_type = self.unit_combo.get()
        
        if not item_name:
            messagebox.showwarning("Warning", self.texts['enter_name'])
            return
        
        if not unit_type:
            messagebox.showwarning("Warning", self.texts['select_unit'])
            return
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("INSERT INTO items (category_name, item_name, unit_type) VALUES (?, ?, ?)",
                          (category, item_name, unit_type))
            self.db_conn.commit()
            messagebox.showinfo("Success", self.texts['success_add'])
            self.item_name_entry.delete(0, tk.END)
            self.unit_combo.set('')
            self.load_items()
            if self.refresh_callback:
                self.refresh_callback()
        except Exception as e:
            messagebox.showerror("Error", f"{self.texts['error']}{str(e)}")
    
    def edit_item(self):
        selection = self.items_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        selected = self.items_listbox.get(selection[0])
        old_name = selected.split(' (')[0]
        old_unit = selected.split('(')[1].rstrip(')')
        category = self.category_combo.get()
        
        new_name = simpledialog.askstring("Edit", f"Enter new name for '{old_name}':", initialvalue=old_name)
        
        if new_name and new_name != old_name:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("UPDATE items SET item_name = ? WHERE category_name = ? AND item_name = ?",
                              (new_name, category, old_name))
                self.db_conn.commit()
                messagebox.showinfo("Success", self.texts['success_edit'])
                self.load_items()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Error", f"{self.texts['error']}{str(e)}")
    
    def delete_item(self):
        selection = self.items_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        selected = self.items_listbox.get(selection[0])
        item_name = selected.split(' (')[0]
        category = self.category_combo.get()
        
        if messagebox.askyesno("Confirm", self.texts['confirm_delete']):
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("DELETE FROM items WHERE category_name = ? AND item_name = ?", (category, item_name))
                self.db_conn.commit()
                messagebox.showinfo("Success", self.texts['success_delete'])
                self.load_items()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Error", f"{self.texts['error']}{str(e)}")