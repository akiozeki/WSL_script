from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel
import metpy.calc as mpcalc
from metpy.units import units
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import xarray as xr
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

case="200912low_ensemble"
member=1
wrf_dir="/DATA/USER/ozeki/MyWRF"
wrfout_dir=f"{wrf_dir}/output_data/{case}"
fig_dir=f"{wrf_dir}/fig/{case}"



start_date=datetime(2009,12,25)
end_date=datetime(2009,12,28)
hour_step=[0,6,12,18]
print(f"Set Time : {start_date}----{end_date}")


date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day

  for h in hour_step:
    time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}"
    ctl_wrfout=f"{wrfout_dir}/ctl/n{member}/wrfout_d01_{time_str}:00:00"
    me_wrfout=f"{wrfout_dir}/me/n{member}/wrfout_d01_{time_str}:00:00"
    print("Time Step : ",time_str)
    print("Read wrfout File ")
#    print(ctl_wrfout)
#    print(me_wrfout)

##ファイルオープンとデータ取得
    ctl_ds=Dataset(ctl_wrfout)
    me_ds=Dataset(me_wrfout)

#変数を取り出す
    ctl_lat=getvar(ctl_ds,"lat")
    ctl_p=getvar(ctl_ds,"pressure")
    
    ctl_theta=getvar(ctl_ds,"theta",units="K")
    ctl_theta900=interplevel(ctl_theta,ctl_p,900)
    ctl_theta850=interplevel(ctl_theta,ctl_p,850)
    ctl_theta800=interplevel(ctl_theta,ctl_p,800)

    ctl_u=getvar(ctl_ds,"ua")
    ctl_u900=interplevel(ctl_u,ctl_p,900)
    ctl_u800=interplevel(ctl_u,ctl_p,800)

    ctl_z=getvar(ctl_ds,"z")
    ctl_z900=interplevel(ctl_z,ctl_p,900)
    ctl_z800=interplevel(ctl_z,ctl_p,800)

##################
    me_lat=getvar(me_ds,"lat")
    me_p=getvar(me_ds,"pressure")

    me_theta=getvar(ctl_ds,"theta",units="K")
    me_theta900=interplevel(me_theta,me_p,900)
    me_theta850=interplevel(me_theta,me_p,850)
    me_theta800=interplevel(me_theta,me_p,800)

    me_u=getvar(me_ds,"ua")
    me_u900=interplevel(me_u,me_p,900)
    me_u800=interplevel(me_u,me_p,800)

    me_z=getvar(me_ds,"z")
    me_z900=interplevel(me_z,me_p,900)
    me_z800=interplevel(me_z,me_p,800)

    
    cart_proj=get_cartopy(ctl_p)
    lats,lons=latlon_coords(ctl_p)

    ctl_ds.close()
    me_ds.close()


##計算
    ctl_delta_z=ctl_z800 - ctl_z900
    me_delta_z=me_z800 - me_z900

#安定度
    ctl_delta_theta=ctl_theta800 - ctl_theta900    
    ctl_N2=(9.81/ctl_theta850)*(ctl_delta_theta/ctl_delta_z)
    ctl_N=np.sqrt(ctl_N2)
    ctl_N=ctl_N*units("/s")

    me_delta_theta=me_theta800 - me_theta900
    me_N2=(9.81/me_theta850)*(me_delta_theta/me_delta_z)
    me_N=np.sqrt(me_N2)
    me_N=me_N*units("/s")

    ano_N=ctl_N - me_N
#    print(ano_N2)
#鉛直シア
    ctl_delta_u=ctl_u800 - ctl_u900  
    ctl_ushear=ctl_delta_u/ctl_delta_z
    ctl_ushear=ctl_ushear*units("m/s^2")
    ctl_ushear_ganma=np.abs(ctl_ushear)

    me_delta_u=me_u800 - me_u900
    me_ushear=me_delta_u/me_delta_z
    me_ushear=me_ushear*units("m/s^2")
    me_ushear_ganma=np.abs(me_ushear)

    ano_ushear=ctl_ushear_ganma - me_ushear_ganma
#    print(ano_ushear)

#eady_growth_rate
    ctl_f=mpcalc.coriolis_parameter(ctl_lat)
    ctl_egr=0.31*(ctl_f/ctl_N)*ctl_ushear_ganma

    me_f=mpcalc.coriolis_parameter(me_lat)
    me_egr=0.31*(me_f/me_N)*me_ushear_ganma

    ano_egr=ctl_egr - me_egr
#    print("anomaly_eady_growth_rate\n",ano_egr)

##Plot

##N
#CTL
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,ctl_N,
      levels=np.arange(0,0.035,0.005),
      cmap="Reds",
      transform=ccrs.PlateCarree()
      )
    
    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label="[/s]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"ctl-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}/ctl/n{member}/N_{time_str}.png")
    plt.close("all")

#ME
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,me_N,
      levels=np.arange(0,0.035,0.005),
      cmap="Reds",
      transform=ccrs.PlateCarree()
      )
    
    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label="[/s]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"me-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}/me/n{member}/N_{time_str}.png")
    plt.close("all")

#Anomaly
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,ano_N,
      levels=np.arange(-0.03,0.035,0.005),
      cmap="bwr",
      transform=ccrs.PlateCarree()
      )
    
    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label="[/s]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"anomaly-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}/ano/n{member}/anomaly_N_{time_str}.png")
    plt.close("all")
    print("Plot N")

##ushear 
#CTL
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,ctl_ushear,
      levels=np.arange(-0.03,0.035,0.005),
      cmap="bwr",
      transform=ccrs.PlateCarree()
      )
    
    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label="[m/s^2]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"ctl-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}/ctl/n{member}/ushear_{time_str}.png")
    plt.close("all")

#ME
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,me_ushear,
      levels=np.arange(-0.03,0.035,0.005),
      cmap="bwr",
      transform=ccrs.PlateCarree()
      )
    
    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label="[m/s^2]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"me-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}/me/n{member}/ushear_{time_str}.png")
    plt.close("all")

#Anomaly
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,ano_ushear,
      levels=np.arange(-0.03,0.035,0.005),
      cmap="bwr",
      transform=ccrs.PlateCarree()
      )
    
    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label="[m/s^2]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"anomaly-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}/ano/n{member}/anomaly_ushear_{time_str}.png")
    plt.close("all")
    print("Plot ushear")

##eady_growth_rate
#CTL
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,ctl_egr*10000,
      levels=np.arange(0,0.8,0.1),
      cmap="Reds",
      transform=ccrs.PlateCarree()
      )
    
    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label="10^-4[m/s^2]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"ctl-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}/ctl/n{member}/egr_{time_str}.png")
    plt.close("all")

#ME
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,me_egr*10000,
      levels=np.arange(0,0.8,0.1),
      cmap="Reds",
      transform=ccrs.PlateCarree()
      )
    
    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label="10^-4[m/s^2]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"me-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}/me/n{member}/egr_{time_str}.png")
    plt.close("all")

#Anomaly
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,ano_egr*10000,
      levels=np.arange(-0.45,0.55,0.10),
      cmap="bwr",
      transform=ccrs.PlateCarree()
      )
    
    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label="10^-4[m/s^2]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"anomaly-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}/ano/n{member}/anomaly_egr_{time_str}.png")
    plt.close("all")
    print("Plot eady growth rate")
    
    print("\n")

  date+=timedelta(days=1)  

print("End Program")
