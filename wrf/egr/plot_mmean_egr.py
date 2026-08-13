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
from matplotlib.ticker import FixedLocator
from scipy.stats import ttest_ind


#各パラメータを設定
#変数EGR or revN or Ushear
var="EGR"
varlabel="[ /Day ]"
factor=86400
#単位変化のための係数

#var="N"
##描画はその逆数
#varlabel="[ 10^2 s ]"
#factor=0.01

#var="Ushear"
#varlabel="[ m/s /km ]"
#factor=1000

p=850
mday=7
key=f"{var}{p}_{mday}dMean"

case="2025DJF"
ex1="CTL_lamb"
ex2="ME00_lamb"

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"
input_dir=f"/home/akioz/calculate/wrf/{case}/EGR"

os.makedirs(f"{fig_dir}/{ex1}/egr",exist_ok=True)
os.makedirs(f"{fig_dir}/{ex2}/egr",exist_ok=True)

sign_level=0.005
#上記のようにすると両側検定95%になる
ny=129
nx=129
n_member=1

#作図の描画設定
domain=[125,140,35,44]
#カラーマップの配列　上からEGR,revN,Usheaer用
cmaplev=np.arange(0,2.8,0.4)
#cmaplev=np.arange(0.5,1.2,0.1)
#cmaplev=np.arange(0,14,2)

cmaplev_a=np.arange(-0.9,1.1,0.2)
#cmaplev_a=np.arange(-0.25,0.35,0.1)
#cmaplev_a=np.arange(-4.5,5.5,1)

cmaplev_r=np.arange(-0.4,2.8,0.4)


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
ter1=getvar(coord_ds,"ter",units="m")
ter1=np.ma.masked_where(land != 1,ter1)
#lats,lons=latlon_coords(land)
#print(lats)
coord_ds.close()
#同じ実験設定であればファイルや変数は何でもよい(はず)

if n_member > 1 :
 coord_ds2=Dataset(f"{wrfout_dir}/{ex2}/n1/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")
else :
 coord_ds2=Dataset(f"{wrfout_dir}/{ex2}/wrfout_d01_{sy}-{sm:02d}-{sd:02d}_{sh:02d}:00:00")

land2=getvar(coord_ds2,"LANDMASK")
ter2=getvar(coord_ds,"ter",units="m")
ter2=np.ma.masked_where(land2 != 1,ter2)


dfile1=f"{input_dir}/{ex1}_{key}.nc"
ds1=xr.open_dataset(dfile1)
var1=ds1[f"{var}"]

if var == "N":
 var1=1/var1

lats,lons=latlon_coords(var1)
ds1.close()

dfile2=f"{input_dir}/{ex2}_{key}.nc"
ds2=xr.open_dataset(dfile2)
var2=ds2[f"{var}"]
if var == "N":
 var2=1/var2
 var="revN"
#print(var2) 
ds2.close()

var1=var1.mean(dim="member",skipna=True)
var2=var2.mean(dim="member",skipna=True)

##t検定
sign=np.zeros((ny,nx))
for j in range(ny):
  for i in range(nx):
    sample1=var1.values[:,j,i]
    sample2=var2.values[:,j,i]
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


##平均計算
#時間方向へ平均(member,ny,nx)
mean1=var1.mean(dim="time",skipna=True)
mean2=var2.mean(dim="time",skipna=True)



##陸面マスク
mean1=np.ma.masked_where(land == 1,mean1)
mean2=np.ma.masked_where(land == 1,mean2)
sign=np.ma.masked_where(land == 1,sign)

#print(mean1)
#print(mean2)
dif=mean1 - mean2
log2dif=np.log2(mean1) - np.log2(mean2)
ratmean=mean1 / mean2

key=f"{var}{p}-{mday}dMean"
##Plot
##Mean1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,mean1*factor,
  levels=cmaplev,
  extend="both",
  cmap="Reds",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  label=varlabel
  )

cbar.ax.tick_params(labelsize=10)

shade2=ax.contourf(lons,lats,ter1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())




ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-{case}Mean-{key}")

plt.savefig(f"{fig_dir}/{ex1}/egr/{ex1}Mean_{key}.png")

plt.close("all")

##Mean2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,mean2*factor,
  levels=cmaplev,
  extend="both",
  cmap="Reds",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  label=varlabel
  )

cbar.ax.tick_params(labelsize=10)

shade2=ax.contourf(lons,lats,ter2,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

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
gl.xlocator=FixedLocator([127,130,133,136,139])
#gl.ylocator=FixedLocator()
gl.x_inline = False      # ラベルを図の内側（インライン）に書かない設定
gl.y_inline = False      # 緯度も念のため設定
gl.ylabel_style = {'rotation': 0}
gl.xlabel_style = {'rotation': 0}
gl.xpadding = 10

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-{case}Mean-{key}")

plt.savefig(f"{fig_dir}/{ex2}/egr/{ex2}Mean_{key}.png")

plt.close("all")

#Dif
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,dif*factor,
  levels=cmaplev_a,
  extend="both",
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="vertical",
  shrink=0.8,
  aspect=20
  )

cbar.ax.tick_params(labelsize=10)

#ax.contourf(lons,lats,sign,levels=[-0.5,0.5],colors="none",hatches=["/\/"],transform=ccrs.PlateCarree())
##有意な所にハッチ
shade2=ax.contourf(lons,lats,ter1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

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
gl.xlocator=FixedLocator([127,130,133,136,139])
#gl.ylocator=FixedLocator()
gl.x_inline = False      # ラベルを図の内側（インライン）に書かない設定
gl.y_inline = False      # 緯度も念のため設定
gl.ylabel_style = {'rotation': 0}
gl.xlabel_style = {'rotation': 0}
gl.xpadding = 10

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"Difference-{case}Mean-{key}")

plt.savefig(f"{fig_dir}/{ex2}/egr/Dif_Mean_{key}.png")

plt.close("all")

#log2Dif
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

shade=ax.contourf(
  lons,lats,log2dif,
  levels=np.arange(-1.4,1.8,0.4),
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.8,
  aspect=25
  )

cbar.ax.tick_params(labelsize=10)

#plt.scatter(lon_point,lat_point,marker="^",s=500,color="green",transform=ccrs.PlateCarree())
#ax.contourf(lons,lats,sign,levels=[0.5,1.5],colors="none",hatches=["..."],transform=ccrs.PlateCarree())
##有意な所にハッチ
shade2=ax.contourf(lons,lats,ter1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

ax.plot([122,137],[40.5,40.5],color="blue",linewidth=3.0,transform=ccrs.PlateCarree())
#plt.scatter(lon_point,lat_point,marker="^",s=500,color="green",transform=ccrs.PlateCarree())

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
gl.xlocator=FixedLocator([127,130,133,136,139])
#gl.ylocator=FixedLocator()
gl.x_inline = False      # ラベルを図の内側（インライン）に書かない設定
gl.y_inline = False      # 緯度も念のため設定
gl.ylabel_style = {'rotation': 0}
gl.xlabel_style = {'rotation': 0}
gl.xpadding = 10
ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"log2Difference-{case}Mean-{key}")

plt.savefig(f"{fig_dir}/{ex2}/egr/log2Dif_Mean_{key}.png")

plt.close("all")


#Rate
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)


shade=ax.contourf(
  lons,lats,ratmean,
  levels=cmaplev_r,
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.8,
  aspect=25
  )

cbar.ax.tick_params(labelsize=10)

#plt.scatter(lon_point,lat_point,marker="^",s=500,color="green",transform=ccrs.PlateCarree())

shade2=ax.contourf(lons,lats,ter1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

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
gl.xlocator=FixedLocator([127,130,133,136,139])
#gl.ylocator=FixedLocator()
gl.x_inline = False      # ラベルを図の内側（インライン）に書かない設定
gl.y_inline = False      # 緯度も念のため設定
gl.ylabel_style = {'rotation': 0}
gl.xlabel_style = {'rotation': 0}
gl.xpadding = 10

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"Rate-{case}Mean-{key}")

plt.savefig(f"{fig_dir}/{ex2}/egr/RatMean_{key}.png")

plt.close("all")



print("End Program")
