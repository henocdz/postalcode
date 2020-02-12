# import csv
# import requests
import json

us_zipcodes_json = "addresses_us.json"
brazilian_cps_json = "addresses_br.json"
mexican_cps_json = "addresses_mx.json"
output_json = "addresses.json"

with open(brazilian_cps_json, "r") as br, open(us_zipcodes_json, "r") as us, open(
    mexican_cps_json, "r"
) as mx, open(output_json, "w+") as output:
    br_json = json.loads(br.read())
    mx_json = json.loads(mx.read())
    us_json = json.loads(us.read())

    br_output = dict(name="Brazil", code="BR", states=br_json)
    us_output = dict(name="United States", code="US", states=us_json)
    mx_json.append(br_output)
    mx_json.append(us_output)

    output.write(json.dumps(mx_json, ensure_ascii=True))
