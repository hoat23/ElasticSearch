# Monitoring MCaffe using ElasticSearch.

## Sending syslog to Elasticsearch

### Configuration of input tcp in Logstash

#### Generate SSL.X509 using OpenSSL

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
    
    xml {
      source => "message"
      target => "mcaffe_json"
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

