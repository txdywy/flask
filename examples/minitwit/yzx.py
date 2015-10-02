import hashlib, requests, datetime
try:
    from config import YZX_SID, YZX_APPID, YZX_TOKEN
except Exception as e:
    YZX_SID, YZX_APPID, YZX_TOKEN = '', '', ''
    print '----------no yzx--------' 

sid = YZX_SID
appId = YZX_APPID
token = YZX_TOKEN

def sms(to='13621228208', template_id='13593', param='1,2'):
    m = hashlib.md5()
    url = 'http://www.ucpaas.com/maap/sms/code?sid=%s&appId=%s&time=%s&sign=%s&to=%s&templateId=%s&param=%s'
    d = datetime.datetime.now()
    time = d.strftime('%Y%m%d%H%M%S') + str(d.microsecond)[:3]
    m.update(sid + time + token)
    sign = m.hexdigest().lower()
    u = url % (sid, appId, time, sign, to, template_id, param)
    r = requests.get(u)
    return r.text
