
# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 19/11/2018
# Description: Server to show everything to received.
#########################################################################################
import sys, requests, json, ast
from utils import print_json
from utils_elk import *
from datetime import datetime, timedelta
from flask import Flask, request, abort
#######################################################################################
app = Flask(__name__)
port = 3009
#######################################################################################
@app.route('/', methods=['GET','POST'])
def webhook():
    print("DEF webhook()-> "+ str(sys.stdout.flush()) )
    print_json( bytesELK2json( request.data ))
    return '', 200

@app.route('/hearbeat_ping_down', methods=['GET','POST'])
def solve_ping():
    print("DEF ping-----------------------")
    print( request.data )
    return '', 200



#######################################################################################
if __name__ == '__main__':
    app.run(host='172.30.0.114',port=3009)
