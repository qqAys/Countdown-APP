import json
import os
import tkinter as tk
from ctypes import windll
from tkinter import ttk, messagebox

import winsound

APP_NAME_ENGLISH = "Countdown APP"
APP_NAME_CHINESE = "倒计时APP"
VERSION = "0.0.0.2"
AUTHOR = "Jinx@qqAys"
URL = "https://github.com/qqAys/Countdown-APP"

CONFIG_FILE = "countdown_app_config.json"


CONFIG_LOAD_ERROR = "加载配置出错"
CONFIG_SAVE_ERROR = "保存配置出错"
VALUE_ERROR = "值错误"
VALUE_DUPLICATE = "值重复"
OPERATION_ERROR = "操作错误"
OPERATION_SUCCESS = "操作成功"


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config
        except Exception as e:
            messagebox.showerror(CONFIG_LOAD_ERROR, f"加载配置出错: {e}")
    return {}


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f)
    except Exception as e:
        messagebox.showerror(CONFIG_SAVE_ERROR, f"保存配置出错: {e}")


class CountdownApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME_CHINESE)

        # 高DPI适配
        windll.shcore.SetProcessDpiAwareness(1)
        scale_factor = windll.shcore.GetScaleFactorForDevice(0)
        self.tk.call('tk', 'scaling', scale_factor / 75)

        width = 350
        height = 500
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        size_geo = "%dx%d+%d+%d" % (
            width,
            height,
            (screenwidth - width) / 2,
            (screenheight - height) / 2,
        )
        self.geometry(size_geo)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.iconbitmap("favicon.ico")

        menubar = tk.Menu(self)
        self.config(menu=menubar)
        menubar.add_command(
            label="关于",
            command=lambda: messagebox.showinfo("关于", f"{APP_NAME_ENGLISH} v{VERSION}\n\n{AUTHOR} {URL}")
        )

        self.config_data = load_config()
        self.preset_times = self.config_data.get("preset_times", [20, 30, 50, 60, 200])
        self.custom_times = self.config_data.get("custom_times", [])
        self.custom_time_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # 预设时间区域
        preset_frame = ttk.LabelFrame(self, text="预设时间")
        preset_frame.pack(padx=10, pady=10, fill="x")

        for i, t in enumerate(self.preset_times):
            row = i // 3
            col = i % 3
            btn = ttk.Button(preset_frame, text=f"{t}秒", command=lambda t=t: self.start_countdown(t))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        for col in range(3):
            preset_frame.columnconfigure(col, weight=1)

        # 自定义时间区域
        custom_frame = ttk.LabelFrame(self, text="自定义时间")
        custom_frame.pack(padx=10, pady=10, fill="both", expand=True)
        entry_label = ttk.Label(custom_frame, text="输入秒数：")
        entry_label.pack(padx=12, pady=(5, 0), anchor="w")
        entry = ttk.Entry(custom_frame, textvariable=self.custom_time_var, width=10)
        entry.pack(padx=12, pady=5, anchor="w")
        btn_frame = ttk.Frame(custom_frame)
        btn_frame.pack(padx=5, pady=5, anchor="w")
        save_btn = ttk.Button(btn_frame, text="保存", command=self.save_custom_time)
        save_btn.pack(side="left", padx=5)
        start_input_btn = ttk.Button(btn_frame, text="使用", command=self.start_input_countdown)
        start_input_btn.pack(side="left", padx=5)

        list_label = ttk.Label(custom_frame, text="已保存的自定义时间（秒）：")
        list_label.pack(padx=5, pady=(10, 0), anchor="w")
        self.listbox = tk.Listbox(custom_frame, height=5)
        self.listbox.pack(padx=5, pady=5, fill="both", expand=True)
        # 按键绑定
        self.listbox.bind("<Double-1>", self.on_listbox_double_click)
        self.listbox.bind("<Button-3>", self.on_listbox_click)

        self.context_menu = tk.Menu(self, tearoff=0)  # 初始化右键弹窗
        self.context_menu.add_command(label="使用",command=self.start_list_countdown)
        self.context_menu.add_command(label="删除", command=self.delete_custom_time)

        self.update_listbox()

        # 使用列表倒计时按钮
        start_list_btn = ttk.Button(custom_frame, text="使用选中", command=self.start_list_countdown)
        start_list_btn.pack(side="left", padx=5, pady=5)
        # 删除选中自定义时间按钮
        delete_btn = ttk.Button(custom_frame, text="删除选中", command=self.delete_custom_time)
        delete_btn.pack(side="right", padx=5, pady=5)

    def on_listbox_click(self, event):
        if event.num == 3:  # 如果是右键点击
            self.context_menu.post(event.x_root, event.y_root)
        else:
            pass

    def on_listbox_double_click(self, event):
        self.start_list_countdown()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for t in self.custom_times:
            self.listbox.insert(tk.END, f"{t}秒")

    def save_custom_time(self):
        try:
            t = int(self.custom_time_var.get())
            if t <= 0:
                raise ValueError("倒计时时间必须为正整数")
            if t not in self.custom_times:
                self.custom_times.append(t)
                self.custom_times.sort()
                self.config_data["custom_times"] = self.custom_times
                save_config(self.config_data)
                self.update_listbox()
            else:
                messagebox.showwarning(VALUE_DUPLICATE, f"自定义时间 {t} 秒已经存在")
        except ValueError:
            messagebox.showerror(VALUE_ERROR, "请输入有效的正整数秒数")

    def delete_custom_time(self):
        try:
            selection = self.listbox.curselection()
            if not selection:
                messagebox.showerror(OPERATION_ERROR, "请选择一个要删除的自定义时间")
                return
            index = selection[0]
            t_str = self.listbox.get(index)
            t = int(t_str.replace("秒", ""))
            self.custom_times.remove(t)
            self.config_data["custom_times"] = self.custom_times
            save_config(self.config_data)
            self.update_listbox()
            messagebox.showinfo(OPERATION_SUCCESS, f"自定义时间 {t} 秒已删除")
        except Exception as e:
            messagebox.showerror(OPERATION_ERROR, f"删除失败: {e}")

    def start_input_countdown(self):
        try:
            t = int(self.custom_time_var.get())
            if t <= 0:
                raise ValueError("倒计时时间必须为正整数")
            self.start_countdown(t)
        except ValueError:
            messagebox.showerror(VALUE_ERROR, "请输入有效的正整数秒数")

    def start_list_countdown(self):
        try:
            selection = self.listbox.curselection()
            if selection:
                index = selection[0]
                t_str = self.listbox.get(index)
                t = int(t_str.replace("秒", ""))
                self.start_countdown(t)
            else:
                messagebox.showerror(OPERATION_ERROR, "请选择一个保存的自定义时间")
        except Exception as e:
            messagebox.showerror(OPERATION_ERROR, f"无法启动倒计时: {e}")

    def start_countdown(self, seconds):
        CountdownWindow(self, seconds)


class CountdownWindow(tk.Toplevel):
    def __init__(self, master, seconds):
        super().__init__(master)
        self.seconds = seconds
        self.init_time = self.seconds
        self.title(f"{self.init_time}秒倒计时")
        self.geometry("250x80")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.attributes("-toolwindow", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # 保存原始背景色
        self.original_bg = self.cget("bg")
        # 创建文本标签，居中显示
        self.label = ttk.Label(
            self,
            text=self.format_time(self.seconds),
            font=("Helvetica", 24),
            anchor="center",
            justify="center"
        )
        self.label.pack(expand=True, fill="both", pady=10)
        self.running = True
        self.after(1000, self.update_timer)

    @staticmethod
    def format_time(secs):
        hours = secs // 3600
        minutes = (secs % 3600) // 60
        seconds = secs % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_timer(self):
        if not self.running:
            return
        if self.seconds > 0:
            self.seconds -= 1
            self.label.config(text=self.format_time(self.seconds))
            self.after(1000, self.update_timer)
        else:
            self.label.config(text=f"{self.init_time}秒时间到！")
            # 倒计时结束后开始闪烁效果
            self.flash_effect(0)

    def flash_effect(self, count):
        # 声光闪烁
        if count < 100:
            try:
                winsound.Beep(2500, 15)
            except:
                pass
        new_bg = "red" if count % 2 == 0 else self.original_bg
        self.configure(bg=new_bg)
        self.label.configure(background=new_bg)
        self.after(300, lambda: self.flash_effect(count + 1))

    def on_close(self):
        self.running = False
        self.destroy()


if __name__ == "__main__":
    app = CountdownApp()
    app.mainloop()

