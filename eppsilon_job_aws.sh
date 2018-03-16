#! /bin/bash
#$ -V
#$ -S /bin/bash

#This script is an extra layer between Grid Engine and IDL commands because
#Grid Engine runs best on bash scripts.

#inputs needed: file_path_cubes, obs_list_path, version, nslots
#inputs optional: cube_type, pol, evenodd, image_filter_name

echo JOBID ${JOB_ID}
echo VERSION ${version}
echo "JOB START TIME" `date +"%Y-%m-%d_%H:%M:%S"`
myip="$(dig +short myip.opendns.com @resolver1.opendns.com)"
echo PUBLIC IP ${myip}


input_file=${file_path_cubes}/

#***Create a string of arguements to pass into mit_ps_job given the input
#   into this script
if [[ -z ${cube_type} ]] && [[ -z ${pol} ]] && [[ -z ${evenodd} ]]; then
    if [[ -z ${image_filter_name} ]]; then
	arg_string="${input_file} ${version}"
    else
	arg_string="${input_file} ${version} ${image_filter_name}"
    fi
else
    if [[ ! -z ${cube_type} ]] && [[ ! -z ${pol} ]] && [[ ! -z ${evenodd} ]]; then
	if [[ -z ${image_filter_name} ]]; then
	    arg_string="${input_file} ${version} ${cube_type} ${pol} ${evenodd}"
	else
	    arg_string="${input_file} ${version} ${cube_type} ${pol} ${evenodd} ${image_filter_name}"
	fi
    else
        echo "Need to specify cube_type, pol, and evenodd altogether"
        exit 1
    fi
fi
#***

#create uvfits download location with full permissions
if [ -d /Healpix ]; then
    sudo chmod -R 777 /Healpix
else
    sudo mkdir -m 777 /Healpix
fi

unset exit_flag

####Check for all Healpix cubes
while read obs_id
do
    # Check if the Healpix exists locally; if not, check S3
    if [ ! -f "/Healpix/${obs_id}_${evenodd}_cube${pol^^}.sav" ]; then

        # Check that the Healpix file exists on S3
        healpix_exists=$(aws s3 ls ${file_path_cubes}/Healpix/${obs_id}_${evenodd}_cube${pol^^}.sav)
        if [ -z "$healpix_exists" ]; then
            >&2 echo "ERROR: HEALPix file not found ${obs_id}_${evenodd}_cube${pol^^}.sav"
            exit_flag=1
        fi
    fi
done < $obs_list_path

if [ -z ${exit_flag} ]; then exit 1;fi 
####

####Download Healpix cubes
while read obs_id
do
    # Check if the Healpix exists locally; if not, download it from S3
    if [ ! -f "/Healpix/${obs_id}_${evenodd}_cube${pol^^}.sav" ]; then

        # Download Healpix from S3
        sudo aws s3 cp ${file_path_cubes}/Healpix/${obs_id}_${evenodd}_cube${pol^^}.sav \
        /Healpix/${obs_id}_${evenodd}_cube${pol^^}.sav --quiet

        # Verify that the cubes downloaded correctly
        if [ ! -f "/Healpix/${obs_id}_${evenodd}_cube${pol^^}.sav" ]; then
            >&2 echo "ERROR: downloading cubes from S3 failed"
            echo "Job Failed"
            exit 1
        fi
    fi
done < $obs_list_path
####

idl -IDL_DEVICE ps -IDL_CPU_TPOOL_NTHREADS $nslots -e mit_ps_job -args $arg_string aws || :

if [ $? -eq 0 ]
then
    echo "Integration Job Finished"
    error_mode=0
else
    echo "Job Failed"
    error_mode=1
fi

# Move integration outputs to S3
i=1  #initialize counter
aws s3 mv /Healpix/Combined_obs_${version}_${evenodd}_cube${pol^^}.sav \
${file_path_cubes}/Healpix/Combined_obs_${version}_${evenodd}_cube${pol^^}.sav --quiet
while [ $? -ne 0 ] && [ $i -lt 10 ]; do
    let "i += 1"  #increment counter
    >&2 echo "Moving FHD outputs to S3 failed. Retrying (attempt $i)."
    aws s3 mv /Healpix/Combined_obs_${version}_${evenodd}_cube${pol^^}.sav \
${file_path_cubes}/Healpix/Combined_obs_${version}_${evenodd}_cube${pol^^}.sav --quiet
done

# Remove obsid cubes from the instance
while read obs_id
do
    sudo rm /Healpix/${obs_id}_${evenodd}_cube${pol^^}.sav
done < $obs_list_path

echo "JOB END TIME" `date +"%Y-%m-%d_%H:%M:%S"`
