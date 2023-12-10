import ipaddress
import socket
import requests

def check_online_offline(domain):
    """check if a domain is online or offline"""
    try:
        response_code = requests.get(domain).status_code
        if response_code == 200:
            return True
        else:
            return False
    except:
        return False
    
    
def validate_domain(domain):
    """validate if a domain is given"""
    try:
        ipaddress.ip_address(domain)
        return False
    except:
        pass
    domain_parts = domain.split(".")
    if len(domain_parts) > 1:
        if len(domain_parts[-1]) > 1:
            return True
        else:
            return False
    else:
        return False
    
def validate_ip(ip):
    """validate if an ip is given"""
    try:
        ipaddress.ip_address(ip)
        return True
    except:
        return False
    
def domain_to_ip(domain):
    """convert a domain to an ip or return dump ip"""
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except:
        return "0.0.0.0"
    
def ip_to_domain(ip):
    """convert an ip to a domain or return dump domain"""
    try:
        domain = socket.gethostbyaddr(ip)[0]
        return domain
    except:
        return False