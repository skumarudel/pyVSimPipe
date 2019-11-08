input_file_template='''
RUNNR {runnum:d}
EVTNR 1 
NSHOW {nshower:d} 
PRMPAR {pid:d}
ERANGE {elow_GeV:d} {ehigh_GeV:d} 
ESLOPE -{index:.1f}
THETAP {ze:.1f} {ze:.1f} 
PHIP 0. 360.
SEED {seed:d}  0 0
SEED {seed1:d} 0 0
SEED {seed2:d} 0 0
SEED {seed3:d} 0 0
ATMOD 1
MAGNET 25.2 40.88
ARRANG 10.4
ELMFLG F T
RADNKG 200.E2
FIXCHI 0.
HADFLG 0 0 0 0 0 2
QGSJET T 0
QGSSIG T
HILOW 100.
ECUTS 0.30 0.05 0.02 0.02
MUADDI F
MUMULT T
LONGI T 20. F F
MAXPRT 50
PAROUT F F
ECTMAP 1.E5
DEBUG F 6 F 1000000
DIRECT {outdir}
USER {user} 
HOST {host} 
ATMOSPHERE {atm:d} T
TELFIL {ofname_tmp} 
OBSLEV 1270.E2
TELESCOPE -23.7E2 37.6E2 0.E2 7.E2
TELESCOPE -47.7E2 -44.1E2 4.4E2 7.E2
TELESCOPE 60.1E2 -29.4E2 9.8E2 7.E2
TELESCOPE 11.3E2 35.9E2 7.E2 7.E2
TELESCOPE -8.61E2 -135.48E2 12.23E2 7.E2
CSCAT {reuse:d}  750.E2 0.
CERFIL 0
CERSIZ 5.
CWAVLG 200. 700.
EXIT
'''

script_template='''
corsika_bin={corsika_bin}
input_file={input_file}
log_file={log_file}

local_dir={local_dir}
output_file={exit}

#Create directories

data_dir=$(dirname $output_file)
log_dir=$(dirname $log_file)
input_dir=$(dirname $input_file)

mkdir -p $data_dir
mkdir -p $log_dir
mkdir -p $input_dir
mkdir -p $local_dir

#make local run folder
mkdir -p "$local_dir/$(basename $output_file).run"
output_file_tmp=$local_dir/$(basename $output_file)

# Generate input file
cat > $input_file <<- EOM
{input_file_text}
EOM

check_corsika_file_exist={check_corsika_file_exist}

if [ -f "$output_file" ]; then
    output_file_exist=True
fi 

#cd $(dirname $corsika_bin)
cd "$local_dir/$(basename $output_file).run"

for f in $(dirname $corsika_bin)/*;do
        ln -sT $f $(basename $f)
done

if [ ! "$output_file_exist" = "True" ] || [ "$check_corsika_file_exist" = "False" ];then
    $corsika_bin < $input_file &> $log_file
    # done 
    mv $output_file_tmp $output_file
fi
# remove link for running environment
rm -rf "$local_dir/$(basename $output_file).run"


'''
