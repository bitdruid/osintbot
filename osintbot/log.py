import os
import sys

def exception(type: str, e: Exception) -> None:
    log(type, f"!-- Error function: {sys.exc_info()[-1].tb_frame.f_code.co_name}")
    log(type, f"!-- Error line: {sys.exc_info()[-1].tb_lineno}")
    log(type, f"!-- Error stacktrace: {e}")

def log(type: str, message: str) -> None:
    print(message)
    os.makedirs('logs', exist_ok=True)
    if type == 'mail':
        with open('logs/mail.log', 'a') as f:
            f.write(message + '\n')
    elif type == 'discord':
        with open('logs/discord.log', 'a') as f:
            f.write(message + '\n')
    else:
        with open('logs/unknown.log', 'a') as f:
            f.write(message + '\n')