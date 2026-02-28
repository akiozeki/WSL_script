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

#変数選択-N or ushear or egr#
var="N"
pp=850
key=f"7d_mean_{var}{pp}"

sign_level=0.001
#上記のようにすると両側検定99%になる
ny=129
nx=129
n_member=10
 
case="200912low_ensemble"
wrf_dir="/DATA/USER/ozeki/MyWRF"
wrfout_dir=f"{wrf_dir}/output_data/{case}"
fig_dir=f"{wrf_dir}/fig/{case}"

start_date=datetime(2009,12,25,12)
end_date=datetime(2009,12,28,12)
time_step=timedelta(hours=6)
n_step=(end_date - start_date) // time_step
print(f"Set Time : {start_date}----{end_date},n_step={n_step+1}")
############################

##座標系情報を得るために任意のwrfoutファイルを開く
coord_ds=Dataset(f"{wrfout_dir}/ctl/n1/wrfout_d01_2009-12-27_00:00:00")
land=getvar(coord_ds,"LANDMASK")
cart_proj=get_cartopy(land)
print("projection:",cart_proj)
#lats,lons=latlon_coords(land)
#print(lats)
coord_ds.close()
#同じ実験設定であればファイルや変数は何でもよい(はず)


ctl_var_list=[]
me_var_list=[]
date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day
  h=date.hour
  time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}:00:00"
  print("time:",time_str)

  print("Open_Datset>")
  ctl_file=f"{wrfout_dir}/ctl/ensemble/CTL_{key}_{time_str}.nc"
  ctl_ds=xr.open_dataset(ctl_file)

  ctl_var=ctl_ds[f"{var}{pp}"]
  ctl_var=1/ctl_var
#この行はNの逆数を求めるために使用  
  ctl_var_list.append(ctl_var)
#  print(ctl_var)
  lats,lons=latlon_coords(ctl_var)
#  print(lats)

  me_file=f"{wrfout_dir}/me/ensemble/ME_{key}_{time_str}.nc"
  me_ds=xr.open_dataset(me_file)
  me_var=me_ds[f"{var}{pp}"]
  me_var=1/me_var
#ここではNの逆数を使うときのみ
  me_var_list.append(me_var)
  print(me_file)
#  print(me_var)

  ctl_ds.close()
  me_ds.close()

#  ctl_date_sum+=ctl_var
#  me_date_sum+=me_var

  date+=time_step

ctl_var_ds=xr.concat(ctl_var_list,dim="time")
me_var_ds=xr.concat(me_var_list,dim="time")
print(ctl_var_ds)


###平均計算
mean_type="Date-Mean"
#時間方向へ平均(member,ny,nx)
#ctl_mean1=ctl_var_ds.mean(dim="time",skipna=True)
#me_mean1=me_var_ds.mean(dim="time",skipna=True)
#print(ctl_mean1)
#ctl_date_mean=ctl_date_sum / n_step
#me_date_mean=me_date_sum / n_step
#この方法では欠損値nanを扱えない気がするがエラー等では出ていないので目をつぶる

##アンサブル平均(time,ny,nx)
ctl_mean1=ctl_var_ds.mean(dim="member",skipna=True)
me_mean1=me_var_ds.mean(dim="member",skipna=True)
print(ctl_mean1)
#ctl_date_mean=ctl_date_sum / n_step
#me_date_mean=me_date_sum / n_step
#この方法では欠損値nanを扱えない気がするがエラー等では出ていないので目をつぶる

#期間平均(ny,nx)
ctl_mean2=ctl_mean1.mean(dim="time",skipna=True)
me_mean2=me_mean1.mean(dim="time",skipna=True)
ano_mean2=ctl_mean2 - me_mean2
ratio_mean2=ctl_mean2 / me_mean2

print(ctl_mean2)

###ウェルチのt検定
#sign=np.zeros((ny,nx))
#for j in range(ny):
#  for i in range(nx):
#    sample1=ctl_mean1.values[:,j,i]
#    sample2=me_mean1.values[:,j,i]
##ens or dateで検定の取り方が変わる    
##       print(sample1)
##       print(sample2)
##       print("\n")
#    t_value,p_value=ttest_ind(sample1,sample2,equal_var=False)
#    sign_tf=(p_value < sign_level)
#    sign[j,i]=sign_tf.astype(int)
##変数sign_tfは有意ならTrue,有意でないならFalseを表す
##さらに.astype(int)で整数型への変換,True->1,False->0を行う
##  print(sign)
#
#print("全格子点数:", sign.size)
#print("有意(True)の数:", np.sum(sign))

#陸面マスク
ctl_mean2=np.ma.masked_where(land == 1,ctl_mean2)
me_mean2=np.ma.masked_where(land == 1,me_mean2)
ano_mean2=np.ma.masked_where(land == 1,ano_mean2)
ratio_mean2=np.ma.masked_where(land == 1,ratio_mean2)
#sign=np.ma.masked_where(land == 1,sign)

##Plot
##CTL
#fig=plt.figure()
#ax=plt.axes(projection=cart_proj)
#ax.set_extent([125,140,35,45])
#
#shade=ax.contourf(
#  lons,lats,ctl_mean2*86400,
##  levels=np.arange(1,2.4,0.2),
#  levels=np.arange(0,2.8,0.4),
#  cmap="Reds",
#  transform=ccrs.PlateCarree()
#  )
#
#cbar=plt.colorbar(
#  shade,orientation="horizontal",
#  shrink=0.6,
#  aspect=25
##  label="[ 10^-2 /s ]",
#  )
#
#cbar.ax.tick_params(labelsize=10)
#
#gl = ax.gridlines(draw_labels=True)
#gl.xformatter = LONGITUDE_FORMATTER
#gl.yformatter = LATITUDE_FORMATTER
#gl.top_labels = False
#gl.right_labels = False
#
#ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
#ax.set_title(f"CTL-{mean_type}")
#
#plt.savefig(f"{fig_dir}/ctl/ensemble/CTL_{mean_type}{var}{pp}_{start_date}_{end_date}.png")
#
#plt.close("all")
#
##ME
#fig=plt.figure()
#ax=plt.axes(projection=cart_proj)
#ax.set_extent([125,140,35,45])
#
#shade=ax.contourf(
#  lons,lats,me_mean2*86400,
##  levels=np.arange(1,2.4,0.2),
#  levels=np.arange(0,2.8,0.4),
#  cmap="Reds",
#  transform=ccrs.PlateCarree()
#  )
#
#cbar=plt.colorbar(
#  shade,orientation="horizontal",
#  shrink=0.6,
#  aspect=25
##  label="[ 10^-2 /s ]"
#  )
#cbar.ax.tick_params(labelsize=10)
#
#gl = ax.gridlines(draw_labels=True)
#gl.xformatter = LONGITUDE_FORMATTER
#gl.yformatter = LATITUDE_FORMATTER
#gl.top_labels = False
#gl.right_labels = False
#
#ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
#ax.set_title(f"ME-{mean_type}")
#
#plt.savefig(f"{fig_dir}/me/ensemble/ME_{mean_type}{var}{pp}_{start_date}_{end_date}.png")
#
#plt.close("all")
#
##Anomaly
#fig=plt.figure()
#ax=plt.axes(projection=cart_proj)
#ax.set_extent([125,140,35,45])
#
#shade=ax.contourf(
#  lons,lats,ano_mean2*86400,
##  levels=np.arange(-0.5,0.7,0.2),
#  levels=np.arange(-0.9,1.1,0.2),
#  cmap="bwr",
#  transform=ccrs.PlateCarree()
#  )
#
#cbar=plt.colorbar(
#  shade,orientation="horizontal",
#  shrink=0.6,
#  aspect=25
##  label="[ 10^-2 /s ]"
#  )
#cbar.set_ticks([-0.9,-0.5,0,0.5,0.9])  
#cbar.ax.tick_params(labelsize=10)
#ax.contourf(lons,lats,sign,levels=[0.5,1.5],colors="none",hatches=["///"],transform=ccrs.PlateCarree())
##有意な所にハッチ
#
#gl = ax.gridlines(draw_labels=True)
#gl.xformatter = LONGITUDE_FORMATTER
#gl.yformatter = LATITUDE_FORMATTER
#gl.top_labels = False
#gl.right_labels = False
#
#ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
#ax.set_title(f"Anomaly-{mean_type}")
#
#plt.savefig(f"{fig_dir}/ano/ensemble/Anomaly_{mean_type}{var}{pp}_{start_date}_{end_date}.png")
#
#plt.close("all")

#Ratio
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,45])

shade=ax.contourf(
  lons,lats,ratio_mean2,
  levels=np.arange(-0.4,2.6,0.4),
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25
#  label="[ 10^-2 /s ]"
  )
#cbar.set_ticks([-0.9,-0.5,0,0.5,0.9])  
#cbar.ax.tick_params(labelsize=10)
#ax.contourf(lons,lats,sign,levels=[0.5,1.5],colors="none",hatches=["///"],transform=ccrs.PlateCarree())
#有意な所にハッチ

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"Ratio-{mean_type}")

plt.savefig(f"{fig_dir}/ano/ensemble/Ratio_{mean_type}{var}{pp}_{start_date}_{end_date}.png")

plt.close("all")


print("End Program")
