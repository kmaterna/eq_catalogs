"""
The earthquake catalog format. Each of these fields are single values; a catalog is a list of earthquakes. 
"""
from Tectonic_Utils.seismo import moment_calculations
import datetime as dt

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

    def is_within_times(self, starttime, endtime):
        """
        :param starttime: datetime
        :param endtime: datetime
        :return: bool
        """
        if starttime <= self.dt <= endtime:
            return 1;
        else:
            return 0;


class Catalog:
    """
    The main Catalog object.
    """
    def __init__(self, catalog):
        self.catalog = catalog;  # a list of earthquake objects

    def __len__(self):
        return len(self.catalog);

    def __getitem__(self, item):
        return self.catalog[item];

    def restrict_cat_times(self, starttime, endtime):
        """
        Filter a catalog based on starttime and endtime

        :param starttime: dt object
        :param endtime:  dt object
        :return: list of eq items
        """
        MyCat = [];
        for item in self.catalog:
            if item.is_within_bbox(starttime, endtime):
                MyCat.append(item);
        newCat = Catalog(MyCat);
        print("-->Returning %d out of %d events" % (len(newCat), len(self.catalog)));
        return newCat;

    def restrict_above_Mc(self, Mc):
        """
        Restrict an earthquake catalog to above a certain magnitude. Not working on FMs at the moment

        :param Mc: minimum magnitude
        :type Mc: float
        :returns: catalog
        :rtype: Catalog
        """
        print("Restricting catalog to above Mc", Mc);
        MyCat = [];
        for item in self.catalog:
            if item.Mag >= Mc:
                MyCat.append(item);
        return Catalog(MyCat);

    def restrict_cat_box(self, bbox):
        """
        Restrict an earthquake catalog to a certain region. Not working on FMs at the moment

        :param bbox: bounding box [lon0, lon1, lat0, lat1, depth0, depth1, optionally t1, t2].  t1/t2 could be None.
        :type bbox: list
        :returns: bounded catalog
        :rtype: Catalog
        """
        print("Restricting catalog to box ", bbox)
        if len(bbox) == 6:
            # If times are not specified, then we keep time bounds of the original catalog.
            dtarray = [eq.dt for eq in self.catalog];
            bbox.append(min(dtarray));
            bbox.append(max(dtarray));
        else:  # if time is not specified because t1 or t2 are None:
            dtarray = [eq.dt for eq in self.catalog];
            if bbox[6] is None:
                bbox[6] = min(dtarray);
            if bbox[7] is None:
                bbox[7] = max(dtarray);
        MyCat = [];
        for item in self.catalog:
            if item.is_within_bbox(bbox):
                new_Event = Catalog_EQ(dt=item.dt, lon=item.lon, lat=item.lat, depth=item.depth, Mag=item.Mag,
                                       strike=item.strike, rake=item.rake, dip=item.dip, catname=item.catname,
                                       bbox=bbox);
                MyCat.append(new_Event);
        newCat = Catalog(MyCat);
        print("-->Returning %d out of %d events" % (len(self.catalog), len(newCat)));
        return newCat;

    def compute_total_moment(self):
        """
        Compute the total moment released by a seismicity catalog

        :returns: total moment in Newton-meters
        :rtype: float
        """
        total_moment = 0;
        for item in self.catalog:
            moment_i = moment_calculations.moment_from_mw(item.Mag);
            total_moment += moment_i;
        return total_moment;

    def get_start_stop_time(self):
        """
        Return the start and stop time of a catalog of earthquakes.

        :return: start (datetime), end (datetime)
        """
        dtarray = [eq.dt for eq in self.catalog];
        starttime = min(dtarray);
        endtime = max(dtarray);
        return starttime, endtime;

    def make_cumulative_moment(self):
        """
        Return time and cumulative moment (N-m) released by a seismicity catalog, as arrays, for a staircase plot

        :returns: time array, total moment array
        :rtype: list of dts, list of moments
        """
        dt_total, mo_total = [], [];
        adding_sum = 0;
        dt_total.append(self.catalog[0].dt);
        mo_total.append(0);
        for item in self.catalog:
            dt_total.append(item.dt);
            mo_total.append(adding_sum);
            adding_sum = adding_sum + moment_calculations.moment_from_mw(item.Mag);
            mo_total.append(adding_sum);
            dt_total.append(item.dt);
        return dt_total, mo_total;

    def make_cumulative_stack(self):
        """
        Return time and cumulative EQ number in a seismicity catalog, as arrays, for a staircase plot

        :returns: time array, EQ number array
        :rtype: list of dts, list of number
        """
        dt_total, eq_total = [], [];
        adding_sum = 0;
        dt_total.append(self.catalog[0].dt);
        eq_total.append(0);
        for item in self.catalog:
            dt_total.append(item.dt);
            eq_total.append(adding_sum);
            adding_sum = adding_sum + 1;
            eq_total.append(adding_sum);
            dt_total.append(item.dt);
        return dt_total, eq_total;

    def make_simple_seismicity_rates(self, window=5):
        """
        Reduce a catalog into a time array and an array of earthquakes/day, averaged over a certain window.

        :param window: number of days
        :type window: int
        :return: time series of events
        """
        dtarray_eqs = [item.dt for item in self.catalog];
        start_time, end_time = self.get_start_stop_time()
        target_time = start_time;
        boundary_times = [start_time];
        while target_time < end_time:
            target_time = target_time + dt.timedelta(days=window);
            boundary_times.append(target_time);
        boundary_times.append(end_time);

        # Find the earthquakes between each boundary time
        dtarray_rates, rates = [], [];   # will have the same dimension
        for i in range(0, len(boundary_times)-1):
            dtarray_rates.append(boundary_times[i] + dt.timedelta(days=window/2));  # the center of the bin
            bin_eqs = [date for date in dtarray_eqs if boundary_times[i] <= date < boundary_times[i+1]];   # eqs in bin
            rates.append(len(bin_eqs) / window);  # rates in eq/day

        return dtarray_rates, rates;
