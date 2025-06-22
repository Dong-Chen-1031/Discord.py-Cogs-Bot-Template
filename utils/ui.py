import discord
from discord import Embed

def info_embed(
        info,
        color=discord.Color.blue(),
    ) -> Embed:
    """製作資訊嵌入"""
    embed = Embed(description=f"**{info}**", color=color)
    # embed.set_footer(text="TTS Bot")
    return embed

def dev_embed(
        info,
        color=discord.Color.blue(),
        footer_text="開發者專用",
    ) -> Embed:
    """製作開發者資訊嵌入"""
    embed = Embed(title="開發者指令", description=f"**{info}**", color=color)
    embed.set_footer(text=footer_text)
    return embed