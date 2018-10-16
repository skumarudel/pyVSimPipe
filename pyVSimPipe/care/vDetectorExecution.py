from pyVSimPipe.vExecutionChain import Execution
from pyVSimPipe.corsika.vShowerExecution import particle_code
from pyVSimPipe.care.template import *
from os import path


class DetectorExecution(Execution):
    def __init__(self,shower_property,detector_property,
                      run_env,existed_entry=None):
       input_file_name_template = 'corsika_{primary}_ATM{atm}_Ze{ze}_elow{elow}TeV_ehigh{ehigh}TeV_index{index}_nshower{nshower:d}_reuse{reuse:d}_seed0_{s0}_seed1_{s1}_seed2_{s2}_seed3_{s3}'
       ifname = input_file_name_template.format(atm=shower_property.atm,
                                                 primary=shower_property.primary,
                                                 ze =shower_property.ze,
                                                 elow =shower_property.elow,
                                                 ehigh=shower_property.ehigh,
                                                 index=shower_property.index,
                                                 nshower=shower_property.nshower,
                                                 reuse=shower_property.reuse,
                                                 s0=shower_property.seed[0],
                                                 s1=shower_property.seed[1],
                                                 s2=shower_property.seed[2],
                                                 s3=shower_property.seed[3])

       if (run_env['data_dir']  == 'None'):
           data_dir = path.realpath(path.curdir)
       else:
           data_dir = run_env['data_dir']
       if(existed_entry is None):
           entry='{data_dir}/Shower/ATM{atm}/Ze_{ze}/{fname}.tel'.format(atm=shower_property.atm,
                                                                            ze=shower_property.ze,
                                                                            fname=ifname,
                                                                            data_dir=data_dir)
       else:
           entry = existed_entry 

       output_file_name_template='CARE_{primary}_{epoch}_ATM{atm}_Ze{ze}_elow{elow}TeV_ehigh{ehigh}TeV_index{index}_nshower{nshower:d}_reuse{reuse:d}_seed0_{s0}_seed1_{s1}_seed2_{s2}_seed3_{s3}_Wobble_{wobble_angle:.1f}{wobble_dir}_Noise_{noise_level:03d}MHz.vbf' 
       ofname = output_file_name_template.format(atm=shower_property.atm,
                                                 primary=shower_property.primary,
                                                 ze =shower_property.ze,
                                                 elow =shower_property.elow,
                                                 ehigh=shower_property.ehigh,
                                                 index=shower_property.index,
                                                 nshower=shower_property.nshower,
                                                 reuse=shower_property.reuse,
                                                 s0=shower_property.seed[0],
                                                 s1=shower_property.seed[1],
                                                 s2=shower_property.seed[2],
                                                 s3=shower_property.seed[3],
                                                 wobble_angle=detector_property.wobble_angle,
                                                 wobble_dir=detector_property.wobble_dir,
                                                 noise_level=detector_property.noise_level,
                                                 epoch=detector_property.epoch)
       exit = '{data_dir}/CARE/{epoch}/ATM{atm}/{fname}'.format(epoch=detector_property.epoch,
                                                               atm=shower_property.atm,
                                                               fname=ofname,
                                                               data_dir=data_dir) 
       super().__init__(run_env,entry,exit) 
       self.shower_property   = shower_property
       self.detector_property = detector_property

    def get_script(self):
        # generate wobble number
        dp = self.detector_property 
        sp = self.shower_property  
        wobble_sign = {'n':(0,1,0),
                       's':(0,-1,0),
                       'e':(1,0,0),
                       'w':(-1,0,0),
                       'd':(0,0,1)}

        wn,we,de = wobble_sign[dp.wobble_dir.strip().lower()]
        wobble_north = wn*dp.wobble_angle     
        wobble_east  = we*dp.wobble_angle     
        diffuse_ext  = de*dp.wobble_angle 
        pilot_file_text = pilot_file_template.format(wobble_north=wobble_north,
                                                wobble_east=wobble_east,diffuse_ext=diffuse_ext) 
        run_env = self.__run_env__
        if (run_env['data_dir']  == 'None'):
            data_dir = path.realpath(path.curdir)
        else:
            data_dir = run_env['data_dir']
        ioreader_bin = run_env['ioreader_bin']
        groptics_bin = run_env['groptics_bin']   
        care_bin     = run_env['care_bin']
        if(run_env['scratch_dir'] !="None"):
            local_dir='{scratch_dir}/CARE/ATM{atm}/Ze_{ze}/'.format(atm=sp.atm,
                                                                      ze=sp.ze,
                                                                      scratch_dir=run_env['scratch_dir'])
        else:
            local_dir='{scratch_dir}/CARE/ATM{atm}/Ze_{ze}/'.format(atm=sp.atm,
                                                                      ze=sp.ze,
                                                                      scratch_dir='{}/local/'.format(data_dir))

        log_dir='{data_dir}/log/CARE/ATM{atm}/Ze_{ze}/'.format(atm=sp.atm,
                                                                 ze=sp.ze,
                                                                 data_dir=data_dir)
        if(sp.atm == 61):
            season       =  'w'
        elif(sp.atm == 62):
            season = 's'
        else:
            raise Exception('ATM code {:d} is not supported'.format(season)) 
        noise = int(dp.noise_level)
        output_dir = path.dirname(self.__exit__)
        primary_code = particle_code[sp.primary]
        runnum=int('{:<05d}'.format(primary_code))
        output_file_name_base, extname= path.splitext(path.basename(self.__exit__)) 
        script = script_template.format(ioreader_bin = ioreader_bin,
                                        groptics_bin = groptics_bin,
                                        care_bin = care_bin,
                                        corsika_file = self.__entry__,
                                        local_dir = local_dir,
                                        groptics_config='{}/GrOpticsConfig'.format(data_dir),
                                        care_config='{}/CARE_config'.format(data_dir),
                                        atm_data='{}/data'.format(data_dir),
                                        pilot_file='{}/{}.plt'.format(local_dir,output_file_name_base),
                                        season=season,
                                        noise=noise,
                                        runnum=runnum,
                                        output_dir=output_dir,
                                        log_dir=log_dir,
                                        output_file_name_base= output_file_name_base, 
                                        pilot_file_text=pilot_file_text
                                        )
        return script 
