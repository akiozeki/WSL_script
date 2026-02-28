###別ファイルで作ったnetCDFファイルを使って指定した期間の平均を求める
from datetime import datetime
from netCDF4 import Dataset
import xarray as xr
import numpy as np
from wrf import getvar,get_cartopy,latlon_coords
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

#key="zyouran"
#kihon:基本場,zyouran:擾乱場

#var="Adv.theta_g"
var="Adv.f"
#var="Stretching"
#var="Sum"
#Adv.theta_g or Adv.f or Stretching

case="2025DJF"
ex1="CTL"
ex2="ME00"

n_member=1
dx=200
lev=800

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"
input_dir=f"/home/akioz/calculate/wrf/{case}/QGVeq"

#cmaplev=np.arange(-7.5*10**-9, 8.5*10**-9, 1*10**-9)
cmaplev=np.arange(-7.5*10**-10, 8.5*10**-10,1*10**-10)
#cmaplev_dif=np.arange(-7.5*10**-9, 8.5*10**-9, 1*10**-9)
#cmaplev_dif=np.arange(-7.5*10**-10, 8.5*10**-10, 1*10**-10)
cmaplev_dif=np.arange(-7.5*10**-11, 8.5*10**-11, 1*10**-11)

sdate=datetime(2024,12,1,0)


##座標系情報を得るために任意のwrfoutファイルを開く
sy=sdate.year
sm=sdate.month
sd=sdate.day
sh=sdate.hour


if n_member > 1 :
 coord_ds=Dataset(f"{wrfout_dir}/{ex1}/n1/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")
else :
 coord_ds=Dataset(f"{wrfout_dir}/{ex1}/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")

land=getvar(coord_ds,"LANDMASK")
cart_proj=get_cartopy(land)
print("projection:",cart_proj)
#lats,lons=latlon_coords(land)
#print(lats)
coord_ds.close()



dfile1=f"{input_dir}/{ex1}{lev}hpa_QPVeq_LightHand_dxdy{dx}.nc"
dfile2=f"{input_dir}/{ex2}{lev}hpa_QPVeq_LightHand_dxdy{dx}.nc"

ds1=xr.open_dataset(dfile1)
ds2=xr.open_dataset(dfile2)

print(ds1)
print(ds2)

if var == "Sum" :
  var1=ds1["Adv.theta_g"] + ds1["Adv.f"] + ds1["Stretching"]
  var2=ds2["Adv.theta_g"] + ds2["Adv.f"] + ds2["Stretching"]

else:
  var1=ds1[var]
  var2=ds2[var]

lats,lons=latlon_coords(var1)

ds1.close()
ds2.close()

dif=var1 - var2

##Plot
##EX1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

shade=ax.contourf(
  lons,lats,var1,
  levels=cmaplev,
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25
  )

cbar.ax.tick_params(labelsize=10)

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines = False
gl.ylines = False


ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-{var}{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex1}/QGVeq/{ex1}{var}{lev}_dxdy{dx}.png")

plt.close("all")

##Mean2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

shade=ax.contourf(
  lons,lats,var2,
  levels=cmaplev,
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25
  )

cbar.ax.tick_params(labelsize=10)

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines = False
gl.ylines = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-{var}{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex2}/QGVeq/{ex2}{var}{lev}_dxdy{dx}.png")

plt.close("all")

##Differemce
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

shade=ax.contourf(
  lons,lats,dif,
  levels=cmaplev_dif,
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25
  )

cbar.ax.tick_params(labelsize=10)


gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines = False
gl.ylines = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"Diff-{var}{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex2}/QGVeq/{var}{lev}_dxdy{dx}.png")

plt.close("all")

print("End Program")
