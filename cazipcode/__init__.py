#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

__version__ = "0.0.2"
__short_description__ = "Powerful Canada zipcode search engine."
__license__ = "MIT"
__author__ = "Sanhe Hu"

try:
    from .search import great_circle, fields, PostalCode, SearchEngine
except:
    pass
