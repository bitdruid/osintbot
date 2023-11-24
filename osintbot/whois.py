import sys
import os
import ipaddress
import socket
import requests

def check_domain(domain):
    """check if domain or ip"""
    try:
        ipaddress.ip_address(domain)
        return False
    except:
        return True
    
def validate_domain(domain):
    """validate if domain has the correct format"""
    domain_parts = domain.split(".")
    if len(domain_parts) > 1:
        if len(domain_parts[-1]) > 1:
            return True
        else:
            return False
    else:
        return False
            
def whois(domain):
    """whois domain"""
    try:
        whois_data = os.popen("whois " + domain).read()
        if "Domain Name:" in whois_data:
            return whois_data
        else:
            return False
    except:
        return False
    
def hosting_domain(whois_data):
    """get hosting information from domain"""
    stats = {}
    domain = whois_data.split("Domain Name:")[1].split("\n")[0].strip()
    if domain:
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
            if "Registrar:" in whois_data:
                stats["domain-registrar"] = whois_data.split("Registrar:")[1].split("\n")[0].strip()
            return stats

def run(domain):
    response = {}
    if check_domain(domain):
        if validate_domain(domain):
            whois_data = whois(domain)
            if whois_data:
                response["whois"] = whois_data
                stats = hosting_domain(whois_data)
                if stats:
                    response["stats"] = stats
                return response
            else:
                return False
    else:
        return False