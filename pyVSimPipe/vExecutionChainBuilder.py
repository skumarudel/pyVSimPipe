from pyVSimPipe.corsika.vShowerExecution import ShowerExecution 
from pyVSimPipe.care.vDetectorExecution import DetectorExecution 
from pyVSimPipe.vExecutionChain import ExecutionChain,SingularityExecutionChain 
import logging
logger=logging.getLogger(__name__) 
# 1. ExecutionChain builder
#   - consolidate orders
#   - check with inventory for existing files
#   - generate execution chain

class ExecutionChainBuilder:
    def __init__(self,order,run_env,qsub_setting,
                      is_singularity=False,vbf_inventory = None,
                      shower_inventory=None):
        self.__execution_chain__ = []
        self.__raw_order__ = order
        self.__qsub_setting__ = qsub_setting
        self.__shower_inventory__ = shower_inventory
        self.__vbf_inventory__  = vbf_inventory
        self.__is_singularity__ = is_singularity
        self.__run_env__ = run_env
        self.__reduce__()
        self.__build__()

    def __reduce__(self):
        orders = self.__raw_order__
        reduced_order_tuple = [] 
        for item in orders.orders:
            reduced_order_tuple = self.__add_order_to_dict__(item,reduced_order_tuple)
        self.__reduced_order__ = reduced_order_tuple
        
    def __build__(self):
        # Compare reduced order to existing inventory
        global_run_env = self.__run_env__
        qsub_setting = self.__qsub_setting__
        for sp,dp_s in self.__reduced_order__:
            # Check for existed VBF files 
            if(self.__vbf_inventory__ is not None):
                dp_to_be_run = [dp for dp in dp_s if self.__vbf_inventory__.GetMatchedProperty(sp,dp) is None]
            else:
                dp_to_be_run = dp_s
            # Now check for existed tel files
            if(self.__shower_inventory__ is not None):
                matched_record = self.__shower_inventory__.GetMatchedProperty(sp)
            else:
                matched_record = None
            if(self.__is_singularity__):
                logger.debug("Build singularity execution chain.")
                chain = SingularityExecutionChain(global_run_env,qsub_setting) 
            else:
                logger.debug("Build normal execution chain.")
                chain = ExecutionChain(global_run_env,qsub_setting) 
            run_env = chain.__run_env__
            if(matched_record is None):
                se = ShowerExecution(sp,run_env)             
                chain.add(se)
                for dp in dp_to_be_run:
                    de = DetectorExecution(sp,dp,run_env)                        
                    chain.add(de)
            else:
                 for dp in dp_to_be_run:
                    de = DetectorExecution(sp,dp,run_env,existed_entry=matched_record.file_location.file_location)                       
                    chain.add(de)
            self.__execution_chain__.append(chain)               

    @staticmethod
    def __add_order_to_dict__(item,order_tuple):
        # loop through each shower property
        # put under the same key if shower property is the same
        found_key = False
        for i,k in enumerate(map(lambda x:x[0],order_tuple)):
            if(k == item.shower_property):
                found_key = True
                order_tuple[i][1].append(item.detector_property)   
                break
        if(not found_key):
            order_tuple.append((item.shower_property,[item.detector_property])) 
        return order_tuple  

    def get_execution_chain(self):
        return self.__execution_chain__


