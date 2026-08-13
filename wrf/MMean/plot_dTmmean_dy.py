#from __from__ import print_function
import os
from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel
import metpy.calc as mpcalc
from metpy.units import units
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import xarray as xr
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from scipy.stats import ttest_ind

var="temp_m"
#temp or temp_m(基本場) or temp_a(擾乱)
varlabel="K/100km"
factor=100000
lev=850

dy=25000
nx=129
ny=129
sign_level=0.05

ex1="CTL_lamb"
ex2="ME00_lamb"
n_member=1
moving_day=7

case="2025DJF"
wrfout_dir=f"/home/akioz/MyWRF/output/{case}"
input_dir=f"/home/akioz/calculate/wrf/{case}/MMean"
fig_dir=f"/home/akioz/fig/wrf/{case}"
os.makedirs(f"{fig_dir}/{ex1}/",exist_ok=True)
os.makedirs(f"{fig_dir}/{ex2}/",exist_ok=True)

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
ter=getvar(coord_ds,"ter",units="m")
ter=np.ma.masked_where(land != 1,ter)

if n_member == 1 :
  coord_ds2=Dataset(f"{wrfout_dir}/{ex2}/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")
else :
  coord_ds2=Dataset(f"{wrfout_dir}/{ex2}/n1/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")
land2=getvar(coord_ds2,"LANDMASK")
ter2=getvar(coord_ds2,"ter",units="m")
ter2=np.ma.masked_where(land2 != 1,ter2)



#print(lats)
coord_ds.close()

dfile1=f"{input_dir}/{ex1}_temp{lev}_{moving_day}dMean.nc"
dfile2=f"{input_dir}/{ex2}_temp{lev}_{moving_day}dMean.nc"

ds1=xr.open_dataset(dfile1)
ds2=xr.open_dataset(dfile2)

#print(ds1)
#print(ds2)

T1=ds1[var]
T2=ds2[var]
print(T1.values)

dT_dy1=-np.gradient(T1,dy,axis=1)
dT_dy2=-np.gradient(T2,dy,axis=1)
#*T(time,south_north,west_east)

#print(dT_dy1)
#print(dT_dy2)
##t検定
sign=np.zeros((ny,nx))
for j in range(ny):
  for i in range(nx):
    sample1=dT_dy1[:,j,i]
    sample2=dT_dy2[:,j,i]
#    print(sample1)
#    print(sample2)
#    print("\n")
    t_value,p_value=ttest_ind(sample1,sample2,equal_var=True)
#equal_varTrueにするとスチューデント,Falseでウェルチ
    sign_tf=(p_value < sign_level)
    sign[j,i]=sign_tf.astype(int)
#変数sign_tfは有意ならTrue,有意でないならFalseを表す
#さらに.astype(int)で整数型への変換,True->1,False->0を行う
print(sign)

print("全格子点数:", sign.size)
print("有意(True)の数:", np.sum(sign))


if n_member == 1:
  mean_T1=T1.mean(dim="time",skipna=True)
  mean_T2=T2.mean(dim="time",skipna=True)
  mean_dT_dy1=np.nanmean(dT_dy1,axis=0)
  mean_dT_dy2=np.nanmean(dT_dy2,axis=0)

#*dT_dy(time,south_north,west_east)

else:
  mean_T1=mean_T1.mean(dim="member",skipna=True)
  mean_T2=mean_T2.mean(dim="member",skipna=True)
  mean_dT_dy1=np.nanmean(mean_dT_dy1,axis=2)
  mean_dT_dy2=np.nanmean(mean_dT_dy2,axis=2)
#軸番号は要確認

print("T1",mean_T1)
print("T2",mean_T2)
print("dT_dy1",mean_dT_dy1)
print("dT_dy2",mean_dT_dy2)

ds1.close()
ds2.close()

#陸面マスク
mean_T1=np.ma.masked_where(land == 1,mean_T1)
mean_T2=np.ma.masked_where(land == 1,mean_T2)
mean_dT_dy1=np.ma.masked_where(land == 1,mean_dT_dy1)
mean_dT_dy2=np.ma.masked_where(land == 1,mean_dT_dy2)
#sign=np.ma.masked_where(land == 1,sign)

dif_T=mean_T1 - mean_T2
dif_dT_dy=mean_dT_dy1 - mean_dT_dy2

###Plot
##ex1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,44])

contour=ax.contour(
  lons,lats,mean_T1,
  levels=np.arange(256,270,2),
  colors="black",linewidths=1.0,
  transform=ccrs.PlateCarree()
  )
ax.clabel(contour)


shade=ax.contourf(
  lons,lats,mean_dT_dy1*factor,
  levels=np.arange(-0.4,2.2,0.2),
  cmap="Spectral_r",
  extend="both",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical",
  shrink=0.8,
  aspect=20
  )
cbar.ax.tick_params(labelsize=14)

#shade2=ax.contourf(lons,lats,ter,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

# グリッド線の設定
gl = ax.gridlines(draw_labels=True, 
                  linewidth=1, 
                  color='gray', 
                  alpha=0.5, 
                  linestyle='--')
# ラベルの表示位置を制御
gl.xlines = True         # 経度線を描く
gl.ylines = True         # 緯度線を描く
#gl.xformatter = LONGITUDE_FORMATTER
#gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlocator=FixedLocator([127,130,133,136,139])
#gl.ylocator=FixedLocator()
gl.x_inline = False      # ラベルを図の内側（インライン）に書かない設定
gl.y_inline = False      # 緯度も念のため設定
gl.ylabel_style = {'rotation': 0}
gl.xlabel_style = {'rotation': 0}
gl.xpadding = 10

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-dT/dy{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex1}/{ex1}dT_dy{lev}_{moving_day}dMean.png")
plt.close("all")

#ex2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,44])

contour=ax.contour(
  lons,lats,mean_T2,
  levels=np.arange(256,270,2),
  colors="black",linewidths=1.0,
  transform=ccrs.PlateCarree()
  )
ax.clabel(contour)


shade=ax.contourf(
  lons,lats,mean_dT_dy2*factor,
  levels=np.arange(-0.4,2.2,0.2),
  cmap="Spectral_r",
  extend="both",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical",
  shrink=0.8,
  aspect=20
  )
cbar.ax.tick_params(labelsize=14)

#shade2=ax.contourf(lons,lats,ter2,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

# グリッド線の設定
gl = ax.gridlines(draw_labels=True, 
                  linewidth=1, 
                  color='gray', 
                  alpha=0.5, 
                  linestyle='--')
# ラベルの表示位置を制御
gl.xlines = True         # 経度線を描く
gl.ylines = True         # 緯度線を描く
#gl.xformatter = LONGITUDE_FORMATTER
#gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlocator=FixedLocator([127,130,133,136,139])
#gl.ylocator=FixedLocator()
gl.x_inline = False      # ラベルを図の内側（インライン）に書かない設定
gl.y_inline = False      # 緯度も念のため設定
gl.ylabel_style = {'rotation': 0}
gl.xlabel_style = {'rotation': 0}
gl.xpadding = 10

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-dT/dy{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/{ex2}dT_dy{lev}_{moving_day}dMean.png")
plt.close("all")

#Difference
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,44])

contour=ax.contour(
  lons,lats,dif_T,
  levels=np.arange(-1.2,1.6,0.4),
  colors="black",linewidths=1.0,
  transform=ccrs.PlateCarree()
  )
ax.clabel(contour)
#clabel.tick_params(labelsize=12)

shade=ax.contourf(
  lons,lats,dif_dT_dy*factor,
  levels=np.arange(-0.85,0.95,0.1),
  cmap="bwr",
  extend="both",
  transform=ccrs.PlateCarree()
  )
cbar=plt.colorbar(
  shade,orientation="vertical",
  shrink=0.8,
  aspect=20
  )
cbar.ax.tick_params(labelsize=14)

#ax.contourf(lons,lats,sign,levels=[0.5,1.5],colors="none",hatches=["..."],transform=ccrs.PlateCarree())
lon_point=128
lat_point=42
#plt.scatter(lon_point,lat_point,marker="^",s=200,color="green",transform=ccrs.PlateCarree())

shade2=ax.contourf(lons,lats,ter,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

# グリッド線の設定
gl = ax.gridlines(draw_labels=True, 
                  linewidth=1, 
                  color='gray', 
                  alpha=0.5, 
                  linestyle='--')
# ラベルの表示位置を制御
gl.xlines = True         # 経度線を描く
gl.ylines = True         # 緯度線を描く
#gl.xformatter = LONGITUDE_FORMATTER
#gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlocator=FixedLocator([127,130,133,136,139])
#gl.ylocator=FixedLocator()
gl.x_inline = False      # ラベルを図の内側（インライン）に書かない設定
gl.y_inline = False      # 緯度も念のため設定
gl.ylabel_style = {'rotation': 0}
gl.xlabel_style = {'rotation': 0}
gl.xpadding = 10

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
#ax.set_title(f"{ex1} - {ex2}-dT/dy{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/DifdT_dy{lev}_{moving_day}dMean.png")
plt.close("all")

print("End Program")
