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
from scipy.stats import ttest_ind
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

var="z"
lev=800
var_unit="m"

var_label="Z800"
case="2025DJF"
ex1="CTL"
ex2="ME00"

cmaplev=np.arange(5120,5920,180)
#cmaplev=np.arange(7120,7920,80)
#cmaplev_dif=np.arange(-6,7.5,1.5)
cmaplev_dif=np.arange(-12,15,3)

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"


start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
print(f"Set Time : {start_date}----{end_date}")

var_list1=[]
var_list2=[]

date=start_date

while date <= end_date:
  y=date.year
  m=date.month
  d=date.day
  h=date.hour

  time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}"
  wrfout1=f"{wrfout_dir}/{ex1}/wrfout_d01_{time_str}:00:00"
  wrfout2=f"{wrfout_dir}/{ex2}/wrfout_d01_{time_str}:00:00"
  print(f"Read wrfout File {time_str}")

#ファイルオープンとデータ取得
  ds1=Dataset(wrfout1)
  ds2=Dataset(wrfout2)

#変数取り出す
  p1=getvar(ds1,"p",units="hpa")
  var1=getvar(ds1,var,units=var_unit)
  pvar1=interplevel(var1,p1,lev)
  var_list1.append(pvar1)

  p2=getvar(ds2,"p",units="hpa")
  var2=getvar(ds2,var,units=var_unit)
  pvar2=interplevel(var2,p2,lev)
  var_list2.append(pvar2)
 
  cart_proj=get_cartopy(var1)
  lats,lons=latlon_coords(var1)
  land=getvar(ds1,"LANDMASK")

  ds1.close()
  ds2.close()

  date+=timedelta(hours=dh)

darray1=xr.concat(var_list1,dim="time")
darray2=xr.concat(var_list2,dim="time")

##ココで母平均の差の検定
ny=129
nx=129
sign_level=0.1

sign=np.zeros((ny,nx))
p_value=np.zeros((ny,nx))
t_value=np.zeros((ny,nx))

for j in range(ny):
  for i in range(nx):
    sample1=darray1.values[:,j,i]
    sample2=darray2.values[:,j,i]
    t_value[j,i],p_value[j,i]=ttest_ind(sample1,sample2,equal_var=False)
    sign_tf=(p_value[j,i] < sign_level)
    sign[j,i]=sign_tf.astype(int)

print(p_value)
print(f"{100-sign_level*100}%有意な格子点/全格子点数:{np.sum(sign)}/{sign.size}")


mean1=darray1.mean(dim="time",skipna=True)
mean2=darray2.mean(dim="time",skipna=True)
dif=mean1 - mean2

#print(mean1)
#print(mean2)

##Plot
#ex1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

shade=ax.contourf(
  lons,lats,mean1,
  cmap="viridis",
#  levels=cmaplev,
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  label=f"{var_label}_[ {var_unit} ]"
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
ax.set_title(f"{ex1}-{var_label}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex1}/{ex1}{var_label}.png")
plt.close("all")

#ex2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

shade=ax.contourf(
  lons,lats,mean2,
  cmap="viridis",
#  levels=cmaplev,
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  label=f"{var_label}_[ {var_unit} ]"
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
ax.set_title(f"{ex2}-{var_label}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/{ex2}{var_label}.png")
plt.close("all")

#Dif
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

shade=ax.contourf(
  lons,lats,dif,
  cmap="bwr",
  levels=cmaplev_dif,
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  label=f"{var_label}_[ {var_unit} ]"
  )

ax.contourf(lons,lats,sign,levels=[0.5,1.5],colors="none",hatches=["///"],transform=ccrs.PlateCarree())

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1} - {ex2}-{var_label}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/Dif{var_label}.png")
plt.close("all")


#p値
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

shade=ax.contourf(
  lons,lats,p_value,
  cmap="Reds",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  label=f"{var_label}_[ {var_unit} ]"
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
ax.set_title(f"P-value{100-sign_level*100}%",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/P-value{100-sign_level*100}%{var_label}.png")
plt.close("all")



print("End Program")
