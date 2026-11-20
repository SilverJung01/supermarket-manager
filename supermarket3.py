# ==============================
# 1. ایمپورت‌ها و راه‌اندازی دیتابیس
# ==============================
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

DB_NAME = 'supermarket.db'


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
           CREATE TABLE IF NOT EXISTS products(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               buy_price REAL NOT NULL,
               sell_price REAL NOT NULL,
               quantity INTEGER NOT NULL
            )
        """)

        conn.commit()
        conn.close()
    except sqlite3.Error as err:
        messagebox.showerror('خطا', f'خطا در ایجاد جدول:\n{err}')


# ==============================
# 2. بارگذاری و جستجوی داده‌ها
# ==============================
def load_data(search_query=None):
    for row in tree.get_children():
        tree.delete(row)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if search_query:
            query = 'SELECT * FROM products WHERE name LIKE ?'
            cursor.execute(query, (f'%{search_query}%',))
        else:
            cursor.execute('SELECT * FROM products')

        rows = cursor.fetchall()
        for row in rows:
            tree.insert('', tk.END, values=row)

        conn.close()
    except sqlite3.Error as err:
        messagebox.showerror('خطا', f'خطا در دریافت اطلاعات:\n{err}')


# ==============================
# 3. پاک‌کردن فرم
# ==============================
def clear_entries():
    entry_name.delete(0, tk.END)
    entry_buy.delete(0, tk.END)
    entry_sell.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_search.delete(0, tk.END)
    load_data()


# ==============================
# 4. انتخاب ردیف از جدول
# ==============================
def on_row_select(event):
    selected_item = tree.selection()
    if not selected_item:
        return
    values = tree.item(selected_item)['values']
    if len(values) >= 5:
        entry_name.delete(0, tk.END)
        entry_name.insert(0, values[1])

        entry_buy.delete(0, tk.END)
        entry_buy.insert(0, values[2])

        entry_sell.delete(0, tk.END)
        entry_sell.insert(0, values[3])

        entry_qty.delete(0, tk.END)
        entry_qty.insert(0, values[4])

# ==============================
# 5 و 6. افزودن کالا
# (خواندن ورودی‌ها، اعتبارسنجی و ذخیره)
# ==============================
def add_product():
    # --- 5. خواندن ورودی‌ها ---
    name = entry_name.get().strip()
    buy_p = entry_buy.get().strip()
    sell_p = entry_sell.get().strip()
    qty = entry_qty.get().strip()

    # --- 6. اعتبارسنجی و ذخیره ---
    if not name or not buy_p or not sell_p or not qty:
        messagebox.showerror('خطا', 'لطفا تمامی فیلد هارا پر کنید!')
        return

    try:
        buy_p = float(buy_p)
        sell_p = float(sell_p)
        qty = int(qty)
    except ValueError:
        messagebox.showerror('خطا', 'قیمت ها باید عدد و تعداد باید عدد صحیح باشند.')
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = 'INSERT INTO products (name, buy_price, sell_price, quantity) VALUES (?, ?, ?, ?)'
        cursor.execute(sql, (name, buy_p, sell_p, qty))

        conn.commit()
        conn.close()

        messagebox.showinfo('موفقیت', 'کالا با موفقیت ثبت شد.')
        clear_entries()

    except sqlite3.Error as err:
        messagebox.showerror('خطا', f'خطا در ثبت کالا:\n{err}')


# ==============================
# 7. جستجوی کالا
# ==============================
def search_product():
    query = entry_search.get().strip()
    load_data(query)


# ==============================
# 8. حذف کالا
# ==============================
def delete_product():
    selected_item = tree.selection()

    if not selected_item:
        messagebox.showwarning(
            'هشدار', 'لطفا ابتدا یک سطر را از جدول انتخاب کنید.'
        )
        return

    product_id = tree.item(selected_item)['values'][0]
    confirm = messagebox.askyesno('تایید حذف', 'آیا از حذف این کالا مطمئن هستید؟')

    if confirm:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))

            conn.commit()
            conn.close()

            messagebox.showinfo('موفقیت', 'کالا با موفقیت حذف شد.')
            clear_entries()

        except sqlite3.Error as err:
            messagebox.showerror('خطا', f'خطا در حذف:\n{err}')


# ==============================
# 9. ویرایش کالا
# ==============================
def edit_product():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning('هشدار', 'اول یک سطر را از جدول انتخاب کنید.')
        return

    product_id = tree.item(selected_item)['values'][0]
    name = entry_name.get().strip()
    buy_p = entry_buy.get().strip()
    sell_p = entry_sell.get().strip()
    qty = entry_qty.get().strip()

    if not name or not buy_p or not sell_p or not qty:
        messagebox.showerror('خطا', 'فیلد ها نباید خالی باشند.')
        return

    try:
        buy_p = float(buy_p)
        sell_p = float(sell_p)
        qty = int(qty)
    except ValueError:
        messagebox.showerror('خطا', 'مقادیر عددی نامعتبر هستند.')
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """UPDATE products
                 SET name = ?, buy_price = ?, sell_price = ?, quantity = ?
                 WHERE id = ?"""
        cursor.execute(sql, (name, buy_p, sell_p, qty, product_id))
        conn.commit()
        conn.close()

        messagebox.showinfo('موفقیت', 'اطلاعات کالا با موفقیت ویرایش شد.')
        clear_entries()
    except sqlite3.Error as err:
        messagebox.showerror('خطا', f'خطا در ویرایش:\n{err}')


# ==============================
# 10. ساخت پنجره اصلی
# ==============================
root = tk.Tk()
root.title('مدیریت محصولات - سوپرمارکت مسعود')
root.geometry('850x550')


# ==============================
# 11. فرم ورود اطلاعات
# ==============================
frame_form = tk.LabelFrame(root, text='اطلاعات کالا', padx=10, pady=10)
frame_form.pack(fill='x', padx=10, pady=10)

# 
# tk.Label(frame_form, text='x').grid(row=1, column=1, sticky='e', padx=5, pady=5)
# entry_x= tk.Entry(frame_form, width=15)
# entry_x.grid(row=1, column=0, padx=5, pady=5)
# 

tk.Label(frame_form, text='نام کالا:').grid(
    row=0, column=3, sticky='e', padx=5, pady=5)

entry_name = tk.Entry(frame_form, width=20)
entry_name.grid(row=0, column=2, padx=5, pady=5)

tk.Label(frame_form, text='قیمت خرید:').grid(
    row=0, column=1, sticky='e', padx=5, pady=5)

entry_buy = tk.Entry(frame_form, width=15)
entry_buy.grid(row=0, column=0, padx=5, pady=5)

tk.Label(frame_form, text='قیمت فروش:').grid(
    row=1, column=3, sticky='e', padx=5, pady=5)

entry_sell = tk.Entry(frame_form, width=20)
entry_sell.grid(row=1, column=2, padx=5, pady=5)

tk.Label(frame_form, text='تعداد:').grid(
    row=1, column=1, sticky='e', padx=5, pady=5)

entry_qty = tk.Entry(frame_form, width=15)
entry_qty.grid(row=1, column=0, padx=5, pady=5)


# ==============================
# 12. دکمه‌های عملیات
# ==============================
frame_btns = tk.Frame(root, pady=5)
frame_btns.pack(fill='x', padx=10)

tk.Button(
    frame_btns,
    text='افزودن کالا',
    bg='#4CAF50',
    fg='white',
    width=12,
    command=add_product,
).pack(side='right', padx=5)
tk.Button(
    frame_btns,
    text='ویرایش کالا',
    bg='#2196F3',
    fg='white',
    width=12,
    command=edit_product,
).pack(side='right', padx=5)
tk.Button(
    frame_btns,
    text='حذف کالا',
    bg='#f44336',
    fg='white',
    width=12,
    command=delete_product,
).pack(side='right', padx=5)
tk.Button(
    frame_btns, text='پاک‌کردن فرم', width=12, command=clear_entries
).pack(side='right', padx=5)


# ==============================
# 13. نوار جستجو
# ==============================
frame_search = tk.Frame(root, pady=5)
frame_search.pack(fill='x', padx=10)

tk.Button(frame_search, text='جستجو', width=10, command=search_product).pack(
    side='left', padx=5
)
entry_search = tk.Entry(frame_search, width=25)
entry_search.pack(side='left', padx=5)
tk.Label(frame_search, text='جستجوی نام کالا:').pack(side='left', padx=5)


# ==============================
# 14. جدول نمایش کالاها
# ==============================
columns = ('id', 'name', 'buy_price', 'sell_price', 'quantity')
tree = ttk.Treeview(root, columns=columns, show='headings', height=12)

tree.heading('id', text='شناسه')
tree.heading('name', text='نام کالا')
tree.heading('buy_price', text='قیمت خرید')
tree.heading('sell_price', text='قیمت فروش')
tree.heading('quantity', text='تعداد')

tree.column('id', width=60, anchor='center')
tree.column('name', width=200, anchor='center')
tree.column('buy_price', width=120, anchor='center')
tree.column('sell_price', width=120, anchor='center')
tree.column('quantity', width=80, anchor='center')

tree.pack(fill='both', expand=True, padx=10, pady=10)
tree.bind('<<TreeviewSelect>>', on_row_select)


# ==============================
# 15. اجرای برنامه
# ==============================
init_db()
load_data()
print('برنامه آماده و در حال اجراست...')
root.mainloop()