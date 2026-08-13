###別ファイルで作ったnetCDFファイルを使って指定した期間の平均を求める
from datetime import datetime
from netCDF4 import Dataset
import xarray as xr
import numpy as np
from wrf import getvar,get_cartopy,latlon_coords
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


##変数指定
#shading
svar="thg"
#svar="dthg_dt"
#svar="Adv.thgx"
#svar="Adv.thgy"
# svar="Adv.thgh"
# svar="Adv.f"
# svar="Stretching"
# svar="Str_res"
#svar="Sum"
#svar=0

#contour
#cvar="Z"
#cvar="thg"
#cvar="dthg_dt"
cvar="Adv.thgx"
cvar="Adv.thgy"
#cvar="Adv.thgh"
#cvar="Adv.f"
cvar="Stretching"
#cvar="Str_res"
#cvar="Sum"
cvar=0

#vector
#uvar="Ug"
#vvar="Vg"
#uvar="Ua"
#vvar="Va"
uvar=0
vvar=0
#0だとベクトル地衡風の描画なし

##実験，計算設定
case="2025DJF"
ex1="CTL_lamb"
ex2="ME00_lamb"

n_member=1
dx=25
lev=800
sigma=5

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"
input_dir=f"/home/akioz/calculate/wrf/{case}/QGVeq"

domain=[120,140,32,50]
#図の描画範囲
levs=np.arange(-7.5*10**-5, 8.5*10**-5, 1*10**-5)
#levs=np.arange(-7.5*10**-9, 8.5*10**-9, 1*10**-9)
#levs=np.arange(-7.5*10**-10, 8.5*10**-10,1*10**-10)
levs_dif=np.arange(-3.5*10**-5, 4.5*10**-5, 1*10**-5)
#levs_dif=np.arange(-7.5*10**-9, 8.5*10**-9, 1*10**-9)
#levs_dif=np.arange(-7.5*10**-10, 8.5*10**-10, 1*10**-10)

#levc=np.arange(-7.5*10**-5, 8.5*10**-5, 1*10**-5)
#levc_dif=np.arange(-2.5*10**-5, 3*10**-5, 0.5*10**-5)
levc=np.arange(-7.5*10**-9, 8.5*10**-9, 1*10**-9)
#levc_dif=np.arange(-7.5*10**-9, 8.5*10**-9, 1*10**-9)
#levc_dif=np.arange(-9*10**-9, 11*10**-9, 2*10**-9)
levc_plus=np.arange(0.5,8.5,1)
levc_minus=np.arange(-7.5,0.5,1)

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
ter=getvar(coord_ds,"ter")
print("projection:",cart_proj)
lats,lons=latlon_coords(land)
#print(lats)
coord_ds.close()


dfile1=f"{input_dir}/{ex1}{lev}hpa_QGVeq_dxdy{dx}_sigma{sigma}.nc"
dfile2=f"{input_dir}/{ex2}{lev}hpa_QGVeq_dxdy{dx}_sigma{sigma}.nc"

ds1=xr.open_dataset(dfile1)
ds2=xr.open_dataset(dfile2)

print(ds1)
print(ds2)
if svar == 0 :
  svar1=svar2=0
  print("No Shading Var")

elif svar == "Adv.thgh" :
  svar1=ds1["Adv.thgx"].mean(dim="time",skipna=True) + ds1["Adv.thgy"].mean(dim="time",skipna=True)
  svar2=ds2["Adv.thgx"].mean(dim="time",skipna=True) + ds2["Adv.thgy"].mean(dim="time",skipna=True)


elif svar == "Sum" :
  svar1=ds1["Adv.thgx"].mean(dim="time",skipna=True) + ds1["Adv.thgy"].mean(dim="time",skipna=True) + ds1["Adv.f"].mean(dim="time",skipna=True) + ds1["Stretching"].mean(dim="time",skipna=True)
  svar2=ds2["Adv.thgx"].mean(dim="time",skipna=True) + ds2["Adv.thgy"].mean(dim="time",skipna=True) + ds2["Adv.f"].mean(dim="time",skipna=True) + ds2["Stretching"].mean(dim="time",skipna=True)

elif svar == "Str_res" :
  svar1=0 - ds1["Adv.thgx"].mean(dim="time",skipna=True) - ds1["Adv.thgy"].mean(dim="time",skipna=True) - ds1["Adv.f"].mean(dim="time",skipna=True)
  svar2=0 - ds2["Adv.thgx"].mean(dim="time",skipna=True) - ds2["Adv.thgy"].mean(dim="time",skipna=True) - ds2["Adv.f"].mean(dim="time",skipna=True)

else:
  svar1=ds1[svar].mean(dim="time",skipna=True)
  svar2=ds2[svar].mean(dim="time",skipna=True)

sdif=svar1 - svar2

if cvar == 0 :
  print("No Contour Var")

elif cvar == "Adv.thgh" :
  cvar1=ds1["Adv.thgx"].mean(dim="time",skipna=True) + ds1["Adv.thgy"].mean(dim="time",skipna=True)
  cvar2=ds2["Adv.thgx"].mean(dim="time",skipna=True) + ds2["Adv.thgy"].mean(dim="time",skipna=True)
  cdif=cvar1 - cvar2

elif cvar == "Str_res" :
  cvar1=0 - ds1["Adv.thgx"].mean(dim="time",skipna=True) - ds1["Adv.thgy"].mean(dim="time",skipna=True) - ds1["Adv.f"].mean(dim="time",skipna=True)
  cvar2=0 - ds2["Adv.thgx"].mean(dim="time",skipna=True) - ds2["Adv.thgy"].mean(dim="time",skipna=True) - ds2["Adv.f"].mean(dim="time",skipna=True)
  cdif=cvar1 - cvar2

else :
   cvar1=ds1[cvar].mean(dim="time",skipna=True)
   cvar2=ds2[cvar].mean(dim="time",skipna=True)
   cdif=cvar1 - cvar2
    
if vvar == 0 :
  print("No Vector Var")

else :
  u1=ds1[uvar].mean(dim="time",skipna=True)
  v1=ds1[vvar].mean(dim="time",skipna=True)
  u2=ds2[uvar].mean(dim="time",skipna=True)
  v2=ds2[vvar].mean(dim="time",skipna=True)
  udif=u1 -u2
  vdif=v1 -v2

ds1.close()
ds2.close()

##Plot 
##EX1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

if svar != 0 :
  shade=ax.contourf(
    lons,lats,svar1,
    levels=levs,
    cmap="bwr",
    extend="both",
    transform=ccrs.PlateCarree()
    )

  cbar=plt.colorbar(
    shade,orientation="horizontal",
    shrink=0.6,
    aspect=25
    )
  cbar.ax.tick_params(labelsize=10)

if cvar != 0:
  contour=ax.contour(
  lons,lats,cvar1,
  levels=levc,
  colors="black",linewidths=1.0,
  transform=ccrs.PlateCarree()
    )
  ax.clabel(contour)

if uvar == "Ug" or uvar == "Ua" :
  step=12
  qx,qy,qk=1.1,-0.1,20
  vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  u1.values[::step,::step],
  v1.values[::step,::step],
  scale=400,
  width=0.005,
  color="black",
  transform=ccrs.PlateCarree()
    )

  ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

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
ax.set_title(f"{ex1}-{svar}-{cvar}-{vvar}{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex1}/QGVeq/{ex1}{svar}_{cvar}_{uvar}{vvar}_{lev}hpa_dxdy{dx}_sigma{sigma}.png")

plt.close("all")

##EX2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)

if svar != 0 :
  shade=ax.contourf(
    lons,lats,svar2,
    levels=levs,
    cmap="bwr",
    extend="both",
    transform=ccrs.PlateCarree()
    )

  cbar=plt.colorbar(
    shade,orientation="horizontal",
    shrink=0.6,
    aspect=25
    )
  
  cbar.ax.tick_params(labelsize=10)

if cvar != 0:
  contour=ax.contour(
  lons,lats,cvar2,
  levels=levc,
  colors="black",linewidths=1.0,
  transform=ccrs.PlateCarree()
   )
  ax.clabel(contour)

  

if uvar == "Ug" or uvar == "Ua" :
  step=12
  qx,qy,qk=1.1,-0.1,20
  vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  u2.values[::step,::step],
  v2.values[::step,::step],
  scale=400,
  width=0.005,
  color="black",
  transform=ccrs.PlateCarree()
   )

  ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

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
ax.set_title(f"{ex1}-{svar}-{cvar}-{vvar}{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex2}/QGVeq/{ex2}{svar}_{cvar}_{uvar}{vvar}_{lev}_dxdy{dx}_sigma{sigma}.png")

plt.close("all")


##Differemce
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)
ax.contourf(
      lons,lats,ter,
      cmap="Greys",
      extend="max",
      levels=np.arange(0,2000,100),
      transform=ccrs.PlateCarree()
    )

if svar != 0 :
  shade=ax.contourf(
    lons,lats,sdif,
    levels=levs_dif,
    cmap="bwr",
    extend="both",
    transform=ccrs.PlateCarree()
    )

  cbar=plt.colorbar(
    shade,orientation="horizontal",
    shrink=0.6,
    aspect=25
    )
  
  cbar.ax.tick_params(labelsize=10)


if cvar != 0:
  contour_plus=ax.contour(
  lons,lats,cdif*(10**10),
  levels=levc_plus,
  colors="red",linewidths=1.0,
  transform=ccrs.PlateCarree()
    )
  ax.clabel(contour_plus)

  contour_minus=ax.contour(
  lons,lats,cdif*(10**10),
  levels=levc_minus,
  colors="blue",linewidths=1.0,
  transform=ccrs.PlateCarree()
    )
  ax.clabel(contour_minus)

  
if uvar == "Ug" or uvar == "Ua" :
  step=12
  qx,qy,qk=1.1,-0.1,5
  vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  udif.values[::step,::step],
  vdif.values[::step,::step],
  scale=50,
  width=0.005,
  color="black",
  transform=ccrs.PlateCarree()
   )

  ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

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
#ax.set_title(f"Dif-{svar}-{cvar}-{vvar}{lev}-dx=dy={dx}")

plt.savefig(f"{fig_dir}/{ex2}/QGVeq/Dif_{svar}_{cvar}_{uvar}{vvar}_{lev}hpa_dxdy{dx}_sigma{sigma}.png")

plt.close("all")

print("End Program")
