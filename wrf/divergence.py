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


time_str="2009-12-27_00"
wrfout_dir="/DATA/USER/ozeki/MyWRF/output_data"
fig_dir="/DATA/USER/ozeki/MyWRF/fig"
fig_ctl=f"{fig_dir}/200912etc_25km_ctl"
fig_me=f"{fig_dir}/200912etc_25km_me"

wrfout_ctl=f"{wrfout_dir}/200912etc_25km_ctl/wrfout_d01_{time_str}:00:00"
wrfout_me=f"{wrfout_dir}/200912etc_25km_me/wrfout_d01_{time_str}:00:00"

level=925

dx=25000.0*units.meter
dy=25000.0*units.meter


#ファイルオープンと変数取得
ds_ctl=Dataset(f"{wrfout_ctl}")
p_ctl=getvar(ds_ctl,"pressure")
u_ctl=getvar(ds_ctl,"ua")
v_ctl=getvar(ds_ctl,"va")
land_ctl=getvar(ds_ctl,"LANDMASK")

#us_ctl=np.ma.masked_where(land_ctl == 1,u_ctl)
#vs_ctl=np.ma.masked_where(land_ctl == 1,v_ctl)

up_ctl=interplevel(u_ctl,p_ctl,level)
vp_ctl=interplevel(v_ctl,p_ctl,level)
up_ctl=up_ctl*units.meter/units.second
vp_ctl=vp_ctl*units.meter/units.second

cart_proj=get_cartopy(u_ctl)
lats,lons=latlon_coords(u_ctl)

#divergence計算
div_ctl=mpcalc.divergence(up_ctl,vp_ctl,dx=dx,dy=dy,x_dim=-1,y_dim=-2)
print("div_ctl\n",div_ctl)

divs_ctl=np.ma.masked_where(land_ctl == 1,div_ctl)

ds_ctl.close()


ds_me=Dataset(f"{wrfout_me}")
p_me=getvar(ds_me,"pressure")
u_me=getvar(ds_me,"ua")
v_me=getvar(ds_me,"va")
land_me=getvar(ds_me,"LANDMASK")

#us_me=np.ma.masked_where(land_me == 1,u_me)
#vs_me=np.ma.masked_where(land_me == 1,v_me)

up_me=interplevel(u_me,p_me,level)
vp_me=interplevel(v_me,p_me,level)
up_me=up_me*units.meter/units.second
vp_me=vp_me*units.meter/units.second

#divergence計算
div_me=mpcalc.divergence(up_me,vp_me,dx=dx,dy=dy,x_dim=-1,y_dim=-2)
print("div_me\n",div_me)

divs_me=np.ma.masked_where(land_me == 1,div_me)

ds_me.close()


#偏差の計算
ano_up=up_ctl - up_me
ano_vp=vp_ctl - vp_me
ano_div=divs_ctl - divs_me

##PLOT
#CTL
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,45])


shade=ax.contourf(
  lons,lats,divs_ctl*10000,
  levels=[-3.0,-2.5,-2.0,-1.5,-1.0,-0.5,0,0.5,1.0,1.5,2.0,2.5,3.0],
  cmap="bwr",transform=ccrs.PlateCarree()
  )
cbar=plt.colorbar(shade,orientation="horizontal",label="divergence[10^-4/s]")

step=2
qx,qy,qk=1.1,-0.1,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  up_ctl.values[::step,::step],
  vp_ctl.values[::step,::step],
  scale=400,
  color="green",
  transform=ccrs.PlateCarree())
ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
######

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"ctl-{time_str}UTC",fontsize=20)
#ax.set_title("Elevation_25km_grid")

plt.savefig(f"{fig_ctl}/{level}divergence_{time_str}.png")

plt.close("all")

#ME
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,45])


shade=ax.contourf(
  lons,lats,divs_me*10000,
  levels=[-3.0,-2.5,-2.0,-1.5,-1.0,-0.5,0,0.5,1.0,1.5,2.0,2.5,3.0],
  cmap="bwr",transform=ccrs.PlateCarree()
  )
cbar=plt.colorbar(shade,orientation="horizontal",label="divergence[10^-4/s]")

step=2
qx,qy,qk=1.1,-0.1,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  up_me.values[::step,::step],
  vp_me.values[::step,::step],
  scale=400,
  color="green",
  transform=ccrs.PlateCarree())
ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
######

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"me-{time_str}UTC",fontsize=20)
#ax.set_title("Elevation_25km_grid")

plt.savefig(f"{fig_me}/{level}divergence_{time_str}.png")

plt.close("all")

#Anomaly
fig=plt.figure()
ax=plt.axes(projection=cart_proj)
ax.set_extent([125,140,35,45])


shade=ax.contourf(
  lons,lats,ano_div*10000,
  levels=[-3.0,-2.5,-2.0,-1.5,-1.0,-0.5,0,0.5,1.0,1.5,2.0,2.5,3.0],
  cmap="bwr",transform=ccrs.PlateCarree()
  )
cbar=plt.colorbar(shade,orientation="horizontal",label="divergence[10^-4/s]")

step=2
qx,qy,qk=1.1,-0.1,10
vector=ax.quiver(
  lons.values[::step,::step],
  lats.values[::step,::step],
  ano_up.values[::step,::step],
  ano_vp.values[::step,::step],
  scale=400,
  color="green",
  transform=ccrs.PlateCarree())
ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")

gl = ax.gridlines(draw_labels=True)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.top_labels = False
gl.right_labels = False
######

ax.coastlines()
ax.add_feature(cfeature.LAND,color="gray")
ax.set_title(f"ano_{time_str}UTC",fontsize=20)
#ax.set_title("Elevation_25km_grid")

plt.savefig(f"{fig_ctl}/anomaly_{level}divergence_{time_str}.png")

plt.close("all")

