import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd


class SoilMoistureModule:
    def __init__(self, main_app):
        self.main_app = main_app

    def create_soil_frame(self):
        # 整体框架分为左右两部分
        left_frame = tk.Frame(self.main_app.soil_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        right_frame = tk.Frame(self.main_app.soil_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 左侧表格部分
        self.tree = ttk.Treeview(left_frame, columns=("采样时间", "土壤深度（cm）", "土壤湿度（%）", "光照强度（Lux）"),
                                 show="headings")
        for col in ("采样时间", "土壤深度（cm）", "土壤湿度（%）", "光照强度（Lux）"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 右侧上方当前数据部分
        middle_frame = tk.Frame(right_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.current_label = tk.Label(middle_frame, text="当前土壤相对湿度：--%", font=("", 30), fg="blue")
        self.current_label.pack(pady=20)
        self.progress = ttk.Progressbar(middle_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack()

        # 右侧下方按钮部分
        bottom_frame = tk.Frame(right_frame)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        history_button = tk.Button(bottom_frame, text="查看历史数据", command=self.show_history_chart)
        history_button.pack(side=tk.LEFT, padx=10)
        refresh_button = tk.Button(bottom_frame, text="刷新当前数据", command=self.show_current_moisture)
        refresh_button.pack(side=tk.LEFT)

        self.history_frame = tk.Frame(right_frame)
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 读取数据并填充表格
        self.load_data()

    def load_data(self):
        try:
            df = pd.read_csv('dirt.txt', sep='\s+')
            for index, row in df.iterrows():
                self.tree.insert("", "end", values=list(row))
        except FileNotFoundError:
            import tkinter.messagebox
            tkinter.messagebox.showerror("错误", "未找到 dirt.txt 文件！")
        except Exception as e:
            import tkinter.messagebox
            tkinter.messagebox.showerror("错误", f"读取文件时出错：{e}")

    def generate_soil_moisture_data(self):
        today = datetime.today()
        dates = [(today - timedelta(days=5) + timedelta(days=i)).date() for i in range(5)]
        dates = [date.strftime("%Y-%m-%d") for date in dates]
        moisture_levels = [random.randint(15, 25) for _ in range(5)]
        return dates, moisture_levels

    def show_history_chart(self):
        try:
            dates, moisture_levels = self.generate_soil_moisture_data()
            fig, ax = plt.subplots()
            ax.plot(dates, moisture_levels, marker='o')
            ax.set_xlabel('日期')
            ax.set_ylabel('土壤湿度 (%)')
            ax.set_title('土壤湿度历史数据')
            ax.grid(True)
            canvas = FigureCanvasTkAgg(fig, master=self.history_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        except Exception as e:
            import tkinter.messagebox
            tkinter.messagebox.showerror("错误", f"显示历史数据图表时出错：{e}")

    def show_current_moisture(self):
        current_moisture = random.randint(15, 25)
        self.current_label.config(text=f"当前土壤相对湿度：{current_moisture}%")
        self.progress['value'] = current_moisture


if __name__ == "__main__":
    root = tk.Tk()
    root.title("土壤湿度模块")
    soil_frame = tk.Frame(root)
    soil_frame.pack(fill=tk.BOTH, expand=True)
    app = SoilMoistureModule(main_app=type('MainApp', (object,), {'soil_frame': soil_frame})())
    app.create_soil_frame()
    root.mainloop()
