import requests
import socket
import osintkit.helper as helper
import osintkit.whois as whois

def iplookup(ip, domain):
    """Query on ipinfo and return result for asn, isp, country."""
    ip_json = {}
    ip_json["primary ipv4"] = ip
    try:
        ip_json["primary ipv6"] = socket.getaddrinfo(ip, None, socket.AF_INET6)[0][4][0]
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
    return ip_json

def request(input):
    """Return iplookup data."""
    domain, ip = helper.get_primary(input)
    if not domain or not ip:
        return {}
    response = {}
    iplookup_data = iplookup(ip, domain)
    if "primary ipv4" in iplookup_data:
        response["iplookup"] = iplookup_data
        return response
    else:
        return response
    



    
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

