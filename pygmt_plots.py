
import pygmt

def simple_pygmt_map(mycat, filename):
    """A basic pygmt plot for earthquake catalogs, color-coded by depth and size-coded by magnitude."""
    lons = [eq.lon for eq in mycat];
    lats = [eq.lat for eq in mycat];
    depths = [eq.depth for eq in mycat];
    mags = [0.14*eq.Mag for eq in mycat];  # scaling for symbol size

    region = [min(lons), max(lons), min(lats), max(lats)];
    pygmt.makecpt(cmap="jet", series=str(min(depths)) + "/" + str(max(depths)) + "/"+str(0.1),
                  output="mycpt.cpt", background=True);
    proj = "M7i"
    fig = pygmt.Figure()
    fig.coast(region=region, projection=proj, borders='2', shorelines='0.5p,black', water='lightblue',
              resolution='h', frame="0.05");
    fig.plot(x=lons, y=lats, color=depths, size=mags, style='c', cmap="mycpt.cpt", pen="thin,black");  # earthquakes
    fig.colorbar(position="jBr+w3.5i/0.2i+o2.5c/1.5c+h", cmap="mycpt.cpt", frame=["x" + str(1.0), "y+L\"km\""]);
    fig.savefig(filename);
    return;
