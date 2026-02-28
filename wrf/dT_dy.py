#dT/dyの平均とdtの平均/dy
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

var="dT_dy"
#dTbar_dy or dT_dy
varlabel="K/10km"
factor=10000
p=850

dy=25000

ex1="CTL"
ex2="ME00"

case="2025DJF"
wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"


start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
print(f"Set Time : {start_date}----{end_date}")


T_list1=[]
T_list2=[]
dT_dy_list1=[]
dT_dy_list2=[]

date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day
  h=date.hour

  time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}"
  wrfout1=f"{wrfout_dir}/{ex1}/wrfout_d01_{time_str}:00:00"
  wrfout2=f"{wrfout_dir}/{ex2}/wrfout_d01_{time_str}:00:00"
  print("Read wrfout File",time_str)

##ファイルオープンとデータ取得
  ds1=Dataset(wrfout1)
  ds2=Dataset(wrfout2)

  p1=getvar(ds1,"p",units="hpa")
  tmp1=getvar(ds1,"tk")
  ptmp1=interplevel(tmp1,p1,p)
  land=getvar(ds1,"LANDMASK")

  p2=getvar(ds2,"p",units="hpa")
  tmp2=getvar(ds2,"tk")
  ptmp2=interplevel(tmp2,p2,p)

  cart_proj=get_cartopy(land)
  lats,lons=latlon_coords(land)

  ds1.close()
  ds2.close()

#ココで分岐
  if var == "dTbar_dy":
    T_list1.append(ptmp1)
    T_list2.append(ptmp2)


  elif var == "dT_dy":
##計算
#ここではm単位で指定  

    dT_dy1=-np.gradient(ptmp1,dy,axis=0)
    dT_dy2=-np.gradient(ptmp2,dy,axis=0)
#勾配は北-南で計算されるので北<南を正とするためにマイナスを付す    
#今回単位付与は行っていない(np.gradientで勾配計算をする際Quantifyは相性が悪い)
#計算をmpcalcで行えれば単位も扱えるかもしれない

    dT_dy_list1.append(dT_dy1)
    dT_dy_list2.append(dT_dy2)

  date+=timedelta(hours=6)


if var == "dTbar_dy":
  T_darray1=xr.concat(T_list1,dim="time")
  T_darray2=xr.concat(T_list2,dim="time")
  Tbar1=T_darray1.mean(dim="time",skipna=True)
  Tbar2=T_darray2.mean(dim="time",skipna=True)
  dTbar_dy1=-np.gradient(Tbar1,dy,axis=0)
  dTbar_dy2=-np.gradient(Tbar2,dy,axis=0)

  mean1=np.ma.masked_where(land == 1,dTbar_dy1)
  mean2=np.ma.masked_where(land == 1,dTbar_dy2)
  anomean= mean1 -mean2

elif var == "dT_dy":
  dT_dy_darray1=np.stack(dT_dy_list1,axis=0)
  dT_dy_darray2=np.stack(dT_dy_list2,axis=0)
  dT_dybar1=np.nanmean(dT_dy_darray1,axis=0)
  dT_dybar2=np.nanmean(dT_dy_darray2,axis=0)

  mean1=np.ma.masked_where(land == 1,dT_dybar1)
  mean2=np.ma.masked_where(land == 1,dT_dybar2)
  anomean= mean1 -mean2

##Plot
#ex1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([127,145,35,44])

shade=ax.contourf(
  lons,lats,mean1*factor,
  levels=np.arange(-0.25,0.27,0.02),
  cmap="viridis",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  label=f"{var}_[ {varlabel} ]"
  )

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-{var}{p}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex1}/{ex1}{var}{p}.png")
plt.close("all")

#ex2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([127,145,35,44])

shade=ax.contourf(
  lons,lats,mean2*factor,
  levels=np.arange(-0.25,0.27,0.02),
  cmap="viridis",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  label=f"{var}_[ {varlabel} ]"
  )

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-{var}{p}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/{ex2}{var}{p}.png")
plt.close("all")

#Anomaly
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([127,145,35,44])

shade=ax.contourf(
  lons,lats,anomean*factor,
  levels=np.arange(-0.25,0.27,0.02),
  cmap="seismic",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  label=f"{var}_[ {varlabel} ]"
  )

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"Anomaly-{var}{p}",fontsize=20)

plt.savefig(f"{fig_dir}/Ano/Ano{var}{p}.png")
plt.close("all")

print("End Program")
