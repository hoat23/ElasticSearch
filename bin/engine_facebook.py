# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Description: Integrar alertas con messenger
#########################################################################################
import sys, requests, json, ast
from credentials import *
from utils import print_json
from datetime import datetime, timedelta
#########################################################################################
def engine_facebook(data_json):
    #Handle messages sent by facebook messenger to the application
    if data_json["object"] == "page":
        for entry in data_json["entry"]:
            for messaging_event in entry["messaging"]:
	            if messaging_event.get("message"):
        	        sender_id = messaging_event["sender"]["id"]
                	recipient_id = messaging_event["recipient"]["id"]
	                message_text = messaging_event["message"]["text"]
        	        #send_message_split(sender_id, parse_natural_text(message_text))
	                send_message_split(sender_id, message_text)
    else:
        print("{0}|WARN | engine_facebook ".format(datetime.utcnow().isoformat()) )
        print_json(data_json)
    return "ok"
#########################################################################################
def send_message_split(sender_id, message_text, char_split = ". "):
    messages = message_text.split(char_split)
    for message_txt in messages:
        callSendAPI(message_txt,sender_id=sender_id)
    return
#########################################################################################
def req_post(post_json , timeout=None):
    try: 
        URL_API = post_json['uri']
        params = post_json['qs']
        data = post_json['json']
        headers = {'Content-Type': 'application/json'}
        if type(data) != str : data = json.dumps(data)
        rpt = requests.post(URL_API, params=params, headers=headers, data=data)
        #if not( (rpt.status_code)==200 or (rpt.status_code)==201 ):
        print("{0}|INFO | req_post | {1} | {2} | URL_API=[{3}]".format( datetime.utcnow().isoformat() , rpt.status_code, rpt.reason, URL_API) )
    except:
        print("{0}|ERROR| req_post ".format(datetime.utcnow().isoformat()) )
    return
#########################################################################################
def callSendAPI(message ,sender_id = "00000000000000", type_msg = "RESPONSE" ):
    data_json = {
        "messaging_type": type_msg,
        "recipient": { "id": sender_id },
        "message": { "text": message }
    }
    print("{0}|INFO | post_fb  | psid={1} type_msg={2}".format(datetime.utcnow().isoformat(), sender_id, type_msg) )
    post_json = {
        "uri" : "https://graph.facebook.com/v3.2/me/messages",#2.6->ok
        "qs": { "access_token": ACCESS_TOKEN_FB },
        "json": data_json
    }
    req_post( post_json )
    return
#########################################################################################
if __name__ == "__main__":
    mssg = "{0} testing engine_facebook.py".format( datetime.utcnow().isoformat() )
    callSendAPI(mssg, SENDER_ID_H23)
    print("{0}|INFO | testing engine_facebook.py".format( datetime.utcnow().isoformat() ) )
