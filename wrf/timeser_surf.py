#from __from__ import print_function

from datetime import datetime,timedelta
from netCDF4 import Dataset
from wrf import getvar,get_cartopy,latlon_coords,geo_bounds,interplevel
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER,LATITUDE_FORMATTER

case="2025DJF"
experiment="ME00"
member=0
#=0でアンサンブルナシに対応
print(f"{experiment}-run")
print(f"N={member}")

wrf_dir="/home/akioz/MyWRF"
if member == 0:
  wrfout_dir=f"{wrf_dir}/output/{case}/{experiment}"
  fig_dir=f"/home/akioz/fig/wrf/{case}/{experiment}"

else:
  wrfout_dir=f"{wrf_dir}/output/{case}/{experiment}/n{member}"
  fig_dir=f"/home/akioz/fig/wrf/{case}/{experiment}/n{member}"


##期間を指定
start_date=datetime(2024,12,1)
end_date=datetime(2025,2,28)
hour_step=[0,6,12,18]
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
    slp=getvar(wrfout,"slp")
    tmp2m_K=getvar(wrfout,"T2")
    tmp2m=tmp2m_K - 273.15
    u10,v10=getvar(wrfout,"uvmet10")
#    print(u10)
#    print(v10)
    landmask=getvar(wrfout,"LANDMASK")
    slp_sea=np.ma.masked_where(landmask == 1,slp)
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
    ax.set_extent([116,154,27,50])
    contour=ax.contour(lons,lats,slp,levels=np.arange(940,1040,4),colors="black",linewidths=1.5,transform=ccrs.PlateCarree())
#陸面マスク
#    contour=ax.contour(lons,lats,slp_sea,levels=np.arange(940,1040,4),colors="black",linewidths=1.5,transform=ccrs.PlateCarree())
    ax.clabel(contour)

#気温   
    shade=ax.contourf(lons,lats,tmp2m,levels=np.arange(-30,35,5),cmap="bwr",transform=ccrs.PlateCarree())
#    plt.colorbar(shade,orientation="horizontal",label="TEMP925hPa[°C]")
#    shade=ax.contourf(lons,lats,el,levels=np.arange(0,2000,100),cmap="pink_r",transform=ccrs.PlateCarree())

#風
    step=4
    qx,qy,qk=1.1,-0.1,10
    vector=ax.quiver(
      lons.values[::step,::step],
      lats.values[::step,::step],
      u10.values[::step,::step],
      v10.values[::step,::step],
      scale=400,
      color="black",
      transform=ccrs.PlateCarree()
      )
    
    ax.quiverkey(vector,qx,qy,qk,f"{qk}m/s")
    

    gl=ax.gridlines(draw_labels=True)
    gl.xformatter=LONGITUDE_FORMATTER
    gl.yformatter=LATITUDE_FORMATTER
    gl.top_labels=False
    gl.right_labels=False
    
    ax.coastlines()
    ax.add_feature(cfeature.LAND,color="gray")
    ax.set_title(f"{experiment}_{time_str}UTC",fontsize=20)
    #ax.set_title("Elevation_25km_grid")
    
    plt.savefig(f"{fig_dir}/time_series/{experiment}_surf_{time_str}n{member}.png")
    plt.close("all")

    wrfout.close()
  date+=timedelta(days=1)

print("End Program")

##アニメーション
from PIL import Image
import glob
import pprint

keyword=f"{experiment}_surf"

files=sorted(glob.glob(f"{fig_dir}/time_series/{keyword}*.png"))
pprint.pprint(files)

images=list(map(lambda file : Image.open(file),files))
images[0].save(f"{fig_dir}/time_series/{experiment}_animation_{keyword}.gif",save_all=True,append_images=images[1:],optimize=True,duration=1000,loop=0)
print("Create Animation")
