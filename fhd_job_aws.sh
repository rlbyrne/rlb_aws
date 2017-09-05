#! /bin/bash

#############################################################################
#Runs one observation at a time in grid engine.  Second level program for
#running firstpass on AWS machines. First level program is run_fhd_aws.sh
#############################################################################

echo JOBID ${JOB_ID}
echo TASKID ${SGE_TASK_ID}
obs_id=$(pull_args.py $*)
echo OBSID ${obs_id}

# Check if the uvfits file exists locally; if not, download it from S3
if [ ! -f "/uvfits/${obs_id}.uvfits" ]; then

    # Check that the uvfits file exists on S3
    uvfits_exists=$(aws s3 ls s3://mwapublic/uvfits/5.1/${obs_id}.uvfits)
    if [ -z "$uvfits_exists" ]; then
        >&2 echo "ERROR: uvfits file not found"
        echo "Job Failed"
        exit 1
    fi

    # Download uvfits from S3
    sudo aws s3 cp s3://mwapublic/uvfits/5.1/${obs_id}.uvfits \
    /uvfits/${obs_id}.uvfits

    # Verify that the uvfits downloaded correctly
    if [ ! -f "/uvfits/${obs_id}.uvfits" ]; then
        >&2 echo "ERROR: downloading uvfits from S3 failed"
        echo "Job Failed"
        exit 1
    fi
fi

# Check if the metafits file exists locally; if not, download it from S3
if [ ! -f "/uvfits/${obs_id}.metafits" ]; then

    # Check that the metafits file exists on S3
    metafits_exists=$(aws s3 ls s3://mwatest/metafits/5.1/${obs_id}.metafits)
    if [ -z "$metafits_exists" ]; then
        >&2 echo "ERROR: metafits file not found"
        echo "Job Failed"
        exit 1
    fi

    # Download metafits from S3
    sudo aws s3 cp s3://mwatest/metafits/5.1/${obs_id}.metafits \
    /uvfits/${obs_id}.metafits

    # Verify that the metafits downloaded correctly
    if [ ! -f "/uvfits/${obs_id}.metafits" ]; then
        >&2 echo "ERROR: downloading metafits from S3 failed"
        echo "Job Failed"
        exit 1
    fi
fi

# Copy previous runs from S3 (allows FHD to not recalculate everything)
aws s3 cp s3://mwatest/diffuse_survey/fhd_${version}/ \
${outdir}/fhd_${version}/ --recursive --exclude "*" --include "${obs_id}*"

# Run FHD
idl -IDL_DEVICE ps -IDL_CPU_TPOOL_NTHREADS $nslots -e \
eor_firstpass_versions -args $obs_id $outdir $version || :

if [ $? -eq 0 ]
then
    echo "FHD Job Finished"
    error_mode=0
else
    echo "Job Failed"
    error_mode=1
fi

# Move FHD outputs to S3
echo "Copying outputs to s3://mwatest/diffuse_survey/fhd_${version}"
aws s3 mv ${outdir}/fhd_${version}/ \
s3://mwatest/diffuse_survey/fhd_${version}/ --recursive --exclude "*" \
--include "${obs_id}*"
aws s3 mv ${outdir}/fhd_${version}/ \
s3://mwatest/diffuse_survey/fhd_${version}/ --recursive --exclude "*" \
--include "${JOB_ID}*"

exit $error_mode
