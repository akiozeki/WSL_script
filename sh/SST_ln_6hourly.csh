#!/bin/csh
#年,月をまたぐ場合は面倒くさいが書き換えて複数回実行する

set year=2009
set month=12
set startday=13
set endday=31

echo "${year}/${month}/${startday}_${year}/${month}/${endday}"

set i=$startday

while ($i < $endday + 1)
  #頭に0を付す
  set day=`printf "%02d" $i`

#最終日は00UTCだけ使う
  if ($i == $endday) then
   echo "${day}-00"
   ln -sf /DATA/DATA/OISST/WRF_WPS/${year}/SST:${year}-${month}-${day}_00 /DATA/USER/ozeki/MyWRF/WPS
  
  else 
#foreachはコンマじゃなくてスペース区切り注意  
    foreach hour (00 06 12 18)
      echo "${day}-${hour}"
      ln -sf /DATA/DATA/OISST/WRF_WPS/${year}/SST:${year}-${month}-${day}_${hour} /DATA/USER/ozeki/MyWRF/WPS
    end  
  endif

  @ i += 1
end

echo "End Program"

