#!/bin/bash

######################################################################################
# Top level script to integrate healpix cubes and run power spectrum code.
#
# A file path to the fhd directory is needed.
# 
# A file path to a text file listing observation ids OR preintegrated subcubes is
# needed.
# 
# If a text file of observation ids to be used in integration is specified, the obs 
# ids are assumed to be seperated by newlines.
#
# If a text file of preintegrated subcubes is specified, the format should be
# the name of the save file seperated by newlines.  "even_cube.sav" and "odd_cube.sav"
# is not necessary to include, as both will be used anyways.  The subcubes are
# assumed to be in <fhd_directory>/Healpix/. If elsewhere in the FHD directory, the 
# name of the subcubes must specify this in the text file as Other_than_Healpix/<name>.
#
# Set -ps to 1 to skip integration and make cubes only.
#
# Written by N. Barry 
#
######################################################################################

#Parse flags for inputs
while getopts ":d:f:n:p:h:t:" option
do
   case $option in
        d) FHDdir="$OPTARG";;			#file path to fhd directory with cubes
        f) integrate_list="$OPTARG";;		#txt file of obs ids or subcubes or a single obsid
        n) nslots=$OPTARG;;             	#Number of slots for grid engine
	p) ps_only=$OPTARG;;			#Flag for skipping integration to make PS only
        h) hold=$OPTARG;;                       #Hold for a job to finish before running. Useful when running immediately after firstpass
	i) image_filter=$OPTARG;;               #Apply an image window filter during eppsilon
        \?) echo "Unknown option: Accepted flags are -d (file path to fhd directory with cubes), -f (obs list or subcube path or single obsid), "
	    echo "-n (number of slots), -p (make ps only), "
	    echo "-h (hold int/ps script on a running job id), and -t (apply a window filter during ps),"
            exit 1;;
        :) echo "Missing option argument for input flag"
           exit 1;;
   esac
done

#Manual shift to the next flag
shift $(($OPTIND - 1))

#Throw error if no file path to FHD directory
if [ -z ${FHDdir} ]
then
   echo "Need to specify a file path to a FHD directory with cubes: Example /nfs/complicated_path/fhd_mine/"
   exit 1
fi

#Remove extraneous / on FHD directory if present
if [[ $FHDdir == */ ]]; then FHDdir=${FHDdir%?}; fi

#Error if integrate_list is not set
if [ -z ${integrate_list} ]
then
    echo "Need to specify obs list file path or preintegrated subcubes list file path with option -f"
    exit 1
fi

#Warning if integrate list filename does not exist
if [ ! -e "$integrate_list" ]
then
    echo "Integrate list is either not a file or the file does not exist!"
    echo "Assuming the integrate list is a single observation id."

    if [ -z ${ps_only} ]
    then
        echo "ps_only flag must be set if integrate list is a single observation id. Set -o 1 if desired function"
        exit 1
    fi 
    version=$integrate_list  #Currently assuming that the integrate list is a single obsid
else
    version=$(basename $integrate_list) # get filename
    version="${version%.*}" # strip extension
fi

#Set typical slots needed for standard PS with obs ids if not set.
if [ -z ${nslots} ]; then nslots=10; fi

#Set default to do integration
if [ -z ${ps_only} ]; then ps_only=0; fi

# create hold string
if [ -z ${hold} ]; then hold_str=""; else hold_str="-hold_jid ${hold}"; fi

# create hold string
if [[ -n ${image_filter} ]]; then image_filter="Blackman-Harris"; fi

PSpath='~/MWA/eppsilon/'

#Versions made during integrate list logic check above
echo Version is $version

if [ ! -e "$integrate_list" ]
then
    first_line=$integrate_list
else
    first_line=$(head -n 1 $integrate_list)
fi

first_line_len=$(echo ${#first_line})

rm -f ${FHDdir}/Healpix/${version}_int_chunk*.txt # remove any old chunk files lying around

exit_flag=0

#Check that cubes or integrated cubes are present, print and error if they are not
if [ "$ps_only" -ne "1" ]; then 	#only if we're integrating
while read line
do
   if [ "$first_line_len" == 10 ]; then
      if ! ls $FHDdir/Healpix/$line*cube*.sav &> /dev/null; then
         echo Missing cube for obs $line
	 if [ -z "$hold" ]; then
	    exit_flag=1
	 fi
      fi
   else
      if [[ "$first_line" != */* ]]; then
	 check=$FHDdir/Healpix/$line*.sav
      else
	 check=$FHDdir/$line*.sav
      fi
      if ! ls $check &> /dev/null; then
	 echo Missing save file for $line
	 exit_flag=1
      fi
   fi
done < $integrate_list
fi

if [ "$exit_flag" -eq 1 ]; then exit 1; fi

if [ "$first_line_len" == 10 ]; then
    
    obs=0   

    while read line
    do
        ((chunk=obs/100+1))		#integer division results in chunks labeled 0 (first 100), 1 (second 100), etc
        echo $line >> ${FHDdir}/Healpix/${version}_int_chunk${chunk}.txt	#put that obs id into the right txt file
        ((obs++))			#increment obs for the next run through
    done < $integrate_list
    nchunk=$chunk 			#number of chunks we ended up with

else

    if [[ "$first_line" != */* ]]; then
   
        chunk=0 
        while read line
        do
            echo Healpix/$line >> ${FHDdir}/Healpix/${version}_int_chunk${chunk}.txt        #put that obs id into the right txt file
        done < $integrate_list
        nchunk=$chunk                       #number of chunks we ended up with
    
    else

        chunk=0 
        while read line
        do
            echo $line >> ${FHDdir}/Healpix/${version}_int_chunk${chunk}.txt        #put that obs id into the right txt file
        done < $integrate_list
        nchunk=$chunk                       #number of chunks we ended up with

    fi

fi

unset idlist
if [ "$ps_only" -ne "1" ]; then   
    if [ "$nchunk" -gt "1" ]; then

        # set up files for master integration
        sub_cubes_list=${FHDdir}/Healpix/${version}_sub_cubes.txt
        rm $sub_cubes_list # remove any old lists

        # launch separate chunks
        for chunk in $(seq 1 $nchunk); do
	    chunk_obs_list=${FHDdir}/Healpix/${version}_int_chunk${chunk}.txt
	    outfile=${FHDdir}/Healpix/${version}_int_chunk${chunk}_out.log
	    errfile=${FHDdir}/Healpix/${version}_int_chunk${chunk}_err.log
	    for evenodd in even odd; do
		for pol in XX YY; do 
	    	    message=$(qsub ${hold_str} -l h_vmem=$mem,h_stack=512k,h_rt=$wallclock_time -V -v file_path_cubes=$FHDdir,obs_list_path=$chunk_obs_list,version=$version,chunk=$chunk,nslots=$nslots,legacy=$legacy,evenodd=$evenodd,pol=$pol -e $errfile -o $outfile -pe chost $nslots ${PSpath}ps_wrappers/integrate_job.sh)
	    	    message=($message)
	    	    if [ "$chunk" -eq 1 ] && [[ "$evenodd" = "even" ]] && [[ "$pol" = "XX" ]]; then idlist=${message[2]}; else idlist=${idlist},${message[2]}; fi
		done
	    done
	    echo Combined_obs_${version}_int_chunk${chunk} >> $sub_cubes_list # trick it into finding our sub cubes
        done

        # master integrator
        chunk=0
        outfile=${FHDdir}/Healpix/${version}_int_chunk${chunk}_out.log
        errfile=${FHDdir}/Healpix/${version}_int_chunk${chunk}_err.log
	for evenodd in even odd; do
	    for pol in XX YY; do 
        	message=$(qsub -hold_jid $idlist -l h_vmem=$mem,h_stack=512k,h_rt=$wallclock_time -V -v file_path_cubes=$FHDdir,obs_list_path=$sub_cubes_list,version=$version,chunk=$chunk,nslots=$nslots,legacy=$legacy,evenodd=$evenodd,pol=$pol -e $errfile -o $outfile -pe chost $nslots ${PSpath}ps_wrappers/integrate_job.sh)
        	message=($message)
		if [[ "$evenodd" = "even" ]] && [[ "$pol" = "XX" ]]; then idlist_master=${message[2]}; else idlist_master=${idlist_master},${message[2]}; fi
	    done
	done
	hold_str="-hold_jid ${idlist_master}"

    else

        # Just one integrator
        mv ${FHDdir}/Healpix/${version}_int_chunk1.txt ${FHDdir}/Healpix/${version}_int_chunk0.txt
        chunk=0
        chunk_obs_list=${FHDdir}/Healpix/${version}_int_chunk${chunk}.txt
        outfile=${FHDdir}/Healpix/${version}_int_chunk${chunk}_out.log
        errfile=${FHDdir}/Healpix/${version}_int_chunk${chunk}_err.log
	for evenodd in even odd; do
	    for pol in XX YY; do
        	message=$(qsub ${hold_str} -l h_vmem=$mem,h_stack=512k,h_rt=$wallclock_time -V -v file_path_cubes=$FHDdir,obs_list_path=$chunk_obs_list,version=$version,chunk=$chunk,nslots=$nslots,legacy=$legacy,evenodd=$evenodd,pol=$pol -e $errfile -o $outfile -pe chost $nslots ${PSpath}ps_wrappers/integrate_job.sh)
       		message=($message)
		if [[ "$evenodd" = "even" ]] && [[ "$pol" = "XX" ]]; then idlist_int=${message[2]}; else idlist_int=${idlist_int},${message[2]}; fi
	    done
	done
        hold_str="-hold_jid ${idlist_int}"

    fi
else
    echo "Running only ps code" # Just PS if flag has been set
fi

outfile=${FHDdir}/ps/logs/${version}_ps_out
errfile=${FHDdir}/ps/logs/${version}_ps_err


if [ ! -d ${FHDdir}/ps ]; then
    mkdir ${FHDdir}/ps
fi
if [ ! -d ${FHDdir}/ps/logs ]; then
    mkdir ${FHDdir}/ps/logs
fi

###Polarization definitions
pol_arr=('xx' 'yy')
n_pol=${#pol_arr[@]}

###Evenodd definitions
evenodd_arr=('even' 'odd')
n_evenodd=${#evenodd_arr[@]}

###Cube definitions
cube_type_arr=('weights' 'dirty' 'model')
n_cube=${#cube_type_arr[@]}

hold_str_int=$hold_str
unset id_list

for pol in "${pol_arr[@]}"
do
    for evenodd in "${evenodd_arr[@]}"
    do
        for cube_type in "${cube_type_arr[@]}"
        do
            if [ $cube_type = "weights" ]
            then
                hold_str_temp=$hold_str_int
            else
                hold_str_temp="-hold_jid ${weights_id}"
            fi

            message=$(qsub ${hold_str_temp} -V -b y -cwd -v file_path_cubes=$FHDdir,obs_list_path=$integrate_list,version=$version,nslots=$nslots,cube_type=$cube_type,pol=$pol,evenodd=$evenodd,image_filter_name=$image_filter -e ${errfile}_${pol}_${evenodd}_${cube_type}.log -o ${outfile}_${pol}_${evenodd}_${cube_type}.log -N ${cube_type}_${pol}_${evenodd} -pe smp $nslots -sync y eppsilon_job_aws.sh)
            message=($message)
            id=${message[2]}
            if [ -z "$id_list" ]; then id_list=${message[2]};else id_list=${id_list},${message[2]};fi

            if [ $cube_type = "weights" ]
            then
                weights_id=$id
            fi
        done
    done
done

#final plots
qsub -hold_jid $id_list -V -v file_path_cubes=$FHDdir,obs_list_path=$integrate_list,version=$version,nslots=$nslots,image_filter_name=$image_filter -e ${errfile}_plots.log -o ${outfile}_plots.log -N PS_plots -pe smp $nslots -sync y eppsilon_job_aws.sh
