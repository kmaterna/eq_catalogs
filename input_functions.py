# Functions to read and write various earthquake catalog formats
# November 2020


import numpy as np
import matplotlib.pyplot as plt  
import datetime as dt
import csv
from .eqcat_object import Catalog


def input_qtm(filename):
	# Designed to use the txt file format of Ross et al. (2019)'s QTM catalog
	# downloaded from https://scedc.caltech.edu/research-tools/altcatalogs.html
	print("Reading file %s " % filename);
	print(dt.datetime.now());
	
	# This takes 15 seconds (surprisingly, np.loadtxt takes 30 seconds to do the same thing)
	year = []; month = []; day = []; hour = []; minute = []; second = []; lat = []; lon = []; depth = []; mag = [];
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
			newdate = dt.datetime.strptime(year[i]+month[i]+day[i]+hour[i]+minute[i], "%Y%m%d%H%M");
		except ValueError:  # WE ACTUALLY GOT AN EARTHQUAKE DURING A LEAP SECOND!!!! 
			print("You may have a problem at: ");
			print(year[i]+month[i]+day[i]+hour[i]+minute[i]);
			newdate = dt.datetime.strptime(year[i]+month[i]+day[i]+hour[i], "%Y%m%d%H");
		dtarray.append(newdate);
	MyCat = Catalog(dtarray=dtarray, lon=lon, lat=lat, depth=depth, Mag=mag, strike=None, dip=None, rake=None, catname="QTM");
	print("done at : ", dt.datetime.now());
	return MyCat;


def input_shearer_cat(filename):
	# Useful for the Shearer Yang Catalog
	print("Reading file %s " % filename);
	ifile = open(filename);
	dtarray = []; latitude = []; longitude = []; depth = []; magnitude = [];
	for line in ifile:
		temp = line.split();
		year = temp[0]
		month = temp[1]
		day = temp[2]
		hour = temp[3]
		minute = temp[4] 
		second = temp[5][0:2]
		if int(second)>59:
			print("We found a leap second at: ",year, month, day, hour, minute, second);
			print("Turning it back one second")
			second = '59'
		if hour == '-1':
			print("We found a problem at: ",year, month, day, hour, minute, second);
			print("Turning it forward one second")
			hour = '00'
			minute = '00'
			second = '00'
		eqdate = dt.datetime.strptime(year+" "+month+" "+day+" "+hour+" "+minute+" "+second,"%Y %m %d %H %M %S");
		dtarray.append(eqdate);
		latitude.append(float(temp[7]))
		longitude.append(float(temp[8]))
		depth.append(float(temp[9]))
		magnitude.append(float(temp[10]));
	ifile.close();

	MyCat = Catalog(dtarray=dtarray, lon=longitude, lat=latitude, depth=depth, Mag=magnitude, strike=None, dip=None, rake=None, catname="Shearer");
	return MyCat;


def read_Wei_2015_supplement(filename):
	print("Reading earthquake catalog from file %s " % filename)
	lon, lat = [], []; 
	depth, mag =[], [];
	strike, dip, rake = [], [], [];
	ifile = open(filename);
	for line in ifile:
		lon.append(float(line.split()[2]));
		lat.append(float(line.split()[1]));
		depth.append(float(line.split()[3]));
		mag.append(float(line.split()[4]));
		fm.append(line.split()[5]);
		fm = line.split()[5];
		strike.append(float(fm.split('/')[0]));
		dip.append(float(fm.split('/')[1]));
		rake.append(float(fm.slplit('/')[2]));
	ifile.close();
	MyCat = Catalog(dtarray=None, lon=lon, lat=lat, depth=depth, Mag=mag, strike=strike, dip=dip, rake=rake, catname='Wei_2015');
	return MyCat;


def read_intxt_fms(filename, catname='Intxt'):
	# Useful for .intxt file formats, as defined in the elastic modeling code
	print("Reading earthquake catalog from file %s " % filename);
	ifile = open(filename,'r');
	lon, lat = [], []; 
	depth, mag =[], [];	
	strike, dip, rake = [], [], [];
	for line in ifile:
		temp=line.split();
		if len(temp)==0:
			continue;
		if temp[0]=="S:":
			temp=line.split();
			strike.append(float(temp[1]));
			rake.append(float(temp[2]));
			dip.append(float(temp[3]));
			lon.append(float(temp[4]));
			lat.append(float(temp[5]));
			depth.append(float(temp[6]));
			mag.append(float(temp[7]));
	MyCat = Catalog(dtarray=None, lon=lon, lat=lat, strike=strike, dip=dip, rake=rake, depth=depth, Mag=mag, catname=catname);
	ifile.close();
	return MyCat;


def read_usgs_website_csv(filename):
	# When you hit the 'DOWNLOAD' button on the USGS website
	dtarray = []; latitude = []; longitude = []; depth = []; magnitude = [];
	with open(filename) as csvfile:
		mycatreader = csv.reader(csvfile);
		for row in mycatreader:
			if row[0]=='time':
				continue;
			dtarray.append(dt.datetime.strptime(row[0][0:19],"%Y-%m-%dT%H:%M:%S"));
			latitude.append(float(row[1]));
			longitude.append(float(row[2]));
			depth.append(float(row[3]));
			magnitude.append(float(row[4]));

	MyCat = Catalog(dtarray=dtarray, lon=longitude, lat=latitude, depth=depth, Mag=magnitude, strike=None, dip=None, rake=None, catname="USGS");
	return MyCat;


def read_simple_catalog_txt(filename):
	# Reading a very simple .txt format for earthquake catalogs
	print("Reading Catalog in %s " % filename);
	[datestrs, lon, lat, depth, Mag] = np.loadtxt(filename, dtype={'names': ('datestr', 'lon', 'lat', 'depth', 'mag'),
																   'formats': ('U19', np.float, np.float, np.float, np.float)
																   }, unpack=True);
	dtarray = [dt.datetime.strptime(i, "%Y-%m-%d-%H-%M-%S") for i in datestrs];
	MyCat = Catalog(dtarray=dtarray, lon=lon, lat=lat, depth=depth, Mag=Mag, strike=None, dip=None, rake=None, catname='');
	return MyCat;


def write_simple_catalog_txt(MyCat, outfile):
	# Writing a very simple .txt format for earthquake catalogs
	print("Writing Catalog in %s " % outfile );
	ofile = open(outfile, 'w');
	for i in range(len(MyCat.dtarray)):
		datestr = dt.datetime.strftime(MyCat.dtarray[i], "%Y-%m-%d-%H-%M-%S");
		ofile.write("%s %f %f %.3f %.2f\n" % (datestr, MyCat.lon[i], MyCat.lat[i], MyCat.depth[i], MyCat.Mag[i]) );
	ofile.close();
	return;

