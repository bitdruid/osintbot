import osintkit.helper as helper
import subprocess

def request(input):
    domain = helper.ip_to_domain(input)
    if not domain:
        return "N/A"
    
    nameservers = ['9.9.9.9', '1.1.1.1', '8.8.8.8', '208.67.222.222', '8.26.56.26']

    response = {}
    arecord = []
    aaaa_record = []
    for nameserver in nameservers:
        a_command = f"dig @{nameserver} {domain} A +short"
        aaaa_command = f"dig @{nameserver} {domain} AAAA +short"
        try:
            record = subprocess.check_output(a_command, shell=True, stderr=subprocess.DEVNULL, text=True)
            for ip in record.strip().split("\n"):
                if helper.validate_ip(ip):
                    arecord.append(ip)
            arecord = list(set(arecord))
            record = subprocess.check_output(aaaa_command, shell=True, stderr=subprocess.DEVNULL, text=True)
            for ip in record.strip().split("\n"):
                if helper.validate_ip(ip):
                    aaaa_record.append(ip)
            aaaa_record = list(set(aaaa_record))
        except Exception as e:
            print(e)
            pass
    response["A"] = arecord
    response["AAAA"] = aaaa_record

    return response if any(response.values()) else "N/A"

if __name__ == "__main__":
    from osintkit.main import main_template
    main_template(request)

