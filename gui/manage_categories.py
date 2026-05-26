# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from utils.window_utils import center_window
import json

class ManageCategoriesWindow(tk.Toplevel):
    def __init__(self, master, db_conn, refresh_callback=None):
        super().__init__(master)
        self.db_conn = db_conn
        self.refresh_callback = refresh_callback
        self.current_lang = self.load_language()
        self.texts = self.get_texts(self.current_lang)
        
        self.title(self.texts['title'])
        self.geometry("500x400")
        center_window(self, 500, 400)
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
                'title': 'مدیریت دسته بندی ها',
                'existing': 'دسته بندی های موجود:',
                'add': 'افزودن دسته بندی جدید',
                'name': 'نام دسته بندی:',
                'add_btn': 'افزودن',
                'edit': 'ویرایش',
                'delete': 'حذف',
                'close': 'بستن',
                'confirm_delete': 'آیا از حذف این دسته بندی مطمئن هستید؟',
                'enter_name': 'لطفاً نام دسته بندی را وارد کنید!',
                'exists': 'این دسته بندی قبلاً وجود دارد!',
                'success_add': 'دسته بندی با موفقیت اضافه شد.',
                'success_edit': 'دسته بندی با موفقیت ویرایش شد.',
                'success_delete': 'دسته بندی با موفقیت حذف شد.',
                'error': 'خطا: '
            }
        else:
            return {
                'title': 'Manage Categories',
                'existing': 'Existing Categories:',
                'add': 'Add New Category',
                'name': 'Category Name:',
                'add_btn': 'Add',
                'edit': 'Edit',
                'delete': 'Delete',
                'close': 'Close',
                'confirm_delete': 'Are you sure you want to delete this category?',
                'enter_name': 'Please enter category name!',
                'exists': 'This category already exists!',
                'success_add': 'Category added successfully.',
                'success_edit': 'Category edited successfully.',
                'success_delete': 'Category deleted successfully.',
                'error': 'Error: '
            }
    
    def setup_ui(self):
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Existing categories
        tk.Label(main_frame, text=self.texts['existing'], font=('Arial', 11, 'bold')).pack(anchor="w", pady=5)
        
        self.listbox_frame = tk.Frame(main_frame)
        self.listbox_frame.pack(fill="both", expand=True, pady=5)
        
        self.categories_listbox = tk.Listbox(self.listbox_frame, height=8, font=('Arial', 10))
        self.categories_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.listbox_frame, orient="vertical", command=self.categories_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.categories_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        tk.Button(btn_frame, text=self.texts['edit'], command=self.edit_category,
                 bg='#f39c12', fg='white', padx=15, pady=5).pack(side="left", padx=5)
        tk.Button(btn_frame, text=self.texts['delete'], command=self.delete_category,
                 bg='#e74c3c', fg='white', padx=15, pady=5).pack(side="left", padx=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Add new category
        tk.Label(main_frame, text=self.texts['add'], font=('Arial', 11, 'bold')).pack(anchor="w", pady=5)
        
        add_frame = tk.Frame(main_frame)
        add_frame.pack(fill="x", pady=5)
        
        tk.Label(add_frame, text=self.texts['name'], font=('Arial', 10)).pack(side="left", padx=5)
        self.category_name_entry = tk.Entry(add_frame, width=30, font=('Arial', 10))
        self.category_name_entry.pack(side="left", padx=5)
        
        tk.Button(add_frame, text=self.texts['add_btn'], command=self.add_category,
                 bg='#27ae60', fg='white', padx=15, pady=5).pack(side="left", padx=5)
        
        # Close button
        tk.Button(main_frame, text=self.texts['close'], command=self.destroy,
                 bg='#95a5a6', fg='white', padx=20, pady=5).pack(pady=10)
    
    def load_categories(self):
        self.categories_listbox.delete(0, tk.END)
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name")
            for row in cursor.fetchall():
                self.categories_listbox.insert(tk.END, row[0])
        except Exception as e:
            messagebox.showerror("Error", f"{self.texts['error']}{str(e)}")
    
    def add_category(self):
        name = self.category_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", self.texts['enter_name'])
            return
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            self.db_conn.commit()
            messagebox.showinfo("Success", self.texts['success_add'])
            self.category_name_entry.delete(0, tk.END)
            self.load_categories()
            if self.refresh_callback:
                self.refresh_callback()
        except Exception as e:
            messagebox.showerror("Error", f"{self.texts['error']}{str(e)}")
    
    def edit_category(self):
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to edit")
            return
        
        old_name = self.categories_listbox.get(selection[0])
        new_name = simpledialog.askstring("Edit", f"Enter new name for '{old_name}':", initialvalue=old_name)
        
        if new_name and new_name != old_name:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("UPDATE categories SET name = ? WHERE name = ?", (new_name, old_name))
                self.db_conn.commit()
                messagebox.showinfo("Success", self.texts['success_edit'])
                self.load_categories()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Error", f"{self.texts['error']}{str(e)}")
    
    def delete_category(self):
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to delete")
            return
        
        name = self.categories_listbox.get(selection[0])
        if messagebox.askyesno("Confirm", self.texts['confirm_delete']):
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("DELETE FROM categories WHERE name = ?", (name,))
                self.db_conn.commit()
                messagebox.showinfo("Success", self.texts['success_delete'])
                self.load_categories()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Error", f"{self.texts['error']}{str(e)}")