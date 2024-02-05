
def json_to_string(json):
    message = ""
    for key, value in json.items():
        heading = f"{key}:\n"
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                message += f"{subkey}: {subvalue}\n"
        else:
            message += f"{value}\n"
        message += heading
    return message + "\n"