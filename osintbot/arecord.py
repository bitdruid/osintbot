import socket
import helper

def request(input):
    """Returns a list of A records for a domain."""
    domain, ip = helper.get_primary(input)
    try:
        a_records = socket.gethostbyname_ex(domain)[2]
        return a_records
    except:
        return False

if __name__ == "__main__":
    from pprint import pprint
    import sys
    if len(sys.argv) > 1:
        input = sys.argv[1]
        response = request(input)
        if response:
            pprint(response)
        else:
            print("No data available.")
    else:
        print("Usage: python3 arecords.py <domain/ip>")
