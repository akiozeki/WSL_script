###移動平均した変数(基本場)と偏差(擾乱)の成分に分けて保存する

from datetime import datetime,timedelta
from netCDF4 import Dataset
import math
from wrf import getvar,interplevel,ALL_TIMES
import numpy as np
import xarray as xr
from metpy.units import units
#######################

#アンサンブルメンバー数,実験ごとにメンバー数が違う場合には対応できていない
n_ensemble=1

##変数##
var_name="omega"
unit="Pa s-1"
#wrf-pythonの変数名と一致させる
lev=850

#ファイルパスと時間###
case="2025DJF"
wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
output_dir=f"/home/akioz/calculate/wrf/{case}/MMean"

#ex="CTL_lamb"
ex="ME00_lamb"

start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
print(f"Set Time : {start_date}----{end_date} dh={dh}")
#設定した期間の前後3.5日分のデータが必要

##移動平均の設定##
moving_day=7
step_per_day=4
step_all=moving_day*step_per_day
half_step=step_all/2
#######################

saving_list=[]
saving_list_m=[]
saving_list_a=[]
time_list=[]

date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day
  h=date.hour
  time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}:00:00"
  print("time:",time_str)

  m_list=[]
  m_list_m=[]
  m_list_a=[]
  
  for e_member in range(n_ensemble):
    moving_list=[]
#移動平均のためのリスト 

    move_date=date - timedelta(hours=6*half_step)
    if n_ensemble >= 2 :
      print(f"n={e_member+1}")

    print(f"Caluculate_{moving_day}days_Moving_Mean")
    print("from",move_date)

##移動平均を取る範囲のデータをまとめる
    for t in range(step_all):
      my=move_date.year
      mm=move_date.month
      md=move_date.day
      mh=move_date.hour
      moving_time_str=f"{my}-{mm:02d}-{md:02d}_{mh:02d}:00:00"
  
      if n_ensemble >= 2:
        moving_file=Dataset(f"{wrfout_dir}/{ex}/n{e_member+1}/wrfout_d01_{moving_time_str}")
        moving_list.append(moving_file)

      else: 
        moving_file=Dataset(f"{wrfout_dir}/{ex}/wrfout_d01_{moving_time_str}")
        moving_list.append(moving_file)

      move_date+=timedelta(hours=dh)
#ココで移動平均内での時間更新      
    print("to",move_date)
    
  
##変数取り出し
    p=getvar(moving_list,"p",timeidx=ALL_TIMES,method="join",units="hpa")
  
#    var_all=getvar(moving_list,var_name,timeidx=ALL_TIMES,method="join",units=unit)
    var_all=getvar(moving_list,var_name,timeidx=ALL_TIMES,method="join")

#**ココで単位付与も必ずする    
    var=interplevel(var_all,p,lev)

##ファイルclose
    for ds in moving_list:
      ds.close()
  
##計算
#各変数の移動平均(ここで次元圧縮:file*ny*nx -> 1*ny*nx)
    var_mmean=var.mean(dim="file",skipna=True)
    print(f"space_mean({ex}) = ",np.nanmean(var_mmean))
#アンサブル方向に延ばす(member*ny*nx)

##ココで再度対象時刻のwrfoutを開く   
    if n_ensemble >= 2:
      curent_file=Dataset(f"{wrfout_dir}/{ex}/n{e_member+1}/wrfout_d01_{time_str}")

    else: 
      current_file=Dataset(f"{wrfout_dir}/{ex}/wrfout_d01_{time_str}")


#変数取り出し
    cp=getvar(current_file,"p",units="hpa")
  
#    cvar_all=getvar(current_file,var_name,units=unit)
    cvar_all=getvar(current_file,var_name)
#**ココで単位付与も必ずする    
    cvar=interplevel(cvar_all,cp,lev)
    var_a=cvar - var_mmean
#    print(var_a)

    m_list.append(cvar)
    m_list_m.append(var_mmean)
    m_list_a.append(var_a)

    current_file.close()
###ココで1つのアンサンブルメンバにおける移動平均した計算は終了
    print(f"Calculate_{moving_day}dMean : N = {e_member+1}")

###ココでアンサンブル方向のforループ終了

#通常のリストではnetCDF化出来ないためDataArray化する
  if n_ensemble == 1:
    saving_list.append(cvar)
    saving_list_m.append(var_mmean)
    saving_list_a.append(var_a)

  else:
    var_darray=xr.concat(m_list,dim="member")
    var_darray_m=xr.concat(m_list_m,dim="member")
    var_darray_a=xr.concat(m_list_a,dim="member")

    var_darray=var_darray.assign_coords(member=("member",np.arange(1,n_ensemble+1,1)))
    var_darray_m=var_darray_m.assign_coords(member=("member",np.arange(1,n_ensemble+1,1)))
    var_darray_a=var_darray_a.assign_coords(member=("member",np.arange(1,n_ensemble+1,1)))
    saving_list.append(var_darray)
    saving_list_m.append(var_darray_m)
    saving_list_a.append(var_darray_a)


  
  time_list.append(time_str)
  print("Change_Time_Step\n")
  date+=timedelta(hours=dh)  
###時間更新

#この段階ではdarrayに投影系の情報が含まれており，これはnetCDF形式に対応しないので削除する
saving_darray=xr.concat(saving_list,dim="time")
saving_darray.attrs.pop("projection",None)
#saving_darray=saving_darray.assign_coords(time=("time",time_list))
saving_darray_m=xr.concat(saving_list_m,dim="time")
saving_darray_m.attrs.pop("projection",None)
#saving_darray_m=saving_darray_m.assign_coords(time=("time",time_list))
saving_darray_a=xr.concat(saving_list_a,dim="time")
saving_darray_a.attrs.pop("projection",None)
#saving_darray_d=saving_darray_d.assign_coords(time=("time",time_list))
#この配列は(time,(member),ny,nx),これを保存する


##netCDFへ保存
saving_darray.name=var_name
saving_darray_m.name=f"{var_name}_m"
saving_darray_a.name=f"{var_name}_a"
saving_ds=xr.merge([saving_darray,saving_darray_m,saving_darray_a])

print(saving_ds)
# Dataset attrs
#print("Dataset attrs:", saving_ds.attrs)

# DataVars attrs / encoding
#for v in saving_ds.data_vars:
#    if "projection" in saving_ds[v].attrs:
#        print("var attrs:", v)
#    if "projection" in saving_ds[v].encoding:
#        print("var encoding:", v)
#
## Coords attrs / encoding
#for c in saving_ds.coords:
#    if "projection" in saving_ds[c].attrs:
#        print("coord attrs:", c)
#    if "projection" in saving_ds[c].encoding:
#        print("coord encoding:", c)
##saving_ds.attrs.pop("projection", None)

saving_name=f"{output_dir}/{ex}_{var_name}{lev}_{moving_day}dMean.nc"
saving_ds.to_netcdf(saving_name)
print(f"Create {saving_name}")

print("End Program")
