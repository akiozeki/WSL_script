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

var_label="SST-SAT"
var_unit_label="degC"
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
#    print(ctl_wrfout)
#    print(me_wrfout)

##ファイルオープンとデータ取得
    ctl_ds=Dataset(ctl_wrfout)
    me_ds=Dataset(me_wrfout)

#変数取り出す
    ctl_slp=getvar(ctl_ds,"slp")
    ctl_sst=getvar(ctl_ds,"SST")
    ctl_tmp2m=getvar(ctl_ds,"T2")
    me_sst=getvar(me_ds,"SST")
    me_tmp2m=getvar(me_ds,"T2")

    cart_proj=get_cartopy(ctl_tmp2m)
    lats,lons=latlon_coords(ctl_tmp2m)

    ctl_land=getvar(ctl_ds,"LANDMASK")
    me_land=getvar(me_ds,"LANDMASK")

    ctl_ds.close()
    me_ds.close()

#計算
    ctl_tdelta=ctl_sst - ctl_tmp2m
    ctl_tdelta=np.ma.masked_where(ctl_land == 1,ctl_tdelta)
    me_tdelta=me_sst - me_tmp2m
    me_tdelta=np.ma.masked_where(me_land == 1,me_tdelta)
    ano_tdelta=ctl_tdelta - me_tdelta

    ctl_slp=np.ma.masked_where(ctl_land == 1,ctl_slp)

##Plot
#CTL
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([127,140,35,44])

    shade=ax.contourf(
      lons,lats,ctl_tdelta,
      levels=np.arange(-9,11,2),
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
    
    plt.savefig(f"{fig_dir}/ctl/n{member}/{var_label}_{time_str}.png")
    plt.close("all")

#ME
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([127,140,35,44])

    shade=ax.contourf(
      lons,lats,me_tdelta,
      levels=np.arange(-9,11,2),
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
    
    plt.savefig(f"{fig_dir}/me/n{member}/{var_label}_{time_str}.png")
    plt.close("all")

#Anomaly
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([127,140,35,44])

    shade=ax.contourf(
      lons,lats,ano_tdelta,
      levels=np.arange(-4.5,5.5,1),
      cmap="bwr",
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
