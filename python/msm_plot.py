import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

ds=xr.open_dataset("/home/akioz/data/netCDF/MSM/msmp_20250905.nc")
print(ds)

plt.rcParams["font.size"]=12
fig = plt.figure(figsize=[20,12],constrained_layout=True)

skip=12
plev=950
qx,qy,qk=1.3,0.05,20
axs=[]
tlevs=np.arange(18,30,1)
for i in range(ds.time.size):
    ax=fig.add_subplot(2,4,i+1,projection=ccrs.PlateCarree())
#    ax.set_extent([137.5,139,34.5,35.5],crs=ccrs.PlateCarree())
    ax.set_extent([130,150,25,45],crs=ccrs.PlateCarree())

    z=ds.z.sel(p=plev).isel(time=i)
    T=ds.temp.sel(p=plev).isel(time=i)
    u=ds.u.sel(p=plev).isel(time=i)[::skip,::skip]
    v=ds.v.sel(p=plev).isel(time=i)[::skip,::skip]
    shade=ax.contourf(ds.lon,ds.lat,T-273.15,
                    tlevs,transform=ccrs.PlateCarree(), cmap="bwr")
    contour=ax.contour(ds.lon,ds.lat,z,colors="black",linewidths=1.5,transform=ccrs.PlateCarree())
    ax.clabel(contour)

    q=ax.quiver(ds.lon[::skip],ds.lat[::skip],u,v,scale=200,width=0.01,transform=ccrs.PlateCarree())
    if i+1==ds.time.size:
        ax.quiverkey(q,qx,qy,qk,f"{qk} m/s")
    ax.set_title(ds.time[i].dt.strftime("%Y-%m-%d-%HUTC").values)
    ax.coastlines()
    gl = ax.gridlines(draw_labels=True)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.top_labels = False
    gl.right_labels = False
    gl.xlines=False
    gl.ylines=False
    axs.append(ax)
fig.colorbar(shade, ax=axs, shrink=0.8, label="T(℃)")
fig.suptitle(f"MSM Analysis {plev}hPa")
plt.savefig(f"/home/akioz/fig/makinohara_tornado/0905msm_plot{plev}hPa_large")
#plt.show()

