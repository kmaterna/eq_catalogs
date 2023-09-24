# Functions that operate on earthquake catalogs

import numpy as np

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
            restricted = eqcat.restrict_cat_box(box_interest);
            density[i][j] = len(restricted);
    return xarray, yarray, density;
