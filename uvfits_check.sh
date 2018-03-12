#!/bin/bash

######################################################################################
# Top level script to check uvfits and metafits
#
# A file path to a text file listing observation ids is needed. Obs ids are
# assumed to be seperated by newlines.
# 
# Written by Nichole Barry
#
# NOTE 
# print statements must be turned off in idl_startup file (e.g. healpix check)
######################################################################################

#Parse flags for inputs
while getopts ":f:u:m:" option
do
   case $option in
        f) check_list="$OPTARG";;		#txt file of obs ids or subcubes or a single obsid
        u) s3_uvfits="$OPTARG";;			      #OPTIONAL: file path to uvfits directory
        m) s3_metafits="$OPTARG";;          #OPTIONAL: file path to metafits directory
        \?) echo "Unknown option: Accepted flags are "
            echo "-f (obs list), -u (uvfits loc), -m (metafits loc)"
            exit 1;;
        :) echo "Missing option argument for input flag"
           exit 1;;
   esac
done

#Manual shift to the next flag
shift $(($OPTIND - 1))

###########Check inputs
#Error if check_list is not set
if [ -z ${check_list} ]
then
    echo "Need to specify obs list file path with option -f"
    exit 1
fi

#Default s3_uvfits directory
if [ -z ${s3_uvfits} ]
then
   s3_uvfits=s3://mwapublic/uvfits/4.1
fi

#Remove extraneous / on s3_uvfits if present
if [[ $s3_uvfits == */ ]]
then 
   s3_uvfits=${s3_uvfits%?}
fi

#Default s3_metafits directory
if [ -z ${s3_metafits} ]
then
   s3_metafits=s3://mwatest/metafits/4.1
fi

#Remove extraneous / on s3_metafits if present
if [[ $s3_metafits == */ ]]
then 
   s3_metafits=${s3_metafits%?}
fi
############End of check inputs

#aws s3 ls command cannot use wildcards, hence this workaround  - 3/2018
ls_output_filename_uvfits=( $(aws s3 ls ${s3_uvfits}/ | tr -s ' ' | cut -d' ' -f4) )
ls_output_filename_metafits=( $(aws s3 ls ${s3_metafits}/ | tr -s ' ' | cut -d' ' -f4) )

#Check that all uvfits are present, print if they are not
unset miss_flag
while read line
do
    if [[ "$(grep -o $line <<< ${ls_output_filename_uvfits[*]} | wc -l)" -eq 0 ]]
    then
        if [ -z ${miss_flag} ]
        then
            echo Some uvfits are missing:
            miss_flag=1
        fi
        echo $line
    fi
done < $check_list

#Check that all metafits are present, print if they are not
unset miss_flag
while read line
do
    if [[ "$(grep -o $line <<< ${ls_output_filename_metafits[*]} | wc -l)" -eq 0 ]]
    then
        if [ -z ${miss_flag} ]
        then
            echo Some metafits are missing:
            miss_flag=1
        fi
        echo $line
    fi
done < $check_list
