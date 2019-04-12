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
from engine import *
#######################################################################################
host = "127.0.0.1"
port = 8080
app = Flask(__name__)
#########################################################################################
def req_post(post_json , timeout=None):
    try: 
        print("{0}|INFO | req_post | URL_API=[{1}]".format(datetime.datetime.utcnow().isoformat(), URL_API) )
    except:
        print("{0}|ERROR| req_post | URL_API=[{1}]".format(datetime.datetime.utcnow().isoformat()) )
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

    print("{0}|INFO | post_fb | psid={1} type_msg={2}".format(datetime.datetime.utcnow().isoformat(), sender_id, type_msg) )
    print_json(data_json)
    
    post_json = {
        "uri" : "https://graph.facebook.com/v2.6/me/messages",
        "qs": { "access_token": ACCESS_TOKEN_FB },
        "json": data_json
    }

    req_post( post_json )

    return



