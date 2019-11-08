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

## Running Logstash in Windows

File of configuration "logstash.yml"

```
# ------------  Node identity ------------
# Use a descriptive name for the node:
node.name: h23_logstash
# ------------ Data path ------------------
path.data: /var/lib/logstash
# ------------ Pipeline Settings --------------
# pipeline.id: main
# pipeline.workers: 2
# pipeline.batch.size: 125
# pipeline.batch.delay: 50
# pipeline.unsafe_shutdown: false
# ------------ Pipeline Configuration Settings --------------
# path.config:
# config.string:
# config.test_and_exit: false
# config.reload.automatic: false
# config.reload.interval: 3s
# config.debug: false
# config.support_escapes: false
# ------------ Module Settings ---------------
# modules:
#   - name: MODULE_NAME
#     var.PLUGINTYPE1.PLUGINNAME1.KEY1: VALUE
#     var.PLUGINTYPE1.PLUGINNAME1.KEY2: VALUE
#     var.PLUGINTYPE2.PLUGINNAME1.KEY1: VALUE
#     var.PLUGINTYPE3.PLUGINNAME3.KEY1: VALUE
# ------------ Cloud Settings ---------------
#cloud.id: "elastic:password"
#cloud.auth: "elastic:password"
# ------------ Queuing Settings --------------
# queue.type: memory
# path.queue:
# queue.page_capacity: 64mb
# queue.max_events: 0
# queue.max_bytes: 1024mb
# queue.checkpoint.acks: 1024
# queue.checkpoint.writes: 1024
# queue.checkpoint.interval: 1000
# ------------ Dead-Letter Queue Settings --------------
dead_letter_queue.enable: true
# If using dead_letter_queue.enable: true, the maximum size of each dead letter queue. Entries
# will be dropped if they would increase the size of the dead letter queue beyond this setting.
# Default is 1024mb
# dead_letter_queue.max_bytes: 1024mb
path.dead_letter_queue: "/var/log/dead_letter_queue"
# ------------ Metrics Settings --------------
# Bind address for the metrics REST endpoint
# http.host: "127.0.0.1"
# http.port: 9600-9700
# ------------ Debugging Settings --------------
# Options for log.level: fatal, error, warn, info (default), debug, trace
log.level: info
path.logs: /var/log/logstash
# ------------ Other Settings --------------
# Where to find custom plugins
# path.plugins: []
# ------------ X-Pack Settings (not applicable for OSS build)--------------
# X-Pack Monitoring
xpack.monitoring.enabled: true
xpack.monitoring.elasticsearch.username: "user"
xpack.monitoring.elasticsearch.password: password
xpack.monitoring.elasticsearch.hosts: ["https://aaaaabbbbbcccccc.us-east-1.aws.found.io:9243"]
xpack.monitoring.collection.interval: 10s
xpack.monitoring.collection.pipeline.details.enabled: true
# X-Pack Management
xpack.management.enabled: true
xpack.management.pipeline.id: ["test_beats","test_syslog","test_filter","test_output"]
xpack.management.elasticsearch.username: "user"
xpack.management.elasticsearch.password: password
xpack.management.elasticsearch.hosts: ["https://aaaabbbbcccc.us-east-1.aws.found.io:9243"]
```

Command for running service in PowerShell

```
PS C:\logstash> .\bin\logstash.bat -f .\conf\logstash.yml
```




