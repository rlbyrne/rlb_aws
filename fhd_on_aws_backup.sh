#! /bin/bash

outdir=$1
version=$2

while true; do
    sleep 3600 #backup every hour
    echo "Backup to S3: " `date +"%Y-%m-%d_%H-%M-%S"`
    aws s3 sync ${outdir}/fhd_${version}/ \
    s3://mwatest/diffuse_survey/fhd_${version}/ >/dev/null
done
