import requests
from bs4 import BeautifulSoup
import json
import tkinter as tk
from tkinter import ttk


class WeatherModule:
    def __init__(self, main_app):
        self.main_app = main_app

    def create_weather_frame(self):
        weather_button = tk.Button(self.main_app.weather_frame, text="获取并展示天气数据", command=self.show_weather_data)
        weather_button.pack(side=tk.TOP, padx=10, pady=5)

        self.today_weather_frame = tk.Frame(self.main_app.weather_frame)
        self.today_weather_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.future_weather_frame = tk.Frame(self.main_app.weather_frame)
        self.future_weather_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建当天天气的空表格
        today_headers = ['小时', '温度', '风力方向', '风级', '降水量', '相对湿度', '空气质量']
        self.create_table_title(self.today_weather_frame, "当天天气数据")
        self.create_table(self.today_weather_frame, today_headers, [])

        # 创建未来7天天气的空表格
        future_headers = ['日期', '天气', '最低气温', '最高气温', '风向1', '风向2', '风级']
        self.create_table_title(self.future_weather_frame, "未来7天天气数据")
        self.create_table(self.future_weather_frame, future_headers, [])

    def clear_files(self):
        file_paths = ["weather1.txt", "weather7.txt", "message.txt"]
        for file_path in file_paths:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.truncate()
            except FileNotFoundError:
                pass

    def getHTMLtext(self, url):
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            print("成功访问")
            return r.text
        except:
            print("访问错误")
            return " "

    def get_content(self, html):
        final = []
        bs = BeautifulSoup(html, "html.parser")
        body = bs.body
        data = body.find('div', {'id': '7d'})
        data2 = body.find_all('div', {'class': 'left-div'})
        text = data2[2].find('script').string
        text = text[text.index('=') + 1:-2]
        jd = json.loads(text)
        dayone = jd['od']['od2']
        dayone = dayone[::-1]
        final_day = []
        for i in dayone:
            temp = []
            temp.append(i['od21'])
            temp.append(i['od22'])
            temp.append(i['od24'])
            temp.append(i['od25'])
            temp.append(i['od26'])
            temp.append(i['od27'])
            temp.append(i['od28'])
            final_day.append(temp)
        ul = data.find('ul')
        li = ul.find_all('li')
        final = []
        for day in li[1:8]:
            temp = []
            date = day.find('h1').string
            date = date[0:date.index('日')]
            temp.append(date)
            inf = day.find_all('p')
            temp.append(inf[0].string)
            temp.append(inf[1].find('i').string[:-1])
            if inf[1].find('span'):
                temp.append(inf[1].find('span').string)
            else:
                temp.append(None)
            wind = [span['title'] for span in inf[2].find_all('span')]
            temp.extend(wind)
            wind_scale = inf[2].find('i').string
            temp.append(int(wind_scale[wind_scale.index('级') - 1:wind_scale.index('级')]))
            final.append(temp)
        return final_day, final

    def write_to_txt(self, file_name, data, day=7):
        with open(file_name, 'a', errors='ignore', encoding='utf-8') as f:
            if day == 7:
                header = ['日期', '天气', '最低气温', '最高气温', '风向1', '风向2', '风级']
            else:
                header = ['小时', '温度', '风力方向', '风级', '降水量', '相对湿度', '空气质量']
            f.write('\t'.join(header) + '\n')
            for row in data:
                row_str = '\t'.join(map(str, row))
                f.write(row_str + '\n')

    def show_weather_data(self):
        url1 = 'http://www.weather.com.cn/weather/101181001.shtml'
        html1 = self.getHTMLtext(url1)
        data1, data1_7 = self.get_content(html1)
        self.write_to_txt('weather1.txt', data1, 1)
        self.write_to_txt('weather7.txt', data1_7, 7)
        self.display_txt_content('weather1.txt', self.today_weather_frame)
        self.display_txt_content('weather7.txt', self.future_weather_frame)

    def display_txt_content(self, file_path, frame):
        try:
            headers, data = self.read_txt_file(file_path)
            if 'weather1.txt' in file_path:
                table_name = "当天天气数据"
            elif 'weather7.txt' in file_path:
                table_name = "未来7天天气数据"
            else:
                table_name = "天气数据"
            # 先清空原有表格
            for widget in frame.winfo_children():
                widget.destroy()
            self.create_table_title(frame, table_name)
            self.create_table(frame, headers, data)
        except FileNotFoundError:
            pass

    def read_txt_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            headers = lines[0].strip().split('\t')
            data = [line.strip().split('\t') for line in lines[1:]]
        return headers, data

    def create_table_title(self, frame, table_name):
        title_label = tk.Label(frame, text=table_name, font=("", 14, "bold"))
        title_label.pack(pady=5)

    def create_table(self, frame, headers, data):
        tree = ttk.Treeview(frame, columns=headers, show='headings')
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, width=100)
        for row in data:
            tree.insert('', 'end', values=row)
        tree.pack(fill=tk.BOTH, expand=True)