# -*- coding: utf-8 -*-
import sqlite3
#پنجره سطح دسترسی کاربر
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

def create_users_table(conn):
    """جدول کاربران (users) را ایجاد می‌کند."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role_id INTEGER,
            FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE SET NULL
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
            UNIQUE(role_id, permission_key)
        )
    """)
    conn.commit()
    
def add_role(conn, role_name):
    """یک سطح دسترسی جدید را به پایگاه داده اضافه می‌کند."""
    cursor = conn.cursor()
    cursor.execute("INSERT INTO roles (role_name) VALUES (?)", (role_name,))
    conn.commit()

def get_all_roles(conn):
    """تمام سطوح دسترسی موجود را بازیابی می‌کند."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roles")
    return cursor.fetchall()

def update_role(conn, role_id, new_name):
    """نام یک سطح دسترسی را ویرایش می‌کند."""
    cursor = conn.cursor()
    cursor.execute("UPDATE roles SET role_name = ? WHERE id = ?", (new_name, role_id))
    conn.commit()

def delete_role(conn, role_id):
    """یک سطح دسترسی را از پایگاه داده حذف می‌کند."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.commit()
    
def get_permissions_for_role(conn, role_id):
    """دسترسی‌های مربوط به یک سطح دسترسی را بازیابی می‌کند."""
    cursor = conn.cursor()
    cursor.execute("SELECT permission_key FROM role_permissions WHERE role_id = ?", (role_id,))
    return [row[0] for row in cursor.fetchall()]

def update_role_permissions(conn, role_id, permissions):
    """دسترسی‌های یک سطح دسترسی را به‌روزرسانی می‌کند."""
    cursor = conn.cursor()
    # ابتدا تمام دسترسی‌های قبلی را حذف می‌کنیم
    cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))
    # سپس دسترسی‌های جدید را اضافه می‌کنیم
    for perm in permissions:
        cursor.execute("INSERT INTO role_permissions (role_id, permission_key) VALUES (?, ?)", (role_id, perm))
    conn.commit()
