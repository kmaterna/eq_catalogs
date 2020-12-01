# Functions that operate on earthquake catalogs
# Doing useful things

import matplotlib.pyplot as plt
from .eqcat_object import Catalog


def restrict_cat_box(catalog, bbox):
    # A function on earthquake catalogs
    # Limit a catalog to the provided 6- or 8-component bounding box: [lon, lat, depth, and optionally time]
    # losing the focal mechanisms for the moment
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
    print("Returning %d out of %d events" % (len(MyCat.depth), len(catalog.depth)));
    return MyCat;


def make_cumulative_stack(MyCat):
    # Take a catalog
    # Returns two arrays: time and seismicity
    # They can be plotted for a cumulative seismicity plot
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
    # Here you can use ax_annotations to operate on the axes and give useful line annotations
    # like major earthquakes, time boundaries, etc.
    dt_total, eq_total = make_cumulative_stack(MyCat);
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
