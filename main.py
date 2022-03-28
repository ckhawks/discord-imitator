import discord
import logging
from discord.ext import commands
import os

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# load token from config
from json import load
from pathlib import Path

with Path("config.json").open() as f:
    config = load(f)

# enable members intent
intents = discord.Intents.default()
intents.members = True

"""
client = discord.Client()

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

client = MyClient()
client.run(config["token"])
"""

bot = commands.Bot(command_prefix = "~", intents=intents)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    
    await bot.process_commands(message)

# every 24 hours changes person it's imitating
# force change imitation command
# randomly talks ??
# talks on command (or when pinged)
# changes name/avatar when imitating a user
# chooses a random person to imitate from the server
# bot->chooses random person from guild to imitate
#   uses userid to refer to that individual
#   changes name/avatar
#   changes "conversation database" to this individual

# bot keeps track / logs messages sent throughout the day
#   channel blacklist? wordle
# every x interval, retrain with new messages appended to dataset


if __name__ == "__main__":
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            name = file[:-3]
            bot.load_extension(f"cogs.{name}")
    bot.run(config["token"])
    

