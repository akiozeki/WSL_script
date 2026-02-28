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

var_label="SST"
var_unit_label="K"
case="202401"
wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/202401"
fig_dir=f"/home/akioz/fig"


start_date=datetime(2024,1,1)
end_date=datetime(2024,1,2)
hour_step=[0,6,12,18]
print(f"Set Time : {start_date}----{end_date}")


date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day

  for h in hour_step:
    time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}"
    wrfout=f"{wrfout_dir}/wrfout_d01_{time_str}:00:00"
    print("Read wrfout File",time_str)

##ファイルオープンとデータ取得
    ds=Dataset(wrfout)

#変数取り出す
    slp=getvar(ds,"slp")
    sst=getvar(ds,"SST")

    cart_proj=get_cartopy(slp)
    lats,lons=latlon_coords(slp)

    land=getvar(ds,"LANDMASK")

    ds.close()

#陸面マスク
#    sst=np.ma.masked_where(land == 1,sst)
#    slp=np.ma.masked_where(land == 1,slp)

##Plot
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)
    ax.set_extent([127,140,35,44])

    shade=ax.contourf(
      lons,lats,sst-273.15,
      levels=np.arange(0,22,2),
#      cmap="bwr",
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
    ax.set_title(f"{time_str}UTC",fontsize=20)
    
    plt.savefig(f"{fig_dir}/{var_label}_{time_str}.png")
    plt.close("all")


  date+=timedelta(days=1)

print("End Program")
