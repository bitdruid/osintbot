import argparse
import osintkit.whois as whois
import osintkit.geoip as geoip
import osintkit.iplookup as iplookup
import osintkit.arecord as arecord
from pprint import pprint

def main():
    parser = argparse.ArgumentParser(description="OSINT Kit")
    required = parser.add_mutually_exclusive_group(required=True)

    required.add_argument("--whois", type=str, metavar="", help="Perform a whois lookup on a domain or IP address")
    required.add_argument("--iplookup", type=str, metavar="", help="Perform an IP lookup on a domain or IP address")
    required.add_argument("--geoip", type=str, metavar="", help="Perform a GeoIP lookup on a domain or IP address")
    required.add_argument("--arecord", type=str, metavar="", help="Perform an A record lookup on a domain")



    args = parser.parse_args()

    response = None
    if args:
        if args.whois:
            response = whois.request(args.whois)
        if args.iplookup:
            response = iplookup.request(args.iplookup)
        if args.arecord:
            response = arecord.request(args.arecord)


        if response:
            pprint(response)
        else:
            pprint("No data available.")
    else:
        parser.print_help()
        pprint("Usage: osintkit --arg <domain/ip>")

if __name__ == "__main__":
    main()
