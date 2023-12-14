import requests
import helper

api_dict = {
    "ipwho.is": "http://ipwho.is/{ip}?output=json",
    "ipapi.com": "http://ip-api.com/json/{ip}",
    "ipapi.co": "https://ipapi.co/{ip}/json/",
    "freegeoip.live": "https://freegeoip.live/json/{ip}",
    #"hackertarget.com": "https://api.hackertarget.com/ipgeo/?q={ip}",
}

def query_api(api, ip):
    """Query an API with the given IP. API string format: http://example.com/{placeholder}/otherstuff"""
    api_url = api_dict[api].format(ip=ip)
    try:
        user_agent = "Mozilla/5.0" # some APIs require a user agent else they block the request
        api_data = requests.get(api_url, headers={"User-Agent": user_agent})
        if api_data.status_code == 200:
            return api_data.json()
        else:
            api_data = "API request failed: {api_url} - Response code: {response_code}".format(api_url=api_url, response_code=api_data.status_code)
            return api_data
    except:
        api_data = "API request failed: {api_url}".format(api_url=api_url)
        return api_data





def filter_response(json_response):
    """Filter the response for the most relevant data."""
    valid_keys = [
        "country",
        "region",
        "state",
        "city",
        "latitude",
        "longitude"
    ]
    rename_keys = {
        "country_name": "country",
        "region_name": "region",
        "lat": "latitude",
        "lon": "longitude",
    }
    filtered_response = {}
    for api in json_response:
        filtered_response[api] = {}
        for key in json_response[api]:
            if key in valid_keys:
                filtered_response[api][key] = json_response[api][key]
            elif key in rename_keys:
                filtered_response[api][rename_keys[key]] = json_response[api][key]
    return filtered_response





def convert_coords_to_url(json_response):
    """Add a link to opentopomap by latitude and longitude for each response."""
    topo_url = "https://opentopomap.org/#marker=7/{latitude}/{longitude}"
    for api in json_response:
        try:
            json_response[api]["url"] = topo_url.format(latitude=json_response[api]["latitude"], longitude=json_response[api]["longitude"])
        except:
            pass
    return json_response





def request(input):
    """Request data from all APIs, build json response and hand over."""

    if helper.validate_ip(input):
        ip = input
    elif helper.validate_domain(input):
        ip = helper.domain_to_ip(input)
    else:
        return False
    
    response = {}
    result = {}
    for api in api_dict:
        api_data = query_api(api, ip)
        if api_data:
            response[api] = api_data
    response = filter_response(response)
    response = convert_coords_to_url(response)
    result["geoip"] = response
    return result





if __name__ == "__main__":
    from pprint import pprint
    import sys

    if "help" in sys.argv or "-h" in sys.argv or "--help" in sys.argv:
        print("Usage: python3 geoip.py <domain/ip>")
        exit()

    if len(sys.argv) > 1:
        input = sys.argv[1]
        response = request(input)
        if response:
            pprint(response)
        else:
            print("No data available.")

    else:
        print("Usage: python3 geoip.py <domain/ip>")