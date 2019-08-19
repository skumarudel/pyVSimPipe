# Control directory
# .qsub --> qsub script 
# .list --> list of process name and target files
#           for collection. Serialization into JSON?
from os import path,mkdir
import pyVSimPipe
from pyVSimPipe.vOrder import Record, VOrder
from pyVSimPipe.db_source import CSV_source 
from pyVSimPipe.vExecutionChainBuilder import ExecutionChainBuilder
import subprocess
import click
import json
from shutil import copyfile,copytree 
import logging
import json
import sys

# Check python version 
# and get the correct configparser version
if( sys.version_info[0] < 3):
    import ConfigParser as configparser        
else:
    import configparser as configparser  
logger  = logging.getLogger(__name__)

def setup():
    logger.info("Setup run environment")
    file_path = path.dirname(pyVSimPipe.__file__)
    # copy config files
    if(not path.exists("./CARE_config")):
        copytree("{}/share/CARE_config".format(file_path),"./CARE_config") 
    if(not path.exists("./GrOpticsConfig")):
        copytree("{}/share/GrOpticsConfig".format(file_path),"./GrOpticsConfig") 
    if(not path.exists("./data")):
        copytree("{}/share/data".format(file_path),"./data") 
    # copy default order file
    if(not path.exists("./order.csv")):
        copyfile("{}/share/order.csv".format(file_path),"order.csv")

    # copy default config file
    if(not path.exists("./config.ini")):
        copyfile("{}/share/config.ini".format(file_path),"config.ini")
    if(not path.exists("./config_guillimin.ini")):
        copyfile("{}/share/config_guillimin.ini".format(file_path),"config_guillimin.ini")
    # copy example order
    if(not path.exists("order.csv")):
        copyfile("{}/share/order.csv".format(file_path),"order.csv")
    # make .qsub dir
    if(not path.exists(".qsub")):
        mkdir(".qsub")
    elif(not path.isdir(".qsub")):
        raise Exception("Cannot initialize .qsub directory. It is an existed file.") 
    #  in singularity mode also create .qsub/run_script
    if(not path.exists(".qsub/run_script")):
        mkdir(".qsub/run_script")
    elif(not path.isdir(".qsub/run_script")):
        raise Exception("Cannot initialize .qsub/run_script directory. It is an existed file.") 


class LaunchControl:
    def __init__(self,config_file,order_file,
                      shower_inventory=None,
                      vbf_inventory=None,is_singularity=True):
        config_reader = configparser.SafeConfigParser()
        with open(config_file,'r') as f:
            if(sys.version_info[0] < 3):
                config_reader.readfp(f)
            else:
                config_reader.read_file(f)        
        if(is_singularity):
            self.__run_env__         = config_reader._sections['SINGULARITY'] 
        else:
            self.__run_env__         = config_reader._sections['RUN'] 

        self.__qsub_setting__    = config_reader._sections['QSUB'] 
        self.__qsub_setting__['optional_pbs_directive'] = json.loads(self.__qsub_setting__['optional_pbs_directive'])
        ss =  CSV_source(order_file)
        self.__order__      = VOrder(ss) 
        self.__vbf_inventory__  = vbf_inventory 
        self.__shower_inventroy__ = shower_inventory 
        self.__is_singularity__  = is_singularity
        self.__jobs__ = []

        
    def buildMissle(self):
        logger.debug('Building execution chain.')
        builder = ExecutionChainBuilder(self.__order__,self.__run_env__,self.__qsub_setting__,
                                        vbf_inventory=self.__vbf_inventory__,shower_inventory=self.__shower_inventroy__,
                                        is_singularity=self.__is_singularity__)                    
        self.missle = builder.get_execution_chain() 

    def launch(self,dry_run = False):
        logger.debug('Launch!')
        if(self.__is_singularity__):
            logger.debug('Singularity Mode.')
            self.__launch_singularity__(dry_run)
        else:
            logger.debug('Normal Mode.')
            self.__launch__(dry_run) 
        # Write job record to json file
        with open('qsub_record.json',"w") as f:
            f.write(json.dumps([x.get_data_as_dict() for x in self.__jobs__]))         

    def __launch_singularity__(self,dry_run=False):
        jobs = []
        for c in self.missle:
            name = c.get_name()
            with open(".qsub/run_script/{}.container.qsub".format(name),'w') as f:
                f.write(c.get_run_script())   
            with open(".qsub/{}.qsub".format(name),'w') as f:
                f.write(c.get_script(".qsub/run_script/{}.container.qsub".format(name)))
            script_name = ".qsub/{}.qsub".format(name) 
            if(not dry_run):
                process = subprocess.Popen(['sbatch',script_name],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)            
                out = process.stdout.readlines()
                err = process.stderr.readlines()
                for ol in out:
                    jobs.append(JobRecord(ol.decode().strip(),[ee.__exit__ for ee in c.__executions__]))
                    click.secho(ol.decode().strip(),fg='green')
                for el in err:
                    click.secho(el.decode().strip(),fg='red')
        self.__jobs__ = jobs
            
    def __launch__(self,dry_run=False):
        jobs = []
        for c in self.missle:
            name = c.get_name()
            with open(".qsub/{}.qsub".format(name)) as f:
                f.write(c.get_script())
            script_name = ".qsub/{}.qsub".format(name) 
            if(not dry_run):
                process = subprocess.Popen(['sbatch',script_name],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)            
                out = process.stdout.readlines()
                err = process.stderr.readlines()
                for ol in out:
                    jobs.append(JobRecord(ol.decode().strip(),[ee.__exit__ for ee in c.__executions__]))
                    click.secho(ol.decode().strip(),fg='green')
                for el in err:
                    click.secho(el.decode().strip(),fg='red')
        self.__jobs__ = jobs

    def kill(self):
        pass

    def collect(self):
        pass
        # check status: check target files and matcha against results
        # if finish -> unlock
        # and build inventory list 

class JobRecord(Record):
   def __init__(self,qsub_id,exit_files):
       self.qsub_id = qsub_id
       self.exit_files = exit_files

