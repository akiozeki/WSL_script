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

vcord="pressure"
vunit="hPa"
left=31
right=60
vtop=500
vbottom=1000
xstep=1
vstep=8
#ベクトルの間引き間隔

levs=np.arange(0,0.25,0.05)
levs_dif=np.arange(-7.5*10**-2,8.5*10**-2,1*10**-2)
levc_dif=np.arange(-4.5,5.5,1)
levc=np.arange(260,324,4)
# levc_dif=np.arange(-5,6,1.0)


wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"


start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
print(f"Set Time : {start_date}----{end_date}")

theta1_list=[]
theta2_list=[]
dtheta_dp1_list=[]
dtheta_dp2_list=[]
omg1_list=[]
omg2_list=[]

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

  p1=getvar(ds1,"pressure")
  theta1=getvar(ds1,"theta",units="K")
  omg1=getvar(ds1,"omg")
  lat=getvar(ds1,"lat")
  lon=getvar(ds1,"lon")

  p2=getvar(ds2,"pressure")
  theta2=getvar(ds2,"theta",units="K")
  omg2=getvar(ds2,"omg")


#断面データを取り出す
  start_point=CoordPair(x=sx,y=sy)
  end_point=CoordPair(x=ex,y=ey)

  theta1_vert=vertcross(theta1,p1,start_point=start_point,end_point=end_point,latlon=True)
#  print(theta1_vert)
#ここからの温位の鉛直勾配 [K/hPa] を求める  
  if date == start_date :
    vert=theta1_vert.vertical.values
    idx=theta1_vert.cross_line_idx.values
    print("p_array",vert)
#最初のループのみ断面データの鉛直座標を取得 

  dtheta_dp1=xr.DataArray(
    np.gradient(theta1_vert.values,vert,axis=0),
    coords=theta1_vert.coords,
    dims=theta1_vert.dims
  ) 
#  print(dtheta_dp1)
  omg1_vert=vertcross(omg1,p1,start_point=start_point,end_point=end_point,latlon=True)
 
  theta1_list.append(theta1_vert)
  dtheta_dp1_list.append(dtheta_dp1)
  omg1_list.append(omg1_vert)

  theta2_vert=vertcross(theta2,p2,start_point=start_point,end_point=end_point,latlon=True)
  dtheta_dp2=xr.DataArray(
    np.gradient(theta2_vert.values,vert,axis=0),
    coords=theta2_vert.coords,
    dims=theta2_vert.dims
  ) 
  omg2_vert=vertcross(omg2,p2,start_point=start_point,end_point=end_point,latlon=True) 

  theta2_list.append(theta2_vert)
  dtheta_dp2_list.append(dtheta_dp2)
  omg2_list.append(omg2_vert)
    
  #print(theta1_list)
  #print(u1_list)

#ここでどの断面を取ったかを表す平面図も描いておく
  if date == end_date:
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

    plt.savefig(f"{fig_dir}/{ex1}/vert/vert_cross_line({sx},{sy})to({ex},{ey}).png")
    plt.close("all")

  ds1.close()
  ds2.close()
  date+=timedelta(hours=dh)


theta1_array=np.stack(theta1_list,axis=0)
theta1_mean=np.nanmean(theta1_array,axis=0)
#print(theta1_array)
#print(theta1_mean)

theta2_array=np.stack(theta2_list,axis=0)
theta2_mean=np.nanmean(theta2_array,axis=0)

omg1_array=np.stack(omg1_list,axis=0)
omg1_mean=np.nanmean(omg1_array,axis=0)
#print(omg1_mean)

omg2_array=np.stack(omg2_list,axis=0)
omg2_mean=np.nanmean(omg2_array,axis=0)


dtheta_dp1_array=np.stack(dtheta_dp1_list,axis=0)
dtheta_dp1_mean=np.nanmean(dtheta_dp1_array,axis=0)

dtheta_dp2_array=np.stack(dtheta_dp2_list,axis=0)
dtheta_dp2_mean=np.nanmean(dtheta_dp2_array,axis=0)

theta_dif=theta1_mean - theta2_mean
omg_dif=omg1_mean - omg2_mean
dtheta_dp_dif=dtheta_dp1_mean - dtheta_dp2_mean

print(theta_dif)

xdummy=np.zeros_like(omg1_mean)
nan1=np.isnan(theta1_mean)
nan2=np.isnan(theta2_mean)
#x方向は描かないので，0埋め配列を置く


#Plot 
#ex1
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
ax.set_xlabel("Horizontal")
ax.set_ylabel(f"Vertical [{vunit}]")
ax.set_xlim(left,right)
ax.set_ylim(vbottom,vtop)
ax.contourf(idx,vert,nan1,levels=[0.5,1.5],colors=["black"])

shade=ax.contourf(idx,vert,dtheta_dp1_mean,levels=levs,extend="max",cmap="Reds")
cbar=plt.colorbar(shade)
#cbar.ax.set_xlabel("K",rotation=90,labelpad=20)
#cbar.ax.tick_params(labelsize=10)

contour=ax.contour(idx,vert,theta1_mean,levels=levc,colors="black",linewidths=1.0)
ax.clabel(contour)

qx,qy,qk=0.9,-0.1,1
vector=ax.quiver(
 idx[::xstep],
 vert[::vstep],
 xdummy[::vstep,::xstep],
 -omg1_mean[::vstep,::xstep],
 scale=10,
 width=0.008,
 color="orange"
 )

ax.quiverkey(vector,qx,qy,qk,"1 Pa/s")



#ax.set_title(f"{ex1}-Vertical")
plt.tight_layout()
#if vcord == "pressure" : ax.invert_yaxis()#鉛直軸反転
plt.savefig(f"{fig_dir}/{ex1}/vert/{ex1}-{case}_atheta_ap_vertical({sx},{sy})to({ex},{ey}).png")
plt.close("all")

#ex2
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
ax.set_xlabel("Horizontal")
ax.set_ylabel(f"Vertical [{vunit}]")
ax.set_xlim(left,right)
ax.set_ylim(vbottom,vtop)
ax.contourf(idx,vert,nan2,levels=[0.5,1.5],colors=["black"])

shade=ax.contourf(idx,vert,dtheta_dp2_mean,levels=levs,extend="max",cmap="Reds")
plt.colorbar(shade)
    
contour=ax.contour(idx,vert,theta2_mean,levels=levc,colors="black",linewidths=1.0)
ax.clabel(contour)


qx,qy,qk=0.9,-0.1,1
vector=ax.quiver(
  idx[::xstep],
  vert[::vstep],
  xdummy[::vstep,::xstep],
  -omg2_mean[::vstep,::xstep],
  scale=10,
  width=0.008,
  color="orange"
  )

ax.quiverkey(vector,qx,qy,qk,"1 Pa/s")

#ax.set_title(f"{ex2}-Vertical")
plt.tight_layout()
#if vcord == "pressure" : ax.invert_yaxis()#鉛直軸反転不要
plt.savefig(f"{fig_dir}/{ex2}/vert/{ex2}-{case}vertical_atheta_ap_({sx},{sy})to({ex},{ey}).png")
plt.close("all")

#difference
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
ax.set_xlabel("Horizontal")
ax.set_ylabel(f"Vertical [{vunit}]")
ax.set_xlim(left,right)
ax.set_ylim(vbottom,vtop)
ax.contourf(idx,vert,nan1,levels=[0.5,1.5],colors=["black"])

shade=ax.contourf(idx,vert,dtheta_dp_dif,levels=levs_dif,cmap="bwr",extend="both")
plt.colorbar(shade)
    
contour=ax.contour(idx,vert,theta_dif,levels=levc_dif,colors="black",linewidths=1.0)


ax.clabel(contour)

qx,qy,qk=0.9,-0.1,1
vector=ax.quiver(
  idx[::xstep],
  vert[::vstep],
  xdummy[::vstep,::xstep],
  -omg_dif[::vstep,::xstep],
  scale=5,
  width=0.008,
  color="green"
  )

ax.quiverkey(vector,qx,qy,qk,"1 Pa/s")

#ax.set_title(f"{ex1} - {ex2}-Vertical")
plt.tight_layout()
#if vcord == "pressure" : ax.invert_yaxis()#鉛直軸反転->不要
plt.savefig(f"{fig_dir}/{ex2}/vert/Dif-{case}vertical_atheta_ap_({sx},{sy})to({ex},{ey}).png")
plt.close("all")

print("End Program")    
