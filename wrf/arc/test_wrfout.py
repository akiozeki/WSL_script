#from __from__ import print_function

from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

ncfile=Dataset("/home/akioz/MyWRF/output/2025DJF/CTL/wrfout_d01_2025-01-01_00:00:00")
#wrfoutファイルを読む

##変数の抽出・計算
slp=getvar(ncfile,"slp")
print(slp)
#SLP

theta=getvar(ncfile,"theta")
print(theta)
#温位

p=getvar(ncfile,"pressure")
print(p)
#圧力

u=getvar(ncfile,"ua")
v=getvar(ncfile,"va")
print("u->",u)
print("v->",v)

el=getvar(ncfile,"HGT")
print(el)
#標高

cart_proj=get_cartopy(slp)
#cartopyマッピングオブジェクトの取得
print(cart_proj)

lats,lons=latlon_coords(slp)
#緯度経度座標系を得る,これを設定しないとずれて地図を作図した時にヨーロッパ辺りが表示される

print("latitude",lats.values)
print("longitude",lons.values)


theta_850=interplevel(theta,p,850)
u_850=interplevel(u,p,850)
v_850=interplevel(v,p,850)
#print(theta_850)
#p系での変数を抽出する

#fig=plt.figure()
#
##ax=plt.axes(projection=ccrs.PlateCarree())
##ax=plt.axes(projection=cart_proj)
#ax=plt.axes(projection=ccrs.LambertConformal(central_longitude=135,central_latitude=35))
#
#contour=ax.contour(lons,lats,slp,colors="black",linewidths=0.8,transform=ccrs.PlateCarree())
#ax.clabel(contour)
#
#shade=ax.contourf(lons,lats,theta_850,cmap="coolwarm",transform=ccrs.PlateCarree())
##shade=ax.contourf(lons,lats,el,cmap="terrain",transform=ccrs.PlateCarree())
#plt.colorbar(shade)
#
#step=5
#qx,qy,qk=1.1,-0.1,10
#vector=ax.quiver(
#  lons.values[::step,::step],
#  lats.values[::step,::step],
#  u_850.values[::step,::step],
#  v_850.values[::step,::step],
#  scale=400,
#  color="green",
#  transform=ccrs.PlateCarree())
#  
#ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")
#
##ax.set_xticks(np.arange(125,150,5))
##ax.set_yticks(np.arange(25,50,5))
##axをcart_projで作るとうまくいかないaxが参照する座標軸と一致しないから？
#
##ax.set_xticks(np.arange(120,150,5),crs=ccrs.PlateCarree())
##ax.set_yticks(np.arange(20,50,5),crs=ccrs.PlateCarree())
##こちらはラベルがメートル単位になってうまくいかない
#
#
#####緯度経度ラベルを表示する(ChatGPTが教えてくれた)
#gl = ax.gridlines(draw_labels=True)
##gl.xformatter = LONGITUDE_FORMATTER
#gl.yformatter = LATITUDE_FORMATTER
#gl.top_labels = False
#gl.right_labels = False
#######
#
#ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
#ax.set_title("2024-01-01-12UTC",fontsize=20)
##ax.set_title("Elevation_25km_grid")
#
#plt.tight_layout()
#plt.savefig("/home/akioz/fig/wrf/plottest_20240101_12UTC_cart_proj_mercator.png")
##plt.savefig("../fig/cart_proj_elevation.png")
