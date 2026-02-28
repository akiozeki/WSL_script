###別ファイルで作ったnetCDFファイルを使って検定と作図を行う
from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel,ALL_TIMES
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import xarray as xr
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from scipy.stats import ttest_ind

#変数選択#
var="divergence"
var_label="10^-5 m/s^2"
lev=900
key=f"7d_mean_{var}{lev}"

sign_level=0.005
ny=129
nx=129
#上記のようにすると両側検定95%になる
 
case="200912low_ensemble"
wrf_dir="/DATA/USER/ozeki/MyWRF"
wrfout_dir=f"{wrf_dir}/output_data/{case}"
fig_dir=f"{wrf_dir}/fig/{case}"

start_date=datetime(2009,12,25,12)
end_date=datetime(2009,12,28,12)
print(f"Set Time : {start_date}----{end_date}")
############################

##座標系情報を得るために適当なwrfoutファイルを開く
coord_ds=Dataset(f"{wrfout_dir}/ctl/n1/wrfout_d01_2009-12-25_12:00:00")
land=getvar(coord_ds,"LANDMASK")
cart_proj=get_cartopy(land)
print("projection:",cart_proj)
lats,lons=latlon_coords(land)
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
  print("\ntime:",time_str)

  print("Open Data File>")
  ctl_file=f"{wrfout_dir}/ctl/ensemble/CTL_{key}_{time_str}.nc"
  ctl_ds=xr.open_dataset(ctl_file)
  print(ctl_file)
  ctl_var=ctl_ds[f"{var}{lev}"]
  ctl_var_list.append(ctl_var)
#  print(ctl_var)
#  lats,lons=latlon_coords(ctl_var)
#  print(lats)

  me_file=f"{wrfout_dir}/me/ensemble/ME_{key}_{time_str}.nc"
  me_ds=xr.open_dataset(me_file)
  me_var=me_ds[f"{var}{lev}"]
  me_var_list.append(me_var)
  print(me_file)
#  print(me_var)

  ctl_ds.close()
  me_ds.close()

##アンサンブル平均
  print(f"Calculate Ensemble Mean({time_str})")
  ctl_ensemble_mean=ctl_var.mean(dim="member",skipna=True)
  me_ensemble_mean=me_var.mean(dim="member",skipna=True)
  ano_ensemble_mean=ctl_ensemble_mean - me_ensemble_mean
  print("(CTL, ME, Anomaly) on center point:")
  print(f"({ctl_ensemble_mean.values[64,64]},{me_ensemble_mean.values[64,64]},{ano_ensemble_mean.values[64,64]})")

##ウェルチのt検定
  print(f"Start Welch T-test(95%)({time_str})")
  sign=np.zeros((ny,nx))
  for j in range(ny):
    for i in range(nx):
      sample1=ctl_var.values[:,j,i]
      sample2=me_var.values[:,j,i]
#       print(sample1)
#       print(sample2)
#       print("\n")
      t_value,p_value=ttest_ind(sample1,sample2,equal_var=False)
      sign_tf=p_value < sign_level
      sign[j,i]=sign_tf.astype(int)
#変数sign_tfは有意ならTrue,有意でないならFalseを表す
#さらに.astype(int)で整数型への変換,True->1,False->0を行う
#  print(sign)
  print(f"有意(True)の数:{np.sum(sign)}/{sign.size}")

##マスク
#陸面マスク
  ctl_ensemble_mean=np.ma.masked_where(land == 1,ctl_ensemble_mean)
  me_ensemble_mean=np.ma.masked_where(land == 1,me_ensemble_mean)
  ano_ensemble_mean=np.ma.masked_where(land == 1,ano_ensemble_mean)
#有意でないところをマスク
  ano_ensemble_maen=np.ma.masked_where(sign == 0,ano_ensemble_mean)


#Plot 各時刻のアンサンブル平均 
  print("Start Plot")
#CTL
  fig=plt.figure()
  ax=plt.axes(projection=cart_proj)
  ax.set_extent([125,140,35,45])

  shade=ax.contourf(
    lons,lats,ctl_ensemble_mean*100000,
    levels=np.arange(-4.5,5.5,1.0),
    cmap="bwr",
    transform=ccrs.PlateCarree()
    )
  
  cbar=plt.colorbar(
    shade,orientation="horizontal",
    shrink=0.6,
    aspect=25,
    label=f"{var_label}"
    )

  gl = ax.gridlines(draw_labels=True)
  gl.xformatter = LONGITUDE_FORMATTER
  gl.yformatter = LATITUDE_FORMATTER
  gl.top_labels = False
  gl.right_labels = False

  ax.coastlines()
  ax.add_feature(cfeature.LAND,color="gray")
  ax.set_title(f"ctl-{time_str}UTC",fontsize=20)
  
  plt.savefig(f"{fig_dir}/ctl/ensemble/{var}{lev}_{time_str}.png")
  plt.close("all")

#ME
  fig=plt.figure()
  ax=plt.axes(projection=cart_proj)
  ax.set_extent([125,140,35,45])

  shade=ax.contourf(
    lons,lats,me_ensemble_mean*100000,
    levels=np.arange(-4.5,5.5,1.0),
    cmap="bwr",
    transform=ccrs.PlateCarree()
    )
  
  cbar=plt.colorbar(
    shade,orientation="horizontal",
    shrink=0.6,
    aspect=25,
    label=f"{var_label}"
    )

  gl = ax.gridlines(draw_labels=True)
  gl.xformatter = LONGITUDE_FORMATTER
  gl.yformatter = LATITUDE_FORMATTER
  gl.top_labels = False
  gl.right_labels = False

  ax.coastlines()
  ax.add_feature(cfeature.LAND,color="gray")
  ax.set_title(f"me-{time_str}UTC",fontsize=20)
  
  plt.savefig(f"{fig_dir}/me/ensemble/{var}{lev}_{time_str}.png")
  plt.close("all")

#Anomaly
  fig=plt.figure()
  ax=plt.axes(projection=cart_proj)
  ax.set_extent([125,140,35,45])

  shade=ax.contourf(
    lons,lats,ano_ensemble_mean*100000,
    levels=np.arange(-4.5,5.5,1.0),
    cmap="bwr",
    transform=ccrs.PlateCarree()
    )
  
  cbar=plt.colorbar(
    shade,orientation="horizontal",
    shrink=0.6,
    aspect=25,
    label=f"{var_label}"
    )


  gl = ax.gridlines(draw_labels=True)
  gl.xformatter = LONGITUDE_FORMATTER
  gl.yformatter = LATITUDE_FORMATTER
  gl.top_labels = False
  gl.right_labels = False

  ax.coastlines()
  ax.add_feature(cfeature.LAND,color="gray")
  ax.set_title(f"anomaly-{time_str}UTC",fontsize=20)
  
  plt.savefig(f"{fig_dir}/ano/ensemble/{var}{lev}_{time_str}.png")
  plt.close("all")
 
  date+=timedelta(hours=6)


##アンサンブル期間平均
print("\n")
print("Calculate Ensemble Date Mean")
ctl_var_list=xr.concat(ctl_var_list,dim="time")
me_var_list=xr.concat(me_var_list,dim="time")

ctl_dmean=ctl_var_list.mean(dim="time",skipna=True)
me_dmean=me_var_list.mean(dim="time",skipna=True)
#この状態ではまだアンサンブル方向に軸が残っている

ctl_edmean=ctl_dmean.mean(dim="member",skipna=True)
me_edmean=me_dmean.mean(dim="member",skipna=True)
ano_edmean=ctl_edmean - me_edmean

##ウェルチのt検定
print("Start Welch T-test(95%)")
sign=np.zeros((ny,nx))
for j in range(ny):
  for i in range(nx):
    sample1=ctl_dmean.values[:,j,i]
    sample2=me_dmean.values[:,j,i]
#       print(sample1)
#       print(sample2)
#       print("\n")
    t_value,p_value=ttest_ind(sample1,sample2,equal_var=False)
    sign_tf=(p_value < sign_level)
    sign[j,i]=sign_tf.astype(int)
#変数sign_tfは有意ならTrue,有意でないならFalseを表す
#さらに.astype(int)で整数型への変換,True->1,False->0を行う
#  print(sign)

print(f"有意(True)の数:{np.sum(sign)}/{sign.size}")

##マスク
#陸面マスク
ctl_edmean=np.ma.masked_where(land == 1,ctl_edmean)
me_edmean=np.ma.masked_where(land == 1,me_edmean)
ano_edmean=np.ma.masked_where(land == 1,ano_edmean)
#有意でないところをマスク
ano_edmean=np.ma.masked_where(sign == 0,ano_edmean)


##Plot アンサンブル期間平均 
print("Start Plot")
#CTL
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,45])

shade=ax.contourf(
  lons,lats,ctl_edmean*100000,
  levels=np.arange(-4.5,5.5,1.0),
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  label=f"{var_label}"
  )

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"CTL-Date-Mean",fontsize=20)

plt.savefig(f"{fig_dir}/ctl/ensemble/CTL_{var}{lev}_ens_date_7dmean.png")
plt.close("all")

#ME
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,45])

shade=ax.contourf(
  lons,lats,me_edmean*100000,
  levels=np.arange(-4.5,5.5,1.0),
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  label=f"{var_label}"
  )

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"ME-Date-Mean",fontsize=20)

plt.savefig(f"{fig_dir}/me/ensemble/ME_{var}{lev}_ens_date_7dmean.png")
plt.close("all")

#Anomaly
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,45])

shade=ax.contourf(
  lons,lats,ano_edmean*100000,
  levels=np.arange(-4.5,5.5,1.0),
  cmap="bwr",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  label=f"{var_label}"
  )

#ax.contourf(lons,lats,sign,levels=[0.5,1.5],colors="none",hatches=["///"],transform=ccrs.PlateCarree())

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"Anomaly-Date-Mean",fontsize=20)

plt.savefig(f"{fig_dir}/ano/ensemble/Anomaly_{var}{lev}_ens_date_7dmean.png")
plt.close("all")


print("End Program")  

