###ここでは実験ごとに渦度方程式の右辺各項(Adv.theta_g, Adv.f, Stretching)を求めてnetCDFファイルに保存する
from scipy.ndimage import gaussian_filter
from datetime import datetime,timedelta
import math
from netCDF4 import Dataset
from wrf import getvar,interplevel
import numpy as np
import xarray as xr


def gfilter(var,gs):
  var_smooth=xr.DataArray(
    gaussian_filter(var,sigma=(gs,gs)),
    coords=var.coords,
    dims=var.dims
  )
  return(var_smooth)

##実験設定
case="2025DJF"
ex="CTL_lamb"
#ex="ME00_lamb"

map_proj="lambert"
#"lambert" or "mercator" 
ref_lat=42.5
#メルカトルであれば使用する

lev=850
gsigma=0
#ガウシアンフィルタで用いる標準偏差(0でナシ)

start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
dsec=dh*3600
print(f"Set Time : {start_date}----{end_date} dh={dh}")

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output"
output_dir=f"/home/akioz/calculate/wrf/{case}/Voleq"

##定数
a=6370*10**3
g=9.81
omega=7.292*10**-5
#Holton,p12参照
ref_lat=42.5

dx=25*(10**3)
dy=25*(10**3)

print("a =",a)
print("g =",g)
print("Ω =",omega)
print("ref_lat =",ref_lat)
print("dx=dy=",dx)

list=[]
listx=[]
listy=[]
listf=[]
lists=[]

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
  
  if date == start_date :
    lat=getvar(ds,"lat")
    f=2*omega*np.sin(np.radians(lat*np.pi/180))
  #  f=gfilter(f,gsigma)
 
  p=getvar(ds,"p",units="hpa")

  ua=getvar(ds,"ua",units="ms-1")
  va=getvar(ds,"va",units="ms-1")

  u=interplevel(ua,p,lev)
  v=interplevel(va,p,lev)


#計算前に各変数へガウシアンフィルタをかける
  u=gfilter(u,gsigma)
  v=gfilter(v,gsigma)

#  print(z)

  ds.close()

##計算
  if map_proj == "lambert":
##変数へユークリッド距離に応じた座標を付与
    u = u.assign_coords({
      "west_east": np.arange(u.west_east.size) * dx,
      "south_north": np.arange(u.south_north.size) * dy
    })

    v = v.assign_coords({
      "west_east": np.arange(v.west_east.size) * dx,
      "south_north": np.arange(v.south_north.size) * dy
    })

    f = f.assign_coords({
      "west_east": np.arange(v.west_east.size) * dx,
      "south_north": np.arange(v.south_north.size) * dy
    })
    
#微分計算    
    dudx=u.differentiate("west_east")
    dudy=u.differentiate("south_north")
    dvdx=v.differentiate("west_east")
    dvdy=v.differentiate("south_north")

#渦度
    theta=dvdx - dudy
    
#相対渦度移流
    adv_thx=-u*theta.differentiate("west_east")
    adv_thy=-v*theta.differentiate("south_north")
    
#惑星渦度移流
    adv_f=-v*f.differentiate("south_north")

#ストレッチング項
    str=-(theta + f)*(dudx + dvdy)


  if map_proj == "mercator":
    rate_cos=np.cos(ref_lat*np.pi/180)/np.cos(lat*np.pi/180)
 ##メルカトルは未完成です  

  list.append(theta)
  listx.append(adv_thx)
  listy.append(adv_thy)
  listf.append(adv_f)
  lists.append(str)

  date+=timedelta(hours=dh)

da=xr.concat(list,dim="time")
dax=xr.concat(listx,dim="time")
day=xr.concat(listy,dim="time")
daf=xr.concat(listf,dim="time")
das=xr.concat(lists,dim="time")

#ここでオイラー微分項を計算
da_dt=da.differentiate("time") / dsec

da=da.rename("theta")
da_dt=da_dt.rename("dtheta_dt")
dax=dax.rename("Adv.theta_x")
day=day.rename("Adv.theta_y")
daf=day.rename("Adv.f")
das=das.rename("Stretching")

ds_out=xr.merge([da,da_dt,dax,day,daf,das])
print(ds_out)

#ランベルト図法はこれを表す変数がnetCDF形式に対応しないので削除
ds_out.attrs.pop("projection", None)
for var in ds_out.data_vars:
    ds_out[var].attrs.pop("projection", None)


output=f"{output_dir}/{ex}{lev}hpa_Voleq_dxdy{int(dy/1000)}_sigma{gsigma}.nc"

ds_out.to_netcdf(output)
print("Save :",output)