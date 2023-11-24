import logging
from telegram import constants
from telegram.ext import MessageHandler, ConversationHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import os
from pprint import pprint
from __version__ import __version__

class Environment:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.bot_admin_id = int(os.getenv('BOT_ADMIN_ID'))
        self.bot_allowed_users = [self.bot_admin_id]
        if os.getenv('BOT_ALLOWED_USERS') is not None:
            self.bot_allowed_users += [int(user) for user in os.getenv('BOT_ALLOWED_USERS').split(",") if user.strip()]
        self.about_message = \
            "This bot was created by bitdruid.\n" + \
            "Current Version is: {}\n\n".format(__version__) + \
            "https://github.com/bitdruid/osintbot"
        
def create_document(filename, content):
    document = open(filename, "w")
    document.write(content)
    document.close()
    document = open(filename, "rb")
    return document

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from functools import wraps
ALLOWED_USERS = Environment().bot_allowed_users
def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USERS:
            not_authorized_message = \
                    "You are not authorized to use this bot. \
                    If you landed here but do not know the admin in person, you are not allowed to use this bot.\n\n \
                    If the admin linked you to this bot, type /telegramID to get your Telegram ID and send it to the admin."
            print(f"Unauthorized access denied for {user_id}.")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=not_authorized_message)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def restricted_admin(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != Environment().bot_admin_id:
            not_authorized_message = "Only the admin is allowed to use this command."
            print(f"Unauthorized access denied for {user_id}.")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=not_authorized_message)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped





@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    start_message = "You are authorized to use this bot. For more information:\n\n/commands".format(user_id)
    print(f"Authorized access granted for {user_id}.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)

@restricted
async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_message = \
    "Available commands:\n\n" + \
    "/start - welcome message\n" + \
    "/commands - all commands\n" + \
    "/whois <domain> - whois a domain\n" + \
    "/admin - admin commands\n" + \
    "/telegramID - get your Telegram ID\n" + \
    "/about - About this bot"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=commands_message)

@restricted
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=Environment().about_message)

async def telegramID(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    telegramID_message = "Your Telegram ID is {}.".format(user_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=telegramID_message)

@restricted_admin
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Admin commands... not implemented yet.")
    allowed_users_message = "Allowed users: {}".format(Environment().bot_allowed_users)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=allowed_users_message)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="This command is not available. Type /commands to see all available commands.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Cancelled.")





#####
##### OSINT COMMANDS
#####

WHOIS = range(1)
async def request_whois(update: Update, context: ContextTypes.DEFAULT_TYPE):
    argument = context.args
    if len(argument) > 0:
        await query_whois(update, context)
        return ConversationHandler.END
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="For which domain do you want to query WHOIS data?")
        return WHOIS

import whois
import stuff
@restricted
async def query_whois(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if query_whois is called by request_whois, context.args is not None but update.message.text is None
    if context.args is not None:
        domain = context.args[0]
    else:
        # if query_whois is called by the ConversationHandler, update.message.text is not None but context.args is None
        if update.message.text is not None:
            if update.message.text.startswith("/whois"):
                domain = update.message.text.split("/whois ")[1]
            else:
                domain = update.message.text
        else:
            return ConversationHandler.END
    if not stuff.validate_domain(domain):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="This is not a valid domain.")
        return ConversationHandler.END
    await context.bot.send_message(chat_id=update.effective_chat.id, text="WHOIS query for {}...".format(domain))
    domain_data = whois.run(domain)
    if domain_data not in [False, None]:
        if "stats" in domain_data:
            domain_stats = domain_data["stats"]
            hosting_stats = ""
            # format stats for markdown code span
            for key, value in domain_stats.items():
                hosting_stats += f"{key}: `{value}`\n"
            hosting_message = "WHOIS hosting {}:".format(domain) + "\n\n" + hosting_stats
            await context.bot.send_message(chat_id=update.effective_chat.id, text=hosting_message, parse_mode=constants.ParseMode.MARKDOWN)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No stats available for this domain.")
        if "whois" in domain_data:
            domain_whois = domain_data["whois"]
            document = create_document("whois" + "_" + domain + ".txt", domain_whois)
            await context.bot.send_document(chat_id=update.effective_chat.id, document=document)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No WHOIS data available for this domain.")
    else:
        failed_message = \
            "No WHOIS data available for this input." + \
            "Check if the domain is valid and does exist."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=failed_message)
    return ConversationHandler.END





if __name__ == '__main__':
    print(f"Starting bot with token {Environment().bot_token} and admin {Environment().bot_admin_id}...")

    application = ApplicationBuilder().token(Environment().bot_token).build()
    
    start_handler = CommandHandler('start', start)
    commands_handler = CommandHandler('commands', commands)
    whois_handler = ConversationHandler(
        entry_points=[CommandHandler('whois', request_whois)],
        states={
            WHOIS: [MessageHandler(filters.TEXT & ~filters.COMMAND, query_whois)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    admin_handler = CommandHandler('admin', admin)
    telegramID_handler = CommandHandler('telegramID', telegramID)
    about_handler = CommandHandler('about', about)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(commands_handler)
    application.add_handler(whois_handler)
    application.add_handler(CommandHandler('admin', admin))
    application.add_handler(telegramID_handler)
    application.add_handler(about_handler)

    application.add_handler(unknown_handler)
    
    application.run_polling()