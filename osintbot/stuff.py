import ipaddress
    
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