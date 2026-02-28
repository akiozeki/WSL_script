#!/bin/csh

#アンサンブルの間の処理=>wrfoutファイルの移動やログファイルのコピーのみ行う
#不要ファイルの削除,出力ファイルを任意ディレクトリに移動
set wrf_dir=/DATA/USER/ozeki/MyWRF
echo $wrf_dir
##データの送り先を指定#####
set data_dir=$wrf_dir/output_data/200912low_ensemble/me/n10
###########################
echo Destination of File is $data_dir


cd $wrf_dir/WRF/run
echo cd WRF/run Directory

mv wrfinput_d01 $data_dir
mv wrfbdy_d01 $data_dir 
mv wrfout_d01* $data_dir
mv wrfrst_d01* $data_dir
cp rsl.out.0000 $data_dir
cp rsl.error.0000 $data_dir
