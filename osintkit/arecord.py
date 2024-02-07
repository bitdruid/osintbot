import osintkit.helper as helper
import dns.resolver





def request(input: str) -> str:
    """
    Performs a DNS query for A and AAAA records of a given domain.

    Parameters:
    - input (str): The domain or IP address to query.

    Returns:
    - str: A JSON string containing the A and AAAA records of the domain, or False if no records are found.

    """
    if not (domain := helper.ip_to_domain(input)):
        return False
    arecords = []
    response = {}

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
    
    try:
        arecords = resolver.resolve(domain, "A")
        arecords = [str(record) for record in arecords]
        a_str = "\n".join(arecords)
        response["A"] = a_str
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        response["A"] = "N/A"

    try:
        aaaa_records = resolver.resolve(domain, "AAAA")
        aaaa_records = [str(record) for record in aaaa_records]
        aaaa_str = "\n".join(aaaa_records)
        response["AAAA"] = aaaa_str
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        response["AAAA"] = "N/A"

    return response





if __name__ == "__main__":
    import sys
    import json
    script_name = sys.argv[0]
    if "help" in sys.argv or "-h" in sys.argv or "--help" in sys.argv:
        print(f"Usage: python3 {script_name} <domain/ip>")
        exit()

    if len(sys.argv) > 1:
        input = sys.argv[1]
        response = request(input)
        response = json.dumps(response, indent=4)
        print(response)
    else:
        print(f"Usage: python3 {script_name} <domain/ip>")
