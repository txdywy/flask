import hashlib, requests
m = hashlib.md5()
url = 'http://www.ucpaas.com/maap/sms/code?sid=%s&appId=%s&time=%s&sign=%s&to=%s&templateId=%s&param=%s'
sid = YZX_SID
appId = YZX_APPID
token = YZX_TOKEN
time = '20150924164300135'
m.update(sid+time+token)
sign = m.hexdigest().lower()
templateId = '13593'
to = '13522417187'#'13621228208'
param = '1,2'
u = url % (sid, appId, time, sign, to, templateId, param)
r = requests.get(u)
print r.text

