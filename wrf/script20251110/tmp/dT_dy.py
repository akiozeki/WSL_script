#from __from__ import print_function
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

var_label="dT850_dy"
var_unit_label="K/10km"

case="200912low_ensemble"
member=1
wrf_dir="/DATA/USER/ozeki/MyWRF"
wrfout_dir=f"{wrf_dir}/output_data/{case}"
fig_dir=f"{wrf_dir}/fig/{case}"


start_date=datetime(2009,12,26)
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
    print("Read wrfout File",time_str)

##ファイルオープンとデータ取得
    ctl_ds=Dataset(ctl_wrfout)
    me_ds=Dataset(me_wrfout)

    ctl_p=getvar(ctl_ds,"pressure")
    ctl_slp=getvar(ctl_ds,"slp")
    ctl_tmp=getvar(ctl_ds,"tk")
    ctl_tmp850=interplevel(ctl_tmp,ctl_p,850)
    print(ctl_tmp850)
    ctl_land=getvar(ctl_ds,"LANDMASK")
    ctl_tmp850=np.ma.masked_where(ctl_land == 1,ctl_tmp850)
#    print("temp850",ctl_tmp850)

    me_p=getvar(me_ds,"pressure")
    me_slp=getvar(me_ds,"slp")
    me_tmp=getvar(me_ds,"tk")
    me_tmp850=interplevel(me_tmp,ctl_p,850)
    me_land=getvar(me_ds,"LANDMASK")
    me_tmp850=np.ma.masked_where(me_land == 1,me_tmp850)


    cart_proj=get_cartopy(ctl_slp)
    lats,lons=latlon_coords(ctl_slp)

    ctl_ds.close()
    me_ds.close()

##計算
    dy=25000
#ここではm単位で指定  

    ctl_dTdy=-np.gradient(ctl_tmp850,dy,axis=0)
    me_dTdy=-np.gradient(me_tmp850,dy,axis=0)
#勾配は北-南で計算されるので北<南を正とするためにマイナスを付す    
    ano_dTdy=ctl_dTdy - me_dTdy

#    print(ano_dTdy)

#今回単位付与は行っていない(np.gradientで勾配計算をする際Quantifyは相性が悪い)
#計算をmpcalcで行えれば単位も扱えるかもしれない

##Plot
#CTL
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([127,145,35,44])

    shade=ax.contourf(
      lons,lats,ctl_dTdy*10000,
      levels=np.arange(-0.80,1.0,0.20),
      cmap="seismic",
      transform=ccrs.PlateCarree()
      )

    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label=f"{var_label}_[{var_unit_label}]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"ctl-{time_str}UTC",fontsize=20)

    plt.savefig(f"{fig_dir}/ctl/n{member}/{var_label}_{time_str}.png")
    plt.close("all")

#ME
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([127,145,35,44])

    shade=ax.contourf(
      lons,lats,me_dTdy*10000,
      levels=np.arange(-0.80,1.0,0.20),
      cmap="seismic",
      transform=ccrs.PlateCarree()
      )

    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label=f"{var_label}_[{var_unit_label}]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"me-{time_str}UTC",fontsize=20)

    plt.savefig(f"{fig_dir}/me/n{member}/{var_label}_{time_str}.png")
    plt.close("all")

#Anomaly
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([127,145,35,44])

    shade=ax.contourf(
      lons,lats,ano_dTdy*10000,
      levels=np.arange(-0.80,1.0,0.20),
      cmap="seismic",
      transform=ccrs.PlateCarree()
      )

    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label=f"{var_label}_[{var_unit_label}]"
      )

    contour=ax.contour(
      lons,lats,ctl_slp,
      levels=np.arange(960,1040,6),
      colors="black",
      transform=ccrs.PlateCarree()
      )
    ax.clabel(contour)

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"anomaly-{time_str}UTC",fontsize=20)

    plt.savefig(f"{fig_dir}/ano/n{member}/anomaly_{var_label}_{time_str}.png")
    plt.close("all")


  date+=timedelta(days=1)

print("End Program")
