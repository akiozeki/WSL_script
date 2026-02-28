###ここでは実験ごとに渦度方程式の右辺各項(Adv.theta_g, Adv.f, Stretching)を求めてnetCDFファイルに保存する
from datetime import datetime,timedelta
import math
from netCDF4 import Dataset
from wrf import getvar,interplevel
import numpy as np
import xarray as xr

##出力形式
mode=1
#0:地衡風と地衡風渦度,1:準地衡渦度方程式(QGVep)の右辺


##実験設定
case="2025DJF"
#ex="CTL"
ex="ME00"

lev=850
skip=8
#グリッドを間引く間隔

start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
print(f"Set Time : {start_date}----{end_date} dh={dh}")

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output"
output_dir=f"/home/akioz/calculate/wrf/{case}/QGVeq"

##定数
a=6370*10**3
g=9.81
omega=7.292*10**-5
#Holton,p12参照
ref_lat=42.5
f0=2*omega*math.sin(math.radians(ref_lat))

dx=25*(10**3)*skip
dy=25*(10**3)*skip

print("a =",a)
print("g =",g)
print("Ω =",omega)
print("ref_lat =",ref_lat)
print("f0 =",f0)
print("dx=dy=",dx)

list1=[]
list2=[]
list3=[]

date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day
  h=date.hour
  time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}:00:00"
  print(time_str)

##変数取り出し
  ds=Dataset(f"{wrfout_dir}/{case}/{ex}/wrfout_d01_{time_str}")
  
  lat=getvar(ds,"lat")
  p=getvar(ds,"p",units="hpa")

  ua=getvar(ds,"ua",units="ms-1")
  va=getvar(ds,"va",units="ms-1")
  za=getvar(ds,"z",units="m")

  u=interplevel(ua,p,lev)
  v=interplevel(va,p,lev)
  z=interplevel(za,p,lev)

##グリッドを間引く
  lat=lat[::skip,::skip]
  u=u[::skip,::skip]
  v=v[::skip,::skip]
  z=z[::skip,::skip]

#  print(z)

  ds.close()

##計算
  rate_cos=np.cos(ref_lat*np.pi/180)/np.cos(lat*np.pi/180)
#  print(rate_cos)
  #メルカトル図法のWRFはdxが一定でなくref_latで設定した緯度のみ設定した値,残りは等緯度となるように出力されるので緯度による重みづけが必要  

#ジオポテンシャル高度の水平偏微分 *x微分には緯度の重み付けが必要！！
  dz_dx=np.gradient(z,dx,axis=1)*rate_cos
  dz_dy=np.gradient(z,dy,axis=0)*(rate_cos/rate_cos)
#  print("dz_dx",dz_dx)
#  print("dz_dy",dz_dy)

#地衡風と地衡風渦度
  u_g=-(g/f0)*dz_dy
  v_g=(g/f0)*dz_dx
  dv_g_dx=np.gradient(v_g,dx,axis=1)*rate_cos
  du_g_dy=np.gradient(u_g,dy,axis=0)
  th_g=dv_g_dx - du_g_dy

  if mode == 0:
    list1.append(u_g)
    list2.append(v_g)
    list3.append(th_g)

#  print("u_g",u_g)
#  print("v_g",v_g)
#  print("th_g",th_g)
  elif mode == 1:

#相対渦度移流項
    dth_g_dx=np.gradient(th_g,dx,axis=1)*rate_cos
    dth_g_dy=np.gradient(th_g,dy,axis=0)
  
    adv_th_g= - (u_g*dth_g_dx + v_g*dth_g_dy)
  #  print("相対渦度移流項:",adv_th_g)

    list1.append(adv_th_g)


#惑星渦度移流項(ベータ項)
#    f=2*omega*np.sin(lat*(np.pi/180))
#    beta=np.gradient(f,dy,axis=0)
#β面近似では一定値として求めている
    beta=2*omega*np.cos(ref_lat*np.pi/180)/a


#    print("df_dy",df_dy)
    adv_f= - beta*v_g
#    print("ベータ項:",adv_f)

    list2.append(adv_f)

#ストレッチング項
#    u_a=u - u_g
#    v_a=v - v_g
#    du_a_dx=np.gradient(u_a,dx,axis=1)*rate_cos
#    dv_a_dy=np.gradient(v_a,dy,axis=0)
#    stretching= - f0*(du_a_dx + dv_a_dy)
#この方法は誤差が非地衡風を使うので誤差が大きい？→残差として求める
    stretching=0 - adv_th_g - adv_f

#    print("ストレッチング項:",stretching)

    list3.append(stretching)

  date+=timedelta(hours=dh)

da1=xr.concat(list1,dim="time")
mean1=da1.mean(dim="time",skipna=True)

da2=xr.concat(list2,dim="time")
mean2=da2.mean(dim="time",skipna=True)

da3=xr.concat(list3,dim="time")
mean3=da3.mean(dim="time",skipna=True)

if mode == 0:
  print("ug",mean1)
  print("vg",mean2)
  print("地衡風渦度",mean3)

  mean1=mean1.rename("u_g")
  mean2=mean2.rename("v_g")
  mean3=mean3.rename("theta_g")
  
  ds_out=xr.merge([mean1,mean2,mean3])
  print(ds_out)

  output=f"{output_dir}/{ex}{lev}hpa_GWind_dxdy{int(dy/1000)}.nc"

elif mode == 1:
  print("相対渦度移流:",mean1)
  print("惑星渦度移流",mean2)
  print("ストレッチング",mean3)


  mean1=mean1.rename("Adv.theta_g")
  mean2=mean2.rename("Adv.f")
  mean3=mean3.rename("Stretching")

  ds_out=xr.merge([mean1,mean2,mean3])
  print(ds_out)

  output=f"{output_dir}/{ex}{lev}hpa_QGVeq_LightHand_dxdy{int(dy/1000)}.nc"

ds_out.to_netcdf(output)
print("Save :",output)
