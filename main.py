import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

# Путь к файлу избранных пользователей
FAVORITES_FILE = "favorites.json"

# Загрузка избранных пользователей из JSON
def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        return []
    with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

# Сохранение избранных пользователей в JSON
def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

# Поиск пользователя через GitHub API
def search_user(username):
    if not username:
        return None
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return "not_found"
    except Exception as e:
        return str(e)

# Обработчик кнопки поиска
def on_search():
    username = entry_search.get().strip()
    if not username:
        messagebox.showwarning("Ошибка", "Поле поиска не должно быть пустым!")
        return

    result = search_user(username)
    if result == "not_found":
        messagebox.showinfo("Информация", f"Пользователь {username} не найден.")
        return
    elif isinstance(result, str):
        messagebox.showerror("Ошибка", f"Произошла ошибка: {result}")
        return

    # Очистка списка результатов
    for item in tree.get_children():
        tree.delete(item)

    # Добавление пользователя в список результатов
    tree.insert("", "end", values=(result["login"], result["name"], result["public_repos"]))

# Добавление пользователя в избранное
def add_to_favorites():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Ошибка", "Выберите пользователя из списка!")
        return

    user_data = tree.item(selected, "values")
    username = user_data[0]

    favorites = load_favorites()
    if username in favorites:
        messagebox.showinfo("Информация", f"{username} уже в избранном.")
        return

    favorites.append(username)
    save_favorites(favorites)
    messagebox.showinfo("Успех", f"{username} добавлен в избранное.")

# Загрузка окна избранных пользователей (для теста)
def show_favorites():
    favorites = load_favorites()
    if not favorites:
        messagebox.showinfo("Избранное", "Избранных пользователей нет.")
        return

    fav_window = tk.Toplevel(root)
    fav_window.title("Избранные пользователи")
    fav_tree = ttk.Treeview(fav_window, columns=("login",), show="headings")
    fav_tree.heading("login", text="Логин")
    for user in favorites:
        fav_tree.insert("", "end", values=(user,))
    fav_tree.pack(fill="both", expand=True)

# Создание GUI
root = tk.Tk()
root.title("GitHub User Finder")
root.geometry("600x400")

# Поле ввода и кнопка поиска
frame_search = tk.Frame(root)
frame_search.pack(pady=10, fill="x")

entry_search = tk.Entry(frame_search, font=("Arial", 12))
entry_search.pack(side="left", expand=True, fill="x", padx=5)

btn_search = tk.Button(frame_search, text="Поиск", command=on_search)
btn_search.pack(side="left", padx=5)

# Кнопка добавления в избранное и просмотра избранных
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5, fill="x")

btn_fav = tk.Button(frame_buttons, text="Добавить в избранное", command=add_to_favorites)
btn_fav.pack(side="left", padx=5)

btn_show_fav = tk.Button(frame_buttons, text="Мои избранные", command=show_favorites)
btn_show_fav.pack(side="left", padx=5)

# Таблица результатов поиска
tree = ttk.Treeview(root, columns=("login", "name", "repos"), show="headings")
tree.heading("login", text="Логин")
tree.heading("name", text="Имя")
tree.heading("repos", text="Репозиториев")
tree.column("login", width=150)
tree.column("name", width=200)
tree.column("repos", width=100)
tree.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()
