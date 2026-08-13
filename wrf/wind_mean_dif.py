from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel
import metpy.calc as mpcalc
from metpy.units import units
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import xarray as xr
from scipy.stats import ttest_ind
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

lev=950

case="2025DJF"
ex1="CTL_lamb"
ex2="ME00_lamb"

map_proj="lambert"

dx=25000
dy=25000
ref_lat=42.5
div_factor=100000

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"


start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
print(f"Set Time : {start_date}----{end_date}")

u_list1=[]
u_list2=[]
v_list1=[]
v_list2=[]
div_list1=[]
div_list2=[]

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

#変数取り出す
  p1=getvar(ds1,"p",units="hpa")
  ua1=getvar(ds1,"ua",units="m/s")
  u1=interplevel(ua1,p1,lev)
  u_list1.append(u1)

  va1=getvar(ds1,"va",units="m/s")
  v1=interplevel(va1,p1,lev)
  v_list1.append(v1)

  p2=getvar(ds2,"p",units="hpa")
  ua2=getvar(ds2,"ua",units="m/s")
  u2=interplevel(ua2,p2,lev)
  u_list2.append(u2)

  va2=getvar(ds2,"va",units="m/s")
  v2=interplevel(va2,p2,lev)
  v_list2.append(v2)

#水平風発散の計算
  if date == start_date:
    land1=getvar(ds1,"LANDMASK")
    land2=getvar(ds2,"LANDMASK")
    cart_proj=get_cartopy(land1)
    lats,lons=latlon_coords(land1)
    rate_cos=np.cos(ref_lat*np.pi/180)/np.cos(lats*np.pi/180)
    el1=getvar(ds1,"ter",units="m")
    el1=np.ma.masked_where(land1 != 1,el1)
    el2=getvar(ds2,"ter",units="m")
    el2=np.ma.masked_where(land2 != 1,el2)
  
  ds1.close()
  ds2.close()

  if map_proj == "lambert":
##Zの変数へユークリッド距離に応じた座標を付与
    u1 = u1.assign_coords({
      "west_east": np.arange(u1.west_east.size) * dx,
      "south_north": np.arange(u1.south_north.size) * dy
    })

    v1 = v1.assign_coords({
      "west_east": np.arange(v1.west_east.size) * dx,
      "south_north": np.arange(v1.south_north.size) * dy
    })

    du_dx1=u1.differentiate("west_east")
    dv_dy1=v1.differentiate("south_north")

    u2 = u2.assign_coords({
      "west_east": np.arange(u2.west_east.size) * dx,
      "south_north": np.arange(u2.south_north.size) * dy
    })

    v2 = v2.assign_coords({
      "west_east": np.arange(v2.west_east.size) * dx,
      "south_north": np.arange(v2.south_north.size) * dy
    })

    du_dx2=u2.differentiate("west_east")
    dv_dy2=v2.differentiate("south_north")

  elif map_proj == "mercator" :
    du_dx2=u2.differentiate("west_east")/dx * rate_cos
    dv_dy2=v2.differentiate("south_north")/dy

  div1=du_dx1 + dv_dy1
  div_list1.append(div1)
  div2=du_dx2 + dv_dy2
  div_list2.append(div2)

  date+=timedelta(hours=dh)

udarray1=xr.concat(u_list1,dim="time")
vdarray1=xr.concat(v_list1,dim="time")
udarray2=xr.concat(u_list2,dim="time")
vdarray2=xr.concat(v_list2,dim="time")
divdarray1=xr.concat(div_list1,dim="time")
divdarray2=xr.concat(div_list2,dim="time")

umean1=udarray1.mean(dim="time",skipna=True)
vmean1=vdarray1.mean(dim="time",skipna=True)
umean2=udarray2.mean(dim="time",skipna=True)
vmean2=vdarray2.mean(dim="time",skipna=True)
divmean1=divdarray1.mean(dim="time",skipna=True)
divmean2=divdarray2.mean(dim="time",skipna=True)


divmean1=np.ma.masked_where(land1 == 1,divmean1)
divmean2=np.ma.masked_where(land2 == 1,divmean2)


udif=umean1 - umean2
vdif=vmean1 - vmean2
divdif=divmean1 - divmean2

##Plot
#ex1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([120,140,35,47])

# shade=ax.contourf(
#   lons,lats,el1,
#   levels=np.arange(0,2000,100),
#   cmap="gray",
#   transform=ccrs.PlateCarree()
#   )

shade=ax.contourf(
  lons,lats,divmean1*div_factor,
  levels=np.arange(-2.5,3,0.5),
  cmap="bwr",
  extend="both",
  transform=ccrs.PlateCarree()
  )
cbar=plt.colorbar(
  shade,
  orientation="horizontal",
  shrink=0.8,aspect=20
  )

cbar.ax.tick_params(labelsize=12)

shade2=ax.contourf(lons,lats,el1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

step=6
qx,qy,qk=1.1,-0.5,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  umean1.values[::step,::step],
  vmean1.values[::step,::step],
  scale=100,
  width=0.01,
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
ax.set_title(f"{ex1}-Wind{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex1}/{ex1}Wind{lev}.png")
plt.close("all")

#ex2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([120,140,35,47])

shade=ax.contourf(
  lons,lats,divmean2*div_factor,
  cmap="bwr",
  extend="both",
  levels=np.arange(-2.5,3,0.5),
  transform=ccrs.PlateCarree()
  )
cbar=plt.colorbar(
  shade,
  orientation="horizontal",
  shrink=0.8,aspect=20
  )

shade2=ax.contourf(lons,lats,el1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

step=6
qx,qy,qk=1.1,-0.5,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  umean2.values[::step,::step],
  vmean2.values[::step,::step],
  scale=100,
  width=0.01,
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
#ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-Wind{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/{ex2}Wind{lev}.png")
plt.close("all")

#Dif
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([120,140,35,47])


shade=ax.contourf(
  lons,lats,divdif*div_factor,
  levels=np.arange(-2.5,3,0.5),
  cmap="bwr",
  extend="both",
  transform=ccrs.PlateCarree()
  )
cbar=plt.colorbar(
  shade,label="1e-5 [ /s ]",
  orientation="horizontal",
  shrink=0.8,aspect=20
  ) 

shade2=ax.contourf(lons,lats,el1,levels=np.arange(0,2000,100),cmap="Greys",transform=ccrs.PlateCarree())

step=6
qx,qy,qk=1.1,-0.5,5
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  udif.values[::step,::step],
  vdif.values[::step,::step],
  scale=100,
  width=0.01,
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
ax.set_title(f"{ex1} - {ex2}-Wind{lev}",fontsize=20)

plt.savefig(f"{fig_dir}/{ex2}/Dif_Wind{lev}.png")
plt.close("all")

print("End Program")
