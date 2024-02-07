import os
import osintkit.helper as helper
            
def whois(domain: str) -> str:
    """whois ip/domain"""
    whois_data = os.popen("whois " + domain).read().lower()
    if "domain name:" in whois_data or "netname:" in whois_data:
        #whois_data = [line.strip() for line in whois_data.split("\n") if line.strip() != ""]
        return whois_data
    return False
domain: str
def whois_status(domain: str, whois_data=None):
    """get domain status entries"""
    return whois_search_term(domain, "domain status:", whois_data, all=True)

def whois_creation_date(domain: str, whois_data=None) -> str:
    """get creation date from domain"""
    return whois_search_term(domain, "creation date:", whois_data)

def whois_registrar(domain: str, whois_data=None) -> str:
    """get registrar information from domain"""
    return whois_search_term(domain, "registrar:", whois_data)

def whois_organization(domain: str, whois_data=None) -> str:
    """get organization information from domain"""
    return whois_search_term(domain, "organization:", whois_data)

# def whois_search_term(domain: str, term: str, whois_data=None, all=False) -> str:
#     """search for a specific term in the whois data"""
#     terms = []
#     if whois_data is None:
#         whois_data = whois(domain)
#     if whois_data is not False:
#         for line in whois_data:
#             if term in line:
#                 terms.append(line.split(term)[1].strip())
#         if all:
#             return list(set(terms))
#         else:
#             #return [terms[0]] if terms else []
#             return terms[0] if terms else "N/A"
#     return False

def whois_search_term(domain: str, term: str, whois_data=None, all=False) -> str:
    """search for a specific term in the whois data"""
    terms = []
    if whois_data is None:
        whois_data = whois(domain)
    if whois_data is not False and term in whois_data:
        if all:
            for line in whois_data.split("\n"):
                if term in line:
                    terms.append(line.split(term)[1].strip())
            return list(set(terms))
        else:
            orga = whois_data.split(term)[1].split("\n")[0].strip()
            if orga != "": return orga
            return "N/A"
    return "N/A"

def request(domain: str) -> dict:
    response = {}
    if helper.validate_primary(domain):
        whois_data = whois(domain)
        if whois_data:
            #response["domain"] = [domain]
            response["creation_date"] = whois_creation_date(domain, whois_data)
            response["registrar"] = whois_registrar(domain, whois_data)
            response["organization"] = whois_organization(domain, whois_data)
            response["whois"] = whois_data
            return response
        else:
            return "N/A"
    



    
if __name__ == "__main__":
    import sys
    import json
    script_name = sys.argv[0]
    if "help" in sys.argv or "-h" in sys.argv or "--help" in sys.argv:
        print(f"Usage: python3 {script_name} <domain/ip>")
        exit()

    if len(sys.argv) > 1:
        input = sys.argv[1]
        response = request(input)
        response = json.dumps(response, indent=4)
        print(response)
    else:
        print(f"Usage: python3 {script_name} <domain/ip>")
