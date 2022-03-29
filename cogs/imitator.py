import discord
from discord.ext import commands
import random
import os
from os import listdir
from os.path import isfile, join
# from async_timeout import timeout
import asyncio

class Imitator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.imitating = None
        # TODO make this guild-based instead of global
        self.chats_folder = "chats/"
        self.chat_filename = None
    
    async def search_for_chat_file(self, ctx, member: discord.Member):
        chat_files = [f for f in listdir(self.chats_folder) if isfile(join(self.chats_folder, f))]
        print(chat_files)
        for chat_file in chat_files:
            print(f"{str(member.id)} =?= {chat_file}")
            if str(member.id) in chat_file:
                self.chat_filename = chat_file
    
    async def get_chat(self):
        if (self.chat_filename is None or self.chat_filename == ""):
            return "I am not currently imitating anybody."

        # select a random line from the individuals' chats file
        print(f"opening {self.chats_folder + self.chat_filename}")
        lines = open(self.chats_folder + self.chat_filename).read().splitlines()
        print(lines)

        if(len(lines) <= 0):
            return None

        line_index = random.randint(0, len(lines) - 1)
        myline = lines[line_index]

        # delete the line from their chats file
        del lines[line_index]

        writing_file = open(self.chats_folder + self.chat_filename, "w+")
        for line in lines:
            writing_file.write(line + "\n")
        writing_file.close()

        # return the selected chat line
        return myline

    async def change_to_user(self, ctx, member: discord.Member):
        self.imitating = member
        await ctx.guild.get_member(self.bot.user.id).edit(nick=f"Fake {member.name}") # , avatar=member.avatar
        await ctx.send(f"{member.name} ({member.id}) {member.avatar_url}")

        await self.search_for_chat_file(ctx, member)
        
    # general talk
    async def say_bullshit(self, ctx):
        
        # show typing indicator
        async with ctx.typing():

            message = await self.get_chat()

            if message is not None:
                
                # .10s per letter in message
                sleeplength = (len(message) * .10)
                await asyncio.sleep(sleeplength)

                # send message
                await ctx.send(message)

            else:
                print(f"Ran out of things to say for {self.imitating.id}_{self.imitating.name}")
                await ctx.message.add_reaction("❌")

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        ctx = message.channel

        # listen for role mentions of imitated user
        for role_mention in message.role_mentions:
            if role_mention in self.imitating.roles:
                await self.say_bullshit(ctx)
        
        # listen for user mentions of imitated user
        for mention in message.mentions:
            if mention == self.imitating:
                await self.say_bullshit(ctx)
            
            # listen for mentions of self bot user (respond to self)
            if mention == self.bot.user:
                await self.say_bullshit(ctx)

        

    # ~talk command - makes thing say shit
    @commands.command()
    async def talk(self, ctx):
        await self.say_bullshit(ctx)       
    
    @commands.command()
    async def forcechange(self, ctx):
        await ctx.send("forcing change of imitation")

        # get current guild from context
        # get all members in guild
        # choose random member
        # display their info

        # select random user
        user_index = random.randint(0, ctx.guild.member_count)
        member = ctx.guild.members[user_index]
        # await ctx.send(f"#{user_index}. ")
       
        await self.change_to_user(ctx, member)
        
        # {member.roles}
        # [<Role id=570730124442599435 name='@everyone'>, <Role id=887968200908759040 name='townies'>, <Role id=639480466809815051 name='vibe checked'>]

    @commands.command()
    async def imitate(self, ctx, member: discord.Member):
        # await ctx.send(member.mention)
        await self.change_to_user(ctx, member)

def setup(bot):
    bot.add_cog(Imitator(bot))
