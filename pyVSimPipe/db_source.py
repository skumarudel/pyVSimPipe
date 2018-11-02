import pandas as pd


class DB_source:
    def __init__(self):
        self.__dict_list__  = None 
    
    def get_dict_list(self):
        if(self.__dict_list__ is not None):
            return self.__dict_list__ 
        else:
            raise Exception("Dictionary list not created") 
class CSV_source(DB_source):
    def __init__(self,fname):
        dtype={'wobble_angle':float,'noise_level':float}
        table = pd.read_csv(fname,converters={'epoch': str.strip,'wobble_dir':str.strip},dtype=dtype,na_values='nan')      
        self.__dict_list__ = [r.to_dict() for i,r in table.iterrows()]
    

