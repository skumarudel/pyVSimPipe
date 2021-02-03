import os
import sys
import logging

logger  = logging.getLogger(__name__)

class OrderRecordComparisionError(Exception):
    pass

class Record:
   def __init__(self):
        pass
   def __eq__(self,other):
      if(isinstance(other, self.__class__)):
        return self.__dict__ == other.__dict__
      else:
        return False
   def __ne__(self, other):
      return not self.__eq__(other)

   def get_data_as_dict(self):
      out = {}
      data = self.__dict__
      for i in data.keys():
        if(isinstance(data[i],Record)):
            out = {**out,**(data[i].get_data_as_dict())}
        else:
            out[i] = data[i] 
      return out

   def __str__(self):
       return self.__class__.__name__ + ':'+ str(self.get_data_as_dict()) 

class VDetectorProperty(Record):
   def __init__(self,order_dict): 
        self.epoch = order_dict['epoch'] 
        self.wobble_dir   = order_dict['wobble_dir'] 
        self.wobble_angle = order_dict['wobble_angle'] 
        self.noise_level  = order_dict['noise_level']

class VShowerProperty(Record):
   def __init__(self,order_dict):
        # Primary can only be gamma, electron, proton, iron
        # at the moment
        self.primary   = order_dict['primary']
        self.atm       = order_dict['atm']
        self.nshower   = order_dict['nshower']
        self.ze        = order_dict['ze']
        self.elow      = order_dict['elow']
        self.ehigh     = order_dict['ehigh']
        self.index     = order_dict['index']
        self.reuse     = order_dict['reuse'] 
        self.seed      = [order_dict['seed0'],order_dict['seed1'],order_dict['seed2'],order_dict['seed3']]
        self.simtype   = order_dict['simtype']
        
class VOrderRecord(Record):
    def __init__(self,order_dict):
        # Shower property
        self.shower_property = VShowerProperty(order_dict) 
        # Detector property 
        self.detector_property = VDetectorProperty(order_dict)
        # Check if all filed in detector property is provided
        if((self.detector_property.epoch is None) or 
           (self.detector_property.wobble_dir is None) or
           (self.detector_property.wobble_angle is None) or
           (self.detector_property.noise_level is None)
          ):
            self.detector_property = None 

    def __eq__(self,other):

      if(isinstance(other, self.__class__)):
        check_content = ((self.shower_property == other.shower_property) and
                       (self.detector_property == other.detector_property) )
        if(check_content  != (self.record_id == other.record_id)):
            raise OrderRecordComparisionError 
      else:
        return False

class VOrder:
    def __init__(self,db_source):
       self.orders = [  VOrderRecord(f) 
                                  for f in db_source.get_dict_list()] 
       self.__validate__()

    def __validate__(self):
        duplicated_id =[]
        different_id_same_content =[]
        for i,rec in enumerate(self.orders):
            if( i == len(self.orders)-1):
                continue
            for check in self.orders[i+1:]:
                content_check = (rec.shower_property == check.shower_property)
                content_check = content_check and (rec.detector_property == check.detector_property)
                if(content_check):
                    raise Exception('Duplicated simulation setting: ({},{})'.format(rec.order_id,check.order_id))
                

