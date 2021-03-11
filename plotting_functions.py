# Functions that plot earthquake catalogs

from . import catalog_functions
import matplotlib.pyplot as plt


def make_lollipop_plot(MyCat, filename):
    plt.figure(dpi=300, figsize=(10, 7));
    for i in range(len(MyCat.dtarray)):
        plt.plot(MyCat.dtarray[i], MyCat.Mag[i], marker='o', markersize=10, linewidth=0, color='black');
        plt.plot([MyCat.dtarray[i], MyCat.dtarray[i]], [0, MyCat.Mag[i]], color='black', linewidth=1);
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
    plt.title("Cumulative Seismicity in %s Catalog" % MyCat.catname, fontsize=20);
    plt.savefig(outfile);
    return;


def make_cumulative_plot_with_depths(MyCat, outfile, ax_annotations=None):
    _ = plt.figure(figsize=(18, 9), dpi=300);
    y_array = range(0, len(MyCat.dtarray));
    plt.scatter(MyCat.dtarray, y_array, c=MyCat.depth, s=37, cmap='viridis_r');
    cb = plt.colorbar();
    cb.set_label("Depth (km)", fontsize=20);
    cb.ax.tick_params(labelsize=16);
    plt.gca().tick_params(axis='both', which='major', labelsize=16);
    if ax_annotations is not None:
        ax_annotations(plt.gca());
    plt.xlabel("Time", fontsize=18);
    plt.ylabel("Cumulative Earthquakes", fontsize=18);
    plt.title("Cumulative Seismicity in %s Catalog" % MyCat.catname, fontsize=20);
    plt.savefig(outfile);
    return;


def depth_magnitude_histograms(MyCat, outfile):
    f, axarr = plt.subplots(1, 2, figsize=(17, 8), dpi=300);
    axarr[0].hist(MyCat.depth);
    axarr[0].set_xlabel('Depth (km)', fontsize=16);
    axarr[0].set_ylabel('Number of Events', fontsize=16);
    axarr[0].set_title('Depths in %s Catalog' % MyCat.catname, fontsize=18);
    axarr[0].tick_params(axis='both', which='major', labelsize=16);
    axarr[1].hist(MyCat.Mag);
    axarr[1].set_xlabel('Magnitude (km)', fontsize=16);
    axarr[1].set_ylabel('Number of Events', fontsize=16);
    axarr[1].set_title('Magnitudes in %s Catalog' % MyCat.catname, fontsize=18);
    axarr[1].tick_params(axis='both', which='major', labelsize=16);
    plt.savefig(outfile);
    return;


def basic_map_view(MyCat, outfile):
    plt.figure(figsize=(10, 10), dpi=300);
    plt.scatter(MyCat.lon, MyCat.lat, s=MyCat.Mag, c=MyCat.depth, cmap='viridis_r');
    cb = plt.colorbar();
    cb.ax.tick_params(labelsize=14);
    cb.set_label("Depth (km)", fontsize=16);
    plt.title(MyCat.catname + " Catalog: %d events " % len(MyCat.lon), fontsize=20);
    plt.gca().tick_params(axis='both', which='major', labelsize=16);
    plt.xlabel("Longitude", fontsize=18);
    plt.ylabel("Latitude", fontsize=18);
    plt.savefig(outfile);
    return;
