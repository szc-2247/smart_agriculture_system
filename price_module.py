import tkinter as tk
from tkinter import ttk
import datetime
import openai
import requests


class PriceModule:
    def __init__(self, main_app):
        self.main_app = main_app
        self.DEEPSEEK_API_KEY = "sk-fdc6a02e984c4781b7c2d1e913f8806d"  # 请替换为你的实际 API 密钥
        self.is_searching = False  # 用于标记是否处于检索状态
        self.all_data = []  # 用于存储所有农作物数据
        self.search_button = None  # 存储检索按钮对象
        self.stop_search_button = None  # 存储停止检索按钮对象

    def create_price_frame(self):
        # 创建价格查询和分析的框架
        self.price_frame = tk.Frame(self.main_app.price_frame)
        self.price_frame.pack(fill=tk.BOTH, expand=True)

        # 上半部分：农作物查询和价格表格
        upper_frame = tk.Frame(self.price_frame)
        upper_frame.pack(fill=tk.BOTH, expand=True)

        # 各类标签用于查询农作物
        label_frame = tk.Frame(upper_frame)
        label_frame.pack()
        crop_label = tk.Label(label_frame, text="选择农作物种类:")
        crop_label.pack(side=tk.LEFT)
        self.crop_combobox = ttk.Combobox(label_frame, values=["小麦", "玉米", "水稻", "大豆", "高粱"])
        self.crop_combobox.pack(side=tk.LEFT)
        self.crop_combobox.bind("<<ComboboxSelected>>", self.show_selected_crop)

        # 价格区间检索框
        price_range_frame = tk.Frame(label_frame)
        price_range_frame.pack(side=tk.LEFT)
        min_price_label = tk.Label(price_range_frame, text="最小价格:")
        min_price_label.pack(side=tk.LEFT)
        self.min_price_entry = tk.Entry(price_range_frame)
        self.min_price_entry.pack(side=tk.LEFT)
        max_price_label = tk.Label(price_range_frame, text="最大价格:")
        max_price_label.pack(side=tk.LEFT)
        self.max_price_entry = tk.Entry(price_range_frame)
        self.max_price_entry.pack(side=tk.LEFT)
        self.search_button = tk.Button(price_range_frame, text="检索", command=self.search_by_crop_and_price)
        self.search_button.pack(side=tk.LEFT)
        self.stop_search_button = tk.Button(price_range_frame, text="停止检索", command=self.stop_search, state=tk.DISABLED)
        self.stop_search_button.pack(side=tk.LEFT)

        # 可视化表格显示农作物价格信息
        table_frame = tk.Frame(upper_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("农作物名称", "价格", "日期")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.load_price_data()

        # 下半部分：DeepSeek 分析
        lower_frame = tk.Frame(self.price_frame)
        lower_frame.pack(fill=tk.BOTH, expand=True)

        # 左边部分：用户输入和提示词按钮
        left_frame = tk.Frame(lower_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 用户输入框
        input_frame = tk.Frame(left_frame)
        input_frame.pack(fill=tk.X)
        self.input_entry = tk.Entry(input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        send_button = tk.Button(input_frame, text="发送", command=lambda: self.send_prompt(self.input_entry.get()))
        send_button.pack(side=tk.LEFT)
        self.input_entry.bind("<Return>", self.on_enter_pressed)  # 绑定回车键事件

        # 提示词按钮
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X)
        prompt_buttons = [
            ("分析价格", "请你帮我分析一下农作物的价格趋势"),
            ("价格波动情况", "请你分析一下农作物价格的波动情况"),
            ("价格与市场关系", "请你分析一下农作物价格与市场的关系")
        ]
        for text, prompt in prompt_buttons:
            button = tk.Button(button_frame, text=text, command=lambda p=prompt: self.send_prompt(p))
            button.pack(side=tk.LEFT)

        # 清空输出框按钮
        clear_button = tk.Button(button_frame, text="清空输出框", command=self.clear_output)
        clear_button.pack(side=tk.LEFT)

        # 右边部分：输出框
        right_frame = tk.Frame(lower_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.output_text = tk.Text(right_frame)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def load_price_data(self):
        try:
            with open('price.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    data = line.strip().split(',')
                    if len(data) == 3:
                        self.tree.insert("", "end", values=data)
                        self.all_data.append(data)
        except FileNotFoundError:
            print("未找到 price.txt 文件")

    def send_prompt(self, prompt):
        message = prompt if prompt else self.input_entry.get()
        result = self.call_deepseek_api(message)
        self.output_text.insert(tk.END, f"用户: {message}\n")
        self.output_text.insert(tk.END, f"助手: {result}\n")

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)

    def call_deepseek_api(self, message):
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d %A %H:%M:%S")
            client = openai.OpenAI(
                api_key=self.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
                timeout=100
            )
            system_message = (
                f"你是一个翎创游戏研发社团所研发的一个名字叫'小农'的农产品价格分析专家助手，"
                f"你在与用户聊天时，不能失去专业水准，不需要使用markdown格式."
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

    def on_enter_pressed(self, event):
        prompt = self.input_entry.get()
        if prompt:
            self.send_prompt(prompt)

    def show_selected_crop(self, event):
        selected_crop = self.crop_combobox.get()
        self.tree.delete(*self.tree.get_children())
        for data in self.all_data:
            if data[0] == selected_crop:
                self.tree.insert("", "end", values=data)

    def search_by_crop_and_price(self):
        selected_crop = self.crop_combobox.get()
        min_price_str = self.min_price_entry.get()
        max_price_str = self.max_price_entry.get()

        min_price = float(min_price_str) if min_price_str else float('-inf')
        max_price = float(max_price_str) if max_price_str else float('inf')

        self.tree.delete(*self.tree.get_children())
        for data in self.all_data:
            if data[0] == selected_crop:
                price = float(data[1])
                if min_price <= price <= max_price:
                    self.tree.insert("", "end", values=data)

        self.is_searching = True
        self.update_search_buttons_state()

    def stop_search(self):
        self.tree.delete(*self.tree.get_children())
        self.load_price_data()
        self.is_searching = False
        self.update_search_buttons_state()

    def update_search_buttons_state(self):
        if self.is_searching:
            self.search_button.config(state=tk.DISABLED)
            self.stop_search_button.config(state=tk.NORMAL)
        else:
            self.search_button.config(state=tk.NORMAL)
            self.stop_search_button.config(state=tk.DISABLED)
