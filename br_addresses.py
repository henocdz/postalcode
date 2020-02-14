import sys
import csv
import requests
import json

brazilian_ceps_file = "br_postalcodes.csv"
brazil_timezones_file = "br_timezones.json"

API_KEY = "RZBSUHER6MUY"


with open(brazil_timezones_file, "r") as f:
    try:
        town_timezones = json.loads(f.read())
    except json.decoder.JSONDecodeError:
        town_timezones = {}

with open(brazilian_ceps_file, "r") as cfile:
    csv_reader = csv.reader(cfile)
    csv_headers = next(csv_reader)
    addresses_aggr = dict()
    last_pc = 0

    for i, line in enumerate(csv_reader):
        state_name, state_code, city_name, town_name, postal_code, lat, lng = line
        state_data = addresses_aggr.setdefault(state_name, dict())

        state_data["code"] = state_code
        state_data["name"] = state_name
        cities = state_data.setdefault("cities", dict())

        city_data = cities.setdefault(city_name, dict(name=city_name))

        timezone = city_data.get("timezone", None)
        if timezone is None:
            if town_name in town_timezones:
                timezone = town_timezones[town_name]
            else:
                # url = f"http://vip.timezonedb.com/v2.1/get-time-zone?key={API_KEY}&format=json&by=position&lat={lat}&lng={lng}"
                url = f"http://vip.timezonedb.com/v2.1/get-time-zone?country=BR&by=position&key={API_KEY}&format=json&fields=zoneName&lat={lat}&lng={lng}"
                response = requests.get(url)
                response_json = response.json()
                timezones = response_json
                zone_name = timezones.get("zoneName")
                timezone = zone_name.replace("\\", "")
                town_timezones[town_name] = timezone

            city_data["timezone"] = timezone

        towns = city_data.setdefault("towns", [])

        if postal_code == "01418200":
            print(line)

        cep_data = dict(name=town_name, postal_code=postal_code)
        towns.append(cep_data)

        pc = round((i + 1) * 100 / 1105714, 1)
        per = f"{pc}%"
        if pc > last_pc:
            last_pc = pc
            sys.stdout.write(f"{per}   \r")
            sys.stdout.flush()

addresses = []
for state_name, state_data in addresses_aggr.items():
    cities_aggr = state_data.pop("cities", {})
    cities = []
    for city_name, city_data in cities_aggr.items():
        cities.append(city_data)

    state_data["cities"] = cities

    addresses.append(state_data)

with open("addresses_br.json", "w") as afile:
    afile.write(json.dumps(addresses, ensure_ascii=True))


with open(brazil_timezones_file, "w") as tzfile:
    tzfile.write(json.dumps(town_timezones, ensure_ascii=True))
