import argparse
import whois
import iplookup
from pprint import pprint

def main():
    parser = argparse.ArgumentParser(description="OSINT Kit")
    subparsers = parser.add_subparsers(dest="command")

    whois_parser = subparsers.add_parser("whois", help="Perform a whois lookup on a domain")
    whois_parser.add_argument("input", help="Domain name to lookup")

    iplookup_parser = subparsers.add_parser("iplookup", help="Perform an IP lookup on a domain or IP address")
    iplookup_parser.add_argument("input", help="Domain name or IP address to lookup")

    args = parser.parse_args()

    if args.command == "whois":
        response = whois.request(args.input)
        if response:
            pprint(response)
        else:
            pprint("No data available.")
    elif args.command == "iplookup":
        response = iplookup.request(args.input)
        if response:
            pprint(response)
        else:
            pprint("No data available.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
