dictionary = {
            "sysUpTime.sysUpTimeInstance" => "[system][sysUpTimeInstance]",
            "sysORLastChange.0" => "[system][sysORLastChange]",
            "sysDescr.0" => "[system][sysDescr]",
            "sysORTable.sysOREntry.sysORDescr.1" => "[system][sysORDescr]",
            "sysORTable.sysOREntry.sysORUpTime.1" => "[system][sysORUpTime]",
            "sysObjectID.0" => "[system][sysObjectID]",
            "sysServices.0" => "[system][sysServices]",
            "sysName.0" => "[system][sysName]",
            "sysORTable.sysOREntry.sysORIndex.1" => "[system][sysORIndex]",
            "sysContact.0" => "[system][sysContact]",
            "sysLocation.0" => "[system][sysLocation]",
            "sysORTable.sysOREntry.sysORID.1" => "[system][sysORID]",
            "101.4.1.1.0" => "[fgSystemInfo][fgSysVersion]",
            "101.4.1.2.0" => "[fgSystemInfo][fgSysMgmVdom]",
            "101.4.1.3.0" => "[fgSystemInfo][fgSysCpuUsage]",
            "101.4.1.4.0" => "[fgSystemInfo][fgSysMemUsage]",
            "101.4.1.5.0" => "[fgSystemInfo][fgSysMemCapacity]",
            "101.4.1.6.0" => "[fgSystemInfo][fgSysDiskUSage]",
            "101.4.1.7.0" => "[fgSystemInfo][fgSysDiskCapacity]",
            "101.4.1.8.0" => "[fgSystemInfo][fgSysSesCount]",
            "101.4.1.9.0" => "[fgSystemInfo][fgSysLowMemUsage]",
            "101.4.1.10.0" => "[fgSystemInfo][fgSysLowMemCapacity]",
            "101.4.1.11.0" => "[fgSystemInfo][fgSysSesRate1]",
            "101.4.1.12.0" => "[fgSystemInfo][fgSysSesRate10]",
            "101.4.1.13.0" => "[fgSystemInfo][fgSysSesRate30]",
            "101.4.1.14.0" => "[fgSystemInfo][fgSysSesRate60]",
            "101.4.1.15.0" => "[fgSystemInfo][fgSysSes6Count]",
            "101.4.1.16.0" => "[fgSystemInfo][fgSysSes6Rate1]",
            "101.4.1.17.0" => "[fgSystemInfo][fgSysSes6Rate10]",
            "101.4.1.18.0" => "[fgSystemInfo][fgSysSes6Rate30]",
            "101.4.1.19.0" => "[fgSystemInfo][fgSysSes6Rate60]",
            "101.4.1.20.0" => "[fgSystemInfo][fgSysUpTime]"
        }
        hash = event.to_hash
        hash.each {|k,v|
            new_key = dictionary[k]
            value = v
            if new_key == nil
                event.set(k,v)
            else
                #logger.info("replace:", "key" => k )
                event.remove(k)
                event.set(new_key, value)
            end
        }