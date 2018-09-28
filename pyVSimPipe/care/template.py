pilot_file_template='''
  Steering pilot file for GrOptics
VERSION 1.0
6Jan2012

C. Duke
Grinnell College

Only records with an initial "*" are active.

cherenkov photon GRISU-type input file,
same type input file as for grisudet.
FILEIN <filename>
 FILEIN ./Config/photon.cph

camera output root file specification type
      - root file name
      - name for tree containing parameters common to all photons
      - base name for photon trees, one tree per telescope,
        telescope number appended to base name
      - photonDirCosine flag: 0/1, if 1 add dirCosineCamera branches
FILEOUT <root filename> <TreeName> <telBaseTreeName> <photonDirCosBranchFlag>
* FILEOUT photonLocation.root allT T 0

name of grOptics log file, default use cerr (if no asterisk)

number of showers/photons, defaults -1
  NSHOWER <numShowers, <0, no limit>
          <numPhotons, <0, no limit>
* NSHOWER -1 -1

x and y coordinates of the source in the field
of view followed by the source extention radius (all in degrees). The fourth
parameter is the latitude of the observatory in degrees. If the latitude is
set to 90 degrees the source position is given in camera corrdinates. If the
latitude is less than 90 degrees, the source position in x corresponds to an
offset in the east west direction while the y position corresponds to north
south.
Example:
wobble North: WOBBLE 0.0 0.5 0.0 31.675
wobble East : WOBBLE 0.5 0.0 0.0 31.675

* WOBBLE {wobble_north:.1f} {wobble_east:.1f} 0.0 31.675

array configuration file
* ARRAYCONFIG ./GrOpticsConfig/GrOpticsVERITASArrayConfigV6.txt

random number seed for TRandom3: default seed = 0, set by machine clock.
seed must be an unsigned integer
* SEED 0
'''


script_template='''

ioreader_bin={ioreader_bin}
groptics_bin={groptics_bin}
care_bin={care_bin}
corsika_file={corsika_file}
local_dir={local_dir}
GrOpticsConfig={groptics_config}
CARE_Config={care_config}
ATM_data={atm_data}
pilot_file={pilot_file}
season={season}

NOISE={noise:d}
runnum={runnum:d}

name_base={output_file_name_base}
output_dir={output_dir}

log_dir={log_dir}

# set up in local dir

mkdir -p $output_dir
mkdir -p $local_dir 
mkdir -p $log_dir
cd $local_dir
ln -sT $GrOpticsConfig ./GrOpticsConfig
ln -sT $CARE_Config ./CARE_config
ln -sT $ATM_data ./data 

# Generate input file
cat > $pilot_file <<- EOM
{pilot_file_text}
EOM

# Run GrOptics

abs_file="./GrOpticsConfig/Ext_results_VSummer_6_1_6.M5.txt"
if [[ "$season" == "w" ]];then
abs_file="./GrOpticsConfig/Ext_results_VWinter_3_2_6.M5.txt"
fi

$ioreader_bin -queff 0.5 -cors $corsika_file -seed $(date +%s$f) -grisu stdout -abs $abs_file -cfg ./GrOpticsConfig/IOReaderDetectorConfigV6.txt | $groptics_bin -of ./"$name_base".groptics.root  -p $pilot_file   &> $log_dir/"$name_base".groptics.log

$care_bin NSBRATEPERPIXEL "0 $NOISE" --seed $(date +%s$f) --configfile ./CARE_config/CARE_V6_Std.txt --outputfile "$name_base" --inputfile "$name_base".groptics.root --vbfrunnumber $runnum  --writepedestals 1 --notraces &> $log_dir/"$name_base".care.log 

mv "$name_base".vbf $output_dir/ 
unlink ./GrOpticsConfig
unlink ./CARE_config
unlink ./data

rm ./*
 
'''

