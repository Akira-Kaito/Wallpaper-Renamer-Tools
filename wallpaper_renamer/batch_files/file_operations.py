import json
import os
import time
import stat
import logging

# 常量定义
MAX_RETRIES = 3
SLEEP_TIME = 1

def get_json_files(directory):
    """
    获取指定目录下的所有 JSON 文件路径。

    :param directory: 要扫描的目录路径
    :return: JSON 文件路径列表
    """
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file)) #os.path.join(root, file) 会把 root 和 file 组合成一个完整的文件路径。
            else:
                logging.warning(f"警告: {file} 未找到JSON文件")
    return json_files


def get_json_files_and_titles(directory):
    """
    获取指定目录下的所有 JSON 文件路径和它们的 'title' 字段值。
    并返回
    """    
    json_files = get_json_files(directory)
    json_files_titles = []
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'title' in data:
                logging.info(f"成功读取: {file_path}，找到标题:{data['title']}")
                json_files_titles.append(data['title'])
            else:
                logging.warning(f"{file_path} 文件中没有 'title' 标签")
        except json.JSONDecodeError:
            logging.warning(f"{file_path} 不是有效的JSON文件")
        except UnicodeDecodeError:
            logging.warning(f"{file_path} 编码问题")
        except Exception as e:
            logging.error(f"处理 {file_path} 时出错: {str(e)}")
    return json_files_titles


def find_json_files(directory):
    """
    扫描指定目录下的所有JSON文件，并读取其中的 'title' 字段。

    :param directory: 要扫描的目录路径
    """
    json_files = get_json_files(directory)
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'title' in data:
                logging.info(f"成功读取: {file_path}，找到标题:{data['title']}")
            else:
                logging.warning(f"{file_path} 文件中没有 'title' 标签")
        except json.JSONDecodeError:
            logging.warning(f"{file_path} 不是有效的JSON文件")
        except UnicodeDecodeError:
            logging.warning(f"{file_path} 编码问题")
        except Exception as e:
            logging.error(f"处理 {file_path} 时出错: {str(e)}")


def rename_folder(old_name, new_name):
    """
    重命名文件夹。

    :param old_name: 旧文件夹名称
    :param new_name: 新文件夹名称
    """
    try:
        os.rename(old_name, new_name)
        logging.info(f"文件夹已从 '{old_name}' 重命名为 '{new_name}'")
    except FileNotFoundError:
        logging.error(f"文件夹 '{old_name}' 不存在")
    except FileExistsError:
        logging.error(f"文件夹 '{new_name}' 已存在")

def rename_folder_based_on_json(directory):
    """
    扫描目录下的所有JSON文件，并将它们所在的文件夹重命名为JSON中的 'title' 值。
    增加权限处理和重试机制。

    :param directory: 要扫描的目录路径
    """
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if 'title' in data:
                        current_dir = root
                        parent_dir = os.path.dirname(current_dir)
                        new_dir_name = data['title']
                        new_dir_path = os.path.join(parent_dir, new_dir_name)
                        if current_dir != new_dir_path:
                            for attempt in range(MAX_RETRIES):
                                try:
                                    os.chmod(current_dir, stat.S_IWRITE)
                                    os.rename(current_dir, new_dir_path)
                                    logging.info(f"成功将文件夹 '{current_dir}' 重命名为 '{new_dir_path}'")
                                    break
                                except PermissionError:
                                    if attempt == MAX_RETRIES - 1:
                                        logging.error(f"错误: 无法重命名 '{current_dir}' (多次重试失败)")
                                    else:
                                        time.sleep(SLEEP_TIME)
                                except FileExistsError:
                                    logging.warning(f"警告: 目标文件夹 '{new_dir_path}' 已存在，跳过重命名")
                                    break
                        else:
                            logging.info(f"提示: 文件夹名称已经是 '{new_dir_name}'，无需修改")
                    else:
                        logging.warning(f"警告: {file_path} 中没有 'title' 字段")
                except json.JSONDecodeError:
                    logging.warning(f"警告: {file_path} 不是有效的JSON文件")
                except UnicodeDecodeError:
                    logging.warning(f"警告: {file_path} 编码问题")
                except Exception as e:
                    logging.error(f"处理 {file_path} 时出错: {str(e)}")

#先找出主要思路是先找出目录下所有 JSON 文件，然后展示这些文件列表让用户选择，最后对选中的文件所在文件夹进行重命名。
def rename_selected_folders(selected_files):
    """
    对选中的 JSON 文件所在文件夹进行重命名。

    :param selected_files: 选中的 JSON 文件路径列表
    """
    for file_path in selected_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'title' in data:
                current_dir = os.path.dirname(file_path)
                parent_dir = os.path.dirname(current_dir)
                new_dir_name = data['title']
                new_dir_path = os.path.join(parent_dir, new_dir_name)
                if current_dir != new_dir_path:
                    for attempt in range(MAX_RETRIES):
                        try:
                            os.chmod(current_dir, stat.S_IWRITE)
                            os.rename(current_dir, new_dir_path)
                            logging.info(f"成功将文件夹 '{current_dir}' 重命名为 '{new_dir_path}'")
                            break
                        except PermissionError:
                            if attempt == MAX_RETRIES - 1:
                                logging.error(f"错误: 无法重命名 '{current_dir}' (多次重试失败)")
                            else:
                                time.sleep(SLEEP_TIME)
                        except FileExistsError:
                            logging.warning(f"警告: 目标文件夹 '{new_dir_path}' 已存在，跳过重命名")
                            break
                else:
                    logging.info(f"提示: 文件夹名称已经是 '{new_dir_name}'，无需修改")
            else:
                logging.warning(f"警告: {file_path} 中没有 'title' 字段")
        except json.JSONDecodeError:
            logging.warning(f"警告: {file_path} 不是有效的JSON文件")
        except UnicodeDecodeError:
            logging.warning(f"警告: {file_path} 编码问题")
        except Exception as e:
            logging.error(f"处理 {file_path} 时出错: {str(e)}")

def focus_window_stay_on_top(window):
    """
    使窗口置顶并保持在最前面。
    """
    window.bind("<FocusIn>", lambda event: window.lift())