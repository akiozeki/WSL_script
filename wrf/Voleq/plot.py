###別ファイルで作ったnetCDFファイルを使って指定した期間の平均を求める
from datetime import datetime
from netCDF4 import Dataset
import xarray as xr
import numpy as np
from wrf import getvar,get_cartopy,latlon_coords
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

var="theta"
#var="dtheta_dt"
#var="Adv.theta_x"
#var="Adv.theta_y"
#var="Adv.theta_h"
#var="Adv.f"
#var="Stretching"
#var="res_Str"
#var="Sum"

case="2025DJF"
ex1="CTL_lamb"
ex2="ME00_lamb"

n_member=1
dx=25
lev=850
sigma=1

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"
input_dir=f"/home/akioz/calculate/wrf/{case}/Voleq"

cmaplev=np.arange(-4.5*10**-5, 5.5*10**-5, 1*10**-5)
#cmaplev=np.arange(-1.5*10**-9, 1.7*10**-9, 0.2*10**-9)
cmaplev_dif=np.arange(-4.5*10**-5, 5.5*10**-5, 1*10**-5)
#cmaplev_dif=np.arange(-1.5*10**-9, 1.7*10**-9, 0.2*10**-9)

sdate=datetime(2024,12,1,0)


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
lats,lons=latlon_coords(land)
#print(lats)
coord_ds.close()


dfile1=f"{input_dir}/{ex1}{lev}hpa_Voleq_dxdy{dx}_sigma{sigma}.nc"
dfile2=f"{input_dir}/{ex2}{lev}hpa_Voleq_dxdy{dx}_sigma{sigma}.nc"

ds1=xr.open_dataset(dfile1)
ds2=xr.open_dataset(dfile2)

#print(ds1)
#print(ds2)

if var == "Adv.theta_h" :
  var1=ds1["Adv.theta_x"].mean(dim="time",skipna=True) + ds1["Adv.theta_y"].mean(dim="time",skipna=True)
  var2=ds2["Adv.theta_x"].mean(dim="time",skipna=True) + ds2["Adv.theta_y"].mean(dim="time",skipna=True)

elif var == "res_Str" : 
  var1=0 - ds1["Adv.theta_x"].mean(dim="time",skipna=True) - ds1["Adv.theta_y"].mean(dim="time",skipna=True) - ds1["Adv.f"].mean(dim="time",skipna=True)
  var2=0 - ds2["Adv.theta_x"].mean(dim="time",skipna=True) - ds2["Adv.theta_y"].mean(dim="time",skipna=True) - ds2["Adv.f"].mean(dim="time",skipna=True)
  
elif var == "Sum" :
  var1=ds1["Adv.theta_x"].mean(dim="time",skipna=True) + ds1["Adv.theta_y"].mean(dim="time",skipna=True) + ds1["Adv.f"].mean(dim="time",skipna=True) + ds1["Stretching"].mean(dim="time",skipna=True)
  var2=ds2["Adv.theta_x"].mean(dim="time",skipna=True) + ds2["Adv.theta_y"].mean(dim="time",skipna=True) + ds2["Adv.f"].mean(dim="time",skipna=True) + ds2["Stretching"].mean(dim="time",skipna=True)

else:
  var1=ds1[var].mean(dim="time",skipna=True)
  var2=ds2[var].mean(dim="time",skipna=True)
 
print(var1)

ds1.close()
ds2.close()

dif=var1 - var2

##Plot
##EX1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

shade=ax.contourf(
  lons,lats,var1,
  levels=cmaplev,
  cmap="bwr",
  extend="both",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.8,
  aspect=25
  )

cbar.ax.xaxis.set_major_formatter(
    FormatStrFormatter('%.1e')
)

cbar.ax.tick_params(labelsize=10)

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
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-{var}{lev}-dx=dy={dx}")

#save_file_path=os.path.join(fig_dir,ex1,...,"name.png")
##永川

plt.savefig(f"{fig_dir}/{ex1}/Voleq/{ex1}{var}{lev}_dxdy{dx}_sigma{sigma}.png")

plt.close("all")

##Mean2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

shade=ax.contourf(
  lons,lats,var2,
  levels=cmaplev,
  cmap="bwr",
  extend="both",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.8,
  aspect=25
  )

cbar.ax.tick_params(labelsize=10)

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
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-{var}{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex2}/Voleq/{ex2}{var}{lev}_dxdy{dx}_sigma{sigma}.png")

plt.close("all")

##Differemce
fig=plt.figure()
ax=plt.axes(projection=cart_proj)

shade=ax.contourf(
  lons,lats,dif,
  levels=cmaplev_dif,
  cmap="bwr",
  extend="both",
  transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.8,
  aspect=25
  )

cbar.ax.tick_params(labelsize=10)


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
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"Diff-{var}{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex2}/Voleq/Dif{var}{lev}_dxdy{dx}_sigma{sigma}.png")

plt.close("all")

print("End Program")
