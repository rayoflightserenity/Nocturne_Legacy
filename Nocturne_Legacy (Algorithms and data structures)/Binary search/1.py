import json
import os
import random
import tkinter as tk
from tkinter import messagebox, ttk

DB_FILE = "events_database.json"


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


class EventGeneratorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("🎲 Реєстр Подій з Повним Редагуванням")
        self.root.geometry("1150x650")
        self.db = load_database()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_gen = ttk.Frame(self.notebook)
        self.tab_add = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_gen, text="🎲 Генератор та Список подій")
        self.notebook.add(self.tab_add, text="➕ Додати нову подію")

        self.spinboxes = {}

        self.setup_gen_tab()
        self.setup_add_tab()
        self.refresh_scrollable_list()

    def show_silent_toast(self, title, message):
        """Беззвучне сповіщення"""
        toast = tk.Toplevel(self.root)
        toast.title(title)
        toast.geometry("380x120")
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        toast.geometry(f"+{root_x + 350}+{root_y + 220}")
        toast.resizable(False, False)
        toast.attributes("-topmost", True)

        frame = ttk.Frame(toast, padding=15)
        frame.pack(fill="both", expand=True)

        lbl = ttk.Label(
            frame,
            text=message,
            font=("Arial", 11, "bold"),
            foreground="#2e7d32",
            justify="center",
            wraplength=340,
        )
        lbl.pack(expand=True)
        toast.after(1500, toast.destroy)

    def setup_gen_tab(self):
        """Головна вкладка"""
        main_frame = ttk.Frame(self.tab_gen, padding=10)
        main_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        top_bar = ttk.Frame(left_frame)
        top_bar.pack(fill="x", pady=(0, 8))

        self.lbl_total_pct = ttk.Label(
            top_bar,
            text="Існуючі події (Зайнято: 0% / 100%):",
            font=("Arial", 11, "bold"),
        )
        self.lbl_total_pct.pack(side="left", anchor="w")

        btn_reset_all = ttk.Button(
            top_bar,
            text="🔄 Обнулити всі відсотки",
            command=self.reset_all_percentages,
        )
        btn_reset_all.pack(side="right", padx=(5, 0))

        # Прокрутка (Scrollable Frame)
        self.canvas = tk.Canvas(left_frame, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfig(self.canvas_window, width=event.width))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # ПРАВА ЧАСТИНА: Івент-Машина
        right_frame = ttk.LabelFrame(main_frame, text=" 🕹️ Івент-Машина ", padding=15)
        right_frame.pack(side="right", fill="both", expand=False)
        right_frame.config(width=360)
        right_frame.pack_propagate(False)

        ttk.Label(right_frame, text="Скільки подій згенерувати?").pack(anchor="w", pady=2)

        self.entry_count = ttk.Spinbox(right_frame, from_=1, to=20, font=("Arial", 11), width=10)
        self.entry_count.set("2")
        self.entry_count.pack(anchor="w", pady=5)

        btn_roll = ttk.Button(right_frame, text="🎲 ЗГЕНЕРУВАТИ ПРИГОДУ", command=self.generate_events)
        btn_roll.pack(fill="x", pady=12)

        ttk.Label(right_frame, text="Результат генерації:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 4))

        self.txt_result = tk.Text(right_frame, width=35, height=18, font=("Arial", 10), wrap="word")
        self.txt_result.pack(fill="both", expand=True)

    def setup_add_tab(self):
        """Вкладка додавання подій"""
        frame_form = ttk.Frame(self.tab_add, padding=20)
        frame_form.pack(fill="both", expand=True)

        ttk.Label(frame_form, text="Назва події:").grid(row=0, column=0, sticky="w", pady=8)
        self.entry_add_name = ttk.Entry(frame_form, width=40)
        self.entry_add_name.grid(row=0, column=1, pady=8)

        ttk.Label(frame_form, text="Ймовірність у відсотках (можна 0.1, 0.5 тощо):").grid(row=1, column=0, sticky="w",
                                                                                          pady=8)

        self.entry_add_weight = ttk.Spinbox(frame_form, from_=0.0, to=100.0, increment=0.1, width=38)
        self.entry_add_weight.set("10.0")
        self.entry_add_weight.grid(row=1, column=1, pady=8)

        ttk.Label(frame_form, text="Опис події:").grid(row=2, column=0, sticky="w", pady=8)
        self.entry_add_desc = ttk.Entry(frame_form, width=40)
        self.entry_add_desc.grid(row=2, column=1, pady=8)

        btn_save = ttk.Button(frame_form, text="Зберегти подію в базу 💾", command=self.save_event)
        btn_save.grid(row=3, column=1, pady=20, sticky="e")

    def refresh_scrollable_list(self):
        """Оновлює список подій із кнопками редагування та видалення"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.spinboxes.clear()
        total_weight = sum(ev["weight"] for ev in self.db)
        self.lbl_total_pct.config(text=f"Існуючі події (Зайнято: {total_weight:.1f}% / 100%):")

        header_frame = ttk.Frame(self.scrollable_frame, padding=5)
        header_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(header_frame, text="Назва події", font=("Arial", 10, "bold"), width=20, anchor="w").pack(side="left",
                                                                                                           padx=5)
        ttk.Label(header_frame, text="Відсоток (%) [Крок: 0.1]", font=("Arial", 10, "bold"), width=22, anchor="w").pack(
            side="left", padx=5)
        ttk.Label(header_frame, text="Опис / Наслідки", font=("Arial", 10, "bold"), anchor="w").pack(side="left",
                                                                                                     fill="x",
                                                                                                     expand=True,
                                                                                                     padx=5)

        for index, ev in enumerate(self.db):
            row_frame = ttk.Frame(self.scrollable_frame, padding=6, relief="groove", borderwidth=1)
            row_frame.pack(fill="x", pady=3, padx=5)

            # 1. Назва
            lbl_name = ttk.Label(row_frame, text=ev["name"], font=("Arial", 10, "bold"), width=20, anchor="w")
            lbl_name.pack(side="left", padx=5)

            # 2. Spinbox (стрілочки відсотків)
            sp_weight = ttk.Spinbox(row_frame, from_=0.0, to=100.0, increment=0.1, width=8, font=("Arial", 10))
            sp_weight.set(f"{ev['weight']:.1f}")
            sp_weight.pack(side="left", padx=5)

            self.spinboxes[index] = sp_weight

            sp_weight.config(command=lambda i=index: self.on_spinbox_change(i))
            sp_weight.bind("<Return>", lambda event, i=index: self.on_spinbox_change(i))
            sp_weight.bind("<FocusOut>", lambda event, i=index: self.on_spinbox_change(i))

            # --- КНОПКИ КЕРУВАННЯ СПРАВА ---
            # Кнопка видалення (виносимо у самий кінець)
            btn_del = ttk.Button(row_frame, text="❌", width=3, command=lambda name=ev["name"]: self.delete_event(name))
            btn_del.pack(side="right", padx=2)

            # НОВА КНОПКА: Редагування події за її індексом
            btn_edit = ttk.Button(row_frame, text="📝", width=3, command=lambda i=index: self.open_inline_edit_window(i))
            btn_edit.pack(side="right", padx=2)

            # 3. Опис посередині
            lbl_desc = ttk.Label(row_frame, text=ev["description"], font=("Arial", 9, "italic"), foreground="gray",
                                 anchor="w")
            lbl_desc.pack(side="left", fill="x", expand=True, padx=10)

    def on_spinbox_change(self, event_idx):
        """Обробка зміни стрілочок «на льоту»"""
        sp = self.spinboxes.get(event_idx)
        if not sp:
            return

        val_str = sp.get().strip().replace(",", ".")
        try:
            new_weight = round(float(val_str), 2)
            if new_weight < 0:
                new_weight = 0.0
        except ValueError:
            new_weight = 0.0

        total_others = sum(ev["weight"] for i, ev in enumerate(self.db) if i != event_idx)
        max_allowed = max(0.0, 100.0 - total_others)

        if total_others + new_weight > 100.0:
            new_weight = round(max_allowed, 1)
            sp.set(f"{new_weight:.1f}")
            self.show_silent_toast("Автокорекція ⚠️", f"Зрізано до максимуму: {new_weight}%")

        self.db[event_idx]["weight"] = new_weight
        save_database(self.db)

        total_weight = sum(ev["weight"] for ev in self.db)
        self.lbl_total_pct.config(text=f"Існуючі події (Зайнято: {total_weight:.1f}% / 100%):")

    def open_inline_edit_window(self, event_idx):
        """Віконце редагування назви та опису події за кнопкою 📝"""
        current_ev = self.db[event_idx]

        edit_win = tk.Toplevel(self.root)
        edit_win.title("📝 Зміна тексту події")
        edit_win.geometry("420x200")
        edit_win.grab_set()  # Блокує головне вікно, поки це відкрите

        # Центрування віконця відносно головного
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        edit_win.geometry(f"+{root_x + 300}+{root_y + 200}")

        frame = ttk.Frame(edit_win, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Нова назва події:").pack(anchor="w", pady=2)
        ent_name = ttk.Entry(frame, width=40)
        ent_name.insert(0, current_ev["name"])
        ent_name.pack(fill="x", pady=4)

        ttk.Label(frame, text="Новий опис / наслідки:").pack(anchor="w", pady=2)
        ent_desc = ttk.Entry(frame, width=40)
        ent_desc.insert(0, current_ev["description"])
        ent_desc.pack(fill="x", pady=4)

        def save_text_changes():
            name_txt = ent_name.get().strip()
            desc_txt = ent_desc.get().strip() or "Немає опису"

            if not name_txt:
                messagebox.showwarning("Помилка", "Назва не може бути порожньою!", parent=edit_win)
                return

            # Оновлюємо дані події (відсоток залишається незмінним)
            self.db[event_idx]["name"] = name_txt
            self.db[event_idx]["description"] = desc_txt

            save_database(self.db)
            edit_win.destroy()
            self.refresh_scrollable_list()
            self.show_silent_toast("Успіх 🎉", "Дані події оновлено!")

        btn_save = ttk.Button(frame, text="💾 Зберегти зміни", command=save_text_changes)
        btn_save.pack(anchor="e", pady=10)

    def reset_all_percentages(self):
        if not self.db:
            messagebox.showinfo("Інфо", "Список подій порожній.")
            return

        if messagebox.askyesno("Обнулення відсотків 🔄", "Скинути ймовірність усіх подій до 0.0%?"):
            for ev in self.db:
                ev["weight"] = 0.0
            save_database(self.db)
            self.refresh_scrollable_list()
            self.show_silent_toast("Обнулено 🔄", "Всі відсотки скинуто до 0.0%!")

    def save_event(self):
        name = self.entry_add_name.get().strip()
        weight_str = self.entry_add_weight.get().strip().replace(",", ".")
        desc = self.entry_add_desc.get().strip() or "Немає опису"

        if not name or not weight_str:
            messagebox.showwarning("Помилка", "Заповніть обов'язкові поля!")
            return

        try:
            weight = round(float(weight_str), 2)
            if weight < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Помилка", "Шанс має бути числом!")
            return

        current_total = sum(ev["weight"] for ev in self.db)
        max_allowed = max(0.0, 100.0 - current_total)

        if max_allowed <= 0:
            messagebox.showwarning("Ліміт 100%", "База заповнена!")
            return

        if current_total + weight > 100.0:
            weight = round(max_allowed, 1)
            self.show_silent_toast("Автокорекція ⚠️", f"Додано із залишком: {weight}%")

        self.db.append({"name": name, "weight": weight, "description": desc})
        save_database(self.db)

        self.entry_add_name.delete(0, tk.END)
        self.entry_add_weight.set("10.0")
        self.entry_add_desc.delete(0, tk.END)

        self.refresh_scrollable_list()
        self.notebook.select(self.tab_gen)

    def delete_event(self, name_to_del):
        if messagebox.askyesno("Підтвердження", f"Видалити подію «{name_to_del}»?"):
            self.db = [ev for ev in self.db if ev["name"] != name_to_del]
            save_database(self.db)
            self.refresh_scrollable_list()

    def binary_search_prefix_sums(self, prefix_sums, target):
        low = 0
        high = len(prefix_sums) - 1
        result_index = high
        while low <= high:
            mid = (low + high) // 2
            if prefix_sums[mid] >= target:
                result_index = mid
                high = mid - 1
            else:
                low = mid + 1
        return result_index

    def generate_events(self):
        if not self.db:
            messagebox.showwarning("Увага", "База подій порожня!")
            return

        if sum(ev["weight"] for ev in self.db) == 0:
            messagebox.showwarning("Увага", "Усі відсотки рівні 0.0%! Будь ласка, вкажіть шанси.")
            return

        try:
            count = int(self.entry_count.get().strip())
            if count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Помилка", "Вкажіть коректну кількість подій!")
            return

        temp_db = list(self.db)
        chosen_events = []

        if count > len(temp_db):
            count = len(temp_db)

        for _ in range(count):
            prefix_sums = []
            current_sum = 0
            for ev in temp_db:
                current_sum += ev["weight"]
                prefix_sums.append(current_sum)

            if current_sum <= 0:
                break

            random_point = random.uniform(0, current_sum)
            event_idx = self.binary_search_prefix_sums(prefix_sums, random_point)

            chosen_event = temp_db[event_idx]
            chosen_events.append(chosen_event)
            temp_db.pop(event_idx)

        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, f"🎲 ВИПАЛИ ПОДІЇ ({len(chosen_events)} шт):\n")
        self.txt_result.insert(tk.END, "=" * 34 + "\n\n")

        for i, ev in enumerate(chosen_events, 1):
            self.txt_result.insert(tk.END, f"{i}. 🔸 {ev['name']} ({ev['weight']:.1f}%)\n")
            self.txt_result.insert(tk.END, f"   ↳ {ev['description']}\n\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = EventGeneratorApp(root)
    root.mainloop()