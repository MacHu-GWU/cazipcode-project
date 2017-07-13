#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from cazipcode import fields, SearchEngine

search = SearchEngine()


def rich_info():
    print(search.by_postalcode("K1G 0A1"))

rich_info()


def human_friendly_api():
    # built-in geo search
    result = search.near(lat=45.477873, lng=-75.721100, radius=100)

    # by province, fuzzy name search.
    result = search.by_province("on")

    # by city, fuzzy name search.
    result = search.by_city("otawa")

    # easy to sort and limit result
    # Top 5 high population postal ocde in ON
    result = search.by_province("on",
                                sort_by=fields.province, ascending=False, returns=10)

    # by population dwellings timezone
    result = search.by_population(population_greater=10000)
    result = search.by_dwellings(dwellings_greater=10000)
    result = search.by_timezone(timezone_greater=5, timezone_less=8)

    # by 3-d space
    (
        lat_greater, lat_less, lng_greater, lng_less,
        elevation_greater, elevation_less,
    ) = None, None, None, None, None, None
    result = search.by_lat_lng_elevation(
        lat_greater, lat_less, lng_greater, lng_less, 
        elevation_greater, elevation_less,
    )

human_friendly_api()


def powerful_query():
    # combination of any criterions
    result = search.find(
        lat=None, lng=None, radius=None,
        lat_greater=None, lat_less=None,
        lng_greater=None, lng_less=None,
        elevation_greater=None, elevation_less=None,
        prefix=None,
        substring=None,
        province=None, city=None, area_name=None,
        area_code=None,
        population_greater=None, population_less=None,
        dwellings_greater=None, dwellings_less=None,
        timezone=None, timezone_greater=None, timezone_less=None,
        day_light_savings=None,
        sort_by=None,
        ascending=True,
        returns=5,
    )

powerful_query()

search.close()
