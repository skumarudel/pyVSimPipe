from pyVSimPipe.vOrder import VShowerProperty,VDetectorProperty,Record
from pyVSimPipe.db_source import CSV_source 
import logging

class VFileLocationRecord(Record):
    def __init__(self,inventory_dict):
       self.host          = inventory_dict['host']
       self.file_location =  inventory_dict['file_location']
       # sha hash of the file
       self.file_hash     = inventory_dict['file_hash']

    def __eq__(self,other):
       if(isinstance(other, self.__class__)):
         if( (self.host == other.host) and (self.file_location == other.file_location)
            and (self.file_hash != other.file_hash)):
            raise Exception("Same file different hash value")
         return self.__dict__ == other.__dict__
       else:
         return False   
    

class VShowerInvertoryRecord(Record):
    def __init__(self,inventory_dict):
        self.order_id =      inventory_dict['order_id']
        self.shower_property = VShowerProperty(inventory_dict) 
        self.file_location   = VFileLocationRecord(inventory_dict)

class VVBFInvertoryRecord(Record):
    def __init__(self,inventory_dict):
        self.order_id =      inventory_dict['order_id']
        self.shower_property = VShowerProperty(inventory_dict) 
        self.dector_property = VDetectorProperty(inventory_dict)
        self.file_location   = VFileLocationRecord(inventory_dict)


class VInventory:
    def __init__(self,db_source,inventory_type):
       if(inventory_type == 'Shower'):
           self.inventory = [ VShowerInvertoryRecord(f) 
                                  for f in db_source.get_dict_list()] 
       elif(inventory_type == 'VBF'):
           self.inventory = [ VVBFInvertoryRecord(f) 
                                  for f in db_source.get_dict_list()] 
       else:
           raise Exception('Unsupported inventory type: {}'.format(inventory_type))  
       self.inventory_type = inventory_type
       self.__validate__()

    def __validate__(self):
        duplicated_id =[]
        different_id_same_content =[]
        for i,rec in enumerate(self.inventory):
            if( i == len(self.inventory)-1):
                continue
            for check in self.inventory[i+1:]:
                id_check = (rec.order_id == check.order_id)
                content_check = (rec.shower_property == check.shower_property)
                if(self.inventory_type == 'VBF'):
                    content_check = content_check and (rec.dector_property == check.dector_property)
                # File check 
                file_check = rec.file_location == check.file_location
                if(id_check):
                    raise Exception('Duplicate ID: {}'.format(rec.order_id))
                if(content_check):
                    raise Exception('Duplicated simulation setting: ({},{})'.format(rec.order_id,check.order_id))
                if(file_check):
                    raise Exception('Duplicated file location: ({},{})'.format(rec.order_id,check.order_id))
                
    def GetMatchedProperty(self,sp,dp=None):
        matched = []
        if(self.inventory_type == 'Shower'):
            for rec in self.inventory:
                if(rec.shower_property == sp):
                    matched.append(rec)
        else:
            for rec in self.inventory:
                if(rec.shower_property == sp and
                   rec.detector_property == dp):
                    matched.append(rec)

        if(len(matched) == 0):
            return None
        elif(len(matched) == 1):
            return matched[0]
        else:
            return matched            

