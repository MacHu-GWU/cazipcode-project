#!/usr/bin/env python
# -*- coding: utf-8 -*-

import heapq
from math import radians, cos
from functools import total_ordering
from six import string_types
from sqlalchemy import select, func, and_

try:
    from .data import (
        engine, t,
        find_province, find_city, find_area_name, fields,
    )
    from .pkg.nameddict import Base
    from .pkg.geo_search import great_circle
except:
    from cazipcode.data import (
        engine, t,
        find_province, find_city, find_area_name, fields,
    )
    from cazipcode.pkg.nameddict import Base
    from cazipcode.pkg.geo_search import great_circle


@total_ordering
class PostalCode(Base):
    """Represent a postal code.

    Attributes:

    - postalcode: 7 letter, example: "A0A 0A3"
    - city: city name, example: "Ottawa"
    - province: 2 letters province name abbreviation, example: "ON"
    - area_code: integer, 3 letter digits, example: 123
    - area_name: area name, example: "Ottawa"
    - latitude: latitude
    - longitude: longitude
    - elevation: elevation
    - population: integer, population
    - dwellings: integer, dwellings
    - timezone: integer, timezone
    - day_light_savings: integer, indicate that whether this zipcode use 
      day light savings.

    Compare two postal code is actually comparing it's postal code string.
    """
    __attrs__ = [
        "postalcode",
        "city",
        "province",
        "area_code",
        "area_name",
        "latitude",
        "longitude",
        "elevation",
        "population",
        "dwellings",
        "timezone",
        "day_light_savings",
    ]

    def __init__(self,
                 postalcode=None,
                 province=None,
                 city=None,
                 area_code=None,
                 area_name=None,
                 latitude=None,
                 longitude=None,
                 elevation=None,
                 population=None,
                 dwellings=None,
                 timezone=None,
                 day_light_savings=None):
        self.postalcode = postalcode
        self.province = province
        self.city = city
        self.area_code = area_code
        self.area_name = area_name
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.population = population
        self.dwellings = dwellings
        self.timezone = timezone
        self.day_light_savings = day_light_savings

    def __str__(self):
        return self.to_json(indent=4)

    def __eq__(self, other):
        return self.postalcode == other.postalcode

    def __lt__(self, other):
        return self.postalcode < other.postalcode

    def __nonzero__(self):
        """For Python2 bool() method.
        """
        return self.postalcode is not None

    def __bool__(self):
        """For Python3 bool() method.
        """
        return self.postalcode is not None


DEFAULT_LIMIT = 5


class SearchEngine(object):
    """
    """

    def __init__(self):
        self.connect = engine.connect()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.connect.close()

    def close(self):
        """Closs engine.

        **中文文档**

        断开与数据库的连接。
        """
        self.connect.close()

    def find(self,
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
             returns=DEFAULT_LIMIT):
        """A powerful search method.

        :param lat, lng, radius: search near lat, lng with in xxx miles.
        :param lat_greater, lat_less, lng_greater, lng_less, 
          elevation_greater, elevation_less: search postalcode within a 3-d
          space box.
        :param province, city, area_name: search by province, city, area_name. 
          state name could be 2-letter abbreviation, or full name, 
          and this search is fuzzy and typo tolerant.
        :param area_code: int, all postal code area_code exactly matches.
        :param prefix: all postal code with this prefix, for example: "01A"
        :param substring: all postal code contains this substring.
        :param population_greater, population_less: population falls in a range.
        :param dwellings_greater, dwellings_less: dwellings falls in a range.
        :param timezone_greater, timezone_less: timezone falls in a range.
        :param timezone: int, all postal code timezone exactly matches.
        :param day_light_savings: bool or int, whether using day light savings.        
        """

        filters = list()

        # near lat, lng
        if lat is not None and lng is not None and radius is not None:
            dist_btwn_lat_deg = 69.172
            dist_btwn_lon_deg = cos(radians(lat)) * 69.172
            lat_degr_rad = abs(radius * 1.05 / dist_btwn_lat_deg)
            lon_degr_rad = abs(radius * 1.05 / dist_btwn_lon_deg)

            lat_lower = lat - lat_degr_rad
            lat_upper = lat + lat_degr_rad
            lng_lower = lng - lon_degr_rad
            lng_upper = lng + lon_degr_rad

#             print("%.6f, %.6f, %.6f, %.6f" % (lat_lower, lat_upper, lng_lower, lng_upper))
#             print("%.6f" % great_circle((lat, lng), (lat_upper, lng_upper)))
#             print("%.6f" % great_circle((lat, lng), (lat_lower, lng_lower)))

            filters.append(t.c.latitude >= lat_lower)
            filters.append(t.c.latitude <= lat_upper)
            filters.append(t.c.longitude >= lng_lower)
            filters.append(t.c.longitude <= lng_upper)

        elif lat is None and lng is None and radius is None:
            pass

        else:
            raise ValueError("lat, lng, radius has to be all given or not.")

        # elevation

        # prefix
        if prefix is not None:
            if not isinstance(prefix, string_types):
                raise TypeError("prefix has to be a string")
            if 1 <= len(prefix) <= 7:
                pattern = "%s%%" % prefix
                filters.append(t.c.postalcode.like(pattern))
            else:
                raise ValueError("prefix has to be a 1-7 letter length!")

        # substring
        if substring is not None:
            if not isinstance(substring, string_types):
                raise TypeError("substring has to be a string")
            if 1 <= len(substring) <= 7:
                pattern = "%%%s%%" % substring
                filters.append(t.c.postalcode.like(pattern))
            else:
                raise ValueError("substring has to be a 1-7 letter length!")

        # province
        if province:
            try:
                province = find_province(province, best_match=True)[0]
                filters.append(t.c.province == province)
            except ValueError:
                pass

        # city
        if city:
            try:
                city = find_city(city, best_match=True)[0]
                filters.append(t.c.city == city)
            except ValueError:
                pass

        # area_name
        if area_name:
            try:
                area_name = find_area_name(area_name, best_match=True)[0]
                filters.append(t.c.area_name == area_name)
            except ValueError:
                pass

        # area_code
        if area_code:
            filters.append(t.c.area_code == area_code)

        # latitude
        if lat_greater is not None:
            filters.append(t.c.latitude >= lat_greater)

        if lat_less is not None:
            filters.append(t.c.latitude <= lat_less)

        # longitude
        if lng_greater is not None:
            filters.append(t.c.longitude >= lng_greater)

        if lng_less is not None:
            filters.append(t.c.longitude <= lng_less)

        # elevation
        if elevation_greater is not None:
            filters.append(t.c.elevation >= elevation_greater)

        if elevation_less is not None:
            filters.append(t.c.elevation <= elevation_less)

        # population
        if population_greater is not None:
            filters.append(t.c.population >= population_greater)

        if population_less is not None:
            filters.append(t.c.population <= population_less)

        # dwellings
        if dwellings_greater is not None:
            filters.append(t.c.dwellings >= dwellings_greater)

        if dwellings_less is not None:
            filters.append(t.c.dwellings <= dwellings_less)

        # timezone
        if timezone_greater is not None:
            filters.append(t.c.timezone >= timezone_greater)

        if timezone_less is not None:
            filters.append(t.c.timezone <= timezone_less)

        if timezone:
            filters.append(t.c.timezone == timezone)

        # day_light_savings
        if day_light_savings is not None:
            day_light_savings = int(day_light_savings)
            filters.append(t.c.day_light_savings == day_light_savings)

        # execute query
        sql = select([t]).where(and_(*filters))

        if sort_by:
            if ascending:
                clause = t.c[sort_by].asc()
            else:
                clause = t.c[sort_by].desc()
            sql = sql.order_by(clause)

        # if use "near" search
        if radius:
            # sort_by given, then sort by keyword
            if sort_by:
                result = list()
                for row in engine.execute(sql):
                    dist = great_circle(
                        (lat, lng), (row.latitude, row.longitude))
                    if dist <= radius:
                        result.append(PostalCode._make(row))
                        if len(result) == returns:
                            break

            # sort_by not given, then sort by distance, don't use limit clause
            else:
                heap = list()
                for row in engine.execute(sql):
                    # 43.959918, 46.995828, -77.885944, -73.556256
                    dist = great_circle(
                        (lat, lng), (row.latitude, row.longitude))
                    if dist <= radius:
                        heap.append((dist, row))

                # Use heap sort to find top-K
                if ascending:
                    heap = heapq.nsmallest(returns, heap, key=lambda x: x[0])
                else:
                    heap = heapq.nlargest(returns, heap, key=lambda x: x[0])

                result = [PostalCode._make(row) for _, row in heap]

        #
        else:
            if not sort_by:
                if ascending:
                    clause = t.c[fields.postalcode].asc()
                else:
                    clause = t.c[fields.postalcode].desc()
                sql = sql.order_by(clause)

            sql = sql.limit(returns)
            result = [PostalCode._make(row) for row in engine.execute(sql)]

        return result

    def near(self, lat, lng, radius,
             sort_by=fields.postalcode,
             ascending=True,
             returns=DEFAULT_LIMIT):
        return self.find(lat=lat, lng=lng, radius=radius,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_prefix(self, prefix,
                  sort_by=fields.postalcode,
                  ascending=True,
                  returns=DEFAULT_LIMIT):
        return self.find(prefix=prefix,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_substring(self, substring,
                     sort_by=fields.postalcode,
                     ascending=True,
                     returns=DEFAULT_LIMIT):
        return self.find(substring=substring,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_province(self, province,
                    sort_by=fields.postalcode,
                    ascending=True,
                    returns=DEFAULT_LIMIT):
        return self.find(province=province,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_city(self, city,
                sort_by=fields.postalcode,
                ascending=True,
                returns=DEFAULT_LIMIT):
        return self.find(city=city,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_area_name(self, area_name,
                     sort_by=fields.postalcode,
                     ascending=True,
                     returns=DEFAULT_LIMIT):
        return self.find(area_name=area_name,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_area_code(self, area_code,
                     sort_by=fields.postalcode,
                     ascending=True,
                     returns=DEFAULT_LIMIT):
        return self.find(area_code=area_code,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_lat_lng_elevation(self,
                             lat_greater=None, lat_less=None,
                             lng_greater=None, lng_less=None,
                             elevation_greater=None, elevation_less=None,
                             sort_by=fields.postalcode,
                             ascending=True,
                             returns=DEFAULT_LIMIT):
        return self.find(lat_greater=lat_greater,
                         lat_less=lat_less,
                         lng_greater=lng_greater,
                         lng_less=lng_less,
                         elevation_greater=elevation_greater,
                         elevation_less=elevation_less,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_population(self,
                      population_greater=None, population_less=None,
                      sort_by=fields.postalcode,
                      ascending=True,
                      returns=DEFAULT_LIMIT):
        return self.find(population_greater=population_greater,
                         population_less=population_less,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_dwellings(self,
                     dwellings_greater=None, dwellings_less=None,
                     sort_by=fields.postalcode,
                     ascending=True,
                     returns=DEFAULT_LIMIT):
        return self.find(dwellings_greater=dwellings_greater,
                         dwellings_less=dwellings_less,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_timezone(self,
                    timezone=None,
                    timezone_greater=None, timezone_less=None,
                    sort_by=fields.postalcode,
                    ascending=True,
                    returns=DEFAULT_LIMIT):
        return self.find(timezone=timezone,
                         timezone_greater=timezone_greater,
                         timezone_less=timezone_less,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)

    def by_day_light_savings(self, day_light_savings,
                             sort_by=fields.postalcode,
                             ascending=True,
                             returns=DEFAULT_LIMIT):
        return self.find(day_light_savings=day_light_savings,
                         sort_by=sort_by,
                         ascending=ascending,
                         returns=returns)
