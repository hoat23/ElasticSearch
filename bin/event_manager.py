# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Description: Procesar las alertas generadas
# More info: https://help.victorops.com/knowledge-base/victorops-elasticsearch-watcher-integration/
#########################################################################################
import sys, requests, json, ast
from utils import print_json
from datetime import datetime, timedelta
from flask import Flask, request, abort
from engine_elastic import *
from engine_facebook import *
from credentials import *
#######################################################################################
host = HOST_SERVER
port = PORT_SERVER
app = Flask(__name__)
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
    print("{0}|INFO | POST | handle_message | len_data={1}".format( datetime.utcnow().isoformat() , len(data)))
    rpt = engine_facebook(data_json)
    return rpt
#######################################################################################
if __name__ == '__main__':
    app.run(host = host, port = port)

