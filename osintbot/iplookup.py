import requests
import helper

def iplookup(ip):
    """Query on ipinfo and return result for asn, isp, country."""
    ip_json = {}
    api_data = requests.get("http://ipinfo.io/" + ip + "/json")
    api_data = api_data.json()
    for key in api_data:
        if key == "country":
            ip_json["Country"] = api_data[key]
        elif key == "org":
            ip_json["ASN and ISP"] = api_data[key]
    return ip_json

def request(input):
    """Return iplookup data."""
    response = {}
    if helper.validate_domain(input):
        ip = helper.domain_to_ip(input)
        iplookup_data = iplookup(ip)
        if "ip" in iplookup_data:
            response["iplookup"] = iplookup_data
        return response
    elif helper.validate_ip(input):
        iplookup_data = iplookup(input)
        if "ip" in iplookup_data:
            response["iplookup"] = iplookup_data
        return response
    else:
        return response
    
if __name__ == "__main__":
    from pprint import pprint
    import sys
    if len(sys.argv) > 1:
        input = sys.argv[1]
        response = request(input)
        if response:
            pprint(response)
        else:
            print("No data available.")
    else:
        print("Usage: python3 iplookup.py <domain/ip>")

