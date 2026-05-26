# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import arabic_reshaper
from bidi.algorithm import get_display
from tkinter import filedialog, messagebox
import jdatetime
import os

def register_font():
    """ثبت فونت B Nazanin برای استفاده در PDF."""
    font_path = os.path.join(os.path.dirname(__file__), '..', 'B-NAZANIN.TTF')
    try:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('BNazanin', font_path))
        else:
            raise FileNotFoundError(f"فایل فونت 'B Nazanin.ttf' در مسیر {font_path} یافت نشد.")
    except Exception as e:
        messagebox.showwarning("خطا در فونت", f"فایل فونت 'B Nazanin.ttf' پیدا نشد. لطفاً آن را در مسیر {font_path} قرار دهید. خطا: {e}")
        raise

def export_to_pdf(data, root):
    """ایجاد فایل PDF با داده‌های موجودی مواد اولیه.
    
    Args:
        data (list of tuples): لیست داده‌ها به فرمت (item, original_quantity, original_unit, entry_date, supplier, price)
        root: پنجره ریشه Tkinter برای نمایش پیام‌ها
    """
    # درخواست نام فایل از کاربر
    filename = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile="موجودی_مواد_اولیه.pdf"
    )
    if not filename:
        return

    # ثبت فونت
    try:
        register_font()
    except Exception:
        return

    # ایجاد کانواس PDF
    try:
        c = canvas.Canvas(filename, pagesize=A4)
        c.setFont('BNazanin', 14)

        # افزودن تاریخ و ساعت
        now = jdatetime.datetime.now().strftime("%Y/%m/%d - %H:%M")
        c.setFont('BNazanin', 10)
        c.drawRightString(A4[0] - 2*cm, A4[1] - 2.5*cm, 
                         get_display(arabic_reshaper.reshape(f"تاریخ و ساعت گزارش: {now}")))

        # افزودن عنوان شرکت
        company_title = "شرکت تعاونی مبتکران جوان شهرکرد"
        c.setFont('BNazanin', 14)
        c.drawRightString(A4[0] - 2*cm, A4[1] - 1.5*cm, 
                         get_display(arabic_reshaper.reshape(company_title)))

        # افزودن لوگو (در صورت وجود)
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'logo.jpg')
        if os.path.exists(logo_path):
            logo_width = 3*cm
            logo_height = 3*cm
            c.drawImage(logo_path, A4[0] - logo_width - 2*cm, A4[1] - logo_height - 3*cm, 
                       width=logo_width, height=logo_height)
        else:
            print(f"هشدار: فایل لوگو 'logo.jpg' در مسیر {logo_path} یافت نشد.")

        # افزودن عنوان گزارش
        report_title = "گزارش موجودی مواد اولیه"
        c.setFont('BNazanin', 16)
        c.drawCentredString(A4[0] / 2, A4[1] - 4*cm, 
                           get_display(arabic_reshaper.reshape(report_title)))

        # آماده‌سازی داده‌ها برای جدول
        table_data = [
            [get_display(arabic_reshaper.reshape(col)) for col in 
             ["ردیف", "نام کالا", "مقدار", "واحد", "تاریخ ورود", "تأمین‌کننده", "قیمت"]]
        ]
        for i, row in enumerate(data, 1):
            table_data.append([
                get_display(arabic_reshaper.reshape(str(i))),
                get_display(arabic_reshaper.reshape(str(row[0]))),  # item
                get_display(arabic_reshaper.reshape(str(row[1]))),  # original_quantity
                get_display(arabic_reshaper.reshape(str(row[2]))),  # original_unit
                get_display(arabic_reshaper.reshape(str(row[3]))),  # entry_date
                get_display(arabic_reshaper.reshape(str(row[4]))),  # supplier
                get_display(arabic_reshaper.reshape(str(row[5])))   # price
            ])

        # ایجاد و تنظیم جدول
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'BNazanin', 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2F2F2')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))

        # تنظیم عرض ستون‌ها
        col_widths = [1.5*cm, 3*cm, 2*cm, 2*cm, 3*cm, 3*cm, 2.5*cm]
        table._colWidths = col_widths

        # رسم جدول
        table_width = sum(col_widths)
        x_pos = (A4[0] - table_width) / 2
        table.wrapOn(c, 0, 0)
        table.drawOn(c, x_pos, A4[1] - 6*cm)

        # ذخیره فایل
        c.save()
        messagebox.showinfo("موفقیت", "گزارش با موفقیت ذخیره شد.")

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در ایجاد فایل PDF:\n{str(e)}")

def export_last_changes_to_pdf(db_conn):
    """ایجاد فایل PDF برای آخرین تغییرات انبار."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM inventory_log ORDER BY entry_date DESC")
        data = cursor.fetchall()
        
        if not data:
            messagebox.showwarning("گزارش", "هیچ اطلاعاتی برای تهیه گزارش وجود ندارد.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="گزارش-آخرین-تغییرات.pdf"
        )
        if not filename:
            return
        
        # ثبت فونت
        register_font()
        
        c = canvas.Canvas(filename, pagesize=A4)
        c.setFont('BNazanin', 14)
        
        # افزودن تاریخ و ساعت
        now = jdatetime.datetime.now().strftime("%Y/%m/%d - %H:%M")
        c.setFont('BNazanin', 10)
        c.drawRightString(A4[0] - 2*cm, A4[1] - 1.5*cm, 
                         get_display(arabic_reshaper.reshape(f"تاریخ و ساعت گزارش: {now}")))

        # افزودن عنوان شرکت
        company_title = "شرکت تعاونی مبتکران جوان شهرکرد"
        c.setFont('BNazanin', 12)
        c.drawRightString(A4[0] - 2*cm, A4[1] - 2.5*cm, 
                         get_display(arabic_reshaper.reshape(company_title)))

        # افزودن لوگو
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'logo.jpg')
        if os.path.exists(logo_path):
            logo_width = 3*cm
            logo_height = 3*cm
            c.drawImage(logo_path, A4[0] - logo_width - 2*cm, A4[1] - logo_height - 3*cm, 
                       width=logo_width, height=logo_height)
        else:
            print(f"هشدار: فایل لوگو 'logo.jpg' در مسیر {logo_path} یافت نشد.")

        # افزودن عنوان گزارش
        report_title = "گزارش آخرین تغییرات انبار"
        c.setFont('BNazanin', 16)
        c.drawCentredString(A4[0] / 2, A4[1] - 4*cm, 
                           get_display(arabic_reshaper.reshape(report_title)))

        # آماده‌سازی داده‌ها برای جدول
        headers = ["ردیف", "نام کالا", "مقدار", "نوع", "تاریخ ورود به انبار", "قیمت", "تامین کننده", "توضیحات"]
        table_data = [[get_display(arabic_reshaper.reshape(h)) for h in headers]]
        for i, row in enumerate(data, 1):
            table_data.append([
                get_display(arabic_reshaper.reshape(str(i))),
                get_display(arabic_reshaper.reshape(str(row[2]))),  # item
                get_display(arabic_reshaper.reshape(str(row[3]))),  # quantity
                get_display(arabic_reshaper.reshape(str(row[4]))),  # type
                get_display(arabic_reshaper.reshape(str(row[6]))),  # entry_date
                get_display(arabic_reshaper.reshape(str(row[7]))),  # price
                get_display(arabic_reshaper.reshape(str(row[8]))),  # supplier
                get_display(arabic_reshaper.reshape(str(row[9])))   # description
            ])

        # ایجاد و تنظیم جدول
        col_widths = [1.5*cm, 3*cm, 2*cm, 2*cm, 3*cm, 2.5*cm, 3*cm, 4*cm]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'BNazanin', 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2F2F2')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))

        # رسم جدول
        table_width = sum(col_widths)
        x_pos = (A4[0] - table_width) / 2
        table.wrapOn(c, 0, 0)
        table.drawOn(c, x_pos, A4[1] - 6*cm)

        # ذخیره فایل
        c.save()
        messagebox.showinfo("موفقیت", "گزارش با موفقیت ذخیره شد.")

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در ایجاد فایل PDF:\n{str(e)}")