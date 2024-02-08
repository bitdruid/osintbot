import requests
import socket
import osintkit.helper as helper
import osintkit.whois as whois

def iplookup(ip, domain):
    """Query on ipinfo."""
    ip_json = {}
    try:
        ip_json["primary ipv4"] = ip
        ip_json["primary ipv6"] = socket.getaddrinfo(ip, None, socket.AF_INET6)[0][4][0]
    except:
        pass
    api_data = requests.get(f"http://ipinfo.io/{ip}/json").json()
    if "hostname" in api_data:
        ip_json["Hostname"] = api_data["hostname"]
    if "country" in api_data:
        ip_json["Country"] = api_data["country"]
    if "org" in api_data:
        ip_json["ASN and ISP"] = api_data["org"]
    registrar = whois.request(domain)["registrar"]
    if registrar:
        ip_json["Domain Registrar"] = registrar
    return ip_json if ip_json else "N/A"

def request(input):
    """Return iplookup data."""
    domain, ip = helper.get_primary(input)
    if not domain or not ip:
        return "N/A"
    return iplookup(ip, domain) or "N/A"

if __name__ == "__main__":
    from osintkit.main import main_template
    main_template(request)
