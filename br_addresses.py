import csv
import requests
import json

brazilian_ceps_file = "br_postalcodes.csv"

API_KEY = "RZBSUHER6MUY"


town_tzs = {}

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

        city_data = cities.setdefault(city_name, dict())

        time_zone = city_data.get("time_zone", None)
        if time_zone is None:
            if town_name in town_tzs:
                time_zone = town_tzs[town_name]
            else:
                # url = f"http://vip.timezonedb.com/v2.1/get-time-zone?key={API_KEY}&format=json&by=position&lat={lat}&lng={lng}"
                url = f"http://vip.timezonedb.com/v2.1/get-time-zone?country=BR&by=position&key={API_KEY}&format=json&fields=zoneName&lat={lat}&lng={lng}"
                response = requests.get(url)
                response_json = response.json()
                timezones = response_json
                zone_name = timezones.get("zoneName")
                time_zone = zone_name.replace("\\", "")
                town_tzs[town_name] = time_zone

        city_data["time_zone"] = time_zone
        city_data["name"] = city_name

        towns = city_data.setdefault("towns", [])

        cep_data = dict(name=town_name, postal_code=postal_code)
        towns.append(cep_data)

        pc = round((i + 1) * 100 / 1105714, 1)
        per = f"{pc}%"
        if pc > last_pc:
            last_pc = pc
            print(per)

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
