from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel,ALL_TIMES
import metpy.calc as mpcalc
from metpy.units import units
import numpy as np
import xarray as xr
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

#######################
#ファイルパスと時間###
case="200912low_ensemble"
wrf_dir="/DATA/USER/ozeki/MyWRF"
wrfout_dir=f"{wrf_dir}/output_data/{case}"
data_dir=f"{wrf_dir}/output_data/{case}"

start_date=datetime(2009,12,25,12)
end_date=datetime(2009,12,28,12)
print(f"Set Time : {start_date}----{end_date}")

#アンサンブルメンバー数,メンバー数が違う場合には対応できていない*1にするとアンサンブルナシ
n_ensemble=10

##移動平均の設定##
moving_day=7
step_per_day=4
step_all=moving_day*step_per_day
half_step=step_all/2
#######################


date=start_date
while date <= end_date:
  y=date.year

  m=date.month
  d=date.day
  h=date.hour
  time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}:00:00"
  print("time:",time_str)


  ctl_N_list=[]
  ctl_ushear_list=[]
  ctl_egr_list=[]
  me_N_list=[]
  me_ushear_list=[]
  me_egr_list=[]
#データ保存のためのリスト

  for member in range(n_ensemble):
    ctl_moving_list=[]
    me_moving_list=[]
#移動平均のためのリスト 

    move_date=date - timedelta(hours=6*half_step)
    print(f"n={member+1}")
    print(f"Caluculate_{moving_day}days_Moving_Average")
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
    ctl_lat=getvar(ctl_moving_list,"lat",timeidx=ALL_TIMES,method="join")
    ctl_p=getvar(ctl_moving_list,"p",timeidx=ALL_TIMES,method="join",units="hpa")
    ctl_theta=getvar(ctl_moving_list,"theta",timeidx=ALL_TIMES,method="join",units="K")
    ctl_theta900=interplevel(ctl_theta,ctl_p,900)
    ctl_theta850=interplevel(ctl_theta,ctl_p,850)
    ctl_theta800=interplevel(ctl_theta,ctl_p,800)
  
    ctl_u=getvar(ctl_moving_list,"ua",timeidx=ALL_TIMES,method="join")
    ctl_u900=interplevel(ctl_u,ctl_p,900)
    ctl_u800=interplevel(ctl_u,ctl_p,800)
  
    ctl_z=getvar(ctl_moving_list,"z",timeidx=ALL_TIMES,method="join",units="m")
    ctl_z900=interplevel(ctl_z,ctl_p,900)
    ctl_z800=interplevel(ctl_z,ctl_p,800)
  
#ME
    me_lat=getvar(me_moving_list,"lat",timeidx=ALL_TIMES,method="join")
    me_p=getvar(me_moving_list,"p",timeidx=ALL_TIMES,method="join",units="hpa")
    me_theta=getvar(me_moving_list,"theta",timeidx=ALL_TIMES,method="join",units="K")
    me_theta900=interplevel(me_theta,me_p,900)
    me_theta850=interplevel(me_theta,me_p,850)
    me_theta800=interplevel(me_theta,me_p,800)
  
    me_u=getvar(me_moving_list,"ua",timeidx=ALL_TIMES,method="join")
    me_u900=interplevel(me_u,me_p,900)
    me_u800=interplevel(me_u,me_p,800)
  
    me_z=getvar(me_moving_list,"z",timeidx=ALL_TIMES,method="join",units="m")
    me_z900=interplevel(me_z,me_p,900)
    me_z800=interplevel(me_z,me_p,800)
  
##ファイルclose
    for ctl_ds in ctl_moving_list:
      ctl_ds.close()
  
    for me_ds in me_moving_list:
      me_ds.close()
  
##計算
#各変数の移動平均(ここで次元圧縮:file*ny*nx -> 1*ny*nx)
    ctl_theta900_mmean=ctl_theta900.mean(dim="file",skipna=True)
    ctl_theta850_mmean=ctl_theta850.mean(dim="file",skipna=True)
    ctl_theta800_mmean=ctl_theta800.mean(dim="file",skipna=True)
  
    ctl_u900_mmean=ctl_u900.mean(dim="file",skipna=True)
    ctl_u800_mmean=ctl_u800.mean(dim="file",skipna=True)
  
    ctl_z900_mmean=ctl_z900.mean(dim="file",skipna=True)
    ctl_z800_mmean=ctl_z800.mean(dim="file",skipna=True)
  
    me_theta900_mmean=me_theta900.mean(dim="file",skipna=True)
    me_theta850_mmean=me_theta850.mean(dim="file",skipna=True)
    me_theta800_mmean=me_theta800.mean(dim="file",skipna=True)
  
    me_u900_mmean=me_u900.mean(dim="file",skipna=True)
    me_u800_mmean=me_u800.mean(dim="file",skipna=True)
  
    me_z900_mmean=me_z900.mean(dim="file",skipna=True)
    me_z800_mmean=me_z800.mean(dim="file",skipna=True)
  
  
#EGR計算※ココではアノマリーは計算しない
    ctl_delta_z=ctl_z800_mmean - ctl_z900_mmean
    me_delta_z=me_z800_mmean- me_z900_mmean
  
#安定度
    ctl_delta_theta=ctl_theta800_mmean - ctl_theta900_mmean    
    ctl_N2=(9.81/ctl_theta850_mmean)*(ctl_delta_theta/ctl_delta_z)
    ctl_N=np.sqrt(ctl_N2)
#    ctl_N=ctl_N*units("/s")
  
    me_delta_theta=me_theta800_mmean - me_theta900_mmean
    me_N2=(9.81/me_theta850_mmean)*(me_delta_theta/me_delta_z)
    me_N=np.sqrt(me_N2)
#    me_N=me_N*units("/s")

#鉛直シア
    ctl_delta_u=ctl_u800_mmean - ctl_u900_mmean  
    ctl_ushear=ctl_delta_u/ctl_delta_z
#    ctl_ushear=ctl_ushear*units("m/s^2")
    ctl_ushear_ganma=np.abs(ctl_ushear)
  
    me_delta_u=me_u800_mmean - me_u900_mmean
    me_ushear=me_delta_u/me_delta_z
#    me_ushear=me_ushear*units("m/s^2")
    me_ushear_ganma=np.abs(me_ushear)
  
#eady_growth_rate
    ctl_f=mpcalc.coriolis_parameter(ctl_lat[0,:,:])
#コリオリパラメータの配列はファイル方向にも存在するため,要素数合わせるためにスライス必要
    ctl_egr=0.31*(ctl_f/ctl_N)*ctl_ushear_ganma
    print("space_mean = ",np.nanmean(ctl_egr.values))
 #値のチェック

    me_f=mpcalc.coriolis_parameter(me_lat[0,:,:])
    me_egr=0.31*(me_f/me_N)*me_ushear_ganma
  
    ctl_N_list.append(ctl_N)
    ctl_ushear_list.append(ctl_ushear_ganma)
    ctl_egr_list.append(ctl_egr)

    me_N_list.append(me_N)
    me_ushear_list.append(me_ushear_ganma)
    me_egr_list.append(me_egr)

##netCDFへ保存
#通常のリストではnetCDF化出来ないためDataArray化する
  ctl_N_darray=xr.concat(ctl_N_list,dim="member")
  ctl_ushear_darray=xr.concat(ctl_ushear_list,dim="member")
  ctl_egr_darray=xr.concat(ctl_egr_list,dim="member")

  me_N_darray=xr.concat(me_N_list,dim="member")
  me_ushear_darray=xr.concat(me_ushear_list,dim="member")
  me_egr_darray=xr.concat(me_egr_list,dim="member")

#CTL
  file_ctl_N=f"{data_dir}/ctl/ensemble/CTL_{moving_day}d_mean_N850_{time_str}.nc"
  file_ctl_ushear=f"{data_dir}/ctl/ensemble/CTL_{moving_day}d_mean_ushear850_{time_str}.nc"
  file_ctl_egr=f"{data_dir}/ctl/ensemble/CTL_{moving_day}d_mean_egr850_{time_str}.nc"
  
  ctl_N_darray.name="N850"
  ctl_ushear_darray.name="ushear850"
  ctl_egr_darray.name="egr850"

  ctl_N_darray.to_netcdf(file_ctl_N)
  ctl_ushear_darray.to_netcdf(file_ctl_ushear)
  ctl_egr_darray.to_netcdf(file_ctl_egr)

#ME
  file_me_N=f"{data_dir}/me/ensemble/ME_{moving_day}d_mean_N850_{time_str}.nc"
  file_me_ushear=f"{data_dir}/me/ensemble/ME_{moving_day}d_mean_ushear850_{time_str}.nc"
  file_me_egr=f"{data_dir}/me/ensemble/ME_{moving_day}d_mean_egr850_{time_str}.nc"
  me_N_darray.name="N850"
  me_ushear_darray.name="ushear850"
  me_egr_darray.name="egr850"

  me_N_darray.to_netcdf(file_me_N)
  me_ushear_darray.to_netcdf(file_me_ushear)
  me_egr_darray.to_netcdf(file_me_egr)
  
  print("Save_File>")
  print(file_ctl_egr)
  print(file_me_egr)
  print("etc...total-6")

  date+=timedelta(hours=6)  
  print("Change_Time_Step\n")
#ココで時間更新

print("End Program")


###Plot -> 別ファイル
#
###N
##CTL
#    fig=plt.figure()
#    ax=plt.axes(projection=cart_proj)
#    ax.set_extent([125,145,34,45])
#
#    shade=ax.contourf(
#      lons,lats,ctl_N,
#      levels=np.arange(0,0.035,0.005),
#      cmap="Reds",
#      transform=ccrs.PlateCarree()
#      )
#    
#    cbar=plt.colorbar(
#      shade,orientation="horizontal",
#      label="[/s]"
#      )
#
#    gl = ax.gridlines(draw_labels=True)
#    gl.xformatter = LONGITUDE_FORMATTER
#    gl.yformatter = LATITUDE_FORMATTER
#    gl.top_labels = False
#    gl.right_labels = False
#
#    ax.coastlines()
#    ax.add_feature(cfeature.LAND,color="gray")
#    ax.set_title(f"ctl-{time_str}UTC",fontsize=20)
#    
#    plt.savefig(f"{fig_dir}/ctl/n{member}/N_{time_str}.png")
#    plt.close("all")
#
##ME
#    fig=plt.figure()
#    ax=plt.axes(projection=cart_proj)
#    ax.set_extent([125,145,34,45])
#
#    shade=ax.contourf(
#      lons,lats,me_N,
#      levels=np.arange(0,0.035,0.005),
#      cmap="Reds",
#      transform=ccrs.PlateCarree()
#      )
#    
#    cbar=plt.colorbar(
#      shade,orientation="horizontal",
#      label="[/s]"
#      )
#
#    gl = ax.gridlines(draw_labels=True)
#    gl.xformatter = LONGITUDE_FORMATTER
#    gl.yformatter = LATITUDE_FORMATTER
#    gl.top_labels = False
#    gl.right_labels = False
#
#    ax.coastlines()
#    ax.add_feature(cfeature.LAND,color="gray")
#    ax.set_title(f"me-{time_str}UTC",fontsize=20)
#    
#    plt.savefig(f"{fig_dir}/me/n{member}/N_{time_str}.png")
#    plt.close("all")
#
##Anomaly
#    fig=plt.figure()
#    ax=plt.axes(projection=cart_proj)
#    ax.set_extent([125,145,34,45])
#
#    shade=ax.contourf(
#      lons,lats,ano_N,
#      levels=np.arange(-0.03,0.035,0.005),
#      cmap="bwr",
#      transform=ccrs.PlateCarree()
#      )
#    
#    cbar=plt.colorbar(
#      shade,orientation="horizontal",
#      label="[/s]"
#      )
#
#    gl = ax.gridlines(draw_labels=True)
#    gl.xformatter = LONGITUDE_FORMATTER
#    gl.yformatter = LATITUDE_FORMATTER
#    gl.top_labels = False
#    gl.right_labels = False
#
#    ax.coastlines()
#    ax.add_feature(cfeature.LAND,color="gray")
#    ax.set_title(f"anomaly-{time_str}UTC",fontsize=20)
#    
#    plt.savefig(f"{fig_dir}/ano/n{member}/anomaly_N_{time_str}.png")
#    plt.close("all")
#    print("Plot N")
#
###ushear 
##CTL
#    fig=plt.figure()
#    ax=plt.axes(projection=cart_proj)
#    ax.set_extent([125,145,34,45])
#
#    shade=ax.contourf(
#      lons,lats,ctl_ushear,
#      levels=np.arange(-0.03,0.035,0.005),
#      cmap="bwr",
#      transform=ccrs.PlateCarree()
#      )
#    
#    cbar=plt.colorbar(
#      shade,orientation="horizontal",
#      label="[m/s^2]"
#      )
#
#    gl = ax.gridlines(draw_labels=True)
#    gl.xformatter = LONGITUDE_FORMATTER
#    gl.yformatter = LATITUDE_FORMATTER
#    gl.top_labels = False
#    gl.right_labels = False
#
#    ax.coastlines()
#    ax.add_feature(cfeature.LAND,color="gray")
#    ax.set_title(f"ctl-{time_str}UTC",fontsize=20)
#    
#    plt.savefig(f"{fig_dir}/ctl/n{member}/ushear_{time_str}.png")
#    plt.close("all")
#
##ME
#    fig=plt.figure()
#    ax=plt.axes(projection=cart_proj)
#    ax.set_extent([125,145,34,45])
#
#    shade=ax.contourf(
#      lons,lats,me_ushear,
#      levels=np.arange(-0.03,0.035,0.005),
#      cmap="bwr",
#      transform=ccrs.PlateCarree()
#      )
#    
#    cbar=plt.colorbar(
#      shade,orientation="horizontal",
#      label="[m/s^2]"
#      )
#
#    gl = ax.gridlines(draw_labels=True)
#    gl.xformatter = LONGITUDE_FORMATTER
#    gl.yformatter = LATITUDE_FORMATTER
#    gl.top_labels = False
#    gl.right_labels = False
#
#    ax.coastlines()
#    ax.add_feature(cfeature.LAND,color="gray")
#    ax.set_title(f"me-{time_str}UTC",fontsize=20)
#    
#    plt.savefig(f"{fig_dir}/me/n{member}/ushear_{time_str}.png")
#    plt.close("all")
#
##Anomaly
#    fig=plt.figure()
#    ax=plt.axes(projection=cart_proj)
#    ax.set_extent([125,145,34,45])
#
#    shade=ax.contourf(
#      lons,lats,ano_ushear,
#      levels=np.arange(-0.03,0.035,0.005),
#      cmap="bwr",
#      transform=ccrs.PlateCarree()
#      )
#    
#    cbar=plt.colorbar(
#      shade,orientation="horizontal",
#      label="[m/s^2]"
#      )
#
#    gl = ax.gridlines(draw_labels=True)
#    gl.xformatter = LONGITUDE_FORMATTER
#    gl.yformatter = LATITUDE_FORMATTER
#    gl.top_labels = False
#    gl.right_labels = False
#
#    ax.coastlines()
#    ax.add_feature(cfeature.LAND,color="gray")
#    ax.set_title(f"anomaly-{time_str}UTC",fontsize=20)
#    
#    plt.savefig(f"{fig_dir}/ano/n{member}/anomaly_ushear_{time_str}.png")
#    plt.close("all")
#    print("Plot ushear")
#
###eady_growth_rate
##CTL
#    fig=plt.figure()
#    ax=plt.axes(projection=cart_proj)
#    ax.set_extent([125,145,34,45])
#
#    shade=ax.contourf(
#      lons,lats,ctl_egr*10000,
#      levels=np.arange(0,0.8,0.1),
#      cmap="Reds",
#      transform=ccrs.PlateCarree()
#      )
#    
#    cbar=plt.colorbar(
#      shade,orientation="horizontal",
#      label="10^-4[m/s^2]"
#      )
#
#    gl = ax.gridlines(draw_labels=True)
#    gl.xformatter = LONGITUDE_FORMATTER
#    gl.yformatter = LATITUDE_FORMATTER
#    gl.top_labels = False
#    gl.right_labels = False
#
#    ax.coastlines()
#    ax.add_feature(cfeature.LAND,color="gray")
#    ax.set_title(f"ctl-{time_str}UTC",fontsize=20)
#    
#    plt.savefig(f"{fig_dir}/ctl/n{member}/egr_{time_str}.png")
#    plt.close("all")
#
##ME
#    fig=plt.figure()
#    ax=plt.axes(projection=cart_proj)
#    ax.set_extent([125,145,34,45])
#
#    shade=ax.contourf(
#      lons,lats,me_egr*10000,
#      levels=np.arange(0,0.8,0.1),
#      cmap="Reds",
#      transform=ccrs.PlateCarree()
#      )
#    
#    cbar=plt.colorbar(
#      shade,orientation="horizontal",
#      label="10^-4[m/s^2]"
#      )
#
#    gl = ax.gridlines(draw_labels=True)
#    gl.xformatter = LONGITUDE_FORMATTER
#    gl.yformatter = LATITUDE_FORMATTER
#    gl.top_labels = False
#    gl.right_labels = False
#
#    ax.coastlines()
#    ax.add_feature(cfeature.LAND,color="gray")
#    ax.set_title(f"me-{time_str}UTC",fontsize=20)
#    
#    plt.savefig(f"{fig_dir}/me/n{member}/egr_{time_str}.png")
#    plt.close("all")
#
##Anomaly
#    fig=plt.figure()
#    ax=plt.axes(projection=cart_proj)
#    ax.set_extent([125,145,34,45])
#
#    shade=ax.contourf(
#      lons,lats,ano_egr*10000,
#      levels=np.arange(-0.45,0.55,0.10),
#      cmap="bwr",
#      transform=ccrs.PlateCarree()
#      )
#    
#    cbar=plt.colorbar(
#      shade,orientation="horizontal",
#      label="10^-4[m/s^2]"
#      )
#
#    gl = ax.gridlines(draw_labels=True)
#    gl.xformatter = LONGITUDE_FORMATTER
#    gl.yformatter = LATITUDE_FORMATTER
#    gl.top_labels = False
#    gl.right_labels = False
#
#    ax.coastlines()
#    ax.add_feature(cfeature.LAND,color="gray")
#    ax.set_title(f"anomaly-{time_str}UTC",fontsize=20)
#    
#    plt.savefig(f"{fig_dir}/ano/n{member}/anomaly_egr_{time_str}.png")
#    plt.close("all")
#    print("Plot eady growth rate")
#    
#    print("\n")
