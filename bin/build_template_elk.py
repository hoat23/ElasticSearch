#coding: UTF-8 
#########################################################################################
# Developer: Deiner Zapata Silva.
# Date: 02/05/2019
# Last update: 19/05/2019
# Description: Builder of templates
#########################################################################################
# Fases del programa.
# 1. Carga un archivo con el nombre del campo y el tipo de dato a ser cargado
# 2. Construccion del template 
# 3. Carga del template a elasticsearch
#########################################################################################
import sys, requests, json
from datetime import datetime, timedelta
import time
from credentials import * #URL="<elastic>" #USER="usr_elk"  #PASS="pass_elk"
from utils import *
from elastic import *
#########################################################################################
class builder_template():
    def __init__(self):
        self.dict_types = {}
        self.fullPath = "log_reference.txt"
        self.coding ='utf-8'
        self.elk = elasticsearch()
        self.tmpl_base = {
            "order": 0,
            "aliases": {},
            "settings": {},
            "mappings" : {
                "doc" : {
                    "dynamic_templates" : [
                    {
                        "undefined_string_fields" : {
                        "mapping" : {"type" : "keyword"},
                        "match_mapping_type" : "string"
                        }
                    },
                    {
                        "no_doc_values" : {
                        "mapping" : { "type" : "{dynamic_type}"},
                        "match_mapping_type" : "*"
                        }
                    }
                    ],
                    "properties" : {
                    "@timestamp" : {"type" : "date"},#fecha del firewall
                    "@version" : {"type" : "integer"},
                    
                    "elk":{
                        "properties": {
                        "logstash": {"type": "keyword"},
                        "index": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "received_at": {"type": "date"} #fecha de elastic
                        }
                    },
                    "cmdb_json" : {
                        "properties" : {
                        "client" : {"type" : "keyword"},
                        "cluster_name" : {"type" : "keyword"},
                        "devip" : {
                            "type" : "ip",
                            "fields" : {"keyword" : {"type" : "keyword"}}
                        },
                        "hash" : {"type" : "keyword"},
                        "model" : {"type" : "keyword"},
                        "sede" : {"type" : "keyword"},
                        "type_device" : {"type" : "keyword"},
                        "wan_group" : {"type" : "keyword"}
                        }
                    },
                    "message": {"type": "keyword"}
                    }
                }
            },
        }
        return
    
    def read_file_with_types(self,fullPath, coding="ISO-8859-1"):
        cont = critical_err = 0
        input_file = open(fullPath,'rb')
        print("[{0} | INFO | read_file_with_types".format(datetime.utcnow().isoformat() ) )
        self.dict_types = {}
        while(1):
            cont = cont + 1 
            try:
                line = input_file.readline()
                line = line.decode(coding).replace("\r\n","")
                line_list = line.split(" ")
                #print("[{0}]".format(line))
                if(len(line)==0):
                    critical_err+=4
                try:
                    self.dict_types.update( { line_list[0] : line_list[1] } )
                    if line_list[0]=="tring":
                        print("cont   " + str(cont))
                except:
                    #print("[{0} | ERROR1| {1} ]".format(datetime.utcnow().isoformat(), line) )    
                    pass
            except:
                #print("[{0} | ERROR2| {1} ]".format(datetime.utcnow().isoformat(), cont) )
                #print(" ->  | {0}".format(line))
                critical_err += 1
                #break
            finally:
                if(critical_err>10):
                    #print("[{0} | CRIT  | {1} ]".format(datetime.utcnow().isoformat(), critical_err) )
                    break
        #print_json(self.dict_types)
        #print("[{0} | END   | {1}]".format(datetime.utcnow().isoformat(), len(self.dict_types) ))
        return self.dict_types

    def template(self,aditional_properties={},idx_pattern = "syslog-group*"):
        self.read_file_with_types(self.fullPath, coding=self.coding)
        tmp_template = self.tmpl_base
        tmp_template.update({"index_patterns": [idx_pattern]})
        dict_filtered = {}
        for key in self.dict_types:
            type_data = self.dict_types[key].lower()
            if type_data != "string":
                if type_data.find("int8")>=0:
                    dict_filtered.update( { key : "integer" } )
                elif type_data.find("int")>=0:
                    dict_filtered.update( { key : "long" } )
                elif type_data.find("ip")>=0:
                    dict_filtered.update( { key : "ip" } )
                else:
                    dict_filtered.update( { key : "***" } )
        
        for key in dict_filtered:
            value =  dict_filtered[key]
            if value == "ip":
                tmp_template['mappings']['doc']['properties'][key]={ 
                    "type": value,
                    "fields": { "keyword": { "type": "keyword"} }
                    }
            else:
                tmp_template['mappings']['doc']['properties'][key]={ "type": value }
        if len(aditional_properties)>0:
            for key in aditional_properties:
                tmp_template['mappings']['doc']['properties'][key]=aditional_properties[key]
        return tmp_template

    def load_template_to_elk(self,nametemplate,template_json):
        if len(template_json)>0 and len(nametemplate)>0:
            URL_FULLPATH = "{0}/_template/{1}".format( self.elk.get_url_elk() , nametemplate) 
            self.elk.req_put(URL_FULLPATH, template_json)
        else:
            print("[{0} | ERROR | load_template_to_elk ]".format(datetime.utcnow().isoformat()) )    
        return
    
    def compare_tmpl_elk(self,tmpl_elk):
        dict_filtered = {}
        for key in tmpl_elk:
            value = tmpl_elk[key]
            type_data = value["type"]
            if type_data!="text":
                dict_filtered.update( {key: type_data} )
        print_json(dict_filtered)
        return

    def build_and_load_template(self):
        aditional_properties = {
            "syslog": {
                "properties": {
                "facility": {"type": "long"},
                "facility_label": {"type": "keyword"},
                "priority": {"type": "long"},
                "serverity": {"type": "long"},
                "severity_label": {"type": "keyword"}
                }
            }
        }
        tmplt_json = self.template(aditional_properties=aditional_properties)
        print_json(tmplt_json)
        save_json(tmplt_json, nameFile="template.json")
        #self.load_template_to_elk("syslog-temporal",tmplt_json)
        return
    
    def delete_template(self, nameTemplate):
        FULLPATH = "{0}/_template/{1}".format(self.elk, nameTemplate)
        self.elk.req_del(FULLPATH, timeout=None)
        return

    def get_list_templates_elk(self):
        list_tmplt = []
        FULLPATH = "{0}/_cat/templates&format:json".format(self.elk.url_elk)
        rpt_json = self.elk.req_get(FULLPATH)
        print_json(rpt_json)
        return rpt_json
#########################################################################################
if __name__ == "__main__":
    print("[INFO] {0}".format(__file__))
    tmpl = builder_template()
    tmpl.build_and_load_template()
    #tmpl.get_list_templates_elk()

"""
all_templates -> tiene definido los settings para todos los templates 
"""