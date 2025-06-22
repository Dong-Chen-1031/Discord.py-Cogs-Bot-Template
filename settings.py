import os
import sys
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# Discord 機器人設定檔案

# Discord 機器人 Token
DISCORD_BOT_TOKEN = str(os.getenv("DISCORD_BOT_TOKEN"))

AUTO_RELOAD = False # 是否自動重新載入 Cogs

# 開發者指令的開發者ID
DEV_ID = [
    123456789012345678,  # 替換為你的 Discord 用戶 ID
    987654321098765432   # 可以添加多個開發者 ID
]

# 檢查 Token 是否存在
if DISCORD_BOT_TOKEN is None:
    print("錯誤: 找不到 DISCORD_BOT_TOKEN 環境變數")
    print("請確認 .env 檔案中已正確設置 DISCORD_BOT_TOKEN")
    print("格式應為: DISCORD_BOT_TOKEN = \"你的Token\"")
    sys.exit(1)

# 機器人開發者指令前綴
PREFIX = ".dev "