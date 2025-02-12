import os

# Файлы программы
HISTORY_FILE = "history.txt"  # Файл с историей действий
ALL_PEOPLE_FILE = "all_people.txt"  # Все пользователи
BLACK_PEOPLE_FILE = "black_people.txt"  # Черный список

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


# Показать весь список ников
def show_all_nicknames():
    print("\nВесь список ников:")
    if os.path.exists(ALL_PEOPLE_FILE):
        with open(ALL_PEOPLE_FILE, "r", encoding="utf-8") as file:
            users = file.readlines()
            if users:
                for user in users:
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


# Добавить ник в группу
def add_nickname():
    nickname = input("Введите никнейм: ").strip()

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

    # Записываем в историю
    add_history(f"Добавлен ник '{nickname}' в группу '{group}'.")

    # Добавляем в список всех пользователей, если не в черном списке
    with open(BLACK_PEOPLE_FILE, "r", encoding="utf-8") as file:
        black_list = file.readlines()

    if nickname not in [line.strip() for line in black_list]:
        with open(ALL_PEOPLE_FILE, "a", encoding="utf-8") as file:
            file.write(f"{nickname} - {group}\n")

    print(f"Ник '{nickname}' сохранён в группе '{group}'.")


# Найти ник
def find_nickname():
    nickname = input("Введите никнейм для поиска: ").strip()

    with open(ALL_PEOPLE_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    found = False
    for line in lines:
        if nickname in line:
            print(f"Ник '{nickname}' найден в группе '{line.split(' - ')[-1].strip()}'.")
            found = True
            break

    if not found:
        print("Такого участника нету.")


# Удалить ник
def delete_nickname():
    nickname = input("Введите никнейм для удаления: ").strip()

    with open(ALL_PEOPLE_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    with open(ALL_PEOPLE_FILE, "w", encoding="utf-8") as file:
        found = False
        for line in lines:
            if nickname not in line:
                file.write(line)
            else:
                found = True
                # Записываем в историю
                add_history(f"Удалён ник '{nickname}'.")

        if found:
            print(f"Ник '{nickname}' удалён.")
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
