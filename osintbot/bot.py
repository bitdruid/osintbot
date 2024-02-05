import discord
from discord.ext import commands
import os
from datetime import datetime
from dotenv import load_dotenv

import db
import send
import helper as bot_helper
import osintkit.helper as kit_helper
from __version__ import __version__
#from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.help_command = None
modes = ['mention_message', 'direct_message', 'channel_message']

document_path = "documents/"
os.makedirs(document_path, exist_ok=True)

db = db.Database()

class Environment:
    def __init__(self):
        if os.path.isfile('.env'):
            load_dotenv(dotenv_path='.env')
        self.bot_token = os.getenv('BOT_TOKEN') if os.getenv('BOT_TOKEN') else ValueError("BOT_TOKEN is not set")
        self.bot_name = os.getenv('BOT_NAME') if os.getenv('BOT_NAME') else "osintbot"
        self.bot_channel = os.getenv('BOT_CHANNEL') if os.getenv('BOT_CHANNEL') else "osint"
        self.about_message = \
            "This bot was created by bitdruid.\n" + \
            "Current Version is: {}\n\n".format(__version__) + \
            "https://github.com/bitdruid/osintbot"





def create_document(filename, content):
    document = open(document_path + filename, "w")
    document.write(content)
    document.close()
    document = open(document_path + filename, "rb")
    return document

def json_to_markdown_codeblock(json):
    heading = ""
    url = ""
    markdown = ""
    message = ""
    for key, value in json.items():
        heading = f"**{key}**\n"
        if isinstance(value, dict):
            markdown += "```\n"
            for subkey, subvalue in value.items():
                if "url" in subkey.lower(): # if url is in key, create clickable link and skip url in markdown
                    url = "<{}>\n".format(subvalue)
                    continue
                markdown += f"{subkey}: {subvalue}\n"
            markdown += "```\n"
        else:
            if "url" in key.lower(): # if url is in key, create clickable link and skip url in markdown
                url = "<{}>\n".format(subvalue)
                continue
            markdown += "```\n"
            markdown += f"{value}\n"
            markdown += "```\n"
        message += heading + url + markdown
        heading, url, markdown = "", "", ""
    return message + "\n"

async def output_text_result(ctx, input: str, result: str, key: str):
    """
    Sends the output text result to the specified context (channel or direct message).

    Parameters:
    - ctx (object): The context object representing the channel or user.
    - input (str): The user input value.
    - result (str): The query result data.
    - key (str): The json key to access the specific result data.
    - dm (bool, optional): Specifies whether to send the result as a direct message. Default is False.
    """
    if key in result:
        result_data = result[key]
        result_message = f"{key.upper()} for {input}:\n" + json_to_markdown_codeblock(result_data)
        await send.message(ctx, result_message)
    else:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + f"No {key.upper()} information available for this input.")

async def output_file_result(ctx, input, result, key):
    """
    Sends the result data as a file to the specified Discord channel.

    Parameters:
    - ctx (discord.Context): The context of the Discord message.
    - input (str): The input value.
    - result (dict): The result data.
    - key (str): The key to access the result data.
    """
    if key in result:
        result_data = result[key]
        document = create_document(key + "_" + input + ".txt", result_data)
        await send.message(ctx, f"{key.upper()} data for {input}:", file=bot.File(document, filename=key + "_" + input + ".txt"))
    else:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + f"No {key.upper()} information available for this input.")
     
async def initialize():
    # check if bot-channel exists and create it if not
    for guild in bot.guilds:
        # insert guild leader into database
        db.db_insert_leader(guild.owner.id, guild.owner.name, guild.id, guild.name)
        db.db_insert_global_config(guild.id, guild.name)
        for channel in guild.channels:
            if channel.name == Environment().bot_channel:
                return
        overwrites = {
            guild.owner: bot.PermissionOverwrite(read_messages=True),
            guild.me: bot.PermissionOverwrite(read_messages=True),
            guild.default_role: bot.PermissionOverwrite(read_messages=False)
        }
        channel = await guild.create_text_channel(Environment().bot_channel, overwrites=overwrites)
        await channel.send("{}".format(guild.owner.mention) + "\n" + f"I'm {Environment().bot_name} and created this private channel for interaction. Configure permissions for this channel as you like.\nGet started with `/help` or mention `@{Environment().bot_name} help` in this channel.")





# timeout a command for guild for 10 seconds
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "This command is on cooldown to prevent flooding API by bot-IP. Try again in {:.2f}s.".format(error.retry_after))
    else:
        raise error






# if bot joins a server or starts it checks for osint-channel and creates it if it does not exist
@bot.event
async def on_ready():
    await initialize()
    
@bot.event
async def on_guild_join(guild):
    await initialize()





@bot.command(name='commands', aliases=['help', 'start', 'usage'], description='Shows help message')
async def help(ctx):
    # send and mention
    commands = {}
    commands_message = ""
    for command in bot.commands:
        commands[command.name] = f"`{command.name}` - {command.description}"
    commands = dict(sorted(commands.items()))
    for command in commands:
        commands_message += commands[command] + "\n"
    await ctx.send("{}".format(ctx.author.mention) + \
        "\n\n" + \
        "__I am {} and i can help you with this:__".format(Environment().bot_name) + \
        "\n\n" + \
        commands_message + \
        "\n" + \
        "You can also mention me to run commands.\nExample: `@{} whois example.com`".format(Environment().bot_name))





import osintkit.whois as whois
@bot.command(name='whois', description='Shows WHOIS information for a domain', )
async def query_whois(ctx, domain=None):
    if not domain:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/whois <ip/domain>")
        return
    if not kit_helper.validate_domain(domain) and not kit_helper.validate_ip(domain):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "Invalid domain or IP address.")
        return
    whois_data = whois.request(domain)
    if whois_data:
        await output_file_result(ctx, domain, whois_data, "whois")
    else:
        failed_message = \
            "No WHOIS data available for this input. " + \
            "Check if the domain is valid and does exist."
        await ctx.send("{}".format(ctx.author.mention) + "\n" + failed_message)





import osintkit.iplookup as iplookup
@commands.cooldown(1, 15, commands.BucketType.guild)
@bot.command(name='iplookup', description='Shows IP information for a domain or IP address')
async def query_iplookup(ctx, input=None):
    if not input:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/iplookup <ip/domain>")
        return
    if not kit_helper.validate_domain(input) and not kit_helper.validate_ip(input):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "Invalid domain or IP address.")
        return
    iplookup_data = iplookup.request(input)
    if iplookup_data:
        await output_text_result(ctx, input, iplookup_data, "iplookup")
    else:
        failed_message = \
            "No IP information available for this input. " + \
            "Check if the domain or IP address is valid and does exist."
        await ctx.send("{}".format(ctx.author.mention) + "\n" + failed_message)





import osintkit.geoip as geoip
@commands.cooldown(1, 15, commands.BucketType.guild)
@bot.command(name='geoip', description='Shows GeoIP information for a domain or IP address')
async def query_geoip(ctx, input=None):
    if not input:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/geoip <ip/domain>")
        return
    if not kit_helper.validate_domain(input) and not kit_helper.validate_ip(input):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "Invalid domain or IP address.")
        return
    geoip_data = geoip.request(input)
    if geoip_data["geoip"]:
        await output_text_result(ctx, input, geoip_data, "geoip")
    else:
        failed_message = \
            "No GeoIP information available for this input. " + \
            "Check if the domain or IP address is valid and does exist."
        await ctx.send("{}".format(ctx.author.mention) + "\n" + failed_message)





import osintkit.arecord as arecord
@commands.cooldown(1, 15, commands.BucketType.guild)
@bot.command(name='arecord', description='Shows A record information for a domain or IP address')
async def query_arecord(ctx, input=None):
    if not input:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/arecord <ip/domain>")
        return
    if not kit_helper.validate_primary(input):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "Invalid domain or IP address.")
        return
    arecord_data = arecord.request(input)
    if arecord_data:
        await output_text_result(ctx, input, arecord_data, "arecord")
    else:
        failed_message = \
            "No A record information available for this input. " + \
            "Check if the domain or IP address is valid and does exist."
        await ctx.send("{}".format(ctx.author.mention) + "\n" + failed_message)





@commands.cooldown(1, 15, commands.BucketType.guild)
@bot.command(name='report', description='Gives you whois, iplookup and geoip information for a domain or IP address')
async def report(ctx, input=None):
    if not input:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/report <ip/domain>")
        return
    if not kit_helper.validate_domain(input) and not kit_helper.validate_ip(input):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "Invalid domain or IP address.")
        return
    report_data = {}
    whois_data = whois.request(input)
    if "whois" in whois_data: 
        document = create_document("whois" + "_" + input + ".txt", whois_data["whois"])
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "WHOIS data for {}:".format(input), file=bot.File(document, filename="whois" + "_" + input + ".txt"))            
    iplookup_data = iplookup.request(input)
    if iplookup_data:
        report_data["iplookup"] = iplookup_data["iplookup"]
    geoip_data = geoip.request(input)
    if geoip_data:
        report_data["geoip"] = geoip_data["geoip"]
    if report_data:
        for key in report_data:
            await output_text_result(ctx, input, report_data, key, dm=True)
    else:
        failed_message = \
            "No data available for this input. " + \
            "Check if the domain or IP address is valid and does exist."
        await ctx.send("{}".format(ctx.author.mention) + "\n" + failed_message)





@bot.command(name='mailheader', description='Analyzes a provided mail header')
async def mailheader(ctx, input=None):
    if not input:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/mailheader <mail header>")
        return
    mailheader_data = mailheader.request(input)
    if mailheader_data:
        await output_text_result(ctx, input, mailheader_data, "mailheader")
    else:
        failed_message = \
            "Could not analyze or recognize this mail header. " + \
            "Check if your file is a valid mail header."
        await ctx.send("{}".format(ctx.author.mention) + "\n" + failed_message)





@bot.command(name='prune', description='Prunes messages from the osint-channel')
async def prune(ctx):
    if ctx.channel.name == Environment().bot_channel:
        count_history = 0
        async for message in ctx.channel.history(limit=None):
            count_history += 1
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        caller = ctx.author
        # purge messages
        await ctx.channel.purge()
        # prune documents
        amount_documents = len(os.listdir(document_path))
        for file in os.listdir(document_path):
            os.remove(document_path + file)
        prune_message = await ctx.send("{}".format(ctx.author.mention) + "\n" + "Pruned history from osint-channel at `{}` by `{}`:\n".format(timestamp, caller) + "- messages: `{}`\n".format(count_history) + "- documents: `{}`".format(amount_documents))
        # pin message
        await prune_message.pin()
    else:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "This command is only available in the osint-channel.")





@bot.command(name='config', description='Configure bot settings for you and your server')
async def config(ctx, command=None, key=None, value=None):
    mode = "set the bot mode for response to `dm` (direct message) or `mm` (mention message)"
    globalmode = mode + " or `off` (user can set mode by himself)"
    if not command:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + \
            "**Usage:**\n/config <command> <value>:\n" + \
            "Available commands:\n" + \
            "- `mode` - " + mode + "\n" + \
            "- `show` - show the current configuration\n" + \
            "Admin commands:\n" + \
            # "- `mkadmin <@user>` - make a user admin\n" + \
            # "- `rmadmin <@user>` - remove a user from admin\n" + \
            "- `globalmode` <mode> - " + globalmode + "\n" + \
            "- `userdump` - dump the user database\n" + \
            "- `confdump` - dump the configuration database")
        return
    if command == "mode":
        if not key:
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/config mode <mode>:\n" + mode)
            return
        if key == "dm":
            db.db_set_user_config(ctx.author.id, ctx.guild.id, "tbl_user_response_mode", "dm")
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "Bot responses will be sent as direct message for user" + ctx.author.mention)
        elif key == "mm":
            db.db_set_user_config(ctx.author.id, ctx.guild.id, "tbl_user_response_mode", "mm")
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "Bot responses will be public sent as mention message for user" + ctx.author.mention)
    if command == "show":
        if db.db_isleader(ctx.author.id, ctx.guild.id):
            config = db.db_get_global_config(ctx.guild.id)
            config = json_to_markdown_codeblock(config)
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "Configuration for:\n" + config)
        else:
            config = db.db_get_user_config(ctx.author.id, ctx.guild.id)
            config = json_to_markdown_codeblock(config)
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "Configuration for:\n" + config)
    if db.db_isleader(ctx.author.id, ctx.guild.id):
        if command == "userdump":
            dump = db.db_dump(ctx.guild.id, "user")
            document = create_document("dbdump" + "_" + ctx.guild.name + ".txt", dump)
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "Database dump for {}:".format(ctx.guild.name), file=bot.File(document, filename="dbdump" + "_" + ctx.guild.name + ".txt"))
        if command == "confdump":
            dump = db.db_dump(ctx.guild.id, "conf")
            document = create_document("confdump" + "_" + ctx.guild.name + ".txt", dump)
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "Configuration dump for {}:".format(ctx.guild.name), file=bot.File(document, filename="confdump" + "_" + ctx.guild.name + ".txt"))
        if command == "globalmode":
            if not key:
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/config globalmode <mode>:\n" + globalmode)
                return
            if key == "dm":
                db.db_set_global_config(ctx.guild.id, ctx.author.id, "tbl_global_response_mode", "dm")
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "Bot responses will be sent as direct message.")
            elif key == "mm":
                db.db_set_global_config(ctx.guild.id, ctx.author.id, "tbl_global_response_mode", "mm")
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "Bot responses will be public sent as mention message.")
            elif key == "off":
                db.db_set_global_config(ctx.guild.id, ctx.author.id, "tbl_global_response_mode", "off")
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "Bot responses will be sent like the user specified for himself.")
    else:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "You are not the leader of this server and not allowed to use this command.")



            
        




@bot.command(name='id', description='Shows your Discord ID')
async def id(ctx):
    await ctx.send("{}".format(ctx.author.mention) + "\n" + "Your Discord ID is: {}".format(ctx.author.id))





@bot.command(name='about', description='Shows information about this bot')
async def about(ctx):
    await ctx.send("{}".format(ctx.author.mention) + "\n" + Environment().about_message)




# you can run commands by mentioning the bot
@bot.event
async def on_message(message):
    # ignore messages from bot, dms and other channels then bot-channel
    if message.author == bot.user:
        return
    if message.guild is None:
        await message.channel.send(f"Please communicate in the bot-channel.")
        return
    if message.channel.name != Environment().bot_channel:
        return
    
    # add the user to the database
    db.db_insert_user(message.author.id, message.author.name, message.guild.id, message.guild.name)
    
    if bot.user.mentioned_in(message):
        # remove mention from message
        content = message.content
        words = content.split()
        words = [words for words in words if not words.startswith("<@")]
        # check if message is not empty after removing mention and get command + arguments
        if len(words) > 0:
            command_name = words[0]
            command_arguments = words[1:]
            # check if command exists
            command = bot.get_command(command_name)
            if command:
                # invoke command = run command
                ctx = await bot.get_context(message)
                try:
                    bucket = command._buckets.get_bucket(ctx)
                    retry_after = bucket.update_rate_limit()
                except:
                    retry_after = False
                if retry_after:
                    await ctx.send(f"{ctx.author.mention} This command is on cooldown. Try again in {retry_after:.2f} seconds.")
                else:
                    await ctx.invoke(command, *command_arguments)
            else:
                await message.channel.send("{}".format(message.author.mention) + "\n" + "Unknown command.")
        else:
            await message.channel.send("{}".format(message.author.mention) + "\n" + "You can use `/help` to get a list of commands.")
    await bot.process_commands(message)





bot.run(Environment().bot_token)