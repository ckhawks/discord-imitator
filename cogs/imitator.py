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
        self.imitating = {}
        """
        {
            570730124442599435: client.Discord Object,
            754221255065862237: client.Discord Object
        }        
        """
        # TODO make this guild-based instead of global
        self.chats_folder = "chats/"
        self.imitatingchats_path = {}
        """
        {
            570730124442599435: "570730124442599435_ReduxNetwork/117778632021245957_Stellaric.txt",
            754221255065862237: "754221255065862237_ComfeeMonkees/219637673273458699_Manager.txt"
        }
        """

    # when bot is ready
    @commands.Cog.listener("on_ready")
    async def on_ready(self):

        # choose initial imitations
        await self.choose_initial_imitations()

    async def choose_random_valid_user(self, guild: discord.Guild):
        complete = False
        tries = 0
        
        while (complete == False and tries < 5):
            user_index = random.randint(0, guild.member_count - 1)
            member = guild.members[user_index]
            print(f"selected {member.name} for {guild.name}")
            # await ctx.send(f"#{user_index}. ")
        
            if await self.change_to_user(None, member, guild) == False:
                print(f"{member.name} is invalid for {guild.name}, retrying...")
                tries = tries + 1
            else:

                # do this here to prevent ratelimiting when searching
                await guild.get_member(self.bot.user.id).edit(nick=f"Fake {member.name}") # , avatar=member.avatar

                complete = True
                return True
        return False


    # set up initial imitations
    async def choose_initial_imitations(self):
        print("choose initial")

        # for each guild that the bot is present in
        for guild in self.bot.guilds:
            print(f"selecting initial for {guild.name}")
            # select random user

            if (await self.choose_random_valid_user(guild) == False):
                print(f"Could not select a valid user after 5 tries for {guild.name}. Perhaps missing data?")
            
        
    
    # using guild id, find associated guild chats folder
    async def search_for_guild_folder(self, ctx, guild: discord.Guild):
        if guild is None:
            guild = ctx.guild

        guilds_files = [f for f in listdir(self.chats_folder)]
        print(guilds_files)
        for guild_file in guilds_files:
            print(f"{str(guild.id)} =?= {guild_file}")
            if str(guild.id) in guild_file:
                return guild_file
        return None

    # using guild folder, find this user's chat file
    async def search_for_chat_file(self, ctx, member: discord.Member, guild: discord.Guild):
        if guild is None:
            guild = ctx.guild

        guild_folder = await self.search_for_guild_folder(ctx, guild)
        if guild_folder is None:
            print(f"No folder present for the guild {guild.name}")
            return False

        chat_files = [f for f in listdir(self.chats_folder + guild_folder + "/") if isfile(join(self.chats_folder + guild_folder + "/", f))]
        print(chat_files)
        for chat_file in chat_files:
            print(f"{str(member.id)} =?= {chat_file}")
            if str(member.id) in chat_file:
                self.imitatingchats_path[guild.id] = guild_folder + "/" + chat_file
                return True
        
        return False

    # get the next chat that should be sent for this guilds' imitated user
    async def get_chat(self, ctx):
        if (self.imitatingchats_path[ctx.guild.id] is None or self.imitatingchats_path[ctx.guild.id] == ""):
            return "I am not currently imitating anybody."

        # select a random line from the individuals' chats file
        print(f"opening {self.chats_folder}{ctx.guild.id}/{self.imitatingchats_path[ctx.guild.id]}")
        lines = open(self.chats_folder + self.imitatingchats_path[ctx.guild.id]).read().splitlines()
        print(lines)

        if(len(lines) <= 0):
            return None

        line_index = random.randint(0, len(lines) - 1)
        myline = lines[line_index]

        # delete the line from their chats file
        del lines[line_index]

        writing_file = open(self.chats_folder + self.imitatingchats_path[ctx.guild.id], "w+")
        for line in lines:
            writing_file.write(line + "\n")
        writing_file.close()

        # return the selected chat line
        return myline

    # change imitating user to this guild member
    async def change_to_user(self, ctx, member: discord.Member, guild: discord.Guild):
        if guild is None:
            guild = ctx.guild

        self.imitating[guild.id] = member
        if ctx:
            await ctx.send(f"{member.name} ({member.id}) {member.avatar_url}")

        if await self.search_for_chat_file(ctx, member, guild) == False:
            print(f"Could not locate chat file or guild folder for member {member.name} and guild {guild.name}")
            return False
        return True

        
    # general talking wrapper function
    async def say_bullshit(self, ctx):

        channel = None

        if isinstance(ctx, discord.Message):
            channel = ctx.channel
        else:
            channel = ctx
        
        # show typing indicator
        async with channel.typing():

            print(f"Attempting to chat-respond to event in {ctx.guild.name}")

            message = await self.get_chat(ctx)

            if message is not None:

                # .10s per letter in message
                sleeplength = (len(message) * .10)
                await asyncio.sleep(sleeplength)

                # send message
                await channel.send(message)

            else:
                print(f"Ran out of things to say for {self.imitating[ctx.guild.id].id}_{self.imitating[ctx.guild.id].name}")
                if isinstance(ctx, discord.Message):
                    await ctx.add_reaction("❌")
                else:
                    await ctx.message.add_reaction("❌")

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        ctx = message

        # listen for role mentions of imitated user
        for role_mention in message.role_mentions:
            if role_mention in self.imitating[ctx.guild.id].roles:
                await self.say_bullshit(ctx)
        
        # listen for user mentions of imitated user
        for mention in message.mentions:
            if mention == self.imitating[ctx.guild.id]:
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

        if (await self.choose_random_valid_user(ctx.guild) == False):
            await ctx.send("Could not select a valid user after 5 tries. Perhaps missing data?")
            print("Could not select a valid user after 5 tries. Perhaps missing data?")
        
        # {member.roles}
        # [<Role id=570730124442599435 name='@everyone'>, <Role id=887968200908759040 name='townies'>, <Role id=639480466809815051 name='vibe checked'>]

    @commands.command()
    async def imitate(self, ctx, member: discord.Member):
        # await ctx.send(member.mention)
        await self.change_to_user(ctx, member, ctx.guild)

def setup(bot):
    bot.add_cog(Imitator(bot))
