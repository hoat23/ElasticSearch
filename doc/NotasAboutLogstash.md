## Listing plugins of Logstash 
```
cd /usr/share/logstash/bin
./logstash-plugin list --verbose
```
## Update plugins of Logstash
```
cd /usr/share/logstash/bin
./logtash-plugin list update
```
## Adding a Dictionary MIB to snmp

### Install ruby (simple format without management version) 

https://linuxize.com/post/how-to-install-ruby-on-centos-7/#install-ruby-using-rbenv
```
yum install ruby
ruby --version
```

### Converting files from .mib to .yml
More documentation about adding mib dictionary to Logstash:  https://discuss.elastic.co/t/mib-oid-translation/29710/2
#### Instaling ruby and libsmi for converting files
```
yum install libsmi
cd /usr/share/logstash/vendor/bundle/jruby/2.5.0/gems/snmp-1.3.2
wget https://raw.githubusercontent.com/hoat23/Firewall-Tools/master/ruby/import.rb
mkdir mibs
```
Link Original: https://raw.githubusercontent.com/hallidave/ruby-snmp/master/import.rb
#### Creating diretory /mibs with the .mibs files
```
cd /mibs
wget http://www.circitor.fr/Mibs/Mib/F/FORTINET-CORE-MIB.mib -O FORTINET-CORE-MIB.mib
cd ..
```
#### Convirting file .mib to .yaml
```
cd /usr/share/logstash/vendor/bundle/jruby/2.5.0/gems/snmp-1.3.2
ruby import.rb mib/
head data/ruby/snmp/mibs/FORTINET-CORE-MIB.yaml
```
### Configuration of pipeline in logstash for load dictionar MIB in format .YML

```
   snmptrap {
        port => 1620
        community => "logstash"
        yamlmibdir => "/usr/share/logstash/vendor/bundle/jruby/2.5.0/gems/snmp-1.3.2/data/ruby/snmp/mibs/"
   }
```
My own dictionary's mibs:
https://github.com/hoat23/Firewall-Tools/tree/master/mibs




