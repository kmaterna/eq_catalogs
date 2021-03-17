
import collections


Catalog_EQ = collections.namedtuple("Catalog_EQ", ["dt", "lon", "lat", "depth", "Mag", "strike", "dip",
                                                   "rake", "catname", "bbox"]);
""" 
The earthquake catalog format. Each of these fields are single values; a catalog is a list of earthquakes. 
"""
