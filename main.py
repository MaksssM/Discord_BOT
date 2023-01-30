import discord
import sqlite3
from discord.ext import commands
from config import settings


intents = discord.Intents.all()
intents.members = True

connect = sqlite3.connect('zalupa')
curs = connect.cursor()

client = commands.Bot(command_prefix = settings['PREFIX'], intents=intents)

@client.event
async def on_ready():
    curs.execute("""Create Table if NOT exists users (
        name TEXT,
        id INT,
        cash BIGINT
    )""")
    connect.commit()    
    for guild in client.guilds:
        for member in guild.members:
            if curs.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                curs.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, {0})")
            else:
                pass


@client.event 
async def on_member_join(member):
    if curs.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        curs.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, {0})")
        connect.commit()
    else:
        pass


@client.command(aliases = ['balance'])
async def _balance(ctx, member:discord.Member = None):
    if member is None:
        await ctx.send(embed = discord.Embed(
            description = f"""Баланс **{ctx.author}** = **{curs.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} **"""
        ))
    else:
        await ctx.send(embed = discord.Embed(
            description = f"""Баланс **{member}** = **{curs.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]} **"""
        ))

@client.command(aliases = ['award'])
async def _award(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, укажите гандона, которому выдать баланс")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, укажите сумму, которую начисляешь")
        elif amount < 1:
            await ctx.send(f"**{ctx.author}**, укажи больше 1")
        else:
            curs.execute("Update users Set cash = cash + {} Where id = {}".format(amount, member.id))
            connect.commit()

              
@client.command(aliases = ['take'])
async def _take(ctx, member:discord.Member = None, amount = None):
    if member is None:
        await ctx.send(f"**{ctx.author}, укажите гандона, которому выдать баланс")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}, укажите сумму, которую забираешь")
        elif int(amount) == 'all':
            curs.execute("UPDATE users SET cash = {} Where id = {}".format(0, member.id))
            connect.commit() 
        elif int(amount) < 1:
            await ctx.send(f"**{ctx.author}, укажи больше 1**")
        else:
            curs.execute("UPDATE users SET cash = cash - {} Where id = {}".format(int(amount), member.id))
            connect.commit()

client.run(settings['TOKEN'])