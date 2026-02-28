###別ファイルで作ったnetCDFファイルを使って指定した期間の平均を求める
from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel,ALL_TIMES
import metpy.calc as mpcalc
from metpy.units import units
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import xarray as xr
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from scipy.stats import ttest_ind
import sys


var="vT_prime"
#var="vv_prime"
varlabel="[ m/s * K ]"
#varlabel="[(m/s)^2]"
factor=1

p=850
high_day=2
low_day=7

high_key=f"{p}_{high_day}dMean"
low_key=f"{p}_{low_day}dMean"

case="2025DJF"
ex1="CTL"
ex2="ME00"

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"
input_dir=f"/home/akioz/calculate/wrf/{case}/MMean"

sign_level=0.001
#上記のようにすると両側検定99%になる
ny=129
nx=129
 
#作図の描画設定
domain=[120,150,30,50]



sdate=datetime(2024,12,1,0)
edate=datetime(2025,2,28,18)
time_step=timedelta(hours=6)
n_step=(edate - sdate) // time_step
print(f"Set Time : {sdate}----{edate},n_step={n_step+1}")
############################

##座標系情報を得るために任意のwrfoutファイルを開く
sy=sdate.year
sm=sdate.month
sd=sdate.day
sh=sdate.hour


coord_ds=Dataset(f"{wrfout_dir}/{ex1}/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")

land=getvar(coord_ds,"LANDMASK")
cart_proj=get_cartopy(land)
print("projection:",cart_proj)
#lats,lons=latlon_coords(land)
#print(lats)
coord_ds.close()
#同じ実験設定であればファイルや変数は何でもよい(はず)

high_vfile1=f"{input_dir}/{ex1}_va{high_key}.nc"
high_vds1=xr.open_dataset(high_vfile1)
high_vvar1=high_vds1["va_m"]

high_tfile1=f"{input_dir}/{ex1}_temp{high_key}.nc"
high_tds1=xr.open_dataset(high_tfile1)
high_tvar1=high_tds1["temp_m"]

lats,lons=latlon_coords(high_vvar1)

high_vds1.close()
high_tds1.close()

high_vfile2=f"{input_dir}/{ex2}_va{high_key}.nc"
high_vds2=xr.open_dataset(high_vfile2)
high_vvar2=high_vds2["va_m"]

high_tfile2=f"{input_dir}/{ex2}_temp{high_key}.nc"
high_tds2=xr.open_dataset(high_tfile2)
high_tvar2=high_tds2["temp_m"]

high_vds2.close()
high_tds2.close()

low_vfile1=f"{input_dir}/{ex1}_va{low_key}.nc"
low_vds1=xr.open_dataset(low_vfile1)
low_vvar1=low_vds1["va_m"]

low_tfile1=f"{input_dir}/{ex1}_temp{low_key}.nc"
low_tds1=xr.open_dataset(low_tfile1)
low_tvar1=low_tds1["temp_m"]

low_vds1.close()
low_tds1.close()

low_vfile2=f"{input_dir}/{ex2}_va{low_key}.nc"
low_vds2=xr.open_dataset(low_vfile2)
low_vvar2=low_vds2["va_m"]

low_tfile2=f"{input_dir}/{ex2}_temp{low_key}.nc"
low_tds2=xr.open_dataset(low_tfile2)
low_tvar2=low_tds2["temp_m"]

low_vds2.close()
low_tds2.close()

#ココでバンドパスフィルタ
vvar1=high_vvar1 - low_vvar1
vvar2=high_vvar2 - low_vvar2
tvar1=high_tvar1 - low_tvar1
tvar2=high_tvar2 - low_tvar2

if var == "vT_prime":
  var1=vvar1 * tvar1
  var2=vvar1 * tvar2
  cmaplev=np.arange(-13,15,2)
  cmaplev_dif=np.arange(-2,2.5,0.5)
  cmap="coolwarm"

if var == "vv_prime":
  var1=vvar1 * vvar1
  var2=vvar2 * vvar2
  cmaplev=np.arange(0,32,4)
  cmaplev_dif=np.arange(-16,18,2)
  cmap="Reds"

###平均計算
#時間方向へ平均(ny,nx)
mean1=var1.mean(dim="time",skipna=True)
mean2=var2.mean(dim="time",skipna=True)

if np.nanmean(mean1) == 0 or np.nanmean(mean2) == 0:
  print("Missing Calculate")
  sys.exit()


##陸面マスク
#mean1=np.ma.masked_where(land == 1,mean1)
#mean2=np.ma.masked_where(land == 1,mean2)
#sign=np.ma.masked_where(land == 1,sign)

#print(mean1)
#print(mean2)
dif=mean1 - mean2

##Plot
##Mean1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,mean1*factor,
  levels=cmaplev,
  cmap=cmap,
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  label=varlabel
  )

cbar.ax.tick_params(labelsize=10)

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-{case}-{var}{high_day}-{low_day}BandPass")

plt.savefig(f"{fig_dir}/{ex1}/zyouran/{ex1}_{var}_{high_day}-{low_day}bpass.png")

plt.close("all")

##Mean2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,mean2*factor,
  levels=cmaplev,
  cmap=cmap,
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  label=varlabel
  )

cbar.ax.tick_params(labelsize=10)

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-{case}-{var}{high_day}-{low_day}BandPass")

plt.savefig(f"{fig_dir}/{ex2}/zyouran/{ex2}_{var}_{high_day}-{low_day}bpass.png")

plt.close("all")

##Difference
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,dif*factor,
  levels=cmaplev_dif,
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical",
  shrink=0.9,
  aspect=25,
  )
cbar.ax.set_xlabel(varlabel,rotation=0,labelpad=20)
cbar.ax.tick_params(labelsize=10)

#ax.contourf(lons,lats,sign,levels=[0.5,1.5],colors="none",hatches=["///"],transform=ccrs.PlateCarree())
##有意な所にハッチ

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")

ax.set_title(f"{ex1} - {ex2}-{case}-{var}{high_day}-{low_day}BandPass")

plt.savefig(f"{fig_dir}/{ex2}/zyouran/Dif_{var}_{high_day}-{low_day}bpass.png")


plt.close("all")

print("End Program")
