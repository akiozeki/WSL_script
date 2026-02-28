from __future__ import print_function, division
import numpy as np
from netCDF4 import Dataset
from wrf import getvar, vertcross, CoordPair
import matplotlib.pyplot as plt
from datetime import datetime,timedelta

case="200912low_ensemble"
experiment="me"
member=1

wrfout_dir=f"/DATA/USER/ozeki/MyWRF/output_data/{case}/{experiment}/n{member}"
fig_dir=f"/DATA/USER/ozeki/MyWRF/fig/{case}/{experiment}"

##期間を指定
start_date=datetime(2009,12,15)
end_date=datetime(2010,1,1)
hour_step=[0,3,6,9,12,15,18,21]
#ココでタイムステップを任意に設定可能
print(f"Set Time : {start_date}----{end_date}")

date=start_date


#断面図の位置設定
##例のごとくlatlon->yx変換
#wrfinput=f"{wrfout_dir}/wrfinput_d01"
#input_ds=Dataset(wrfinput)
#lat=getvar(input_ds,"lat")
#lon=getvar(input_ds,"lon")
#
#start_lat,start_lon=41,122
#end_lat,end_lon=41,132
#
#
#start_dist=np.sqrt((lat-start_lat)**2+(lon-start_lon)**2)
#sy,sx=np.unravel_index(np.argmin(start_dist.values),start_dist.shape)
#print(f"start=(y,x)=({sy},{sx})")
#
#end_dist=np.sqrt((lat-end_lat)**2+(lon-end_lon)**2)
#ey,ex=np.unravel_index(np.argmin(end_dist.values),end_dist.shape)
#print(f"start=(y,x)=({ey},{ex})")

while date <= end_date:
  y=date.year
  m=date.month
  d=date.day

  for h in hour_step:
    time_str=f"{y}-{m:02d}-{d:02d}_{h:02d}"
    filename=f"wrfout_d01_{time_str}:00:00"
    ds=Dataset(f"{wrfout_dir}/{filename}")
    print("Read wrfout File ",filename)


    z=getvar(ds,"z")
    p=getvar(ds,"p",units="hpa")
    tmp=getvar(ds,"temp",units="degC")
    lat=getvar(ds,"lat")
    lon=getvar(ds,"lon")
    #print(lat)
    
    #断面データを取り出す
    start_point=CoordPair(x=20,y=68)
    end_point=CoordPair(x=54,y=68)
    t_vert=vertcross(tmp,z,start_point=start_point,end_point=end_point,latlon=True)
    p_vert=vertcross(p,z,start_point=start_point,end_point=end_point,latlon=True)
    
    print(t_vert)
    
    #変数,座標変数の取り出し
    #height=z_vert.values
    pdata=p_vert.values
    tmpdata=t_vert.values
    vert=t_vert.vertical.values
    idx=t_vert.cross_line_idx.values
    
    plt.rcParams["font.size"]=16
    fig=plt.figure()
    ax=plt.axes()
    ax.set_xticks([])      
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Height[m]")
    ax.set_ylim(0,5000)
    shade=ax.contourf(idx,vert,tmpdata,levels=np.arange(-30,5,5),cmap="bwr")
    plt.colorbar(shade,label="temp[degC]")
    
    contour=ax.contour(idx,vert,pdata,levels=np.arange(500,1100,100),colors="black",linewidth=1.0)
    ax.clabel(contour)
    ax.set_title(f"{time_str}")
    plt.tight_layout()
    #ax.invert_yaxis()鉛直軸反転
    plt.savefig(f"{fig_dir}/n{member}vertical_{time_str}_122-132.png")
    
    ds.close()
  date+=timedelta(days=1)

print("End Program")    

##アニメーション
from PIL import Image
import glob
import pprint

keyword=f"n{member}vertical"

files=sorted(glob.glob(f"{fig_dir}/{keyword}*.png"))
pprint.pprint(files)

images=list(map(lambda file : Image.open(file),files))
images[0].save(f"{fig_dir}/{experiment}_animation_{keyword}.gif",save_all=True,append_images=images[1:],optimize=True,duration=1000,loop=0)
print("Create Animation")
