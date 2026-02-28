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

var="z_m"
#z or z_m(基本場) or z_a(擾乱)
varlabel="m"
factor=1
lev=925

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
#print(lats)
coord_ds.close()

dfile1=f"{input_dir}/{ex1}_z{lev}_{moving_day}dMean.nc"
dfile2=f"{input_dir}/{ex2}_z{lev}_{moving_day}dMean.nc"

ds1=xr.open_dataset(dfile1)
ds2=xr.open_dataset(dfile2)

print(ds1)
print(ds2)

z1=ds1[var]
z2=ds2[var]
print(z1)

#dz_dy1=-np.gradient(z1,dy,axis=1)
#dz_dy2=-np.gradient(z2,dy,axis=1)
#*z(time,south_north,west_east)

#print(dz_dy1)
#print(dz_dy2)

if n_member == 1:
  mean_z1=z1.mean(dim="time",skipna=True)
  mean_z2=z2.mean(dim="time",skipna=True)
#  mean_dz_dy1=np.nanmean(dz_dy1,axis=0)
#  mean_dz_dy2=np.nanmean(dz_dy2,axis=0)

#*dT_dy(time,south_north,west_east)

else:
  mean_z1=mean_z1.mean(dim="member",skipna=True)
  mean_z2=mean_z2.mean(dim="member",skipna=True)
#  mean_dz_dy1=np.nanmean(mean_dz_dy1,axis=2)
#  mean_dz_dy2=np.nanmean(mean_dz_dy2,axis=2)
#軸番号は要確認

print("z1",mean_z1)
print("z2",mean_z2)
#print("dz_dy1",mean_dz_dy1)
#print("dz_dy2",mean_dz_dy2)

ds1.close()
ds2.close()

#陸面マスク
#mean_z1=np.ma.masked_where(land == 1,mean_z1)
#mean_z2=np.ma.masked_where(land == 1,mean_z2)

dif_z=mean_z1 - mean_z2

###Plot
##ex1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
#ax.set_extent([127,145,35,44])

shade=ax.contourf(
  lons,lats,mean_z1*factor,
  levels=cmaplev,
  cmap="Spectral_r",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(shade,orientation="horizontal")

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-Z{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex1}/{ex1}_{var}{lev}_{moving_day}dMean.png")
plt.close("all")

#ex2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
#ax.set_extent([127,145,35,44])

shade=ax.contourf(
  lons,lats,mean_z2*factor,
  levels=cmaplev,
  cmap="Spectral_r",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(shade,orientation="horizontal")


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

plt.savefig(f"{fig_dir}/{ex2}/{ex2}_{var}{lev}_{moving_day}dMean.png")
plt.close("all")

#Difference
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
#ax.set_extent([127,145,35,44])


shade=ax.contourf(
  lons,lats,dif_z*factor,
  levels=cmaplev_d,
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical",
  shrink=0.9,
  aspect=20
  )

cbar.ax.tick_params(labelsize=14)

lon_point=128
lat_point=42
plt.scatter(lon_point,lat_point,marker="^",s=400,color="black",transform=ccrs.PlateCarree())

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1} - {ex2}-Z{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/Dif_{var}{lev}_{moving_day}dMean.png")
plt.close("all")

print("End Program")
