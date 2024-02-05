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
        if ipaddress.ip_address(ip).is_private:
            print("Private IP address given.")
            return False
        if ipaddress.ip_address(ip):
            return True
    except:
        return False


def validate_primary(input: str) -> bool:
    """
    Validate if a given input is a domain or ip address.

    Parameters:
    - input (str): The domain or ip address to validate.

    Returns:
    - bool: True if the input is a domain or ip address, False if not.

    """
    if validate_domain(input) or validate_ip(input):
        return True
    else:
        return False  


def domain_to_ip(domain: str) -> str:
    try:
        #print("Trying to resolve domain {}.".format(domain))
        if validate_ip(domain):
            return domain
        ip = socket.gethostbyname(domain)
        #print("IP address for domain {} is {}.".format(domain, ip))
        if validate_ip(ip):
            return ip
        else:
            return False
    except:
        return False
    
    
def ip_to_domain(ip: str) -> str:
    try:
        #print("Trying to resolve ip {}.".format(ip))
        if validate_domain(ip):
            return ip
        domain = socket.gethostbyaddr(ip)[0]
        #print("Domain for ip {} is {}.".format(ip, domain))
        if validate_domain(domain):
            return domain
        else:
            return False
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
    if validate_domain(input):
        ip = domain_to_ip(input)
        if ip:
            return input, ip
        return False, False
    elif validate_ip(input):
        domain = ip_to_domain(input)
        if domain:
            return domain, input
        return False, False
    else:
        return False, False