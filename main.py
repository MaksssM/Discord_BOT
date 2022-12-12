import discord
import json
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True

file = open('config.json', 'r')
config = json.load(file)

bot = commands.Bot(config['prefix'], intents=intents)


@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'pong!')

@bot.command(name='clear')
async def clear(ctx, amount = 1):
    await ctx.channel.purge(limit = amount)


bot.run(config['token'])
