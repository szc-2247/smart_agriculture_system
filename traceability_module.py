import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from pyzbar.pyzbar import decode
import os


class TraceabilityModule:
    def __init__(self, main_app):
        self.main_app = main_app
        self.DATA_FILE = "traceability_data.txt"

    def create_traceability_frame(self):
        # 创建左侧框架放置表格
        left_frame = tk.Frame(self.main_app.traceability_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=1)

        try:
            logo = Image.open("logo1.png")
            logo.thumbnail((400, 150))
            logo_imgtk = ImageTk.PhotoImage(image=logo)
            logo_label = tk.Label(self.main_app.traceability_frame, image=logo_imgtk)
            logo_label.image = logo_imgtk
            logo_label.pack(pady=10)
        except FileNotFoundError:
            messagebox.showerror("错误", "logo.png 文件未找到，请检查文件路径！")
        self.barcode_image_label = tk.Label(self.main_app.traceability_frame)
        self.barcode_image_label.pack(pady=10)
        self.result_label = tk.Label(self.main_app.traceability_frame, text="", font=("Arial", 12, "bold"))
        self.result_label.pack()
        input_frame = tk.Frame(self.main_app.traceability_frame)
        input_frame.pack(pady=10)
        entry_label = tk.Label(input_frame, text="手动输入溯源代码：")
        entry_label.pack(side=tk.LEFT, padx=10)
        self.entry = tk.Entry(input_frame, width=20)
        self.entry.pack(side=tk.LEFT, padx=10)
        search_button = tk.Button(input_frame, text="搜索", command=self.search_with_input)
        search_button.pack(side=tk.LEFT, padx=10)
        upload_button = tk.Button(self.main_app.traceability_frame, text="上传条形码图片", command=self.upload_and_recognize)
        upload_button.pack(pady=10)

        # 创建表格
        self.create_table(left_frame)
        self.populate_table()

    def create_table(self, frame):
        columns = ("溯源码", "溯源地")
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def populate_table(self):
        data = self.load_data()
        for code, address in data.items():
            self.tree.insert('', 'end', values=(code, address))

    def search_with_input(self):
        code = self.entry.get().strip()
        if not code:
            messagebox.showwarning("警告", "请输入溯源代码！")
            return
        self.search_traceability(code)

    def search_traceability(self, code):
        data = self.load_data()
        if code in data:
            self.result_label.config(text=f"溯源地址：{data[code]}")
        else:
            messagebox.showwarning("警告", "未找到对应的溯源地址！")

    def upload_and_recognize(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not file_path:
            return
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在：{file_path}")
            return
        try:
            img = Image.open(file_path)
            img.thumbnail((400, 400))
            imgtk = ImageTk.PhotoImage(image=img)
            self.barcode_image_label.config(image=imgtk)
            self.barcode_image_label.image = imgtk
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图片：{e}")
            return

        try:
            frame = cv2.imread(file_path)
            if frame is None:
                messagebox.showerror("错误", f"无法读取图片：{file_path}")
                return

            barcodes = decode(frame)
            if barcodes:
                barcode_data = barcodes[0].data.decode('utf-8')
                self.search_traceability(barcode_data)
            else:
                messagebox.showwarning("警告", "未检测到条形码！")
        except Exception as e:
            messagebox.showerror("错误", f"处理图片时出错：{e}")

    def load_data(self):
        data = {}
        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as file:
                for line in file:
                    code, address = line.strip().split(",")
                    data[code] = address
        except FileNotFoundError:
            messagebox.showerror("错误", "数据文件未找到，请检查文件路径！")
        except Exception as e:
            messagebox.showerror("错误", f"读取数据文件时出错：{e}")
        return data