import email
import os.path


def request(input):
    if os.path.isfile(input):
        with open(input, "r") as f:
            header = email.message_from_file(f)
    else:
        header = email.message_from_string(input)
    if header:
        header = email.parser.HeaderParser().parsestr(str(header))
        received = header.get_all("Received")
        return received



if __name__ == "__main__":
    from pprint import pprint
    import sys
    script_name = sys.argv[0]
    if "help" in sys.argv or "-h" in sys.argv or "--help" in sys.argv:
        print(f"Usage: python3 {script_name} <string/file>")
        exit()

    if len(sys.argv) > 1:
        input = sys.argv[1]
        response = request(input)
        if response:
            pprint(response)
        else:
            print("No data available.")
    else:
        print(f"Usage: python3 {script_name} <string/file>")
