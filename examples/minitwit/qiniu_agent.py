from config import *
from qiniu import Auth
try:
    q = Auth(QN_ACCESS_KEY, QN_SECRET_KEY)
except:
    q = None
    print "==========no qiniu config loaded========"
bucket_name = 'udon'

def get_qn_token():
    return q.upload_token(bucket_name)
