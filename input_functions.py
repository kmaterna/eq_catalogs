# Functions to read and write various earthquake catalog formats


import numpy as np
import datetime as dt
import csv
from .eqcat_object import Catalog_EQ
import xml.etree.ElementTree as ET
import pandas


def input_qtm(filename):
    """
    Input the txt file format of Ross et al. (2019)'s QTM catalog
    downloaded from https://scedc.caltech.edu/research-tools/altcatalogs.html
    """
    print("Reading file %s " % filename);
    print(dt.datetime.now());
    MyCat = [];

    # This takes 15 seconds (surprisingly, np.loadtxt takes 30 seconds to do the same thing)
    ifile = open(filename, 'r');
    ifile.readline();
    for line in ifile:
        temp = line.split();
        [year, month, day, hour, minute, _] = line.split()[0:6];
        lat = float(temp[7]);
        lon = float(temp[8]);
        depth = float(temp[9]);
        mag = float(temp[10]);
        try:
            newdate = dt.datetime.strptime(year + month + day + hour + minute, "%Y%m%d%H%M");
        except ValueError:  # WE ACTUALLY GOT AN EARTHQUAKE DURING A LEAP SECOND!!!!
            print("You may have a problem at: ");
            print(year + month + day + hour + minute);
            newdate = dt.datetime.strptime(year + month + day + hour, "%Y%m%d%H");
        myEvent = Catalog_EQ(dt=newdate, lon=lon, lat=lat, depth=depth, Mag=mag, strike=None, dip=None, rake=None,
                             catname="QTM", bbox=None);
        MyCat.append(myEvent);
    print("done at : ", dt.datetime.now());
    ifile.close();
    print("Reading %d catalog events from file %s " % (len(MyCat), filename));
    return MyCat;


def input_shearer_cat(filename):
    """ Read the Shearer Yang Catalog """
    ifile = open(filename);
    MyCat = [];
    for line in ifile:
        temp = line.split();
        [year, month, day, hour, minute] = line.split()[0:5];
        second = temp[5][0:2]
        if int(second) > 59:
            print("We found a leap second at: ", year, month, day, hour, minute, second);
            print("Turning it back one second")
            second = '59'
        if hour == '-1':
            print("We found a problem at: ", year, month, day, hour, minute, second);
            print("Turning it forward one second")
            hour = '00'
            minute = '00'
            second = '00'
        eqdate = dt.datetime.strptime(year + " " + month + " " + day + " " + hour + " " + minute + " " + second,
                                      "%Y %m %d %H %M %S");
        myEvent = Catalog_EQ(dt=eqdate, lon=float(temp[8]), lat=float(temp[7]), depth=float(temp[9]),
                             Mag=float(temp[10]), strike=None, dip=None, rake=None, catname="Shearer", bbox=None);
        MyCat.append(myEvent);
    ifile.close();
    print("Reading %d catalog events from file %s " % (len(MyCat), filename));
    return MyCat;


def read_Wei_2015_supplement(filename):
    MyCat = [];
    ifile = open(filename);
    for line in ifile:
        lon = float(line.split()[2]);
        lat = float(line.split()[1]);
        depth = float(line.split()[3]);
        mag = float(line.split()[4]);
        fm = line.split()[5];
        strike = float(fm.split('/')[0]);
        dip = float(fm.split('/')[1]);
        rake = float(fm.split('/')[2]);
        myEvent = Catalog_EQ(dt=None, lon=lon, lat=lat, depth=depth, Mag=mag, strike=strike, dip=dip, rake=rake,
                             catname='Wei_2015', bbox=None);
        MyCat.append(myEvent);
    print("Reading %d catalog events from file %s " % (len(MyCat), filename));
    ifile.close();
    return MyCat;


def read_intxt_fms(filename, catname='Intxt'):
    """Read focal mechanisms from .intxt file format, as defined in the elastic modeling code"""
    print("Reading earthquake catalog from file %s " % filename);
    ifile = open(filename, 'r');
    MyCat = [];
    for line in ifile:
        temp = line.split();
        if len(temp) == 0:
            continue;
        if temp[0] == "Source_FM:":
            [strike, rake, dip, lon, lat, depth, mag] = [float(i) for i in line.split()[1:8]];
            myEvent = Catalog_EQ(dt=None, lon=lon, lat=lat, strike=strike, dip=dip, rake=rake, depth=depth, Mag=mag,
                                 catname=catname, bbox=None);
            MyCat.append(myEvent);
    ifile.close();
    print("Reading %d catalog events from file %s " % (len(MyCat), filename));
    return MyCat;


def write_intxt_fms(MyCat, filename, mu=30e9, lame1=30e9):
    """Write a catalog into focal mechanism format, as described in the elastic modeling code"""
    print("Writing earthquake catalog into file %s " % filename);
    ofile = open(filename, 'w');
    # Adding header line
    if MyCat[0].bbox is not None:
        bbox_string = ' within ' + str(MyCat[0].bbox[0]) + '/' + str(MyCat[0].bbox[1]) + '/' + \
                      str(MyCat[0].bbox[2]) + '/' + str(MyCat[0].bbox[3]) + '/' + str(MyCat[0].bbox[4]) + '/' + \
                      str(MyCat[0].bbox[5]) + '/' + dt.datetime.strftime(MyCat[0].bbox[6], "%Y%m%d") + '/' + \
                      dt.datetime.strftime(MyCat[0].bbox[7], "%Y%m%d");
    else:
        bbox_string = '';
    ofile.write("# %s catalog %s\n" % (MyCat[0].catname, bbox_string));
    for item in MyCat:
        if not item.strike:
            continue;
        ofile.write("Source_FM: %f %f %f %f %f %f %f %f %f\n" % (item.strike, item.rake, item.dip, item.lon, item.lat,
                                                                 item.depth, item.Mag, mu, lame1));
    ofile.close();
    return;


def read_usgs_website_csv(filename):
    """Read the files when you hit the 'DOWNLOAD' button on the USGS earthquakes website"""
    MyCat = [];
    with open(filename) as csvfile:
        mycatreader = csv.reader(csvfile);
        for row in mycatreader:
            if row[0] == 'time':
                continue;
            dtobj = dt.datetime.strptime(row[0][0:19], "%Y-%m-%dT%H:%M:%S");
            lat = float(row[1]);
            lon = float(row[2]);
            depth = float(row[3]);
            magnitude = float(row[4]);
            myEvent = Catalog_EQ(dt=dtobj, lon=lon, lat=lat, depth=depth, Mag=magnitude, strike=None, dip=None,
                                 rake=None, catname="USGS", bbox=None);
            MyCat.append(myEvent);
    print("Reading %d catalog events from file %s " % (len(MyCat), filename));
    return MyCat;


def read_scsn_txt(filename):
    """
    Read catalog search queries from Southern California Seismic Network
    https://service.scedc.caltech.edu/eq-catalogs/date_mag_loc.php
    """
    MyCat = [];
    ifile = open(filename, 'r');
    for line in ifile:
        if len(line.split()) == 13 and line[0] != '#':
            temp = line.split();
            dtobj = dt.datetime.strptime(temp[0] + "T" + temp[1].split('.')[0], "%Y/%m/%dT%H:%M:%S");
            lat = float(temp[6]);
            lon = float(temp[7]);
            depth = float(temp[8]);
            magnitude = float(temp[4]);
            myEvent = Catalog_EQ(dt=dtobj, lon=lon, lat=lat, depth=depth, Mag=magnitude, strike=None, dip=None,
                                 rake=None, catname="SCSN", bbox=None);
            MyCat.append(myEvent);
    ifile.close();
    print("Reading %d catalog events from file %s " % (len(MyCat), filename));
    return MyCat;


def read_usgs_query_xml_into_MT(filename):
    [Mrr, Mtt, Mpp, Mrt, Mrp, Mtp] = [0, 0, 0, 0, 0, 0];
    [strike, rake, dip, strike2, rake2, dip2] = [0, 0, 0, 0, 0, 0];
    tree = ET.parse(filename)
    root = tree.getroot()
    lev1 = "{http://quakeml.org/xmlns/bed/1.2}eventParameters"
    lev2 = "{http://quakeml.org/xmlns/bed/1.2}event"
    lev3 = "{http://quakeml.org/xmlns/bed/1.2}focalMechanism"
    lev4 = "{http://quakeml.org/xmlns/bed/1.2}momentTensor"
    lev5 = "{http://quakeml.org/xmlns/bed/1.2}tensor"
    for child in root.findall('./' + lev1 + '/' + lev2 + '/' + lev3 + '/' + lev4 + '/' + lev5 + "/*"):
        value = child.tag.split('}')[1];
        # print(value, child[0].text);
        if value == "Mrr":
            Mrr = float(child[0].text);
        if value == "Mtt":
            Mtt = float(child[0].text);
        if value == "Mpp":
            Mpp = float(child[0].text);
        if value == "Mrt":
            Mrt = float(child[0].text);
        if value == "Mrp":
            Mrp = float(child[0].text);
        if value == "Mtp":
            Mtp = float(child[0].text);
    lev4 = "{http://quakeml.org/xmlns/bed/1.2}nodalPlanes"
    lev5 = "{http://quakeml.org/xmlns/bed/1.2}nodalPlane1"
    for child in root.findall('./' + lev1 + '/' + lev2 + '/' + lev3 + '/' + lev4 + '/' + lev5 + "/*"):
        value = child.tag.split('}')[1];
        if value == "strike":
            strike = float(child[0].text);
        if value == "dip":
            dip = float(child[0].text);
        if value == "rake":
            rake = float(child[0].text);
    lev5 = "{http://quakeml.org/xmlns/bed/1.2}nodalPlane2"
    for child in root.findall('./' + lev1 + '/' + lev2 + '/' + lev3 + '/' + lev4 + '/' + lev5 + "/*"):
        value = child.tag.split('}')[1];
        if value == "strike":
            strike2 = float(child[0].text);
        if value == "dip":
            dip2 = float(child[0].text);
        if value == "rake":
            rake2 = float(child[0].text);
    return [Mrr, Mtt, Mpp, Mrt, Mrp, Mtp, strike, dip, rake, strike2, dip2, rake2];


def read_SIL_catalog(filename):
    """Take a catalog from Iceland source"""
    df = pandas.read_csv(filename);
    lons = [float(x) for x in df["SIL_lon"]];
    lats = [float(x) for x in df["SIL_lat"]];
    depth = [float(x) for x in df["SIL_dep"]];
    mag = [float(x) for x in df["SIL_mag"]];
    dtarray = [dt.datetime.strptime(x, '%Y/%m/%d %H:%M:%S') for x in df["Datetime"]];
    MyCat = [];
    for i in range(len(dtarray)):
        myEvent = Catalog_EQ(dt=dtarray[i], lon=lons[i], lat=lats[i], depth=depth[i], Mag=mag[i], strike=None,
                             dip=None, rake=None, catname="SIL", bbox=None);
        MyCat.append(myEvent);
    print("Reading %d catalog events from file %s " % (len(MyCat), filename));
    return MyCat;


def read_associated_MT_file(filename):
    # A special catalog for the Iceland case: time, magnitude, and xml file (a manually created lookup table)
    print("Reading associated mt file %s " % filename);
    myCat = [];
    ifile = open(filename);
    for line in ifile:
        if line.split()[0] == "#":
            continue;
        else:
            dtstr = line.split()[0];
            dtobj = dt.datetime.strptime(dtstr, "%Y-%m-%d-%H-%M-%S");
            mag = float(line.split()[1]);
            mt_xml_file = line.split()[2];
            # Depends on which plane you want to take (shouldn't make difference)
            [_, _, _, _, _, _, _, _, _, strike, dip, rake] = read_usgs_query_xml_into_MT(mt_xml_file);
            myEvent = Catalog_EQ(dt=dtobj, lon=None, lat=None, depth=None, Mag=mag, strike=strike,
                                 dip=dip, rake=rake, catname="", bbox=None);
            myCat.append(myEvent);
    ifile.close();
    return myCat;


def read_simple_catalog_txt(filename):
    """Reading a very simple .txt format for earthquake catalogs"""
    print("Reading Catalog in %s " % filename);
    [datestrs, lon, lat, depth, Mag] = np.loadtxt(filename, dtype={'names': ('datestr', 'lon', 'lat', 'depth', 'mag'),
                                                                   'formats': (
                                                                       'U19', float, float, float, float)},
                                                  unpack=True, skiprows=1);
    dtarray = [dt.datetime.strptime(i, "%Y-%m-%d-%H-%M-%S") for i in datestrs];
    MyCat = [];
    for i in range(len(dtarray)):
        myEvent = Catalog_EQ(dt=dtarray[i], lon=lon[i], lat=lat[i], depth=depth[i], Mag=Mag[i], strike=None,
                             dip=None, rake=None, catname="", bbox=None);
        MyCat.append(myEvent);
    print("Reading %d catalog events from file %s " % (len(MyCat), filename));
    return MyCat;


def read_wech(filename):
    start = 0;
    MyCat = [];
    ifile = open(filename, 'r');
    for line in ifile:
        temp = line.split();
        if 'yyyy-mm-dd' in line or 'DateTime' in line:  # If the header is still inside.
            start = 1;
            continue;
        if len(temp) == 5:  # If we've removed the header already.
            start = 1;
        if start == 1 and len(temp) > 0:
            onedate = dt.datetime.strptime(temp[0] + ' ' + temp[1].split('.')[0], "%Y-%m-%d %H:%M:%S");
            myEvent = Catalog_EQ(dt=onedate, lon=float(temp[3]), lat=float(temp[2]), depth=np.nan, Mag=np.nan,
                                 strike=None, dip=None, rake=None, catname="", bbox=None);
            MyCat.append(myEvent);
        if len(MyCat) == 180000:
            break;
    ifile.close();
    print("Successfully read %d tremor counts from %s " % (len(MyCat), filename));
    return MyCat;


def read_wech_custom(filename):
    MyCat = [];
    start = 0;
    ifile = open(filename, 'r');
    for line in ifile:
        temp = line.split();
        if 'DateTime' in line:  # If the header is still inside.
            start = 1;
            continue;
        if len(temp) == 5:  # If we've removed the header already.
            start = 1;
        if start == 1 and len(temp) > 0:
            onedt = dt.datetime.strptime(temp[0] + ' ' + temp[1].split('.')[0], "%Y-%m-%d %H:%M:%S");
            myEvent = Catalog_EQ(dt=onedt, lon=float(temp[2]), lat=float(temp[3]), depth=np.nan, Mag=np.nan,
                                 strike=None, dip=None, rake=None, catname="", bbox=None);
            MyCat.append(myEvent);
        if len(MyCat) == 180000:
            break;
    ifile.close();
    print("Successfully read %d tremor counts from %s " % (len(MyCat), filename));
    return MyCat;


def read_ide_tremor(filename):
    MyCat = [];
    ifile = open(filename, 'r');
    for line in ifile:
        temp = line.split(',');
        if len(temp) > 1:
            onedt = dt.datetime.strptime(temp[0] + ' ' + temp[1], "%Y-%m-%d %H:%M:%S");
            myEvent = Catalog_EQ(dt=onedt, lon=float(temp[2]), lat=float(temp[3]), depth=np.nan, Mag=np.nan,
                                 strike=None, dip=None, rake=None, catname="", bbox=None);
            MyCat.append(myEvent)
    ifile.close();
    print("Successfully read %d tremor counts from %s " % (len(MyCat), filename));
    return MyCat;


def read_pnsn052019_file(filename):
    MyCat = [];
    ifile = open(filename, 'r');
    ifile.readline();
    for line in ifile:
        temp = line.split(',');
        if len(temp) <= 2:
            continue;
        if temp[0] == 'lat':
            continue;
        onedt = dt.datetime.strptime(temp[3], " %Y-%m-%d %H:%M:%S ");
        myEvent = Catalog_EQ(dt=onedt, lon=float(temp[1]), lat=float(temp[0]), depth=np.nan, Mag=np.nan,
                             strike=None, dip=None, rake=None, catname="", bbox=None);
        MyCat.append(myEvent);
    ifile.close();
    return MyCat;


# ---------- WRITE EARTHQUAKE CATALOGS --------------

def write_simple_catalog_txt(MyCat, outfile):
    """Writing a very simple .txt format for earthquake catalogs"""
    print("Writing Catalog in %s " % outfile);
    ofile = open(outfile, 'w');
    # Adding header line
    if MyCat[0].bbox is not None:
        bbox_string = ' within ' + str(MyCat[0].bbox[0]) + '/' + str(MyCat[0].bbox[1]) + '/' + \
                      str(MyCat[0].bbox[2]) + '/' + str(MyCat[0].bbox[3]) + '/' + str(MyCat[0].bbox[4]) + '/' + \
                      str(MyCat[0].bbox[5]) + '/' + dt.datetime.strftime(MyCat[0].bbox[6], "%Y%m%d") + '/' + \
                      dt.datetime.strftime(MyCat[0].bbox[7], "%Y%m%d");
    else:
        bbox_string = '';
    ofile.write("# %s catalog %s\n" % (MyCat[0].catname, bbox_string));
    ofile.write("# date, lon, lat, depth, magnitude\n");
    for item in MyCat:
        datestr = dt.datetime.strftime(item.dt, "%Y-%m-%d-%H-%M-%S");
        ofile.write("%s %f %f %.3f %.2f\n" % (datestr, item.lon, item.lat, item.depth, item.Mag));
    ofile.close();
    return;


def write_location_catalog_txt(MyCat, outfile):
    """Writing a very simple .txt format for earthquake catalogs"""
    print("Writing Catalog in %s " % outfile);
    ofile = open(outfile, 'w');
    # Adding header line
    if MyCat[0].bbox is not None:
        bbox_string = ' within ' + str(MyCat[0].bbox[0]) + '/' + str(MyCat[0].bbox[1]) + '/' + \
                      str(MyCat[0].bbox[2]) + '/' + str(MyCat[0].bbox[3]) + '/' + str(MyCat[0].bbox[4]) + '/' + \
                      str(MyCat[0].bbox[5]) + '/' + dt.datetime.strftime(MyCat[0].bbox[6], "%Y%m%d") + '/' + \
                      dt.datetime.strftime(MyCat[0].bbox[7], "%Y%m%d");
    else:
        bbox_string = '';
    ofile.write("# %s catalog %s\n" % (MyCat[0].catname, bbox_string));
    ofile.write("# lon, lat\n");
    for item in MyCat:
        ofile.write("%f %f\n" % (item.lon, item.lat));
    ofile.close();
    return;


# ---------- READ EARTHQUAKE RATES --------------
def read_earthquake_rates(infile):
    # Matching the format of write_seismicity_rates() in plotting_functions.
    print("Reading %s " % infile);
    dtarray, rates = [], [];
    ifile = open(infile, 'r');
    for line in ifile:
        if line.split()[0] == "#":
            continue;
        else:
            dtarray.append(dt.datetime.strptime(line.split()[0], "%Y%m%d"));
            rates.append(float(line.split()[1]));
    return [dtarray, rates];
