import requests
import socket
import helper
import whois

def iplookup(ip, domain):
    """Query on ipinfo and return result for asn, isp, country."""
    ip_json = {}
    ip_json["ipv4"] = ip
    try:
        ip_json["ipv6"] = socket.getaddrinfo(ip, None, socket.AF_INET6)[0][4][0]
    except:
        pass
    api_data = requests.get("http://ipinfo.io/" + ip + "/json")
    api_data = api_data.json()
    for key in api_data:
        if key == "hostname":
            ip_json["Hostname"] = api_data[key]
        if key == "country":
            ip_json["Country"] = api_data[key]
        elif key == "org":
            ip_json["ASN and ISP"] = api_data[key]
    registrar = whois.whois_registrar(domain)
    if registrar:
        ip_json["Domain Registrar"] = registrar
    ip_json["Data Source"] = "According to API data from ipinfo.io"
    return ip_json

def request(input):
    """Return iplookup data."""
    response = {}
    if helper.validate_domain(input):
        ip = helper.domain_to_ip(input)
        domain = input
    if helper.validate_ip(input):
        ip = input
        domain = helper.ip_to_domain(input)
    iplookup_data = iplookup(ip, domain)
    if "ipv4" in iplookup_data:
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

