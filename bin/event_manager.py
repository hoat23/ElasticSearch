# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Last update: 30/05/2019
# Description: Procesar las alertas generadas
# More info: https://help.victorops.com/knowledge-base/victorops-elasticsearch-watcher-integration/
#########################################################################################
import sys, requests, json, ast, time
from utils import print_json
from utils_elk import *
from datetime import datetime, timedelta
from flask import Flask, request, abort
from engine_elastic import *
#from engine_facebook import *
from credentials import *
from server_gmail import *
#######################################################################################
host = 'localhost'
port = 80
app = Flask(__name__)
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
    path = "aggregations.incidencia_types.[buckets].clientes.[buckets].cluster_name.[buckets].last_run.hits.[hits]._id"
    data_json = request.json
    #save_yml(data_json, nameFile="incidencias_elk.yml")
    for incidencia_type in data_json['aggregations']['incidencia_types']['buckets']:
        #print("incidencia_type     : " + incidencia_type['key'])
        for cliente in incidencia_type['clientes']['buckets']:
            #print("    cliente     : " + cliente['key'])
            for cluster in cliente['cluster_name']['buckets']:
                #print("         cluster: " + cluster['key'])
                rpt_json = get_data_by_filter("heartbeat-group*-write",terms=[{"cmdb.client":cliente['key']},{"cmdb.cluster_name":cluster['key']}])
                data_aditional = build_data_aditional(rpt_json)
                #print_list(data_aditional)
                #print_json(rpt_json)
                for item in cluster['last_run']['hits']['hits']:
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
@app.route('/webhook', methods=['POST'])
def handle_message():
    #Handle messages sent by facebook messenger to the application
    data_json = request.get_json()
    print("{0}|INFO | POST | handle_message | length:{1}".format( datetime.utcnow().isoformat() , len(data_json)))
    rpt = engine_facebook(data_json)
    return rpt
#######################################################################################
if __name__ == '__main__':
    app.run(host = host, port = port)

