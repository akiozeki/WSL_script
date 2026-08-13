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
#ex="ME00_lamb"
ex="CTL_lamb"

map_proj="lambert"
#"lambert" or "mercator" 
ref_lat=42.5
#メルカトルであれば使用する

dx=25*(10**3)
dy=25*(10**3)
print(f"(dx,dy) = ({dx},{dy})")

#気圧面(hPa)
lev=800
top_lev=lev-50
bottom_lev=lev+50

gsigma=3

start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
dsec=dh*3600
print(f"Set Time : {start_date}----{end_date} dh={dh}")

wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output"
output_dir=f"/home/akioz/calculate/wrf/{case}/TDeq"

##定数
a=6370*10**3
#地球半径

list=[]
listx=[]
listy=[]
listp=[]

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
# print(ds)
  
  lat=getvar(ds,"lat")
  lon=getvar(ds,"lon")
  p=getvar(ds,"p",units="hpa")

  Ta=getvar(ds,"temp",units="K")
  thetaa=getvar(ds,"theta",units="K")
  ua=getvar(ds,"ua",units="ms-1")
  va=getvar(ds,"va",units="ms-1")
  omegaa=getvar(ds,"omega")

  T=interplevel(Ta,p,lev)
  theta=interplevel(thetaa,p,lev)
  theta_top=interplevel(thetaa,p,top_lev)
  theta_bottom=interplevel(thetaa,p,bottom_lev)
  u=interplevel(ua,p,lev)
  v=interplevel(va,p,lev)
  omega=interplevel(omegaa,p,lev)
  
  T=gfilter(T,gsigma)
  u=gfilter(u,gsigma)
  v=gfilter(v,gsigma)
  omega=gfilter(omega,gsigma)


  ds.close()

##計算
  if map_proj == "lambert":
##温度の変数へユークリッド距離に応じた座標を付与
    T = T.assign_coords({
      "west_east": np.arange(T.west_east.size) * dx,
      "south_north": np.arange(T.south_north.size) * dy
    })

    adv_Tx=-u*T.differentiate("west_east")
    adv_Ty=-v*T.differentiate("south_north")

    Sp=-(T / theta)*((theta_top - theta_bottom) / (top_lev*100 - bottom_lev*100))
    adv_Tp=Sp*omega

  elif map_proj == "mercator":

    rate_cos=np.cos(ref_lat*np.pi / 180) / np.cos(lat*np.pi / 180)
# # print(rate_cos)
#   #メルカトル図法のWRFはdxが一定でなくref_latで設定した緯度のみ設定した値,残りは等緯度となるように出力されるので緯度による重みづけが必要  

    adv_Tx=-u * T.differentiate("lon") * rate_cos
    adv_Ty=-v * T.differentiate("lat") * (1 / a)

    Sp=-(T/theta)*((theta_top - theta_bottom) / (top_lev*100 - bottom_lev*100))
    adv_Tp=Sp*omega

  #print(adv_Tx)
  #print(adv_Ty)
  #print(adv_Tp)
  
  list.append(T)
  listx.append(adv_Tx)
  listy.append(adv_Ty)
  listp.append(adv_Tp)

  date+=timedelta(hours=dh)


da=xr.concat(list,dim="time")
#mean=da.mean(dim="time",skipna=True)

#ここでオイラー微分項
dT_dt=da.differentiate("time") / dsec
#print(dT_dt)
#meant=dT_dt.mean(dim="time",skipna=True) / (dsec * len(dT_dt["time"]))
#print(meant)

dax=xr.concat(listx,dim="time")
#meanx=dax.mean(dim="time",skipna=True)

day=xr.concat(listy,dim="time")
#meany=day.mean(dim="time",skipna=True)

dap=xr.concat(listp,dim="time")
#meanp=dap.mean(dim="time",skipna=True)


da=da.rename("T")
print(da.values)
dT_dt=dT_dt.rename("dT_dt")
dax=dax.rename("Adv.Tx")
day=day.rename("Adv.Ty")
dap=dap.rename("Adv.Tp")

ds_out=xr.merge([da,dT_dt,dax,day,dap])
print(ds_out)

output=f"{output_dir}/{ex}{lev}hpa_TDeq_dxdy{int(dy/1000)}_sigma{gsigma}.nc"


# print(type(ds_out.attrs["projection"]))
# ds_out.attrs.pop("projection", None)
# for var in ds_out.data_vars:
#     ds_out[var].attrs.pop("projection", None)


ds_out.to_netcdf(output)
print("Save :",output)