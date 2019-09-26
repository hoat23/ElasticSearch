### Differences between Input and Chain-Input

#### INPUT SIMPLE
path_to_first_aggregation: ctx.payload.aggregations.[NAME_FIRST_AGGREGATION]
```
"input": {
   "search": {...}
}
```

#### INPUT CHAIN

path_to_first_aggregation: ctx.payload.CHAIN_FIRST.aggregations.[NAME_FIRST_AGGREGATIONS]

```
"input": {
   "chain": {
       "inputs": [
          "CHAIN_FIRST" : {
              "search": {...}
           }
        ]
    }
}
```
#### WEBHOOK - SENDING MESSAGE TO MOBILE DEVICES USING TWILIO-API
In the documentation of twilio, can get the command curl to send message to cellphone, in this case "Whatssapp Application".
```
curl -X POST 'https://api.twilio.com/2010-04-01/Accounts/D4L3161z3cA1114nAz/Messages.json' -u myUserIDTwilio:myPasswordTwilio 
--data-urlencode 'To=whatsapp:+51982169331'  
--data-urlencode 'From=whatsapp:+14155238886' 
--data-urlencode  'Body=Hello from Elastic H23'  
--data-urlencode 'MediaUrl=https://www.javiramosmarketing.com/wp-content/uploads/2016/10/stockvault-imagenes-libres-de-derechos-gratis-javiramosmarketing.jpg'
```

Transform this curl to webhook alert for ElastiSearch, it's look like this:

```
"actions" : {
  "post_whatssapp_using_twilioapi" : {
    "webhook" : {
      "url" : "https://api.twilio.com/2010-04-01/Accounts/D4L3161z3cA1114nAz/Messages.json",
      "method" : "POST",
      "body": "Body=Hello from Elastic H23&To=whatsapp%3A%2B51982169331&From=whatsapp%3A%2B14155238886",
      "headers" : {
        "Content-Type" : "application/x-www-form-urlencoded"
      },
      "auth": {
        "basic": {
          "username": "myUserIDTwilio",
          "password": "myPasswordTwilio"
        }
      }
    }
  }
}
```
URL online encoder: https://www.urlencoder.org
