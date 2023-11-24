import sys
import os
import socket
import requests
import stuff
            
def whois(domain):
    """whois domain"""
    whois_data = os.popen("whois " + domain).read()
    if "Domain Name:" in whois_data:
        return whois_data
    else:
        return False
    
def whois_hosting(domain, whois_data):
    """get hosting information from domain"""
    stats = {}
    try:
        ipv4 = socket.gethostbyname(domain)
        stats["ipv4"] = ipv4
    except:
        return False
    else:
        try:
            ipv6 = socket.getaddrinfo(domain, None, socket.AF_INET6)[0][4][0]
            stats["ipv6"] = ipv6
        except:
            pass
        ip_json = requests.get("http://ipinfo.io/" + ipv4 + "/json")
        ip_json = ip_json.json()
        for key in ip_json:
            if key == "hostname":
                stats["hostname"] = ip_json[key]
            elif key == "org":
                stats["organization"] = ip_json[key]
        if whois_data is not False and "Registrar:" in whois_data:
            stats["domain-registrar"] = whois_data.split("Registrar:")[1].split("\n")[0].strip()
        return stats

def run(input):
    response = {}
    if stuff.validate_domain(input):
        whois_data = whois(input)
        if whois_data:
            response["whois"] = whois_data
        stats = whois_hosting(input, whois_data)
        if stats:
            response["stats"] = stats
        if response:
                return response
    return False
    
if __name__ == "__main__":
    from pprint import pprint
    if len(sys.argv) > 1:
        stuff = sys.argv[1]
        response = run(stuff)
        pprint(response)
    else:
        print("Usage: python3 whois.py <domain>")