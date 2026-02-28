from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel
import metpy.calc as mpcalc
from metpy.units import units
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import xarray as xr
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

experiment="ctl"
level=925
time_str="2009-12-27_03"
wrfout_dir=f"/DATA/USER/ozeki/MyWRF/output_data/200912etc_25km_{experiment}"
fig_dir=f"/DATA/USER/ozeki/MyWRF/fig/200912etc_25km_{experiment}"
wrfout=Dataset(f"{wrfout_dir}/wrfout_d01_{time_str}:00:00")

z=getvar(wrfout,"z",units="m")
u=getvar(wrfout,"ua")
v=getvar(wrfout,"va")
cart_proj=get_cartopy(z)
p=getvar(wrfout,"pressure")

dx=25000.0*units.meter
dy=25000.0*units.meter

z925=interplevel(z,p,925)
u925=interplevel(u,p,925)
u925=u925*units.meter/units.second
v925=interplevel(v,p,925)
v925=v925*units.meter/units.second
print(u925)
print(v925)
z925=mpcalc.smooth_gaussian(z925,3)
lat=getvar(wrfout,"lat")*units.degrees
lats,lons=latlon_coords(z925)

print(cart_proj)

Ug,Vg=mpcalc.geostrophic_wind(z925,dx,dy,lat,x_dim=-1,y_dim=-2)
print(Ug)
print(Vg)

#Ua1,Va1=mpcalc.ageostrophic_wind(z500,u500,v500,dx,dy,lat,x_dim=-1,y_dim=-2)
Ua=u925-Ug
Va=v925-Vg

#通常の風
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,45])

#contour=ax.contour(lons.values,lats.values,z925.values,transform=ccrs.PlateCarree())

step=1
qx,qy,qk=1.1,-0.1,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  u925.values[::step,::step],
  v925.values[::step,::step],
  scale=400,
  color="blue",
  transform=ccrs.PlateCarree())

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")
gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
######

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{experiment}-{time_str}UTC",fontsize=20)
#ax.set_title("Elevation_25km_grid")

plt.savefig(f"{fig_dir}/{level}wind{time_str}.png")

plt.close("all")


fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,45])

contour=ax.contour(lons.values,lats.values,z925.values,levels=np.arange(720,800,10),colors="black",transform=ccrs.PlateCarree())
ax.clabel(contour)

step=1
qx,qy,qk=1.1,-0.1,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  Ug.values[::step,::step],
  Vg.values[::step,::step],
  scale=400,
  color="green",
  transform=ccrs.PlateCarree())

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")
gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
######

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{experiment}-{time_str}UTC",fontsize=20)
#ax.set_title("Elevation_25km_grid")

plt.savefig(f"{fig_dir}/{level}geostrophic_wind{time_str}.png")

plt.close("all")

fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,45])

step=1
qx,qy,qk=1.1,-0.1,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  Ua.values[::step,::step],
  Va.values[::step,::step],
  scale=300,
  color="red",
  transform=ccrs.PlateCarree())

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")
gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
######

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{experiment}{time_str}UTC",fontsize=20)
#ax.set_title("Elevation_25km_grid")

plt.savefig(f"{fig_dir}/{level}ageostrophic_wind{time_str}.png")

plt.close("all")
wrfout.close()
