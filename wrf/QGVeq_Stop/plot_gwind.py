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



dfile1=f"{input_dir}/{ex1}{lev}hpa_GWind_dxdy{dx}.nc"
dfile2=f"{input_dir}/{ex2}{lev}hpa_GWind_dxdy{dx}.nc"

ds1=xr.open_dataset(dfile1)
ds2=xr.open_dataset(dfile2)

print(ds1)
print(ds2)

u_g1=ds1["u_g"]
v_g1=ds1["v_g"]
theta_g1=ds1["theta_g"]

u_g2=ds2["u_g"]
v_g2=ds2["v_g"]
theta_g2=ds2["theta_g"]

lats,lons=latlon_coords(u_g1)

ds1.close()
ds2.close()


dif_u_g=u_g1 - u_g2
dif_v_g=v_g1 - v_g2
dif_theta_g=theta_g1 - theta_g2


##Plot
##EX1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

contour=ax.contour(
  lons,lats,theta_g1,
  colors="black",linewidth=2.0,
  transform=ccrs.PlateCarree()
  )
ax.clabel(contour)

step=1
qx,qy,qk=1.1,-0.1,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  u_g1.values[::step,::step],
  v_g1.values[::step,::step],
  scale=200,
  width=0.008,
  color="orangered",
  transform=ccrs.PlateCarree()
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")


#cbar.ax.tick_params(labelsize=10)

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines = False
gl.ylines = False


ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-GWind{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex1}/{ex1}_GWind{lev}_dxdy{dx}.png")

plt.close("all")

##Mean2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

contour=ax.contour(
  lons,lats,theta_g2,
  colors="black",linewidth=2.0,
  transform=ccrs.PlateCarree()
  )
ax.clabel(contour)

step=1
qx,qy,qk=1.1,-0.1,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  u_g2.values[::step,::step],
  v_g2.values[::step,::step],
  scale=200,
  width=0.008,
  color="orangered",
  transform=ccrs.PlateCarree()
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

#cbar.ax.tick_params(labelsize=10)

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines = False
gl.ylines = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-GWind{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex2}/{ex2}_GWind{lev}_dxdy{dx}.png")

plt.close("all")

##Differemce
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

contour=ax.contour(
  lons,lats,dif_theta_g,
  colors="black",linewidth=2.0,
  transform=ccrs.PlateCarree()
  )
ax.clabel(contour)

step=1
qx,qy,qk=1.1,-0.1,2
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  dif_u_g.values[::step,::step],
  dif_v_g.values[::step,::step],
  scale=50,
  width=0.008,
  color="orangered",
  transform=ccrs.PlateCarree()
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

#cbar.ax.tick_params(labelsize=10)


gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines = False
gl.ylines = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1} - {ex2}-GWind{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex2}/Dif_GWind{lev}_dxdy{dx}.png")

plt.close("all")

print("End Program")
