import os
import sys
from datetime import datetime

def exception(type: str, message: str, e: Exception) -> None:
    tb_last_line = sys.exc_info()[-1]
    while tb_last_line.tb_next:
        tb_last_line = tb_last_line.tb_next
    log(type, f"!-- Error message: {message}")
    log(type, f"!-- Error file: {tb_last_line.tb_frame.f_code.co_filename}")
    log(type, f"!-- Error function: {tb_last_line.tb_frame.f_code.co_name}")
    log(type, f"!-- Error line: {tb_last_line.tb_lineno}")
    log(type, f"!-- Error stacktrace: {e}")

def log(type: str, message: str) -> None:
    message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {type.upper()} - {message}"
    print(message)
    sys.stdout.flush() # flush stdout buffer before threads are joined
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