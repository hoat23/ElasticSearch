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
            print("[POST]:"+str(rpt.status_code)+" | "+ str(rpt.reason) )
        

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


"""
curl -X POST -H "Content-Type: application/json" -d '
{
    "messaging_type": "RESPONSE",
    "recipient": { 
        "id": "1610669258970681"
    },
    "message": {
        "text": "hello, world!"
    } 
}' "https://graph.facebook.com/v2.6/me/messages?access_token=EAACiYk1saZAgBAIc58EhTl2FiiWVEKmCmBcw52k4VDSVFumA6k76M5jy4njNAkWZA0H61AdC2tLa8UuLiPwBVdCATcHCKjGYr8M266WtWSqqP0c3FSV5ZBcXo6Yyf67bQI6JegoE2mMellhZATx76H0LZB6xasIATipP9wmnfQeDMSJ0 xAiYgY7Wgdz2ZBVjMZD"

curl -X POST -H "Content-Type: application/json" -d '{"messaging_type": "RESPONSE","recipient": {"id": "1610669258970681"}, "message": {"text": "hello, world!"} }' "https://graph.facebook.com/v2.6/me/messages?access_token=EAACiYk1saZAgBAIc58EhTl2FiiWVEKmCmBcw52k4VDSVFumA6k76M5jy4njNAkWZA0H61AdC2tLa8UuLiPwBVdCATcHCKjGYr8M266WtWSqqP0c3FSV5ZBcXo6Yyf67bQI6JegoE2mMellhZATx76H0LZB6xasIATipP9wmnfQeDMSJ0 xAiYgY7Wgdz2ZBVjMZD"

"""
