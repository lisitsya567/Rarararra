import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql
from pymysql.cursors import DictCursor


class Database:
    connection_data = dict(
        host='localhost',
        port=3306,
        user='root',
        password='1234',
        database='exam_1'
    )

    def __init__(self):
        self.db = pymysql.connect(**self.connection_data, cursorclass=DictCursor)
        self.cursor = self.db.cursor()
        self.init_db()

    def init_db(self):
        query = 'CREATE TABLE IF NOT EXISTS phone_numbers (id INT PRIMARY KEY AUTO_INCREMENT, full_name VARCHAR(100), phone_number VARCHAR(100))'
        self.cursor.execute(query, ())
        self.db.commit()

    def get_records(self):
        query = 'SELECT * FROM phone_numbers'
        self.cursor.execute(query, ())
        return self.cursor.fetchall()

    def get_record(self, record_id):
        query = 'SELECT * FROM phone_numbers WHERE id = %s'
        args = (record_id,)
        self.cursor.execute(query, args)
        return self.cursor.fetchone()

    def delete_record(self, record_id):
        query = 'DELETE FROM phone_numbers WHERE id = %s'
        args = (record_id,)
        self.cursor.execute(query, args)
        self.db.commit()

    def update_record(self, record_id, full_name, phone_number):
        query = 'UPDATE phone_numbers SET full_name = %s, phone_number = %s WHERE id = %s'
        args = (full_name, phone_number, record_id)
        self.cursor.execute(query, args)
        self.db.commit()

    def add_record(self, full_name, phone_number):
        query = 'INSERT INTO phone_numbers (full_name, phone_number) VALUES (%s, %s)'
        args = (full_name, phone_number)
        self.cursor.execute(query, args)
        self.db.commit()

        row_id = self.cursor.lastrowid
        return self.get_record(row_id)


class UpdateProductView(tk.Toplevel):
    full_name_entry: tk.Entry
    phone_number_entry: tk.Entry

    database = Database()

    def __init__(self, record_id, full_name, phone_number, master_root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.master_root = master_root
        self.record_id = record_id
        self.full_name_value = full_name or "Новое ФИО"
        self.phone_number_value = phone_number or "Номер тел."
        self.init_ui()

    def init_ui(self):
        title_label = tk.Label(self, text='Редактировать запись')
        title_label.place(anchor='center')
        title_label.grid(row=0, column=0)

        tk.Label(self, text='ФИО: ').grid(row=1, column=0)
        self.full_name_entry = tk.Entry(self)
        self.full_name_entry.grid(row=1, column=1)
        self.full_name_entry.insert(0, self.full_name_value)

        tk.Label(self, text='Номер: ').grid(row=2, column=0)
        self.phone_number_entry = tk.Entry(self)
        self.phone_number_entry.grid(row=2, column=1)
        self.phone_number_entry.insert(0, self.phone_number_value)

        tk.Button(self, text='Редактировать', command=self.change_value).grid(row=4)
        tk.Button(self, text='Закрыть', command=self.destroy).grid(row=4, column=1)

    def change_value(self):
        record_id, phone_number, full_name = self.record_id, self.phone_number_entry.get(), self.full_name_entry.get()
        self.database.update_record(record_id, full_name, phone_number)

        tree_focus = self.master_root.tree.focus()
        self.master_root.tree.item(tree_focus, values=(record_id, full_name, phone_number))

        messagebox.showinfo('Успех', 'Данные в БД обновлены!')
        self.destroy()


class MainView:
    tree_columns = dict(
        id='ID',
        full_name='ФИО',
        phone_number='Номер'
    )

    database = Database()

    def __init__(self, root: tk.Tk = None):
        self.root = tk.Tk() if not root else root
        self.root.title("Матвеев К.Д")
        self.root.geometry('800x400')
        self.tree = self.build_tree()
        self.init_ui()

    def build_tree(self):
        columns = tuple(self.tree_columns.keys())
        tree = ttk.Treeview(self.root,
                            columns=columns,
                            show='headings')

        for key, heading in self.tree_columns.items():
            tree.heading(key, text=heading)

        self.update_tree(tree)
        return tree

    def update_tree(self, tree: ttk.Treeview = None):
        if not tree:
            tree = self.tree

        for item in tree.get_children():
            tree.delete(item)

        database_records = self.database.get_records()
        for index, record in enumerate(database_records):
            tree.insert("", index, values=tuple(record.values()))

    def to_change_view(self):
        focus = self.tree.focus()
        item = self.tree.item(focus)

        if not item['values']:
            return messagebox.showerror("Ошибка", "Сначала выделите запись, которую нужно редактировать!")

        record_id, full_name, phone_number = item['values']
        UpdateProductView(record_id, full_name, phone_number, master_root=self)

    def delete_from_focus(self):
        focus = self.tree.focus()
        item = self.tree.item(focus)

        if not item['values']:
            return messagebox.showerror("Ошибка", "Выделите хотя бы один ряд для удаления!")

        item_id = item['values'][0]
        self.database.delete_record(item_id)
        self.tree.delete(focus)

        return messagebox.showinfo("Успех", "Запись удалена!")

    def init_ui(self):
        self.tree.grid(row=0, column=0)
        self.tree.place(x=10, y=10)

        tk.Button(self.root, text='Редактировать', command=self.to_change_view).place(x=10, y=250)
        tk.Button(self.root, text='Удалить', command=self.delete_from_focus).place(x=100, y=250)

    def mainloop(self):
        return self.root.mainloop()


if __name__ == '__main__':
    main = MainView()
    main.mainloop()