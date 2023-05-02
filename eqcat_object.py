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

    # ----------- PREDICATES ---------- #
    def is_within_bbox(self, bbox):
        """
        :param bbox: [lonW, lonE, latS, latN, depthT, depthB, t0, t1]
        :return: bool
        """
        if bbox[0] <= self.lon <= bbox[1]:
            if bbox[2] <= self.lat <= bbox[3]:
                if bbox[4] <= self.depth <= bbox[5]:
                    if bbox[6] <= self.dt <= bbox[7]:
                        return 1;
        return 0;
