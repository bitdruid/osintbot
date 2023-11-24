#!bin/bash

# path of the script
SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TARGET_PATH="$SCRIPT_PATH/.."
echo "Preparing virtual environment in $TARGET_PATH"
# Create a virtual environment
if [ ! -d "..$SCRIPT_PATH/.venv" ]; then
    python3 -m venv "$TARGET_PATH/.venv"
fi

# update pip
"$TARGET_PATH/.venv/bin/python" -m pip install --upgrade pip

# install stuff
"$TARGET_PATH/.venv/bin/python" -m pip install python-telegram-bot --upgrade
"$TARGET_PATH/.venv/bin/python" -m pip install flask --upgrade
"$TARGET_PATH/.venv/bin/python" -m pip install requests --upgrade