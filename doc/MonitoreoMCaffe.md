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

## More documentation

Download OpenSSL: https://slproweb.com/products/Win32OpenSSL.html

McAffe info: https://kc.mcafee.com/corporate/index?page=content&id=KB87927&snspd-1116&locale=es_ES&viewlocale=es_ES

