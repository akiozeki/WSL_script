###SST-2m気温と風速を描く　おいおい顕熱フラックスも…
import math
import sys
from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import xarray as xr
from scipy.stats import ttest_ind
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

case="2025DJF"
ex1="CTL"
ex2="ME00"


wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"


start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
print(f"Set Time : {start_date}----{end_date}")

dT_list1=[]
dT_list2=[]
winds_list1=[]
winds_list2=[]

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

  if date == end_date:
    land=getvar(ds1,"LANDMASK") 
    cart_proj=get_cartopy(land)
    lats,lons=latlon_coords(land)
    ter1=getvar(ds1,"ter",units="m")
    ter1=np.ma.masked_where(land != 1,ter1)
    ter2=getvar(ds2,"ter",units="m")
    ter2=np.ma.masked_where(land != 1,ter2)

#変数を取り出す
  sst1=getvar(ds1,"SST")
#  print(sst1.values)
  sat1=getvar(ds1,"T2")
  dT1=sst1 - sat1
#  print("SST - 2m Temperature",dT1)
  dT_list1.append(dT1)

  u1,v1=getvar(ds1,"uvmet10",units="m/s")
#  print(u1)
#  print(v1)
  winds1=np.sqrt(u1**2 + v1**2)
#  print("Wind Speed",winds1)
  winds_list1.append(winds1)

  sst2=getvar(ds2,"SST")
#  print(sst1.values)
  sat2=getvar(ds2,"T2")
  dT2=sst2 - sat2
#  print("SST - 2m Temperature",dT2)
  dT_list2.append(dT2)

  u2,v2=getvar(ds2,"uvmet10",units="m/s")
#  print(u2)
#  print(v2)
  winds2=np.sqrt(u2**2 + v2**2)
#  print("Wind Speed",winds2)
  winds_list2.append(winds2)

  ds1.close()
  ds2.close()
#
  date+=timedelta(hours=dh)
#
dT_darray1=xr.concat(dT_list1,dim="time")
dT_darray2=xr.concat(dT_list2,dim="time")
winds_darray1=xr.concat(winds_list1,dim="time")
winds_darray2=xr.concat(winds_list2,dim="time")
#print(dT_darray1)
#print(winds_darray1)

#
###ココで母平均の差の検定
#ny=129
#nx=129
#sign_level=0.1
#
#sign=np.zeros((ny,nx))
#p_value=np.zeros((ny,nx))
#t_value=np.zeros((ny,nx))
#
#for j in range(ny):
#  for i in range(nx):
#    sample1=darray1.values[:,j,i]
#    sample2=darray2.values[:,j,i]
#    t_value[j,i],p_value[j,i]=ttest_ind(sample1,sample2,equal_var=False)
#    sign_tf=(p_value[j,i] < sign_level)
#    sign[j,i]=sign_tf.astype(int)
#
#print(p_value)
#print(f"{100-sign_level*100}%有意な格子点/全格子点数:{np.sum(sign)}/{sign.size}")


dT_mean1=dT_darray1.mean(dim="time",skipna=True)
dT_mean2=dT_darray2.mean(dim="time",skipna=True)
dT_mean1=np.ma.masked_where(land != 0,dT_mean1)
dT_mean2=np.ma.masked_where(land != 0,dT_mean2)

dT_dif=dT_mean1 - dT_mean2
dT_rate=dT_mean1/dT_mean2

winds_mean1=winds_darray1.mean(dim="time",skipna=True)
winds_mean2=winds_darray2.mean(dim="time",skipna=True)
winds_mean1=np.ma.masked_where(land == 1,winds_mean1)
winds_mean2=np.ma.masked_where(land == 1,winds_mean2)

winds_dif=winds_mean1 - winds_mean2
winds_rate=winds_mean1/winds_mean2

if np.nanmean(dT_dif) == 0:
  print("Missing Calculate SST - 2m Temperature ")
  sys.exit()

if np.nanmean(winds_dif) == 0:
  print("Missing Calculate Wind Speed")
  sys.exit()

print(dT_dif)
print(winds_dif)


##Plot
#ex1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,44])

shade=ax.contourf(
  lons,lats,dT_mean1,
  cmap="Reds",
  levels=np.arange(0,20,4),
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical"
  )

contour=ax.contour(
  lons,lats,winds_mean1,
  levels=np.arange(10,34,4),
  colors="black",linewidths=1.5,
  transform=ccrs.PlateCarree()
  )
ax.clabel(contour)

shade2=ax.contourf(lons,lats,ter1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-Sensible Heat Flux",fontsize=20)

plt.savefig(f"{fig_dir}/{ex1}/{ex1}_SHF.png")
plt.close("all")

#ex2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,44])

shade=ax.contourf(
  lons,lats,dT_mean2,
  cmap="Reds",
  levels=np.arange(0,20,4),
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical"
  )
contour=ax.contour(
  lons,lats,winds_mean2,
  levels=np.arange(10,34,4),
  colors="black",linewidths=1.5,
  transform=ccrs.PlateCarree()
  )
ax.clabel(contour)

shade2=ax.contourf(lons,lats,ter2,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-Sensible Heat Flux",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/{ex2}_SHF.png")
plt.close("all")

#Dif
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,44])

shade=ax.contourf(
  lons,lats,dT_dif,
  cmap="bwr",
  levels=np.arange(-4.5,5.5,1),
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical"
  )

contour=ax.contour(
  lons,lats,winds_dif,
  levels=np.arange(-2.5,3.5,1),
  colors="black",linewidths=1.5,
  transform=ccrs.PlateCarree()
  )
ax.clabel(contour)

shade2=ax.contourf(lons,lats,ter1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())
#ax.contourf(lons,lats,sign,levels=[0.5,1.5],colors="none",hatches=["///"],transform=ccrs.PlateCarree())

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1} - {ex2}-Sensible Heat Flux",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/Dif_SHF.png")
plt.close("all")


#Rate
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,44])

shade=ax.contourf(
  lons,lats,dT_rate,
  cmap="bwr",
  levels=np.arange(0.6,1.45,0.05),
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical"
  )

contour=ax.contour(
  lons,lats,winds_rate,
  levels=np.arange(0.4,1.8,0.1),
  colors="black",linewidths=1.5,
  transform=ccrs.PlateCarree()
  )
ax.clabel(contour)

shade2=ax.contourf(lons,lats,ter1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())
#ax.contourf(lons,lats,sign,levels=[0.5,1.5],colors="none",hatches=["///"],transform=ccrs.PlateCarree())

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1} / {ex2}-Sensible Heat Flux",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/Rate_SHF.png")
plt.close("all")


print("End Program")
