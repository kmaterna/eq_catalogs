# Functions that plot earthquake catalogs

from . import catalog_functions
import matplotlib.pyplot as plt
import datetime as dt
from Tectonic_Utils.seismo import moment_calculations


def make_lollipop_plot(MyCat, filename, lower_mag=2.5, upper_mag=5.0):
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
    plt.ylim([lower_mag, upper_mag])
    plt.xticks(rotation=45)
    plt.savefig(filename, bbox_inches='tight');
    return;


def make_seismicity_rate_plot(dtarray, rates, filename, date_boundaries=None):
    plt.figure(dpi=300, figsize=(12, 7));
    plt.plot(dtarray, rates, linewidth=3);
    plt.xlabel('Time', fontsize=20);
    plt.ylabel('Average Seismicity Rate (Earthquakes/Day)', fontsize=20);
    if date_boundaries:   # optional annotations
        [bottom, top] = plt.gca().get_ylim();
        for time in date_boundaries:
            plt.plot([time, time], [bottom, top], '--k');
    plt.gca().set_ylim([0, 120]);
    plt.gca().tick_params(axis='both', which='major', labelsize=16)
    plt.savefig(filename);
    print("Plotting %s " % filename);
    return;

def write_seismicity_rates(dtarray, rates, filename):
    print("Writing %s " % filename);
    ofile = open(filename, 'w');
    window = dtarray[1] - dtarray[0];
    window = window.days;
    ofile.write("# Center_Date Num_EQs_per_day Window_Days\n");
    for i in range(len(dtarray)):
        ofile.write("%s %d %d\n" % (dt.datetime.strftime(dtarray[i], '%Y%m%d'), rates[i], window));
    ofile.close();
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
    fontsize = 30
    depths = [i.depth for i in MyCat];
    mags = [i.Mag for i in MyCat];
    axarr[0].hist(depths);
    axarr[0].set_xlabel('Depth (km)', fontsize=fontsize);
    axarr[0].set_ylabel('Number of Events', fontsize=fontsize);
    axarr[0].set_title('Depths in %s Catalog' % MyCat[0].catname, fontsize=fontsize);
    axarr[0].tick_params(axis='both', which='major', labelsize=fontsize);
    axarr[1].hist(mags);
    axarr[1].set_xlabel('Magnitude', fontsize=fontsize);
    axarr[1].set_ylabel('Number of Events', fontsize=fontsize);
    axarr[1].set_title('Magnitudes in %s Catalog' % MyCat[0].catname, fontsize=fontsize);
    axarr[1].tick_params(axis='both', which='major', labelsize=fontsize);
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
