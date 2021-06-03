# Functions that operate on earthquake catalogs

from Tectonic_Utils.seismo import moment_calculations
from .eqcat_object import Catalog_EQ


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
    print("Restricting catalog to box ", bbox)
    MyCat = [];
    for item in catalog:
        if bbox[0] <= item.lon <= bbox[1]:
            if bbox[2] <= item.lat <= bbox[3]:
                if bbox[4] <= item.depth <= bbox[5]:
                    if bbox[6] <= item.dt <= bbox[7]:
                        new_Event = Catalog_EQ(dt=item.dt, lon=item.lon, lat=item.lat, depth=item.depth, Mag=item.Mag,
                                               strike=item.strike, rake=item.rake, dip=item.dip, catname=item.catname,
                                               bbox=bbox);
                        MyCat.append(new_Event);
    print("-->Returning %d out of %d events" % (len(MyCat), len(catalog)));
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
