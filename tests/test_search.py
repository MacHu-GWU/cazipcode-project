#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
elementary_path unittest.
"""

import pytest
from cazipcode.search import fields, SearchEngine, great_circle, DEFAULT_LIMIT


def assert_is_all_ascending(array):
    """Assert that this is a strictly asceding array.
    """
    for i, j in zip(array[1:], array[:-1]):
        if (i is not None) and (j is not None):
            assert i >= j


def assert_is_all_descending(array):
    """Assert that this is a strictly desceding array.
    """
    for i, j in zip(array[1:], array[:-1]):
        if (i is not None) and (j is not None):
            assert i <= j


class TestSearchEngine:

    def setup_method(self):
        self.search = SearchEngine()

    def teardown_method(self):
        self.search.close()

    def test_near(self):
        lat, lng, radius = 45.477873, -75.721100, 100

        dist_array = list()
        for p in self.search.near(lat, lng, radius, sort_by=None, ascending=True):
            dist = great_circle((lat, lng), (p.latitude, p.longitude))
            assert dist <= radius
            dist_array.append(dist)
        assert_is_all_ascending(dist_array)
        assert len(dist_array) == DEFAULT_LIMIT

        dist_array = list()
        for p in self.search.near(lat, lng, radius, sort_by=None, ascending=False):
            dist = great_circle((lat, lng), (p.latitude, p.longitude))
            assert dist <= radius
            dist_array.append(dist)
        assert_is_all_descending(dist_array)
        assert len(dist_array) == DEFAULT_LIMIT

        postalcode_array = list()
        for p in self.search.near(lat, lng, radius, sort_by=fields.postalcode, ascending=True):
            assert great_circle(
                (lat, lng), (p.latitude, p.longitude)) <= radius
            postalcode_array.append(p.postalcode)
        assert_is_all_ascending(postalcode_array)
        assert len(dist_array) == DEFAULT_LIMIT

        postalcode_array = list()
        for p in self.search.near(lat, lng, radius, sort_by=fields.postalcode, ascending=False):
            assert great_circle(
                (lat, lng), (p.latitude, p.longitude)) <= radius
            postalcode_array.append(p.postalcode)
        assert_is_all_descending(postalcode_array)
        assert len(dist_array) == DEFAULT_LIMIT

    def test_by_prefix(self):
        postalcode_array = list()
        result = self.search.by_prefix(prefix="K1A")
        for p in result:
            assert p.postalcode.startswith("K1A")
            postalcode_array.append(p.postalcode)
        assert_is_all_ascending(postalcode_array)
        assert len(result) == DEFAULT_LIMIT

    def test_by_substring(self):
        postalcode_array = list()
        result = self.search.by_substring(substring="1A")
        for p in result:
            assert "1A" in p.postalcode
            postalcode_array.append(p.postalcode)
        assert_is_all_ascending(postalcode_array)
        assert len(result) == DEFAULT_LIMIT

    def test_by_province(self):
        result = self.search.by_province(
            province="on", sort_by=fields.population)
        population_array = list()
        for p in result:
            assert p.province == "ON"
        assert_is_all_ascending(population_array)
        assert len(result) == DEFAULT_LIMIT

        result = self.search.by_province(
            province="otraio", sort_by=fields.population)
        population_array = list()
        for p in result:
            assert p.province == "ON"
        assert_is_all_ascending(population_array)
        assert len(result) == DEFAULT_LIMIT

    def test_by_city(self):
        result = self.search.by_city(city="ottawa", sort_by=fields.population)
        population_array = list()
        for p in result:
            assert p.city == "Ottawa"
            population_array.append(p.population)
        assert_is_all_ascending(population_array)
        assert len(result) == DEFAULT_LIMIT

    def test_by_area_name(self):
        result = self.search.by_area_name(
            area_name="ottawa", sort_by=fields.population)
        population_array = list()
        for p in result:
            assert p.area_name == "Ottawa"
            population_array.append(p.population)
        assert_is_all_ascending(population_array)
        assert len(result) == DEFAULT_LIMIT

    def test_by_area_code(self):
        area_code = 613
        result = self.search.by_area_code(area_code)
        for p in result:
            assert p.area_code == area_code
        assert len(result) == DEFAULT_LIMIT

    def test_by_lat_lng_elevation(self):
        lat_greater, lat_less = 45.108240, 46.048956
        result = self.search.by_lat_lng_elevation(
            lat_greater=lat_greater, lat_less=lat_less)
        for p in result:
            assert p.latitude >= lat_greater
            assert p.latitude <= lat_less
        assert len(result) == DEFAULT_LIMIT

        lng_greater, lng_less = -97.643508, -96.387503
        result = self.search.by_lat_lng_elevation(
            lng_greater=lng_greater, lng_less=lng_less)
        for p in result:
            assert p.longitude >= lng_greater
            assert p.longitude <= lng_less
        assert len(result) == DEFAULT_LIMIT

        elevation_greater, elevation_less = 0, 50
        result = self.search.by_lat_lng_elevation(
            elevation_greater=elevation_greater, elevation_less=elevation_less)
        for p in result:
            assert p.elevation >= elevation_greater
            assert p.elevation <= elevation_less
        assert len(result) == DEFAULT_LIMIT

    def test_by_population(self):
        population_greater, population_less = 10000, None
        result = self.search.by_population(population_greater, population_less)
        for p in result:
            if population_greater is not None:
                assert p.population >= population_greater
            if population_less is not None:
                assert p.population <= population_less
        assert len(result) == DEFAULT_LIMIT

    def test_by_dwellings(self):
        dwellings_greater, dwellings_less = 10000, None
        result = self.search.by_dwellings(dwellings_greater, dwellings_less)
        for p in result:
            if dwellings_greater is not None:
                assert p.dwellings >= dwellings_greater
            if dwellings_less is not None:
                assert p.dwellings <= dwellings_less
        assert len(result) == DEFAULT_LIMIT

    def test_by_timezone(self):
        timezone_greater, timezone_less = 5, 8
        result = self.search.by_timezone(
            timezone_greater=timezone_greater, timezone_less=timezone_less)
        for p in result:
            if timezone_greater is not None:
                assert p.timezone >= timezone_greater
            if timezone_less is not None:
                assert p.timezone <= timezone_less
        assert len(result) == DEFAULT_LIMIT

        timezone = 5
        result = self.search.by_timezone(timezone=timezone)
        for p in result:
            assert p.timezone == timezone
        assert len(result) == DEFAULT_LIMIT

    def test_by_day_light_savings(self):
        day_light_savings = True
        result = self.search.by_day_light_savings(day_light_savings)
        for p in result:
            assert p.day_light_savings == True
        assert len(result) == DEFAULT_LIMIT

    def test_by_postalcode(self):
        postalcode = "K1G 0A1"
        p = self.search.by_postalcode(postalcode)
        assert p.postalcode == postalcode

    def test_all_postalcode(self):
        result = self.search.all_postalcode(
            sort_by=fields.postalcode, ascending=True)
        postalcode_array = list()
        for p in result:
            postalcode_array.append(p.postalcode)
        assert_is_all_ascending(postalcode_array)

    def test_random(self):
        result = self.search.random()
        assert len(result) == DEFAULT_LIMIT


if __name__ == "__main__":
    import os
    pytest.main([os.path.basename(__file__), "--tb=native", "-s", ])
