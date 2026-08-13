
#!/bin/bash
wrf_dir=/home/akioz/MyWRF
data_dir=$wrf_dir/output/2025DJF/ME00_lamb

if [ ! -d $data_dir ]; then

    mkdir -vp $data_dir

fi

SDATE="2024112012"
EDATE="2025030406"
dh=6  

cd $wrf_dir/WRF4.6.1/run
echo cd WRFrun Directory

mv wrfinput_d01 $data_dir
mv wrfbdy_d01 $data_dir
mv wrflowinp_d01 $data_dir
cp namelist.input $data_dir
cp rsl.out.0000 $data_dir
cp rsl.error.0000 $data_dir

DATE=$SDATE

while [ "$DATE" -le "$EDATE" ]; do
    YYYY=${DATE:0:4}
    MM=${DATE:4:2}
    DD=${DATE:6:2}
    HH=${DATE:8:2}

    echo "Processing: ${YYYY}-${MM}-${DD}_${HH}:00:00"
   
    rm met_em.d01.${YYYY}-${MM}-${DD}_${HH}:00:00.nc
    mv wrfout_d01_${YYYY}-${MM}-${DD}_${HH}:00:00 $data_dir
    
    rst_file=wrfrst_d01_${YYYY}-${MM}-${DD}_${HH}:00:00
    if [ -f $rst_file ]; then

        mv $rst_file $data_dir

    fi

    DATE=$(date -d "${YYYY}-${MM}-${DD} ${HH}:00 ${dh} hour" +%Y%m%d%H)

done


cd $wrf_dir/WPS4.6.0
echo cd WPS Directory

rm geo_em.d01.nc
rm GRIBFILE*
cp namelist.wps $data_dir

DATE=$SDATE

while [ "$DATE" -le "$EDATE" ]; do
    YYYY=${DATE:0:4}
    MM=${DATE:4:2}
    DD=${DATE:6:2}
    HH=${DATE:8:2}

    echo "Processing: ${YYYY}-${MM}-${DD}_${HH}:00:00"

    rm met_em.d01.${YYYY}-${MM}-${DD}_${HH}:00:00.nc
    rm fnl_${YYYY}${MM}${DD}_${HH}_00.grib2
    rm FILE:${YYYY}-${MM}-${DD}_${HH}
    rm SST:${YYYY}-${MM}-${DD}_${HH}

    DATE=$(date -d "${YYYY}-${MM}-${DD} ${HH}:00 ${dh} hour" +%Y%m%d%H)

done


echo Destination of File is $data_dir

