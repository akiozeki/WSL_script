#!/bin/csh

#namelist,geogrid,ungribを再度行わない場合(地形改変など)
#不要ファイルの削除,出力ファイルを任意ディレクトリに移動
set wrf_dir=/DATA/USER/ozeki/MyWRF
echo $wrf_dir
##データの送り先を指定#####
set data_dir=$wrf_dir/output_data/200912low_ensemble/me/n1
###########################
echo Destination of File is $data_dir

cd $wrf_dir/WPS
echo cd WPS Directory

rm -f met_em.d01.*.nc


cd $wrf_dir/WRF/run
echo cd WRF/run Directory

rm -f met_em.d01*.nc
mv wrfinput_d01 $data_dir
mv wrfbdy_d01 $data_dir 
mv wrfout_d01* $data_dir
mv wrfrst_d01* $data_dir
cp rsl.out.0000 $data_dir
cp rsl.error.0000 $data_dir
