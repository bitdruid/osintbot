import osintkit.helper as helper
import dns.resolver

def request(input):
    domain = helper.ip_to_domain(input)
    if not domain:
        return "N/A"
    
    resolver = dns.resolver.Resolver()
    nameservers = ['9.9.9.9', '1.1.1.1', '8.8.8.8', '208.67.222.222', '76.67.19.19']

    response = {}
    arecord = []
    queries = 4
    for i in range(queries):
        for nameserver in nameservers:
            print(f"running nameserver: {nameserver}")
            resolver.nameserver = [nameserver]
            print(f"resolver: {resolver.nameserver}")
            try:
                record = [str(record) for record in resolver.resolve(domain, "A")]
                for rdata in record:
                    print(f"found A record: {rdata}")
                    arecord.append(str(rdata))
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                pass
    response["A"] = list(set(arecord))

    return response if any(response.values()) else "N/A"

if __name__ == "__main__":
    from osintkit.main import main_template
    main_template(request)

