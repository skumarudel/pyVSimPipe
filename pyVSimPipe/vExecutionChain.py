import logging
from os import path
from pyVSimPipe.qsub_template import qsub_header_template 
import json
import hashlib
logger  = logging.getLogger(__name__) 

class Execution:
    def __init__(self,run_env,entry_file,exit_file):
        self.__run_env__ = run_env
        self.__entry__ = entry_file
        self.__exit__  = exit_file 
    def get_script(self):
        raise Exception("Method not implemented") 

class ExecutionChainValidationError(Exception):
    pass

class ExecutionChain(Execution):
    def __init__(self,run_env,qsub_setting):
        super().__init__(run_env,None,None)      
        self.__qsub_setting__ = qsub_setting
        self.__executions__   =[] 

    def get_qsub_header(self):
        qsub_setting = self.__qsub_setting__ 
        extra_qsub_directive  = ""
        for ll in qsub_setting['optional_pbs_directive']:
           extra_qsub_directive = extra_qsub_directive + "#PBS {}\n".format(ll) 
        qsub_header = qsub_header_template.format(nodes=qsub_setting['nodes'],
                                           ppn  =qsub_setting['ppn'],
                                           name =self.get_name(),
                                           optional_pbs_directive=extra_qsub_directive,
                                           qsub_dir=path.realpath("./.qsub"),
                                           init_command = qsub_setting['init_command']) 
        return qsub_header

    def add(self,exe):
        if(len(self.__executions__) > 0):
            if(not ( exe.__entry__ in [x.__exit__ for x in self.__executions__])):
                print(exe.__entry__)
                print(self.__executions__[0].__exit__)
                raise ExecutionChainValidationError('Exist and entry of execution mismatch!')
        self.__executions__.append(exe)

    def get_script(self):
        script_text += self.get_qsub_header()
        for exe in self.__executions__:
            script_text += exe.get_script()
        return script_text         

    def get_name(self):
        name = []
        for exe in self.__executions__:
            name.append(path.basename(exe.__exit__))
        pre_hash_name = '+'.join(name) 
        return hashlib.sha1(pre_hash_name.encode()).hexdigest()         

class SingularityExecutionChain(ExecutionChain):
    def __init__(self,singularity_setting,qsub_setting):
        # Default singularity container run env
        run_env = {'scratch_dir':'/local-scratch/',
                   'user':singularity_setting['user'],
                   'host':singularity_setting['host'],
                   'corsika_bin':'/software/corsika-76400/run/corsika76400Linux_QGSII_urqmd',
                   'ioreader_bin':'/software/corsikaSimulationTools/corsikaIOreader',
                   'groptics_bin':'/software/GrOptics/grOptics',
                   'care_bin':'/software/CARE/CameraAndReadout',
                   'data_dir':'$HOME/'
                  }

        super().__init__(run_env,qsub_setting)
        self.__singularity_setting__ = singularity_setting
        
    def get_run_script(self):
        script_text = '#!/bin/bash\n' 
        script_text +='source /software/root/bin/thisroot.sh\n'
        script_text +='export LD_LIBRARY_PATH=/software/GrOptics/v1.5.0_beta:$LD_LIBRARY_PATH\n'
        for exe in self.__executions__:
            script_text += exe.get_script()
        return script_text         
       
    def get_script(self,run_script_location):
        singularity_setting = self.__singularity_setting__  
        script_text_template="{qsub_header}\n"\
                             "cd {cur_dir}\n"\
                             "{create_local}\n"\
                             "singularity exec -H ./:/home  -B {scratch}:/local-scratch {image_file} /bin/bash {run_script_location}" 
        create_local = 'mkdir -p ./local/\n'
        if(singularity_setting['scratch_dir'] != "None"):
            script_text = script_text_template.format(scratch=singularity_setting['scratch_dir'],
                                                      qsub_header = self.get_qsub_header(),
                                                      image_file  = singularity_setting['image_file'],
                                                      run_script_location = run_script_location,
                                                      cur_dir=path.realpath(path.curdir),
                                                      create_local='') 
        else:
             script_text = script_text_template.format(scratch='./local/',
                                                      qsub_header = self.get_qsub_header(),
                                                      image_file  = singularity_setting['image_file'],
                                                      run_script_location = run_script_location,
                                                      cur_dir=path.realpath(path.curdir),
                                                      create_local=create_local) 
       
        return script_text
                                            
