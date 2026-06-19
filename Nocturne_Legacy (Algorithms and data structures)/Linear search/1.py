import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

DB_FILE = "database.json"


def load_database():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def save_database(data):
    with open(DB_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


class RoleplayApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Каталог Рольової Гри 🔮")
        self.root.geometry("1000x540")
        self.db = load_database()

        # Створення вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_list = ttk.Frame(self.notebook)
        self.tab_add = ttk.Frame(self.notebook)

        self.notebook.add(
            self.tab_list, text="📋 Список, Редагування та Видалення"
        )
        self.notebook.add(self.tab_add, text="➕ Додати персонажа")

        self.setup_list_tab()
        self.setup_add_tab()
        self.refresh_table(self.db)

    def show_silent_toast(self, title, message):
        """Створює гарне та абсолютно беззвучне віконце-сповіщення"""
        toast = tk.Toplevel(self.root)
        toast.title(title)
        toast.geometry("380x120")

        # Центруємо віконце відносно головного вікна програми
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        toast.geometry(f"+{root_x + 310}+{root_y + 200}")

        toast.resizable(False, False)
        toast.attributes("-topmost", True)  # Завжди поверх інших вікон

        # Контейнер для гарного відступу
        frame = ttk.Frame(toast, padding=15)
        frame.pack(fill="both", expand=True)

        # Текст сповіщення
        lbl = ttk.Label(
            frame,
            text=message,
            font=("Arial", 11, "bold"),
            foreground="#2e7d32",
            justify="center",
            wraplength=340,
        )
        lbl.pack(expand=True)

        # Автоматично закриваємо через 2000 мілісекунд (2 секунди)
        toast.after(2000, toast.destroy)

    def setup_list_tab(self):
        """Вкладка зі списком, пошуком та всіма кнопками керування вгорі"""
        frame_top = ttk.Frame(self.tab_list)
        frame_top.pack(fill="x", padx=10, pady=10)

        ttk.Label(
            frame_top, text="Швидкий пошук (ніком, іменем або роллю):"
        ).pack(side="left", padx=5)
        self.entry_search = ttk.Entry(frame_top, width=20)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", self.perform_search)

        btn_reset = ttk.Button(
            frame_top, text="🔄 Скинути", command=self.reset_search
        )
        btn_reset.pack(side="left", padx=5)

        # Кнопка ВИДАЛЕННЯ
        btn_delete = ttk.Button(
            frame_top,
            text="❌ Видалити вибраного",
            command=self.delete_character,
        )
        btn_delete.pack(side="right", padx=5)

        # Кнопка РЕДАГУВАННЯ
        btn_edit = ttk.Button(
            frame_top, text="📝 Змінити дані", command=self.trigger_edit
        )
        btn_edit.pack(side="right", padx=5)

        # Підказка для користувача
        lbl_hint = ttk.Label(
            self.tab_list,
            text="💡 Порада: виберіть персонажа та натисніть «📝 Змінити дані» або просто двічі клацніть на нього.",
            foreground="gray",
        )
        lbl_hint.pack(anchor="w", padx=15, pady=2)

        # Центр: Таблиця
        frame_table = ttk.Frame(self.tab_list)
        frame_table.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("instagram", "char_name", "role", "date_added", "avatar")
        self.table = ttk.Treeview(frame_table, columns=columns, show="headings")

        self.table.heading("instagram", text="Instagram нік")
        self.table.heading("char_name", text="Ім'я персонажа")
        self.table.heading("role", text="Характеристики / Роль")
        self.table.heading("date_added", text="🕒 Дата додавання")
        self.table.heading("avatar", text="Аватарка")

        self.table.column("instagram", width=130, anchor="center")
        self.table.column("char_name", width=130, anchor="center")
        self.table.column("role", width=250)
        self.table.column("date_added", width=140, anchor="center")
        self.table.column("avatar", width=130)

        scrollbar = ttk.Scrollbar(
            frame_table, orient="vertical", command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.table.bind("<Double-1>", lambda event: self.trigger_edit())

    def setup_add_tab(self):
        """Вкладка для створення нового героя"""
        frame_form = ttk.Frame(self.tab_add, padding=20)
        frame_form.pack(fill="both", expand=True)

        ttk.Label(frame_form, text="Instagram нік:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.entry_add_ig = ttk.Entry(frame_form, width=40)
        self.entry_add_ig.grid(row=0, column=1, pady=5)

        ttk.Label(frame_form, text="Ім'я персонажа:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.entry_add_name = ttk.Entry(frame_form, width=40)
        self.entry_add_name.grid(row=1, column=1, pady=5)

        ttk.Label(frame_form, text="Характеристики/Роль:").grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.entry_add_role = ttk.Entry(frame_form, width=40)
        self.entry_add_role.grid(row=2, column=1, pady=5)

        ttk.Label(frame_form, text="Посилання на аватарку:").grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.entry_add_avatar = ttk.Entry(frame_form, width=40)
        self.entry_add_avatar.grid(row=3, column=1, pady=5)

        btn_save = ttk.Button(
            frame_form, text="Зберегти персонажа 💾", command=self.save_character
        )
        btn_save.grid(row=4, column=1, pady=20, sticky="e")

    def refresh_table(self, data_list):
        for row in self.table.get_children():
            self.table.delete(row)
        for char in data_list:
            date_str = char.get("date_added", "Невідомо")
            self.table.insert(
                "",
                tk.END,
                values=(
                    char["instagram"],
                    char["char_name"],
                    char["role"],
                    date_str,
                    char["avatar"],
                ),
            )

    def perform_search(self, event=None):
        query = self.entry_search.get().lower()
        if not query:
            self.refresh_table(self.db)
            return

        filtered_list = []
        for char in self.db:
            if (
                query in char["char_name"].lower()
                or query in char["instagram"].lower()
                or query in char["role"].lower()
            ):
                filtered_list.append(char)

        self.refresh_table(filtered_list)

    def reset_search(self):
        self.entry_search.delete(0, tk.END)
        self.refresh_table(self.db)

    def save_character(self):
        ig = self.entry_add_ig.get().strip()
        name = self.entry_add_name.get().strip()
        role = self.entry_add_role.get().strip()
        avatar = self.entry_add_avatar.get().strip() or "Не вказано"

        if not ig or not name or not role:
            messagebox.showwarning(
                "Помилка", "Будь ласка, заповніть обов'язкові поля!"
            )
            return

        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")

        new_char = {
            "instagram": ig,
            "char_name": name,
            "role": role,
            "date_added": current_time,
            "avatar": avatar,
        }

        self.db.append(new_char)
        save_database(self.db)

        self.entry_add_ig.delete(0, tk.END)
        self.entry_add_name.delete(0, tk.END)
        self.entry_add_role.delete(0, tk.END)
        self.entry_add_avatar.delete(0, tk.END)

        self.refresh_table(self.db)
        self.notebook.select(self.tab_list)

        # Виклик беззвучного сповіщення замість messagebox
        self.show_silent_toast(
            "Успіх 🎉", f"Персонажа «{name}» успішно додано!"
        )

    def trigger_edit(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning(
                "Редагування", "Виберіть персонажа зі списку для зміни даних!"
            )
            return

        values = self.table.item(selected_item, "values")
        orig_ig = values[0]
        orig_name = values[1]

        char_index = None
        for index, char in enumerate(self.db):
            if char["instagram"] == orig_ig and char["char_name"] == orig_name:
                char_index = index
                break

        if char_index is not None:
            self.open_edit_window(char_index)

    def open_edit_window(self, char_index):
        current_char = self.db[char_index]

        edit_win = tk.Toplevel(self.root)
        edit_win.title("📝 Редагування персонажа")
        edit_win.geometry("450x300")
        edit_win.grab_set()

        frame_edit = ttk.Frame(edit_win, padding=15)
        frame_edit.pack(fill="both", expand=True)

        ttk.Label(frame_edit, text="Instagram нік:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        ent_ig = ttk.Entry(frame_edit, width=30)
        ent_ig.insert(0, current_char["instagram"])
        ent_ig.grid(row=0, column=1, pady=5)

        ttk.Label(frame_edit, text="Ім'я персонажа:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        ent_name = ttk.Entry(frame_edit, width=30)
        ent_name.insert(0, current_char["char_name"])
        ent_name.grid(row=1, column=1, pady=5)

        ttk.Label(frame_edit, text="Характеристики/Роль:").grid(
            row=2, column=0, sticky="w", pady=5
        )
        ent_role = ttk.Entry(frame_edit, width=30)
        ent_role.insert(0, current_char["role"])
        ent_role.grid(row=2, column=1, pady=5)

        ttk.Label(frame_edit, text="Посилання на аватарку:").grid(
            row=3, column=0, sticky="w", pady=5
        )
        ent_avatar = ttk.Entry(frame_edit, width=30)
        ent_avatar.insert(0, current_char["avatar"])
        ent_avatar.grid(row=3, column=1, pady=5)

        def save_changes():
            new_ig = ent_ig.get().strip()
            new_name = ent_name.get().strip()
            new_role = ent_role.get().strip()
            new_avatar = ent_avatar.get().strip() or "Не вказано"

            if not new_ig or not new_name or not new_role:
                messagebox.showwarning(
                    "Помилка",
                    "Будь ласка, заповніть обов'язкові поля!",
                    parent=edit_win,
                )
                return

            self.db[char_index]["instagram"] = new_ig
            self.db[char_index]["char_name"] = new_name
            self.db[char_index]["role"] = new_role
            self.db[char_index]["avatar"] = new_avatar

            save_database(self.db)
            self.perform_search()
            edit_win.destroy()

            # Виклик беззвучного сповіщення замість messagebox
            self.show_silent_toast(
                "Оновлено 📝", "Дані персонажа успішно змінено!"
            )

        btn_save_changes = ttk.Button(
            frame_edit, text="Зберегти зміни 💾", command=save_changes
        )
        btn_save_changes.grid(row=4, column=1, pady=15, sticky="e")

    def delete_character(self):
        selected_item = self.table.selection()

        if not selected_item:
            messagebox.showwarning(
                "Видалення",
                "Виберіть персонажа зі списку, якого хочете видалити!",
            )
            return

        values = self.table.item(selected_item, "values")
        selected_ig = values[0]
        selected_name = values[1]

        # Тут залишаємо діалог підтвердження, щоб випадково нікого не стерти
        confirm = messagebox.askyesno(
            "Підтвердження",
            f"Ви впевнені, що хочете видалити персонажа {selected_name} ({selected_ig})?",
        )

        if confirm:
            for char in self.db:
                if (
                    char["instagram"] == selected_ig
                    and char["char_name"] == selected_name
                ):
                    self.db.remove(char)
                    break

            save_database(self.db)
            self.perform_search()

            # Виклик беззвучного сповіщення замість messagebox
            self.show_silent_toast(
                "Видалено ❌", f"Персонажа {selected_name} видалено!"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = RoleplayApp(root)
    root.mainloop()