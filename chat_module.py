import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
from tkcalendar import Calendar
from tkinter import Spinbox
import openai
import requests
import time as time_module
from datetime import datetime


class ChatModule:
    def __init__(self, main_app):
        self.main_app = main_app
        self.DEEPSEEK_API_KEY = "sk-fdc6a02e984c4781b7c2d1e913f8806d"
        self.todo_list = []
        self.todo_text = None

    def create_chat_frame(self):
        # 创建聊天记录文本框和滚动条
        self.chat_history = tk.Text(self.main_app.chat_frame, wrap=tk.WORD, font=("", 12))
        self.chat_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = tk.Scrollbar(self.main_app.chat_frame, command=self.chat_history.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_history.config(yscrollcommand=scrollbar.set)

        # 创建输入框和发送按钮
        input_frame = tk.Frame(self.main_app.chat_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        self.input_entry = tk.Entry(input_frame, font=("", 12))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        send_button = tk.Button(input_frame, text="发送", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=10)
        self.input_entry.bind("<Return>", lambda event: self.send_message())

        # 创建保存和加载聊天记录的按钮
        button_frame = tk.Frame(self.main_app.chat_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        save_button = tk.Button(button_frame, text="保存聊天记录", command=self.save_chat_history)
        save_button.pack(side=tk.LEFT, padx=10, pady=5)
        load_button = tk.Button(button_frame, text="加载聊天记录", command=self.load_chat_history)
        load_button.pack(side=tk.LEFT, padx=10, pady=5)

        # 创建固定问题按钮区域
        fixed_button_frame = tk.Frame(self.main_app.chat_frame)
        fixed_button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        fixed_questions = [
            ("农业小贴士", lambda: self.send_fixed_question("请给我今天的农业小贴士")),
            ("天气分析", lambda: self.send_fixed_question("请帮我分析一下今天的天气")),
            ("农事提醒", self.add_reminder)
        ]

        for button_text, command in fixed_questions:
            button = tk.Button(fixed_button_frame, text=button_text, command=command)
            button.pack(fill=tk.X, pady=5)

        # 创建待办清单区域
        todo_frame = tk.Frame(self.main_app.chat_frame)
        todo_frame.pack(fill=tk.X, padx=10, pady=5)
        todo_label = tk.Label(todo_frame, text="待办清单", font=("", 12))
        todo_label.pack(side=tk.TOP)
        self.todo_text = tk.Text(todo_frame, wrap=tk.WORD, font=("", 12), height=5)
        self.todo_text.pack(fill=tk.X)
        self.load_todos()

        # 创建删除按钮
        delete_button = tk.Button(todo_frame, text="删除选中行", command=self.delete_selected_todo)
        delete_button.pack(fill=tk.X, pady=5)

    def call_deepseek_api(self, message):
        try:
            today = datetime.now().strftime("%Y-%m-%d %A %H:%M:%S")
            client = openai.OpenAI(
                api_key=self.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
                timeout=100
            )
            try:
                with open('weather1.txt', 'r', encoding='utf-8') as f1:
                    today_weather = f1.read()
                with open('weather7.txt', 'r', encoding='utf-8') as f7:
                    future_weather = f7.read()
                with open('dirt.txt', 'r', encoding='utf-8') as dirt:
                    dirt_message = dirt.read()
                with open('message.txt', 'r', encoding='utf-8') as chatting:
                    chatting_message = chatting.read()
                with open('willdo.txt', 'r', encoding='utf-8') as will_do:
                    will_do_message = will_do.read()
            except FileNotFoundError:
                today_weather = "未知"
                future_weather = "未知"
                dirt_message = "未知"
                chatting_message = "未知"
                will_do_message = "未知"
            system_message = (
                f"你是一个翎创游戏研发社团所研发的一个名字叫'小农'的农业专家助手，"
                f"你在与用户聊天时，可以适当的使用颜文字，并且不能失去专业水准."
                f"今天是{today}，今天的天气是：{today_weather}\n未来七天的天气是：{future_weather}"
                f"检测的土壤湿度数据为：{dirt_message}"
                f"你与用户聊天的记忆为：{chatting_message}"
                f"用户的代办为：{will_do_message}"
            )
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            if response.choices and response.choices[0].message:
                result = response.choices[0].message.content.strip()
            else:
                result = "未收到有效响应"
            with open('message.txt', 'a', encoding='utf-8') as f:
                f.write(f"用户: {message}\n")
                f.write(f"助手: {result}\n")
            return result
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"
        except openai.APIConnectionError as e:
            return f"API连接异常：{str(e)}"
        except openai.APIError as e:
            return f"API返回错误：{str(e)}"
        except Exception as e:
            return f"未预期错误：{str(e)}"

    def send_message(self):
        message = self.input_entry.get()
        if message:
            # 显示用户消息
            self.chat_history.tag_config("user", foreground="blue", justify=tk.RIGHT)
            self.chat_history.insert(tk.END, f"你：{message}\n", "user")
            self.input_entry.delete(0, tk.END)

            # 显示思考提示
            thinking_text = "DeepSeek（农业专家助手）：正在思考...\n"
            self.chat_history.tag_config("assistant", foreground="green", justify=tk.LEFT)
            self.chat_history.insert(tk.END, thinking_text, "assistant")
            self.chat_history.see(tk.END)
            self.chat_history.update()

            start_time = time_module.time()
            response = self.call_deepseek_api(message)
            end_time = time_module.time()
            elapsed_time = round(end_time - start_time, 2)

            # 替换思考提示为实际响应
            self.chat_history.delete(self.chat_history.index(f"end - {len(thinking_text)}c"), tk.END)
            self.chat_history.insert(tk.END, f"eepSeek（农业专家助手）：（已思考{elapsed_time}秒）{response}\n",
                                     "assistant")
            self.chat_history.see(tk.END)

    def send_fixed_question(self, question):
        # 显示用户消息
        self.chat_history.tag_config("user", foreground="blue", justify=tk.RIGHT)
        self.chat_history.insert(tk.END, f"你：{question}\n", "user")

        # 显示思考提示
        thinking_text = "DeepSeek（农业专家助手）：正在思考...\n"
        self.chat_history.tag_config("assistant", foreground="green", justify=tk.LEFT)
        self.chat_history.insert(tk.END, thinking_text, "assistant")
        self.chat_history.see(tk.END)
        self.chat_history.update()

        start_time = time_module.time()
        response = self.call_deepseek_api(question)
        end_time = time_module.time()
        elapsed_time = round(end_time - start_time, 2)

        # 替换思考提示为实际响应
        self.chat_history.delete(self.chat_history.index(f"end - {len(thinking_text)}c"), tk.END)
        self.chat_history.insert(tk.END, f"DeepSeek（农业专家助手）：（已思考{elapsed_time}秒）{response}\n",
                                 "assistant")
        self.chat_history.see(tk.END)

    def save_chat_history(self):
        default_filename = datetime.now().strftime("%Y-%m-%d") + ".txt"
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                chat_text = self.chat_history.get("1.0", tk.END)
                file.write(chat_text)
            messagebox.showinfo("成功", f"聊天记录已保存到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存聊天记录时出错：{e}")

    def load_chat_history(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                chat_text = file.read()
            self.chat_history.delete("1.0", tk.END)
            self.chat_history.insert(tk.END, chat_text)
            messagebox.showinfo("成功", f"聊天记录已加载：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"加载聊天记录时出错：{e}")

    def add_reminder(self):
        reminder_window = tk.Toplevel(self.main_app.root)
        reminder_window.title("添加农事提醒")

        tk.Label(reminder_window, text="提醒内容:").grid(row=0, column=0, padx=10, pady=5)
        reminder_entry = tk.Entry(reminder_window)
        reminder_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(reminder_window, text="提醒时间:").grid(row=1, column=0, padx=10, pady=5)

        def select_date():
            def get_selected_date():
                selected_date = cal.get_date()
                # 将mm/dd/yy格式转换为YYYY-MM-DD
                dt = datetime.strptime(selected_date, '%m/%d/%y')
                new_date = dt.strftime('%Y-%m-%d')
                date_entry.delete(0, tk.END)
                date_entry.insert(0, new_date)
                top.destroy()

            top = tk.Toplevel(reminder_window)
            cal = Calendar(top, selectmode='day', year=datetime.now().year, month=datetime.now().month,
                           day=datetime.now().day)
            cal.pack(padx=10, pady=10)
            tk.Button(top, text="确定", command=get_selected_date).pack(pady=5)

        date_entry = tk.Entry(reminder_window)
        date_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(reminder_window, text="选择日期", command=select_date).grid(row=1, column=2, padx=10, pady=5)

        tk.Label(reminder_window, text="小时:").grid(row=1, column=3, padx=5, pady=5)
        hour_spinbox = Spinbox(reminder_window, from_=0, to=23, width=5)
        hour_spinbox.grid(row=1, column=4, padx=5, pady=5)
        hour_spinbox.insert(0, 0)  # 将初始值设置为0

        tk.Label(reminder_window, text="分钟:").grid(row=1, column=5, padx=5, pady=5)
        minute_spinbox = Spinbox(reminder_window, from_=0, to=59, width=5)
        minute_spinbox.grid(row=1, column=6, padx=5, pady=5)
        minute_spinbox.insert(0, 0)  # 将初始值设置为0

        def save_reminder():
            reminder = reminder_entry.get()
            date_str = date_entry.get()
            hour = hour_spinbox.get()
            minute = minute_spinbox.get()
            if reminder and date_str:
                try:
                    time_str = f"{date_str} {hour}:{minute}:00"
                    datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    with open('willdo.txt', 'a', encoding='utf-8') as f:
                        f.write(f"{reminder} - {time_str}\n")
                    self.load_todos()
                    reminder_window.destroy()
                except ValueError:
                    messagebox.showerror("错误", "时间格式不正确，请选择正确的日期和时间")
            else:
                messagebox.showerror("错误", "请输入提醒内容和选择日期")

        tk.Button(reminder_window, text="保存", command=save_reminder).grid(row=2, column=0, columnspan=7, pady=10)

    def load_todos(self):
        self.todo_text.delete("1.0", tk.END)
        try:
            with open('willdo.txt', 'r', encoding='utf-8') as f:
                todos = f.readlines()
                for todo in todos:
                    self.todo_text.insert(tk.END, todo)
        except FileNotFoundError:
            pass

    def delete_selected_todo(self):
        try:
            # 获取用户选择的行号
            line_num = self.todo_text.index(tk.INSERT).split('.')[0]
            line_num = int(line_num)
            if line_num < 1:
                raise IndexError
            # 从文本框中删除选中行
            start_index = f"{line_num}.0"
            end_index = f"{line_num + 1}.0"
            self.todo_text.delete(start_index, end_index)

            # 从文件中删除选中行
            todos = []
            with open('willdo.txt', 'r', encoding='utf-8') as f:
                todos = f.readlines()
            with open('willdo.txt', 'w', encoding='utf-8') as f:
                for index, todo in enumerate(todos, start=1):
                    if index != line_num:
                        f.write(todo)

        except (IndexError, ValueError):
            messagebox.showerror("错误", "请先选中要删除的行")


