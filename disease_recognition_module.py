import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import random
import openai
import requests
from datetime import datetime


class DiseaseRecognitionModule:
    def __init__(self, main_app):
        self.main_app = main_app
        self.DEEPSEEK_API_KEY = "sk-fdc6a02e984c4781b7c2d1e913f8806d"

    def create_disease_frame(self):
        # 上半部分：图片识别部分
        upper_frame = tk.Frame(self.main_app.disease_frame)
        upper_frame.pack(fill=tk.BOTH, expand=True)

        # 操作区放在左边
        operation_frame = tk.Frame(upper_frame, width=200)
        operation_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        upload_button = tk.Button(operation_frame, text="上传图片", command=self.upload_image)
        upload_button.pack(pady=5)
        recognize_button = tk.Button(operation_frame, text="开始识别", command=self.recognize_image)
        recognize_button.pack(pady=5)
        refresh_button = tk.Button(operation_frame, text="刷新", command=self.refresh)
        refresh_button.pack(pady=5)
        exit_button = tk.Button(operation_frame, text="退出", command=self.main_app.disease_frame.destroy)
        exit_button.pack(pady=5)

        # 中间部分，包含图片预留区和识别结果等
        middle_frame = tk.Frame(upper_frame)
        middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # 图片预留区
        image_frame = tk.Frame(middle_frame)
        image_frame.pack(fill=tk.X, padx=10, pady=5)
        self.image_label = tk.Label(image_frame)
        self.image_label.pack()

        result_frame = tk.Frame(middle_frame)
        result_frame.pack(fill=tk.X, padx=10, pady=5)
        self.result_label = tk.Label(result_frame, text="识别结果：")
        self.result_label.pack()

        confidence_frame = tk.Frame(middle_frame)
        confidence_frame.pack(fill=tk.X, padx=10, pady=5)
        self.confidence_label = tk.Label(confidence_frame, text="识别正确概率：")
        self.confidence_label.pack()

        # 右边部分：measures 显示区
        measures_frame = tk.Frame(upper_frame, borderwidth=2, relief=tk.GROOVE, padx=10, pady=10)
        measures_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = tk.Scrollbar(measures_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.measures_text = tk.Text(measures_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=10, width=50)
        self.measures_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.measures_text.yview)

        # 下半部分：用户输入疾病查询部分
        lower_frame = tk.Frame(self.main_app.disease_frame)
        lower_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        input_label = tk.Label(lower_frame, text="输入疾病名称：（人工智能输出需要10-20s，请耐心等待！）")
        input_label.pack(side=tk.LEFT, padx=10)

        self.disease_entry = tk.Entry(lower_frame)
        self.disease_entry.pack(side=tk.LEFT, padx=10)

        query_button = tk.Button(lower_frame, text="查询疾病", command=self.query_user_input_disease)
        query_button.pack(side=tk.LEFT, padx=10)

        clear_button = tk.Button(lower_frame, text="清空", command=self.clear_lower_output)
        clear_button.pack(side=tk.LEFT, padx=10)

        # 下半部分输出框
        self.lower_output_frame = tk.Frame(self.main_app.disease_frame, borderwidth=2, relief=tk.GROOVE, padx=10, pady=10)
        self.lower_output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        lower_scrollbar = tk.Scrollbar(self.lower_output_frame)
        lower_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lower_output_text = tk.Text(self.lower_output_frame, wrap=tk.WORD, yscrollcommand=lower_scrollbar.set, height=10, width=50)
        self.lower_output_text.pack(fill=tk.BOTH, expand=True)
        lower_scrollbar.config(command=self.lower_output_text.yview)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not file_path:
            messagebox.showinfo("提示", "未选择任何图片")
            return
        self.main_app.image_path = file_path
        try:
            img = Image.open(file_path)
            img.thumbnail((200, 200))  # 减小图片显示大小
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.configure(image=img_tk)
            self.image_label.image = img_tk
            self.result_label.config(text="识别结果：")
            self.confidence_label.config(text="识别正确概率：")
            self.measures_text.delete(1.0, tk.END)
            print(f"上传图片成功，路径：{self.main_app.image_path}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图片：{e}")

    def simulate_recognition(self, image_path):
        diseases = ["小麦叶枯病"]
        disease = random.choice(diseases)
        confidence = random.uniform(0.7, 0.99)
        print(f"模拟识别结果：疾病={disease}，置信度={confidence}")
        return disease, confidence

    def recognize_image(self):
        if not self.main_app.image_path:
            messagebox.showinfo("提示", "请先上传图片")
            return
        try:
            disease, confidence = self.simulate_recognition(self.main_app.image_path)
            self.result_label.config(text=f"识别结果：{disease}")
            self.confidence_label.config(text=f"识别正确概率：{confidence:.2f}")
            self.display_measures(disease)
        except Exception as e:
            print(f"识别图片时出错：{e}")
            messagebox.showerror("错误", f"识别图片时出错：{e}")

    def refresh(self):
        if hasattr(self, 'image_label'):
            self.image_label.config(image=None)
        self.result_label.config(text="识别结果：")
        self.confidence_label.config(text="识别正确概率：")
        self.measures_text.delete(1.0, tk.END)
        self.main_app.image_path = None

    def display_measures(self, disease):
        self.measures_text.delete(1.0, tk.END)
        measures = (
            "化学防治\n"
            "药剂拌种和种子消毒\n"
            "主要药剂有 25% 三唑酮（粉锈宁）可湿性粉剂 75g，拌麦种 100kg 闷种；\n"
            "75% 萎锈灵可湿性粉剂 250g，拌麦种 100kg 闷种；\n"
            "50% 多福混合粉（25% 多菌灵 + 25% 福美双）500 倍液，浸种 48 小时；\n"
            "50% 多菌灵可湿性粉剂、70% 甲基硫菌灵（甲基托布津）可湿性粉剂、40% 拌种灵可湿性粉剂、40% 拌种双可湿性粉剂等 4 种药剂，\n"
            "均按种子重量 0.2% 拌种，其中拌种灵和拌种双易产生药害，使用时要严格控制剂量，避免湿拌。\n"
            "有条件的地区，也可使用种子重量 0.15% 的噻菌灵（涕必灵）（有效成分）、0.03% 的三唑醇（羟锈宁）（有效成分）拌种，\n"
            "控制效果均较好 。\n"
            "\n"
            "喷药\n"
            "重病区，可在小麦分蘖前期，每亩用 70% 代森锰锌可湿性粉剂 143 克或 75% 百菌清可湿性粉剂 15 克（均加水 50 - 75 升），\n"
            "或 65% 代森锌可湿性粉剂 1000 倍液或 1:1:140 波尔多液进行喷药保护，每隔 7 - 10 天喷洒 1 次，共喷 2 - 3 次。\n"
            "也可在小麦挑旗期顶三叶病情达 5% 时，亩用 25% 或 50% 苯菌灵可湿性粉剂 17 - 20 克（有效成分）或 25% 丙环唑乳油 33 毫升，\n"
            "加水 50 - 75 升喷雾，每隔 14 - 28 天喷 1 次，共喷 1 - 3 次，可有效地控制小麦叶枯病的流行为害 。"
        )
        self.measures_text.insert(tk.END, f"针对{disease}的防治措施：\n{measures}")

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
                f"你是一个翎创游戏研发社团所研发的一个名字叫'小农'的农业疾病专家助手，你会为用户给出关于该疾病的建议和防治方法，"
                f"你在与用户聊天时，不需要使用markdown格式."

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

    def query_user_input_disease(self):
        disease = self.disease_entry.get()
        if disease:
            response = self.call_deepseek_api(f"请提供关于{disease}的更多信息和防治建议")
            self.lower_output_text.delete(1.0, tk.END)  # 清空下半部分输出框
            self.lower_output_text.insert(tk.END, response)
        else:
            messagebox.showinfo("提示", "请输入疾病名称")

    def clear_lower_output(self):
        self.lower_output_text.delete(1.0, tk.END)


class MainApp:
    def __init__(self, disease_frame):
        self.disease_frame = disease_frame
        self.image_path = None
        self.disease_module = DiseaseRecognitionModule(self)
        self.disease_module.create_disease_frame()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()