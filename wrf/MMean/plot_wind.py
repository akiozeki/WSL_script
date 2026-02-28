#from __from__ import print_function
from datetime import datetime,timedelta
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

uvar="ua_m"
vvar="va_m"
#z or z_m(基本場) or z_a(擾乱)
varlabel="m/s"
factor=1
lev=850

dx=25000
dy=25000

ex1="CTL"
ex2="ME00"
n_member=1
moving_day=7

cmaplev=np.arange(1240,1600,40)
cmaplev_d=np.arange(-21,23,2)

case="2025DJF"
wrfout_dir=f"/home/akioz/MyWRF/output/{case}"
input_dir=f"/home/akioz/calculate/wrf/{case}/MMean"
fig_dir=f"/home/akioz/fig/wrf/{case}"

sdate=datetime(2024,12,1,0)
edate=datetime(2025,2,28,18)
print(f"Set Time : {sdate}----{edate}")

##座標系情報を得るために任意のwrfoutファイルを開く
sy=sdate.year
sm=sdate.month
sd=sdate.day
sh=sdate.hour


if n_member == 1 :
  coord_ds=Dataset(f"{wrfout_dir}/{ex1}/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")
else :
  coord_ds=Dataset(f"{wrfout_dir}/{ex1}/n1/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")

land=getvar(coord_ds,"LANDMASK")
cart_proj=get_cartopy(land)
print("projection:",cart_proj)
lats,lons=latlon_coords(land)
ter1=getvar(coord_ds,"ter",units="m")
ter1=np.ma.masked_where(land != 1,ter1)
#print(lats)
coord_ds.close()

if n_member == 1 :
  coord_ds2=Dataset(f"{wrfout_dir}/{ex2}/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")
else :
  coord_ds2=Dataset(f"{wrfout_dir}/{ex2}/n1/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")
land2=getvar(coord_ds2,"LANDMASK")
ter2=getvar(coord_ds2,"ter",units="m")
ter2=np.ma.masked_where(land2 != 1,ter2)

coord_ds2.close()

udfile1=f"{input_dir}/{ex1}_ua{lev}_{moving_day}dMean.nc"
udfile2=f"{input_dir}/{ex2}_ua{lev}_{moving_day}dMean.nc"
vdfile1=f"{input_dir}/{ex1}_va{lev}_{moving_day}dMean.nc"
vdfile2=f"{input_dir}/{ex2}_va{lev}_{moving_day}dMean.nc"


uds1=xr.open_dataset(udfile1)
uds2=xr.open_dataset(udfile2)
vds1=xr.open_dataset(vdfile1)
vds2=xr.open_dataset(vdfile2)

u1=uds1[uvar]
u2=uds2[uvar]
v1=vds1[vvar]
v2=vds2[vvar]

#dz_dy1=-np.gradient(z1,dy,axis=1)
#dz_dy2=-np.gradient(z2,dy,axis=1)
#*z(time,south_north,west_east)

#print(dz_dy1)
#print(dz_dy2)

mean_u1=u1.mean(dim="time",skipna=True)
mean_u2=u2.mean(dim="time",skipna=True)
mean_v1=v1.mean(dim="time",skipna=True)
mean_v2=v2.mean(dim="time",skipna=True)
#  mean_dz_dy1=np.nanmean(dz_dy1,axis=0)
#  mean_dz_dy2=np.nanmean(dz_dy2,axis=0)

#  mean_dz_dy1=np.nanmean(mean_dz_dy1,axis=2)
#  mean_dz_dy2=np.nanmean(mean_dz_dy2,axis=2)
#軸番号は要確認

print("u1",mean_u1)
print("v2",mean_v2)
#print("dz_dy1",mean_dz_dy1)
#print("dz_dy2",mean_dz_dy2)

uds1.close()
vds2.close()
uds2.close()
vds2.close()

dif_u=mean_u1 - mean_u2
dif_v=mean_v1 - mean_v2

###Plot
##ex1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
#ax.set_extent([127,145,35,44])

step=12
qx,qy,qk=1.1,-0.5,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  mean_u1.values[::step,::step],
  mean_v1.values[::step,::step],
  scale=100,
  width=0.01,
  color="blue",
  transform=ccrs.PlateCarree()
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")
#shade2=ax.contourf(lons,lats,ter1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())


gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-Wind{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex1}/{ex1}_Wind{lev}_{moving_day}dMean.png")
plt.close("all")

#ex2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
#ax.set_extent([127,145,35,44])

step=12
qx,qy,qk=1.1,-0.5,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  mean_u2.values[::step,::step],
  mean_v2.values[::step,::step],
  scale=100,
  width=0.01,
  color="blue",
  transform=ccrs.PlateCarree()
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")
#shade2=ax.contourf(lons,lats,ter2,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-Z{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/{ex2}_Wind{lev}_{moving_day}dMean.png")
plt.close("all")

#Difference
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
#ax.set_extent([127,145,35,44])

step=12
qx,qy,qk=1.1,-0.5,5
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  dif_u.values[::step,::step],
  dif_v.values[::step,::step],
  scale=50,
  width=0.01,
  color="black",
  transform=ccrs.PlateCarree()
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")
#shade2=ax.contourf(lons,lats,ter1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())



gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1} - {ex2}-Wind{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/Dif_Wind{lev}_{moving_day}dMean.png")
plt.close("all")

print("End Program")
