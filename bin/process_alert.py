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
from engine import *
#######################################################################################
host = "127.0.0.1"
port = 8080
app = Flask(__name__)
#######################################################################################
def bytesELK2json(data,codification='utf-8'):
    d_dict = {}
    if (type(data)==bytes):
        print("[INFO] bytesELK2json | decoding <{0}:{1}>".format(len(data),codification))
        data = data.decode(codification)
    
    try:
        data = data.replace("false","False")
        d_dict = eval(data)
    except:
        print("[ERROR] bytes2ELK2json <{1}>type={0} ".format( type(data) , len(data) ))
    finally:
        return d_dict
#######################################################################################
@app.route('/', methods=['POST'])
def webhook_post():
    #URL = "http://1855b969.ngrok.io"
    print("webhook_post()-> ")
    data_json = bytesELK2json(request.data)
    rpt = processAlert(data_json)
    #print_json( data_json )
    return '', 200
#######################################################################################
@app.route('/', methods=['GET'])
def webhook_get():
    #URL = "http://1855b969.ngrok.io"
    print("webhook_get()-> ")#+ str(sys.stdout.flush()) )
    data_json = bytesELK2json(request.data)
    #print_json( data_json )
    return '', 200
#######################################################################################
@app.route('/hearbeat_ping_down', methods=['GET','POST'])
def solve_ping():
    data_json = bytesELK2json(request.data)
    #print_json( data_json )
    return '', 200
#######################################################################################
if __name__ == '__main__':
    app.run(host = host, port = port)


