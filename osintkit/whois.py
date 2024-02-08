import os
import osintkit.helper as helper

def whois(domain: str) -> str:
    """Retrieve whois data for a domain"""
    whois_data = os.popen("whois " + domain).read().lower()
    return whois_data if any(term in whois_data for term in ["domain name:", "netname:"]) else False

def whois_search_term(domain: str, term: str, whois_data=None, all=False) -> str:
    """Search for a specific term in the whois data"""
    terms = []
    if whois_data is None:
        whois_data = whois(domain)
    if whois_data is not False and term in whois_data:
        if all:
            terms = [line.split(term)[1].strip() for line in whois_data.split("\n") if term in line]
            return list(set(terms))
        else:
            term = whois_data.split(term)[1].split("\n")[0].strip()
            return term if term else "N/A"
    return "N/A"

def request(domain: str) -> dict:
    if not helper.validate_primary(domain):
        return "N/A"

    whois_data = whois(domain)
    if not whois_data:
        return "N/A"

    return {
        "creation_date": whois_search_term(domain, "creation date:", whois_data),
        "registrar": whois_search_term(domain, "registrar:", whois_data),
        "organization": whois_search_term(domain, "organization:", whois_data),
        "whois": whois_data
    }

if __name__ == "__main__":
    from osintkit.main import main_template
    main_template(request)
