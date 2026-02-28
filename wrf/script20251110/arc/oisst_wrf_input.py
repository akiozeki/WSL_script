#/DATA/DATA/OISST/Dailyにある年ごとにまとまった日平均SSTデータをWRFの初期値として読める形で保存する
#/DATA/DATA/OISST/WRF_WPSには3時間毎のSSTデータが存在するが日平均データからどのように作られたか不明なため使わない
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from netCDF4 import Dataset

#年と範囲を指定して(月or日)もいいかも

year=2024
print("Set Year",year)

input_dir="/DATA/DATA/OISST/Daily"
output_dir="/DATA/USER/ozeki/MyWRF/input_data/2024"

file=f"{input_dir}/sst.day.mean.{year}.nc"
ds=xr.open_dataset(file)

time_array=ds.time.values
print(time_array)


#時間軸配列をファイル命名に即した形に整形
#上2つの方法は上手くいかない,time_listがdatetime64という数値numpy配列であったことが原因？

#time_label=[s.split("T")[0] for s in time_list]
#[0]は分割したうちの0番目の要素のみ取り出すという意味

#time_label=np.char.split(time_list,"T")
#time_label=[r[0] for r in time_label]

time_label=np.datetime_as_string(time_list,unit="D")

for t in time_array


print(time_label)





ds.close()


print("End Program")
