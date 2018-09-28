from  pyVSimPipe.db_source import *
from pyVSimPipe.vOrder import *
from pyVSimPipe.vExecutionChain import *
from pyVSimPipe.vExecutionChainBuilder import *
from pyVSimPipe.corsika.vShowerExecution import *
from pyVSimPipe.care.vDetectorExecution import *
from pyVSimPipe.vLaunchControl import setup,LaunchControl
import logging


def test():
    ss = CSV_source("./order.csv")
    order = VOrder(ss)    
    builder = ExecutionChainBuilder(None,None,order) 
    for ind,det in builder.__reduced_order__:
        print(ind)
        for dd in det:
            print(len(str(ind))*' ' + str(dd))  

def test_exe():
    ss = CSV_source("./order.csv")
    order = VOrder(ss)    
    builder = ExecutionChainBuilder(None,None,order,None) 
    ind,det = builder.__reduced_order__[0]   
    run_env = {'scratch_dir':'$LSCRATCH',
               'user':'TLin',
               'host':'guillimin',
               'corsika_bin':'/software/corsika-76400/run/corsika76400Linux_QGSII_urqmd'}
    se = ShowerExecution(ind,run_env)
    print(se.get_script())
    #ec = ExecutionChain(run_env,{}) 

def test_det_exe():
    ss = CSV_source("./order.csv")
    order = VOrder(ss)    
    builder = ExecutionChainBuilder(order,None,None) 
    ind,det = builder.__reduced_order__[0]   
    run_env = {'scratch_dir':'$LSCRATCH',
               'user':'TLin',
               'host':'guillimin',
               'corsika_bin':'/software/corsika-76400/run/corsika76400Linux_QGSII_urqmd',
               'ioreader_bin':'/software/ioreader/ioreader',
               'groptics_bin':'/software/groptics/grOptics',
               'care_bin':'/software/care/care' ,
               'image_file':'test.img'}

    se = ShowerExecution(ind,run_env)

    chain = ExecutionChain(run_env,None)
    chain.add(se)
    for dd in det:
        de = DetectorExecution(ind,dd,run_env)
        chain.add(de)        
    print(chain.get_script())


def test_exe_chain():
    ss = CSV_source("./order.csv")
    order = VOrder(ss)    

    run_env = {'scratch_dir':'$LSCRATCH',
               'user':'TLin',
               'host':'guillimin',
               'corsika_bin':'/software/corsika-76400/run/corsika76400Linux_QGSII_urqmd',
               'ioreader_bin':'/software/ioreader/ioreader',
               'groptics_bin':'/software/groptics/grOptics',
               'care_bin':'/software/care/care', 'image_file':'test.img'}

    
    builder = ExecutionChainBuilder(order,run_env,None,True) 
    chain = builder.get_execution_chain()
    for c in chain:
        print(c.get_script("ici"))

def test_lauch_control():
    config_file = './config.ini'
    order_file  = './order.csv'        
    setup()
    control = LaunchControl(config_file,order_file)
    control.buildMissle()
    control.launch(dry_run=False)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_lauch_control()
