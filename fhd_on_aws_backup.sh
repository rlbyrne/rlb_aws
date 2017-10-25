#! /bin/bash

i=0
while true; do

    if [ -z $(curl -Is http://169.254.169.254/latest/meta-data/spot/termination-time | head -1 | grep 404 | cut -d \  -f 2) ]; then
        echo "Spot instance termination notice sent. Preparing to shut down."

        # Copy gridengine stdout to S3
        aws s3 cp ~/grid_out/fhd_job_aws.sh.o${JOB_ID} \
        s3://mwatest/diffuse_survey/fhd_${version}/grid_out/\
        fhd_job_aws.sh.o${JOB_ID}_${myip} --quiet

        # Copy gridengine stderr to S3
        aws s3 cp ~/grid_out/fhd_job_aws.sh.e${JOB_ID} \
        s3://mwatest/diffuse_survey/fhd_${version}/grid_out/\
        fhd_job_aws.sh.e${JOB_ID}_${myip} --quiet

        aws s3 sync ${outdir}/fhd_${version}/ \
        s3://mwatest/diffuse_survey/fhd_${version}/ --quiet

        break
    fi

    if [ $i -eq 720 ]; then # Back up every hour
        echo "Backup to S3: " `date +"%Y-%m-%d_%H-%M-%S"`
        aws s3 sync ${outdir}/fhd_${version}/ \
        s3://mwatest/diffuse_survey/fhd_${version}/ --quiet

        i=0
    fi

    i=$((i+1))
    sleep 5 # Check instance termination status every 5 seconds
done
