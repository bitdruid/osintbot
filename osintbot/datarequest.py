import osintkit.helper as kit_helper
import osintkit.whois as whois
import osintkit.geoip as geoip
import osintkit.iplookup as iplookup
import osintkit.arecord as arecord

def full_report(input):
    report_data = ""
    iplookup_data = f"<<<<<<<<<< IPLOOKUP DATA FOR {input} >>>>>>>>>>" + "\n\n" + kit_helper.json_to_string(iplookup.request(input))
    arecord_data = f"<<<<<<<<<< ARECORD DATA FOR {input} >>>>>>>>>>" + "\n\n" + kit_helper.json_to_string(arecord.request(input))
    geoip_data = f"<<<<<<<<<< GEOIP DATA FOR {input} >>>>>>>>>>" + "\n\n" + kit_helper.json_to_string(geoip.request(input))
    whois_data = f"<<<<<<<<<< WHOIS DATA FOR {input} >>>>>>>>>>" + "\n\n" + kit_helper.json_to_string(whois.request(input))
    report_data += iplookup_data + "\n" + arecord_data + "\n" + geoip_data + "\n" + whois_data
    return report_data