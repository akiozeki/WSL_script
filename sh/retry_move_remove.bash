
#!/bin/bash
wrf_dir=/home/akioz/MyWRF
data_dir=$wrf_dir/output/latest_error

if [ ! -d $data_dir ]; then

    mkdir -vp $data_dir

fi

SDATE="2024112012"
EDATE="2024112206"
dh=6  

cd $wrf_dir/WRF4.6.1/run
echo cd WRFrun Directory

rm met_em.d01.*:00:00.nc
rm wrfinput_d01 
rm wrfbdy_d01 
rm wrflowinp_d01 
cp rsl.out.0000 $data_dir
cp rsl.error.0000 $data_dir
cp namelist.input $data_dir

DATE=$SDATE

while [ "$DATE" -le "$EDATE" ]; do
    YYYY=${DATE:0:4}
    MM=${DATE:4:2}
    DD=${DATE:6:2}
    HH=${DATE:8:2}

    echo "Processing: ${YYYY}-${MM}-${DD}_${HH}:00:00"
   
    rm wrfout_d01_${YYYY}-${MM}-${DD}_${HH}:00:00 
    
    rst_file=wrfrst_d01_${YYYY}-${MM}-${DD}_${HH}:00:00
    if [ -f $rst_file ]; then

        rm $rst_file 

    fi

    DATE=$(date -d "${YYYY}-${MM}-${DD} ${HH}:00 ${dh} hour" +%Y%m%d%H)

done


cd $wrf_dir/WPS4.6.0
echo cd WPS Directory

cp geo_em.d01.nc $data_dir
rm GRIBFILE*
cp namelist.wps $data_dir
rm met_em.d01.*:00:00.nc

DATE=$SDATE

while [ "$DATE" -le "$EDATE" ]; do
    YYYY=${DATE:0:4}
    MM=${DATE:4:2}
    DD=${DATE:6:2}
    HH=${DATE:8:2}

    echo "Processing: ${YYYY}-${MM}-${DD}_${HH}:00:00"


    DATE=$(date -d "${YYYY}-${MM}-${DD} ${HH}:00 ${dh} hour" +%Y%m%d%H)

done


echo Destination of File is $data_dir

