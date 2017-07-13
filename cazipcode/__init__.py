#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

__version__ = "0.0.1"
__short_description__ = "Powerful Canada zipcode search engine."
__license__ = "MIT"
__author__ = "Sanhe Hu"

try:
    from .data import fields
    from .search import SearchEngine
except:
    pass
