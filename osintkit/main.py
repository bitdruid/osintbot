import argparse
import whois
import geoip
import iplookup
import arecord
from pprint import pprint

def main():
    parser = argparse.ArgumentParser(description="OSINT Kit")
    required = parser.add_mutually_exclusive_group(required=True)

    required.add_argument("-w", "--whois", action="store_true", help="Perform a whois lookup on a domain")
    required.add_argument("-i", "--iplookup", action="store_true", help="Perform an IP lookup on a domain or IP address")
    required.add_argument("-g", "--geoip", action="store_true", help="Perform a GeoIP lookup on a domain or IP address")
    required.add_argument("-a", "--arecord", action="store_true", help="Perform an A record lookup on a domain")



    args = parser.parse_args()

    response = None
    if args.command:
        if args.whois:
            response = whois.request(args.input)
        if args.iplookup:
            response = iplookup.request(args.input)
        if args.arecord:
            response = arecord.request(args.input)


        if response:
            pprint(response)
        else:
            pprint("No data available.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
