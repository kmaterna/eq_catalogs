
import collections


Catalog = collections.namedtuple("Catalog", ["dtarray", "lon", "lat", "depth", "Mag", "strike", "dip",
                                             "rake", "catname", "bbox"]);
""" 
The earthquake catalog format. Each of these fields are arrays of the same length (in the current formulation). 
"""
