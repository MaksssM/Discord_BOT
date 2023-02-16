import asyncio
import discord
import sqlite3
from discord.ext import commands
from config import settings
from balance_bot import BalanceBot



intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=settings['PREFIX'], intents=intents)
client.remove_command('help')

client.add_cog(BalanceBot(client))
@client.command(name='balance')
async def balance_command(ctx):
    balance = get_user_balance(ctx.author.id)
    await ctx.send(f"Your balance is {balance}.")

client.run(settings['TOKEN'])
