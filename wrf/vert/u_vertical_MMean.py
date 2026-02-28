##ココでは移動平均した温位と西風をプロット
from __future__ import print_function, division
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from wrf import getvar,vertcross,CoordPair,ALL_TIMES
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from datetime import datetime,timedelta


case="2025DJF"
plus=""
ex1="CTL"
ex2="ME00"

cmaplev=np.arange(264,286,2)
cmaplev_a=np.arange(-3.5,4.5,1.0)


wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
fig_dir=f"/home/akioz/fig/wrf/{case}"


start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
print(f"Set Time : {start_date}----{end_date}")

##移動平均の設定##
moving_day=7
step_per_day=4
step_all=moving_day*step_per_day
half_step=step_all/2
#######################

u1_list=[]
u2_list=[]

#断面図の位置設定
##例のごとくlatlon->yx変換
wrfinput=f"{wrfout_dir}/{ex1}/wrfinput_d01"
input_ds=Dataset(wrfinput)
lat=getvar(input_ds,"lat")
lon=getvar(input_ds,"lon")

start_lat,start_lon=40.5,122
end_lat,end_lon=40.5,137

start_dist=np.sqrt((lat-start_lat)**2+(lon-start_lon)**2)
sy,sx=np.unravel_index(np.argmin(start_dist.values),start_dist.shape)
print(f"start=(y,x)=({sy},{sx})")

end_dist=np.sqrt((lat-end_lat)**2+(lon-end_lon)**2)
ey,ex=np.unravel_index(np.argmin(end_dist.values),end_dist.shape)
print(f"start=(y,x)=({ey},{ex})")

u_list1=[]
u_list2=[]

date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day
  h=date.hour

  moving_list1=[]
  moving_list2=[]

  move_date=date -timedelta(hours=6*half_step)
  print(f"Caluculate_{moving_day}days_Moving_Mean")
  print("from",move_date)

  for t in range(step_all):
    my=move_date.year
    mm=move_date.month
    md=move_date.day
    mh=move_date.hour
    moving_time_str=f"{my}-{mm:02d}-{md:02d}_{mh:02d}:00:00"
  
    moving_file1=Dataset(f"{wrfout_dir}/{ex1}/wrfout_d01_{moving_time_str}")
    moving_file2=Dataset(f"{wrfout_dir}/{ex2}/wrfout_d01_{moving_time_str}")
    
    moving_list1.append(moving_file1)
    moving_list2.append(moving_file2)

    move_date+=timedelta(hours=dh)
#ココで移動平均内での時間更新      
  print("to",move_date)
 
  z1=getvar(moving_list1,"z",timeidx=ALL_TIMES,method="join",units="m")
  u1=getvar(moving_list1,"ua",timeidx=ALL_TIMES,method="join",units="m/s")

  z2=getvar(moving_list2,"z",timeidx=ALL_TIMES,method="join",units="m")
  u2=getvar(moving_list2,"ua",timeidx=ALL_TIMES,method="join",units="m/s")

#断面データを取り出す
  start_point=CoordPair(x=sx,y=sy)
  end_point=CoordPair(x=ex,y=ey)

  u_vert1=vertcross(u1,z1,start_point=start_point,end_point=end_point,latlon=True)
  u_vert_mmean1=u_vert1.mean(dim="file",skipna=True)
  u_list1.append(u_vert_mmean1.values)

##座標情報を取りだす
  if date == end_date and t == step_all-1:
    vert=u_vert1.vertical.values
    idx=u_vert1.cross_line_idx.values

  u_vert2=vertcross(u2,z2,start_point=start_point,end_point=end_point,latlon=True)
  u_vert_mmean2=u_vert2.mean(dim="file",skipna=True)
  u_list2.append(u_vert_mmean2.values)


  date+=timedelta(hours=dh)

print(u_list1)


u_array1=np.stack(u_list1,axis=0)
u_mean1=np.nanmean(u_array1,axis=0)

u_array2=np.stack(u_list2,axis=0)
u_mean2=np.nanmean(u_array2,axis=0)


u_dif=u_mean1 - u_mean2
print("u_dif:\n",u_dif)

vdummy=np.zeros_like(u_mean1)
#v方向は描かないので，0埋め配列を置く
print("vdummy:\n",vdummy)

##Plot 
ex1
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
ax.set_xlabel("Longitude")
ax.set_ylabel("Height[m]")
ax.set_ylim(0,3000)

shade=ax.contourf(idx,vert,u_mean1,levels=np.arange(0,18,3),cmap="Reds")
cbar=plt.colorbar(shade)
cbar.ax.tick_params(labelsize=14)

xstep=6
zstep=2
qx,qy,qk=0.9,-0.1,10
vector=ax.quiver(
  idx[::xstep],
  vert[::zstep],
  u_mean1[::zstep,::xstep],
  vdummy[::zstep,::xstep],
  scale=100,
  width=0.01,
  color="black"
  )
#qkは基準矢羽根の風速,scaleは長さ(小さいほど長い),widthは太さ(大きいほど太い)

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

ax.set_title(f"{ex1}-Vertical")
plt.tight_layout()
#ax.invert_yaxis()鉛直軸反転
#plt.savefig(f"{fig_dir}/{ex1}/vert/{ex1}MMean-{case}vertical.png")
plt.savefig(f"{fig_dir}/{ex1}/vert/{ex1}MMean-{case}vertical{start_lat}_U.png")
plt.close("all")

#ex2
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
ax.set_xlabel("Longitude")
ax.set_ylabel("Height[m]")
ax.set_ylim(0,3000)
shade=ax.contourf(idx,vert,u_mean2,levels=np.arange(0,18,3),cmap="Reds")
plt.colorbar(shade)
    

xstep=6
zstep=2
qx,qy,qk=0.9,-0.1,10
vector=ax.quiver(
  idx[::xstep],
  vert[::zstep],
  u_mean2[::zstep,::xstep],
  vdummy[::zstep,::xstep],
  scale=100,
  width=0.01,
  color="black"
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

ax.set_title(f"{ex2}-Vertical")
plt.tight_layout()
#ax.invert_yaxis()鉛直軸反転
plt.savefig(f"{fig_dir}/{ex2}/vert/{ex2}-MMean-{case}vertical{start_lat}_U.png")
plt.close("all")

#difference
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
ax.set_xlabel("Longitude")
ax.set_ylabel("Height[m]")
ax.set_ylim(0,3000)
shade=ax.contourf(idx,vert,u_dif,levels=np.arange(-9,11,2),cmap="bwr")
plt.colorbar(shade)
cbar.ax.tick_params(labelsize=14)
    
xstep=4
zstep=2
qx,qy,qk=0.9,-0.1,5
vector=ax.quiver(
  idx[::xstep],
  vert[::zstep],
  u_dif[::zstep,::xstep],
  vdummy[::zstep,::xstep],
  scale=50,
  width=0.01,
  color="black"
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

ax.set_title(f"{ex1} - {ex2}-Vertical")
plt.tight_layout()
#ax.invert_yaxis()鉛直軸反転
plt.savefig(f"{fig_dir}/{ex2}/vert/Dif-MMean-{case}vertical{start_lat}_U.png")
plt.close("all")

print("End Program")    
