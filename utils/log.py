import traceback
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
import logging
import os
import datetime
from typing import Optional
from discord import Interaction, Message
from discord.ext.commands import Context

# 設定Rich主題
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red"
})
console = Console(theme=custom_theme)

# 設定日誌系統
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

current_time = datetime.datetime.now().strftime("%Y-%m-%d")
log_file = f"{log_dir}/{current_time}.log"

# 設定logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 設定Rich handler (控制台輸出)
rich_handler = RichHandler(console=console, rich_tracebacks=True, tracebacks_show_locals=False)
rich_handler.setLevel(logging.INFO)


# 設定File handler (檔案輸出)
file_handler = logging.FileHandler(filename=log_file, encoding="utf-8", mode="a")
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_format)

# 添加handlers
logger.addHandler(rich_handler)
logger.addHandler(file_handler)


def log(to_log: (str|Interaction|Message|Context|None)=None, *args, **kwargs):
    """快速打個 log"""
    try:
        msg = None
        user = None
        args_list = list(args)
        if isinstance(to_log, str):
            args_list.append(to_log)
        elif isinstance(to_log, Interaction):
            user = to_log.user.name
        elif isinstance(to_log, Message):
            user = to_log.author.name
        elif isinstance(to_log, Context):
            user = to_log.author.name

        # 取得當前函數的堆疊資訊
        caller = traceback.extract_stack()[-2]
        # 倒數第二個是呼叫者 (倒數第一個是當前函數)
        short_filename = os.path.basename(caller.filename)
        
        end_msg = f"函式: {caller.name} 檔案: {short_filename} 第 {caller.lineno} 行呼叫"
        if any([user, args_list, kwargs]):
            end_msg += "\n"
        if user:
            end_msg += f" Discord 使用者: {user}"
        if kwargs:
            for key, value in kwargs.items():
                end_msg += f" {key}: {value}"
        if args_list:
            end_msg += f" 詳細資訊: {args_list}"
        logging.info(end_msg)
    except Exception as e:
        logging.error(f"Log 錯誤: {e}")
        logging.error(traceback.format_exc())