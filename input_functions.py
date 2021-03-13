# Functions to read and write various earthquake catalog formats


import numpy as np
import datetime as dt
import csv
from .eqcat_object import Catalog
import xml.etree.ElementTree as ET
import pandas


def input_qtm(filename):
    """
    Input the txt file format of Ross et al. (2019)'s QTM catalog
    downloaded from https://scedc.caltech.edu/research-tools/altcatalogs.html
    """
    print("Reading file %s " % filename);
    print(dt.datetime.now());

    # This takes 15 seconds (surprisingly, np.loadtxt takes 30 seconds to do the same thing)
    year, month, day = [], [], [];
    hour, minute, second = [], [], [];
    lat, lon = [], [];
    depth, mag = [], [];
    ifile = open(filename, 'r');
    ifile.readline();
    for line in ifile:
        temp = line.split();
        year.append(temp[0]);
        month.append(temp[1]);
        day.append(temp[2]);
        hour.append(temp[3]);
        minute.append(temp[4]);
        second.append(temp[5]);
        lat.append(float(temp[7]));
        lon.append(float(temp[8]));
        depth.append(float(temp[9]));
        mag.append(float(temp[10]));
    ifile.close();

    dtarray = [];
    for i in range(len(year)):
        try:
            newdate = dt.datetime.strptime(year[i] + month[i] + day[i] + hour[i] + minute[i], "%Y%m%d%H%M");
        except ValueError:  # WE ACTUALLY GOT AN EARTHQUAKE DURING A LEAP SECOND!!!!
            print("You may have a problem at: ");
            print(year[i] + month[i] + day[i] + hour[i] + minute[i]);
            newdate = dt.datetime.strptime(year[i] + month[i] + day[i] + hour[i], "%Y%m%d%H");
        dtarray.append(newdate);
    MyCat = Catalog(dtarray=dtarray, lon=lon, lat=lat, depth=depth, Mag=mag, strike=None, dip=None, rake=None,
                    catname="QTM", bbox=None);
    print("done at : ", dt.datetime.now());
    return MyCat;


def input_shearer_cat(filename):
    """ Read the Shearer Yang Catalog """
    print("Reading file %s " % filename);
    ifile = open(filename);
    latitude, longitude = [], [];
    dtarray, depth, magnitude = [], [], [];
    for line in ifile:
        temp = line.split();
        year = temp[0]
        month = temp[1]
        day = temp[2]
        hour = temp[3]
        minute = temp[4]
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
        dtarray.append(eqdate);
        latitude.append(float(temp[7]))
        longitude.append(float(temp[8]))
        depth.append(float(temp[9]))
        magnitude.append(float(temp[10]));
    ifile.close();

    MyCat = Catalog(dtarray=dtarray, lon=longitude, lat=latitude, depth=depth, Mag=magnitude, strike=None, dip=None,
                    rake=None, catname="Shearer", bbox=None);
    return MyCat;


def read_Wei_2015_supplement(filename):
    print("Reading earthquake catalog from file %s " % filename)
    lon, lat = [], [];
    depth, mag = [], [];
    strike, dip, rake = [], [], [];
    ifile = open(filename);
    for line in ifile:
        lon.append(float(line.split()[2]));
        lat.append(float(line.split()[1]));
        depth.append(float(line.split()[3]));
        mag.append(float(line.split()[4]));
        fm = line.split()[5];
        strike.append(float(fm.split('/')[0]));
        dip.append(float(fm.split('/')[1]));
        rake.append(float(fm.split('/')[2]));
    ifile.close();
    MyCat = Catalog(dtarray=None, lon=lon, lat=lat, depth=depth, Mag=mag, strike=strike, dip=dip, rake=rake,
                    catname='Wei_2015', bbox=None);
    return MyCat;


def read_intxt_fms(filename, catname='Intxt'):
    """Read focal mechanisms/rect faults from .intxt file format, as defined in the elastic modeling code"""
    print("Reading earthquake catalog from file %s " % filename);
    ifile = open(filename, 'r');
    lon, lat, depth, mag = [], [], [], [];
    strike, dip, rake = [], [], [];
    for line in ifile:
        temp = line.split();
        if len(temp) == 0:
            continue;
        if temp[0] == "S:":
            temp = line.split();
            strike.append(float(temp[1]));
            rake.append(float(temp[2]));
            dip.append(float(temp[3]));
            lon.append(float(temp[4]));
            lat.append(float(temp[5]));
            depth.append(float(temp[6]));
            mag.append(float(temp[7]));
    MyCat = Catalog(dtarray=None, lon=lon, lat=lat, strike=strike, dip=dip, rake=rake, depth=depth, Mag=mag,
                    catname=catname, bbox=None);
    ifile.close();
    return MyCat;


def read_usgs_website_csv(filename):
    """Read the files when you hit the 'DOWNLOAD' button on the USGS earthquakes website"""
    dtarray = [];
    lat, lon = [], [];
    depth, magnitude = [], [];
    with open(filename) as csvfile:
        mycatreader = csv.reader(csvfile);
        for row in mycatreader:
            if row[0] == 'time':
                continue;
            dtarray.append(dt.datetime.strptime(row[0][0:19], "%Y-%m-%dT%H:%M:%S"));
            lat.append(float(row[1]));
            lon.append(float(row[2]));
            depth.append(float(row[3]));
            magnitude.append(float(row[4]));

    MyCat = Catalog(dtarray=dtarray, lon=lon, lat=lat, depth=depth, Mag=magnitude, strike=None, dip=None,
                    rake=None, catname="USGS", bbox=None);
    return MyCat;


def read_usgs_query_xml_into_MT(filename):
    [Mrr, Mtt, Mpp, Mrt, Mrp, Mtp] = [0, 0, 0, 0, 0, 0];
    tree = ET.parse(filename)
    root = tree.getroot()
    lev1 = "{http://quakeml.org/xmlns/bed/1.2}eventParameters"
    lev2 = "{http://quakeml.org/xmlns/bed/1.2}event"
    lev3 = "{http://quakeml.org/xmlns/bed/1.2}focalMechanism"
    lev4 = "{http://quakeml.org/xmlns/bed/1.2}momentTensor"
    lev5 = "{http://quakeml.org/xmlns/bed/1.2}tensor"
    for child in root.findall('./'+lev1+'/'+lev2+'/'+lev3+'/'+lev4+'/'+lev5+"/*"):
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
    return [Mrr, Mtt, Mpp, Mrt, Mrp, Mtp];


def read_SIL_catalog(filename):
    """Take a catalog from Iceland source"""
    print("Reading Catalog in %s " % filename);
    df = pandas.read_csv(filename);
    lons = [float(x) for x in df["SIL_lon"]];
    lats = [float(x) for x in df["SIL_lat"]];
    depth = [float(x) for x in df["SIL_dep"]];
    mag = [float(x) for x in df["SIL_mag"]];
    dtarray = [dt.datetime.strptime(x, '%Y/%m/%d %H:%M:%S') for x in df["Datetime"]];
    MyCat = Catalog(dtarray=dtarray, lon=lons, lat=lats, depth=depth, Mag=mag, strike=None, dip=None,
                    rake=None, catname="SIL", bbox=None);
    return MyCat;


def read_simple_catalog_txt(filename):
    """Reading a very simple .txt format for earthquake catalogs"""
    print("Reading Catalog in %s " % filename);
    [datestrs, lon, lat, depth, Mag] = np.loadtxt(filename, dtype={'names': ('datestr', 'lon', 'lat', 'depth', 'mag'),
                                                                   'formats': (
                                                                       'U19', np.float, np.float, np.float, np.float)},
                                                  unpack=True, skiprows=1);
    dtarray = [dt.datetime.strptime(i, "%Y-%m-%d-%H-%M-%S") for i in datestrs];
    MyCat = Catalog(dtarray=dtarray, lon=lon, lat=lat, depth=depth, Mag=Mag, strike=None, dip=None,
                    rake=None, catname='', bbox=None);
    return MyCat;


def write_simple_catalog_txt(MyCat, outfile):
    """Writing a very simple .txt format for earthquake catalogs"""
    print("Writing Catalog in %s " % outfile);
    ofile = open(outfile, 'w');
    # Adding header line
    if MyCat.bbox is not None:
        bbox_string = ' within '+str(MyCat.bbox[0])+'/'+str(MyCat.bbox[1])+'/' +\
                      str(MyCat.bbox[2])+'/'+str(MyCat.bbox[3])+'/'+str(MyCat.bbox[4])+'/' +\
                      str(MyCat.bbox[5])+'/'+dt.datetime.strftime(MyCat.bbox[6], "%Y%m%d")+'/' +\
                      dt.datetime.strftime(MyCat.bbox[7], "%Y%m%d");
    else:
        bbox_string = '';
    ofile.write("# %s catalog %s\n" % (MyCat.catname, bbox_string) );
    ofile.write("# date, lon, lat, depth, magnitude\n");
    for i in range(len(MyCat.dtarray)):
        datestr = dt.datetime.strftime(MyCat.dtarray[i], "%Y-%m-%d-%H-%M-%S");
        ofile.write("%s %f %f %.3f %.2f\n" % (datestr, MyCat.lon[i], MyCat.lat[i], MyCat.depth[i], MyCat.Mag[i]));
    ofile.close();
    return;
