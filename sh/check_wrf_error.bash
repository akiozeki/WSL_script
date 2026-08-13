##対象のwrfoutファイルを全てncdumpしてエラーを確かめる
cd /home/akioz/MyWRF/WRF4.6.1/run
#cd /home/akioz/MyWRF/output/2025DJF/CTL_lamb2

for f in wrfout_d01*; do
  echo -n "$f:"
  ncdump -h "$f" > /dev/null 2>&1 && echo "OK" || echo "FAILED"
done 
