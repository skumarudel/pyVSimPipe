from pyVSimPipe.vExecutionChain import Execution
from pyVSimPipe.corsika.template import script_template,input_file_template
from os import path

particle_code={'gamma':1,'electron':3,'proton':14,'helium':402}

class ShowerExecution(Execution):
    def __init__(self,shower_property,
                      run_env):
       output_file_name_template = 'corsika_{simtype}_{primary}_ATM{atm}_Ze{ze}_elow{elow}TeV_ehigh{ehigh}TeV_index{index}_nshower{nshower:d}_reuse{reuse:d}_seed0_{s0}_seed1_{s1}_seed2_{s2}_seed3_{s3}'
       ofname = output_file_name_template.format(atm=shower_property.atm,
                                                 primary=shower_property.primary,
                                                 ze =shower_property.ze,
                                                 elow =shower_property.elow,
                                                 ehigh=shower_property.ehigh,
                                                 index=shower_property.index,
                                                 reuse=shower_property.reuse,
                                                 nshower=shower_property.nshower,
                                                 simtype=shower_property.simtype,
                                                 s0=shower_property.seed[0],
                                                 s1=shower_property.seed[1],
                                                 s2=shower_property.seed[2],
                                                 s3=shower_property.seed[3])
       if (run_env['data_dir']  == 'None'):
           data_dir = path.realpath(path.curdir)
       else:
           data_dir = run_env['data_dir'] 
       exit='{data_dir}/Shower/ATM{atm}/{simtype}/Ze_{ze}/{fname}.tel'.format(atm=shower_property.atm,
                                                                    ze=shower_property.ze,
                                                                    fname=ofname,
                                                                    simtype=shower_property.simtype,
                                                                    data_dir = data_dir)
       self.__shower_property__  = shower_property
       self.__ofname_base__ = ofname
       super().__init__(run_env,None,exit) 

    def get_script(self):
        run_env = self.__run_env__
        if (run_env['data_dir']  == 'None'):
            data_dir = path.realpath(path.curdir)
        else:
            data_dir = run_env['data_dir'] 

        sp = self.__shower_property__
        # initialize directory path name
        if(run_env['scratch_dir'] != "None"):
            local_dir='{scratch_dir}/Shower/ATM{atm}/{simtype}/Ze_{ze}/'.format(atm=sp.atm,
                                                                                simtype=sp.simtype,
                                                                      ze=sp.ze,
                                                                      scratch_dir=run_env['scratch_dir'])  
        else:
            local_dir='{scratch_dir}/Shower/ATM{atm}/{simptype}/Ze_{ze}/'.format(atm=sp.atm,
                                                                                 simtype=sp.simtype,
                                                                      ze=sp.ze,
                                                                      scratch_dir='{}/local/'.format(data_dir))  

                                        
        input_file_path=path.dirname(self.__exit__)
        log_dir='{data_dir}/log/Shower/ATM{atm}/{simtype}/Ze_{ze}/'.format(atm=sp.atm,
                                                                           simtype=sp.simtype,
                                                                 ze=sp.ze,
                                                                 data_dir=data_dir)    
        # Generate input file text
        primary_code = particle_code[sp.primary]
        runnum=int('{:<05d}'.format(primary_code))        
        input_file_text = input_file_template.format(runnum=runnum,
                                                nshower=sp.nshower,
                                                pid=primary_code,
                                                elow_GeV=int(sp.elow*1000),
                                                ehigh_GeV=int(sp.ehigh*1000),
                                                index=sp.index,
                                                ze=sp.ze,
                                                seed=sp.seed[0],
                                                seed1=sp.seed[1],
                                                seed2=sp.seed[2],
                                                seed3=sp.seed[3],
                                                host=run_env['host'],
                                                user=run_env['user'],
                                                simtype=5. if sp.simtype == 'diffuse' else 0.,
                                                atm=sp.atm,
                                                reuse=sp.reuse,    
                                                ofname_tmp='{}/{}.tel'.format(local_dir,self.__ofname_base__),
                                                outdir='{}/'.format(path.dirname(self.__exit__))
                                               )         
        script = script_template.format(corsika_bin = run_env['corsika_bin'], 
                                        input_file='{}/{}.input'.format(input_file_path,self.__ofname_base__),
                                        log_file='{}/{}.input'.format(log_dir,self.__ofname_base__),
                                        local_dir=local_dir,
                                        exit=self.__exit__,
                                        input_file_text=input_file_text,
                                        check_corsika_file_exist=run_env['check_corsika_file_exist'])
        return script 
