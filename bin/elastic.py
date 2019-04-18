#coding: UTF-8 
#########################################################################################
# Developer: Deiner Zapata Silva.
# Date: 19/11/2018
# Description: Server to conect Streak - Webhoook
# Link: https://ogma-dev.github.io/posts/simple-flask-webhook/
# sys.setdefaultencoding('utf-8') #reload(sys)
########### from flask import Flask, request, abort
#########################################################################################
import sys, requests, json
from datetime import datetime, timedelta
import time
from credentials import * #URL="<elastic>" #USER="usr_elk"  #PASS="pass_elk"
from utils import *
#######################################################################################
class elasticsearch():            
    def __init__(self, url=None, user=None , pas=None):
        global URL
        global USER
        global PASS
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

    def req_get(self, URL_API,data="",timeout=None):
        if (URL_API==None): URL_API = self.url_elk
        if (len(data)>0):
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
        
        return
    
    def req_post(self, URL_API, data,timeout=None):
        if (URL_API==None): URL_API = self.url_elk
        headers =  {'Content-Type': 'application/json'}
        if (URL_API==None): URL_API = self.url_elk
        if type(data) != str :
            data = json.dumps(data)
        rpt = requests.post(URL_API, auth=(self.user,self.pas), headers=headers, data = data , timeout=timeout)
        if not( (rpt.status_code)==200 or (rpt.status_code)==201 ):
            print("[POST]:"+str(rpt.status_code)+" | "+ str(rpt.reason) )
        
        return

    def req_del(self, URL_API,timeout=None):
        rpt = requests.delete( url=URL_API , auth=(self.user,self.pas), timeout=None)
        print("[DEL]:"+str(rpt.status_code)+" | "+ str(rpt.reason) )
        return

    def get_num_element(self, INDEX="" , TYPE=""):
        if( len(INDEX)>0 ): INDEX ="/"+INDEX
        if( len( TYPE)>0 ): TYPE = "/"+TYPE
        
        URL = self.url_elk + INDEX + TYPE + "/_search"
        json_rpt = self.req_get(URL)
        num_values = json_rpt['hits']['total']
        return num_values        

    def get_all_element(self, INDEX="", TYPE="" ):
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
        
        return values, num_values

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
        
        self.req_put(URL,data,timeout=None)
        return

    def post_data(self, INDEX, data, debug=False,timeout=None):
        URL = self.url_elk + "/" + INDEX 
        if(debug):
            #json_data=json.loads(data) 
            print_json(data)
        
        self.req_post(URL,data)
        return

    def set_data(self, INDEX, TYPE, ID, data):
        URL = self.url_elk + "/" + INDEX + "/" + TYPE + "/"+ ID
        self.req_post(URL,data)
        return

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
        self.req_post(URL , data2sent )
        elapsed_time = time.time() - start_time
        print("[POST_BULK] Elapsed time : %.10f seconds\n" % elapsed_time)
        return
    
    def algorithm(self,data):
        raise NotImplementedError()

    def algorithm_process_data(self,data):
        FECHA_REGISTRO="2018-11-21 17:51:29"

        if(data["VProd_EndpointSecurityThreatPrevention"] == "*"):
            TipoProd="EST"
        else: 
            TipoProd="VSE"
        
        data.update({ "TipoProd" : TipoProd })
        #print_json(data)
        
        IdMcafee={
            "LastVersAgent" : "5.0.6.220",
            "LastVSE1" : "8.8.0.1445",
            "LastVSE2" : "8.8.0.1444",
            "LastVSE3" : "8.8.0.1443",
            "LastDAT1" : "9076",
            "LastDAT2" : "9075",
            "LastDAT3" : "9074",
            "LastEST1" : "10.5.3.3264",
            "LastEST2" : "10.5.3.3263",
            "LastEST3" : "10.5.3.3262",
            "LastAMC1" : "3527",
            "LastAMC2" : "3526",
            "LastAMC3" : "3525",
            "InsFecha" : "2018-11-21 17:51:29"
        }
        #
        if(data["VProd_Agent"]==IdMcafee["LastVersAgent"] and IdMcafee["InsFecha"]==FECHA_REGISTRO):
            data.update({"Agent_status":"ACTUALIZADO"})
        else:
            data.update({"Agent_status":"DESACTUALIZADO"})
        ###################################################
        VERSION_DAT = data["V_DAT"]
        VERSION_VSE = data["VProd_VSE"]
        VERSION_AMC = data["V_AMCore_Content"]
        VERSION_EST = data["VProd_EndpointSecurityThreatPrevention"]
        ###################################################
        data.update({"status_final":"DESACTUALIZADO"})
        
        if(data['TipoProd']=="VSE"):
            data.update({"VSE_status":"DESACTUALIZADO"})
            data.update({"DAT_status":"DESACTUALIZADO"})
            if( (IdMcafee["InsFecha"]==FECHA_REGISTRO and  VERSION_VSE==IdMcafee["LastVSE1"]) or 
                (IdMcafee["InsFecha"]==FECHA_REGISTRO and VERSION_VSE==IdMcafee["LastVSE2"]) or 
                (IdMcafee["InsFecha"]==FECHA_REGISTRO and VERSION_VSE==IdMcafee["LastVSE3"]) ):
                data.update({"VSE_status":"ACTUALIZADO"})
            
            if( (VERSION_DAT==IdMcafee["LastDAT1"] and IdMcafee["InsFecha"]==FECHA_REGISTRO) or
                (VERSION_DAT==IdMcafee["LastDAT2"] and IdMcafee["InsFecha"]==FECHA_REGISTRO) or
                (VERSION_DAT==IdMcafee["LastDAT3"] and IdMcafee["InsFecha"]==FECHA_REGISTRO) ):
                data.update({"DAT_status":"ACTUALIZADO"})
            
            if( data["VSE_status"]=="ACTUALIZADO" and data["DAT_status"]=="ACTUALIZADO" ):
                data.update({"status_final":"ACTUALIZADO"})
        else:
            data.update({"VSE_status":"NO APLICA"})
            data.update({"DAT_status":"NO APLICA"})
        
        if(data['TipoProd']=="EST"):
            data.update({"EST_status":"DESACTUALIZADO"})
            data.update({"AMC_status":"DESACTUALIZADO"})

            if( (VERSION_EST==IdMcafee["LastEST1"] and IdMcafee["InsFecha"]==FECHA_REGISTRO) or
                (VERSION_EST==IdMcafee["LastEST2"] and IdMcafee["InsFecha"]==FECHA_REGISTRO) or
                (VERSION_EST==IdMcafee["LastEST3"] and IdMcafee["InsFecha"]==FECHA_REGISTRO) ):
                data.update({"EST_status":"ACTUALIZADO"})
            
            if( (VERSION_AMC==IdMcafee["LastAMC1"] and IdMcafee["InsFecha"]==FECHA_REGISTRO) or
                (VERSION_AMC==IdMcafee["LastAMC2"] and IdMcafee["InsFecha"]==FECHA_REGISTRO) or
                (VERSION_AMC==IdMcafee["LastAMC3"] and IdMcafee["InsFecha"]==FECHA_REGISTRO) ):
                data.update({"AMC_status":"ACTUALIZADO"})
            
            if( data["EST_status"]=="ACTUALIZADO" and data["AMC_status"]=="ACTUALIZADO" ):
                data.update({"status_final":"ACTUALIZADO"})
        else:
            data.update({"EST_status":"NO APLICA"})
            data.update({"AMC_status":"NO APLICA"})

        return data
    #######################################################################################    
    #@count_elapsed_time
    def process_data(self, INDEX,TYPE=""):
        list_element, length = self.get_all_element(INDEX=INDEX,TYPE="")
        #print(str(length))
        #self.show_all_idx(INDEX=INDEX,TYPE="")
        start_time = time.time()
        cont = 0
        list_data = []
        for e in list_element:
            try:
                data = self.algorithm_process_data(e["_source"])
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
        INDEX = "repsol_data"
        self.process_data(INDEX,"_doc")
        return
#######################################################################################
def test():
    print("Test class elastic")
    ec=elasticsearch()
    #rpt_json = ec.req_get(ec.get_url_elk() + "/_cat/indices?v")
    rpt_json = ec.req_get(ec.get_url_elk() + "/_cluster/state")
    print_json(rpt_json)
    
    """
    lista_json = loadCSVtoJSON("Todos_los_equipos_Peru.csv")
    ec.delete_by_index("repsol")
    ec.post_bulk(lista_json,headers={"index":{"_index":"repsol","_type":"_doc"}})
    ec.process_repsol()
    ec.algorithm()
    """
    
    #ec.get_hits(INDEX="cars",TYPE="transactions")
    #ec.get_hits(INDEX="repsol")
    #ec.set_data("repsoll","_doc","7x8uV2cBidP485DQW1F5", {"Versión de producto (VirusScan Enterprise)":"HOAT23"} )
    #ec.set_data("repsoll","_doc","-x8uV2cBidP485DQW1F5", {"Versión de producto (VirusScan Enterprise)":"HOAT23"} )
    #ec.get_by_id("cars","transactions","1")
    return
#######################################################################################
if __name__=="__main__":
    print("Running file python . . .\n\t["+str(__file__)+"]")
    test()
#######################################################################################
