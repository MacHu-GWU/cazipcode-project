.. image:: https://travis-ci.org/MacHu-GWU/cazipcode-project.svg?branch=master

.. image:: https://img.shields.io/pypi/v/cazipcode.svg

.. image:: https://img.shields.io/pypi/l/cazipcode.svg

.. image:: https://img.shields.io/pypi/pyversions/cazipcode.svg


Welcome to cazipcode Documentation
==================================
Powerful Canada zipcode search engine. Powerful geo lat lng search, fuzzy province, city name search out of the box. And powerful search API with high performance sorting.


**Quick Links**
---------------
- `GitHub Homepage <https://github.com/MacHu-GWU/cazipcode-project>`_
- `Online Documentation <http://pythonhosted.org/cazipcode>`_
- `PyPI download <https://pypi.python.org/pypi/cazipcode>`_
- `Install <install_>`_
- `Issue submit and feature request <https://github.com/MacHu-GWU/cazipcode-project/issues>`_
- `API reference and source code <http://pythonhosted.org/cazipcode/py-modindex.html>`_


**Features**
------------
- **200,000 + postal code covers most of the place.**

- **Rich information of postalcode is available**:

.. code-block:: json

    {
        "postalcode": "K1G 0A1",
        "province": "ON",
        "city": "Ottawa",
        "area_name": "Ottawa",
        "area_code": 613,
        "latitude": 45.417874,
        "longitude": -75.648284,
        "population": 33994,
        "dwellings": 14817,
        "elevation": 56,
        "timezone": 5,
        "day_light_savings": 1
    }

- **Human friendly API**

.. code-block:: python

    from cazipcode import fields, SearchEngine

    with SearchEngine() as search:
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


- **Powerful query**

.. code-block:: python

    from cazipcode import fields, SearchEngine

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


.. _install:

Install
-------

``cazipcode`` is released on PyPI, so all you need is:

.. code-block:: console

	$ pip install cazipcode

To upgrade to latest version:

.. code-block:: console

	$ pip install --upgrade cazipcode