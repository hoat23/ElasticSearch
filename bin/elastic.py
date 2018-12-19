#coding: UTF-8 
#########################################################################################
# Developer: Deiner Zapata Silva.
# Date: 19/11/2018
# Description: Server to conect Streak - Webhoook
# Link: https://ogma-dev.github.io/posts/simple-flask-webhook/
# sys.setdefaultencoding('utf-8') #reload(sys)
#########################################################################################
import sys, requests, json
from datetime import datetime, timedelta
from flask import Flask, request, abort
from time import time
########################################################################################
# Import local lybraries
from utils import *
########################################################################################
URL = "https://658b9b529aee44339307affc751190da.us-east-1.aws.found.io:9243" #key/webhooks
USER = "elastic"
PASS = "m1T9E22JBuR12zxlMhFYasZp"
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

    def req_get(self, URL_API,data=""):
        if (len(data)>0):
            headers = {'Content-Type': 'application/json'}
            data = json.dumps(data)
            rpt = requests.get( url=URL_API , auth=(self.user,self.pas), headers=headers , data=data )
        else:
            rpt = requests.get( url=URL_API , auth=(self.user,self.pas))
        
        if not( (rpt.status_code)==200 or (rpt.status_code)==201 ):
            print("[GET]: "+ str(rpt.status_code) +" | "+ str(rpt.reason))
        #json_pretty = json.loads(rpt.text)
        json_rpt = rpt.json()
        #print(json.dumps(json_pretty, indent=2, sort_keys=True))
        return json_rpt
    
    def req_post(self, URL_API, data):
        headers =  {'Content-Type': 'application/json'}
        if type(data) != str :
            data = json.dumps(data)

        rpt = requests.post(URL_API, auth=(self.user,self.pas), headers=headers, data = data )
        
        if not( (rpt.status_code)==200 or (rpt.status_code)==201 ):
            print("[POST]:"+str(rpt.status_code)+" | "+ str(rpt.reason) )
        
        return

    def req_del(self, URL_API):
        rpt = requests.delete( url=URL_API , auth=(self.user,self.pas))
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
    
    def set_data(self, INDEX, TYPE, ID, data):
        URL = self.url_elk + "/" + INDEX + "/" + TYPE + "/"+ ID
        #json_data=json.loads(data)
        #print_json(json_data)
        self.req_post(URL,data)
        return

    def get_by_id(self, INDEX, TYPE, ID):
        URL = self.url_elk + "/" + INDEX + "/" + TYPE + "/"+ ID
        json_rpt = self.req_get(URL)
        return json_rpt
    
    def delete_by_index(self, INDEX):
        URL = self.url_elk + "/" + INDEX
        json_rpt = self.req_del(URL)
        return

    def delete_by_id(self, INDEX, TYPE, ID):
        URL = self.url_elk + "/" + INDEX + "/" + TYPE + "/"+ ID
        json_rpt = self.req_del(URL)
        return

    def post_bulk(self,list_data,headers=None):
        data2sent = ""
        cont = 0
        start_time = time()
        for lista in list_data : 
            if(headers==None):
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
            else:
                header_temp = headers
                body_temp = lista
            cont = cont + 1
            data2sent = data2sent +json.dumps(header_temp)+"\n"+json.dumps(body_temp) + "\n"
        URL = self.url_elk + "/_bulk"
        self.req_post(URL , data2sent )
        elapsed_time = time() - start_time
        print("[POST_BULK] Elapsed time : %.10f seconds\n" % elapsed_time)
        return
    
    #@count_elapsed_time
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

    def process_data(self, INDEX,TYPE=""):
        list_element, length = self.get_all_element(INDEX=INDEX,TYPE="")
        #print(str(length))
        #self.show_all_idx(INDEX=INDEX,TYPE="")
        start_time = time()
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
                #print_json(data)
            except Exception as err:
                print("\r Except...  "+"_id:"+e["_id"] + ": [ERROR :" + str(err)+"]")
            finally:
                cont = cont + 1
                #print("\r Process... "+str(cont) +":" + str(length) )
        elapsed_time = time() - start_time
        print("\n[PROCESS_DATA] Elapsed time : %.10f seconds\n" % elapsed_time)
        self.post_bulk(list_data)
        return

    def process_repsol(self):
        INDEX = "repsol_data"
        self.process_data(INDEX,"_doc")
        return

def test():
    print("Test class elastic")
    elk=elasticsearch()
    elk.process_repsol()
    return

#elk.get_hits(INDEX="cars",TYPE="transactions")
#elk.get_hits(INDEX="repsol")
#elk.set_data("repsoll","_doc","7x8uV2cBidP485DQW1F5", {"Versión de producto (VirusScan Enterprise)":"HOAT23"} )
#elk.set_data("repsoll","_doc","-x8uV2cBidP485DQW1F5", {"Versión de producto (VirusScan Enterprise)":"HOAT23"} )
#elk.get_by_id("cars","transactions","1")
