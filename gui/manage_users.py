# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database.db import get_all_roles, add_role, update_role, delete_role, get_permissions_for_role, update_role_permissions, get_all_permissions, add_permission, update_permission, delete_permission
import os
#پنجره مدیریت کاربر
class ManageUsersWindow(tk.Toplevel):
    def __init__(self, parent, db_conn):
        super().__init__(parent)
        self.title("مدیریت کاربران و سطوح دسترسی")
        self.geometry("1000x600")
        self.parent = parent
        self.conn = db_conn  # استفاده از اتصال ارسال شده
        self.available_permissions_dict = {} # دیکشنری برای نگهداری دسترسی‌های موجود
        self.setup_ui()
        self.load_roles()
        self.load_permissions()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # قاب مدیریت سطوح دسترسی
        roles_frame = ttk.LabelFrame(main_frame, text="مدیریت سطوح دسترسی", padding="10")
        roles_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)

        # لیست سطوح دسترسی
        role_label = ttk.Label(roles_frame, text="سطوح دسترسی:")
        role_label.pack(anchor=tk.E, pady=5)
        self.role_listbox = tk.Listbox(roles_frame, width=30, height=15)
        self.role_listbox.pack(fill=tk.BOTH, expand=True)
        self.role_listbox.bind("<<ListboxSelect>>", self.on_role_select)

        # ورودی برای نام سطح دسترسی
        role_entry_frame = ttk.Frame(roles_frame)
        role_entry_frame.pack(fill=tk.X, pady=5)
        ttk.Label(role_entry_frame, text="نام سطح دسترسی:").pack(side=tk.RIGHT)
        self.role_name_entry = ttk.Entry(role_entry_frame, width=20)
        self.role_name_entry.pack(side=tk.LEFT, fill=tk.X, padx=5, expand=True)

        # دکمه‌های مدیریت سطوح دسترسی
        role_buttons_frame = ttk.Frame(roles_frame)
        role_buttons_frame.pack(fill=tk.X, pady=5)
        ttk.Button(role_buttons_frame, text="افزودن", command=self.add_role).pack(side=tk.RIGHT, padx=5)
        ttk.Button(role_buttons_frame, text="ویرایش", command=self.edit_role).pack(side=tk.RIGHT, padx=5)
        ttk.Button(role_buttons_frame, text="حذف", command=self.delete_role).pack(side=tk.RIGHT, padx=5)

        # قاب مدیریت دسترسی‌ها
        permissions_management_frame = ttk.LabelFrame(main_frame, text="مدیریت دسترسی‌های برنامه", padding="10")
        permissions_management_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

        ttk.Label(permissions_management_frame, text="لیست دسترسی‌ها:").pack(anchor=tk.E, pady=5)
        self.permissions_listbox = tk.Listbox(permissions_management_frame, width=30, height=15)
        self.permissions_listbox.pack(fill=tk.BOTH, expand=True)

        # ورودی برای نام دسترسی جدید
        perm_entry_frame = ttk.Frame(permissions_management_frame)
        perm_entry_frame.pack(fill=tk.X, pady=5)
        ttk.Label(perm_entry_frame, text="نام دسترسی:").pack(side=tk.RIGHT)
        self.permission_name_entry = ttk.Entry(perm_entry_frame, width=15)
        self.permission_name_entry.pack(side=tk.RIGHT, padx=5)
        ttk.Label(perm_entry_frame, text="کلید:").pack(side=tk.RIGHT)
        self.permission_key_entry = ttk.Entry(perm_entry_frame, width=15)
        self.permission_key_entry.pack(side=tk.RIGHT, padx=5)

        perm_buttons_frame = ttk.Frame(permissions_management_frame)
        perm_buttons_frame.pack(fill=tk.X, pady=5)
        ttk.Button(perm_buttons_frame, text="افزودن دسترسی", command=self.add_new_permission).pack(side=tk.RIGHT, padx=5)
        ttk.Button(perm_buttons_frame, text="ویرایش دسترسی", command=self.edit_new_permission).pack(side=tk.RIGHT, padx=5)
        ttk.Button(perm_buttons_frame, text="حذف دسترسی", command=self.delete_new_permission).pack(side=tk.RIGHT, padx=5)
        self.permissions_listbox.bind("<<ListboxSelect>>", self.on_permission_select)

        # قاب دسترسی‌های سطح کاربری
        role_permissions_frame = ttk.LabelFrame(main_frame, text="دسترسی‌های سطح کاربری", padding="10")
        role_permissions_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Label(role_permissions_frame, text="دسترسی‌ها:").pack(anchor=tk.E, pady=5)
        self.permissions_checkbox_frame = ttk.Frame(role_permissions_frame)
        self.permissions_checkbox_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Button(role_permissions_frame, text="ذخیره دسترسی‌ها", command=self.save_permissions).pack(pady=10)

        # قاب مدیریت کاربران
        users_frame = ttk.LabelFrame(main_frame, text="مدیریت کاربران", padding="10")
        users_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

    def load_roles(self):
        """بارگذاری سطوح دسترسی از پایگاه داده و نمایش در لیست‌باکس."""
        self.role_listbox.delete(0, tk.END)
        self.roles = get_all_roles(self.conn)
        for role in self.roles:
            self.role_listbox.insert(tk.END, role[1])

    def load_permissions(self):
        """بارگذاری دسترسی‌های موجود از پایگاه داده و نمایش در لیست‌باکس."""
        self.permissions_listbox.delete(0, tk.END)
        self.available_permissions = get_all_permissions(self.conn)
        self.available_permissions_dict = {perm[1]: perm[0] for perm in self.available_permissions}
        for perm in self.available_permissions:
            self.permissions_listbox.insert(tk.END, perm[0])

    def add_role(self):
        """افزودن یک سطح دسترسی جدید."""
        role_name = self.role_name_entry.get().strip()
        if not role_name:
            messagebox.showwarning("هشدار", "نام سطح دسترسی نمی‌تواند خالی باشد.")
            return
        try:
            add_role(self.conn, role_name)
            self.load_roles()
            self.role_name_entry.delete(0, tk.END)
            messagebox.showinfo("موفقیت", "سطح دسترسی با موفقیت اضافه شد.")
        except:
            messagebox.showerror("خطا", "این نام سطح دسترسی قبلاً وجود دارد.")

    def edit_role(self):
        """ویرایش نام سطح دسترسی انتخاب‌شده."""
        try:
            selected_index = self.role_listbox.curselection()[0]
            selected_role = self.roles[selected_index]
            new_name = self.role_name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("هشدار", "نام جدید نمی‌تواند خالی باشد.")
                return
            update_role(self.conn, selected_role[0], new_name)
            self.load_roles()
            self.role_name_entry.delete(0, tk.END)
            messagebox.showinfo("موفقیت", "سطح دسترسی با موفقیت ویرایش شد.")
        except IndexError:
            messagebox.showwarning("هشدار", "لطفاً یک سطح دسترسی را برای ویرایش انتخاب کنید.")
        except:
            messagebox.showerror("خطا", "این نام سطح دسترسی قبلاً وجود دارد.")

    def delete_role(self):
        """حذف سطح دسترسی انتخاب‌شده."""
        try:
            selected_index = self.role_listbox.curselection()[0]
            selected_role = self.roles[selected_index]
            if messagebox.askyesno("تأیید حذف", f"آیا مطمئنید که می‌خواهید سطح دسترسی '{selected_role[1]}' را حذف کنید؟"):
                delete_role(self.conn, selected_role[0])
                self.load_roles()
                self.role_name_entry.delete(0, tk.END)
                messagebox.showinfo("موفقیت", "سطح دسترسی با موفقیت حذف شد.")
        except IndexError:
            messagebox.showwarning("هشدار", "لطفاً یک سطح دسترسی را برای حذف انتخاب کنید.")

    def add_new_permission(self):
        """افزودن یک دسترسی جدید به پایگاه داده."""
        perm_name = self.permission_name_entry.get().strip()
        perm_key = self.permission_key_entry.get().strip()
        if not perm_name or not perm_key:
            messagebox.showwarning("هشدار", "نام و کلید دسترسی نمی‌تواند خالی باشد.")
            return
        try:
            add_permission(self.conn, perm_name, perm_key)
            self.load_permissions()
            self.permission_name_entry.delete(0, tk.END)
            self.permission_key_entry.delete(0, tk.END)
            messagebox.showinfo("موفقیت", "دسترسی با موفقیت اضافه شد.")
        except:
            messagebox.showerror("خطا", "این کلید دسترسی قبلاً وجود دارد.")

    def edit_new_permission(self):
        """ویرایش یک دسترسی موجود."""
        try:
            selected_index = self.permissions_listbox.curselection()[0]
            old_perm_key = self.available_permissions[selected_index][1]
            new_name = self.permission_name_entry.get().strip()
            new_key = self.permission_key_entry.get().strip()
            if not new_name or not new_key:
                messagebox.showwarning("هشدار", "نام و کلید جدید نمی‌تواند خالی باشد.")
                return
            update_permission(self.conn, old_perm_key, new_name, new_key)
            self.load_permissions()
            self.permission_name_entry.delete(0, tk.END)
            self.permission_key_entry.delete(0, tk.END)
            messagebox.showinfo("موفقیت", "دسترسی با موفقیت ویرایش شد.")
        except IndexError:
            messagebox.showwarning("هشدار", "لطفاً یک دسترسی را برای ویرایش انتخاب کنید.")
        except:
            messagebox.showerror("خطا", "این کلید دسترسی قبلاً وجود دارد.")

    def delete_new_permission(self):
        """حذف یک دسترسی از پایگاه داده."""
        try:
            selected_index = self.permissions_listbox.curselection()[0]
            perm_key = self.available_permissions[selected_index][1]
            if messagebox.askyesno("تأیید حذف", "آیا مطمئنید که می‌خواهید این دسترسی را حذف کنید؟"):
                delete_permission(self.conn, perm_key)
                self.load_permissions()
                self.permission_name_entry.delete(0, tk.END)
                self.permission_key_entry.delete(0, tk.END)
                messagebox.showinfo("موفقیت", "دسترسی با موفقیت حذف شد.")
        except IndexError:
            messagebox.showwarning("هشدار", "لطفاً یک دسترسی را برای حذف انتخاب کنید.")

    def on_permission_select(self, event):
        """وقتی یک دسترسی انتخاب می‌شود، فیلدهای ورودی را پر می‌کند."""
        try:
            selected_index = self.permissions_listbox.curselection()[0]
            selected_perm = self.available_permissions[selected_index]
            self.permission_name_entry.delete(0, tk.END)
            self.permission_key_entry.delete(0, tk.END)
            self.permission_name_entry.insert(0, selected_perm[0])
            self.permission_key_entry.insert(0, selected_perm[1])
        except IndexError:
            pass

    def on_role_select(self, event):
        """وقتی یک سطح دسترسی انتخاب می‌شود، دسترسی‌های آن را نمایش می‌دهد."""
        try:
            selected_index = self.role_listbox.curselection()[0]
            selected_role = self.roles[selected_index]
            self.role_name_entry.delete(0, tk.END)
            self.role_name_entry.insert(0, selected_role[1])

            # پاک کردن تمام چک‌باکس‌های قدیمی
            for widget in self.permissions_checkbox_frame.winfo_children():
                widget.destroy()
            self.permission_variables = {}

            # بازیابی دسترسی‌های این سطح کاربری
            permissions = get_permissions_for_role(self.conn, selected_role[0])
            
            # ایجاد چک‌باکس‌ها بر اساس لیست دسترسی‌های موجود در پایگاه داده
            for perm_name, perm_key in self.available_permissions_dict.items():
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(self.permissions_checkbox_frame, text=perm_name, variable=var)
                chk.pack(anchor=tk.E, pady=2)
                self.permission_variables[perm_key] = var
                if perm_key in permissions:
                    var.set(True)

        except IndexError:
            pass

    def save_permissions(self):
        """ذخیره دسترسی‌های انتخاب شده برای سطح دسترسی فعلی."""
        try:
            selected_index = self.role_listbox.curselection()[0]
            selected_role = self.roles[selected_index]
            
            # ساخت لیست دسترسی‌های جدید
            selected_permissions = []
            for perm_key, var in self.permission_variables.items():
                if var.get():
                    selected_permissions.append(perm_key)
            
            update_role_permissions(self.conn, selected_role[0], selected_permissions)
            messagebox.showinfo("موفقیت", "دسترسی‌ها با موفقیت به‌روزرسانی شدند.")
        except IndexError:
            messagebox.showwarning("هشدار", "لطفاً یک سطح دسترسی را انتخاب کنید.")
