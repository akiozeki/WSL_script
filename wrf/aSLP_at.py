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

ex="ME00"

var="slp"
var_unit_label="hpa"
case="2025DJF"
wrf_dir="/home/akioz/MyWRF"
wrfout_dir=f"{wrf_dir}/output/{case}/{ex}"
output_dir=f"/home/akioz/calculate/wrf/{case}"


start_date=datetime(2024,12,1,0)
end_date=datetime(2025,2,28,18)
print(f"Set Time : {start_date}----{end_date}")

dh=6

time_list=[]
slp_list=[]
aslp_at_list=[]

date=start_date
while date <= end_date:
  y=date.year
  m=date.month
  d=date.day
  h=date.hour
  time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}"
  print("Time:",time_str)


  bdate=date - timedelta(hours=6)
  by=bdate.year
  bm=bdate.month
  bd=bdate.day
  bh=bdate.hour
  btime_str=f"{by}-{bm:02d}-{bd:02d}_{bh:02d}"
  print("Back Time:",btime_str)

  fdate=date + timedelta(hours=6)
  fy=fdate.year
  fm=fdate.month
  fd=fdate.day
  fh=fdate.hour
  ftime_str=f"{fy}-{fm:02d}-{fd:02d}_{fh:02d}"
  print("Front Time:",ftime_str)
  
  b_wrfout=f"{wrfout_dir}/wrfout_d01_{btime_str}:00:00"
  m_wrfout=f"{wrfout_dir}/wrfout_d01_{time_str}:00:00"
  f_wrfout=f"{wrfout_dir}/wrfout_d01_{ftime_str}:00:00"
  print("Read wrfout File ")
  print(b_wrfout)
  print(m_wrfout)
  print(f_wrfout)

###ファイルオープンとデータ取得
  b_ds=Dataset(b_wrfout)
  m_ds=Dataset(m_wrfout)
  f_ds=Dataset(f_wrfout)

##変数取り出す
  bslp=getvar(b_ds,"slp",units="hpa")
  mslp=getvar(m_ds,"slp",units="hpa")
  fslp=getvar(f_ds,"slp",units="hpa")
  
  b_ds.close()
  m_ds.close()
  f_ds.close()

  aslp_at=(fslp-bslp)/2*dh
#  aslp_at=aslp_at*aslp_at

  time_list.append(date)
  slp_list.append(mslp.values)
  aslp_at_list.append(aslp_at.values)

  date+=timedelta(hours=dh)  

da_slp=xr.DataArray(
  np.array(slp_list),
  dims=("time","south_north","west_east"),
  coords={"time":time_list},
  name="slp"
)

da_aslp_at=xr.DataArray(
    np.array(aslp_at_list),
    dims=("time","south_north","west_east"),
    coords={"time":time_list},
    name="aslp_at"
)

ds=xr.Dataset({
  "slp":da_slp,
  "aslp_at":da_aslp_at
})

filename=f"{output_dir}/{ex}{case}_aslp_at.nc"
ds.to_netcdf(filename)
print("Save File",filename)


print("End Program")
