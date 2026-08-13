##ココでは温位と西風をプロット
from __future__ import print_function, division
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from wrf import getvar, vertcross, CoordPair,get_cartopy,latlon_coords
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

case="2025DJF"
ex1="CTL_lamb"
ex2="ME00_lamb"

#vcord="z"
#vunit="m"
vcord="pressure"
vunit="hPa"
vtop=300
vbottom=1000
#鉛直座標

svar="theta"
#svar=0

cvar="theta"
#cvar=0

vvar="u"
#vvar=0

levs=np.arange(260,324,4)
levs_dif=np.arange(-7,9,2.0)
#levc=np.arange(0,10000,500)
#levc_dif=np.arange(-18,22,4)
levc=np.arange(260,324,4)
levc_dif=np.arange(-7,9,2.0)
#levs=np.arange(0,10000,500)
#levs_dif=np.arange(-18,22,4)


wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"


start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
print(f"Set Time : {start_date}----{end_date}")

z1_list=[]
z2_list=[]
theta1_list=[]
theta2_list=[]
u1_list=[]
u2_list=[]

#断面図の位置設定
##例のごとくlatlon->yx変換
wrfinput=f"{wrfout_dir}/{ex1}/wrfinput_d01"
input_ds=Dataset(wrfinput)
lat=getvar(input_ds,"lat")
lon=getvar(input_ds,"lon")

# start_lat,start_lon=40.5,122
# end_lat,end_lon=40.5,137
start_lat,start_lon=50,120
end_lat,end_lon=30,135

start_dist=np.sqrt((lat-start_lat)**2+(lon-start_lon)**2)
sy,sx=np.unravel_index(np.argmin(start_dist.values),start_dist.shape)
print(f"start=(y,x)=({sy},{sx})")

end_dist=np.sqrt((lat-end_lat)**2+(lon-end_lon)**2)
ey,ex=np.unravel_index(np.argmin(end_dist.values),end_dist.shape)
print(f"start=(y,x)=({ey},{ex})")

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

  ds1=Dataset(wrfout1)
  ds2=Dataset(wrfout2)


  z1=getvar(ds1,"z")
  p1=getvar(ds1,"pressure")
  theta1=getvar(ds1,"theta",units="K")
  u1=getvar(ds1,"ua",units="m/s")
  lat=getvar(ds1,"lat")
  lon=getvar(ds1,"lon")

  z2=getvar(ds2,"z")
  p2=getvar(ds2,"pressure")
  theta2=getvar(ds2,"theta",units="K")
  u2=getvar(ds2,"ua",units="m/s")



#断面データを取り出す
  start_point=CoordPair(x=sx,y=sy)
  end_point=CoordPair(x=ex,y=ey)

  if vcord == "z" :
    theta1_vert=vertcross(theta1,z1,start_point=start_point,end_point=end_point,latlon=True)
    u1_vert=vertcross(u1,z1,start_point=start_point,end_point=end_point,latlon=True)

  elif vcord == "pressure" :
    z1_vert=vertcross(z1,p1,start_point=start_point,end_point=end_point,latlon=True)
    z1_list.append(z1_vert)

    theta1_vert=vertcross(theta1,p1,start_point=start_point,end_point=end_point,latlon=True)
    u1_vert=vertcross(u1,p1,start_point=start_point,end_point=end_point,latlon=True)

  theta1_list.append(theta1_vert)
  u1_list.append(u1_vert.values)

#座標情報を取りだす
  if date == end_date:
#ここでどの断面を取ったかを表す図も描いておく
    ter=getvar(ds1,"ter",units="m")
    cart_proj=get_cartopy(ter)
    lats,lons=latlon_coords(ter)
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.plot(
      [start_lon,end_lon],
      [start_lat,end_lat],
      color="blue",
      linewidth=3,
      transform=ccrs.PlateCarree()
    )

    ax.contourf(
      lons,lats,ter,
      cmap="Greys",
      extend="max",
      levels=np.arange(0,2000,100),
      transform=ccrs.PlateCarree()
    )
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

    plt.savefig(f"{fig_dir}/{ex1}/vert_cross_line({sx},{sy})to({ex},{ey}).png")
    plt.close("all")

    vert=u1_vert.vertical.values
    idx=u1_vert.cross_line_idx.values

  if vcord == "z" :
    theta2_vert=vertcross(theta2,z2,start_point=start_point,end_point=end_point,latlon=True)
    u2_vert=vertcross(u2,z2,start_point=start_point,end_point=end_point,latlon=True)
   
  elif vcord == "pressure" :
    z2_vert=vertcross(z2,p2,start_point=start_point,end_point=end_point,latlon=True)
    z2_list.append(z2_vert)

    theta2_vert=vertcross(theta2,p2,start_point=start_point,end_point=end_point,latlon=True)
    u2_vert=vertcross(u2,p2,start_point=start_point,end_point=end_point,latlon=True) 

  theta2_list.append(theta2_vert)
  u2_list.append(u2_vert)
    
  #print(theta1_list)
  #print(u1_list)

  ds1.close()
  ds2.close()

  date+=timedelta(hours=dh)

if vcord == "pressure" :
  z1_array=np.stack(z1_list,axis=0)
  z1_mean=np.nanmean(z1_array,axis=0)
  z2_array=np.stack(z2_list,axis=0)
  z2_mean=np.nanmean(z2_array,axis=0)
  z_dif=z1_mean - z2_mean

theta1_array=np.stack(theta1_list,axis=0)
theta1_mean=np.nanmean(theta1_array,axis=0)
#print(theta1_array)
#print(theta1_mean)

theta2_array=np.stack(theta2_list,axis=0)
theta2_mean=np.nanmean(theta2_array,axis=0)

u1_array=np.stack(u1_list,axis=0)
u1_mean=np.nanmean(u1_array,axis=0)
print(u1_mean)

u2_array=np.stack(u2_list,axis=0)
u2_mean=np.nanmean(u2_array,axis=0)

theta_dif=theta1_mean - theta2_mean
u_dif=u1_mean - u2_mean
print(theta_dif)

vdummy=np.zeros_like(u1_mean)
nan1=np.isnan(theta1_mean)
nan2=np.isnan(theta2_mean)
#v方向は描かないので，0埋め配列を置く


#Plot 
#ex1
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
ax.set_xlabel("Horizontal")
ax.set_ylabel(f"Vertical [{vunit}]")
ax.set_ylim(vbottom,vtop)

ax.contourf(idx,vert,nan1,levels=[0.5,1.5],colors=["black"])

shade=ax.contourf(idx,vert,theta1_mean,levels=levs,extend="both",cmap="bwr")
cbar=plt.colorbar(shade)
#cbar.ax.set_xlabel("K",rotation=90,labelpad=20)
#cbar.ax.tick_params(labelsize=10)

   
contour=ax.contour(idx,vert,theta1_mean,levels=levc,colors="black",linewidths=1.0)
ax.clabel(contour)

# xstep=4
# vstep=4
# qx,qy,qk=0.9,1.03,10
# vector=ax.quiver(
#  idx[::xstep],
#  vert[::vstep],
#  u1_mean[::vstep,::xstep],
#  vdummy[::vstep,::xstep],
#  scale=200,
#  width=0.008,
#  color="green"
#  )

# ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

ax.set_title(f"{ex1}-Vertical")
plt.tight_layout()
#if vcord == "pressure" : ax.invert_yaxis()#鉛直軸反転
plt.savefig(f"{fig_dir}/{ex1}/vert/{ex1}-{case}vertical({sx},{sy})to({ex},{ey}).png")
plt.close("all")

#ex2
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
ax.set_xlabel("Horizontal")
ax.set_ylabel(f"Vertical [{vunit}]")
ax.set_ylim(vbottom,vtop)
ax.contourf(idx,vert,nan2,levels=[0.5,1.5],colors=["black"])

shade=ax.contourf(idx,vert,theta2_mean,levels=levs,extend="both",cmap="bwr")
plt.colorbar(shade)
    
contour=ax.contour(idx,vert,theta2_mean,levels=levc,colors="black",linewidths=1.0)
ax.clabel(contour)

# xstep=4
# vstep=4
# qx,qy,qk=0.9,1.03,10
# vector=ax.quiver(
#   idx[::xstep],
#   vert[::vstep],
#   u2_mean[::vstep,::xstep],
#   vdummy[::vstep,::xstep],
#   scale=200,
#   width=0.008,
#   color="green"
#   )

# ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

ax.set_title(f"{ex2}-Vertical")
plt.tight_layout()
#if vcord == "pressure" : ax.invert_yaxis()#鉛直軸反転不要
plt.savefig(f"{fig_dir}/{ex2}/vert/{ex2}-{case}vertical({sx},{sy})to({ex},{ey}).png")
plt.close("all")

#difference
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
ax.set_xlabel("Horizontal")
ax.set_ylabel(f"Vertical [{vunit}]")
ax.set_ylim(vbottom,vtop)
ax.contourf(idx,vert,nan1,levels=[0.5,1.5],colors=["black"])

shade=ax.contourf(idx,vert,theta_dif,levels=levs_dif,cmap="bwr",extend="both")
plt.colorbar(shade)
    
contour=ax.contour(idx,vert,theta_dif,levels=levc_dif,colors="black",linewidths=2.0)
ax.clabel(contour)

# xstep=4
# vstep=4
# qx,qy,qk=0.9,1.03,2
# vector=ax.quiver(
#   idx[::xstep],
#   vert[::vstep],
#   u_dif[::vstep,::xstep],
#   vdummy[::vstep,::xstep],
#   scale=50,
#   width=0.008,
#   color="green"
#   )

# ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

#ax.set_title(f"{ex1} - {ex2}-Vertical")
plt.tight_layout()
#if vcord == "pressure" : ax.invert_yaxis()#鉛直軸反転->不要
plt.savefig(f"{fig_dir}/{ex2}/vert/Dif-{case}vertical({sx},{sy})to({ex},{ey}).png")
plt.close("all")

print("End Program")    
