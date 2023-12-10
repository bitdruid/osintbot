import discord
from discord.ext import commands
import os
from datetime import datetime
from dotenv import load_dotenv
import helper as helper
from __version__ import __version__
#from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.help_command = None
modes = ['mention_message', 'direct_message', 'channel_message']

def create_document(filename, content):
    document = open(filename, "w")
    document.write(content)
    document.close()
    document = open(filename, "rb")
    return document

def json_to_markdown_codeblock(json):
    markdown = ""
    for key, value in json.items():
        markdown += f"**{key}:**```\n{value}\n```"
    return markdown

async def output_text_result(ctx, input, result, key):
    if key in result:
        result_data = result[key]
        result_message = f"{key.upper()} for {input}:\n" + json_to_markdown_codeblock(result_data)
        await ctx.send("{}".format(ctx.author.mention) + "\n" + result_message)
    else:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + f"No {key.upper()} information available for this input.")

async def output_file_result(ctx, input, result, key):
    if key in result:
        result_data = result[key]
        document = create_document(key + "_" + input + ".txt", result_data)
        await ctx.send("{}".format(ctx.author.mention) + "\n" + f"{key.upper()} data for {input}:", file=discord.File(document, filename=key + "_" + input + ".txt"))
    else:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + f"No {key.upper()} information available for this input.")


class Environment:
    def __init__(self):
        if os.path.isfile('.env'):
            load_dotenv()
        self.bot_token = os.getenv('BOT_TOKEN') if os.getenv('BOT_TOKEN') else ValueError("BOT_TOKEN is not set")
        self.bot_admin_id = int(os.getenv('BOT_ADMIN_ID')) if os.getenv('BOT_ADMIN_ID') else 0
        self.bot_name = os.getenv('BOT_NAME') if os.getenv('BOT_NAME') else "osintbot"
        #self.bot_allowed_users = [self.bot_admin_id]
        #if os.getenv('BOT_ALLOWED_USERS') is not None:
            #self.bot_allowed_users += [int(user) for user in os.getenv('BOT_ALLOWED_USERS').split(",") if user.strip()]
        self.about_message = \
            "This bot was created by bitdruid.\n" + \
            "Current Version is: {}\n\n".format(__version__) + \
            "https://github.com/bitdruid/osintbot"





@bot.command(name=Environment().bot_name, aliases=['help', 'start', 'usage'], description='Shows help message')
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
        "__I can help you with:__" + \
        "\n\n" + \
        commands_message + \
        "\n" + \
        "You can also mention me to run commands.\nExample: `@{} whois example.com`".format(Environment().bot_name))





import whois
@bot.command(name='whois', description='Shows WHOIS information for a domain', )
async def query_whois(ctx, domain=None):
    if not domain:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/whois <ip/domain>")
        return
    if not helper.validate_domain(domain) and not helper.validate_ip(domain):
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





import iplookup
@bot.command(name='iplookup', description='Shows IP information for a domain or IP address')
async def query_iplookup(ctx, input=None):
    if not input:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/iplookup <ip/domain>")
        return
    if not helper.validate_domain(input) and not helper.validate_ip(input):
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





import geoip
@bot.command(name='geoip', description='Shows GeoIP information for a domain or IP address')
async def query_geoip(ctx, ip=None):
    if not ip:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/geoip <ip/domain>")
        return
    
    




@bot.command(name='report', description='Gives you whois, iplookup and geoip information for a domain or IP address')
async def report(ctx, input=None):
    if not input:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/report <ip/domain>")
        return
    if not helper.validate_domain(input) and not helper.validate_ip(input):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "Invalid domain or IP address.")
        return
    report_data = {}
    whois_data = whois.request(input)
    if "whois" in whois_data: 
        document = create_document("whois" + "_" + input + ".txt", whois_data["whois"])
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "WHOIS data for {}:".format(input), file=discord.File(document, filename="whois" + "_" + input + ".txt"))            
    iplookup_data = iplookup.request(input)
    if iplookup_data:
        report_data["iplookup"] = iplookup_data["iplookup"]
    geoip_data = geoip.request(input)
    if geoip_data:
        report_data["geoip"] = geoip_data["geoip"]
    if report_data:
        for key in report_data:
            await output_text_result(ctx, input, report_data, key)
    else:
        failed_message = \
            "No data available for this input. " + \
            "Check if the domain or IP address is valid and does exist."
        await ctx.send("{}".format(ctx.author.mention) + "\n" + failed_message)





@bot.command(name='prune', description='Prunes messages from the osint-channel')
async def prune(ctx):
    if ctx.channel.name == "osint":
        count_history = 0
        async for message in ctx.channel.history(limit=None):
            count_history += 1
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        caller = ctx.author
        await ctx.channel.purge()
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "Pruned {} messages from the osint-channel at `{}` by `{}`.".format(count_history, timestamp, caller))
        # pin message
        async for message in ctx.channel.history(limit=1):
            await message.pin()
    else:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "This command is only available in the osint-channel.")





@bot.command(name='id', description='Shows your Discord ID')
async def id(ctx):
    await ctx.send("{}".format(ctx.author.mention) + "\n" + "Your Discord ID is: {}".format(ctx.author.id))





@bot.command(name='about', description='Shows information about this bot')
async def about(ctx):
    await ctx.send("{}".format(ctx.author.mention) + "\n" + Environment().about_message)




# you can run commands by mentioning the bot
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
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
                await ctx.invoke(command, *command_arguments)
            else:
                await message.channel.send("{}".format(message.author.mention) + "\n" + "Unknown command.")
        else:
            await message.channel.send("{}".format(message.author.mention) + "\n" + "You can use `/help` to get a list of commands.")
    await bot.process_commands(message)





bot.run(Environment().bot_token)