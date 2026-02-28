from datetime import datetime,timedelta
from netCDF4 import Dataset
import math
from wrf import getvar,interplevel,ALL_TIMES
import numpy as np
import xarray as xr
from metpy.units import units
#######################

#アンサンブルメンバー数,実験ごとにメンバー数が違う場合には対応できていない
n_ensemble=10

##変数##
var="tk"
#wrf-pythonの変数名と一致させる
lev=900

#ファイルパスと時間###
case="200912low_ensemble"
wrf_dir="/DATA/USER/ozeki/MyWRF"
wrfout_dir=f"{wrf_dir}/output_data/{case}"
data_dir=f"{wrf_dir}/output_data/{case}"

start_date=datetime(2009,12,25,12)
end_date=datetime(2009,12,28,12)
print(f"Set Time : {start_date}----{end_date}")


##移動平均の設定##
moving_day=7
step_per_day=4
step_all=moving_day*step_per_day
half_step=step_all/2
#######################

ctl_save_list=[]
me_save_list=[]

date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day
  h=date.hour
  time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}:00:00"
  print("time:",time_str)

  ctl_ens_list=[]
  me_ens_list=[]
  
  for member in range(n_ensemble):
    ctl_moving_list=[]
    me_moving_list=[]
#移動平均のためのリスト 

    move_date=date - timedelta(hours=6*half_step)
    print(f"n={member+1}")
    print(f"Caluculate_{moving_day}days_Moving_Mean")
    print("from",move_date)

##移動平均を取る範囲のデータをまとめる
    for t in range(step_all):
      my=move_date.year
      mm=move_date.month
      md=move_date.day
      mh=move_date.hour
      moving_time_str=f"{my}-{mm:02d}-{md:02d}_{mh:02d}:00:00"
  
      ctl_moving_file=Dataset(f"{wrfout_dir}/ctl/n{member+1}/wrfout_d01_{moving_time_str}")
      ctl_moving_list.append(ctl_moving_file)
      me_moving_file=Dataset(f"{wrfout_dir}/me/n{member+1}/wrfout_d01_{moving_time_str}")
      me_moving_list.append(me_moving_file)
  
      move_date+=timedelta(hours=6)
#ココで移動平均内での時間更新      
    print("to",move_date)
    
  
##変数取り出し
#CTL
    ctl_p=getvar(ctl_moving_list,"p",timeidx=ALL_TIMES,method="join",units="hpa")
  
    ctl_vara=getvar(ctl_moving_list,f"{var}",timeidx=ALL_TIMES,method="join")
    ctl_var=interplevel(ctl_vara,ctl_p,lev)
    ctl_var=ctl_var*units.kelvin
#ME
    me_p=getvar(me_moving_list,"p",timeidx=ALL_TIMES,method="join",units="hpa")
  
    me_vara=getvar(me_moving_list,f"{var}",timeidx=ALL_TIMES,method="join")
    me_var=interplevel(me_vara,me_p,lev)
    me_var=me_var*units.kelvin

##ファイルclose
    for ctl_ds in ctl_moving_list:
      ctl_ds.close()
  
    for me_ds in me_moving_list:
      me_ds.close()
  
##計算
    ctl_var_mmean=ctl_var.mean(dim="file",skipna=True)
#各変数の移動平均(ここで次元圧縮:file*ny*nx -> 1*ny*nx)

    print(f"space_mean(CTL) = ",np.nanmean(ctl_var_mmean))
    ctl_ens_list.append(ctl_var_mmean)
#アンサブル方向に延ばす(member*ny*nx)

    me_var_mmean=me_var.mean(dim="file",skipna=True)

    print(f"space_mean(ME) = ",np.nanmean(ctl_var_mmean))
    me_ens_list.append(me_var_mmean)


#通常のリストではnetCDF化出来ないためDataArray化する

  ctl_ens_darray=xr.concat(ctl_ens_list,dim="member")
  ctl_save_list.append(ctl_ens_darray)
  me_ens_darray=xr.concat(me_ens_list,dim="member")
  me_save_list.append(me_ens_darray)


  print("Change_Time_Step\n")
  date+=timedelta(hours=6)  
#時間更新

ctl_save_darray=xr.concat(ctl_save_list,dim="time")
me_save_darray=xr.concat(me_save_list,dim="time")
#この配列は(time,member,ny,nx),これを保存する


##netCDFへ保存

#CTL
file_ctl=f"{data_dir}/ctl/ensemble/CTL_{moving_day}d_mean_{var}{lev}.nc"
  
ctl_save_darray.name=f"{var}{lev}"

ctl_save_darray.to_netcdf(file_ctl)

#ME
file_me=f"{data_dir}/me/ensemble/ME_{moving_day}d_mean_{var}{lev}.nc"

me_save_darray.name=f"{var}{lev}"

me_save_darray.to_netcdf(file_me)
  
print("Save_File>")
print(file_ctl)
print(file_me)

print("End Program")

