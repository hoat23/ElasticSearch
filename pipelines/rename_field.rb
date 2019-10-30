        dictionary = {
        "action" => "[event][outcome]",
        "app" => "[network][application]",
        "collectedemail" => "[client][user][email]",
        "devid" => "[observer][serial_number]",
        "devname" => "[observer][name]",
        "dstcollectedemail" => "[server][user][email]",
        "dstip" => "[server][ip]",
        "dstmac" => "[server][mac]",
        "dstname" => "[server][address]",
        "dstport" => "[server][port]",
        "dstunauthuser" => "[server][user][name]",
        "duration" => "[event][duration]",
        "group" => "[client][user][group][name]",
        "logid" => "[event][code]",
        "msg" => "[message]",
        "proto" => "[network][iana_number]",
        "rcvdbyte" => "[server][bytes]",
        "rcvdpkt" => "[server][packets]",
        "sentbyte" => "[client][bytes]",
        "sentpkt" => "[client][packets]",
        "service" => "[network][protocol]",
        "sessionid" => "[event][sequence]",
        "srccountry" => "[client][geo][country_name]",
        "srcip" => "[client][ip]",
        "srcmac" => "[client][mac]",
        "srcport" => "[client][port]",
        "subtype" => "[event][action]",
        "tranip" => "[server][nat][ip]",
        "tranport" => "[server][nat][port]",
        "transip" => "[client][nat][ip]",
        "transport" => "[client][nat][port]",
        "type" => "[event][category]",
        "unauthuser" => "[client][user][name]",
        "url" => "[url][path]"
        }
        
        hash = event.to_hash
        hash.each {|k,v|
            new_key = dictionary[k]
            value = v.to_s
            if new_key != nil
                #logger.info("replace : ", {"key" => k, "new_key" => new_key} )
                event.set(new_key, value)
                #tmp_value = event.get(new_key)
                #logger.info("get value: ", {new_key => tmp_value})
            end
        }
