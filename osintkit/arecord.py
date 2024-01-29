import helper
import dns.resolver
import json

def request(input: str) -> str:
    domain = helper.ip_to_domain(input)
    response = {}
    result = {}
    
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
        a_records = resolver.resolve(domain, "A")
        a_records = [str(record) for record in a_records]
        result["A"] = a_records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        a_records = []

    try:
        aaaa_records = resolver.resolve(domain, "AAAA")
        aaaa_records = [str(record) for record in aaaa_records]
        result["AAAA"] = aaaa_records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        aaaa_records = []

    response["arecord"] = result
    if response:
        return json.dumps(response)
    else:
        return False

if __name__ == "__main__":
    from pprint import pprint
    import sys
    script_name = sys.argv[0]
    if len(sys.argv) > 1:
        input = sys.argv[1]
        response = request(input)
        if response:
            pprint(response)
        else:
            print("No data available.")
    else:
        print(f"Usage: python3 {script_name} <domain/ip>")
