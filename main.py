import asyncio
import discord
import sqlite3
from discord.ext import commands
from config import settings


intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=settings['PREFIX'], intents=intents)
client.remove_command('help')



class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.coins = 0
        self.task = None

users = {}


@client.command(name="balance")
async def balance(ctx, member: discord.Member = None):
    if not member:
        user_id = str(ctx.author.id)
        user = users.get(user_id)
        if not user:
            user = User(user_id)
            users[user_id] = user
        balance_message = f"{ctx.author.mention}, your balance is {user.coins} coins."
    else:
        user_id = str(member.id)
        user = users.get(user_id)
        if not user:
            user = User(user_id)
            users[user_id] = user
        balance_message = f"{member.mention}'s balance is {user.coins} coins."
    await ctx.send(balance_message)



@client.command(name="add")
async def add(ctx, amount: int, user: discord.User):
    user_id = str(user.id)
    if user_id not in users:
        users[user_id] = User(user_id)
    user = users[user_id]
    user.coins += amount
    await ctx.send(f"{amount} coins added to {user.mention}'s balance")


@client.event
async def on_message(message):
    user = message.author
    user_id = user.id
    username = user.name

    conn = sqlite3.connect("discord_bot.db")
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, balance INTEGER)"""
    )
    conn.commit()

    c.execute(
        """INSERT OR IGNORE INTO users (user_id, username, balance)
                 VALUES (?, ?, ?)""",
        (user_id, username, 0),
    )
    c.execute(
        """UPDATE users SET username = ? WHERE user_id = ?""", (username, user_id)
    )
    conn.commit()

    if message.content.startswith("!balance"):
        pass

    conn.close()
    await client.process_commands(message)


@client.event
async def on_voice_state_update(member, before, after):
    user_id = str(member.id)
    if user_id not in users:
        users[user_id] = User(user_id)
    user = users[user_id]

    if before.channel is None and after.channel is not None:
        coins_per_minute = 5

        async def add_coins():
            while True:
                await asyncio.sleep(60)
                user.coins += coins_per_minute

        task = asyncio.create_task(add_coins())
        user.task = task
    elif before.channel is not None and after.channel is None:
        if hasattr(user, 'task') and user.task is not None:
            user.task.cancel()
            user.task = None



client.run(settings['TOKEN'])