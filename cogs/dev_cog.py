import logging
import os
import sys
import time
import discord
from discord.ext import commands
from discord import app_commands, Interaction
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils import ui
from utils.log import log

import settings


async def reload_cogs(cogs: list|str, bot:commands.Bot):
    if isinstance(cogs, str):
        cogs = [cogs]
    for cog in cogs:
        try:
            # logging.info(f"正在重新載入 {cog}...")
            await bot.reload_extension(f"cogs.{cog}")
            # logging.info(f"已成功重新載入 {cog}。")
        
        except Exception as e:
            logging.warning(f"Cogs 重新載入失敗: {e}")
            raise e
        
def get_all_cogs():
        cogs =  [filename[:-3] for filename in os.listdir("./cogs") if filename.endswith(".py")]
        # cogs.append(__name__.split(".")[-1])
        return cogs

def get_reload_all_view():
    all_cogs = ["all"]
    all_cogs.extend(get_all_cogs())
    return ReloadView(cogs=all_cogs)

class ReloadButton(discord.ui.Button):
    def __init__(self, cog:str, all_cogs:list[str]|None=None, disable:bool=False):
        super().__init__(label=cog, style=discord.ButtonStyle.primary, disabled=disable, custom_id=f"reload_{cog}_btn")
        self.cog = cog
        self.all_cogs = all_cogs
        if all_cogs is None:
            all_cogs = [cog]
        

    async def callback(self, interaction: discord.Interaction):
        # await interaction.response.edit_message(view=ReloadView(self.all_cogs, disable=self.cog))
        log(interaction, reload_button = self.cog)
        await interaction.response.defer(thinking=True, ephemeral=True)
        if interaction.user.id not in settings.DEV_ID:
            await interaction.response.send_message("你沒有權限使用此按鈕", ephemeral=True)
            return
        try:
            if self.cog == "all":
                cogs = get_all_cogs()
            else:
                cogs = [self.cog]
            await reload_cogs(cogs, interaction.client) # type: ignore
            delete_after = 5
            embed = ui.dev_embed(f"已成功重新載入 `{'`, `'.join(cogs)}`。 共重新載入 {len(cogs)} 項內容。")
            logging.info(f"已成功重新載入 `{'`, `'.join(cogs)}`。 共重新載入 {len(cogs)} 項內容。")
        except Exception as e:
            embed = ui.dev_embed(f"**重新載入失敗\n```cmd\n{e}```**", color = discord.Color.red())
            logging.warning(f"Cogs 重新載入失敗: {e}")
            delete_after = None
        finally:
            await interaction.edit_original_response(embed=embed, view=get_reload_all_view())

class ReloadView(discord.ui.View):
    def __init__(self, cogs:list[str], disable:list[str]|str|None=None):
        super().__init__(timeout=None)
        if disable is None:
            disable = []
        if isinstance(disable, str):
            if disable == "all":
                disable = cogs
            else:
                disable = [disable]
        if isinstance(cogs, str):
            cogs = [cogs]
        for cog in cogs:
            self.add_item(ReloadButton(cog, disable=(cog in disable), all_cogs=cogs))
        self.cogs = cogs
    

class DevCog(commands.Cog):
    def __init__(self, bot):
        self.bot:commands.Bot = bot
        self.file_watcher_task = None
        self.observer = None

    async def cog_unload(self):
        """當 Cog 被卸載時清理文件監控器"""
        if self.file_watcher_task:
            self.file_watcher_task.cancel()
            try:
                await self.file_watcher_task
            except asyncio.CancelledError:
                pass
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            # logging.info("文件監控器已停止")

    def _get_all_cogs(self):
        return get_all_cogs()
    
    async def _load_cogs(self, cogs: list|str):
        if isinstance(cogs, str):
            cogs = [cogs]
        for cog in cogs:
            try:
                await self.bot.load_extension(f"cogs.{cog}")
                # logging.info(f"已成功載入 {cog}。")
            
            except Exception as e:
                logging.warning(f"Cogs 載入失敗: {e}")
                raise e
    
    async def _unload_cogs(self, cogs: list|str):
        if isinstance(cogs, str):
            cogs = [cogs]
        for cog in cogs:
            try:
                await self.bot.unload_extension(f"cogs.{cog}")
                logging.info(f"已成功解除載入 {cog}。")
            
            except Exception as e:
                logging.warning(f"Cogs 解載失敗: {e}")
                raise e
            
    async def _reload_cogs(self, cogs: list|str):
        await reload_cogs(cogs, self.bot)
    

    # 載入指令程式檔案
    @commands.command()
    async def load(self, ctx: commands.Context, extension):
        log(ctx, extension=extension)
        if ctx.author.id not in settings.DEV_ID:return
        try:
            if extension == "all":
                cogs = self._get_all_cogs()                
            else:
                cogs = [extension]

            await self._load_cogs(cogs)

            embed = ui.dev_embed(f"**已成功載入 `{'`, `'.join(cogs)}`。 共載入 {len(cogs)} 項內容。**")
            logging.info(f"已成功載入 `{'`, `'.join(cogs)}`。 共載入 {len(cogs)} 項內容。")

        except Exception as e:
            embed = ui.dev_embed(f"**載入失敗\n```cmd\n{e}```**", color = discord.Color.red())
        finally:
            await ctx.reply(embed = embed)

    # 卸載指令檔案
    @commands.command()
    async def unload(self, ctx: commands.Context, extension):
        log(ctx, extension=extension)
        if ctx.author.id not in settings.DEV_ID:return
        try:
            if extension == "all":
                cogs = self._get_all_cogs()
            else:
                cogs = [extension]

            await self._unload_cogs(cogs)

            embed = ui.dev_embed(f"**已成功解除載入 `{'`, `'.join(cogs)}`。 共解除載入 {len(cogs)} 項內容。**")
            logging.info(f"已成功解除載入 `{'`, `'.join(cogs)}`。 共解除載入 {len(cogs)} 項內容。")
        except Exception as e:
            embed = ui.dev_embed(f"**解除載入失敗\n```cmd\n{e}```**", color = discord.Color.red())
        finally:
            await ctx.reply(embed = embed)

    # 重新載入程式檔案
    @commands.command()
    async def reload(self, ctx: commands.Context, extension:str|None=None):
        log(ctx, extension=extension)
        
        if ctx.author.id not in settings.DEV_ID:return
        if extension is None:
            await ctx.reply(embed=ui.dev_embed("請選擇要重新載入的模組"), view=get_reload_all_view(), ephemeral=True)
            return
        try:
            if extension == "all":
                cogs = self._get_all_cogs()
            else:
                cogs = [extension]
            await self._reload_cogs(cogs)
            embed = ui.dev_embed(f"**已成功重新載入 `{'`, `'.join(cogs)}`。 共重新載入 {len(cogs)} 項內容。**")
            logging.info(f"已成功重新載入 `{'`, `'.join(cogs)}`。 共重新載入 {len(cogs)} 項內容。")
        except Exception as e:
            embed = ui.dev_embed(f"**重新載入失敗\n```cmd\n{e}```**", color = discord.Color.red())
        finally:
            await ctx.reply(embed = embed)

    # 重啟指令
    @commands.command()
    async def restart(self, ctx: commands.Context):
        log(ctx)
        if ctx.author.id not in settings.DEV_ID:return
        logging.info(f"{ctx.author} > {settings.PREFIX} restart")
        logging.info(f"{'='*10} 系統重啟 {'='*10}")
        embed = ui.dev_embed("**機器人正在重啟...**")
        await self.bot.change_presence(status=discord.Status.offline)
        await ctx.reply(embed=embed)
        python = sys.executable
        os.execl(python, python, *sys.argv)

    @commands.command()
    async def test(self, ctx: commands.Context):
        log(ctx)
        if ctx.author.id not in settings.DEV_ID:return
        logging.info(f"{ctx.author} > {settings.PREFIX} test")
        await ctx.reply(embed=ui.dev_embed("**測試成功！**"))
    

class CogFileChangeHandler(FileSystemEventHandler):
    def __init__(self, bot:commands.Bot):
        self.last_modified = None
        self.last_modified_time = 0
        self.lock = False
        self.bot = bot

    def on_modified(self, event):
        current_time = time.time()
        # 檢查事件是否是短時間內重複發生的
        if (not event.is_directory) and str(event.src_path).endswith(".py") and (self.last_modified != event.src_path or current_time - self.last_modified_time > 2):
            self.last_modified = event.src_path
            self.last_modified_time = current_time
            file_path = str(event.src_path).replace('/', '\\')
            logging.info(f"發現檔案更動: {file_path}")
            
            # 檢查是否為 cogs 目錄下的 Python 檔案
            if "\\cogs\\" in file_path and file_path.endswith(".py"):
                cog_name = str(os.path.basename(event.src_path)[:-3])
                self.bot.loop.create_task(reload_cogs(cog_name, self.bot))

async def start_file_watcher(bot, dev_cog:DevCog):
    # logging.info("啟動檔案監控器...")
    event_handler = CogFileChangeHandler(bot)
    observer = Observer()
    
    # 監控 cogs 目錄
    observer.schedule(event_handler, path='./cogs', recursive=False)
    
    observer.start()
    
    # 將 observer 儲存到 dev_cog 實例中
    dev_cog.observer = observer

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        observer.stop()
        # logging.info("文件監控器任務已取消")
    finally:
        observer.join()

# 在 setup 函數中啟動檔案監控
async def setup(bot: commands.Bot):
    dev_cog = DevCog(bot)
    await bot.add_cog(dev_cog)
    bot.add_view(get_reload_all_view())
    if settings.AUTO_RELOAD:
        dev_cog.file_watcher_task = bot.loop.create_task(start_file_watcher(bot, dev_cog))
    logging.info(f'{__name__} 已載入')
