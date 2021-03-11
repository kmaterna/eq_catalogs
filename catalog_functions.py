# Functions that operate on earthquake catalogs

from Tectonic_Utils.seismo import moment_calculations
from .eqcat_object import Catalog


def restrict_cat_box(catalog, bbox):
    """
    Restrict an earthquake catalog to a certain region. Not working on FMs at the moment

    :param catalog: an earthquake catalog
    :type catalog: Catalog
    :param bbox: bounding box [lon0, lon1, lat0, lat1, depth0, depth1, optionally t1, t2]
    :type bbox: list
    :returns: bounded catalog
    :rtype: Catalog
    """
    new_dtarray = [];
    new_lon, new_lat = [], [];
    new_depth, new_Mag = [], [];
    new_strike, new_dip, new_rake = [], [], [];
    print("Restricting catalog to box ", bbox)
    for i in range(len(catalog.dtarray)):
        if bbox[0] <= catalog.lon[i] <= bbox[1]:
            if bbox[2] <= catalog.lat[i] <= bbox[3]:
                if bbox[4] <= catalog.depth[i] <= bbox[5]:
                    if bbox[6] <= catalog.dtarray[i] <= bbox[7]:
                        new_dtarray.append(catalog.dtarray[i]);
                        new_lon.append(catalog.lon[i]);
                        new_lat.append(catalog.lat[i]);
                        new_depth.append(catalog.depth[i]);
                        new_Mag.append(catalog.Mag[i]);
                        if catalog.strike is None:
                            new_strike = None;
                            new_dip = None;
                            new_rake = None;
                        else:
                            new_strike.append(catalog.strike[i]);
                            new_dip.append(catalog.dip[i]);
                            new_rake.append(catalog.rake[i]);
    MyCat = Catalog(dtarray=new_dtarray, lon=new_lon, lat=new_lat, depth=new_depth, Mag=new_Mag,
                    strike=new_strike, rake=new_rake, dip=new_dip, catname=catalog.catname, bbox=bbox);
    print("-->Returning %d out of %d events" % (len(MyCat.depth), len(catalog.depth)));
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
    for item in MyCat.Mag:
        moment_i = moment_calculations.moment_from_mw(item);
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
    dt_total.append(MyCat.dtarray[0]);
    mo_total.append(0);
    for i in range(len(MyCat.lon)):
        dt_total.append(MyCat.dtarray[i]);
        mo_total.append(adding_sum);
        adding_sum = adding_sum + moment_calculations.moment_from_mw(MyCat.Mag[i]);
        mo_total.append(adding_sum);
        dt_total.append(MyCat.dtarray[i]);
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
    dt_total.append(MyCat.dtarray[0]);
    eq_total.append(0);
    for i in range(len(MyCat.lon)):
        dt_total.append(MyCat.dtarray[i]);
        eq_total.append(adding_sum);
        adding_sum = adding_sum + 1;
        eq_total.append(adding_sum);
        dt_total.append(MyCat.dtarray[i]);
    return dt_total, eq_total;
