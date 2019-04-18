# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Description: Procesar las alertas generadas
#######################################################################################
from utils import *
from utils_elk import *
from elastic import *
#######################################################################################
def sendAlert2ELK(list_data_to_up_bulk , header_json={"index":{"_index":"alertas" ,"_type":"_doc","_id":"source_id"}} ,elk=None):
    if elk==None: elk = elasticsearch()
    elk.post_bulk(list_data_to_up_bulk, header_json=header_json, random_if_not_found_id=True)
    return
#######################################################################################
def update_only_one_doc(old_status_alert,data2update={}):
    header_json={"index":{"_index":"alertas","_type":"_doc","_id":"source_id"}}
    return 
#######################################################################################
def build_alert_by_ip(elk, data_json):
    ip = data_json['ip']
    client = data_json['client']
    label_watch_id = data_json['label_watch_id']
    # Query para obtener el estatus de la alerta - "solo las q tienen <status:up>"
    query_json = {
        "query": {
            "bool": {
            "must": [
                {"term": {"ip": ip}},
                {"term": {"client": client}},
                {"term": {"label_watch_id": label_watch_id}},
                {"term": {"status_alert" : "up"}}
            ]
            }
        }
    }    
    #Hacemos un request a ELK para ver el estatus de la alerta
    new_alert_by_ip = {}
    #Si "status_alert"=="up", entonces se actualiza la alerta, sino 
    #Si "status_alert"=="down", entonces se crea una nueva alerta, puesto que esa ya se cerro
    #Si no existe, entonces es la primera vez q se registra, lo q indica q hay agregar <first_execution_time>
    rpt_json = elk.req_get(elk.get_url_elk() + "/alertas/_search",data=query_json,timeout=None)
    #print_json(rpt_json)
    if 'error' in rpt_json or rpt_json['hits']['total']==0:
        #Alerta no tiene status o es la primera vez que va ha ser registrada
        """
        "hits": {
            "hits": []
            "max_score": null
            "total":0
        }
        """
        data_json.update( {'first_execution_time': data_json['last_execution_time'], "status_alert": "up"} )
        new_alert_by_ip = data_json
        # lanzamos un watcher para que monitorize dicha ip, hasta que se levante <up>
        print("[INFO ] build_alert_by_ip | <ip:{0}> Firts time.".format(ip))
    elif 'status_alert' in rpt_json['hits']['hits'][0]['_source']:
        old_status_alert = rpt_json['hits']['hits'][0]['_source']['status_alert']
        if old_status_alert=='up':
            #Actualizamos solo el tiempo de ejecucion de la alerta
            old_alert = rpt_json['hits']['hits'][0]
            new_alert_by_ip =  {"source_id": old_alert['_id']}
            new_alert_by_ip.update( old_alert['_source'] )
            new_alert_by_ip.update( {'last_execution_time':data_json['last_execution_time']} )
            print("[INFO ] build_alert_by_ip | <ip:{0}> Updating.".format(ip))
        else:
            print("[ERROR] build_alert_by_ip | <status_alert> not found.")
    else:
        print("[ERROR] build_alert_by_ip | La alerta esta resgistrada & <status_alert> not found.")
        #print_json(rpt_json)
    return new_alert_by_ip
#######################################################################################
def update_alert_by_groupIP(ip_list, description_alert_json):
    
    elk = elasticsearch()
    #dict_client_by_ip = download_configuration_from_elk(elk)
    dict_IP = loadYMLtoJSON('dict_IP.yml')
    list_data_json = []
    cont = 0
    for ip in ip_list:
        if ip in dict_IP:
            #print("[INFO ] update_alert_by_groupIP | {0}".format(ip))
            data_json = { "ip" : ip }
            columns = ["client", "sede", "type_device", "name_device", "function_ip"]
            aditional_data = dict_IP[ip].split(";")
            for n in range(0,len(columns)):
                data_json.update( {columns[n] : aditional_data[n]} )
            data_json.update( description_alert_json)
            alert_json_by_ip =  build_alert_by_ip( elk, data_json )
            if len(alert_json_by_ip)>0: 
                list_data_json.append(alert_json_by_ip)
                cont=cont+1
            else:
                print("No se agrego la data a la lista.......ERROR")
        else:
            print("[ERROR] update_alert_by_groupIP | IP:{0} don't save in ELK. ".format(ip))
    sendAlert2ELK(list_data_json,elk=elk)
    print_list(ip_list)
    return 
#######################################################################################
def get_description(data_json,list_key_to_extract = []):
    alert_description = {}
    for key in list_key_to_extract:
        if key in data_json:
            alert_description[key] = data_json[key]
        else:
            print("[ERROR] get_description | Dont' found <key:{0}>".format(key))
    return alert_description
#######################################################################################
def engine_elastic(data_json):
    rpt = "OK"
    #print_json(data_json)
    if 'path_element' in data_json:
        path_element = data_json['path_element']
        rpt_list = getelementfromjson(data_json,path_element)
        update_alert_by_groupIP(rpt_list, get_description(data_json, list_key_to_extract = ["label_watch_id","last_execution_time"]))
    else:
        print("[ERROR] processAlert | Key not found in data_json <path_element>")
        print(data_json)
        rpt = "ERROR"
    
    return rpt
#######################################################################################
if __name__ == "__main__":
    print("[INICIO] Testing engine")
#"192.168.21.3" tasa