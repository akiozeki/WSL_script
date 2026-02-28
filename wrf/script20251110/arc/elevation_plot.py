from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

fig_dir="/DATA/USER/ozeki/MyWRF/fig/200912low_ensemble"

#改変前
dfile1="/DATA/USER/ozeki/MyWRF/output_data/200912low_ensemble/ctl/n1/wrfinput_d01"

#改変後
dfile2="/DATA/USER/ozeki/MyWRF/output_data/200912low_ensemble/me/n1/wrfinput_d01"

ds1=Dataset(dfile1)
el1=getvar(ds1,"HGT")
print(el1)

cart_proj=get_cartopy(el1)
lats,lons=latlon_coords(el1)

fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([121,140,30,48])
shade=ax.contourf(lons,lats,el1,levels=np.arange(0,2000,100),cmap="pink_r",transform=ccrs.PlateCarree())
cbar = plt.colorbar(shade,orientation="vertical",label="Elevation[m]")
cbar.ax.set_ylabel("[m]",rotation=0)

####緯度経度ラベルを表示する(ChatGPTが教えてくれた)
gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlocator=FixedLocator([120,123,126,129,132,135,138])
gl.ylocator=FixedLocator([32,35,38,41,44,47])
######

ax.coastlines()
ax.add_feature(cfeature.BORDERS,linestyle=':')
#ax.add_feature(cfeature.LAND,color="gray")
#ax.set_title("Elevation_25km_grid")
#line_lon1=[124,130,130,124,124]
#line_lat1=[34,34,39,39,34]
#ax.plot(line_lon1,line_lat1,color="red",linewidth=2,transform=ccrs.PlateCarree())
#
#line_lon2=[123,132,132,123,123]
#line_lat2=[39,39,46,46,39]
#ax.plot(line_lon2,line_lat2,color="red",linewidth=2,transform=ccrs.PlateCarree())
#
line_lon3=[124,124,123,123,132,132,130,130,124]
line_lat3=[34,39,39,46,46,39,39,34,34]
ax.plot(line_lon3,line_lat3,color="red",linewidth=4,transform=ccrs.PlateCarree())

plt.savefig(f"{fig_dir}/ctl/Mt.Chanbai_domain_elevation.png")
#plt.tight_layout()
plt.close("all")
ds1.close()

##改変後プロット
ds2=Dataset(dfile2)
el2=getvar(ds2,"HGT")
print(el2)

cart_proj=get_cartopy(el2)
lats,lons=latlon_coords(el2)

fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([121,140,30,48])
shade=ax.contourf(lons,lats,el2,levels=np.arange(0,2000,100),cmap="pink_r",transform=ccrs.PlateCarree())
cbar=plt.colorbar(shade,orientation="vertical",label="[m]")
cbar.ax.set_ylabel("[m]",rotation=0)


####緯度経度ラベルを表示する(ChatGPTが教えてくれた)
gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
gl.xlocator=FixedLocator([120,123,126,129,132,135,138])
gl.ylocator=FixedLocator([32,35,38,41,44,47])
######

ax.coastlines()
#ax.add_feature(cfeature.LAND,color="gray")
#ax.set_title("Elevation_25km_grid")

plt.savefig(f"{fig_dir}/me/Mt.Chanbai_domain_elevation.png")
#plt.tight_layout()
plt.close("all")
ds2.close()
