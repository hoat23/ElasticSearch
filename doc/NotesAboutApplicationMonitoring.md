# APPLICATION PERFOMANCE MONITORING

## Python

### Instalation

```bash
python -m pip install elastic-apm
```

### Configuration

#### CMD
```
ELASTIC_APM_SERVICE_NAME=foo python manage.py runserver
```


#### Inline
```
apm_client = Client(service_name="foo")
```

#### Flask
```
app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': 'my-app',
    'SECRET_TOKEN': 'changeme',
    'LOG_LEVEL': 'trace',
    'API_REQUEST_TIME': '5s'
}

apm = ElasticAPM(app)
```

