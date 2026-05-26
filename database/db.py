# -*- coding: utf-8 -*-
import sqlite3
from tkinter import messagebox
import os
import jdatetime
from datetime import datetime

# دیکشنری برای تبدیل واحدهای اصلی به واحدهای مصرفی
UNIT_CONVERSIONS = {
    "کیلوگرم": {"to_unit": "گرم", "multiplier": 1000},
    "گرم": {"to_unit": "گرم", "multiplier": 1},
    "لیتر": {"to_unit": "میلی‌لیتر", "multiplier": 1000},
    "میلی‌لیتر": {"to_unit": "میلی‌لیتر", "multiplier": 1},
    "تن": {"to_unit": "کیلوگرم", "multiplier": 1000},
    "متر": {"to_unit": "سانتی‌متر", "multiplier": 100},
    "سانتی‌متر": {"to_unit": "سانتی‌متر", "multiplier": 1},
    "عدد": {"to_unit": "عدد", "multiplier": 1},
    "کارتن": {"to_unit": "عدد", "multiplier": 1}
}

DB_PATH = os.path.join(os.path.dirname(__file__), "warehouse.db")

def get_connection():
    """اتصال به پایگاه داده را برمی‌گرداند."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("خطای پایگاه داده", f"خطا در اتصال به پایگاه داده:\n{e}")
        return None

def create_roles_table(conn):
    """جدول سطوح دسترسی (roles) را ایجاد می‌کند."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()

def export_to_csv(db_conn, table_name, file_path):
    """Export table to CSV file"""
    import csv
    try:
        cursor = db_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            return False
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)
            writer.writerows(rows)
        
        return True
    except Exception as e:
        print(f"Export error: {str(e)}")
        return False


def create_users_table(conn):
    """جدول کاربران (users) را ایجاد می‌کند."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role_id INTEGER,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE SET NULL
        )
    """)
    conn.commit()

def create_permissions_table(conn):
    """جدول دسترسی‌های برنامه را ایجاد می‌کند."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            key TEXT UNIQUE NOT NULL,
            description TEXT
        )
    """)
    conn.commit()

def create_role_permissions_table(conn):
    """جدول دسترسی‌های سطوح کاربری را ایجاد می‌کند."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            permission_key TEXT NOT NULL,
            FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY(permission_key) REFERENCES permissions(key) ON DELETE CASCADE,
            UNIQUE(role_id, permission_key)
        )
    """)
    conn.commit()

def setup_database():
    """ایجاد جداول لازم در صورت عدم وجود."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # جدول لاگ موجودی
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                item TEXT,
                quantity TEXT, 
                type TEXT,
                original_quantity REAL,
                original_unit TEXT,
                purchase_date TEXT,
                entry_date TEXT,
                price REAL,
                supplier TEXT,
                description TEXT,
                user TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول دسته‌بندی‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول اقلام
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT,
                item_name TEXT,
                unit_type TEXT,
                min_threshold REAL DEFAULT 0,
                max_threshold REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category_name, item_name)
            )
        ''')
        
        # جدول محصولات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT UNIQUE,
                product_name TEXT NOT NULL,
                unit TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول مواد اولیه محصولات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity_per_unit REAL NOT NULL,
                unit TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        ''')
        
        # جدول لاگ تولید
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS production_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                production_date TEXT NOT NULL,
                materials_used TEXT,
                user TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول لاگ خروج از انبار
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                recipient TEXT NOT NULL,
                reason TEXT,
                exit_date TEXT NOT NULL,
                user TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول موجودی فعلی
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS current_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT UNIQUE NOT NULL,
                quantity REAL NOT NULL DEFAULT 0,
                unit TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # افزودن جداول مربوط به مدیریت کاربران و دسترسی‌ها
        create_roles_table(conn)
        create_users_table(conn)
        create_permissions_table(conn)
        create_role_permissions_table(conn)
        
        # درج سطوح دسترسی پیش‌فرض
        cursor.execute("INSERT OR IGNORE INTO roles (role_name) VALUES ('مدیر'), ('کاربر'), ('مشاهده‌گر')")
        
        # درج کاربر پیش‌فرض admin
        import hashlib
        hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password, role_id) 
            VALUES ('admin', ?, (SELECT id FROM roles WHERE role_name = 'مدیر'))
        """, (hashed_password,))
        
        # درج دسترسی‌های پیش‌فرض
        permissions = [
            ('مدیریت مواد اولیه', 'raw_material_manage'),
            ('مدیریت تولید', 'production_manage'),
            ('مدیریت محصولات', 'product_manage'),
            ('خروج از انبار', 'exit_warehouse'),
            ('مشاهده گزارشات', 'view_reports'),
            ('مدیریت کاربران', 'user_manage'),
            ('مدیریت دسترسی‌ها', 'permission_manage')
        ]
        
        for perm in permissions:
            cursor.execute("INSERT OR IGNORE INTO permissions (name, key) VALUES (?, ?)", perm)
        
        conn.commit()
        # print("✅ پایگاه داده با موفقیت راه‌اندازی شد.")
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("خطا در پایگاه داده", f"خطایی در اتصال به پایگاه داده:\n{e}")
        return None

# ================= توابع مواد اولیه =================

def get_raw_inventory(db_conn):
    """محاسبه موجودی کل مواد اولیه بر اساس ورودی‌ها و خروجی‌ها."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT 
                category,
                item,
                SUM(original_quantity) AS total_quantity,
                original_unit,
                supplier,
                AVG(price) as avg_price
            FROM inventory_log 
            WHERE type NOT LIKE '%خروج%'
            GROUP BY item, original_unit, category, supplier
            HAVING total_quantity > 0
            ORDER BY category, item
        """)
        
        rows = cursor.fetchall()
        result = []
        for row in rows:
            category = row[0] or ""
            item_name = row[1]
            total_quantity = row[2]
            original_unit = row[3]
            supplier = row[4] or ""
            avg_price = row[5] or 0
            
            result.append((category, item_name, total_quantity, original_unit, supplier, avg_price))
        return result
    except sqlite3.Error as e:
        messagebox.showerror("خطا", f"خطا در بارگیری موجودی:\n{e}")
        return []

def check_inventory(db_conn, item_name):
    """محاسبه موجودی فعلی یک آیتم خاص."""
    try:
        cursor = db_conn.cursor()
        
        # محاسبه موجودی از لاگ
        cursor.execute("""
            SELECT 
                SUM(CASE 
                    WHEN type LIKE '%خروج%' THEN -original_quantity 
                    ELSE original_quantity 
                END) AS total_quantity
            FROM inventory_log 
            WHERE item = ?
        """, (item_name,))
        
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
    except sqlite3.Error as e:
        messagebox.showerror("خطا", f"خطا در بررسی موجودی:\n{e}")
        return 0

def insert_log_entry(db_conn, data):
    """ثبت اطلاعات ورود یا خروج در جدول inventory_log."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            INSERT INTO inventory_log 
            (category, item, quantity, type, original_quantity, original_unit, 
             purchase_date, entry_date, price, supplier, description, user)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("category", ""), 
            data["item"], 
            data.get("quantity", ""), 
            data.get("type", "ورود"), 
            data.get("original_quantity", 0),
            data.get("original_unit", ""),
            data.get("purchase_date", ""), 
            data.get("entry_date", ""), 
            data.get("price", 0), 
            data.get("supplier", ""), 
            data.get("description", ""), 
            data.get("user", "سیستم")
        ))
        db_conn.commit()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("خطا", f"خطا در ثبت اطلاعات:\n{e}")
        return False

def load_data(db_conn, tree, limit=100):
    """بارگیری ۱۰۰ مورد اخیر از inventory_log."""
    try:
        if tree:
            for item in tree.get_children():
                tree.delete(item)
        
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT * FROM inventory_log 
            ORDER BY entry_date DESC, id DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        if tree:
            for i, row in enumerate(rows):
                tree.insert("", "end", values=(
                    i + 1, 
                    row[2],  # item
                    row[3],  # quantity
                    row[4],  # type
                    row[8],  # entry_date
                    row[12] if len(row) > 12 else "System"  # user
                ))
        
        return rows
    except sqlite3.Error as e:
        print(f"Error loading data: {e}")
        return []


def apply_filter(db_conn, tree, start_date, end_date):
    """فیلتر کردن اطلاعات inventory_log بر اساس تاریخ."""
    if not start_date and not end_date:
        messagebox.showwarning("هشدار", "لطفاً حداقل یک تاریخ را وارد کنید.")
        return []

    try:
        for item in tree.get_children():
            tree.delete(item)

        cursor = db_conn.cursor()
        query = "SELECT * FROM inventory_log WHERE 1=1"
        params = []

        if start_date:
            query += " AND entry_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND entry_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY entry_date DESC, id DESC"
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo("نتیجه جستجو", "هیچ موردی با فیلترهای اعمال شده یافت نشد.")

        for i, row in enumerate(rows):
            tree.insert("", "end", values=(
                i + 1, 
                row[2],  # item
                row[3],  # quantity
                row[4],  # type
                row[8],  # entry_date
                row[12]  # user
            ))
        
        return rows
    except sqlite3.Error as e:
        messagebox.showerror("خطا", f"خطا در فیلتر کردن اطلاعات:\n{e}")
        return []

# ================= توابع تولید =================

def get_product_recipes(db_conn):
    """دریافت دستور ساخت تمام محصولات."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT 
                p.product_name,
                p.unit,
                pm.item_name,
                pm.quantity_per_unit,
                pm.unit as material_unit
            FROM products p
            LEFT JOIN product_materials pm ON p.id = pm.product_id
            ORDER BY p.product_name, pm.item_name
        """)
        
        rows = cursor.fetchall()
        recipes = {}
        
        for row in rows:
            product_name, product_unit, material_name, quantity_per_unit, material_unit = row
            if product_name not in recipes:
                recipes[product_name] = {
                    "unit": product_unit,
                    "materials": []
                }
            if material_name:  # در صورت وجود مواد
                recipes[product_name]["materials"].append({
                    "item": material_name,
                    "quantity_per_unit": quantity_per_unit,
                    "unit": material_unit
                })
        return recipes
    except sqlite3.Error as e:
        messagebox.showerror("خطا", f"خطا در بارگیری دستور ساخت محصولات:\n{e}")
        return {}

def add_production(db_conn, product_name, quantity, unit, date, materials_list, user="سیستم"):
    """ثبت اطلاعات تولید در جدول production_log."""
    cursor = db_conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO production_log (product_name, quantity, unit, production_date, materials_used, user)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_name, quantity, unit, date, str(materials_list), user))
        
        # به‌روزرسانی موجودی مواد اولیه
        for material in materials_list:
            item_name, qty = material
            cursor.execute("""
                UPDATE inventory_log 
                SET original_quantity = original_quantity - ?
                WHERE item = ? AND type NOT LIKE '%خروج%'
            """, (qty, item_name))
        
        db_conn.commit()
        return True
    except sqlite3.Error as e:
        db_conn.rollback()
        messagebox.showerror("خطا", f"خطا در ثبت تولید:\n{e}")
        return False

def update_inventory(db_conn, item, quantity_change):
    """به‌روزرسانی موجودی مواد اولیه."""
    cursor = db_conn.cursor()
    try:
        # ابتدا بررسی می‌کنیم آیا آیتم در جدول جاری موجودی وجود دارد
        cursor.execute("SELECT quantity FROM current_inventory WHERE item = ?", (item,))
        result = cursor.fetchone()
        
        if result:
            # به‌روزرسانی موجودی فعلی
            new_quantity = result[0] + quantity_change
            cursor.execute("""
                UPDATE current_inventory 
                SET quantity = ?, last_updated = CURRENT_TIMESTAMP
                WHERE item = ?
            """, (new_quantity, item))
        else:
            # درج آیتم جدید
            cursor.execute("""
                INSERT INTO current_inventory (item, quantity, unit)
                VALUES (?, ?, ?)
            """, (item, quantity_change, 'عدد'))
        
        db_conn.commit()
        return True
    except sqlite3.Error as e:
        db_conn.rollback()
        messagebox.showerror("خطا", f"خطا در به‌روزرسانی موجودی:\n{e}")
        return False

# ================= توابع محصولات =================

def get_product_materials(db_conn, product_id):
    """بارگذاری مواد مصرفی برای یک محصول."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT id, item_name, quantity_per_unit, unit 
            FROM product_materials 
            WHERE product_id = ?
        """, (product_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("خطا", f"خطا در بارگیری مواد:\n{e}")
        return []

def add_product_material(db_conn, product_id, item, quantity_per_unit, unit="عدد"):
    """اضافه کردن ماده به فرمول محصول."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            INSERT INTO product_materials (product_id, item_name, quantity_per_unit, unit) 
            VALUES (?, ?, ?, ?)
        """, (product_id, item, quantity_per_unit, unit))
        db_conn.commit()
        return True
    except sqlite3.Error as e:
        db_conn.rollback()
        messagebox.showerror("خطا", f"خطا در اضافه کردن ماده:\n{e}")
        return False

def update_product_material(db_conn, material_id, quantity_per_unit):
    """ویرایش مقدار مصرفی ماده."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            UPDATE product_materials 
            SET quantity_per_unit = ? 
            WHERE id = ?
        """, (quantity_per_unit, material_id))
        db_conn.commit()
        return True
    except sqlite3.Error as e:
        db_conn.rollback()
        messagebox.showerror("خطا", f"خطا در ویرایش ماده:\n{e}")
        return False

def delete_product_material(db_conn, material_id):
    """حذف ماده از فرمول محصول."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM product_materials WHERE id = ?", (material_id,))
        db_conn.commit()
        return True
    except sqlite3.Error as e:
        db_conn.rollback()
        messagebox.showerror("خطا", f"خطا در حذف ماده:\n{e}")
        return False

# ================= توابع گزارشات =================

def get_production_report(db_conn):
    """گزارش تولیدات را برمی‌گرداند."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT 
                product_name,
                quantity,
                unit,
                production_date,
                materials_used,
                user
            FROM production_log 
            ORDER BY production_date DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("خطا", f"خطا در دریافت گزارش تولیدات:\n{e}")
        return []

def get_exit_reports(db_conn):
    """گزارش خروج از انبار را برمی‌گرداند."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT 
                item,
                original_quantity,
                supplier as recipient,
                description as reason,
                entry_date,
                user
            FROM inventory_log 
            WHERE type LIKE '%خروج%' 
            ORDER BY entry_date DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("خطا", f"خطا در دریافت گزارش خروج:\n{e}")
        return []

def get_final_inventory(db_conn):
    """موجودی نهایی تمام اقلام را برمی‌گرداند."""
    try:
        cursor = db_conn.cursor()
        
        cursor.execute("""
            SELECT 
                item as name,
                SUM(CASE 
                    WHEN type LIKE '%خروج%' THEN -original_quantity 
                    ELSE original_quantity 
                END) as quantity,
                original_unit as unit,
                CASE 
                    WHEN item IN (SELECT DISTINCT product_name FROM production_log) THEN 'محصول'
                    ELSE 'مواد اولیه'
                END as type
            FROM inventory_log 
            GROUP BY item, original_unit
            HAVING quantity > 0
            ORDER BY type, item
        """)
        
        return cursor.fetchall()
        
    except sqlite3.Error as e:
        messagebox.showerror("خطا", f"خطا در دریافت موجودی نهایی:\n{e}")
        return []

def get_inventory_summary(db_conn):
    """خلاصه موجودی را برمی‌گرداند."""
    try:
        cursor = db_conn.cursor()
        
        # تعداد اقلام مختلف
        cursor.execute("SELECT COUNT(DISTINCT item) FROM inventory_log WHERE type NOT LIKE '%خروج%'")
        total_items = cursor.fetchone()[0] or 0
        
        # تعداد محصولات
        cursor.execute("SELECT COUNT(DISTINCT product_name) FROM production_log")
        total_products = cursor.fetchone()[0] or 0
        
        # تعداد تولیدات
        cursor.execute("SELECT COUNT(*) FROM production_log")
        total_productions = cursor.fetchone()[0] or 0
        
        # تعداد خروج‌ها
        cursor.execute("SELECT COUNT(*) FROM inventory_log WHERE type LIKE '%خروج%'")
        total_exits = cursor.fetchone()[0] or 0
        
        # ارزش کل موجودی
        cursor.execute("""
            SELECT SUM(original_quantity * price) 
            FROM inventory_log 
            WHERE type NOT LIKE '%خروج%' AND price > 0
        """)
        total_value = cursor.fetchone()[0] or 0
        
        return {
            'total_items': total_items,
            'total_products': total_products,
            'total_productions': total_productions,
            'total_exits': total_exits,
            'total_value': total_value
        }
        
    except sqlite3.Error as e:
        messagebox.showerror("خطا", f"خطا در دریافت خلاصه موجودی:\n{e}")
        return {}

# ================= توابع مدیریت کاربران =================

def add_role(conn, role_name):
    """یک سطح دسترسی جدید را به پایگاه داده اضافه می‌کند."""
    cursor = conn.cursor()
    cursor.execute("INSERT INTO roles (role_name) VALUES (?)", (role_name,))
    conn.commit()
    return cursor.lastrowid

def get_all_roles(conn):
    """تمام سطوح دسترسی موجود را بازیابی می‌کند."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, role_name FROM roles ORDER BY id")
    return cursor.fetchall()

def update_role(conn, role_id, new_name):
    """نام یک سطح دسترسی را ویرایش می‌کند."""
    cursor = conn.cursor()
    cursor.execute("UPDATE roles SET role_name = ? WHERE id = ?", (new_name, role_id))
    conn.commit()
    return True

def delete_role(conn, role_id):
    """یک سطح دسترسی را از پایگاه داده حذف می‌کند."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.commit()
    return True
    
def get_permissions_for_role(conn, role_id):
    """دسترسی‌های مربوط به یک سطح دسترسی را بازیابی می‌کند."""
    cursor = conn.cursor()
    cursor.execute("SELECT permission_key FROM role_permissions WHERE role_id = ?", (role_id,))
    return [row[0] for row in cursor.fetchall()]

def update_role_permissions(conn, role_id, permissions):
    """دسترسی‌های یک سطح دسترسی را به‌روزرسانی می‌کند."""
    cursor = conn.cursor()
    try:
        # ابتدا تمام دسترسی‌های قبلی را حذف می‌کنیم
        cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))
        # سپس دسترسی‌های جدید را اضافه می‌کنیم
        for perm in permissions:
            cursor.execute("INSERT INTO role_permissions (role_id, permission_key) VALUES (?, ?)", (role_id, perm))
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False

def get_all_permissions(conn):
    """تمام دسترسی‌های تعریف شده را از پایگاه داده می‌خواند."""
    cursor = conn.cursor()
    cursor.execute("SELECT name, key, description FROM permissions ORDER BY name")
    return cursor.fetchall()

def add_permission(conn, name, key, description=""):
    """یک دسترسی جدید به پایگاه داده اضافه می‌کند."""
    cursor = conn.cursor()
    cursor.execute("INSERT INTO permissions (name, key, description) VALUES (?, ?, ?)", (name, key, description))
    conn.commit()
    return True

def update_permission(conn, old_key, new_name, new_key, description=""):
    """نام و کلید یک دسترسی را ویرایش می‌کند."""
    cursor = conn.cursor()
    cursor.execute("UPDATE permissions SET name = ?, key = ?, description = ? WHERE key = ?", 
                   (new_name, new_key, description, old_key))
    conn.commit()
    return True

def delete_permission(conn, key):
    """یک دسترسی را از پایگاه داده حذف می‌کند."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM permissions WHERE key = ?", (key,))
    conn.commit()
    return True

def get_users(conn):
    """لیست تمام کاربران را برمی‌گرداند."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.username, u.full_name, u.email, u.phone, 
               u.is_active, r.role_name, u.created_at
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        ORDER BY u.created_at DESC
    """)
    return cursor.fetchall()

def add_user(conn, username, password, role_id, full_name="", email="", phone=""):
    """افزودن کاربر جدید."""
    import hashlib
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password, role_id, full_name, email, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, hashed_password, role_id, full_name, email, phone))
    conn.commit()
    return cursor.lastrowid

def update_user(conn, user_id, username, role_id, full_name="", email="", phone="", is_active=1):
    """ویرایش اطلاعات کاربر."""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET username = ?, role_id = ?, full_name = ?, email = ?, phone = ?, is_active = ?
        WHERE id = ?
    """, (username, role_id, full_name, email, phone, is_active, user_id))
    conn.commit()
    return True

def delete_user(conn, user_id):
    """حذف کاربر."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    return True

def change_user_password(conn, user_id, new_password):
    """تغییر رمز عبور کاربر."""
    import hashlib
    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
    
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()
    return True

# ================= توابع کمکی =================

def backup_database(db_conn, backup_path):
    """پشتیبان‌گیری از پایگاه داده."""
    try:
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        return True
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در پشتیبان‌گیری:\n{e}")
        return False

def restore_database(backup_path):
    """بازیابی پایگاه داده از پشتیبان."""
    try:
        import shutil
        shutil.copy2(backup_path, DB_PATH)
        return True
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در بازیابی:\n{e}")
        return False

def export_to_csv(db_conn, table_name, file_path):
    """خروجی CSV از یک جدول."""
    try:
        import csv
        cursor = db_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(rows)
        
        return True
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در خروجی CSV:\n{e}")
        return False