import requests
import osintkit.helper as helper

api_dict = {
    "ipwho.is": "http://ipwho.is/{ip}?output=json",
    "ipapi.com": "http://ip-api.com/json/{ip}",
    "ipapi.co": "http://ipapi.co/{ip}/json/",
    "freegeoip.live": "http://freegeoip.live/json/{ip}",
    #"hackertarget.com": "https://api.hackertarget.com/ipgeo/?q={ip}",
}

def query_api(api, ip):
    """Query an API with the given IP. API string format: http://example.com/{placeholder}/otherstuff"""
    api_url = api_dict[api].format(ip=ip)
    user_agent = "Mozilla/5.0" # some APIs require a user agent else they block the request
    api_data = requests.get(api_url, headers={"User-Agent": user_agent})
    if api_data.status_code == 200:
        return api_data.json()
    else:
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
    for value in json_response:
        if value in valid_keys:
            filtered_response[value] = json_response[value]
        elif value in rename_keys:
            filtered_response[rename_keys[value]] = json_response[value]
    return filtered_response





def convert_coords_to_url(json_response):
    """Add a link to opentopomap by latitude and longitude for each response."""
    topo_url = "https://opentopomap.org/#marker=7/{latitude}/{longitude}"
    topo_url = topo_url.format(latitude=json_response["latitude"], longitude=json_response["longitude"])
    del json_response["latitude"]
    del json_response["longitude"]
    # sort keys alphabetically and append url
    json_response = {key: json_response[key] for key in sorted(json_response.keys())}
    json_response["url"] = topo_url
    return json_response





def request(input):
    """Request data from all APIs, build json response and hand over."""
    domain, ip = helper.get_primary(input)
    if not ip:
        return None
    response = {}
    result = {}
    for api in api_dict:
        api_data = query_api(api, ip)
        api_data = filter_response(api_data)
        api_data = convert_coords_to_url(api_data)
        if "country" in api_data:
            response[api] = api_data
    result["geoip"] = response
    return result





if __name__ == "__main__":
    from pprint import pprint
    import sys
    script_name = sys.argv[0]
    if "help" in sys.argv or "-h" in sys.argv or "--help" in sys.argv:
        print(f"Usage: python3 {script_name} <domain/ip>")
        exit()

    if len(sys.argv) > 1:
        input = sys.argv[1]
        response = request(input)
        if response:
            pprint(response)
        else:
            print("No data available.")
    else:
        print(f"Usage: python3 {script_name} <domain/ip>")
