###別ファイルで作ったnetCDFファイルを使って指定した期間の平均を求める
import os
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


#var="vT_prime"
var="VV_prime"
#varlabel="[ m/s * K ]"
varlabel="[(m/s)^2]"
factor=1

p=850
mday=7
key=f"{p}_{mday}dMean"

case="2025DJF"
ex1="CTL_lamb"
ex2="ME00_lamb"

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"
input_dir=f"/home/akioz/calculate/wrf/{case}/MMean"

os.makedirs(f"{fig_dir}/{ex1}/zyouran",exist_ok=True)
os.makedirs(f"{fig_dir}/{ex2}/zyouran",exist_ok=True)

sign_level=0.001
#上記のようにすると両側検定99%になる
ny=129
nx=129
n_member=1
 
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
#同じ実験設定であればファイルや変数は何でもよい(はず)

ufile1=f"{input_dir}/{ex1}_ua{key}.nc"
uds1=xr.open_dataset(ufile1)
print(uds1)
uvar1=uds1["ua_a"]

vfile1=f"{input_dir}/{ex1}_va{key}.nc"
vds1=xr.open_dataset(vfile1)
vvar1=vds1["va_a"]

tfile1=f"{input_dir}/{ex1}_temp{key}.nc"
tds1=xr.open_dataset(tfile1)
tvar1=tds1["temp_a"]

lats,lons=latlon_coords(vvar1)

uds1.close()
vds1.close()
tds1.close()

ufile2=f"{input_dir}/{ex2}_ua{key}.nc"
uds2=xr.open_dataset(ufile2)
uvar2=uds2["ua_a"]

vfile2=f"{input_dir}/{ex2}_va{key}.nc"
vds2=xr.open_dataset(vfile2)
vvar2=vds2["va_a"]

tfile2=f"{input_dir}/{ex2}_temp{key}.nc"
tds2=xr.open_dataset(tfile2)
tvar2=tds2["temp_a"]

uds2.close()
vds2.close()
tds2.close()

if var == "vT_prime":
  var1=vvar1 * tvar1
  var2=vvar1 * tvar2
  cmaplev=np.arange(-22,26,4)
  cmaplev_dif=np.arange(-4.5,5.5,1)
  cmap="bwr"

if var == "VV_prime":
  var1=uvar1**2 + vvar1**2
  var2=uvar2**2 + vvar2**2
  cmaplev=np.arange(0,142,16)
  cmaplev_dif=np.arange(-27,33,6)
  cmap="Reds"

###平均計算
#時間方向へ平均(member,ny,nx)
mean1=var1.mean(dim="time",skipna=True)
mean2=var2.mean(dim="time",skipna=True)

##アンサブル平均(time,ny,nx)
#if n_member > 1 :
##ウェルチのt検定
#  sign=np.zeros((ny,nx))
#  for j in range(ny):
#    for i in range(nx):
#      sample1=ctl_mean1.values[:,j,i]
#      sample2=me_mean1.values[:,j,i]
#      print(sample1)
#      print(sample2)
#      print("\n")
#      t_value,p_value=ttest_ind(sample1,sample2,equal_var=False)
#      sign_tf=(p_value < sign_level)
#      sign[j,i]=sign_tf.astype(int)
##変数sign_tfは有意ならTrue,有意でないならFalseを表す
##さらに.astype(int)で整数型への変換,True->1,False->0を行う
#  print(sign)
#
#  print("全格子点数:", sign.size)
#  print("有意(True)の数:", np.sum(sign))

#mean1=mean1.mean(dim="member",skipna=True)
#mean2=mean2.mean(dim="member",skipna=True)


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
  extend="max",
  cmap=cmap,
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical",
  shrink=0.9,
  aspect=25
#  label=varlabel
  )

cbar.ax.tick_params(labelsize=12)

lon_point=128
lat_point=42
plt.scatter(lon_point,lat_point,marker="^",s=400,color="black",transform=ccrs.PlateCarree())

####緯度経度ラベルを表示する(ChatGPTが教えてくれた)
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
#gl.xlocator=FixedLocator([127,130,133,136,139])
#gl.ylocator=FixedLocator()
gl.x_inline = False      # ラベルを図の内側（インライン）に書かない設定
gl.y_inline = False      # 緯度も念のため設定
gl.ylabel_style = {'rotation': 0}
gl.xlabel_style = {'rotation': 0}
gl.xpadding = 10

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
#ax.set_title(f"{ex1}-{case}Mean-{var}{key}")

plt.savefig(f"{fig_dir}/{ex1}/zyouran/{ex1}Mean_{var}{key}.png")

plt.close("all")

##Mean2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,mean2*factor,
  levels=cmaplev,
  extend="max",
  cmap=cmap,
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical",
  shrink=0.9,
  aspect=25
#  label=varlabel
  )

cbar.ax.tick_params(labelsize=12)

####緯度経度ラベルを表示する(ChatGPTが教えてくれた)
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
#gl.xlocator=FixedLocator([127,130,133,136,139])
#gl.ylocator=FixedLocator()
gl.x_inline = False      # ラベルを図の内側（インライン）に書かない設定
gl.y_inline = False      # 緯度も念のため設定
gl.ylabel_style = {'rotation': 0}
gl.xlabel_style = {'rotation': 0}
gl.xpadding = 10

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
#ax.set_title(f"{ex2}-{case}Mean-{var}{key}")

plt.savefig(f"{fig_dir}/{ex2}/zyouran/{ex2}Mean_{var}{key}.png")

plt.close("all")

##Difference
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,dif*factor,
  levels=cmaplev_dif,
  extend="both",
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical",
  shrink=0.9,
  aspect=25,
  )
#cbar.ax.set_xlabel(varlabel,rotation=0,labelpad=20)
cbar.ax.tick_params(labelsize=14)

#白頭山にポイント
lon_point=128
lat_point=42
#plt.scatter(lon_point,lat_point,marker="^",s=400,color="black",transform=ccrs.PlateCarree())

#ax.contourf(lons,lats,sign,levels=[0.5,1.5],colors="none",hatches=["///"],transform=ccrs.PlateCarree())
##有意な所にハッチ

####緯度経度ラベルを表示する(ChatGPTが教えてくれた)
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
#gl.xlocator=FixedLocator([127,130,133,136,139])
#gl.ylocator=FixedLocator()
gl.x_inline = False      # ラベルを図の内側（インライン）に書かない設定
gl.y_inline = False      # 緯度も念のため設定
gl.ylabel_style = {'rotation': 0}
gl.xlabel_style = {'rotation': 0}
gl.xpadding = 10

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
#ax.set_title(f"{ex1} - {ex2}-{case}Mean-{var}{key}")

plt.savefig(f"{fig_dir}/{ex2}/zyouran/Dif_{var}{key}.png")

plt.close("all")

print("End Program")
