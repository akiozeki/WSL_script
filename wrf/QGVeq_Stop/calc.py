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
#ex="CTL_lamb"
ex="ME00_lamb"

map_proj="lambert"
#"lambert" or "mercator" 
ref_lat=42.5
#メルカトルであれば使用する

lev=800
gsigma=0
#ガウシアンフィルタで用いる標準偏差(0でナシ)

start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
dsec=dh*3600
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

dx=25*(10**3)
dy=25*(10**3)

print("a =",a)
print("g =",g)
print("Ω =",omega)
print("ref_lat =",ref_lat)
print("f0 =",f0)
print("dx=dy=",dx)

listz=[]
listug=[]
listvg=[]
listua=[]
listva=[]
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
  
  lat=getvar(ds,"lat")
  p=getvar(ds,"p",units="hpa")

  ua=getvar(ds,"ua",units="ms-1")
  va=getvar(ds,"va",units="ms-1")
  za=getvar(ds,"z",units="m")

  u=interplevel(ua,p,lev)
  v=interplevel(va,p,lev)
  z=interplevel(za,p,lev)


#計算前に各変数へガウシアンフィルタをかける
  z=gfilter(z,gsigma)
  u=gfilter(u,gsigma)
  v=gfilter(v,gsigma)

#  print(z)

  ds.close()

##計算
  if map_proj == "lambert":
##Zの変数へユークリッド距離に応じた座標を付与
    z = z.assign_coords({
      "west_east": np.arange(z.west_east.size) * dx,
      "south_north": np.arange(z.south_north.size) * dy
    })

#微分計算    
    dzdx=z.differentiate("west_east")
    dzdy=z.differentiate("south_north")
    dz2dx2=dzdx.differentiate("west_east")
    dz2dy2=dzdy.differentiate("south_north")
    dz3dx3=dz2dx2.differentiate("west_east")
    dz3dy3=dz2dy2.differentiate("south_north")
    dz3dxdy2=dz2dy2.differentiate("west_east")
    dz3dx2dy=dz2dx2.differentiate("south_north")

#地衡風と渦度
    f0=omega*np.cos(ref_lat*np.pi/180)
    ug=-(g/f0)*dzdy
    vg=(g/f0)*dzdx
    thg=(g/f0)*(dz2dx2 + dz2dy2)

#非地衡風成分
    ua=u - ug
    va=v - vg
    duadx=ua.differentiate("west_east")
    dvady=va.differentiate("south_north")

#相対渦度移流
    adv_thgx= -(g**2/f0**2)*(-dzdy*(dz3dx3 + dz3dxdy2))
    adv_thgy= - (g**2/f0**2)*(dzdx*(dz3dx2dy + dz3dy3))
    

#惑星渦度移流
    beta=2*omega*np.cos(ref_lat*np.pi/180)/a
    adv_f=-beta*vg

#ストレッチング項
    strt=-f0*(duadx + dvady)


  if map_proj == "mercator":
    rate_cos=np.cos(ref_lat*np.pi/180)/np.cos(lat*np.pi/180)
 ##メルカトルは未完成   

  listz.append(z)  
  listug.append(ug)
  listvg.append(vg)
  listua.append(ua)
  listva.append(va)
  list.append(thg)
  listx.append(adv_thgx)
  listy.append(adv_thgy)
  listf.append(adv_f)
  lists.append(strt)

  date+=timedelta(hours=dh)

daz=xr.concat(listz,dim="time")
daug=xr.concat(listug,dim="time")
davg=xr.concat(listvg,dim="time")
daua=xr.concat(listua,dim="time")
dava=xr.concat(listva,dim="time")
da=xr.concat(list,dim="time")
dax=xr.concat(listx,dim="time")
day=xr.concat(listy,dim="time")
daf=xr.concat(listf,dim="time")
das=xr.concat(lists,dim="time")

#ここでオイラー微分項を計算
da_dt=da.differentiate("time") / dsec

daz=daz.rename("Z")
daug=daug.rename("Ug")
davg=davg.rename("Vg")
daua=daua.rename("Ua")
dava=dava.rename("Va")
da=da.rename("thg")
da_dt=da_dt.rename("dthg_dt")
dax=dax.rename("Adv.thgx")
day=day.rename("Adv.thgy")
daf=day.rename("Adv.f")
das=das.rename("Stretching")

ds_out=xr.merge([daz,daug,davg,daua,dava,da,da_dt,dax,day,daf,das])
print(ds_out)

#ランベルト図法はこれを表す変数がnetCDF形式に対応しないので削除
ds_out.attrs.pop("projection", None)
for var in ds_out.data_vars:
    ds_out[var].attrs.pop("projection", None)


output=f"{output_dir}/{ex}{lev}hpa_QGVeq_dxdy{int(dy/1000)}_sigma{gsigma}.nc"

ds_out.to_netcdf(output)
print("Save :",output)