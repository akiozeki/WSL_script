##任意の緯度経度ポイントの時系列を書く
from datetime import datetime,timedelta
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import xarray as xr

varname="temp"
varlabel="K"

case="2025DJF"
ex="CTL"
n_member=1
moving_day=7

##緯度-経度-等圧面を指定(緯度経度は最も近いグリッドになる)
lat=40
lon=135
lev=850

##時間方向のスライス2024-12-01_00->0,2025-02-28_18->359
s=0
e=359
####################

input_dir=f"/home/akioz/calculate/wrf/{case}/MMean"
fig_dir=f"/home/akioz/fig/wrf/{case}/{ex}/time_series"

dfile=f"{input_dir}/{ex}_{varname}{lev}_{moving_day}dMean.nc"
ds=xr.open_dataset(dfile)
print(ds)

lat_a=ds["XLAT"]
lon_a=ds["XLONG"]
time=ds["Time"]

#print(lat_a)
#print(lon_a)
print(time)

dist=np.sqrt((lat_a - lat)**2+(lon_a - lon)**2)
y,x=np.unravel_index(np.argmin(dist.values),dist.shape)
print(f"Set Point (y,x)=({y},{x})")

var_a=ds[varname]
varm_a=ds[f"{varname}_m"]
vara_a=ds[f"{varname}_a"]
#print("T_a:",T_a)

#指定したy,xの時系列データを取り出す
var=var_a[s:e,y,x]
varm=varm_a[s:e,y,x]
vara=vara_a[s:e,y,x]
#print("T:",T)

##Plot
#var
fig=plt.figure()
ax=plt.axes()
ax.set_xlim(time.min(),time.max())
ax.set_ylim(250,280)
ax.plot(time[s:e],var,c="orangered",lw=2)
#ax.set_title("All")
ax.xaxis.set_major_locator(mdates.DayLocator(interval=14))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
ax.tick_params(labelsize=14)
fig.autofmt_xdate()
#plt.show()
plt.savefig(f"{fig_dir}/{varname}_all({lat},{lon}).png")
plt.close("all")

#varm
fig=plt.figure()
ax=plt.axes()
ax.set_xlim(time.min(),time.max())
ax.set_ylim(250,280)
ax.plot(time[s:e],varm,c="orangered",lw=2)
#ax.set_title("All")
ax.xaxis.set_major_locator(mdates.DayLocator(interval=14))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
ax.tick_params(labelsize=14)
fig.autofmt_xdate()
#plt.show()
plt.savefig(f"{fig_dir}/{varname}_m({lat},{lon}).png")
plt.close("all")

#varm
fig=plt.figure()
ax=plt.axes()
ax.set_xlim(time.min(),time.max())
ax.set_ylim(-15,15)
ax.plot(time[s:e],vara,c="orangered",lw=2)
#ax.set_title("All")
ax.xaxis.set_major_locator(mdates.DayLocator(interval=14))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
ax.tick_params(labelsize=14)
fig.autofmt_xdate()
#plt.show()
plt.savefig(f"{fig_dir}/{varname}_a({lat},{lon}).png")
plt.close("all")


