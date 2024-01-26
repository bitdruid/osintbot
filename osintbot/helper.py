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
    
import socket

def domain_to_ip(domain: str) -> str:
    try:
        if validate_ip(domain):
            return domain
        ip = socket.gethostbyname(domain)
        return ip
    except:
        return False
    
def ip_to_domain(ip: str) -> str:
    try:
        if validate_domain(ip):
            return ip
        domain = socket.gethostbyaddr(ip)[0]
        return domain
    except:
        return False
    
def get_primary(input: str) -> tuple:
    """
    Returns the primary domain and ip for a given domain or ip.

    Parameters:
    - domain (str): The domain to check.

    Returns:
    - tuple: [0] domain, [1] ip
    - bool: False, False if no domain or ip is given

    """
    print(f"get_primary({input})")
    if validate_domain(input):
        return input, domain_to_ip(input)
    elif validate_ip(input):
        return ip_to_domain(input), input
    else:
        return False, False