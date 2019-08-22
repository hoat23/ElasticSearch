# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Last update: 22/08/2019
# Description: Procesar las alertas generadas de elastic
#              Se agrego soporte de REdis para manejar mayor cantidad de eventos
# More info: https://help.victorops.com/knowledge-base/victorops-elasticsearch-watcher-integration/
#########################################################################################
import sys
import requests
import json
import ast
import time
import redis
import functools as ft
import pandas as pd
from utils import print_json
from utils_elk import *
from datetime import datetime, timedelta
from flask import Flask, request, abort
from engine_elastic import *
#from engine_facebook import *
from credentials import *
from server_gmail import *
#######################################################################################
host = HOST_SERVER # defined in credentials.py
port = PORT_SERVER # defined in credentials.py
#######################################################################################
app = Flask(__name__)
#######################################################################################
def get_hit_count_global():
    retries = 5
    count = -1
    while True:
        try: 
            count = cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            print("get_hit_count_global | ERROR | {0}".format( exc ))
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)
        finally:
            print("get_hit_count_global | INFO | count = {0}".format( count ))
            return count
    return
#######################################################################################
def build_data_aditional(data_json):
    data_aditional = []
    path= "aggregations.ip.[buckets].last_status.hits.[hits]"
    for ip in data_json['aggregations']['ip']['buckets']:
        #print("---> " + ip['key'])
        data = ip['last_status']['hits']['hits'][0]['_source']
        data_aditional.append("     {0:16s}   |   {1:10s}   |   {2:10s}   |   {3:10s}".format( data['cmdb']['reporting_ip'],data['cmdb']['categoria'],data['cmdb']['ip_group'],data['monitor']['status']))
    return data_aditional
@app.route('/incidencias_elk', methods=['POST'])
def post_incidencias_elk():
    print("{0}|INFO | POST | incidencias_elk".format( datetime.utcnow().isoformat() ))
    path = "aggregations.incidencia_types.[buckets].clientes.[buckets].ip_group.[buckets].last_run.hits.[hits]._id"
    data_json = request.json
    #save_yml(data_json, nameFile="incidencias_elk.yml")
    for incidencia_type in data_json['aggregations']['incidencia_types']['buckets']:
        #print("incidencia_type     : " + incidencia_type['key'])
        for cliente in incidencia_type['clientes']['buckets']:
            #print("    cliente     : " + cliente['key'])
            for ip_group in cliente['ip_group']['buckets']:
                #print("         ip_group: " + ip_group['key'])
                rpt_json = get_data_by_filter("heartbeat-group*-write",terms=[{"cmdb.client":cliente['key']},{"cmdb.ip_group":ip_group['key']}])
                data_aditional = build_data_aditional(rpt_json)
                #print_list(data_aditional)
                #print_json(rpt_json)
                for item in ip_group['last_run']['hits']['hits']:
                    #print("             _id:" + item['_id'])
                    #print_json(item['_source'])
                    send_email_by_incidencia(item,data_aditional)
    return '', 200
#######################################################################################
@app.route('/wbhk_elastic', methods=['POST'])
def elk_watcher_post():
    print("{0}|INFO | POST | elk_watcher".format( datetime.utcnow().isoformat() ))
    data_json = bytesELK2json(request.data) #request.json()
    rpt = engine_elastic(data_json)
    #print_json( data_json )
    return '', 200
#######################################################################################
@app.route('/webhook', methods=['GET'])
def handle_verification():
    if (request.args.get('hub.verfiy_token', '')==VERIFY_TOKEN_FB):
        print("{0}|INFO | GET | handle_verification | token_verificado".format( datetime.utcnow().isoformat() ))
        return request.args.get('hub.challenge', '')
    else:
        print("{0}|ERROR| GET | handle_verification | token_incorrecto".format( datetime.utcnow().isoformat() ))
        return "Error, wrong validation token H23."
#--------------------------------------------------------------------------------------
"""
@app.route('/webhook', methods=['POST'])
def handle_message():
    #Handle messages sent by facebook messenger to the application
    data_json = request.get_json()
    print("{0}|INFO | POST | handle_message | length:{1}".format( datetime.utcnow().isoformat() , len(data_json)))
    rpt = engine_facebook(data_json)
    return rpt
"""
@app.route('/test', methods=['POST'])
def webhook_elk():
    print("/ [POST]-> "+ str(sys.stdout.flush()) )
    data = request.data
    data_parse = bytesELK2json(data)
    print_json(data_parse)
    print("/heartbeat [POST] | len(list_groups):{0}".format(len(list_groups)) )
    return '', 200
#######################################################################################
@app.route('/alert_heartbeat', methods=['POST'])
def webhook_alert_heartbeat():
    print("/ [POST]-> "+ str(sys.stdout.flush()) )
    data = request.data
    data_parse = bytesELK2json(data)
    # Extrayendo header
    headers_list = data_parse['metadata']['headers_list']
    email_json = data_parse['metadata']['email']
    file_name_html = email_json['email_body']['alternative']
    groupby = data_parse['metadata']['transform']['groupby']
    watch_id = data_parse['watch_id']
    table_data = aggregation2table(data_parse,headers_list=headers_list)
    # Evaluando condicional para trigger alert
    table_df = pd.DataFrame(table_data, columns = headers_list)
    list_groups = []
    for name, group_df in table_df.groupby(groupby[0]):
        #print(name)
        trigger = ft.reduce( lambda a,b: a|b , group_df['monitor_status']=="down" )
        if trigger:
            list_groups.append( group_df )
    if len(list_groups)>0:
        new_table_df = pd.concat(list_groups)
        new_table_df.reset_index(drop=True, inplace=True)
        new_table_df.index +=  1
        #print( new_table_df )
        table_html = new_table_df.to_html()
        print("webhook_alert_heartbeat | INFO | id:{0} | {1}".format(watch_id, file_name_html))
        file_html = open(file_name_html, "w")
        file_html.write(table_html)
        file_html.close()
        #print( table_html )
        send_email_by_watcher(email_json)
        #table_data2csv(table_data, headers_list = headers_list, nameFile="heartbeat_list_ip.csv")
        #save_yml( data_parse , nameFile="alertas_elk.yml")
    else:
        print("/heartbeat [POST] | len(list_groups):{0}".format(len(list_groups)) )
    return '', 200
#######################################################################################
if __name__ == '__main__':
    #cache = redis.Redis(host='localhost', port = port)
    app.run(host = host, port = port)

