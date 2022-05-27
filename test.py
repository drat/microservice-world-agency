import random
import requests

api = requests.Session()
session_id = random.randint(10001, 50000)
api.proxies.update({
    'http': f'http://user-pquoctuanno1:Tuan27121998@all.dc.smartproxy.com:{session_id}',
    'https': f'http://user-pquoctuanno1:Tuan27121998@all.dc.smartproxy.com:{session_id}'
})
res = api.get('https://www.facebook.com/')
open('./index.html', 'w').write(res.text)