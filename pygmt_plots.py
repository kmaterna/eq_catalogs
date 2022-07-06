
import pygmt
import datetime as dt
from . import catalog_functions

def simple_pygmt_map(mycat, filename, legendfile=None, scalelength=1, cbar_interval=1.0, map_frame_int=0.05,
                     region=None, symbolscale=0.14):
    """A basic pygmt plot for earthquake catalogs, color-coded by depth and size-coded by magnitude."""
    lons = [eq.lon for eq in mycat];
    lats = [eq.lat for eq in mycat];
    depths = [eq.depth for eq in mycat];
    mags = [symbolscale*eq.Mag for eq in mycat];  # scaling for symbol size

    if region is None:
        region = [min(lons), max(lons), min(lats), max(lats)];
    pygmt.makecpt(cmap="turbo", series=str(min(depths)) + "/" + str(max(depths)) + "/"+str(0.1),
                  output="mycpt.cpt", background=True);
    proj = "M7i"
    fig = pygmt.Figure()
    fig.coast(region=region, projection=proj, borders='2', shorelines='0.5p,black', water='lightblue',
              resolution='h', frame=str(map_frame_int),
              map_scale="jBR+c"+str(region[2])+"+o0.6/0.7+w"+str(scalelength)+"k");
    fig.plot(x=lons, y=lats, color=depths, size=mags, style='c', cmap="mycpt.cpt", pen="thin,black");  # earthquakes
    fig.colorbar(position="jBr+w3.5i/0.2i+o3.5c/1.5c+h", cmap="mycpt.cpt",
                 frame=["x" + str(cbar_interval), "y+L\"km\""]);
    starttime, endtime = catalog_functions.get_start_stop_time(mycat);
    startstr = dt.datetime.strftime(starttime, "%Y-%m-%d");
    endstr = dt.datetime.strftime(endtime, "%Y-%m-%d");
    fig.text(text=startstr + " to " + endstr + ", "+str(len(mycat))+" events", position='TR',
             font="12p,Helvetica,black", pen="0.5p,black", fill='white', offset="-0.1/-0.1");
    if legendfile:
        fig.legend(position="JBL+jBL+o0.2c", spec=legendfile, box='+gwhite+p0.5p', projection=proj);   # user-provided
    fig.savefig(filename);
    print("Saving pygmt map %s" % filename);
    return;
