import json
import os

# Назви файлів для збереження даних
CONTACTS_FILE = "contacts.json"
NOTES_FILE = "notes.json"


def save_data(filename, data):
    """
    Зберігає дані у JSON-файл.
    """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_data(filename):
    """
    Завантажує дані з JSON-файлу.
    Якщо файл не існує або пошкоджений, повертає порожній список.
    """
    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []
