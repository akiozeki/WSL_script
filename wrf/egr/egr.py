#任意高度のegr,安定度,鉛直シアの期間平均をを求める

from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel,ALL_TIMES
import metpy.calc as mpcalc
from metpy.units import units
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

case="2025DJF"
ex1="CTL"
ex2="ME00"
wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output"
fig_dir=f"/home/akioz/fig/wrf/{case}"

start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
print(f"Set Time : {start_date}----{end_date} dh={dh}")



#求める気圧面および差分近似の上端下端
p=850
p_t=800
p_w=900

#変数EGR or revN or Ushear
#var="EGR"
#varlabel="[ /Day ]"
#factor=86400
#単位変化のための係数

#var="revN"
#varlabel="[ 10^2 s ]"
#factor=0.01

var="Ushear"
varlabel="[ m/s /km ]"
factor=1000

#作図の描画設定
domain=[127,145,35,44]
#カラーマップの配列　上からEGR,revN,Usheaer用
#cmaplev=np.arange(0,2.8,0.4)
#cmaplev=np.arange(0.5,1.2,0.1)
cmaplev=np.arange(0,14,2)

#cmaplev_a=np.arange(-0.9,1.1,0.2)
#cmaplev_a=np.arange(-0.25,0.35,0.1)
cmaplev_a=np.arange(-5.25,6.75,1.5)

cmaplev_r=np.arange(-0.4,2.8,0.4)


list1=[]
list2=[]

date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day
  h=date.hour
  time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}:00:00"
  print(time_str)

#ファイルオープンと変数取り出し
  ds1=Dataset(f"{wrfout_dir}/{case}/{ex1}/wrfout_d01_{time_str}")
  lat1=getvar(ds1,"lat")
  p1=getvar(ds1,"p",units="hpa")
#getvarするときは単位指定推奨  

  theta1=getvar(ds1,"theta",units="K")
  theta1_t=interplevel(theta1,p1,p_t)
  theta1_m=interplevel(theta1,p1,p)
  theta1_w=interplevel(theta1,p1,p_w)

  u1=getvar(ds1,"ua",units="ms-1")
  u1_t=interplevel(u1,p1,p_t)
  u1_w=interplevel(u1,p1,p_w)

  z1=getvar(ds1,"z",units="m")
  z1_t=interplevel(z1,p1,p_t)
  z1_w=interplevel(z1,p1,p_w)

#陸面マスク,投影法,緯度経度座標もここで取得する
  if date == end_date:
    land=getvar(ds1,"LANDMASK")
    cart_proj=get_cartopy(land)
    lats,lons=latlon_coords(land)

  ds1.close()

  ds2=Dataset(f"{wrfout_dir}/{case}/{ex2}/wrfout_d01_{time_str}")
  lat2=getvar(ds2,"lat")
  p2=getvar(ds2,"p",units="hpa")

  theta2=getvar(ds2,"theta",units="K")
  theta2_t=interplevel(theta2,p2,p_t)
  theta2_m=interplevel(theta2,p2,p)
  theta2_w=interplevel(theta2,p2,p_w)

  u2=getvar(ds2,"ua",units="ms-1")
  u2_t=interplevel(u2,p2,p_t)
  u2_w=interplevel(u2,p2,p_w)

  z2=getvar(ds2,"z",units="m")
  z2_t=interplevel(z2,p2,p_t)
  z2_w=interplevel(z2,p2,p_w)

  ds2.close()

##計算
  g=9.81
  f1=mpcalc.coriolis_parameter(lat1)
  f2=mpcalc.coriolis_parameter(lat2)
 
  dz1 = z1_t - z1_w
  dz2 = z2_t - z2_w
  dtheta1 = theta1_t - theta1_w
  dtheta2 = theta2_t - theta2_w
  du1 = u1_t - u1_w
  du2 = u2_t - u2_w

  N1=np.sqrt((g/theta1_m)*(dtheta1/dz1))
  N2=np.sqrt((g/theta2_m)*(dtheta2/dz2))
#  print(N1.values)

#  gushear1=np.abs(du1/dz1)
#  gushear2=np.abs(du2/dz2)
  gushear1=(du1/dz1)
  gushear2=(du2/dz2)
#
#  print(gushear1.values)
  egr1=0.31*f1*(1/N1)*gushear1
  egr2=0.31*f2*(1/N2)*gushear2

  if var == "EGR" :
    print("EGR1 Space Mean = ",np.nanmean(egr1.values))
    print("EGR2 Space Mean = ",np.nanmean(egr2.values))
    list1.append(egr1)
    list2.append(egr2)

  elif var == "revN" :
    list1.append(N1)
    list2.append(N2)
    print("N1 Space Mean = ",np.nanmean(N1.values))
    print("N2 Space Mean = ",np.nanmean(N2.values))
 
  elif var == "Ushear" :
    list1.append(gushear1)
    list2.append(gushear2)
    print("Ushear1 Space Mean = ",np.nanmean(gushear1.values))
    print("Ushear2 Space Mean = ",np.nanmean(gushear2.values))
 
  else:
    print("Var Not Found")

  date+=timedelta(hours=dh)

darray1=xr.concat(list1,dim="time")
darray2=xr.concat(list2,dim="time")

mean1=darray1.mean(dim="time",skipna=True)
mean2=darray2.mean(dim="time",skipna=True)
mean1=np.ma.masked_where(land == 1,mean1)
mean2=np.ma.masked_where(land == 1,mean2)

if var == "revN" :
  anomean=1/mean1 - 1/mean2
  ratmean=mean2/mean1

else:
  anomean=mean1 - mean2
  ratmean=mean1 / mean2


##Plot
#Mean1
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)
if var == "revN" :
  shade=ax.contourf(
    lons,lats,1/mean1*factor,
    levels=cmaplev,cmap="Reds",transform=ccrs.PlateCarree()
    )

else :
  shade=ax.contourf(
    lons,lats,mean1*factor,
    levels=cmaplev,cmap="Reds",transform=ccrs.PlateCarree()
    )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.8,
  aspect=25,
  label=varlabel
  )

cbar.ax.tick_params(labelsize=10)
gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False


ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex1}-{case}Mean-{var}")

figname=f"{fig_dir}/{ex1}/{ex1}_{var}_Mean.png"
plt.savefig(figname)
print(f"Create Figure {figname}")

plt.close("all")

#Mean2
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)
if var == "revN" :
  shade=ax.contourf(
    lons,lats,1/mean2*factor,
    levels=cmaplev,cmap="Reds",transform=ccrs.PlateCarree()
    )

else :
  shade=ax.contourf(
    lons,lats,mean2*factor,
    levels=cmaplev,cmap="Reds",transform=ccrs.PlateCarree()
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
gl.xlines=False
gl.ylines=False


ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"{ex2}-{case}Mean-{var}")

figname=f"{fig_dir}/{ex2}/{ex2}_{var}_Mean.png"
plt.savefig(figname)
print(f"Create Figure {figname}")

plt.close("all")

#Ano
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)
shade=ax.contourf(
  lons,lats,anomean*factor,
  levels=cmaplev_a,cmap="bwr",transform=ccrs.PlateCarree()
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
gl.xlines=False
gl.ylines=False


ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"Ano-{case}Mean-{var}")

figname=f"{fig_dir}/Ano/Ano_{var}_Mean.png"
plt.savefig(figname)
print(f"Create Figure {figname}")

plt.close("all")

#Rate
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent(domain)
shade=ax.contourf(
  lons,lats,ratmean,
  levels=cmaplev_r,cmap="bwr",transform=ccrs.PlateCarree()
  )

cbar=plt.colorbar(
  shade,orientation="horizontal",
  shrink=0.6,
  aspect=25,
  )

#ax.plot([122,137],[40.5,40.5],color="blue",linewidth=3.0,transform=ccrs.PlateCarree())

cbar.ax.tick_params(labelsize=10)
gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlines=False
gl.ylines=False


ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"Rate-{case}Mean-{var}")

figname=f"{fig_dir}/Rate/Rate_{var}_Mean.png"
plt.savefig(figname)
print(f"Create Figure {figname}")
plt.close("all")


print("End Program")  
