#!/bin/bash

######################################################################################
# Top level script to check end-product outputs from FHD run.
#
# A file path to the fhd directory is needed.
# 
# A file path to a text file listing observation ids is needed. Obs ids are
# assumed to be seperated by newlines.
# 
# LOG
# Written by Nichole Barry
#
# NOTE 
# print statements must be turned off in idl_startup file (e.g. healpix check)
######################################################################################

#Parse flags for inputs
while getopts ":d:f:e:p:" option
do
   case $option in
        d) FHDdir="$OPTARG";;			      #file path to fhd directory with cubes
        f) integrate_list="$OPTARG";;		#txt file of obs ids or subcubes or a single obsid
        e) evenodd="$OPTARG";;          #OPTIONAL: array of even-odd names
        p) pol="$OPTARG";;              #OPTIONAL: array of pol names
        \?) echo "Unknown option: Accepted flags are -d (file path to fhd directory with cubes), "
            echo "-f (obs list), -e (array of even-odd), -p (array of pol)"
            exit 1;;
        :) echo "Missing option argument for input flag"
           exit 1;;
   esac
done

#Manual shift to the next flag
shift $(($OPTIND - 1))

###########Check inputs
#Throw error if no file path to FHD directory
if [ -z ${FHDdir} ]
then
   echo "Need to specify a file path to a FHD directory with cubes: Example /nfs/complicated_path/fhd_mine/"
   exit 1
fi

#Throw error if file path does not exist
if [ ! -d "$FHDdir" ]
then
   echo "Argument after flag -d is not a real directory. Argument should be the file path to the location of cubes to integrate."
   exit 1

#Error if check_list is not set
if [ -z ${check_list} ]
then
    echo "Need to specify obs list file path with option -f"
    exit 1
fi

#Default evenodd if not set.
if [ -z ${evenodd} ]; then evenodd=(even odd); fi

#Default evenodd if not set.
if [ -z ${pol} ]; then pol=(XX YY); fi
############End of check inputs

n_evenodd=${#evenodd[@]}
n_pol=${#pol[@]}
num_files=$(($n_evenodd * $n_pol))

#Check that all Healpix cubes are present, print if they are not
while read line
do
    unset miss_flag
    if [ "(aws s3 ls -1qd ${FHDdir}/Healpix/${line}*cube*.sav | wc -l)" != $num_files ]
    then
        if [ -z ${miss_flag} ]
        then
            echo Some HEALPix cubes are missing for 
            miss_flag=1
        fi
        echo $line
	  fi
    done
done < $integrate_list
