# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Last update: 09/06/2019
# Description: Funcion para enviar logs a un server remoto: elastic, logstash, etc.
#######################################################################################
import argparse
import sys
import socket
from os.path import basename
from datetime import datetime
from utils import *
from utils_elk import *
from elastic import *
#######################################################################################
class logging_advance(object):
    """# Adapatcion del patron Singleton
    def __new__(cls, new_instance=False):
        if new_instance:
            cls.instance = super(logging_advance, cls).__new__(cls)#Creando instancia
        if not hasattr(cls, 'instance'):#Si no existe el attributo 'instance'
            cls.instance = super(logging_advance, cls).__new__(cls)#Lo creamos
            print("{0}|{1:5s}|{2}|{3}".format(datetime.utcnow().isoformat(), "INFO", cls.__name__, "Instanciando un objeto."))
        return cls.instance
    """
    def __init__(self,_index="debug-python", _type="_doc",service="", send_elk=False, fullpath=None):
        self.elk = elasticsearch()
        self._index = _index
        self._type = _type
        self.URL_API = "{0}/{1}/{2}".format(self.elk.get_url_elk(), _index, _type)
        self.fullpath = fullpath
        self.flagSendELK = send_elk
        if fullpath!=None and len(service)==0:
            print()
            self.service = basename(fullpath)
        elif fullpath==None and len(service)==0:
            self.service = "logging_advance"
        else:
            self.service = service
        return
    
    def set_service(self,service):
        self.service = service
        return
    
    def get_service(self):
        return self.service
    
    def send_to_elk(self, data_json):
        rpt_json = self.elk.req_post(self.URL_API, data=data_json )
        #print_json(rpt_json)
        return
    
    def formatting(self, service, description, tipo_log="INFO", name_function="", data_json={}, print_screen=False):
        timestamp = datetime.utcnow().isoformat()
        debug_json = {
            "@timestamp": timestamp,
            "tipo": tipo_log,
            "description": description,
            "service": service,
            "hostname": socket.gethostname()
        }
        if len(data_json)>0: debug_json.update( {"data_aditional": [data_json]} )
        if len(name_function)>0: 
            debug_json.update( {"name_function": name_function} )
            str_log = "{0}|{1:5s}|{2}|{3}".format( timestamp, tipo_log, name_function, description )
        else:
            str_log = "{0}|{1:5s}|{2}".format( timestamp, tipo_log, description )
        
        if print_screen:
            if len(str_log)>0: print(str_log)
            if len(data_json)>0: print_json(data_json)
        return debug_json
    
    def print_log(self, tipo_log, description, data_json={}, name_function="", send_elk=False):
        debug_json = self.formatting(self.service, description, tipo_log=tipo_log, name_function=name_function, print_screen=True)
        if send_elk or self.flagSendELK: 
            self.send_to_elk(debug_json)
        return debug_json

    def print_info(self, description, data_json={}, name_function="", send_elk=False):
        rpt_json = self.print_log("INFO", description, data_json=data_json, name_function=name_function, send_elk=send_elk)
        return rpt_json
    
    def print_warn(self, description, data_json={}, name_function="", send_elk=False):
        rpt_json = self.print_log("WARN", description, data_json=data_json, name_function=name_function, send_elk=send_elk)
        return rpt_json
    
    def print_debug(self, description, data_json={}, name_function="", send_elk=False):
        rpt_json = self.print_log("DBG", description, data_json=data_json, name_function=name_function, send_elk=send_elk)
        return rpt_json

    def print_error(self, description, data_json={}, name_function="", send_elk=False):
        rpt_json = self.print_log("ERROR", description, data_json=data_json, name_function=name_function, send_elk=send_elk)
        return rpt_json
#######################################################################################
if __name__ == "__main__":
    print("[INFO] Inicio de logging.py")
    x = logging_advance(service="servicio x")
    y = logging_advance(service="servicio y")
    x.print_log("INFO", "Inicio de logging.py",send_elk=True)
    print("x servicio")
    print(x.get_service())
    print("y servicio")
    print(y.get_service())
    pass