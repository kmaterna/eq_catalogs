
import collections

# The earthquake catalog format
Catalog = collections.namedtuple("Catalog", ["dtarray", "lon", "lat", "depth", "Mag", "strike", "dip",
                                             "rake", "catname", "bbox"]);
