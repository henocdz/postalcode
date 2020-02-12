import json
from geopy.geocoders import GoogleV3
import concurrent.futures

MAPS_API_KEY = ""


STATES = {
    "AA": "Armed Forces Americas",
    "AE": "Armed Forces Middle East",
    "AK": "Alaska",
    "AL": "Alabama",
    "AP": "Armed Forces Pacific",
    "AR": "Arkansas",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "FM": "Federated Stated of Micronesia",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MH": "Marshall Islands",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MP": "Northern Mariana Islands",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "PW": "Palau",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VI": "Virgin Islands",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}

raw_us_postal_codes_file = "us_zipcodes.json"
us_addresses_output = "addresses_us.json"
us_city_timezones_file = "us_timezones.json"

with open(us_city_timezones_file, "r") as pc:
    TIME_ZONES = json.loads(pc.read())

with open(raw_us_postal_codes_file, "r") as usf:
    postal_codes = json.loads(usf.read())

    city_timezones = dict()
    state_timezones = dict()
    state_tzs = dict(PR="America/Puerto_Rico", VI="America/St_Thomas")

    last_pc = 0
    states = dict()
    cities = set()
    for i, (postal_code, info) in enumerate(postal_codes.items()):

        state_code = info["state"]
        state_name = STATES[state_code]
        raw_city_name = info["city"]
        city_name = " ".join([cc.capitalize() for cc in raw_city_name.split(" ")])

        state_data = states.setdefault(
            state_code, dict(code=state_code, name=state_name, cities={})
        )

        city_data = state_data["cities"].setdefault(
            city_name, dict(name=city_name, towns=[], time_zone=None, postal_codes=[]),
        )

        city_key = f"{city_name} {state_code}"
        cities.add(city_key)

        timezone = city_data.get("time_zone", None)
        if timezone is None:
            try:
                timezone = TIME_ZONES[city_key]
                if not timezone:
                    print(city_key)
            except KeyError:
                print(city_key)
                time_zone = "America/Denver"
            city_data["time_zone"] = timezone

        city_data["postal_codes"].append(postal_code)

        pc = round((i + 1) * 100 / 41697, 1)
        per = f"{pc}%"
        if pc > last_pc:
            last_pc = pc
            print(per)


# def get_timezone(city_key):
#     try:
#         geolocator = GoogleV3(api_key=MAPS_API_KEY, timeout=5)
#         location = geolocator.geocode(city_key)

#         tz = geolocator.reverse_timezone(location.point)
#         timezone = tz.raw["timeZoneId"]
#     except Exception:
#         timezone = ""

#     return timezone


# with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
#     fs = dict()
#     for city_key in cities:
#         if city_key not in TIME_ZONES:
#             fs[executor.submit(get_timezone, city_key=city_key)] = city_key

#     last_pc = 0
#     i = 0
#     for future in concurrent.futures.as_completed(fs):
#         city = fs[future]
#         tz = future.result()
#         if tz:
#             TIME_ZONES[city] = tz

#         pc = round((i + 1) * 100 / len(cities), 1)
#         per = f"{pc}%"
#         if pc > last_pc:
#             last_pc = pc
#         i += 1

# with open(us_city_timezones_file, "w") as tzoutput:
#     tzoutput.write(json.dumps(TIME_ZONES))


with open(us_addresses_output, "w") as output:
    for _, state in states.items():
        cities = list(state["cities"].values())
        state["cities"] = cities

    output.write(json.dumps(list(states.values()), ensure_ascii=True))
