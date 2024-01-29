import os
import helper
            
def whois(domain):
    """whois ip/domain"""
    whois_data = os.popen("whois " + domain).read().lower()
    if "domain name:" in whois_data or "netname:" in whois_data:
        return whois_data
    return False
    
def whois_registrar(domain):
    """get registrar information from domain"""
    whois_data = whois(domain).lower()
    if whois_data is not False and "registrar:" in whois_data:
        return whois_data.split("registrar:")[1].split("\n")[0].strip()
    return False

def request(input):
    response = {}
    if helper.validate_domain(input) or helper.validate_ip(input):
        whois_data = whois(input)
        if whois_data:
            response["whois"] = whois_data
        if response:
                return response
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
        print("Usage: python3 whois.py <ip/domain>")