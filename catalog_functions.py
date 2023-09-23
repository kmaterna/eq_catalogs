# Functions that operate on earthquake catalogs

from Tectonic_Utils.seismo import moment_calculations
from .eqcat_object import Catalog_EQ
import datetime as dt
import numpy as np


def restrict_cat_box(catalog, bbox):
    """
    Restrict an earthquake catalog to a certain region. Not working on FMs at the moment

    :param catalog: an earthquake catalog
    :type catalog: Catalog
    :param bbox: bounding box [lon0, lon1, lat0, lat1, depth0, depth1, optionally t1, t2].  t1/t2 could also be None.
    :type bbox: list
    :returns: bounded catalog
    :rtype: Catalog
    """
    print("Restricting catalog to box ", bbox)
    if len(bbox) == 6:
        # If times are not specified, then we keep time bounds of the original catalog.
        dtarray = [eq.dt for eq in catalog];
        bbox.append(min(dtarray));
        bbox.append(max(dtarray));
    else:   # if time is not specified because t1 or t2 are None:
        dtarray = [eq.dt for eq in catalog];
        if bbox[6] is None:
            bbox[6] = min(dtarray);
        if bbox[7] is None:
            bbox[7] = max(dtarray);
    MyCat = [];
    for item in catalog:
        if item.is_within_bbox(bbox):
            new_Event = Catalog_EQ(dt=item.dt, lon=item.lon, lat=item.lat, depth=item.depth, Mag=item.Mag,
                                   strike=item.strike, rake=item.rake, dip=item.dip, catname=item.catname, bbox=bbox);
            MyCat.append(new_Event);
    print("-->Returning %d out of %d events" % (len(MyCat), len(catalog)));
    return MyCat;


def restrict_cat_times(catalog, starttime, endtime):
    """
    :param catalog: list of eq items
    :param starttime: dt object
    :param endtime:  dt object
    :return: list of eq items
    """
    MyCat = [];
    for item in catalog:
        if item.is_within_bbox(starttime, endtime):
            MyCat.append(item);
    print("-->Returning %d out of %d events" % (len(MyCat), len(catalog)));
    return MyCat;


def restrict_above_Mc(totalCat, Mc):
    """
    Restrict an earthquake catalog to above a certain magnitude. Not working on FMs at the moment

    :param totalCat: an earthquake catalog
    :type totalCat: Catalog
    :param Mc: minimum magnitude
    :type Mc: float
    :returns: catalog
    :rtype: Catalog
    """
    print("Restricting catalog to above Mc", Mc);
    MyCat = [];
    for item in totalCat:
        if item.Mag >= Mc:
            MyCat.append(item);
    return MyCat;


def compute_total_moment(MyCat):
    """
    Compute the total moment released by a seismicity catalog

    :param MyCat: an earthquake catalog
    :type MyCat: Catalog
    :returns: total moment in Newton-meters
    :rtype: float
    """
    total_moment = 0;
    for item in MyCat:
        moment_i = moment_calculations.moment_from_mw(item.Mag);
        total_moment += moment_i;
    return total_moment;


def make_cumulative_moment(MyCat):
    """
    Return time and cumulative moment (N-m) released by a seismicity catalog, as arrays, for a staircase plot

    :param MyCat: an earthquake catalog
    :type MyCat: Catalog
    :returns: time array, total moment array
    :rtype: list of dts, list of moments
    """
    dt_total, mo_total = [], [];
    adding_sum = 0;
    dt_total.append(MyCat[0].dt);
    mo_total.append(0);
    for item in MyCat:
        dt_total.append(item.dt);
        mo_total.append(adding_sum);
        adding_sum = adding_sum + moment_calculations.moment_from_mw(item.Mag);
        mo_total.append(adding_sum);
        dt_total.append(item.dt);
    return dt_total, mo_total;


def make_cumulative_stack(MyCat):
    """
    Return time and cumulative EQ number in a seismicity catalog, as arrays, for a staircase plot

    :param MyCat: an earthquake catalog
    :type MyCat: Catalog
    :returns: time array, EQ number array
    :rtype: list of dts, list of number
    """
    dt_total, eq_total = [], [];
    adding_sum = 0;
    dt_total.append(MyCat[0].dt);
    eq_total.append(0);
    for item in MyCat:
        dt_total.append(item.dt);
        eq_total.append(adding_sum);
        adding_sum = adding_sum + 1;
        eq_total.append(adding_sum);
        dt_total.append(item.dt);
    return dt_total, eq_total;


def make_simple_seismicity_rates(MyCat, window=5):
    """
    Reduce a catalog into a time array and an array of earthquakes/day, averaged over a certain window.

    :param MyCat: an earthquake catalog
    :type MyCat: Catalog
    :param window: number of days
    :type window: int
    :return: time series of events
    """
    dtarray_eqs = [item.dt for item in MyCat];
    start_time = min(dtarray_eqs);
    target_time = start_time;
    end_time = max(dtarray_eqs);
    boundary_times = [start_time];
    while target_time < end_time:
        target_time = target_time + dt.timedelta(days=window);
        boundary_times.append(target_time);
    boundary_times.append(end_time);

    # Find the earthquakes between each boundary time
    dtarray_rates, rates = [], [];   # will have the same dimension
    for i in range(0, len(boundary_times)-1):
        dtarray_rates.append(boundary_times[i] + dt.timedelta(days=window/2));  # the center of the bin
        bin_eqs = [date for date in dtarray_eqs if boundary_times[i] <= date < boundary_times[i+1]];   # num eqs in bin
        rates.append(len(bin_eqs) / window);  # rates in eq/day

    return dtarray_rates, rates;


def combine_two_catalogs_hstack(Cat1, Cat2, merging_function):
    """
    Take two catalogs and stitch them together, taking some attributes from one catalog and some from the other.
    Somewhat unintuitive function.
    This function is most useful when moment tensors come from one catalog (i.e., USGS)
    and locations come from another (i.e., local).
    This function is more like the union of a 'set'.

    :param Cat1: catalog
    :param Cat2: catalog
    :param merging_function: specific merging function on two earthquake objects (depends on each project)
    :return: Catalog
    """
    print("Combining elements of two catalogs...")
    MyCat = [];
    cat2_dts = [item.dt for item in Cat2];
    for item in Cat1:
        if item.dt in cat2_dts:
            idx2 = cat2_dts.index(item.dt);
            new_eq = merging_function(item, Cat2[idx2]);
            MyCat.append(new_eq);
        else:
            MyCat.append(item);
    return MyCat;


def combine_two_catalogs_vstack(Cat1, Cat2):
    """
    Take two catalogs (assumed to be from compatible sources) and append them into a single catalog.
    This is the simplest "combining catalogs" function.

    :param Cat1: Catalog
    :param Cat2: Catalog
    :return: combined catalog
    :rtype: Catalog
    """
    combined_Cat = [];
    for item in Cat1:
        combined_Cat.append(item);
    for item in Cat2:
        combined_Cat.append(item);
    return combined_Cat;


def get_start_stop_time(mycat):
    """
    Return the start and stop time of a catalog of earthquakes.

    :param mycat: catalog of earthquake events.  It may have a bbox element.
    :return: start (datetime), end (datetime)
    """
    dtarray = [eq.dt for eq in mycat];
    if mycat[0].bbox is None:   # no official bbox provided
        starttime = min(dtarray);
        endtime = max(dtarray);
    else:   # bbox provided
        if mycat[0].bbox[6] is None:
            starttime = min(dtarray);
        else:
            starttime = mycat[0].bbox[6];
        if mycat[0].bbox[7] is None:
            endtime = max(dtarray);
        else:
            endtime = mycat[0].bbox[7];
    return starttime, endtime;


def compute_spatial_density(eqcat, bounds, spacing_x, spacing_y):
    """
    Compute a 2D array of spatial density of earthquakes in a catalog

    :param eqcat: catalog of earthquakes
    :param bounds: a bounding box [W, E, S, N, top, bottom]
    :param spacing_x: float
    :param spacing_y: float
    :return: xarray (1d array), yarray (1d array), density (2d array)
    """
    xarray = np.arange(bounds[0], bounds[1], spacing_x);
    yarray = np.arange(bounds[2], bounds[3], spacing_y);
    density = np.zeros([len(yarray), len(xarray)]);
    for i in range(len(yarray)):
        for j in range(len(xarray)):
            box_interest = [xarray[j], xarray[j]+spacing_x, yarray[i], yarray[i]+spacing_y, bounds[4], bounds[5]];
            restricted = restrict_cat_box(eqcat, box_interest);
            density[i][j] = len(restricted);
    return xarray, yarray, density;
