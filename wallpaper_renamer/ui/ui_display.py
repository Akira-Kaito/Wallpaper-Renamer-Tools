import json
import logging
#import select
#from sqlite3 import PARSE_DECLTYPES
import tkinter as tk
from tkinter import messagebox, filedialog
#from unittest import result
#from file_operations import find_json_files, get_json_files_and_titles, rename_folder_based_on_json, get_json_files, focus_window_stay_on_top
from ..batch_files.file_operations import *
from ..batch_files.user_interaction import *
import customtkinter as ctk
import os
import stat
import time
import sys
import shutil
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 程序作者
AUTHOR_NAME = "焉晓驰(AKira)"
# B站主页链接
BILIBILI_LINK = "https://space.bilibili.com/3493274255887085"
#控件间距
PADY = 10
#爱发电主页
AFDIAN_LINK = "https://afdian.com/a/bingzhulongyan"

# 设置主题和外观模式
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# 定义一个设置图标的函数，考虑打包后的情况

def set_window_icon(window):
    try:
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                # 使用打包工具的临时资源目录
                base_path = sys._MEIPASS
            else:
                # 使用可执行文件所在目录（Nuitka打包的情况）
                base_path = os.path.dirname(sys.executable)
            
            # Nuitka打包后图标可能在多个可能的位置
            possible_icon_paths = [
                  os.path.join(base_path, 'wallpaper_renamer.ico'),
                  os.path.join(base_path, '..', 'wallpaper_renamer.ico')  # 上一级目录
              ]
        else:
            # 开发环境下使用当前脚本所在目录
            # 开发环境，获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.dirname(os.path.dirname(current_dir))
            possible_icon_paths = [
                os.path.join(base_path, 'wallpaper_renamer.ico'),
                os.path.join(base_path, 'ui', 'wallpaper_renamer.ico')
            ]

        # 尝试所有可能的路径
        icon_path = None
        for path in possible_icon_paths:
            path = os.path.normpath(path)
            if os.path.exists(path):
                icon_path = path
                break

        if icon_path is None:
            # 打印所有尝试过的路径以便调试
            print("无法找到图标文件，尝试了以下路径:")
            for path in possible_icon_paths:
                print(f"- {os.path.normpath(path)}")
            messagebox.showerror("图标错误", "无法找到图标文件")
            return

        print(f"使用图标路径: {icon_path}")
        window.iconbitmap(default=icon_path)
        if sys.platform.startswith("win"):
            window.after(200, lambda: window.iconbitmap(icon_path))
            
    except Exception as e:
        #print(f"为窗口设置图标时出错: {e}")
        #messagebox.showerror("错误", f"设置窗口图标时出错: {e}")
        pass


def handle_json_error(result_label, error_message):
    logging.error(error_message)
    result_label.configure(text=error_message)

def read_json_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise
    except json.JSONDecodeError:
        raise
    except Exception as e:
        raise

class WallpaperRenamerApp:
    def __init__(self, root):
        self.root = root
        set_window_icon(self.root)
        self.root.title("壁纸重命名工具")
        self.root.geometry("350x350")
        self.root.resizable(False, False)

        focus_window_stay_on_top(self.root)
        
        # 主界面布局
        self.create_widgets()

    def create_widgets(self):
        # 模式选择提示
        mode_label = ctk.CTkLabel(self.root, text="选择模式", font=("SimHei", 14))
        mode_label.pack(pady=PADY)

        # 模式1按钮
        self.mode1_button = ctk.CTkButton(
            self.root,
            text="1. 扫描指定目录下的单个 json 文件",
            font=("SimHei", 10),
            width=200,
            command=self.scan_single_json
        )
        #self.mode1_button.pack(pady=PADY)

        #查找wallpaper安装路径，并且进行备份的按钮
        self.search_wallpaper_path_button = ctk.CTkButton(
            self.root,
            text="壁纸备份",
            font=("SimHei", 10),
            width=100,
            command=self.search_wallpaper_path_and_backup
        )
        self.search_wallpaper_path_button.pack(pady=PADY)

        # 模式2按钮
        self.mode2_button = ctk.CTkButton(
            self.root,
            text="读取",
            font=("SimHei", 10),
            width=100,
            command=self.scan_all_titles
        )
        self.mode2_button.pack(pady=PADY)

        # 目录输入框
        self.directory_input = ctk.CTkEntry(self.root, font=("SimHei", 12), width=300)
        self.directory_input.pack(pady=PADY)

        # 浏览按钮
        browse_button = ctk.CTkButton(
            self.root,
            text="浏览",
            font=("SimHei", 10),
            width=100,
            command=self.browse_directory
        )
        browse_button.pack(pady=PADY)

        
        # 设置按钮
        settings_button = ctk.CTkButton(
            self.root,
            text="软件声明",
            font= ("SimHei", 10),
            width=100,
            command=self.show_disclaimer
        )
        settings_button.pack(pady=PADY)

        # 结果显示标签
        self.result_label = ctk.CTkLabel(
            self.root, 
            text="", 
            font=("SimHei", 12), 
            wraplength=400
        )
        self.result_label.pack(pady=PADY)

    #主要功能是让用户通过图形界面选择一个目录，并将所选目录的路径填充到应用程序的目录输入框中
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_input.delete(0, tk.END)
            self.directory_input.insert(0, directory)

    def research_json(self):
        path = self.directory_input.get().strip()
        if not path:
            self.result_label.configure(text="请输入有效路径")
            return
        try:
            data = read_json_file(path)
            if 'title' in data:
                logging.info(f"找到标题: {data['title']}")
                self.result_label.configure(text=f"找到标题: {data['title']}")
            else:
                logging.warning("文件中没有 'title' 标签")
                self.result_label.configure(text="文件中没有 'title' 标签")
        except FileNotFoundError:
            handle_json_error(self.result_label, "文件未找到，请检查路径")
        except json.JSONDecodeError:
            handle_json_error(self.result_label, "文件不是有效的 JSON 格式")
        except Exception as e:
            handle_json_error(self.result_label, f"发生错误: {str(e)}")

    def scan_all_titles(self):
        directory = self.directory_input.get().strip()
        if not directory:
            self.result_label.configure(text="请输入有效目录")
            return
        # 查找 JSON 文件
        json_files = find_json_files(directory) 
        # 弹出对话框询问是否重命名
        response = messagebox.askyesno("重命名选择", "是否需要重命名？")
        if response:
            # 调用重命名模式选择方法
            self.choose_rename_mode(directory)

    #查找wallpaper安装路径，并且进行备份的窗口
    def search_wallpaper_path_and_backup(self):
        class SearchAndBackupDialog(ctk.CTkToplevel):
            def __init__(self, root, master=None, **kwargs):
                super().__init__(master, **kwargs)
                self.root = root
                self.title("查找 Wallpaper 安装路径并备份")
                self.result = None
                focus_window_stay_on_top(self)
                #self.body(self)
                self.buttonbox()
                #设置窗口大小不可更改
                self.minsize(420, 400)
                self.maxsize(420, 400)
                # 延迟设置图标
                set_window_icon(self)
                # 自动查找steam安装的wallpaper路径，若找不到则让用户手动输入
                #on_browse_button_click(self)
            """def body(self, master):
                self.label = ctk.CTkLabel(
                    master,
                    text="查找 Wallpaper 安装路径并备份", 
                    font=("SimHei", 20)
                )
                self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
            """
            

            def buttonbox(self):
                button_frame = ctk.CTkFrame(self)
                button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
                
                btn1 = ctk.CTkButton(
                    button_frame,
                    text="自动查找wallpaper路径", 
                    width=150,
                    command=lambda: self.on_browse_button_click(),
                    font=("SimHei", 12)
                )
                btn1.grid(row=1, column=1, padx=10, pady=10)

                label1 = ctk.CTkLabel(
                    self,
                    text="wallpaper 安装路径:",
                    font=("SimHei", 12)
                )
                label1.grid(row=2, column=0, padx=10, pady=10)
                # 目录输入框
                self.directory_input1 = ctk.CTkEntry(self, font=("SimHei", 12), width=300)
                self.directory_input1.grid(row=3,column=0, padx=5, pady=5)

                browse_button1 = ctk.CTkButton(
                    self,
                    text="浏览",
                    font=("SimHei", 10),
                    width=100,
                    command=lambda: self.browse_directory(self.directory_input1)
                )
                browse_button1.grid(row=3, column=1, padx=5, pady=5)

                label2 = ctk.CTkLabel(
                    self,
                    text="备份路径:",
                    font=("SimHei", 12)
                )
                label2.grid(row=4, column=0, padx=10, pady=10)
            
                # 目录输入框
                self.directory_input2 = ctk.CTkEntry(self, font=("SimHei", 12), width=300)
                self.directory_input2.grid(row=5,column=0, padx=5, pady=5)

                # 浏览按钮
                browse_button2 = ctk.CTkButton(
                    self,
                    text="浏览",
                    font=("SimHei", 10),
                    width=100,
                    command=lambda: self.browse_directory(self.directory_input2)
                )
                browse_button2.grid(row=5, column=1, padx=5, pady=5)

                # 开始备份按钮
                backup_button = ctk.CTkButton(
                    self,
                    text="开始备份",
                    font=("SimHei", 10),
                    width=100,
                    command=self.backup_files
                )
                backup_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

                # 移除进度条和进度标签相关代码

            class ProgressDialog(ctk.CTkToplevel):
                def __init__(self, master=None, **kwargs):
                    super().__init__(master, **kwargs)
                    self.title("备份进度")
                    self.geometry("300x100")
                    self.resizable(False, False)
                    self.progress_bar = ctk.CTkProgressBar(self, width=250)
                    self.progress_bar.pack(pady=20)
                    self.progress_bar.set(0)
                    self.progress_label = ctk.CTkLabel(self, text="0%", font=("SimHei", 12))
                    self.progress_label.pack()

                def update_progress(self, processed_files, total_files):
                    progress = processed_files / total_files
                    self.progress_bar.set(progress)
                    self.progress_label.configure(text=f"{int(progress*100)}%")
                    self.update_idletasks()

            def backup_files(self):
                try:
                    source_dir = self.directory_input1.get().strip()
                    dest_dir = self.directory_input2.get().strip()

                    if not source_dir or not dest_dir:
                        messagebox.showerror("错误", "请输入有效的源路径和目标路径")
                        return

                    # 弹出确认对话框
                    confirm = messagebox.askyesno("确认备份", "您确定要开始备份吗？")
                    if not confirm:
                        return

                    # 显示进度条弹窗
                    progress_dialog = self.ProgressDialog(self)

                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)

                    # 获取所有文件的总数
                    total_files = sum([len(files) for _, _, files in os.walk(source_dir)])
                    processed_files = 0

                    for root, dirs, files in os.walk(source_dir):
                        for file in files:
                            src_file = os.path.join(root, file)
                            dest_file = os.path.join(dest_dir, os.path.relpath(src_file, source_dir))
                            dest_path = os.path.dirname(dest_file)

                            if not os.path.exists(dest_path):
                                os.makedirs(dest_path)

                            shutil.copy2(src_file, dest_file)

                            # 更新进度
                            processed_files += 1
                            progress_dialog.update_progress(processed_files, total_files)

                    # 关闭进度条弹窗
                    progress_dialog.destroy()

                    messagebox.showinfo("成功", "备份完成")
                except Exception as e:
                    print(f"backup_files 方法出错: {e}")
                    # 关闭进度条弹窗（如果出现错误）
                    if 'progress_dialog' in locals():
                        progress_dialog.destroy()
                    messagebox.showerror("错误", f"备份过程中出现错误: {str(e)}")

            #给用户输入要备份的路径
            def browse_directory(self, entry, *args, **kwargs):
                directory = filedialog.askdirectory()
                if directory:
                    entry.delete(0, tk.END)
                    entry.insert(0, directory)

            def backup_files(self):
                source_dir = self.directory_input1.get().strip()
                dest_dir = self.directory_input2.get().strip()

                if not source_dir or not dest_dir:
                    messagebox.showerror("错误", "请输入有效的源路径和目标路径")
                    return

                # 弹出确认对话框
                confirm = messagebox.askyesno("确认备份", "您确定要开始备份吗？")
                if not confirm:
                    return

                try:
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)

                    for root, dirs, files in os.walk(source_dir):
                        for file in files:
                            src_file = os.path.join(root, file)
                            dest_file = os.path.join(dest_dir, os.path.relpath(src_file, source_dir))
                            dest_path = os.path.dirname(dest_file)

                            if not os.path.exists(dest_path):
                                os.makedirs(dest_path)

                            shutil.copy2(src_file, dest_file)

                    messagebox.showinfo("成功", "备份完成")
                except Exception as e:
                    messagebox.showerror("错误", f"备份过程中出现错误: {str(e)}")


            # 自动查找steam安装的wallpaper路径，若找不到则让用户手动输入
            def on_browse_button_click(self):
                try:
                    wallpaper_path = get_wallpaper_path_in_steam()
                    if wallpaper_path:
                        self.directory_input1.delete(0, tk.END)
                        self.directory_input1.insert(0, wallpaper_path)
                    else:
                        self.directory_input1.delete(0, tk.END)
                        messagebox.showinfo("提示", "自动查找壁纸路径失败，请手动输入路径。")
                except Exception as e:
                    print(f"on_browse_button_click 方法出错: {e}")
                    messagebox.showerror("错误", f"自动查找壁纸路径时出错: {e}")

            def backup_files(self):
                try:
                    source_dir = self.directory_input1.get().strip()
                    dest_dir = self.directory_input2.get().strip()

                    if not source_dir or not dest_dir:
                        messagebox.showerror("错误", "请输入有效的源路径和目标路径")
                        return

                    # 弹出确认对话框
                    confirm = messagebox.askyesno("确认备份", "您确定要开始备份吗？")
                    if not confirm:
                        return

                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)

                    for root, dirs, files in os.walk(source_dir):
                        for file in files:
                            src_file = os.path.join(root, file)
                            dest_file = os.path.join(dest_dir, os.path.relpath(src_file, source_dir))
                            dest_path = os.path.dirname(dest_file)

                            if not os.path.exists(dest_path):
                                os.makedirs(dest_path)

                            shutil.copy2(src_file, dest_file)

                    messagebox.showinfo("成功", "备份完成")
                except Exception as e:
                    print(f"backup_files 方法出错: {e}")
                    messagebox.showerror("错误", f"备份过程中出现错误: {str(e)}")


            # 自动查找steam安装的wallpaper路径，若找不到则让用户手动输入
            def on_browse_button_click(self):
                self.auto_browse_directory()
                wallpaper_path = get_wallpaper_path_in_steam()
                if wallpaper_path:
                    # 可以将路径填充到输入框中，这里假设填充到 directory_input1
                    self.directory_input1.delete(0, tk.END)
                    self.directory_input1.insert(0, wallpaper_path)
                else:
                    # 自动查找失败，清空输入框，让用户手动输入
                    self.directory_input1.delete(0, tk.END)
                    messagebox.showinfo("提示", "自动查找壁纸路径失败，请手动输入路径。")


            #主要功能是让用户通过图形界面选择一个目录，并将所选目录的路径填充到应用程序的目录输入框中
            def auto_browse_directory(self):
                directory = filedialog.askdirectory()
                if directory:
                    self.directory_input1.delete(0, tk.END)
                    self.directory_input1.insert(0, directory)
        
        #实例化窗口（弹出窗口）
        dialog = SearchAndBackupDialog(self.root)
        self.root.wait_window(dialog)
        set_window_icon(dialog)

            

    
    #模式选择窗口
    def choose_rename_mode(self, directory):
        class RenameDialog(ctk.CTkToplevel):
            def __init__(self, root, master=None, **kwargs):
                super().__init__(master, **kwargs)
                self.root = root
                self.title("选择重命名模式")
                self.result = None
                focus_window_stay_on_top(self)
                self.body(self)
                self.buttonbox()
                self.minsize(300, 100)
                self.maxsize(300, 100)
                # 调用设置图标的函数
                set_window_icon(self)

                
            def body(self, master):
                ctk.CTkLabel(master, text="选择重命名模式：\n1. 重命名所有文件\n2. 选择部分文件重命名", font=("SimHei", 12)).pack(pady=10)

            def buttonbox(self):
                button_frame = ctk.CTkFrame(self)
                button_frame.pack()
                btn1 = ctk.CTkButton(button_frame, text="1", width=100, command=lambda: self.on_button(1), font=("SimHei", 12))
                btn1.pack(side=ctk.LEFT, padx=5, pady=5)
                btn2 = ctk.CTkButton(button_frame, text="2", width=100, command=lambda: self.on_button(2), font=("SimHei", 12))
                btn2.pack(side=ctk.LEFT, padx=5, pady=5)

            def on_button(self, value):
                self.result = value
                self.destroy()

        dialog = RenameDialog(self.root)
        self.root.wait_window(dialog)
        #set_window_icon(dialog)
        if dialog.result == 1:
            rename_folder_based_on_json(directory)
            self.result_label.configure(text="所有文件重命名完成")
        elif dialog.result == 2:
            json_files = get_json_files(directory)
            json_files_titles = get_json_files_and_titles(directory)
            if not json_files:
                self.result_label.configure(text="未找到 JSON 文件，无法进行选择重命名。")
                return

            select_window = ctk.CTkToplevel(self.root)
            set_window_icon(select_window)
            select_window.title("选择文件重命名")
            select_window.geometry("600x600")
            focus_window_stay_on_top(select_window)

            result_textbox = ctk.CTkTextbox(select_window, font=("SimHei", 12), width=580, height=200)
            result_textbox.pack(pady=10)

            error_messages = []

            for file_path in json_files:
                try:
                    data = read_json_file(file_path)
                    if 'title' in data:
                        logging.info(f"找到标题:{data['title']}")
                    else:
                        error_msg = f"{file_path} 文件中没有 'title' 标签"
                        error_messages.append(error_msg)
                        logging.warning(error_msg)
                except FileNotFoundError:
                    error_msg = f"{file_path} 文件未找到"
                    error_messages.append(error_msg)
                    logging.error(error_msg)
                except json.JSONDecodeError:
                    error_msg = f"{file_path} 不是有效的JSON文件"
                    error_messages.append(error_msg)
                    logging.error(error_msg)
                except UnicodeDecodeError:
                    error_msg = f"{file_path} 编码问题"
                    error_messages.append(error_msg)
                    logging.error(error_msg)
                except Exception as e:
                    error_msg = f"处理 {file_path} 时出错: {str(e)}"
                    error_messages.append(error_msg)
                    logging.error(error_msg)

            # 若有错误信息，统一显示
            if error_messages:
                error_text = "\n".join(error_messages)
                result_textbox.insert("end", error_text + "\n")
                messagebox.showerror("处理文件时出错", error_text)

            # 创建一个可滚动的框架
            scrollable_frame = ctk.CTkScrollableFrame(select_window, width=580)
            scrollable_frame.pack(pady=10)

            # 为每个文件名在可滚动框架内创建复选框
            checkbox_vars_list = []
            for name in json_files_titles: 
                var = ctk.IntVar()
                checkbox = ctk.CTkCheckBox(scrollable_frame, text=name, variable=var)
                checkbox.pack(pady=5, anchor="w")
                checkbox_vars_list.append(var)

            def rename_selected_files():
                for index, file_path in enumerate(json_files):
                    if checkbox_vars_list[index].get() == 1:
                        try:
                            data = read_json_file(file_path)
                            if 'title' in data:
                                current_dir = os.path.dirname(file_path)
                                parent_dir = os.path.dirname(current_dir)
                                new_dir_name = data['title']
                                new_dir_path = os.path.join(parent_dir, new_dir_name)
                                if current_dir != new_dir_path:
                                    for attempt in range(3):
                                        try:
                                            os.chmod(current_dir, stat.S_IWRITE)
                                            os.rename(current_dir, new_dir_path)
                                            logging.info(f"成功将文件夹 '{current_dir}' 重命名为 '{new_dir_path}'")
                                            result_textbox.insert("end", f"成功将文件夹 '{current_dir}' 重命名为 '{new_dir_path}'\n")
                                            break
                                        except PermissionError:
                                            if attempt == 2:
                                                logging.error(f"错误: 无法重命名 '{current_dir}' (多次重试失败)")
                                                result_textbox.insert("end", f"错误: 无法重命名 '{current_dir}' (多次重试失败)\n")
                                            else:
                                                time.sleep(1)
                                        except FileExistsError:
                                            logging.warning(f"警告: 目标文件夹 '{new_dir_path}' 已存在，跳过重命名")
                                            result_textbox.insert("end", f"警告: 目标文件夹 '{new_dir_path}' 已存在，跳过重命名\n")
                                            break
                                else:
                                    logging.info(f"提示: 文件夹名称已经是 '{new_dir_name}'，无需修改")
                                    result_textbox.insert("end", f"提示: 文件夹名称已经是 '{new_dir_name}'，无需修改\n")
                            else:
                                logging.warning(f"警告: {file_path} 中没有 'title' 字段")
                                result_textbox.insert("end", f"警告: {file_path} 中没有 'title' 字段\n")
                        except FileNotFoundError:
                            logging.warning(f"警告: {file_path} 文件未找到")
                            result_textbox.insert("end", f"警告: {file_path} 文件未找到\n")
                        except json.JSONDecodeError:
                            logging.warning(f"警告: {file_path} 不是有效的JSON文件")
                            result_textbox.insert("end", f"警告: {file_path} 不是有效的JSON文件\n")
                        except UnicodeDecodeError:
                            logging.warning(f"警告: {file_path} 编码问题")
                            result_textbox.insert("end", f"警告: {file_path} 编码问题\n")
                        except Exception as e:
                            logging.error(f"处理 {file_path} 时出错: {str(e)}")
                            result_textbox.insert("end", f"处理 {file_path} 时出错: {str(e)}\n")

            # 创建按钮来获取选中的文件
            button = ctk.CTkButton(select_window, text="获取选中文件", command=rename_selected_files)
            button.pack(pady=10)

    def scan_single_json(self):
        self.research_json()

    def show_disclaimer(self):
        # 创建声明窗口
        disclaimer_window = ctk.CTkToplevel(self.root)
        disclaimer_window.title("软件声明")
        disclaimer_window.geometry("600x400")
        disclaimer_window.resizable(True, True)
        disclaimer_window.transient(self.root)
        disclaimer_window.grab_set()
        set_window_icon(disclaimer_window)

        # 创建滚动条
        scrollbar = ctk.CTkScrollbar(disclaimer_window)
        scrollbar.pack(side="right", fill="y")

        # 创建文本框并关联滚动条
        text_widget = ctk.CTkTextbox(
            disclaimer_window,
            yscrollcommand=scrollbar.set,
            wrap="word",
            font= ("SimHei", 12)
        )
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        scrollbar.configure(command=text_widget.yview)

        # 读取并显示声明内容
        try:
            # 获取声明文件路径
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                base_path = os.path.dirname(os.path.dirname(current_dir))
            disclaimer_path = os.path.join(base_path, 'wallpaper_renamer', 'ui', 'disclaimer.txt')
            
            with open(disclaimer_path, 'r', encoding='utf-8') as f:
                disclaimer_content = f.read()
            text_widget.insert("1.0", disclaimer_content)
            text_widget.configure(state="disabled")  # 设置为只读
        except Exception as e:
            text_widget.insert("1.0", f"无法加载软件声明: {str(e)}")
            text_widget.configure(state="disabled")

    def open_settings_window(self):
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("390x300")
        settings_window.minsize(390, 250)
        settings_window.maxsize(390, 250)
        # 调用设置图标的函数
        set_window_icon(settings_window)

        # 创建关于部分
        about_frame = ctk.CTkFrame(settings_window)
        about_frame.pack(pady=20, padx=20, fill="both", expand=True)

        author_label = ctk.CTkLabel(about_frame, text=f"程序作者: {AUTHOR_NAME}", font=("SimHei", 12))
        author_label.pack(pady=5)

        bilibili_label = ctk.CTkLabel(about_frame, text=f"B 站主页: {BILIBILI_LINK}", font=("SimHei", 12), cursor="hand2")
        # 定义鼠标进入事件处理函数
        def on_enter(event):
            bilibili_label.configure(text_color="blue")
        # 定义鼠标离开事件处理函数
        def on_leave(event):
            bilibili_label.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        bilibili_label.bind("<Enter>", on_enter)
        bilibili_label.bind("<Leave>", on_leave)
        bilibili_label.pack(pady=5)
        bilibili_label.bind("<Button-1>", lambda e: self.open_bilibili_link())

        afdian_label = ctk.CTkLabel(about_frame, text=f"爱发电主页: {AFDIAN_LINK}", font=("SimHei", 12), cursor="hand2")
        # 定义鼠标进入事件处理函数
        def on_enter(event):
            afdian_label.configure(text_color="blue")
        # 定义鼠标离开事件处理函数
        def on_leave(event):
            afdian_label.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        afdian_label.bind("<Enter>", on_enter)
        afdian_label.bind("<Leave>", on_leave)
        afdian_label.pack(pady=5)
        afdian_label.bind("<Button-1>", lambda e: self.open_afdian_link())

        # 添加软件声明链接
        disclaimer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'disclaimer.txt')
        disclaimer_label = ctk.CTkLabel(about_frame, text="软件声明", font=("SimHei", 12), cursor="hand2")
        
        def on_disclaimer_enter(event):
            disclaimer_label.configure(text_color="blue")
        def on_disclaimer_leave(event):
            disclaimer_label.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        def open_disclaimer():
            import subprocess
            try:
                subprocess.Popen(['notepad.exe', disclaimer_path])
            except Exception as e:
                messagebox.showerror("错误", f"打开软件声明文件时出错: {e},您可以在软件目录的ui文件夹中查看软件声明")
        disclaimer_label.bind("<Enter>", on_disclaimer_enter)
        disclaimer_label.bind("<Leave>", on_disclaimer_leave)
        disclaimer_label.bind("<Button-1>", lambda e: open_disclaimer())
        disclaimer_label.pack(pady=20)

    #打开B站主页
    def open_bilibili_link(self):
        import webbrowser
        webbrowser.open(BILIBILI_LINK)

    #打开爱发电主页
    def open_afdian_link(self):
        import webbrowser
        webbrowser.open(AFDIAN_LINK)