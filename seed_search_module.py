import tkinter as tk
from tkinter import messagebox
import openai
import requests
import time as time_module
from datetime import datetime
from tkinter import ttk


class SeedSearchModule:
    def __init__(self, main_app):
        self.main_app = main_app
        self.DEEPSEEK_API_KEY = "sk-fdc6a02e984c4781b7c2d1e913f8806d"

    def create_seed_search_frame(self):
        # 创建主框架，使用水平排列
        main_frame = tk.Frame(self.main_app.seed_search_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建种子信息表格框架
        table_frame = tk.Frame(main_frame)
        table_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # 创建表格
        self.tree = ttk.Treeview(table_frame, columns=('品种', '对应种子'), show='headings')
        self.tree.heading('品种', text='品种')
        self.tree.heading('对应种子', text='对应种子')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 从文件中读取种子信息并插入表格
        try:
            with open('seed.txt', 'r', encoding='utf-8') as file:
                for line in file:
                    variety, seed = line.strip().split(',')
                    self.tree.insert('', 'end', values=(variety, seed))
        except FileNotFoundError:
            messagebox.showwarning("警告", "未找到 seed.txt 文件！")
        except ValueError:
            messagebox.showwarning("警告", "seed.txt 文件格式错误！")

        # 创建种子查询框架
        self.seed_search_frame = tk.Frame(main_frame)
        self.seed_search_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 定义 10 种种子名称
        seeds = ["小麦", "玉米", "水稻", "大豆", "花生", "棉花", "油菜", "番茄", "黄瓜", "茄子"]

        # 创建种子按钮框架
        button_frame = tk.Frame(self.seed_search_frame)
        button_frame.pack(pady=10)
        for seed in seeds:
            button = tk.Button(button_frame, text=seed, command=lambda s=seed: self.search_seed(s))
            button.pack(side=tk.LEFT, padx=5)

        # 创建种子名称输入框和提示信息
        input_frame = tk.Frame(self.seed_search_frame)
        input_frame.pack(pady=10)
        seed_name_label = tk.Label(input_frame, text="请输入种子名称:")
        seed_name_label.pack(side=tk.LEFT, padx=5)
        self.seed_name_entry = tk.Entry(input_frame)
        self.seed_name_entry.insert(0, "例如：小麦、山东48小麦")
        self.seed_name_entry.bind("<FocusIn>", self.clear_placeholder)
        self.seed_name_entry.bind("<FocusOut>", self.restore_placeholder)
        self.seed_name_entry.pack(side=tk.LEFT, padx=5)

        # 创建查询和清除按钮框架
        action_frame = tk.Frame(self.seed_search_frame)
        action_frame.pack(pady=20)
        search_button = tk.Button(action_frame, text="查询", command=self.search_seed)
        search_button.pack(side=tk.LEFT, padx=5)
        clear_button = tk.Button(action_frame, text="清除结果", command=self.clear_result)
        clear_button.pack(side=tk.LEFT, padx=5)
        txt_button = tk.Button(action_frame, text="（人工智能输出需要10 - 20s，请耐心等待！）")
        txt_button.pack(side=tk.LEFT, padx=5)

        # 创建结果显示区域和滚动条
        result_frame = tk.Frame(self.seed_search_frame)
        result_frame.pack(pady=10)
        self.result_text = tk.Text(result_frame, height=10, width=50)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(result_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)

    def clear_placeholder(self, event):
        if self.seed_name_entry.get() == "例如：小麦、山东48小麦":
            self.seed_name_entry.delete(0, tk.END)

    def restore_placeholder(self, event):
        if self.seed_name_entry.get() == "":
            self.seed_name_entry.insert(0, "例如：小麦、山东48小麦")

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
            except FileNotFoundError:
                today_weather = "未知"
                future_weather = "未知"
                dirt_message = "未知"
                chatting_message = "未知"
            system_message = (
                f"你是一个翎创游戏研发社团所研发的一个名字叫'小农'的农业专家助手，"
                f"你是一个种子专家，不能失去专业水准，输出内容时不需要使用markdown格式."
                f"如果用户询问的是一个种子大类的时候，请你回答必要的内容之后推荐几个对应的种子品种。如果用户询问种子品种时，直接回答必要的内容."
                f"今天是{today}，今天的天气是：{today_weather}\n未来七天的天气是：{future_weather}"
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

            return result
        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"
        except openai.APIConnectionError as e:
            return f"API连接异常：{str(e)}"
        except openai.APIError as e:
            return f"API返回错误：{str(e)}"
        except Exception as e:
            return f"未预期错误：{str(e)}"

    def search_seed(self, seed_name=None):
        if seed_name is None:
            seed_name = self.seed_name_entry.get()
        if seed_name and seed_name != "例如：小麦、山东48小麦":
            query_message = f"请告诉我关于 {seed_name} 种子的特性和种植建议。"
            self.result_text.insert(tk.END, "正在思考...\n")
            self.result_text.update()
            start_time = time_module.time()
            response = self.call_deepseek_api(query_message)
            end_time = time_module.time()
            elapsed_time = round(end_time - start_time, 2)
            # 计算要删除内容的起始索引
            start_index = self.result_text.index(tk.END + '- 2 lines linestart')
            self.result_text.delete(start_index, tk.END)
            self.result_text.insert(tk.END, f"已思考{elapsed_time}秒\n{response}\n")
        else:
            messagebox.showwarning("警告", "请输入有效的种子名称！")

    def clear_result(self):
        self.result_text.delete(1.0, tk.END)
