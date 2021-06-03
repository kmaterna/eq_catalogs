# Functions that plot earthquake catalogs

from . import catalog_functions
import matplotlib.pyplot as plt
from Tectonic_Utils.seismo import moment_calculations


def make_lollipop_plot(MyCat, filename):
    """
    A plot of event magnitude versus time. Looks like lollipops.
    """
    plt.figure(dpi=300, figsize=(10, 7));
    for item in MyCat:
        plt.plot(item.dt, item.Mag, marker='o', markersize=10, linewidth=0, color='black');
        plt.plot([item.dt, item.dt], [0, item.Mag], color='black', linewidth=1);
    plt.ylabel('Magnitude', fontsize=20);
    plt.xlabel('Time', fontsize=20);
    plt.gca().tick_params(axis='both', which='major', labelsize=16)
    plt.ylim([2.5, 5.0])
    plt.savefig(filename);
    return;


def make_cumulative_plot(MyCat, outfile, ax_annotations=None):
    """
    Here you can use ax_annotations to operate on the axes and give useful line annotations
    like major earthquakes, time boundaries, etc.
    """
    dt_total, eq_total = catalog_functions.make_cumulative_stack(MyCat);
    _ = plt.figure(figsize=(18, 9), dpi=300);
    plt.plot_date(dt_total, eq_total, linewidth=2, linestyle='solid', marker=None, color='blue');
    plt.gca().tick_params(axis='both', which='major', labelsize=16);
    if ax_annotations is not None:
        ax_annotations(plt.gca());
    plt.xlabel("Time", fontsize=18);
    plt.ylabel("Cumulative Earthquakes", fontsize=18);
    plt.title("Cumulative Seismicity in %s Catalog" % MyCat[0].catname, fontsize=20);
    plt.savefig(outfile);
    return;


def make_cumulative_plot_with_depths(MyCat, outfile, ax_annotations=None):
    """Same as previous plotting function, but with dots color coded by depth. """
    _ = plt.figure(figsize=(18, 9), dpi=300);
    y_array = range(0, len(MyCat));
    dtarray = [item.dt for item in MyCat];
    carray = [item.depth for item in MyCat];
    plt.scatter(dtarray, y_array, c=carray, s=37, cmap='viridis_r');
    cb = plt.colorbar();
    cb.set_label("Depth (km)", fontsize=20);
    cb.ax.tick_params(labelsize=16);
    plt.gca().tick_params(axis='both', which='major', labelsize=16);
    if ax_annotations is not None:
        ax_annotations(plt.gca());
    plt.xlabel("Time", fontsize=18);
    plt.ylabel("Cumulative Earthquakes", fontsize=18);
    plt.title("Cumulative Seismicity in %s Catalog" % MyCat[0].catname, fontsize=20);
    plt.savefig(outfile);
    return;


def depth_magnitude_histograms(MyCat, outfile):
    """Two side-by-side histograms of depth and magnitude of the catalog."""
    f, axarr = plt.subplots(1, 2, figsize=(17, 8), dpi=300);
    depths = [i.depth for i in MyCat];
    mags = [i.Mag for i in MyCat];
    axarr[0].hist(depths);
    axarr[0].set_xlabel('Depth (km)', fontsize=16);
    axarr[0].set_ylabel('Number of Events', fontsize=16);
    axarr[0].set_title('Depths in %s Catalog' % MyCat[0].catname, fontsize=18);
    axarr[0].tick_params(axis='both', which='major', labelsize=16);
    axarr[1].hist(mags);
    axarr[1].set_xlabel('Magnitude', fontsize=16);
    axarr[1].set_ylabel('Number of Events', fontsize=16);
    axarr[1].set_title('Magnitudes in %s Catalog' % MyCat[0].catname, fontsize=18);
    axarr[1].tick_params(axis='both', which='major', labelsize=16);
    plt.savefig(outfile);
    return;


def map_seismicity_catalog(MyCat, outfile, ax_annotations=None):
    """
    A general function for mapping a seismicity catalog in lat/lon space
    Additional information can be passed in with the ax_annotations function
    """
    plt.figure(figsize=(14, 12), dpi=300);
    lons = [i.lon for i in MyCat];
    lats = [i.lat for i in MyCat];
    Mags = [i.Mag for i in MyCat];
    depths = [i.depth for i in MyCat];
    plt.scatter(lons, lats, s=Mags, c=depths, cmap='viridis_r');
    cb = plt.colorbar();
    cb.ax.tick_params(labelsize=14);
    cb.set_label("Depth (km)", fontsize=16);
    if ax_annotations is not None:
        ax_annotations(plt.gca());
    plt.title(MyCat[0].catname + " Catalog: %d events " % len(MyCat), fontsize=20);
    plt.gca().tick_params(axis='both', which='major', labelsize=16);
    plt.xlabel("Longitude", fontsize=18);
    plt.ylabel("Latitude", fontsize=18);
    plt.savefig(outfile);
    return;


def write_catalog_total_moments(MyCat, outputfile):
    """
    Write a few summary metrics of the catalog into a text file. Includes total moment and equivalent magnitude.
    """
    Moment = catalog_functions.compute_total_moment(MyCat);
    Mw_total = moment_calculations.mw_from_moment(Moment);
    print("Total Moment Equivalent (Mw) from %d events: %f" % (len(MyCat), Mw_total) );
    ofile = open(outputfile, 'w');
    M_total_str = "{:.2e}".format(Moment);
    ofile.write("Total Moment from %d events: %s N-m\n" % (len(MyCat), M_total_str) );
    ofile.write("Total Moment Equivalent (Mw) from %d events: %f\n" % (len(MyCat), Mw_total) );
    ofile.close();
    return;
