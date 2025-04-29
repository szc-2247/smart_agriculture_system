import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta, time
import geocoder
import socket
import time as time_module
import os

from weather_module import WeatherModule
from seed_search_module import SeedSearchModule
from soil_moisture_module import SoilMoistureModule
from disease_recognition_module import DiseaseRecognitionModule
from chat_module import ChatModule
from traceability_module import TraceabilityModule
from price_module import PriceModule

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

DEEPSEEK_API_KEY = "sk-fdc6a02e984c4781b7c2d1e913f8806d"


class SmartAgricultureSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("智农兴商———智慧农业乡村振兴系统demo——已接入 deepseek - V3  满血版")
        self.root.geometry("1000x600")
        self.create_search_bar()
        self.image_path = None
        self.create_top_info_bar()

        # 初始化所有模块
        self.weather_module = WeatherModule(self)
        self.seed_search_module = SeedSearchModule(self)
        self.soil_moisture_module = SoilMoistureModule(self)
        self.disease_recognition_module = DiseaseRecognitionModule(self)
        self.chat_module = ChatModule(self)
        self.traceability_module = TraceabilityModule(self)
        self.price_module = PriceModule(self)  # 初始化 PriceModule

        # 调用 create_notebook 方法
        self.create_notebook()

        self.show_current_moisture()
        self.update_time()
        self.update_location()
        self.update_ip()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_search_bar(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        search_label = tk.Label(search_frame, text="搜索一下")
        search_label.pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_button = tk.Button(search_frame, text="搜索", command=self.search_webpage)
        search_button.pack(side=tk.RIGHT, padx=10)

    def create_top_info_bar(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        self.time_label = tk.Label(top_frame, text="当前时间：--", font=("", 14))
        self.time_label.pack(side=tk.LEFT)
        self.location_label = tk.Label(top_frame, text="当前地点：-", font=("", 14))
        self.location_label.pack(side=tk.LEFT, padx=20)
        self.ip_label = tk.Label(top_frame, text="当前登录 IP：-", font=("", 14))
        self.ip_label.pack(side=tk.LEFT, padx=20)

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.weather_frame = tk.Frame(self.notebook)
        self.notebook.add(self.weather_frame, text="***天气预报***")
        self.weather_module.create_weather_frame()

        self.seed_search_frame = tk.Frame(self.notebook)
        self.notebook.add(self.seed_search_frame, text="***种子查询***")
        self.seed_search_module.create_seed_search_frame()

        self.price_frame = tk.Frame(self.notebook)
        self.notebook.add(self.price_frame, text="***农产品价格查询***")
        self.price_module.create_price_frame()  # 在这里调用 create_price_frame

        self.soil_frame = tk.Frame(self.notebook)
        self.notebook.add(self.soil_frame, text="***土壤湿度数据***")
        self.soil_moisture_module.create_soil_frame()

        self.disease_frame = tk.Frame(self.notebook)
        self.notebook.add(self.disease_frame, text="***农作物疾病识别***")
        self.disease_recognition_module.create_disease_frame()

        self.chat_frame = tk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="***对话功能***")
        self.chat_module.create_chat_frame()

        self.traceability_frame = tk.Frame(self.notebook)
        self.notebook.add(self.traceability_frame, text="***农产品溯源***")
        self.traceability_module.create_traceability_frame()

    def search_webpage(self):
        keyword = self.search_entry.get()
        if keyword:
            url = f"https://cn.bing.com/search?q=  {keyword}&qs=n&form=QBRE&sp=-1&lq=0&pq={keyword}&sc=15-3&sk=&cvid=B020E58B3B17479D897A8051D14F96BD&ghsh=0&ghacc=0&ghpl="
            import webbrowser
            webbrowser.open(url)

    def show_current_moisture(self):
        self.soil_moisture_module.show_current_moisture()

    def update_time(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"当前时间：{now}")
        self.root.after(1000, self.update_time)

    def update_location(self):
        try:
            g = geocoder.ipinfo('me')
            if not g.ok:
                g = geocoder.geocodefarm('me')
            if g.ok:
                location = g.city or g.town or g.country or "未知地点"
                self.location_label.config(text=f"当前地点：{location}")
            else:
                self.location_label.config(text="当前地点：无法获取位置信息")
        except:
            self.location_label.config(text="当前地点：无法获取位置信息")
        self.root.after(60 * 1000, self.update_location)

    def update_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            self.ip_label.config(text=f"当前登录 IP：{ip}")
        except Exception:
            self.ip_label.config(text="当前登录 IP：无法获取 IP 信息")
        self.root.after(60 * 1000, self.update_ip)

    def on_close(self):
        self.weather_module.clear_files()
        self.root.destroy()
