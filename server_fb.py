# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Description: Integrar alertas con messenger
#########################################################################################
import sys, requests, json, ast
from credentials import *
from utils import print_json
from datetime import datetime, timedelta
from flask import Flask, request, abort
#######################################################################################
host = "127.0.0.1"
port = 8080
app = Flask(__name__)
#########################################################################################
def req_post(post_json , timeout=None):
    try: 
        URI_API = post_json['uri']
        headers = post_json['qs']
        data = post_json['json']
        headers.update({'Content-Type': 'application/json'})
        if type(data) != str : data = json.dumps(data)
        rpt = requests.post(URL_API, headers=headers, data = data , timeout=timeout)
        if not( (rpt.status_code)==200 or (rpt.status_code)==201 ):
            print("{0}|INFO | req_post | {1} | {2} ".format( datetime.utcnow().isoformat() , rpt.status_code, rpt.reason) ) )
        

        print("{0}|INFO | req_post | URL_API=[{1}]".format(datetime.utcnow().isoformat(), URL_API) )
    except:
        print("{0}|ERROR| req_post | URL_API=[{1}]".format(datetime.utcnow().isoformat()) )
    return
#########################################################################################
def callSendAPI(message ,sender_id="1610669258970681", type_msg = "RESPONSE" ):
    
    data_json = { 
        "messaging_type": type_msg,
        "recipient": {
            "id": sender_id
        },
        "message": message
    }

    print("{0}|INFO | post_fb | psid={1} type_msg={2}".format(datetime.utcnow().isoformat(), sender_id, type_msg) )
    print_json(data_json)
    
    post_json = {
        "uri" : "https://graph.facebook.com/v2.6/me/messages",
        "qs": { "access_token": ACCESS_TOKEN_FB },
        "json": data_json
    }

    req_post( post_json )

    return

