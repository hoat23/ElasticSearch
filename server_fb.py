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
@app.route('/', methods=['GET'])
def handle_verification():
    if (request.args.get('hub.verfiy_token', '')==VERIFY_TOKEN_FB):
        print("[GET] TOKEN VERFICADO")
        return request.args.get('hub.challenge', '')
    else:
        print("[GET] TOKEN INCORRECTO")
        return "Error, wrong validation token H23."
#########################################################################################
@app.route('/', methods=['POST'])
def handle_message():
    '''
    Handle messages sent by facebook messenger to the application
    '''
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            if messaging_event.get("message"):
                sender_id = messaging_event["sender"]["id"]
                recipient_id = messaging_event["recipient"]["id"]
                message_text = messaging_event["message"]["text"]
                #send_message_response(sender_id, parse_natural_text(message_text))
                send_message(sender_id, message_text)
#########################################################################################
def send_message_response(sender_id, message_text):
    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)
    for message in messages:
        send_message(sender_id, message)
    return
#########################################################################################
def send_message(sender_id, message_text):
    '''
    Sending response back to theuser using facebook graph API
    '''
    print("send_message({0})".format(message_text))
    URL_API= "https://graph.facebook.com/v2.6/me/messages"
    qs = {"acces_token" : ACCESS_TOKEN_FB}
    headers = {"Content-Type": "application/json"}
    data = json.dumps( {
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    } )
    r = requests.post(URL_API, params = qs, headers=headers, data = data )
    print("fin...   {0}".format(r.status_code))
    return
#########################################################################################
def req_post(post_json , timeout=None):
    try: 
        URL_API = post_json['uri']
        params = post_json['qs']
        data = post_json['json']
        headers = {'Content-Type': 'application/json'}
        if type(data) != str : data = json.dumps(data)
        print("req_post | type(data): {0}".format(type(data)))
        rpt = requests.post(URL_API, params=params, headers=headers, data=data)
        #if not( (rpt.status_code)==200 or (rpt.status_code)==201 ):
        print("{0}|INFO | req_post | {1} | {2} ".format( datetime.utcnow().isoformat() , rpt.status_code, rpt.reason) )
        print("{0}|INFO | req_post | URL_API=[{1}]".format(datetime.utcnow().isoformat(), URL_API) )
    except:
        print("{0}|ERROR| req_post | URL_API=[{1}]".format(datetime.utcnow().isoformat()) )
    return
#########################################################################################
def callSendAPI(message ,sender_id="1610669258970681", type_msg = "RESPONSE" ):
    data_json = {
        #"messaging_type": type_msg,
        "recipient": {
            "id": sender_id
        },
        "message": {
           "text": message
        }
    }

    print("{0}|INFO | post_fb | psid={1} type_msg={2}".format(datetime.utcnow().isoformat(), sender_id, type_msg) )
    
    post_json = {
        "uri" : "https://graph.facebook.com/v2.6/me/messages",
        "qs": { "access_token": ACCESS_TOKEN_FB },
        "json": data_json
    }
    #send_message(sender_id, "holaaa...mundo")
    req_post( post_json )
    return
#########################################################################################
if __name__ == "__main__":
    #app.run()
    callSendAPI("Hola ...from Python")
    print("............................")
    #send_message( "1610669258970681" , "hola...from Python")
    print("fin")
