import qy_util
import time
import os
time.sleep(3)
ip = os.popen("ifconfig").read()
qy_util.post(ip, touser='txdywy')
