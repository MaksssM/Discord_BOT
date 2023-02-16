import asyncio
import sqlite3

import discord
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



class BalanceBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.users = {}

    @commands.command(name="balance")
    async def balance(self, ctx, member: discord.Member = None):
        if not member:
            user_id = str(ctx.author.id)
            conn = sqlite3.connect("discord_bot.db")
            c = conn.cursor()
            c.execute(
                """INSERT OR IGNORE INTO users (user_id, coins)
                VALUES (?, ?)""",
                (user_id, 0)
            )
            c.execute(
                """SELECT coins FROM users WHERE user_id=?""",
                (user_id,)
            )
            result = c.fetchone()
            if result is not None:
                coins = result[0]
                balance_message = f"{ctx.author.mention}, your balance is {coins} coins."
            else:
                balance_message = f"{ctx.author.mention}, your balance is 0 coins."
            conn.commit()
            conn.close()
        else:
            user_id = str(member.id)
            conn = sqlite3.connect("discord_bot.db")
            c = conn.cursor()
            c.execute(
                """INSERT OR IGNORE INTO users (user_id, coins)
                VALUES (?, ?)""",
                (user_id, 0)
            )
            c.execute(
                """SELECT coins FROM users WHERE user_id=?""",
                (user_id,)
            )
            result = c.fetchone()
            if result:
                coins = result[0]
                balance_message = f"{member.mention}'s balance is {coins} coins."
            else:
                balance_message = f"{member.mention}'s balance is 0 coins."
            conn.commit()
            conn.close()
        await ctx.send(balance_message)


@commands.command(name="addcoins")
@commands.has_permissions(administrator=True)
async def addcoins(self, ctx, amount: int, user: discord.User):
    user_id = str(user.id)
    if user_id not in users:
        users[user_id] = User(user_id)
    user = users[user_id]
    user.coins += amount

    conn = sqlite3.connect("discord_bot.db")
    c = conn.cursor()
    c.execute(
        """INSERT OR IGNORE INTO users (user_id, coins)
        VALUES (?, ?)""",
        (user_id, 0)
    )
    c.execute(
        """UPDATE users SET coins=? WHERE user_id=?""",
        (user.coins, user_id)
    )
    conn.commit()
    conn.close()

    await ctx.send(f"{amount} coins added to {user.mention}'s balance")


@commands.Cog.listener()
async def on_message(self, message):
    user = message.author
    user_id = user.id
    username = user.name

    conn = sqlite3.connect("discord_bot.db")
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            coins INTEGER
        )"""
    )
    conn.commit()

    if message.content.startswith("!balance"):
        user_id = message.author.id
        c.execute(
            """SELECT coins FROM users WHERE user_id=?""",
            (user_id,)
        )
        result = c.fetchone()
        if result:
            coins = result[0]
            await message.channel.send(f"{message.author.name} balance: {coins} coins")
        else:
            await message.channel.send(f"{message.author.name} not found")
    elif message.content.startswith("!add"):

        _, amount_str, user_str = message.content.split()
        amount = int(amount_str)
        user_id = user_str.strip("<@!>")
        user = await client.fetch_user(user_id)

        if not user:
            await message.channel.send(f"{message.author.name}, user not found.")
            return

        if amount <= 0:
            await message.channel.send(f"{message.author.name}, the amount must be greater than zero.")
            return

        await add(message.channel, amount, user)
    else:
        await client.process_commands(message)

    conn.close()


@commands.Cog.listener()
async def on_voice_state_update(self, member, before, after):
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
