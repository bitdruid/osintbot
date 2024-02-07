import json
import argparse
import osintkit.whois as whois
import osintkit.geoip as geoip
import osintkit.iplookup as iplookup
import osintkit.arecord as arecord
import osintkit.helper as helper

def main():
    parser = argparse.ArgumentParser(description="OSINT Kit")
    required = parser.add_mutually_exclusive_group(required=True)

    required.add_argument("--whois", type=str, metavar="", help="Perform a whois lookup on a domain or IP address")
    required.add_argument("--iplookup", type=str, metavar="", help="Perform an IP lookup on a domain or IP address")
    required.add_argument("--geoip", type=str, metavar="", help="Perform a GeoIP lookup on a domain or IP address")
    required.add_argument("--arecord", type=str, metavar="", help="Perform an A record lookup on a domain")

    optional = parser.add_argument_group()
    optional.add_argument("-hr", "--human-readable", action="store_true", help="Print the output in human readable format")



    args = parser.parse_args()

    response = None
    if args:
        if args.whois:
            response = whois.request(args.whois)
        if args.iplookup:
            response = iplookup.request(args.iplookup)
        if args.arecord:
            response = arecord.request(args.arecord)
        if args.geoip:
            response = geoip.request(args.geoip)

        if response:
            if args.human_readable:
                print(helper.json_to_string(response))
            else:
                print(json.dumps(response, indent=4))
        else:
            print("No data available.")
    else:
        parser.print_help()
        print("Usage: osintkit --arg <domain/ip>")

if __name__ == "__main__":
    main()
