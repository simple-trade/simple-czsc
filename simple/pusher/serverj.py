import requests
import urllib.parse as p

def wx_push(text='计算完成', desp='',url=''):
    data = {'text': text, 'desp': desp}
    resp = requests.post(url=url, data=data)
    print('push resp: %s' % resp)

