import tkinter as tk
from smart_agriculture_system import SmartAgricultureSystem


def start_main():
    root = tk.Tk()
    app = SmartAgricultureSystem(root)
    root.mainloop()


if __name__ == "__main__":
    start_main()
    