import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

point="omaezaki"
date="20250905"

csv_dir="/home/akioz/data/csv"
file1=f"{csv_dir}/amedas_{point}{date}.csv"
#df1_onheader=pd.read_csv(file1)
df1=pd.read_csv(file1,skiprows=2)
#print(df1)

time=df1["時分"].to_numpy()
time = pd.to_datetime(df1["時分"],format="%H:%M")
print(time)

#wind_speed1=df1["平均風速(m/s)"].to_numpy()
wind_speed1=df1["最大風速(m/s)"].to_numpy()
print(wind_speed1)
wind_direction1=df1["最大風向(度)"].to_numpy()


fig=plt.figure(figsize=[12,6])
ax1=plt.axes()
fig.autofmt_xdate(rotation=0,ha="center")


ax1.set_xlabel("Time",fontsize=18)
ax1.set_ylabel("Max Wind Speed (m/s)",fontsize=18)
#ax.set_ylabel("Mean Wind Speed (m/s)")

#軸目盛の手動設定
formatter=mdates.DateFormatter("%H")
ax1.xaxis.set_major_formatter(formatter)

ax1.tick_params(axis='x',labelsize=16)  # X軸目盛りフォントサイズ
ax1.tick_params(axis='y',labelsize=16)  # Y軸目盛りフォントサイズ

ax1.set_title("Omaezaki2025/09/05",fontsize="18")

plt.tight_layout()

ax1.plot(time,wind_speed1,linewidth=3,color="red")

ax2=ax1.twinx()
ax2.set_ylabel("Max Wind Direction",fontsize=18)
ax2.tick_params(axis='y',labelsize=16)
ax2.scatter(time,wind_direction1,color="green")

plt.tight_layout()
fig_dir="/home/akioz/fig/makinohara_tornado"
plt.savefig(f"{fig_dir}/Wind_amedas_omaezaki.png")
plt.show()