##ココでは温位と鉛直風をプロット
from __future__ import print_function, division
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from wrf import getvar, vertcross, CoordPair
import matplotlib.pyplot as plt
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

theta1_list=[]
theta2_list=[]
w1_list=[]
w2_list=[]

#断面図の位置設定
##例のごとくlatlon->yx変換
wrfinput=f"{wrfout_dir}/{ex1}/wrfinput_d01"
input_ds=Dataset(wrfinput)
lat=getvar(input_ds,"lat")
lon=getvar(input_ds,"lon")

start_lat,start_lon=36,132
end_lat,end_lon=44,132


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
  theta1=getvar(ds1,"theta",units="K")
  w1=getvar(ds1,"wa",units="m/s")
  lat=getvar(ds1,"lat")
  lon=getvar(ds1,"lon")

  z2=getvar(ds2,"z")
  theta2=getvar(ds2,"theta",units="K")
  w2=getvar(ds2,"wa",units="m/s")



#断面データを取り出す
  start_point=CoordPair(x=sx,y=sy)
  end_point=CoordPair(x=ex,y=ey)

  theta1_vert=vertcross(theta1,z1,start_point=start_point,end_point=end_point,latlon=True)
  theta1_list.append(theta1_vert)

  w1_vert=vertcross(w1,z1,start_point=start_point,end_point=end_point,latlon=True)

#座標情報を取りだす
  if date == end_date:
    vert=w1_vert.vertical.values
    idx=w1_vert.cross_line_idx.values

  w1_list.append(w1_vert.values)
  theta2_vert=vertcross(theta2,z2,start_point=start_point,end_point=end_point,latlon=True)
  theta2_list.append(theta2_vert)

  w2_vert=vertcross(w2,z2,start_point=start_point,end_point=end_point,latlon=True)
  w2_list.append(w2_vert)
    
  print(theta1_list)
  print(w1_list)

  ds1.close()
  ds2.close()

  date+=timedelta(hours=dh)

theta1_array=np.stack(theta1_list,axis=0)
theta1_mean=np.nanmean(theta1_array,axis=0)
#print(theta1_array)
#print(theta1_mean)

theta2_array=np.stack(theta2_list,axis=0)
theta2_mean=np.nanmean(theta2_array,axis=0)

w1_array=np.stack(w1_list,axis=0)
w1_mean=np.nanmean(w1_array,axis=0)
print(w1_mean)

w2_array=np.stack(w2_list,axis=0)
w2_mean=np.nanmean(w2_array,axis=0)

theta_dif=theta1_mean - theta2_mean
w_dif=w1_mean - w2_mean
print(theta_dif)

udummy=np.zeros_like(w1_mean)
#v方向は描かないので，0埋め配列を置く


#Plot 
#ex1
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
#ax.set_xlabel("Longitude")
ax.set_xlabel("Latitude")
ax.set_ylabel("Height[m]")
ax.set_ylim(0,3000)
shade=ax.contourf(idx,vert,theta1_mean,levels=cmaplev,cmap="bwr")
cbar=plt.colorbar(shade)
#cbar.ax.set_xlabel("K",rotation=90,labelpad=20)
#cbar.ax.tick_params(labelsize=10)

    
contour=ax.contour(idx,vert,theta1_mean,levels=cmaplev,colors="black",linewidths=1.0)
ax.clabel(contour)

xstep=2
qx,qy,qk=0.9,1.03,5
vector=ax.quiver(
  idx[::xstep],
  vert,
  udummy[:,::xstep],
  w1_mean[:,::xstep]*100,
  scale=200,
  width=0.008,
  color="green"
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}cm/s")

ax.set_title(f"{ex1}-Vertical")
plt.tight_layout()
#ax.invert_yaxis()鉛直軸反転
#plt.savefig(f"{fig_dir}/{ex1}/vert/{ex1}_{case}_wtheta_wevertical.png")
plt.savefig(f"{fig_dir}/{ex1}/vert/{ex1}_{case}_wtheta_snvertical.png")
plt.close("all")

#ex2
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
#ax.set_xlabel("Longitude")
ax.set_xlabel("Latitude")
ax.set_ylabel("Height[m]")
ax.set_ylim(0,3000)
shade=ax.contourf(idx,vert,theta2_mean,levels=cmaplev,cmap="bwr")
plt.colorbar(shade)
    
contour=ax.contour(idx,vert,theta2_mean,levels=cmaplev,colors="black",linewidths=1.0)
ax.clabel(contour)

xstep=2
qx,qy,qk=0.9,1.03,5
vector=ax.quiver(
  idx[::xstep],
  vert,
  udummy[:,::xstep],
  w2_mean[:,::xstep]*100,
  scale=200,
  width=0.008,
  color="green"
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}cm/s")

ax.set_title(f"{ex2}-Vertical")
plt.tight_layout()
#ax.invert_yaxis()鉛直軸反転
#plt.savefig(f"{fig_dir}/{ex2}/vert/{ex2}_{case}_wtheta_wevertical.png")
plt.savefig(f"{fig_dir}/{ex2}/vert/{ex2}_{case}_wtheta_snvertical.png")
plt.close("all")

#difference
plt.rcParams["font.size"]=16
fig=plt.figure()
ax=plt.axes()
ax.set_xticks([])      
#ax.set_xlabel("Longitude")
ax.set_xlabel("Latitude")
ax.set_ylabel("Height[m]")
ax.set_ylim(0,3000)
shade=ax.contourf(idx,vert,theta_dif,levels=cmaplev_a,cmap="bwr")
plt.colorbar(shade)
    
contour=ax.contour(idx,vert,theta_dif,levels=cmaplev_a,colors="black",linewidths=1.0)
ax.clabel(contour)

xstep=2
qx,qy,qk=0.9,1.03,5
vector=ax.quiver(
  idx[::xstep],
  vert,
  udummy[:,::xstep],
  w_dif[:,::xstep]*100,
  scale=200,
  width=0.008,
  color="green"
  )

ax.quiverkey(vector,qx,qy,qk,f"{qk}cm/s")

ax.set_title(f"{ex1} - {ex2}-Vertical")
plt.tight_layout()
#ax.invert_yaxis()鉛直軸反転
#plt.savefig(f"{fig_dir}/{ex2}/vert/Dif_{case}_wtheta_wevertical.png")
plt.savefig(f"{fig_dir}/{ex2}/vert/Dif_{case}_wtheta_snvertical.png")
plt.close("all")

print("End Program")    
