#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from sqlalchemy import String, Integer, Float
from sqlalchemy import create_engine, MetaData, Table, Column, Index
from sqlalchemy import select
try:
    from cazipcode.pkg.superjson import json
    from cazipcode.pkg.fuzzywuzzy import process
except:
    from ..pkg.superjson import json
    from ..pkg.fuzzywuzzy import process


class fields:
    postalcode = "postalcode"
    city = "city"
    province = "province"
    area_code = "area_code"
    area_name = "area_name"
    latitude = "latitude"
    longitude = "longitude"
    elevation = "elevation"
    population = "population"
    dwellings = "dwellings"
    timezone = "timezone"
    day_light_savings = "day_light_savings"


# define table
metadata = MetaData()
t = Table("canada_postalcode", metadata,
          Column(fields.postalcode, String, primary_key=True),
          Column(fields.city, String),
          Column(fields.province, String),
          Column(fields.area_code, Integer),
          Column(fields.area_name, String),
          Column(fields.latitude, Float),
          Column(fields.longitude, Float),
          Column(fields.elevation, Integer),
          Column(fields.population, Integer),
          Column(fields.dwellings, Integer),
          Column(fields.timezone, Integer),
          Column(fields.day_light_savings, Integer),
          )


db_file = "data.sqlite"
db_path = os.path.join(os.path.dirname(__file__), db_file)

# if exists
if os.path.exists(db_path):
    engine = create_engine("sqlite:///%s" % db_path)

# if not exists, create the database
else:
    postalcode_data = json.load("canada_postcode.json.gz", verbose=False)
    postalcode_data = sorted(postalcode_data, key=lambda p: p["postalcode"])
    # try to create a database file locally.
    try:
        engine = create_engine("sqlite:///%s" % db_path)
        metadata.create_all(engine)
        engine.execute(t.insert(), postalcode_data)

    # if meet permission error, use in-memory database.
    except:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        engine.execute(t.insert(), postalcode_data)

    i_city = Index("c_city", t.c.city)
    i_city.create(engine)

    i_province = Index("c_province", t.c.province)
    i_province.create(engine)

    i_latitude = Index("c_latitude", t.c.latitude)
    i_latitude.create(engine)

    i_longitude = Index("c_longitude", t.c.longitude)
    i_longitude.create(engine)

    i_population = Index("c_population", t.c.population)
    i_population.create(engine)

    i_dwellings = Index("c_dwellings", t.c.dwellings)
    i_dwellings.create(engine)

    i_timezone = Index("c_timezone", t.c.timezone)
    i_timezone.create(engine)

#
province_short_to_long = {
    "NL": "Newfoundland and Labrador",
    "NS": "Nova Scotia",
    "PE": "Prince Edward Island",
    "NB": "New Brunswick",
    "QC": "Quebec",
    "ON": "Ontario",
    "MB": "Manitoba",
    "SK": "Saskatchewan",
    "AB": "Alberta",
    "BC": "British Columbia",
    "NU": "Nunavut",
    "NT": "Northwest Territories",
    "YT": "Yukon",
}
province_long_to_short = {
    long: short for short, long in province_short_to_long.items()}
province_long_to_short_upper = {
    long.upper(): short for short, long in province_short_to_long.items()}

all_province_short = set(province_short_to_long)
all_province_long = set(province_long_to_short)
all_province_short_and_long = {
    province.upper() for province in set.union(all_province_short, all_province_long)}

sql = select([t.c.city.distinct()])
all_city = {row["city"] for row in engine.execute(sql) if row["city"]}
city_long_to_long_upper = {city.upper(): city for city in all_city}

sql = select([t.c.area_name.distinct()])
all_area_name = {
    row["area_name"] for row in engine.execute(sql) if row["area_name"]}
area_name_long_to_long_upper = {
    area_name.upper(): area_name for area_name in all_area_name}


def fuzzy_match(text, choices, best_match=False, min_confidence=70):
    """

    """
    result = list()
    if best_match:
        choice, confidence = process.extractOne(text, choices)
#         print(choice, confidence)
        if confidence >= min_confidence:
            result.append(choice)

    else:
        for choice, confidence in process.extract(text, choices):
            #             print(choice, confidence)
            if confidence >= min_confidence:
                result.append(choice)

    return result


def find_province(text, best_match=True):
    result = list()

    text = text.strip()
    if len(text) < 2:
        message = ("'%s' is not a valid province name, use 2 letter "
                   "short name or correct full name please.")
        raise ValueError(message % text)

    # check if it is a abbreviate name
    # or the name is exactly right
    upper = text.upper()
    if upper in all_province_short_and_long:
        return [province_long_to_short_upper.get(upper, upper), ]

    # use fuzzy match
    result = fuzzy_match(
        text, all_province_long, best_match, min_confidence=70)

    if len(result) == 0:
        message = ("'%s' is not a valid province name, use 2 letter "
                   "short name or correct full name please.")
        raise ValueError(message % text)
    else:
        result = [province_long_to_short[long] for long in result]
        return result


def find_city(text, best_match=True):
    if text.upper() in city_long_to_long_upper:
        return [city_long_to_long_upper[text.upper()], ]

    result = fuzzy_match(text, all_city, best_match, min_confidence=70)

    if len(result) == 0:
        message = ("'%s' is not a valid city name, "
                   "use correct full name please.")
        raise ValueError(message % text)
    else:
        return result


def find_area_name(text, best_match=True):
    if text.upper() in area_name_long_to_long_upper:
        return [area_name_long_to_long_upper[text.upper()], ]

    result = fuzzy_match(text, all_area_name, best_match, min_confidence=70)

    if len(result) == 0:
        message = ("'%s' is not a valid city name, "
                   "use correct full name please.")
        raise ValueError(message % text)
    else:
        return result


if __name__ == "__main__":
    assert find_province("on") == ["ON"]
    assert find_province("ontario") == ["ON"]
    assert find_province("tario") == ["ON"]

    assert find_city("ottawa") == ["Ottawa", ]
    assert find_city("otawa") == ["Ottawa", ]

    assert find_area_name("ottawa") == ["Ottawa", ]
    assert find_area_name("otawa") == ["Ottawa", ]
