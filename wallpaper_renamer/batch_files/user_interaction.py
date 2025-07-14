import os
import logging

def get_user_choice(prompt, valid_choices):
    """
    获取用户的有效选择。若用户输入无效，会提示用户重新输入。

    :param prompt: 提示信息
    :param valid_choices: 有效的选择列表
    :return: 用户的有效选择
    """
    while True:
        user_input = input(prompt).strip()
        try:
            choice = int(user_input)
            if choice in valid_choices:
                return choice
            logging.error(f"错误: 请输入 {', '.join(map(str, valid_choices))} 中的一个")
        except ValueError:
            logging.error(f"错误: 请输入数字 {', '.join(map(str, valid_choices))}")
        logging.info("请重新输入...\n")

def get_valid_directory():
    """
    获取用户输入的有效目录路径。

    :return: 有效的目录路径
    """
    while True:
        path = input("请输入要扫描的路径: ").strip()
        path = path.strip('"').strip("'")
        if not path:
            logging.error("错误: 请输入有效路径")
            continue
        try:
            abs_path = os.path.abspath(path)
        except Exception:
            logging.error(f"错误: 路径 '{path}' 无效")
            continue
        if not os.path.exists(abs_path):
            logging.error(f"错误: 路径 '{abs_path}' 不存在")
            continue
        if not os.path.isdir(abs_path):
            logging.error(f"错误: '{abs_path}' 不是目录")
            continue
        return abs_path