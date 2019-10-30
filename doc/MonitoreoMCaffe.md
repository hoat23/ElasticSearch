# Monitoring MCaffe using ElasticSearch.

## Sending syslog to Elasticsearch

### Configuration of input tcp in Logstash

#### Generate Certificate SSL X509 using OpenSSL

First install OpenSSL in your server and validate:
```
openssl --version
```
Execute this command:

```
openssl req -newkey rsa:2048 -nodes -keyout /etc/owner_certifies/syslogselfsigned.key -x509 -days 365 -out /etc/owner_certifies/syslogselfsigned.crt -config /etc/pki/tls/openssl.cnf
```

#### Configurate pipeline in Logstash
```
input{
    # MCAFFE SYSLOG EPO
    tcp {
      port => 5128
      add_field => {"[elk][index]" => "mcaffe"}
      ssl_cert => '/etc/owner_certifies/syslogselfsigned.crt'
      ssl_key => '/etc/owner_certifies/syslogselfsigned.key'
      ssl_enable => true
      ssl_verify => false
    }
}

filter{
    
    grok {
        match => { "message" => '%{SYSLOG5424LINE}' }
    }        
    
    mutate {
        gsub => ["syslog5424_msg",'\"','"']
    }
    
    #target => "mcaffe_json"
    xml {
        source => "syslog5424_msg"
        target => "mcaffe_json"
        store_xml => false
    }
    
    mutate {
        remove_field => ["message"]
    }
    
}

output{
    # dots
    stdout {
      codec => rubydebug
    }
    
}
```
#### Configurate syslog in MCaffe

#### Data in ElasticSearch
```
{
  "_index": "mcaffe-group01-000001",
  "_type": "_doc",
  "_id": "_wNkHW4BQ0flEfWzqkoI",
  "_version": 1,
  "_score": null,
  "_source": {
    "host": "CLIENTepomcafee.CLIENT.pvt",
    "syslog5424_sd": "[agentInfo@3401 tenantId=\"1\" bpsId=\"1\" tenantGUID=\"{00000000-0000-0000-0000-000000000000}\" tenantNodePath=\"1\\2\"]",
    "@timestamp": "2019-10-30T15:59:11.607Z",
    "elk": {
      "index": "mcaffe_antivirus"
    },
    "syslog5424_pri": "29",
    "syslog5424_ver": "1",
    "syslog5424_host": "CLIENTEPOMCAFEE",
    "syslog5424_ts": "2019-10-30T03:59:11.0Z",
    "@version": "1",
    "syslog5424_app": "EPOEvents",
    "port": 49966,
    "mcaffe_json": {
      "EventList": [
        {
          "ProductVersion": "11.0.405.4",
          "ProductFamily": "Secure",
          "Event": [
            {
              "OPGData": [                "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"
              ],
              "EventID": [
                "19136"
              ],
              "GMTTime": [
                "2019-10-30T15:58:52"
              ],
              "Severity": [
                "0"
              ],
              "UserInfo": [
                "ZZBHoQUAAAAAAAAD+gAAAIWSQWvCQBCFv3Oh/6H4B2JvDaR3S4L50Cq0Xn6b/tWCmpCmQv69bzeJcTUigWHmvZk3OzMJSTiw4I8VJSl7fsh5oqKmEJay5JURz7wwlh0xIWSqipTY+YEXxfxKq2CLkcKD7E4qTd5t7o1MX86/+lcXVbe5Rq+S3bMWb6ONuOVg33t5n2cT9f5UW7G9C9UEDvlSfaUZOnU/TqRnhGxb1o8jae2kZfSSus24xmJp2biUrn2dnbubZJh5d9VG09krNrnXWHTaYul197HIzdPzffQtv2jx3p/p+s1mUu3Ids0UjV3WORIyVw97g8zVGu3Ev9M9fuhPnfDIA0c="
              ]
            }
          ],
          "ProductName": "McAfee DLP Host"
        }
      ],
      "MachineInfo": [
        {
          "TimeZoneBias": [
            "300"
          ],
          "MachineName": [
            "SNBLGREY"
          ],
          "AgentGUID": [
            "{674ecea4-1a68-11e9-38da-d481d781ceee}"
          ],
          "IPAddress": [
            "20.22.122.127"
          ],
          "RawMACAddress": [
            "d18127314e5e"
          ],
          "OSName": [
            "Windows 7"
          ],
          "UserName": [
            "SYSTEM"
          ]
        }
      ]
    },
    "syslog5424_msgid": "EventFwd"
  },
  "fields": {
    "@timestamp": [
      "2019-10-30T15:59:11.607Z"
    ],
    "syslog5424_ts": [
      "2019-10-30T03:59:11.000Z"
    ],
    "mcaffe_json.EventList.Event.GMTTime": [
      "2019-10-30T15:58:52.000Z"
    ]
  },
  "sort": [
    1572451151607
  ]
}
```
## More documentation

Download OpenSSL: https://slproweb.com/products/Win32OpenSSL.html

McAffe info: https://kc.mcafee.com/corporate/index?page=content&id=KB87927&snspd-1116&locale=es_ES&viewlocale=es_ES

