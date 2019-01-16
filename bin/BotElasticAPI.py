#!/usr/bin/env python
import pprint
import requests
import getpass
import time
import paramiko as pmk
import sys, json, socket, argparse
import elastic as e
from utils import *
########################################################################################
def build_alias_by_sede(elk_index,client,sede):
    """
    POST _aliases
    {
    "actions": [{
        "add": {
            "index": "{elk_index}-{client_a}-*",
            "alias": "{elk_index}-{client_a}-{sede_01}",
            "filter": {
                "term": {"sede": "{sede_01}"}
            }
        }
    }]
    }
    """
    print("---> build_alias_by_sede ")
    add_alias = {
        "add":{
            "index": elk_index + "-" + client + "-*" ,
            "alias": elk_index + "-" + client + "-" + sede ,
            "filter": {
                "term": {"sede": sede}
            }
        }
    }
    print_json(add_alias)
    return
########################################################################################
def build_alias_by_sede_type_device(elk_index,client,sede,type_device):
    """
    POST _aliases
    {
    "actions": [{
        "add": {
            "index": "{elk_index}-{client_a}-*",
            "alias": "{elk_index}-{client_a}-{sede_01}",
            "filter": {
                "term": {"sede": "{sede_01}"}
            }
        }
    }]
    }
    """
    print("---> build_alias_by_sede_type_device ")
    add_alias = {
        "add":{
            "index": elk_index + "-" + client + "-*" ,
            "alias": elk_index + "-" + client + "-" + sede + "-" + type_device,
            "filter": {
                "term": {"sede": sede},
                "term": {"type_device": type_device}
            }
        }
    }
    print_json(add_alias)
    return
########################################################################################
def build_alias_by_only_type_device(elk_index,client,type_device):
    """
    POST _aliases
    {
    "actions": [{
        "add": {
            "index": "{elk_index}-{client_a}-*",
            "alias": "{elk_index}-{client_a}-{sede_01}",
            "filter": {
                "term": {"sede": "{sede_01}"}
            }
        }
    }]
    }
    """
    print("---> build_alias_by_only_type_device ")
    add_alias = {
        "add":{
            "index": elk_index + "-" + client + "-*" ,
            "alias": elk_index + "-" + client + "-" + type_device,
            "filter": {
                "term": {"type_device": type_device}
            }
        }
    }
    print_json(add_alias)
    return
########################################################################################
def build_all_templates(list_elk_index,list_client,list_dev_type):
    for elk_index in list_elk_index:
        print("################# "+ elk_index + " #################")
        for client in list_client:
            print("################# "+ client +" #################")
            sede = "lima"
            for type_device in list_dev_type:
                build_alias_by_sede(elk_index,client,sede)
                build_alias_by_sede_type_device(elk_index,client,sede,type_device)
                build_alias_by_only_type_device(elk_index,client,type_device)
    return
########################################################################################
def sent2elk(URL_ELK,data_query,print=False,req=None,timeout=None):
    ec=e.elasticsearch()
    if(req=="PUT"):
        ec.put_data('/' + URL_ELK , data_query,print=print,timeout=timeout)
    if(req=="POST"):
        ec.post_data( URL_ELK, data_query,print=print,timeout=timeout)
    return
########################################################################################
def build_index_by_one_client(elk_index,client,list_sedes,list_dev_type,cont_index="000001",alias_write=True):
    print("#############################################################")
    URL_ELK = elk_index+"-"+client+"-"+cont_index
    header = "PUT "+URL_ELK
    print(header)
    for type_device in list_dev_type:
        #print("---->"+type_device)
        elk_index_client = elk_index + "-" + client
        elk_index_client_type_device = elk_index+"-"+client+"-"+type_device
        data_query={
            "aliases": {
                elk_index_client :{},
                elk_index_client_type_device:{
                    "filter": {
                        "term": {
                        "type_device": type_device
                        }
                    }
                }
            }
        }    
        if alias_write:
            elk_index_client_write = elk_index+"-"+client+"-"+"write"
            data_query['aliases'].update( { elk_index_client_write:{} } )

        for sede in list_sedes:    
            #print("-->"+sede)
            elk_index_client_sede = elk_index+"-"+client+"-"+sede
            data_sede ={
                elk_index_client_sede:{
                    "filter": {
                        "term": {"sede": sede}
                    }
                }
            }
            data_query['aliases'].update(data_sede)

            elk_index_client_sede_type_device = elk_index+"-"+client+"-"+sede+"-"+type_device
            data_sede_type_device ={
                elk_index_client_sede_type_device:{
                    "filter": {
                        "bool": {
                        "must": [
                            {"term":{"sede":sede}},
                            {"term":{"type_device":type_device}}
                        ]
                        }
                    }
                }
            }
            #print_json(data_query)
            data_query['aliases'].update(data_sede_type_device)
    
    return URL_ELK,data_query
########################################################################################
def build_parse_alias(current_index,new_index,alias_to_parse):
    print("#############################################################")
    header = "_aliases"
    print("POST " + header)
    data_json = {
        "actions": [
                {
                "remove": {
                    "index": current_index,
                    "alias": alias_to_parse
                    }
                },
                {
                "add": {
                    "index": new_index,
                    "alias": alias_to_parse
                    }
                }   
        ]
    }
    return header, data_json
########################################################################################
def parse_alias_write_all(list_elk_index, list_client):
    list_index = []
    for elk_index in list_elk_index:
        for client in list_client:
            if client == "alianza":
                current_index = elk_index + "-" + client + "-" + "000001-temp"
                new_index = elk_index + "-" + client + "-" + "000001"
                alias_to_parse = elk_index+"-"+client+"-"+"write"
                header, data_query = build_parse_alias(current_index,new_index,alias_to_parse)
                print_json(data_query)
                sent2elk(header,data_query,print=False,req="POST")
                list_index.append(new_index)
    return list_index
########################################################################################
def build_reindex(src_index,dest_index,filter_opt=None):
    header = "_reindex?slices=2"
    print("POST "+header)
    data_json = {
        "source": {
            "index": src_index
        },
        "dest": {
            "index": dest_index
        }
    }
    return header, data_json
##############################################################################
def reindex_all(list_elk_index, list_client):
    list_index = []
    for elk_index in list_elk_index:
        for client in list_client:
            if client == "alianza":
                src_index = elk_index + "-" + client + "-" +"000001-temp"
                dest_index =  elk_index + "-" + client + "-" + "000001"
                header, data_query = build_reindex(src_index,dest_index)
                print_json(data_query)
                sent2elk(header,data_query,print=False,req="POST",timeout=2)
                list_index.append(dest_index)
    
    return list_index
########################################################################################
def create_index_all(list_elk_index,list_client,dict_sede,list_dev_type):
    list_to_filter = ["supra"]
    list_dev_type=["switch","firewall"]
    list_index = []
    for elk_index in list_elk_index:
        for client in list_client:
            if client == "alianza":
                list_sedebyclient = dict_sede[client]
                index,data_query = build_index_by_one_client(elk_index,client,list_sedebyclient,list_dev_type,cont_index="000001",alias_write=True)
                print_json(data_query)
                sent2elk(index,data_query,print=False,req="PUT",timeout=2)
                list_index.append(index)
    return list_index
########################################################################################
if __name__ == "__main__" :
    list_elk_index=["syslog"]#"syslog","heartbeat"]
    list_dev_type=["switch","firewall"]
    #list_client=["alianza","aje","alexim","babyclubchic","bdo","brexia","crp","comexa","continental","cosapi","cpal","disal","dispercol","divemotors","egemsa","enapu","famesa","fibertel","filasur","gomelst","happyland","imm","ind_marique","ifreserve","ingenyo","itochu","la_llave","lab_hofarm","labocer","mastercol","movilmax","orval","proinversion","san_silvestre","santo_domingo","socios_en_salud","supra","thomas_greg","trofeos_castro","uladech","univ_per_union","valle_alto","zinsa","upch","tasa","prompe","engie","cdtel","test_client"]
    list_client=["alianza","aje","alexim","babyclubchic","bdo","brexia","crp","comexa","continental","cosapi","cpal","disal","dispercol","divemotors","egemsa","enapu","famesa","fibertel","filasur","gomelst","happyland","imm","ind_marique","ifreserve","ingenyo","itochu","la_llave","lab_hofarm","labocer","mastercol","movilmax","orval","proinversion","san_silvestre","santo_domingo","socios_en_salud","supra","thomas_greg","trofeos_castro","uladech","univ_per_union","valle_alto","zinsa","upch","tasa","prompe","engie","cdtel"]
    dict_sede = {
        "test_client": ["unica"],
        "alianza": ["unica"],
        "aje": ["salem_sullana","salem_puentepiedra","salem_lima","salem_chiclayo","planta_tarapoto" ,"planta_pucallpa","planta_iquitos","planta_huachipa","planta_chiclayo","planta_barranca","planta_ayacucho","cedi_huallaga","cedis_tumbes","cedis_tulipanes_iquitos","cedis_tarapoto","cedis_piura","canan_huachipa","canan_chorrillos","canam_huancayo","almacen_mechita","almacen_maxo","qubo"],
        "alexim": ["unica"],
        "babyclubchic": ["unica"],
        "bdo": ["consulting","outsourcing"],
        "brexia": ["unica"],
        "crp": ["unica"],
        "comexa": ["unica"],
        "continental": ["aqp_lambramani","universidad-continental","uc-cuzco","instituto-continental","lima_norte"],
        "cosapi": ["unica"],
        "cpal": ["unica"],
        "disal": ["unica"],
        "dispercol": ["unica"],
        "divemotors": ["unica"],
        "egemsa": ["unica"],
        "enapu": ["unica"],
        "famesa": ["puente_piedra","surco"],
        "fibertel": ["unica"],
        "filasur": ["unica"],
        "gomelst": ["unica"],
        "happyland": ["unica"],
        "imm": ["unica"],
        "ind_marique": ["unica"],
        "ifreserve": ["unica"],
        "ingenyo": ["unica"],
        "itochu": ["unica"],
        "la_llave": ["unica"],
        "lab_hofarm": ["unica"],
        "labocer": ["unica"],
        "mastercol": ["unica"],
        "movilmax": ["unica"],
        "orval": ["unica"],
        "proinversion": ["unica"],
        "san_silvestre": ["unica"],
        "santo_domingo": ["unica"],
        "socios_en_salud": ["lince","comas","carabayllo"],
        "supra": ["unica"],
        "thomas_greg": ["unica"],
        "trofeos_castro": ["unica"],
        "uladech": ["unica"],
        "univ_per_union": ["unica"],
        "valle_alto": ["unica"],
        "zinsa": ["unica"],
        "upch": ["cro","central","este"],
        "tasa": ["san_borja","astillero","pucusana", "supe","chimbote", "callao","piscosur","malabrigo","ilo","vegueta","atico","pisconorte","matarani"],
        "prompe": ["basadre","calle_1"],
        "engie": ["unica"],
        "cdtel": ["unica"]
    }
    """
    print("Construyendo all templates...")
    for client in list_client :
        try:
            print_list(dict_sede[client])
        except KeyError:
            None
    """
    """
    list_index = create_index_all(list_elk_index, list_client,dict_sede,list_dev_type)
    print("#############################################################")
    print(" LISTA DE INDICES . . .")
    print_list(list_index)
    """
    """
    list_index = parse_alias_write_all(list_elk_index, list_client)
    print(" LISTA DE INDICES . . .")
    print_list(list_index)
    """
    """
    list_index = reindex_all(list_elk_index, list_client)
    print(" LISTA DE INDICES . . .")
    print_list(list_index)
    """
    list_delete_index = []

"""
LISTA DE INDICES . . .
        000. syslog-alianza-000001
        001. syslog-aje-000001
        002. syslog-alexim-000001
        003. syslog-babyclubchic-000001
        004. syslog-bdo-000001
        005. syslog-brexia-000001
        006. syslog-crp-000001
        007. syslog-comexa-000001
        008. syslog-continental-000001
        009. syslog-cosapi-000001
        010. syslog-cpal-000001
        011. syslog-disal-000001
        012. syslog-dispercol-000001
        013. syslog-divemotors-000001
        014. syslog-egemsa-000001
        015. syslog-enapu-000001
        016. syslog-famesa-000001
        017. syslog-fibertel-000001
        018. syslog-filasur-000001
        019. syslog-gomelst-000001
        020. syslog-happyland-000001
        021. syslog-imm-000001
        022. syslog-ind_marique-000001
        023. syslog-ifreserve-000001
        024. syslog-ingenyo-000001
        025. syslog-itochu-000001
        026. syslog-la_llave-000001
        027. syslog-lab_hofarm-000001
        028. syslog-labocer-000001
        029. syslog-mastercol-000001
        030. syslog-movilmax-000001
        031. syslog-orval-000001
        032. syslog-proinversion-000001
        033. syslog-san_silvestre-000001
        034. syslog-santo_domingo-000001
        035. syslog-socios_en_salud-000001
        036. syslog-supra-000001
        037. syslog-thomas_greg-000001
        038. syslog-trofeos_castro-000001
        039. syslog-uladech-000001
        040. syslog-univ_per_union-000001
        041. syslog-valle_alto-000001
        042. syslog-zinsa-000001
        043. syslog-upch-000001
        044. syslog-tasa-000001
        045. syslog-prompe-000001
        046. heartbeat-alianza-000001
        047. heartbeat-aje-000001
        048. heartbeat-alexim-000001
        049. heartbeat-babyclubchic-000001
        050. heartbeat-bdo-000001
        051. heartbeat-brexia-000001
        052. heartbeat-crp-000001
        053. heartbeat-comexa-000001
        054. heartbeat-continental-000001
        055. heartbeat-cosapi-000001
        056. heartbeat-cpal-000001
        057. heartbeat-disal-000001
        058. heartbeat-dispercol-000001
        059. heartbeat-divemotors-000001
        060. heartbeat-egemsa-000001
        061. heartbeat-enapu-000001
        062. heartbeat-famesa-000001
        063. heartbeat-fibertel-000001
        064. heartbeat-filasur-000001
        065. heartbeat-gomelst-000001
        066. heartbeat-happyland-000001
        067. heartbeat-imm-000001
        068. heartbeat-ind_marique-000001
        069. heartbeat-ifreserve-000001
        070. heartbeat-ingenyo-000001
        071. heartbeat-itochu-000001
        072. heartbeat-la_llave-000001
        073. heartbeat-lab_hofarm-000001
        074. heartbeat-labocer-000001
        075. heartbeat-mastercol-000001
        076. heartbeat-movilmax-000001
        077. heartbeat-orval-000001
        078. heartbeat-proinversion-000001
        079. heartbeat-san_silvestre-000001
        080. heartbeat-santo_domingo-000001
        081. heartbeat-socios_en_salud-000001
        082. heartbeat-supra-000001
        083. heartbeat-thomas_greg-000001
        084. heartbeat-trofeos_castro-000001
        085. heartbeat-uladech-000001
        086. heartbeat-univ_per_union-000001
        087. heartbeat-valle_alto-000001
        088. heartbeat-zinsa-000001
        089. heartbeat-upch-000001
        090. heartbeat-tasa-000001
        091. heartbeat-prompe-000001
"""

    