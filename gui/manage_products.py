# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import center_window
from database.db import get_raw_inventory, add_product_material, update_product_material, delete_product_material, setup_database
import sqlite3
#تعریف و مدیریت محصولات
class ManageProductsWindow(tk.Toplevel):
    """A window to define and manage products with their required materials per unit."""
    def __init__(self, master, db_conn):
        super().__init__(master)
        self.master = master
        self.db_conn = db_conn
        self.title("مدیریت محصولات")
        
        window_width = 700
        window_height = 500
        center_window(self, window_width, window_height)
        self.resizable(True, True)
        
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        title_label = tk.Label(main_frame, text="تعریف و مدیریت محصولات", font=("Arial", 14, "bold"))
        title_label.pack(pady=5)
        
        self.form_frame = tk.Frame(main_frame)
        self.form_frame.pack(fill="x", pady=5)
        
        tk.Label(self.form_frame, text="نام محصول:", font=("Arial", 10)).grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.product_name = tk.Entry(self.form_frame, font=("Arial", 10), width=25)
        self.product_name.grid(row=0, column=1, padx=2, pady=2)
        
        tk.Label(self.form_frame, text="واحد محصول:", font=("Arial", 10)).grid(row=1, column=0, padx=2, pady=2, sticky="e")
        self.product_unit = tk.Entry(self.form_frame, font=("Arial", 10), width=25)
        self.product_unit.grid(row=1, column=1, padx=2, pady=2)
        
        button_frame = tk.Frame(self.form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(button_frame, text="ثبت محصول", font=("Arial", 10), bg="lightgreen", command=self.add_product).pack(side="left", padx=3)
        self.edit_button = tk.Button(button_frame, text="ویرایش", font=("Arial", 10), bg="lightyellow", command=self.edit_product, state="disabled")
        self.edit_button.pack(side="left", padx=3)
        self.delete_button = tk.Button(button_frame, text="حذف", font=("Arial", 10), bg="lightcoral", command=self.delete_product, state="disabled")
        self.delete_button.pack(side="left", padx=3)
        
        materials_label = tk.Label(main_frame, text="مواد اولیه مصرف‌شده:", font=("Arial", 12, "bold"))
        materials_label.pack(pady=5)
        
        materials_button_frame = tk.Frame(main_frame, bg="lightgray")
        materials_button_frame.pack(fill="x", pady=3)
        tk.Button(materials_button_frame, text="افزودن ماده", font=("Arial", 10), bg="lightblue", command=self.add_material).pack(side="left", padx=5, pady=2)
        self.edit_material_button = tk.Button(materials_button_frame, text="ویرایش ماده", font=("Arial", 10), bg="lightyellow", command=self.edit_material, state="disabled")
        self.edit_material_button.pack(side="left", padx=5, pady=2)
        self.delete_material_button = tk.Button(materials_button_frame, text="حذف ماده", font=("Arial", 10), bg="lightcoral", command=self.delete_material, state="disabled")
        self.delete_material_button.pack(side="left", padx=5, pady=2)
        
        self.materials_tree = ttk.Treeview(main_frame, columns=("id", "item", "quantity_per_unit", "unit"), show="headings", height=6)
        self.materials_tree.heading("id", text="شناسه")
        self.materials_tree.heading("item", text="نام کالا")
        self.materials_tree.heading("quantity_per_unit", text="مقدار مصرفی")
        self.materials_tree.heading("unit", text="واحد")
        self.materials_tree.column("id", width=40, anchor="center")
        self.materials_tree.column("item", width=150, anchor="center")
        self.materials_tree.column("quantity_per_unit", width=120, anchor="center")
        self.materials_tree.column("unit", width=70, anchor="center")
        self.materials_tree.pack(fill="x", pady=3)
        
        materials_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.materials_tree.yview)
        materials_scrollbar.pack(side="right", fill="y")
        self.materials_tree.configure(yscrollcommand=materials_scrollbar.set)
        self.materials_tree.bind("<<TreeviewSelect>>", self.on_material_select)
        
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill="x", pady=5)
        tk.Label(search_frame, text="جستجو:", font=("Arial", 10)).pack(side="left", padx=2)
        self.search_entry = tk.Entry(search_frame, font=("Arial", 10), width=25)
        self.search_entry.pack(side="left", padx=2)
        tk.Button(search_frame, text="جستجو", font=("Arial", 10), command=self.search_products).pack(side="left", padx=2)
        
        self.products_tree = ttk.Treeview(main_frame, columns=("id", "name", "unit"), show="headings", height=8)
        self.products_tree.heading("id", text="شناسه")
        self.products_tree.heading("name", text="نام محصول")
        self.products_tree.heading("unit", text="واحد")
        self.products_tree.column("id", width=40, anchor="center")
        self.products_tree.column("name", width=180, anchor="center")
        self.products_tree.column("unit", width=70, anchor="center")
        self.products_tree.pack(fill="both", expand=True, pady=5)
        
        products_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.products_tree.yview)
        products_scrollbar.pack(side="right", fill="y")
        self.products_tree.configure(yscrollcommand=products_scrollbar.set)
        self.products_tree.bind("<<TreeviewSelect>>", self.on_select)
        
        self.temp_materials = []
        self.selected_product_id = None
        
        self.load_products()
        inventory = get_raw_inventory(self.db_conn)
        self.available_materials = {row[1]: row[3] for row in inventory if row[1]}
        if not self.available_materials:
            messagebox.showwarning("هشدار", "هیچ ماده اولیه‌ای در انبار موجود نیست. لطفاً ابتدا مواد اولیه را اضافه کنید.")
    
    def load_products(self):
        """Load products from the production_log table as a proxy for 'products'."""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT id, product_name, unit FROM production_log GROUP BY product_name ORDER BY id DESC")
            rows = cursor.fetchall()
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            for row in rows:
                self.products_tree.insert("", "end", values=(row[0], row[1], row[2]))
        except sqlite3.Error as e:
            messagebox.showerror("خطا", f"خطا در بارگیری محصولات:\n{e}")
    
    def on_select(self, event):
        """Enable edit/delete buttons and load materials when a product is selected."""
        selected_item = self.products_tree.selection()
        if selected_item:
            self.edit_button.config(state="normal")
            self.delete_button.config(state="normal")
            item = self.products_tree.item(selected_item[0])
            values = item["values"]
            self.product_name.delete(0, tk.END)
            self.product_name.insert(0, values[1])
            self.product_unit.delete(0, tk.END)
            self.product_unit.insert(0, values[2])
            self.selected_product_id = values[0]
            self.temp_materials = []
            self.load_materials(values[0])
        else:
            self.edit_button.config(state="disabled")
            self.delete_button.config(state="disabled")
            self.clear_form()
    
    def on_material_select(self, event):
        """Enable edit/delete material buttons when a row is selected."""
        selected_item = self.materials_tree.selection()
        if selected_item:
            self.edit_material_button.config(state="normal")
            self.delete_material_button.config(state="normal")
        else:
            self.edit_material_button.config(state="disabled")
            self.delete_material_button.config(state="disabled")
    
    def add_product(self):
        """Add a new product and its materials."""
        product_name = self.product_name.get().strip()
        product_unit = self.product_unit.get().strip()
        
        if not all([product_name, product_unit]):
            messagebox.showwarning("هشدار", "لطفاً نام محصول و واحد آن را وارد کنید!")
            return
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT id FROM production_log WHERE product_name = ?", (product_name,))
            if cursor.fetchone():
                messagebox.showwarning("هشدار", "محصولی با این نام قبلاً تعریف شده است!")
                return
            
            # ثبت محصول در production_log (با quantity=0 به عنوان یک نمونه)
            cursor.execute("INSERT INTO production_log (product_name, quantity, unit, production_date) VALUES (?, ?, ?, date('now'))",
                           (product_name, 0, product_unit))
            product_id = cursor.lastrowid
            
            # ثبت مواد اولیه
            for material in self.temp_materials:
                item_name, qty, unit = material
                add_product_material(self.db_conn, product_id, item_name, qty)
            
            self.db_conn.commit()
            messagebox.showinfo("موفقیت", "محصول و مواد اولیه با موفقیت ثبت شدند!")
            self.load_products()
            self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("خطا", f"خطا در ثبت محصول:\n{e}")
    
    def edit_product(self):
        """Edit the selected product and its materials."""
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showwarning("هشدار", "لطفاً یک محصول را انتخاب کنید!")
            return
        
        product_id = self.products_tree.item(selected_item[0])["values"][0]
        product_name = self.product_name.get().strip()
        product_unit = self.product_unit.get().strip()
        
        if not all([product_name, product_unit]):
            messagebox.showwarning("هشدار", "لطفاً نام محصول و واحد آن را وارد کنید!")
            return
        
        try:
            cursor = self.db_conn.cursor()
            # به‌روزرسانی نام محصول در production_log
            cursor.execute("UPDATE production_log SET product_name = ?, unit = ? WHERE id = ?",
                           (product_name, product_unit, product_id))
            
            # حذف مواد اولیه قبلی و ثبت مواد جدید
            cursor.execute("DELETE FROM product_materials WHERE product_id = ?", (product_id,))
            for material in self.temp_materials:
                item_name, qty, unit = material
                add_product_material(self.db_conn, product_id, item_name, qty)
            
            self.db_conn.commit()
            messagebox.showinfo("موفقیت", "محصول و مواد اولیه با موفقیت ویرایش شدند!")
            self.load_products()
            self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("خطا", f"خطا در ویرایش محصول:\n{e}")
    
    def delete_product(self):
        """Delete the selected product and its materials."""
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showwarning("هشدار", "لطفاً یک محصول را انتخاب کنید!")
            return
        
        product_id = self.products_tree.item(selected_item[0])["values"][0]
        if messagebox.askyesno("تأیید حذف", "آیا مطمئن هستید که می‌خواهید این محصول را حذف کنید؟"):
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("DELETE FROM product_materials WHERE product_id = ?", (product_id,))
                cursor.execute("DELETE FROM production_log WHERE id = ?", (product_id,))
                self.db_conn.commit()
                messagebox.showinfo("موفقیت", "محصول با موفقیت حذف شد!")
                self.load_products()
                self.clear_form()
            except sqlite3.Error as e:
                messagebox.showerror("خطا", f"خطا در حذف محصول:\n{e}")
    
    def search_products(self):
        """Search products by name."""
        search_term = self.search_entry.get().strip().lower()
        if not search_term:
            self.load_products()
            return
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT id, product_name, unit FROM production_log WHERE LOWER(product_name) LIKE ? GROUP BY product_name ORDER BY id DESC",
                          ('%' + search_term + '%',))
            rows = cursor.fetchall()
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            for row in rows:
                self.products_tree.insert("", "end", values=(row[0], row[1], row[2]))
        except sqlite3.Error as e:
            messagebox.showerror("خطا", f"خطا در جستجو:\n{e}")
    
    def add_material(self):
        """Add a material to the temporary list or selected product."""
        add_window = tk.Toplevel(self)
        add_window.title("افزودن ماده اولیه")
        center_window(add_window, 300, 200)
        add_window.resizable(False, False)
        
        tk.Label(add_window, text="نام کالا:", font=("Arial", 10)).pack(pady=3)
        inventory = get_raw_inventory(self.db_conn)
        material_items = [row[1] for row in inventory]
        material_combobox = ttk.Combobox(add_window, values=material_items, font=("Arial", 10), width=25)
        material_combobox.pack(pady=3)
        
        tk.Label(add_window, text="مقدار مصرفی برای هر واحد:", font=("Arial", 10)).pack(pady=3)
        material_quantity = tk.Entry(add_window, font=("Arial", 10), width=25)
        material_quantity.pack(pady=3)
        
        tk.Label(add_window, text="واحد:", font=("Arial", 10)).pack(pady=3)
        material_unit_label = tk.Label(add_window, text="", font=("Arial", 10), width=25)
        material_unit_label.pack(pady=3)
        
        def update_unit(event):
            item = material_combobox.get()
            unit = next((row[3] for row in inventory if row[1] == item), "")
            material_unit_label.config(text=unit)
        
        material_combobox.bind("<<ComboboxSelected>>", update_unit)
        
        def add_material_action():
            item = material_combobox.get()
            try:
                qty = float(material_quantity.get())
                unit = next((row[3] for row in inventory if row[1] == item), "")
                if item and qty > 0 and unit:
                    if self.selected_product_id:
                        add_product_material(self.db_conn, self.selected_product_id, item, qty)
                        self.load_materials(self.selected_product_id)
                    else:
                        self.temp_materials.append((item, qty, unit))
                        for item in self.materials_tree.get_children():
                            self.materials_tree.delete(item)
                        for i, (item_name, qty_val, unit_val) in enumerate(self.temp_materials, 1):
                            self.materials_tree.insert("", "end", values=(i, item_name, qty_val, unit_val))
                    add_window.destroy()
                else:
                    messagebox.showwarning("هشدار", "نام کالا، مقدار یا واحد نامعتبر است!")
            except ValueError:
                messagebox.showwarning("هشدار", "لطفاً مقدار را به صورت عددی مثبت وارد کنید!")
        
        tk.Button(add_window, text="افزودن", font=("Arial", 10), bg="lightgreen", command=add_material_action).pack(pady=5)
    
    def edit_material(self):
        """Edit the selected material."""
        selected_material = self.materials_tree.selection()
        if not selected_material:
            messagebox.showwarning("هشدار", "لطفاً یک ماده را انتخاب کنید!")
            return
        
        material_id = self.materials_tree.item(selected_material[0])["values"][0]
        item = self.materials_tree.item(selected_material[0])["values"][1]
        qty = self.materials_tree.item(selected_material[0])["values"][2]
        unit = self.materials_tree.item(selected_material[0])["values"][3]
        
        edit_window = tk.Toplevel(self)
        edit_window.title("ویرایش ماده اولیه")
        center_window(edit_window, 300, 150)
        edit_window.resizable(False, False)
        
        tk.Label(edit_window, text="نام کالا:", font=("Arial", 10)).pack(pady=3)
        tk.Label(edit_window, text=item, font=("Arial", 10)).pack(pady=3)
        
        tk.Label(edit_window, text="مقدار مصرفی برای هر واحد:", font=("Arial", 10)).pack(pady=3)
        material_quantity = tk.Entry(edit_window, font=("Arial", 10), width=25)
        material_quantity.insert(0, qty)
        material_quantity.pack(pady=3)
        
        tk.Label(edit_window, text="واحد:", font=("Arial", 10)).pack(pady=3)
        tk.Label(edit_window, text=unit, font=("Arial", 10)).pack(pady=3)
        
        def edit_material_action():
            try:
                new_qty = float(material_quantity.get())
                if new_qty > 0:
                    if self.selected_product_id:
                        update_product_material(self.db_conn, material_id, new_qty)
                        self.load_materials(self.selected_product_id)
                    else:
                        material_idx = int(material_id) - 1
                        self.temp_materials[material_idx] = (item, new_qty, unit)
                        for material_item in self.materials_tree.get_children():
                            self.materials_tree.delete(material_item)
                        for i, (item_name, qty_val, unit_val) in enumerate(self.temp_materials, 1):
                            self.materials_tree.insert("", "end", values=(i, item_name, qty_val, unit_val))
                    edit_window.destroy()
                else:
                    messagebox.showwarning("هشدار", "مقدار باید مثبت باشد!")
            except ValueError:
                messagebox.showwarning("هشدار", "لطفاً مقدار را به صورت عددی وارد کنید!")
        
        tk.Button(edit_window, text="به‌روزرسانی", font=("Arial", 10), bg="lightgreen", command=edit_material_action).pack(pady=5)
    
    def delete_material(self):
        """Delete the selected material."""
        selected_material = self.materials_tree.selection()
        if not selected_material:
            messagebox.showwarning("هشدار", "لطفاً یک ماده را انتخاب کنید!")
            return
        
        material_id = self.materials_tree.item(selected_material[0])["values"][0]
        if messagebox.askyesno("تأیید حذف", "آیا مطمئن هستید که می‌خواهید این ماده را حذف کنید؟"):
            try:
                if self.selected_product_id:
                    delete_product_material(self.db_conn, material_id)
                    self.load_materials(self.selected_product_id)
                else:
                    material_idx = int(material_id) - 1
                    self.temp_materials.pop(material_idx)
                    for item in self.materials_tree.get_children():
                        self.materials_tree.delete(item)
                    for i, (item_name, qty, unit) in enumerate(self.temp_materials, 1):
                        self.materials_tree.insert("", "end", values=(i, item_name, qty, unit))
            except sqlite3.Error as e:
                messagebox.showerror("خطا", f"خطا در حذف ماده:\n{e}")
    
    def load_materials(self, product_id):
        """Load materials for the selected product."""
        self.selected_product_id = product_id
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT id, item_name, quantity_per_unit FROM product_materials WHERE product_id = ?", (product_id,))
            rows = cursor.fetchall()
            for item in self.materials_tree.get_children():
                self.materials_tree.delete(item)
            
            inventory = get_raw_inventory(self.db_conn)
            
            for row in rows:
                item_name = row[1]
                unit = next((inv_row[3] for inv_row in inventory if inv_row[1] == item_name), "")
                self.materials_tree.insert("", "end", values=(row[0], item_name, row[2], unit))
        except sqlite3.Error as e:
            messagebox.showerror("خطا", f"خطا در بارگیری مواد اولیه:\n{e}")
    
    def clear_form(self):
        """Clear the form after adding or editing."""
        self.product_name.delete(0, tk.END)
        self.product_unit.delete(0, tk.END)
        for item in self.materials_tree.get_children():
            self.materials_tree.delete(item)
        self.temp_materials = []
        self.selected_product_id = None
        self.edit_button.config(state="disabled")
        self.delete_button.config(state="disabled")
        self.edit_material_button.config(state="disabled")
        self.delete_material_button.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    db_conn = setup_database()
    app = ManageProductsWindow(root, db_conn)
    root.mainloop()