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

case="2025DJF"
ex1="CTL"
ex2="ME00"

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"
input_dir=f"/home/akioz/calculate/wrf/{case}"

 
#作図の描画設定
domain=[120,152,30,50]

#cmap="coolwarm"
slp_lev=np.arange(960,1040,4)
slp_lev_dif=np.arange(-4,4,0.5)

cmap="Purples"
cmap_dif="PRGn_r"
aslp_lev=np.arange(0,28,4)
#aslp_lev=np.arange(0,880,80)
aslp_lev_dif=np.arange(-1.7,1.9,0.2)
#aslp_lev_dif=np.arange(-75,85,10)
#カラーマップ


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
lats,lons=latlon_coords(land)
#print(lats)
coord_ds.close()
#同じ実験設定であればファイルや変数は何でもよい(はず)

dfile1=f"{input_dir}/{ex1}{case}_aslp_at.nc"
ds1=xr.open_dataset(dfile1)
slp1=ds1["slp"]
aslp1=ds1["aslp_at"]
print(slp1)
print(aslp1)
ds1.close()

dfile2=f"{input_dir}/{ex2}{case}_aslp_at.nc"
ds2=xr.open_dataset(dfile2)
slp2=ds2["slp"]
aslp2=ds2["aslp_at"]


ds2.close()

#aslp_atは負の値のみ取り出して絶対値(2乗)平均
##平均計算
#時間方向へ平均(member,ny,nx)
slp_mean1=slp1.mean(dim="time",skipna=True)
#aslp_mean1=(aslp1.where(aslp1 < 0)**2).mean(dim="time",skipna=True)
aslp_mean1=(abs(aslp1.where(aslp1 > 0))).mean(dim="time",skipna=True)


slp_mean2=slp2.mean(dim="time",skipna=True)
#aslp_mean2=(aslp1.where(aslp2 < 0)**2).mean(dim="time",skipna=True)
aslp_mean2=(abs(aslp2.where(aslp1 > 0))).mean(dim="time",skipna=True)


##陸面マスク
slp_mean1=np.ma.masked_where(land == 1,slp_mean1)
slp_mean2=np.ma.masked_where(land == 1,slp_mean2)
aslp_mean1=np.ma.masked_where(land == 1,aslp_mean1)
aslp_mean2=np.ma.masked_where(land == 1,aslp_mean2)

dif_slp=slp_mean1 - slp_mean2
dif_aslp=aslp_mean1 - aslp_mean2
if np.nanmean(dif_aslp) == 0:
 print("Missing!!")

##Plot
##Mean1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
#ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,aslp_mean1,
  levels=aslp_lev,
  cmap=cmap,
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  label="[ hPa / hour ]"
#  label="[ hPa^2 / hour^2 ]"
  )
cbar.ax.tick_params(labelsize=10)

#contour=ax.contour(lons,lats,slp_mean1,
#  levels=slp_lev,colors="black",linewidths=1.0,
#  transform=ccrs.PlateCarree()
#  )
#ax.clabel(contour)  

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines = False
gl.ylines = False


ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-{case}-aSLP/at")

plt.savefig(f"{fig_dir}/{ex1}/SLP/{ex1}_aSLP_at.png")

plt.close("all")

##Mean2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
#ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,aslp_mean2,
  levels=aslp_lev,
  cmap=cmap,
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  label="[ hPa / hour ]"
#  label="[ hPa^2 / hour^2 ]"
  )
cbar.ax.tick_params(labelsize=10)

#contour=ax.contour(lons,lats,slp_mean1,
#  levels=slp_lev,colors="black",linewidths=1.0,
#  transform=ccrs.PlateCarree()
#  )
#ax.clabel(contour)  

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines = False
gl.ylines = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-{case}-aSLP/at")

plt.savefig(f"{fig_dir}/{ex2}/SLP/{ex2}_aSLP_at.png")

plt.close("all")

##Difference
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
#ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,dif_aslp,
  levels=aslp_lev_dif,
  cmap=cmap_dif,
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  label="[ hPa / hour ]"
#  label="[ hPa^2 / hour^2 ]"
  )

cbar.ax.tick_params(labelsize=10)

#contour=ax.contour(lons,lats,dif_slp,
#  levels=slp_lev_dif,colors="black",linewidths=1.0,
#  transform=ccrs.PlateCarree()
#  )
#ax.clabel(contour)  


gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines = False
gl.ylines = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1} - {ex2}-{case}Mean-aSLP/at")

plt.savefig(f"{fig_dir}/{ex2}/SLP/Dif_aSLP_at.png")

plt.close("all")


print("End Program")
