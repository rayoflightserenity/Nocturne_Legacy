import os

# Файлы программы
HISTORY_FILE = "history.txt"  # Файл с историей действий
ALL_PEOPLE_FILE = "all_people.txt"  # Все пользователи
BLACK_PEOPLE_FILE = "black_people.txt"  # Черный список
ADMIN_FILE = "admin.txt"  # Администраторы
PEOPLE_FILE = "people.txt"  # Участники
DELETED_NICKS_FILE = "deleted_nicknames.txt"  # Файл с удалёнными вручную никами

# Доступные группы
AVAILABLE_GROUPS = ["Администраторы", "Участники", "Черный список"]

# Функция для добавления истории
def add_history(action):
    with open(HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(action + "\n")

# Показать историю действий
def show_history():
    print("\nИстория действий:")
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = file.readlines()
            if history:
                for line in history:
                    print(line.strip())
            else:
                print("История пуста.")
    else:
        print("История еще не была записана.")

# Показать весь список ников, исключая удалённые вручную
def show_all_nicknames():
    print("\nВесь список ников:")
    if os.path.exists(ALL_PEOPLE_FILE):
        with open(ALL_PEOPLE_FILE, "r", encoding="utf-8") as file:
            users = file.readlines()
            if users:
                # Читаем список вручную удалённых ников
                deleted_nicks = set()
                if os.path.exists(DELETED_NICKS_FILE):
                    with open(DELETED_NICKS_FILE, "r", encoding="utf-8") as deleted_file:
                        deleted_nicks = set(deleted_file.readlines())

                # Показываем только тех, кто не был удалён вручную
                for user in users:
                    if user.strip() not in deleted_nicks:
                        print(user.strip())
            else:
                print("Список пользователей пуст.")
    else:
        print("Нет сохраненных пользователей.")

# Сортировка списка ников
def sort_nicknames():
    print("\nСортировка ников по алфавиту:")
    if os.path.exists(ALL_PEOPLE_FILE):
        with open(ALL_PEOPLE_FILE, "r", encoding="utf-8") as file:
            users = file.readlines()
            if users:
                sorted_users = sorted(users)
                for user in sorted_users:
                    print(user.strip())
            else:
                print("Список пользователей пуст.")
    else:
        print("Нет сохраненных пользователей.")

# Функция проверки, содержит ли ник знак "@"
def is_valid_nickname(nickname):
    if "@" not in nickname:
        print("Никнейм должен содержать символ '@'. Попробуйте снова.")
        return False
    return True

# Проверка, существует ли уже ник в группе
def is_nickname_exists(nickname, group_file):
    with open(group_file, "r", encoding="utf-8") as file:
        existing_nicks = file.readlines()
        for existing_nick in existing_nicks:
            if existing_nick.strip() == nickname:
                return True
    return False

# Добавить ник в группу
def add_nickname():
    nickname = input("Введите никнейм: ").strip()

    if not is_valid_nickname(nickname):
        return

    while True:
        # Показать список доступных групп
        print("\nВыберите группу для сохранения ника:")
        for idx, group in enumerate(AVAILABLE_GROUPS, 1):
            print(f"{idx}. {group}")
        print("4. Назад")

        group_choice = input("Введите номер группы: ").strip()

        # Проверка выбора группы
        if group_choice == "4":
            print("Возвращаемся назад...")
            return  # Возвращаемся в главное меню
        elif not group_choice.isdigit() or int(group_choice) not in range(1, len(AVAILABLE_GROUPS) + 1):
            print("Некорректный выбор. Попробуйте снова.")
        else:
            group = AVAILABLE_GROUPS[int(group_choice) - 1]
            break  # Если выбрана правильная группа, выходим из цикла

    # Определяем файл для выбранной группы
    if group == "Администраторы":
        group_file = ADMIN_FILE
    elif group == "Участники":
        group_file = PEOPLE_FILE
    elif group == "Черный список":
        group_file = BLACK_PEOPLE_FILE

    # Проверяем, существует ли уже ник в группе
    if is_nickname_exists(nickname, group_file):
        print(f"Ошибка: Ник '{nickname}' уже существует в группе '{group}'.")
        return

    # Записываем в историю
    add_history(f"Добавлен ник '{nickname}' в группу '{group}'.")

    # Добавляем ник в группу
    with open(group_file, "a", encoding="utf-8") as file:
        file.write(f"{nickname}\n")

    # Добавляем ник в общий список
    with open(ALL_PEOPLE_FILE, "a", encoding="utf-8") as file:
        file.write(f"{nickname} - {group}\n")

    print(f"Ник '{nickname}' сохранён в группе '{group}'.")

# Найти ник
def find_nickname():
    nickname = input("Введите никнейм для поиска: ").strip()

    if not is_valid_nickname(nickname):
        return

    found = False

    # Поиск в админах
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "r", encoding="utf-8") as file:
            admins = file.readlines()
            for admin in admins:
                if nickname.strip() == admin.strip():
                    print(f"Ник '{nickname}' найден в группе 'Администраторы'.")
                    found = True
                    break

    # Поиск в участниках
    if not found and os.path.exists(PEOPLE_FILE):
        with open(PEOPLE_FILE, "r", encoding="utf-8") as file:
            people = file.readlines()
            for person in people:
                if nickname.strip() == person.strip():
                    print(f"Ник '{nickname}' найден в группе 'Участники'.")
                    found = True
                    break

    # Поиск в черном списке
    if not found and os.path.exists(BLACK_PEOPLE_FILE):
        with open(BLACK_PEOPLE_FILE, "r", encoding="utf-8") as file:
            black_list = file.readlines()
            for black in black_list:
                if nickname.strip() == black.strip():
                    print(f"Ник '{nickname}' найден в группе 'Черный список'.")
                    found = True
                    break

    if not found:
        print("Такого участника нету.")

# Удалить ник
def delete_nickname():
    nickname = input("Введите никнейм для удаления: ").strip()

    if not is_valid_nickname(nickname):
        return

    found = False
    # Чтение всех файлов для удаления
    for file_name, group in [(ADMIN_FILE, "Администраторы"),
                             (PEOPLE_FILE, "Участники"),
                             (BLACK_PEOPLE_FILE, "Черный список"),
                             (ALL_PEOPLE_FILE, "Все пользователи")]:
        with open(file_name, "r", encoding="utf-8") as file:
            lines = file.readlines()

        with open(file_name, "w", encoding="utf-8") as file:
            for line in lines:
                if nickname != line.strip():
                    file.write(line)
                else:
                    found = True
                    add_history(f"Удалён ник '{nickname}' из группы '{group}'.")

    if found:
        print(f"Ник '{nickname}' удалён.")
        # Записать ник в файл удалённых вручную ников
        with open(DELETED_NICKS_FILE, "a", encoding="utf-8") as file:
            file.write(f"{nickname}\n")
    else:
        print("Такого ника нету.")

# Удалить историю
def delete_history():
    password = input("Введите пароль для удаления истории: ").strip()
    if password == "0000":
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            file.truncate(0)  # Очищаем файл
        print("История удалена.")
    else:
        print("Неверный пароль.")

# Главное меню
def main():
    while True:
        print("\nВыберите действие:")
        print("1. Добавить ник")
        print("2. Найти ник")
        print("3. Удалить ник")
        print("4. Весь список ников")
        print("5. Сортировать ники")
        print("6. Показать историю")
        print("7. Удалить историю")
        print("8. Выйти")

        choice = input("Введите номер действия: ").strip()

        if choice == "1":
            add_nickname()
        elif choice == "2":
            find_nickname()
        elif choice == "3":
            delete_nickname()
        elif choice == "4":
            show_all_nicknames()
        elif choice == "5":
            sort_nicknames()
        elif choice == "6":
            show_history()
        elif choice == "7":
            delete_history()
        elif choice == "8":
            print("Выход из программы.")
            break
        else:
            print("Некорректный ввод, попробуйте снова.")

# Запуск программы
if __name__ == "__main__":
    main()
