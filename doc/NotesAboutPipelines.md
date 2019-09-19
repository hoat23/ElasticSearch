### Mapper parsing exception in a field

ERROR MESSAGE: "type"=>"mapper_parsing_exception"

```
logstash          | [2019-08-01T19:16:05,081][WARN ][logstash.outputs.elasticsearch] Could not index event to Elasticsearch. {:status=>400, :action=>["index", {:_id=>nil, :_index=>"supra-yanbal-test", :_type=>"_doc", :routing=>nil}, #<LogStash::Event:0x3a112620>], :response=>{"index"=>{"_index"=>"supra-yanbal-test", "_type"=>"_doc", "_id"=>"gw6cTmwBr0EJYobKWNT6", "status"=>400, "error"=>{"type"=>"mapper_parsing_exception", "reason"=>"failed to parse field [cmdb.reporting_ip] of type [ip] in document with id 'gw6cTmwBr0EJYobKWNT6'", "caused_by"=>{"type"=>"illegal_argument_exception", "reason"=>"'9176a5fe28c1' is not an IP string literal."}}}}}
```
[cmdb][reporting_ip] always tipe IP, if [cmdb][reporting_ipp] has any value like this"9176a5fe28c1".

```
    # Para no afectar el enrichment
    if [cmdb][reporting_ip] {
        if [devip]{
            mutate{
            remove_field => ["[devip]"]
            }
        }
        mutate{
            add_field => {"[devip]" => "%{[cmdb][reporting_ip]}"}
        }
    }
```
Changing
```
    grok {
      match => ["[cmdb][reporting_ip]", "%{IP:[cmdb][reporting_ip]}"]
      remove_field => ["[devip]"]
      tag_on_failure => "_reporting_ip_is_not_ip"
    }

    if "_reporting_ip_is_not_ip" in [tags]{
      mutate{
          rename => {"[cmdb][reporting_ip]" => "[cmdb][reporting_hash]"}
          remove_tag => ["_reporting_ip_is_not_ip"]
      }
    }
```
The grok detect if [cmdb][reporting_ip] is type IP, when is false add to tag "_reporting_ip_is_not_ip".
