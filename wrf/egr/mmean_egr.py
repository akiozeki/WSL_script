from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,latlon_coords,interplevel,ALL_TIMES
import metpy.calc as mpcalc
from metpy.units import units
import numpy as np
import xarray as xr


#######################
var="EGR"
#EGR or N or Ushear

#ファイルパスと時間###
case="2025DJF"
ex1="CTL_lamb"
ex2="ME00_lamb"
wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}"
output_dir=f"/home/akioz/calculate/wrf/{case}/EGR"
start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
dh=6
print(f"Set Time : {start_date}----{end_date} dh={dh}")

#アンサンブルメンバー数,メンバー数が違う場合には対応できていない*1にするとアンサンブルナシ
n_ensemble=1

##移動平均の設定##
moving_day=7
step_per_day=4
step_all=moving_day*step_per_day
half_step=step_all / 2


p=850
p_t=800
p_w=900
#######################


saving_list1=[]
saving_list2=[]
time_list=[]

date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day
  h=date.hour
  time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}:00:00"
  print("time:",time_str)

  m_list1=[]
  m_list2=[]
#アンサンブル軸のためのリスト

  for member in range(n_ensemble):
    moving_list1=[]
    moving_list2=[]
#移動平均のためのリスト 

    move_date=date - timedelta(hours=6*half_step)
    if n_ensemble >= 2 :
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
  
      if n_ensemble >= 2:
        moving_file1=Dataset(f"{wrfout_dir}/{ex1}/n{member+1}/wrfout_d01_{moving_time_str}")
        moving_list1.append(moving_file1)
        moving_file2=Dataset(f"{wrfout_dir}/{ex2}/n{member+1}/wrfout_d01_{moving_time_str}")
        moving_list2.append(moving_file2)

      else: 
        moving_file1=Dataset(f"{wrfout_dir}/{ex1}/wrfout_d01_{moving_time_str}")
        moving_list1.append(moving_file1)
        moving_file2=Dataset(f"{wrfout_dir}/{ex2}/wrfout_d01_{moving_time_str}")
        moving_list2.append(moving_file2)

      move_date+=timedelta(hours=dh)
#ココで移動平均内での時間更新      
    print("to",move_date)
    
  
###変数取り出し
    lat1=getvar(moving_list1,"lat",timeidx=ALL_TIMES,method="join")
    p1=getvar(moving_list1,"p",timeidx=ALL_TIMES,method="join",units="hpa")
    theta1=getvar(moving_list1,"theta",timeidx=ALL_TIMES,method="join",units="K")
    theta1_t=interplevel(theta1,p1,p_t)
    theta1_m=interplevel(theta1,p1,p) 
    theta1_w=interplevel(theta1,p1,p_w)
  
    u1=getvar(moving_list1,"ua",timeidx=ALL_TIMES,method="join")
    u1_t=interplevel(u1,p1,p_t)
    u1_w=interplevel(u1,p1,p_w)
  
    z1=getvar(moving_list1,"z",timeidx=ALL_TIMES,method="join",units="m")
    z1_t=interplevel(z1,p1,p_t)
    z1_w=interplevel(z1,p1,p_w)

    lat2=getvar(moving_list2,"lat",timeidx=ALL_TIMES,method="join")
    p2=getvar(moving_list2,"p",timeidx=ALL_TIMES,method="join",units="hpa")
    theta2=getvar(moving_list2,"theta",timeidx=ALL_TIMES,method="join",units="K")
    theta2_t=interplevel(theta2,p2,p_t)
    theta2_m=interplevel(theta2,p2,p) 
    theta2_w=interplevel(theta2,p2,p_w)
  
    u2=getvar(moving_list2,"ua",timeidx=ALL_TIMES,method="join")
    u2_t=interplevel(u2,p2,p_t)
    u2_w=interplevel(u2,p2,p_w)
  
    z2=getvar(moving_list2,"z",timeidx=ALL_TIMES,method="join",units="m")
    z2_t=interplevel(z2,p2,p_t)
    z2_w=interplevel(z2,p2,p_w)
  
##ファイルclose
    for ds1 in moving_list1:
      ds1.close()
  
    for ds2 in moving_list2:
      ds2.close()
  
###計算
##各変数の移動平均(ここで次元圧縮:file*ny*nx -> 1*ny*nx)
    theta1_t_mmean=theta1_t.mean(dim="file",skipna=True)
    theta1_m_mmean=theta1_m.mean(dim="file",skipna=True)
    theta1_w_mmean=theta1_w.mean(dim="file",skipna=True)
  
    u1_t_mmean=u1_t.mean(dim="file",skipna=True)
    u1_w_mmean=u1_w.mean(dim="file",skipna=True)
  
    z1_t_mmean=z1_t.mean(dim="file",skipna=True)
    z1_w_mmean=z1_w.mean(dim="file",skipna=True)

    theta2_t_mmean=theta2_t.mean(dim="file",skipna=True)
    theta2_m_mmean=theta2_m.mean(dim="file",skipna=True)
    theta2_w_mmean=theta2_w.mean(dim="file",skipna=True)
  
    u2_t_mmean=u2_t.mean(dim="file",skipna=True)
    u2_w_mmean=u2_w.mean(dim="file",skipna=True)
  
    z2_t_mmean=z2_t.mean(dim="file",skipna=True)
    z2_w_mmean=z2_w.mean(dim="file",skipna=True)
  
  
    g=9.81

    f1=mpcalc.coriolis_parameter(lat1[0,:,:])
    f2=mpcalc.coriolis_parameter(lat2[0,:,:])
#コリオリパラメータの配列はファイル方向にも存在するため,要素数合わせるためにスライス必要

    dz1=z1_t_mmean - z1_w_mmean
    dz2=z2_t_mmean - z2_w_mmean
  
#安定度
    dtheta1=theta1_t_mmean - theta1_w_mmean    
    N1=np.sqrt((g/theta1_m_mmean)*(dtheta1/dz1))

    dtheta2=theta2_t_mmean - theta2_w_mmean    
    N2=np.sqrt((g/theta2_m_mmean)*(dtheta2/dz2))

#鉛直シア
    du1=u1_t_mmean - u1_w_mmean  
    gushear1=np.abs(du1/dz1)

    du2=u2_t_mmean - u2_w_mmean  
    gushear2=np.abs(du2/dz2)
  
  
#eady_growth_rate
    egr1=0.31*f1*(1/N1)*gushear1
    egr2=0.31*f2*(1/N2)*gushear2


    if var == "EGR" :
      print("EGR1 Space Mean = ",np.nanmean(egr1.values))
      print("EGR2 Space Mean = ",np.nanmean(egr2.values))
      m_list1.append(egr1)
      m_list2.append(egr2)

    elif var == "N" :
      m_list1.append(N1)
      m_list2.append(N2)
      print("N1 Space Mean = ",np.nanmean(N1.values))
      print("N2 Space Mean = ",np.nanmean(N2.values))
 
    elif var == "Ushear" :
      m_list1.append(gushear1)
      m_list2.append(gushear2)
      print("Ushear1 Space Mean = ",np.nanmean(gushear1.values))
      print("Ushear2 Space Mean = ",np.nanmean(gushear2.values))
 
    else:
      print("Var Not Found")
  
  m_darray1=xr.concat(m_list1,dim="member")
  m_darray1=m_darray1.assign_coords(member=("member",np.arange(1,n_ensemble+1,1)))
  saving_list1.append(m_darray1)

  m_darray2=xr.concat(m_list2,dim="member")
  m_darray2=m_darray2.assign_coords(member=("member",np.arange(1,n_ensemble+1,1)))
  saving_list2.append(m_darray2)
#アンサンブルアリだと(member,ny,nx),ナシだと(1,ny,ny)の配列となる  


  time_list.append(date)
  date+=timedelta(hours=dh)  

  print("Change_Time_Step\n")
#ココで時間更新

saving_darray1=xr.concat(saving_list1,dim="time")
saving_darray1=saving_darray1.assign_coords(time=("time",time_list))

saving_darray2=xr.concat(saving_list2,dim="time")
saving_darray2=saving_darray2.assign_coords(time=("time",time_list))
#(time,member,ny,nx)または(time,1,ny,nx)の配列

saving_darray1.name=var
saving_name1=f"{output_dir}/{ex1}_{var}{p}_{moving_day}dMean.nc"
saving_darray1.to_netcdf(saving_name1)
print(f"Create {saving_name1}")

saving_darray2.name=var
saving_name2=f"{output_dir}/{ex2}_{var}{p}_{moving_day}dMean.nc"
saving_darray2.to_netcdf(saving_name2)
print(f"Create {saving_name2}")

print("End Program")
