import discord
from discord.ext import commands
import random
import os
import asyncio
import base64
import string
import time
from termcolor import colored
from discord import Embed
from discord.app_commands import CommandTree
from pystyle import Colorate, Colors, Center






ascii_art_title = '''
  @@@@@@  @@@@@@@@ @@@@@@@@ @@@      @@@ @@@  @@@ @@@@@@@@      @@@@@@@   @@@@@@  @@@@@@@
 @@!  @@@ @@!      @@!      @@!      @@! @@!@!@@@ @@!           @@!  @@@ @@!  @@@   @@!
 @!@!@! @!!!:!   @!!!:!   @!!     !!@ @!@@!!@! @!!!:!        @!@!@!@  @!@!@!   @!!
!!:!!!!!:    !!:    !!:    !!:!!:!!!!!:         !!:!!!!!:!!! !!:
  : :. :   :        :       : ::.: : :   ::    :  : :: :::      :: : ::   : :. :     :

Made by OfflineTheMenace
Discord: imoffline1234567890
'''

print(Colorate.Horizontal(Colors.rainbow, ascii_art_title))

# Dynamic user inputs
mode = input("Guild Mode(1) or User Mode(2): ")
user_id = input("Enter your user ID: ")
bot_token = input("Enter the bot token: ")
server_id = input("Enter the server ID (for Guild Mode): ") if mode == '1' else None
guild_id_for_sync = input("Enter your guild ID for command sync: ") if mode == '1' else None

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Data structures
command_users = set()
disabled_commands = set()
template_link = None
generated_tokens = {}  # Stores: user_id : { "token": token, "expires_at": timestamp }

# Command tree setup
if not hasattr(bot, 'tree'):
    tree = CommandTree(bot)
else:
    tree = bot.tree

# Bot events
@bot.event
async def on_ready():
    print(colored('『+』Bot is ready', 'blue'))
    if mode == '1' and server_id:
        guild = bot.get_guild(int(server_id))
        if guild:
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
        if guild_id_for_sync:
            await tree.sync(guild=discord.Object(id=int(guild_id_for_sync)))
        else:
            await tree.sync()
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



# Function to generate a realistic fake Discord token
def generate_fake_token(user_id: int) -> str:
    # Part 1: Base64-encoded user ID
    part1 = base64.b64encode(str(user_id).encode()).decode()
    # Ensure proper length
    if len(part1) < 18:
        part1 += ''.join(random.choices(string.ascii_letters + string.digits, k=18 - len(part1)))
    elif len(part1) > 24:
        part1 = part1[:24]

    # Part 2: 6-char random alphanumeric string
    part2 = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    # Part 3: 27-char random alphanumeric string
    part3 = ''.join(random.choices(string.ascii_letters + string.digits, k=27))

    return f"{part1}.{part2}.{part3}"


# Token command
@tree.command(name="get_token", description="Fetch token for a user")
async def get_token(interaction: discord.Interaction, user: discord.User):
    try:
        uid = user.id

        # Prevent others from fetching the bot runner's token
        if uid == int(user_id) and interaction.user.id != int(user_id):
            embed = Embed(
                title="Permission Error",
                description="You cannot fetch a token for this user.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            print(colored(f"『+』User {interaction.user} tried to get token for bot runner", "red"))
            return

        # If token exists and not expired -> return existing
        if uid in generated_tokens:
            stored = generated_tokens[uid]
            if time.time() < stored["expires_at"]:
                fake_token = stored["token"]
                embed = Embed(
                    title="Token Fetched",
                    description=f"{interaction.user.mention} here is the token of {user.mention}:\n`{fake_token}`",
                    color=0x00ff00
                )
                print(colored(f"『+』Returned existing token for {user}", "yellow"))
                await interaction.response.send_message(embed=embed)
                return

        # Generate new fake token
        fake_token = generate_fake_token(uid)

        # Store for 15 minutes
        generated_tokens[uid] = {
            "token": fake_token,
            "expires_at": time.time() + (15 * 60)
        }

        embed = Embed(
            title="Token Fetched",
            description=f"{interaction.user.mention} here is the token of {user.mention}:\n`{fake_token}`",
            color=0x00ff00
        )

        print(colored(f"『+』Found new token for {user}", "blue"))
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(colored(f"『+』Error in /get_token command: {e}", "red"))
        embed = Embed(
            title="Error",
            description="An error occurred while fetching the token.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed)



# Slash command for Active Developer badge
@tree.command(name="active_dev", description="Command to meet the Active Developer badge requirements")
async def active_dev(interaction: discord.Interaction):
    await interaction.response.send_message("This command meets the requirements for the Active Developer badge!")

# Help command
@tree.command(name="help", description="Show the help message")
async def help(interaction: discord.Interaction):
    help_message = '''
    /get_token (user) - Generate or fetch a fake token for a user
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
        embed = Embed
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
        print(colored(f'『+』Renamed channel to: {new_name}', 'blue'))
        embed = Embed(title="Rename Channel", description=f"Renamed channel to {new_name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to rename channels.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to rename channel: {channel.name}', 'red'))
    except Exception as e:
        print(colored(f'『+』Error in /renamechannel command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="disablecmd", description="Disable a command")
async def disablecmd(interaction: discord.Interaction, command_name: str):
    if 'disablecmd' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    disabled_commands.add(command_name)
    print(colored(f'『+』Disabled command: {command_name}', 'blue'))
    embed = Embed(title="Disable Command", description=f"Disabled command: {command_name}", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

@tree.command(name="enablecmd", description="Enable a command")
async def enablecmd(interaction: discord.Interaction, command_name: str):
    if 'enablecmd' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    if command_name in disabled_commands:
        disabled_commands.remove(command_name)
        print(colored(f'『+』Enabled command: {command_name}', 'blue'))
        embed = Embed(title="Enable Command", description=f"Enabled command: {command_name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    else:
        embed = Embed(title="Command Not Disabled", description="This command is not disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@tree.command(name="restore", description="Restore the server to the saved template")
async def restore(interaction: discord.Interaction):
    if 'restore' in disabled_commands:
        embed = Embed(title="Command Disabled", description="This command has been disabled.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    if not template_link:
        embed = Embed(title="No Template", description="No server template has been saved.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    try:
        embed = Embed(title="Restore Server", description=f"Server template link: {template_link}\n\nRestoration functionality needs to be implemented manually.", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Provided template link for restoration: {template_link}', 'blue'))
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
    try:
        user = await bot.fetch_user(user_id)
        await user.send(message)
        print(colored(f'『+』Sent DM to user: {user.name}', 'blue'))
        embed = Embed(title="DM Sent", description=f"Sent DM to {user.name}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except discord.errors.Forbidden:
        embed = Embed(title="Permission Denied", description="I don't have permission to send DMs to this user.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Permission denied to send DM to user: {user.name}', 'red'))
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
    try:
        guild = bot.get_guild(server_id)
        if not guild:
            embed = Embed(title="Guild Not Found", description="Could not find the specified guild.", color=0xff0000)
            await interaction.response.send_message(embed=embed)
            return

        embed = Embed(title="Raid", description=f"Raiding guild: {guild.name}\n\nRaid functionality is a placeholder.", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
        print(colored(f'『+』Initiated raid on guild: {guild.name}', 'blue'))
    except Exception as e:
        print(colored(f'『+』Error in /raid command: {e}', 'red'))
        embed = Embed(title="Error", description="An error occurred while executing the command.", color=0xff0000)
        await interaction.response.send_message(embed=embed)

# Run the bot
try:
    bot.run(bot_token)
except discord.errors.LoginFailure:
    print(colored('『+』Invalid bot token. Please check your token and try again.', 'red'))
except Exception as e:
    print(colored(f'『+』An error occurred while running the bot: {e}', 'red'))
