# Functions that operate on earthquake catalogs
# Doing useful things

import numpy as np
import matplotlib.pyplot as plt
from .eqcat_object import Catalog

def restrict_cat_box(catalog, bbox):
	# A function on earthquake catalogs
	# Limit a catalog to the provided bounding box in lon, lat, depth, and optionally time
	# losing the focal mechanisms for the moment
	new_dtarray = []; new_lon = []; new_lat = []; new_depth = []; new_Mag = [];
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
	MyCat = Catalog(dtarray=new_dtarray, lon=new_lon, lat=new_lat, depth=new_depth, Mag=new_Mag, fm=None);
	print("Returning %d out of %d events" % (len(MyCat.depth), len(catalog.depth)) );
	return MyCat;


def make_cumulative_stack(MyCat):
	# Take a catalog
	# Returns two arrays: time and seismicity
	# They can be plotted for a cumulative seismicity plot
	dt_total = []; eq_total = []; adding_sum = 0;
	dt_total.append(MyCat.dtarray[0]);
	eq_total.append(0);
	for i in range(len(MyCat.lon)):	
		dt_total.append(MyCat.dtarray[i]);
		eq_total.append(adding_sum);
		adding_sum = adding_sum+1;
		eq_total.append(adding_sum);
		dt_total.append(MyCat.dtarray[i]);
	return dt_total, eq_total;


def make_lollipop_plot(MyCat, filename):
	plt.figure(dpi=300, figsize=(10,7));
	for i in range(len(MyCat.dtarray)):
		plt.plot(MyCat.dtarray[i], MyCat.Mag[i], marker='o', markersize=10, linewidth=0,color='black');
		plt.plot([MyCat.dtarray[i], MyCat.dtarray[i]],[0,MyCat.Mag[i]], color='black',linewidth=1);
	plt.ylabel('Magnitude',fontsize=20);
	plt.xlabel('Time',fontsize=20);
	plt.gca().tick_params(axis='both', which='major', labelsize=16)
	plt.ylim([2.5, 5.0])
	plt.savefig(filename);
	return;
