#coding: UTF-8 
#########################################################################################
# Developer: Deiner Zapata Silva.
# Date: 06/03/2019
# Last update: 05/06/2019
# Description: Codigo para actualizacion de archivo de configuración de heartbeat.yml
#########################################################################################
# Fases del programa.
# 1. Conexion y descarga de la configuracion de ELK
# 2. Construccion de los archivos necesarios de configuraciòn
# 3. Reinicio de los servicios respectivos 
#########################################################################################
import time, sys, os, platform, json
from elastic import elasticsearch
from utils import *
from utils_elk import *
from datetime import datetime
#######################################################################################
CLIENTE = 'YANBAL'
#######################################################################################
class reconfigurate_hearbeat():
    def __init__(self):
        # Windows, linux, win32
        self.s_o = platform.system()
        print("START| {0} reconfigurate_heartbeat | SO {1}".format(datetime.utcnow().isoformat(),self.s_o))
        self.service_bin = "/etc/init.d/heartbeat-elastic"
        self.fullpath_bin = "/usr/share/heartbeat/bin/heartbeat"
        self.fullpath_log = "/var/log/heartbeat"

        if(self.s_o=='Windows'):
            self.fullpath_yml = "heartbeat.yml"
        else:
            self.fullpath_yml = "/etc/heartbeat/heartbeat.yml"
        self.query = {}
        self.elk = elasticsearch()
        return

    def download_configuracion(self,client):
        #client: "AWS", "TASA", "YANBAL"
        self.client = client.lower()
        elk = elasticsearch()
        self.logstash = download_configuration_from_elk(elk)
        URL_FULLPATH = "{0}/index_configuration/_doc/dict_monitoring_{1}".format( elk.get_url_elk() ,  self.client.replace(" ","_") )
        self.dict_client_ip = elk.req_get( URL_FULLPATH )
        save_yml(self.dict_client_ip, nameFile="dict_monitoring_"+self.client.replace(" ","_"))
        print( "|INFO | download_configuration dict_monitoring_"+self.client.replace(" ","_")+".yml")
        if "_source" in self.dict_client_ip:
            self.dict_client_ip = self.dict_client_ip['_source']
            self.dict_client_ip = bucket_to_dictionary(self.dict_client_ip['buckets'])
        else:
            print( "|ERROR| download_configuration <dict_client_ip>=null")
            print_json(self.dict_client_ip)
            self.dict_client_ip = {}
        #print_json(self.dict_client_ip)
        return self.dict_client_ip, self.logstash
    
    def get_logstash_configuration(self, client_json):
        """
        Always have 'key' and 'value' with the respect values.
        client_json = { 'key': 'name_field_key', 'value': 'value_by_the_key' }
        """
        logstash_configuration = {}
        field,value = list(client_json.keys())[0], list(client_json.values())[0]
        for d_json_one_client in self.logstash: 
            if field in d_json_one_client:
                if value == d_json_one_client[field]:
                    logstash_configuration = d_json_one_client
                    break
        #print_json(logstash_configuration)
        return logstash_configuration

    def build_yml(self):
        logstash_configuration = self.get_logstash_configuration({'label': self.client})
        list_client_to_execute = logstash_configuration['list_client_to_execute']
        list_client_to_execute_heartbeat = []
        if 'all' in list_client_to_execute:
            list_client_to_execute_heartbeat = list_client_to_execute['all']
        else:
            print("ERROR | {0} download_configuration | key 'all' don't found in list_client_to_execute.".format(datetime.utcnow().isoformat()))
            sys.exit(0)
        """
        "processors": [
            {"add_host_metadata": '\x7e'},
            {"add_cloud_metadata": '\x7e'}
        ],
        """
        heartbeat_json = {
            "output.logstash": {
                "hosts": [
                    "{0}:{1}".format(logstash_configuration['ip_output_heartbeat'], logstash_configuration['port']['heartbeat'])
                ],
                "worker": 8
            },
            "setup.template.settings": {
                "index.codec": "best_compression",
                "index.number_of_shards": 1
            },
        }
        #-----------------------------------hearbeat.monitors---------------------------------------------"
        list_of_ips = []
        for client in list_client_to_execute_heartbeat:
            try:
                list_ip_by_one_client = self.dict_client_ip[client]
                client_to_monitoring_json = {
                    "type": "icmp",
                    "timeout": logstash_configuration['heartbeat']['timeout'],
                    "schedule": logstash_configuration['heartbeat']['schedule']
                }
                client_to_monitoring_json.update( { "name": client } )
                list_hosts = []
                for ip_port in list_ip_by_one_client:
                    list_hosts.append( ip_port['ip'] )
                client_to_monitoring_json.update( {"hosts":list_hosts} )
                if(len(list_hosts)>0): list_of_ips.append( client_to_monitoring_json )
                print("|INFO | adding   {0}".format( client))
            except:
                print("|WARN |          {0}".format( client))
                pass
        
        heartbeat_json.update( {"heartbeat.monitors": list_of_ips})
        #print_json(heartbeat_json)
        #-------------------------------------------------------------------------------------------------"
        os.system("cd")
        save_yml(heartbeat_json, nameFile=self.fullpath_yml)
        print("INFO | {0} reconfigurate_heartbeat | Created <heartbeat.yml>".format(datetime.utcnow().isoformat()))
        return 
    
    def relaunch_service(self,mode="production"): #mode={"production" , "debug"}
        os.system("cd")
        os.system("{0} stop".format(self.service_bin))
        time.sleep(2)
        if(mode=="debug"):
            print("INFO | {0} reconfigurate_heartbeat | Starting heartbeat mode debug.".format(datetime.utcnow().isoformat()))
            os.system("{0} -c {1} -e".format(self.fullpath_bin, self.fullpath_yml))
        else:#mode="production"
            print("INFO | {0} reconfigurate_heartbeat | Restarting service heartbeat.".format(datetime.utcnow().isoformat()))
            os.system("{0} restart".format(self.service_bin))
        
if __name__ == "__main__":
    hearbeat = reconfigurate_hearbeat()
    hearbeat.download_configuracion(CLIENTE)
    hearbeat.build_yml()
    hearbeat.relaunch_service(mode="production")

