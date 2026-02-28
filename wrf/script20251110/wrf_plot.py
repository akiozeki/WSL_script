#from __from__ import print_function

from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER,LATITUDE_FORMATTER

experiment="me"
member=1
print(f"{experiment}-run")
print(f"N={member}")

wrf_dir="/DATA/USER/ozeki/MyWRF"
wrfout_dir=f"{wrf_dir}/output_data/200912low_ensemble/{experiment}/n{member}"
fig_dir=f"{wrf_dir}/fig/200912low_ensemble/{experiment}"


##期間を指定
start_date=datetime(2009,12,22)
end_date=datetime(2010,1,1)
hour_step=[0,3,6,9,12,15,18,21]
#ココでタイムステップを任意に設定可能
print(f"Set Time : {start_date}----{end_date}")

date=start_date

while date <= end_date:
  y=date.year
  m=date.month
  d=date.day

  for h in hour_step:
    time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}"
    filename=f"wrfout_d01_{time_str}:00:00"
    wrfout=Dataset(f"{wrfout_dir}/{filename}")
    print("Read wrfout File ",filename)

##データ抽出
    p=getvar(wrfout,"pressure")
    slp=getvar(wrfout,"slp")
    u=getvar(wrfout,"ua")
    v=getvar(wrfout,"va")
    u925=interplevel(u,p,925)
    v925=interplevel(v,p,925)
    z=getvar(wrfout,"z")
    z500=interplevel(z,p,500)
    el=getvar(wrfout,"HGT")
    

    landmask=getvar(wrfout,"LANDMASK")
    slp_sea=np.ma.masked_where(landmask == 1,slp)
#    tmp_kelvin=getvar(wrfout,"temp")
#    print(tmp_kelvin)
#    tmp_kelvin_925=interplevel(tmp_kelvin,p,925)
    cart_proj=get_cartopy(slp)
#cartopyマッピングオブジェクトの取得
#    print(cart_proj)

    lats,lons=latlon_coords(slp)
#緯度経度座標系を得る,これを設定しないとずれて地図を作図した時にヨーロッパ辺りが表示される
#    tmp_925=tmp_kelvin_925-273.15
#    print("T925\n",tmp_925)

##作図
    fig=plt.figure()
    ax=plt.axes(projection=cart_proj)

    contour=ax.contour(lons,lats,slp,levels=np.arange(940,1040,4),colors="black",linewidths=1.5,transform=ccrs.PlateCarree())
#陸面マスク
#    contour=ax.contour(lons,lats,slp_sea,levels=np.arange(940,1040,4),colors="black",linewidths=1.5,transform=ccrs.PlateCarree())
    ax.clabel(contour)

#気温   
#    shade=ax.contourf(lons,lats,tmp_925,levels=np.arange(-30,35,5),cmap="bwr",transform=ccrs.PlateCarree())
#    plt.colorbar(shade,orientation="horizontal",label="TEMP925hPa[°C]")
#    shade=ax.contourf(lons,lats,el,levels=np.arange(0,2000,100),cmap="pink_r",transform=ccrs.PlateCarree())

#Z500
    shade=ax.contourf(lons,lats,z500,levels=np.arange(5000,6000,100),cmap="bwr",transform=ccrs.PlateCarree())
    cbar=plt.colorbar(shade,orientation="vertical",label="[m]")
    cbar.set_label("[m]",rotation=0)
#風
#    step=5
#    qx,qy,qk=1.1,-0.1,10
#    vector=ax.quiver(
#      lons.values[::step,::step],
#      lats.values[::step,::step],
#      u925.values[::step,::step],
#      v925.values[::step,::step],
#      scale=400,
#      color="blue",
#      transform=ccrs.PlateCarree()
#      )
#    
#    ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")
#    

    gl=ax.gridlines(draw_labels=True)
    gl.xformatter=LONGITUDE_FORMATTER
    gl.yformatter=LATITUDE_FORMATTER
    gl.top_labels=False
    gl.right_labels=False
    
    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"{experiment}_{time_str}UTC",fontsize=20)
    #ax.set_title("Elevation_25km_grid")
    
    plt.savefig(f"{fig_dir}/slp_Z500_{time_str}n{member}.png")
    plt.close("all")

    wrfout.close()
  date+=timedelta(days=1)

print("End Program")

##アニメーション
from PIL import Image
import glob
import pprint

keyword="slp_Z500"

files=sorted(glob.glob(f"{fig_dir}/{keyword}*.png"))
pprint.pprint(files)

images=list(map(lambda file : Image.open(file),files))
images[0].save(f"{fig_dir}/{experiment}n{member}_animation_{keyword}.gif",save_all=True,append_images=images[1:],optimize=True,duration=1000,loop=0)
print("Create Animation")
