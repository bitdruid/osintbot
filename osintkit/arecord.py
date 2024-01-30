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
    domain = helper.ip_to_domain(input)
    response = {}
    result = {}
    
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
        a_records = resolver.resolve(domain, "A")
        a_records = [str(record) for record in a_records]
        response["A"] = a_records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        a_records = []

    try:
        aaaa_records = resolver.resolve(domain, "AAAA")
        aaaa_records = [str(record) for record in aaaa_records]
        response["AAAA"] = aaaa_records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        aaaa_records = []

    result["arecord"] = response
    if response:
        return result
    else:
        return False





if __name__ == "__main__":
    from pprint import pprint
    import sys
    script_name = sys.argv[0]
    if "help" in sys.argv or "-h" in sys.argv or "--help" in sys.argv:
        print(f"Usage: python3 {script_name} <domain/ip>")
        exit()

    if len(sys.argv) > 1:
        input = sys.argv[1]
        response = request(input)
        if response:
            pprint(response)
        else:
            print("No data available.")
    else:
        print(f"Usage: python3 {script_name} <domain/ip>")
