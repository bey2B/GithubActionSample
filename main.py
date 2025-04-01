import pystray
import tkinter as tk
from PIL import Image
import json
import os
from datetime import datetime


class TodoApp:
    def update_icon_title(self):
        # 更新系统托盘图标的提示文本
        incomplete_tasks = [todo["task"] for todo in self.todos if not todo["completed"]]
        if incomplete_tasks:
            title = "待办事项:\n" + "\n".join(f"- {task}" for task in incomplete_tasks[:3])
            if len(incomplete_tasks) > 3:
                title += f"\n——还有{len(incomplete_tasks) - 3}项"
        else:
            title = "待办事项"
        self.icon.title = title

    def add_todo(self):
        # 创建输入窗口
        window = tk.Tk()
        window.title("添加待办事项")
        window.geometry("300x150")
        window.resizable(False, False)  # 禁止调整窗口大小

        # 使窗口居中显示
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')

        label = tk.Label(window, text="输入待办事项:")
        label.pack(pady=10)

        entry = tk.Entry(window, width=30)
        entry.pack(pady=5)

        # 确保窗口出现在最前面并获得焦点
        window.lift()
        window.focus_force()
        entry.focus_set()

        def save():
            task = entry.get()
            if task:
                self.todos.append({
                    "task": task,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "completed": False
                })
                self.save_todos()
                self.icon.menu = self.create_menu()
                self.update_icon_title()  # 更新提示文本
                window.destroy()

        # 绑定回车键
        entry.bind('<Return>', lambda event: save())

        button = tk.Button(window, text="保存", command=save)
        button.pack(pady=10)

        # 设置焦点到输入框
        entry.focus()

        window.mainloop()

    def toggle_todo(self, index):
        if isinstance(index, int) and 0 <= index < len(self.todos):
            self.todos[index]["completed"] = not self.todos[index]["completed"]
            self.save_todos()
            self.icon.menu = self.create_menu()
            self.update_icon_title()  # 更新提示文本

    def __init__(self):
        self.todos = []
        self.load_todos()

        # 创建系统托盘图标
        self.icon = pystray.Icon(
            "todo_list",
            Image.new('RGB', (64, 64), 'green'),
            "待办事项",
            self.create_menu()
        )
        self.update_icon_title()  # 初始化时更新提示文本

    def load_todos(self):
        try:
            if os.path.exists('todos.json'):
                with open('todos.json', 'r', encoding='utf-8') as f:
                    self.todos = json.load(f)
        except Exception as e:
            print(f"加载待办事项失败: {e}")

    def save_todos(self):
        try:
            with open('todos.json', 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存待办事项失败: {e}")

    def create_menu(self):
        menu_items = []

        # 添加新待办事项选项
        menu_items.append(pystray.MenuItem("添加待办事项", self.add_todo))

        # 添加待办事项列表
        for i, todo in enumerate(self.todos):
            status = "✓ " if todo["completed"] else "□ "
            # 修改 lambda 函数的调用方式
            menu_items.append(pystray.MenuItem(
                f"{status}{todo['task']}",
                self.create_toggle_callback(i)
            ))

        menu_items.append(pystray.MenuItem("退出", lambda: self.icon.stop()))

        return pystray.Menu(*menu_items)

    def create_toggle_callback(self, index):
        return lambda _: self.toggle_todo(index)

    def run(self):
        self.icon.run()


if __name__ == "__main__":
    app = TodoApp()
    app.run()
