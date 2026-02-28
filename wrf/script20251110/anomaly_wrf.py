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

var_label="Potential Temperature"
var_unit_label="degC"
case="200912etc_25km"
wrf_dir="/DATA/USER/ozeki/MyWRF"
wrfout_dir=f"{wrf_dir}/output_data/{case}_"
fig_dir=f"{wrf_dir}/fig/{case}_"


start_date=datetime(2009,12,26)
end_date=datetime(2009,12,28)
hour_step=[0,3,6,9,12,15,18,21]
print(f"Set Time : {start_date}----{end_date}")


date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day

  for h in hour_step:
    time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}"
    ctl_wrfout=f"{wrfout_dir}ctl/wrfout_d01_{time_str}:00:00"
    me_wrfout=f"{wrfout_dir}me/wrfout_d01_{time_str}:00:00"
    print("Read wrfout File ")
#    print(ctl_wrfout)
#    print(me_wrfout)

##ファイルオープンとデータ取得
    ctl_ds=Dataset(ctl_wrfout)
    me_ds=Dataset(me_wrfout)

#変数取り出す
    ctl_p=getvar(ctl_ds,"pressure")
    
    ctl_var=getvar(ctl_ds,"theta",units="degC")
    ctl_var=interplevel(ctl_var,ctl_p,850)

    me_p=getvar(me_ds,"pressure")
    me_var=getvar(me_ds,"theta",units="degC")
    me_var=interplevel(me_var,me_p,850)

    ano_var=ctl_var - me_var
#    print(ctl_pw)
#    print(me_pw)
    print("anomaly:\n",ano_var)
    
    cart_proj=get_cartopy(ctl_var)
    lats,lons=latlon_coords(ctl_var)

    ctl_ds.close()
    me_ds.close()

##Plot
#CTL
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,ctl_var,
      levels=np.arange(0,30,5),
      cmap="bwr",
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
    
    plt.savefig(f"{fig_dir}ctl/{var_label}_{time_str}.png")
    plt.close("all")

#ME
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,me_var,
      levels=np.arange(0,30,5),
      cmap="bwr",
      transform=ccrs.PlateCarree()
      )
    
    cbar=plt.colorbar(
      shade,orientation="horizontal",
      label=f"var_label_[{var_unit_label}]"
      )

    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False

    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"me-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}me/{var_label}_{time_str}.png")
    plt.close("all")

#Anomaly
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([125,145,34,45])

    shade=ax.contourf(
      lons,lats,ano_var,
      levels=[-10,-8,-6,-4,-2,0,2,4,6,8,10],
      cmap="bwr",
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
    ax.set_title(f"anomaly-{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}ano/anomaly_{var_label}_{time_str}.png")
    plt.close("all")


  date+=timedelta(days=1)  

print("End Program")
