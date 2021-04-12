#coding: UTF-8 
#########################################################################################
# Developer: Deiner Zapata Silva.
# Date: 19/11/2018
# Last update: 28/02/2021
# Description: Server to conect Streak - Webhoook
# Notes: Elastic only support binary data encoded in base64.
# Link: https://ogma-dev.github.io/posts/simple-flask-webhook/
# sys.setdefaultencoding('utf-8') #reload(sys)
# {'index.routing.allocation.include.instance_configuration':'aws.data.highstorage.d2'}
########### from flask import Flask, request, abort
#########################################################################################
import sys
import requests
import json
import time
from datetime import datetime, timedelta
from credentials import * #URL="<elastic>" #USER="usr_elk"  #PASS="pass_elk"
from utils import *
#######################################################################################
class elasticsearch():            
    def __init__(self, url=None, user=None , pas=None, config_json=None):
        self.config_json = None
        self.ip = None
        self.port = None
        if config_json!=None:
            if len(config_json)==1:
                config_json = config_json[0]
                """
                ############### credentials_elasticsearch.yml ################
                elasticsearch:
                    ip: https://00011034032043u24.us-east-1.aws.found.io
                    port: 9243 #value by default
                    user: username
                    pass: passwordpassword
                """
                if config_json["type"]=="file":
                    name_file = config_json["file"]
                    self.config_json = loadYMLtoJSON(name_file)
                    self.ip = self.config_json["elasticsearch"]["ip"]
                    self.port = self.config_json["elasticsearch"]["port"]
                    
                    url = "{0}:{1}".format(self.ip , self.port)
                    pas = self.config_json["elasticsearch"]["pass"]
                    user = self.config_json["elasticsearch"]["user"]
            else:
                print("INFO | elasticsearch | Falta especificar.")
        if(url==None):
            self.url_elk = URL
        else:
            self.url_elk = url
        
        if(user==None):
            self.user = USER
        else:
            self.user = user
        
        if(pas==None):
            self.pas = PASS
        else:
            self.pas  = pas
        
        # _index / _type / _id
        self.index = None
        self.type = None

    def get_url_elk(self):
        return self.url_elk

    def req_get(self, URL_API,data=None,timeout=None):
        if (URL_API==None): URL_API = self.url_elk
        if (data!=None):#len(data)>0
            headers = {'Content-Type': 'application/json'}
            data = json.dumps(data)
            rpt = requests.get( url=URL_API , auth=(self.user,self.pas), headers=headers , data=data , timeout=timeout)
        else:
            rpt = requests.get( url=URL_API , auth=(self.user,self.pas), timeout=timeout)
        
        if not( (rpt.status_code)==200 or (rpt.status_code)==201 ):
            print("[GET]: "+ str(rpt.status_code) +" | "+ str(rpt.reason))        
        try:
            json_rpt = rpt.json()
            #json_pretty = json.loads(rpt.text)
            #print(json.dumps(json_pretty, indent=2, sort_keys=True))
        except:
            json_rpt = rpt.text
        
        return json_rpt
    
    def req_put(self, URL_API, data,timeout=None):
        if (URL_API==None): URL_API = self.url_elk
        headers =  {'Content-Type': 'application/json'}
        if (URL_API==None): URL_API = self.url_elk
        if type(data) != str :
            data = json.dumps(data)

        rpt = requests.put(URL_API, auth=(self.user,self.pas), headers=headers, data = data, timeout=timeout)
        
        if not( (rpt.status_code)==200 or (rpt.status_code)==201 ):
            print("[PUT]:"+str(rpt.status_code)+" | "+ str(rpt.reason) )
        
        return rpt.json()
    
    def req_post(self, URL_API, data,timeout=None):
        if (URL_API==None): URL_API = self.url_elk
        headers =  {'Content-Type': 'application/json'}
        if (URL_API==None): URL_API = self.url_elk
        if type(data) != str :
            data = json.dumps(data)
        rpt = requests.post(URL_API, auth=(self.user,self.pas), headers=headers, data = data , timeout=timeout)
        if not( (rpt.status_code)==200 or (rpt.status_code)==201 ):
            print("[POST]:"+str(rpt.status_code)+" | "+ str(rpt.reason) )
        
        return rpt.json()

    def req_del(self, URL_API,timeout=None):
        rpt = requests.delete( url=URL_API , auth=(self.user,self.pas), timeout=None)
        print("[DEL]:"+str(rpt.status_code)+" | "+ str(rpt.reason) )
        return rpt.json()

    def get_num_element(self, INDEX="" , TYPE=""):
        if( len(INDEX)>0 ): INDEX ="/"+INDEX
        if( len( TYPE)>0 ): TYPE = "/"+TYPE
        
        URL = self.url_elk + INDEX + TYPE + "/_search"
        json_rpt = self.req_get(URL)
        num_values = json_rpt['hits']['total']['value'] #['value'] Aplica para version 7.x
        return num_values        

    def get_documents(self, INDEX="", TYPE="" , query ={"match_all":{}}):
        if( len(INDEX)>0 ): INDEX ="/"+INDEX
        if( len( TYPE)>0 ): TYPE = "/"+TYPE

        URL = self.url_elk + INDEX + TYPE + "/_search"
        query = {
            "size": self.get_num_element(INDEX=INDEX,TYPE=TYPE),
            "query": query
        }
        json_rpt = self.req_get(URL, data=query)
        try:
            num_values = json_rpt['hits']['total']
            values  = json_rpt['hits']['hits']
        except:
            print("get_documents | ERROR | {0}".format(json_rpt['error']['reason']))
            print_json(json_rpt)
            sys.exit(0)
        return values, num_values

    def get_search(self, body_query, index):
        URL = "{0}/{1}/_search".format (self.url_elk,index)
        json_rpt = self.req_get(URL, data = body_query)
        return json_rpt

    def show_all_idx(self, INDEX="", TYPE="" ):
        if( len(INDEX)>0 ): INDEX ="/"+INDEX
        if( len( TYPE)>0 ): TYPE = "/"+TYPE

        URL = self.url_elk + INDEX + TYPE + "/_search"
        query = {
            "size": self.get_num_element(INDEX=INDEX,TYPE=TYPE),
            "query":{
                "match_all":{}
            }
        }

        json_rpt = self.req_get(URL, data=query)
        #print_json(json_rpt)
        num_values = json_rpt['hits']['total']
        values  = json_rpt['hits']['hits']
        cont = 1
        for e in values:
            print("\t"+str(cont)+":"+str(num_values)+"\t_index : "+e["_id"])
            cont = cont + 1 
        return

    def get_hits(self, INDEX="" , TYPE=""):
        if( len(INDEX)>0 ): INDEX ="/"+INDEX
        if( len( TYPE)>0 ): TYPE = "/"+TYPE

        URL = self.url_elk + INDEX + TYPE + "/_search"
        query = {
            "query":{
                "match_all":{}
            }
        }

        json_rpt = self.req_get(URL, data=query)
        print_json(json_rpt)
        num_values = json_rpt['hits']['total']
        values  = json_rpt['hits']['hits']
        
        print("\nnum: "+str(num_values))
        return values, num_values
    
    def put_data(self, INDEX, data, debug=False,timeout=None):
        URL = self.url_elk + "/" + INDEX 
        if(debug):
            #json_data=json.loads(data) 
            print_json(data)
        
        rpt_json = self.req_put(URL,data,timeout=None)
        return rpt_json

    def post_data(self, INDEX, data, debug=False,timeout=None):
        URL = self.url_elk + "/" + INDEX 
        if(debug):
            #json_data=json.loads(data) 
            print_json(data)
        
        rpt_json = self.req_post(URL,data)
        return rpt_json

    def set_data(self, INDEX, TYPE, ID, data):
        URL = self.url_elk + "/" + INDEX + "/" + TYPE + "/"+ ID
        rpt_json = self.req_post(URL,data)
        return rpt_json

    def get_by_id(self, INDEX, TYPE, ID):
        URL = self.url_elk + "/" + INDEX + "/" + TYPE + "/"+ ID
        json_rpt = self.req_get(URL)
        return json_rpt

    def delete_by_index(self,INDEX):
        URL = self.url_elk + "/" + INDEX
        self.req_del(URL)
        return

    def delete_by_id(self, INDEX, TYPE, ID):
        URL = self.url_elk + "/" + INDEX + "/" + TYPE + "/"+ ID
        self.req_del(URL)
        return

    def delete_by_list_of_index(self, LIST_INDEX):
        for INDEX in LIST_INDEX:
            self.delete_by_index(INDEX)
        return

    def search_by_template(self, template_id, params, index):
        """
        Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/search-template.html
        
        @template_id: Templates name when is create
        @params: Params used by template
        
        Example:
            template_id: "MENU_DINAMICO"
            params: {
                "FIELD_MENU_01": "Ruta de Aprendizaje",
                "FIELD_MENU_02": "Curso"    
            }
        """
        URL_API = "{}/{}/_search/template".format(self.url_elk, index)
        data_json = {
          "id": template_id,
          "params": params
        }
        rpt_json = self.req_get(URL_API,data=data_json,timeout=None)
        
        return rpt_json


    def post_bulk(self,list_data,header_json=None,random_if_not_found_id=False):
        data2sent = ""
        start_time = time.time()
        if(len(list_data)==0):
            print("[WARN] post_bulk | list_data is NULL.")
            #time.sleep(1)
            return
        cont = 0
        for lista in list_data :
            cont = cont + 1
            header_temp = {}
            if(header_json==None):
                # Significa que el _index, _type y _id estan especificados en list_data=[_index,_type,_id,_source]
                # update -> solo actualiza algunos campos, no es necesario especificar todos los campos del doc.
                #           {"update":{"_index":<index>,"_type":<type>,"_id":<id>}}
                #           { "doc" :  lista["_source"] }
                # index  -> fuerza la actualización del documento, si el campo no existe se elimina del doc.
                #           {"index":{"_index":<index>,"_type":<type>,"_id":<id>}}
                #           lista["_source"]
                #--------------------------------------------------------------------------------
                header_temp = {
                    "update":{ 
                        "_index": lista["_index"],
                        "_type" : lista["_type"],
                        "_id" : lista["_id"],
                        "_source": True
                    }
                }
                #--------------------------------------------------------------------------------
                body_temp = { "doc" :  lista["_source"] }
                #--------------------------------------------------------------------------------
            elif 'index' in header_json:
                # header_json={"index":{"_index":"alertas","_type":"_doc","_id":"source_id"}}
                if "_id" in header_json['index']: #Especifica la 'key' que tiene el id a ser sobreescrito
                    nameKeyToSearch = header_json['index']['_id']
                    try: 
                        # Intentamos extraer el ID de lista_data
                        _id = "{0}".format( lista[nameKeyToSearch] )
                    except:
                        if random_if_not_found_id :# El ID sera asignado por ELASTIC
                            _id = None # Si key=None, entonces 'renameValues' elimina dicho campo del json
                        else:# El Id es un contador interno único
                            _id = "{0}".format( cont )
                    finally:
                        #Construimos el 'header' con la variable '_id'
                        header_temp = renameValues(header_json,nameKeyToSearch,_id)
                        body_temp = lista
                else:
                    header_temp = header_json
                    body_temp = lista    
            else:
                header_temp = header_json
                body_temp = lista
            # Pasamos todo a string antes de ser enviada.
            data2sent = data2sent +json.dumps(header_temp)+"\n"+json.dumps(body_temp) + "\n"
        URL = self.url_elk + "/_bulk"
        rpt_json = self.req_post(URL , data2sent )
        elapsed_time = time.time() - start_time
        print("[POST_BULK] Elapsed time : %.10f seconds\n" % elapsed_time)
        #print_json(rpt_json)
        if 'errors' in rpt_json:
            if rpt_json['errors']== True:
                print_json(rpt_json)
        return rpt_json
    
    def algorithm(self,data):
        raise NotImplementedError()

    def algorithm_process_data(self,data,list_server):
        try:
            tmp = data['NetBIOS Name'].split("\\")
            name_device = tmp[1]
            flagFound=False
            for name in list_server:
                if name_device == name:
                    flagFound=True
                    break
            if flagFound:
                data['type_device'] = 'server'
            else:
                data['type_device'] = 'workstation'
                #input("error      ")
        except:
            #print_json(data)
            data['type_device'] = 'workstation'
            #input("press any key...")
        #print("algorithm_process_data | END | ")
        return data
    #######################################################################################    
    #@count_elapsed_time
    def process_data(self, INDEX,TYPE=""):
        mes = "Jul-19"
        query={
            "bool": {
            "must": [
                {"match": {"tipo_reporte": "vulnerabilidades"}},
                {"match": {"mes": mes}}
            ],
            "should": [
                {"match": {"severity": "High"}},
                {"match": {"severity": "Critical"
                }
                }
            ]
            }
        }
        list_element, length = self.get_documents(INDEX=INDEX,TYPE="",query=query)
        #print(str(length))
        #self.show_all_idx(INDEX=INDEX,TYPE="")
        start_time = time.time()
        cont = 0
        list_data = []
        list_server = loadYMLtoJSON("server.yml")
        #print_json(list_server)
        for e in list_element:
            try:
                data = self.algorithm_process_data(e["_source"],list_server)
                list_data.append({
                        "_index":e["_index"],
                        "_type" :e["_type"],
                        "_id"   :e["_id"],
                        "_source":data
                    })
                #self.set_data( e["_index"] , e["_type"] , e["_id"] , data )
            except Exception as err:
                print("\r Except...  "+"_id:"+e["_id"] + ": [ERROR :" + str(err)+"]")
            finally:
                cont = cont + 1
        elapsed_time = time.time() - start_time
        print("\n[PROCESS_DATA] Elapsed time : %.10f seconds\n" % elapsed_time)
        self.post_bulk(list_data)
        return

    def process_repsol(self):
        INDEX = "repsol-vulnerabilidades"
        self.process_data(INDEX,"_doc")
        return
#######################################################################################
def test_conection_from_file():
    config_json = {
        "elasticsearch": [{
            "type": "file",
            "file": "credential_elasticsearch.yml"
        }]
    }
    ec = elasticsearch(config_json=config_json["elasticsearch"])
    rpt_json = ec.req_get(ec.get_url_elk() + "/_cluster/state?pretty")
    print_json(rpt_json)
    return
######################################################################################
def test():
    print("Test class elastic")
    ec=elasticsearch(url=URL,user=USER,pas=PASS)
    
    #ec=elasticsearch()
    #rpt_json = ec.req_get(ec.get_url_elk() + "/_cat/indices?v") #_search?pretty
    #rpt_json = ec.req_get(ec.get_url_elk() + "/_cluster/state/_all/syslog-global-write")
    #rpt_json = ec.req_get(ec.get_url_elk() + "/_cluster/health?pretty")
    rpt_json = ec.req_get(ec.get_url_elk() + "/_cluster/state")
    #rpt_json = ec.req_get(ec.get_url_elk() + "/_cluster/state/nodes/syslog-global-write")
    print_json(rpt_json)
    return
#######################################################################################
if __name__=="__main__":
    print("Running file python . . .\n\t["+str(__file__)+"]")
    test()
#######################################################################################