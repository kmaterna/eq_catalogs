"""
The earthquake catalog format. Each of these fields are single values; a catalog is a list of earthquakes. 
"""

class Catalog_EQ:
    def __init__(self, dt, lon, lat, depth, Mag, strike=None, dip=None, rake=None, catname='', bbox=None):
        self.dt = dt;
        self.lon = lon;
        self.lat = lat;
        self.depth = depth;
        self.Mag = Mag;
        self.strike = strike;
        self.dip = dip;
        self.rake = rake;
        self.catname = catname;
        self.bbox = bbox;
