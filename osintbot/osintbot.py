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
    commands_message = ""
    for command in bot.commands:
        commands_message += "`{}` - {}\n".format(command.name, command.description)
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
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/whois <domain>")
        return
    if not helper.validate_domain(domain):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "Invalid domain name.")
        return
    domain_data = whois.request(domain)
    if domain_data:
        if "stats" in domain_data:
            domain_stats = domain_data["stats"]
            hosting_stats = ""
            # format stats for markdown code span
            hosting_stats = json_to_markdown_codeblock(domain_stats)
            hosting_message = "WHOIS hosting {}:".format(domain) + "\n\n" + hosting_stats
            await ctx.send("{}".format(ctx.author.mention) + "\n" + hosting_message)
        else:
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "No stats available for this domain.")
        if "whois" in domain_data:
            domain_whois = domain_data["whois"]
            document = create_document("whois" + "_" + domain + ".txt", domain_whois)
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "WHOIS data for {}:".format(domain), file=discord.File(document, filename="whois" + "_" + domain + ".txt"))
        else:
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "No WHOIS data available for this domain.")
    else:
        failed_message = \
            "No WHOIS data available for this input." + \
            "Check if the domain is valid and does exist."
        await ctx.send("{}".format(ctx.author.mention) + "\n" + failed_message)





import iplookup
@bot.command(name='iplookup', description='Shows IP information for a domain or IP address')
async def query_iplookup(ctx, ip=None):
    if not ip:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/iplookup <ip/domain>")
        return
    if not helper.validate_domain(ip) and not helper.validate_ip(ip):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "Invalid domain or IP address.")
        return
    iplookup_data = iplookup.request(ip)
    if iplookup_data:
        if "iplookup" in iplookup_data:
            iplookup_entry = iplookup_data["iplookup"]
            iplookup_message = "IPLOOKUP for {}:".format(ip) + "\n\n" + json_to_markdown_codeblock(iplookup_entry)
            await ctx.send("{}".format(ctx.author.mention) + "\n" + iplookup_message)
        else:
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "No IP information available for this input.")
    else:
        failed_message = \
            "No IP information available for this input." + \
            "Check if the domain or IP address is valid and does exist."
        await ctx.send("{}".format(ctx.author.mention) + "\n" + failed_message)





import geoip
@bot.command(name='geoip', description='Shows GeoIP information for a domain or IP address')
async def query_geoip(ctx, ip=None):
    if not ip:
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/geoip <ip/domain>")
        return





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