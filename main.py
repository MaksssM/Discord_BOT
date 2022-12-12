import discord
import json
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True

file = open('config.json', 'r')
config = json.load(file)

bot = commands.Bot(config['prefix'], intents = intents)
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'pong!')


bot.run(config['token'])
