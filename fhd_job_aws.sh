#! /bin/bash

#############################################################################
#Runs one observation at a time in grid engine.  Second level program for
#running firstpass on AWS machines. First level program is run_fhd_aws.sh
#############################################################################

echo JOBID ${JOB_ID}
echo TASKID ${SGE_TASK_ID}
obs_id=$(pull_args.py $*)
echo OBSID ${obs_id}

uvfits_loc=$(s3://mwapublic/uvfits/5.1)
metafits_loc=$(s3://mwatest/metafits/5.1)

# Check if the uvfits and metafits files exist on S3; error and exit if they
# are not found
uvfits_exists=$(aws s3 ls ${uvfits_loc}/${obs_id}.uvfits)
if [ -z "$uvfits_exists" ]
then
    >&2 echo "ERROR: uvfits file not found"
    echo "Job Failed"
    exit 1
fi

metafits_exists=$(aws s3 ls ${metafits_loc}/${obs_id}.metafits)
if [ -z "$metafits_exists"]
then
    >&2 echo "ERROR: metafits file not found"
    echo "Job Failed"
    exit 1
fi

# Copy uvfits and metafits files from S3
aws s3 cp ${uvfits_loc}/${obs_id}.uvfits /uvfits
aws s3 cp ${metafits_loc}/${obs_id}.metafits /uvfits

# Verify that uvfits and metafits were successfully copied from S3
if [ ! -f "/uvfits/${obs_id}.uvfits" ]
then
    >&2 echo "ERROR: copying uvfits from S3 failed"
    echo "Job Failed"
    exit 1
fi

if [ ! -f "/uvfits/${obs_id}.metafits" ]
then
    >&2 echo "ERROR: copying metafits from S3 failed"
    echo "Job Failed"
    exit 1
fi

# Run FHD
/usr/local/bin/idl -IDL_DEVICE ps -IDL_CPU_TPOOL_NTHREADS $nslots -e \
eor_firstpass_versions -args $obs_id $outdir $version

# Copy FHD outputs to S3
aws s3 mv ${outdir}/fhd_${version}/ \
s3://mwatest/diffuse_survey/fhd_${version}/ --recursive --exclude "*" \ --include "${obs_id}*"
aws s3 mv ${outdir}/fhd_${version}/ \
s3://mwatest/diffuse_survey/fhd_${version}/ --recursive --exclude "*" \
--include "${JOB_ID}*"

if [ $? -eq 0 ]
then
    echo "Finished"
    exit 0
else
    echo "Job Failed"
    exit 1
fi
